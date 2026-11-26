"""Java practice programs: Real-world Patterns tab."""
from sd_j_util import J

J("feed-fanout", r'''
import java.util.*;

public class FeedFanoutDemo {
    static final Map<String, Set<String>> followers = new HashMap<>();      // author -> followers
    static final Map<String, Set<String>> following = new HashMap<>();      // user -> authors
    static final Map<String, Deque<String>> feedCache = new HashMap<>();    // precomputed feeds (push)
    static final Map<String, List<String>> authorTimeline = new HashMap<>();
    static final int CELEB_THRESHOLD = 3; static int cacheWrites = 0;

    static void follow(String u, String a) { followers.computeIfAbsent(a, k -> new TreeSet<>()).add(u); following.computeIfAbsent(u, k -> new TreeSet<>()).add(a); }

    static void post(String author, String postId) {
        authorTimeline.computeIfAbsent(author, k -> new ArrayList<>()).add(0, postId);
        Set<String> fs = followers.getOrDefault(author, Set.of());
        if (fs.size() >= CELEB_THRESHOLD) { System.out.println(author + " posts " + postId + " -> celebrity: stored once, pulled at read time"); return; }
        for (String f : fs) { feedCache.computeIfAbsent(f, k -> new ArrayDeque<>()).addFirst(postId); cacheWrites++; }
        System.out.println(author + " posts " + postId + " -> pushed into " + fs.size() + " follower feeds");
    }

    static List<String> readFeed(String user) {
        List<String> feed = new ArrayList<>(feedCache.getOrDefault(user, new ArrayDeque<>()));
        for (String a : following.getOrDefault(user, Set.of()))
            if (followers.get(a).size() >= CELEB_THRESHOLD) feed.addAll(authorTimeline.getOrDefault(a, List.of()));   // merge celebrity posts
        feed.sort(Comparator.comparing((String p) -> Integer.parseInt(p.substring(1))).reversed());               // newest first (ids are time-ordered)
        return feed;
    }

    public static void main(String[] args) {
        follow("asha", "ravi"); follow("zoya", "ravi");
        for (String u : List.of("asha", "zoya", "meera", "kiran")) follow(u, "celeb");
        post("ravi", "p1"); post("celeb", "p2"); post("ravi", "p3"); post("celeb", "p4");
        System.out.println("asha's feed: " + readFeed("asha"));
        System.out.println("meera's feed: " + readFeed("meera"));
        System.out.println("cache writes: " + cacheWrites + " (with pure push the celebrity would cost " + followers.get("celeb").size() + " writes per post; with 100M followers, 100M)");
    }
}
''', ["Cap each cached feed at 5 entries (`LTRIM`) and show older posts falling off.",
      "Skip pushing to inactive users (last login > 30 days) and build their feed on demand.",
      "Add ranking: sort by likes × recency decay instead of pure time."])

J("counters", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class CountersDemo {
    public static void main(String[] args) throws Exception {
        int threads = 8, likesEach = 100_000;
        // 1. One contended counter vs LongAdder (striped/sharded counter inside the JVM)
        AtomicLong single = new AtomicLong(); LongAdder sharded = new LongAdder();
        long t1 = time(threads, () -> { for (int i = 0; i < likesEach; i++) single.incrementAndGet(); });
        long t2 = time(threads, () -> { for (int i = 0; i < likesEach; i++) sharded.increment(); });
        System.out.printf("single AtomicLong : %,d likes (all threads fight over one memory location)%n", single.get());
        System.out.printf("sharded LongAdder : %,d likes (threads write different cells; read = sum of cells)%n", sharded.sum());
        // 2. Buffer-and-flush to a 'database'
        ConcurrentHashMap<String, LongAdder> buffer = new ConcurrentHashMap<>(); Map<String, Long> db = new TreeMap<>(); int[] dbWrites = {0};
        ScheduledExecutorService flusher = Executors.newSingleThreadScheduledExecutor();
        flusher.scheduleAtFixedRate(() -> {
            for (String k : buffer.keySet()) { long d = buffer.get(k).sumThenReset(); if (d > 0) { synchronized (db) { db.merge(k, d, Long::sum); dbWrites[0]++; } } }
        }, 20, 20, TimeUnit.MILLISECONDS);
        time(threads, () -> { for (int i = 0; i < 50_000; i++) buffer.computeIfAbsent("post:" + (i % 3), k -> new LongAdder()).increment(); });
        Thread.sleep(60); flusher.shutdown(); flusher.awaitTermination(1, TimeUnit.SECONDS);
        for (String k : buffer.keySet()) { long d = buffer.get(k).sumThenReset(); if (d > 0) { db.merge(k, d, Long::sum); dbWrites[0]++; } }
        System.out.printf("buffered counting : db=%s from %,d likes with only %s DB writes%n", db, threads * 50_000, dbWrites[0] < 100 ? "a few dozen" : String.valueOf(dbWrites[0]));
    }

    static long time(int threads, Runnable r) throws Exception {
        ExecutorService p = Executors.newFixedThreadPool(threads); long t = System.nanoTime();
        List<Future<?>> fs = new ArrayList<>(); for (int i = 0; i < threads; i++) fs.add(p.submit(r));
        for (Future<?> f : fs) f.get(); p.shutdown(); return System.nanoTime() - t;
    }
}
''', ["Count unique likers: keep a `Set<userId>` per post so liking twice doesn't count, and measure memory for 1 million users.",
      "Simulate a crash before the flush and show how many likes are lost; then add a write-ahead list.",
      "Implement a time-windowed counter: likes in the last 60 seconds using 60 one-second buckets."])

J("notification-pattern", r'''
import java.util.*;

public class NotificationPipelineDemo {
    record Event(String id, String user, String type, int priority) {}
    record Prefs(boolean push, boolean email, boolean sms, int quietFrom, int quietTo) {}
    static final Map<String, Prefs> prefs = Map.of("asha", new Prefs(true, true, false, 23, 7), "ravi", new Prefs(false, true, true, 0, 0));
    static final Set<String> sent = new HashSet<>();
    static final Map<String, Integer> perUserToday = new HashMap<>();

    static void dispatch(Event e, int hour) {
        Prefs p = prefs.get(e.user());
        List<String> channels = new ArrayList<>();
        if (p.push()) channels.add("push"); if (p.email()) channels.add("email"); if (p.sms() && e.priority() == 1) channels.add("sms");
        for (String ch : channels) {
            String dedupe = e.id() + ":" + ch;
            if (!sent.add(dedupe)) { System.out.println("  skip duplicate " + dedupe); continue; }
            boolean quiet = p.quietFrom() > p.quietTo() ? (hour >= p.quietFrom() || hour < p.quietTo()) : (hour >= p.quietFrom() && hour < p.quietTo());
            if (quiet && e.priority() > 1 && ch.equals("push")) { System.out.println("  " + e.user() + " " + ch + " delayed to morning (quiet hours)"); continue; }
            if (e.priority() > 1 && perUserToday.merge(e.user(), 1, Integer::sum) > 3) { System.out.println("  " + e.user() + " " + ch + " dropped: daily marketing cap"); continue; }
            System.out.println("  -> " + ch + "-queue: " + e.type() + " for " + e.user());
        }
    }

    public static void main(String[] args) {
        System.out.println("23:30 OTP for asha (priority 1):"); dispatch(new Event("e1", "asha", "OTP 482913", 1), 23);
        System.out.println("23:31 promo for asha (priority 3):"); dispatch(new Event("e2", "asha", "Diwali sale", 3), 23);
        System.out.println("10:00 shipment for ravi:"); dispatch(new Event("e3", "ravi", "order shipped", 1), 10);
        System.out.println("10:00 same event delivered twice by the queue:"); dispatch(new Event("e3", "ravi", "order shipped", 1), 10);
    }
}
''', ["Add retries with a fallback provider: if 'sms-provider-A' fails twice, use 'sms-provider-B'.",
      "Add templates: `ORDER_SHIPPED` -> 'Hi {name}, order {id} has shipped' filled per user.",
      "Use a `PriorityBlockingQueue` so OTPs are always sent before marketing messages."])

J("chat-delivery", r'''
import java.util.*;

public class ChatDeliveryDemo {
    record Msg(String clientId, String from, String to, String text, long seq) {}
    static final Map<String, List<Msg>> store = new HashMap<>();                 // conversation -> messages
    static final Map<String, Long> seqByConv = new HashMap<>();
    static final Map<String, String> connectedServer = new HashMap<>(Map.of("asha", "chat-A"));   // presence/routing table
    static final Set<String> seenClientIds = new HashSet<>();

    static String conv(String a, String b) { return a.compareTo(b) < 0 ? a + ":" + b : b + ":" + a; }

    static String send(String from, String to, String clientId, String text) {
        if (!seenClientIds.add(clientId)) return "ack (duplicate " + clientId + " ignored)";
        String c = conv(from, to); long seq = seqByConv.merge(c, 1L, Long::sum);
        Msg m = new Msg(clientId, from, to, text, seq);
        store.computeIfAbsent(c, k -> new ArrayList<>()).add(m);                    // persist BEFORE acking
        String server = connectedServer.get(to);
        String delivery = server == null ? to + " offline -> push notification" : "routed to " + server + " -> delivered to " + to;
        return "ack ✓ seq=" + seq + ", " + delivery;
    }

    static List<String> syncAfter(String user, String other, long lastSeq) {
        return store.getOrDefault(conv(user, other), List.of()).stream().filter(m -> m.seq() > lastSeq).map(m -> m.seq() + ":" + m.text()).toList();
    }

    public static void main(String[] args) {
        System.out.println("asha -> ravi 'hi'        : " + send("asha", "ravi", "c-1", "hi"));
        System.out.println("asha -> ravi 'you there?': " + send("asha", "ravi", "c-2", "you there?"));
        System.out.println("network retry of c-2     : " + send("asha", "ravi", "c-2", "you there?"));
        connectedServer.put("ravi", "chat-B");
        System.out.println("ravi reconnects, had seen seq 0 -> sync " + syncAfter("ravi", "asha", 0));
        System.out.println("ravi -> asha 'yes!'      : " + send("ravi", "asha", "c-3", "yes!"));
        System.out.println("asha's phone (seen seq 2) syncs -> " + syncAfter("asha", "ravi", 2));
    }
}
''', ["Add read receipts: store each user's last read seq and print '✓✓ read' when it passes a message.",
      "Add group chats: one message fans out to N members, each with their own delivery state.",
      "Add multi-device: asha has a phone and a laptop, each tracking its own last synced seq."])

J("video-streaming", r'''
import java.util.*;

public class AdaptiveBitrateDemo {
    record Rendition(String name, int kbps) {}
    static final List<Rendition> ladder = List.of(new Rendition("240p", 400), new Rendition("360p", 800), new Rendition("480p", 1400),
        new Rendition("720p", 2800), new Rendition("1080p", 5000), new Rendition("4K", 16000));

    public static void main(String[] args) {
        int segmentSec = 4; double buffer = 0, estimateKbps = 0;
        int[] networkKbps = {6000, 8000, 8000, 1500, 1200, 6000, 9000, 25000, 25000};   // measured per segment (tunnel at 4-5)
        int stalls = 0;
        System.out.println("seg  network   pick    buffer  note");
        for (int i = 0; i < networkKbps.length; i++) {
            Rendition pick = ladder.get(0);
            if (i > 0) for (Rendition r : ladder) if (r.kbps() <= estimateKbps * 0.8 && (buffer > 6 || r.kbps() <= 1400)) pick = r;
            double downloadSec = pick.kbps() * segmentSec / (double) networkKbps[i];
            String note = "";
            if (downloadSec > buffer && i > 0) { stalls++; note = "STALL (rebuffering)"; buffer = 0; } else buffer -= downloadSec;
            buffer = Math.max(0, buffer) + segmentSec;
            estimateKbps = i == 0 ? networkKbps[i] : 0.7 * estimateKbps + 0.3 * networkKbps[i];   // smoothed throughput estimate
            System.out.printf("%3d  %5d kbps  %-6s  %4.1f s  %s%n", i + 1, networkKbps[i], pick.name(), buffer, note);
        }
        System.out.println("stalls: " + stalls + " - the smoothed throughput estimate lagged behind the sudden drop; a buffer-based rule (practice task 1) reacts faster");
        long totalKbps = ladder.stream().mapToLong(Rendition::kbps).sum();
        System.out.printf("storage for a 10-minute video, all renditions: %.2f GB%n", totalKbps * 1000L / 8.0 * 600 / 1e9);
    }
}
''', ["Use a buffer-based rule instead (BOLA-style): pick quality by buffer level only, and compare stalls.",
      "Split a 'video' (an int array) into 4-second segments and 'transcode' them in parallel with an `ExecutorService`.",
      "Generate an HLS `.m3u8` master playlist text listing all renditions."])

J("file-sync", r'''
import java.security.MessageDigest;
import java.util.*;

public class FileSyncDemo {
    static final int CHUNK = 4;                                                 // 4 bytes for the demo (4 MB in real life)
    static final Map<String, byte[]> blockStore = new HashMap<>();              // hash -> bytes (dedup across all users)
    static final Map<String, List<String>> fileVersions = new HashMap<>();      // path -> chunk hashes of latest version
    static final Map<String, Integer> versionNo = new HashMap<>();

    static String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)).substring(0, 6); }

    static void upload(String device, String path, String content, int baseVersion) throws Exception {
        int current = versionNo.getOrDefault(path, 0);
        if (baseVersion != current) {                                         // someone else changed it meanwhile
            String copy = path.replace(".txt", " (" + device + "'s conflicted copy).txt");
            System.out.println(device + ": conflict on " + path + " (based on v" + baseVersion + ", server has v" + current + ") -> saved as '" + copy + "'");
            upload(device, copy, content, versionNo.getOrDefault(copy, 0)); return;
        }
        byte[] data = content.getBytes(); List<String> hashes = new ArrayList<>(); int uploaded = 0;
        for (int i = 0; i < data.length; i += CHUNK) {
            byte[] c = Arrays.copyOfRange(data, i, Math.min(data.length, i + CHUNK)); String h = sha(c); hashes.add(h);
            if (!blockStore.containsKey(h)) { blockStore.put(h, c); uploaded++; }
        }
        fileVersions.put(path, hashes); versionNo.put(path, current + 1);
        System.out.println(device + ": " + path + " v" + (current + 1) + " = " + hashes.size() + " chunks, uploaded " + uploaded + " new, skipped " + (hashes.size() - uploaded));
    }

    public static void main(String[] args) throws Exception {
        upload("laptop", "notes.txt", "AAAABBBBCCCCDDDD", 0);
        upload("laptop", "notes.txt", "AAAABBBBXXXXDDDD", 1);                   // edit in the middle: only 1 chunk changes
        upload("phone", "copy.txt", "AAAABBBBCCCCDDDD", 0);                     // same content elsewhere: fully deduplicated
        upload("phone", "notes.txt", "AAAAZZZZCCCCDDDD", 1);                    // phone edited an old version offline
        System.out.println("block store holds " + blockStore.size() + " unique chunks for 4 files/versions");
    }
}
''', ["Add download sync: given a device's chunk list for a file and the server's, fetch only missing chunks.",
      "Use content-defined chunking (cut where a rolling hash hits a pattern) so inserting a byte at the start doesn't change every chunk.",
      "Keep the last 3 versions of each file and implement restore."])

J("payments-ledger", r'''
import java.util.*;

public class LedgerDemo {
    record Entry(long txId, String account, long debitPaise, long creditPaise) {}
    static final List<Entry> ledger = new ArrayList<>();                       // append-only
    static final Map<String, Long> idempotency = new HashMap<>();
    static long txSeq = 0;

    static long post(String idemKey, List<Entry> lines) {
        if (idempotency.containsKey(idemKey)) return idempotency.get(idemKey);
        long d = lines.stream().mapToLong(Entry::debitPaise).sum(), c = lines.stream().mapToLong(Entry::creditPaise).sum();
        if (d != c) throw new IllegalArgumentException("unbalanced transaction: debits " + d + " != credits " + c);
        long id = ++txSeq;
        for (Entry e : lines) ledger.add(new Entry(id, e.account(), e.debitPaise(), e.creditPaise()));
        idempotency.put(idemKey, id); return id;
    }
    static long balance(String acct) { return ledger.stream().filter(e -> e.account().equals(acct)).mapToLong(e -> e.creditPaise() - e.debitPaise()).sum(); }
    static String rs(long paise) { return String.format("Rs %,.2f", paise / 100.0); }

    public static void main(String[] args) {
        post("topup-1", List.of(new Entry(0, "bank:settlement", 200_000, 0), new Entry(0, "wallet:asha", 0, 200_000)));
        post("pay-77", List.of(new Entry(0, "wallet:asha", 100_000, 0), new Entry(0, "merchant:shoeshop", 0, 98_000), new Entry(0, "revenue:fees", 0, 2_000)));
        post("pay-77", List.of(new Entry(0, "wallet:asha", 100_000, 0), new Entry(0, "merchant:shoeshop", 0, 98_000), new Entry(0, "revenue:fees", 0, 2_000)));   // retry
        try { post("bad-1", List.of(new Entry(0, "wallet:asha", 500, 0), new Entry(0, "merchant:shoeshop", 0, 400))); }
        catch (IllegalArgumentException e) { System.out.println("rejected: " + e.getMessage()); }
        post("refund-77", List.of(new Entry(0, "merchant:shoeshop", 98_000, 0), new Entry(0, "revenue:fees", 2_000, 0), new Entry(0, "wallet:asha", 0, 100_000)));
        ledger.forEach(e -> System.out.printf("tx%d %-18s debit %10s credit %10s%n", e.txId(), e.account(), e.debitPaise() > 0 ? rs(e.debitPaise()) : "", e.creditPaise() > 0 ? rs(e.creditPaise()) : ""));
        for (String a : List.of("wallet:asha", "merchant:shoeshop", "revenue:fees")) System.out.println("balance " + a + " = " + rs(balance(a)));
        System.out.println("sum of all balances (+ settlement) = " + rs(ledger.stream().mapToLong(e -> e.creditPaise() - e.debitPaise()).sum()) + "  (always zero)");
    }
}
''', ["Add a reconciliation job that compares the ledger with a 'bank statement' list and prints mismatches.",
      "Add a payment state machine (CREATED -> AUTHORIZED -> CAPTURED/FAILED -> REFUNDED) that rejects illegal transitions.",
      "Store balances in a separate table updated in the same 'transaction' and verify they always equal the ledger sum."])

J("inventory-overselling", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class OversellingDemo {
    static int stockUnsafe; static final AtomicInteger stockSafe = new AtomicInteger();

    static int flashSale(boolean safe, int stock, int buyers) throws Exception {
        stockUnsafe = stock; stockSafe.set(stock); AtomicInteger orders = new AtomicInteger();
        ExecutorService pool = Executors.newFixedThreadPool(16); CountDownLatch go = new CountDownLatch(1); List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < buyers; i++) fs.add(pool.submit(() -> {
            go.await();
            if (!safe) { if (stockUnsafe > 0) { Thread.yield(); stockUnsafe--; orders.incrementAndGet(); } }   // check-then-act race
            else {
                while (true) {                                            // UPDATE ... SET stock = stock - 1 WHERE stock >= 1
                    int s = stockSafe.get(); if (s < 1) break;
                    if (stockSafe.compareAndSet(s, s - 1)) { orders.incrementAndGet(); break; }
                }
            }
            return null;
        }));
        go.countDown(); for (Future<?> f : fs) f.get(); pool.shutdown();
        return orders.get();
    }

    public static void main(String[] args) throws Exception {
        int worst = 0; for (int run = 0; run < 20; run++) worst = Math.max(worst, flashSale(false, 10, 5000));
        System.out.println("check-then-act : 10 PS5s, 5,000 buyers -> up to " + (worst > 10 ? worst + " orders (OVERSOLD)" : worst + " orders (race didn't show this time; it will in production)"));
        System.out.println("conditional decrement: 10 PS5s, 5,000 buyers -> " + flashSale(true, 10, 5000) + " orders, never more");
        // Reservation with TTL: hold for 10 min; unpaid holds return to stock
        Map<String, Long> holds = new LinkedHashMap<>(Map.of("asha", 0L, "ravi", 2L, "zoya", 9L)); int available = 0; long now = 12;
        for (var it = holds.entrySet().iterator(); it.hasNext(); ) { var h = it.next(); if (now - h.getValue() >= 10) { it.remove(); available++; } }
        System.out.println("at minute 12, expired unpaid holds released -> " + available + " back in stock, still held: " + holds.keySet());
    }
}
''', ["Split stock into 4 buckets (separate counters) and pick a random bucket per buyer to cut contention.",
      "Put buyers in a `LinkedBlockingQueue` 'waiting room' and let a single worker sell in order.",
      "Make reservations and payments a mini state machine (HELD -> PAID or EXPIRED) with timestamps."])

J("leaderboard-pattern", r'''
import java.util.*;

public class LeaderboardDemo {
    // Sorted set: member -> score map + a TreeSet ordered by (score desc, time asc, name) for O(log n) updates and top-k.
    record Entry(String member, long score, long achievedAt) {}
    static final Map<String, Entry> byMember = new HashMap<>();
    static final TreeSet<Entry> ranked = new TreeSet<>(Comparator.comparingLong((Entry e) -> -e.score()).thenComparingLong(Entry::achievedAt).thenComparing(Entry::member));

    static void zincrby(String m, long by, long now) {
        Entry old = byMember.get(m); if (old != null) ranked.remove(old);
        Entry e = new Entry(m, (old == null ? 0 : old.score()) + by, now); byMember.put(m, e); ranked.add(e);
    }
    static List<String> top(int k) { return ranked.stream().limit(k).map(e -> e.member() + "=" + e.score()).toList(); }
    static int rank(String m) { return ranked.headSet(byMember.get(m)).size() + 1; }       // O(n) here; a skip list with spans makes it O(log n)

    public static void main(String[] args) {
        zincrby("asha", 50, 1); zincrby("ravi", 80, 2); zincrby("zoya", 70, 3); zincrby("asha", 40, 4); zincrby("kiran", 90, 5);
        System.out.println("top 3: " + top(3));
        System.out.println("rank of zoya: " + rank("zoya"));
        zincrby("zoya", 20, 6);
        System.out.println("zoya +20 -> top 3: " + top(3) + " (ties: asha reached 90 first, ahead of zoya)");
        Random r = new Random(1); for (int i = 0; i < 100_000; i++) zincrby("p" + i, r.nextInt(100), 10 + i);
        System.out.println("100,003 players, top 3: " + top(3) + ", asha's rank: " + rank("asha"));
    }
}
''', ["Add 'players around me': 2 above and 2 below a given member.",
      "Keep a separate leaderboard per day (key `lb:2026-11-26`) and compute a weekly board by merging 7 days.",
      "Shard by score range (0–49, 50–99) and compute a global rank as (players in higher shards + rank in own shard)."])

J("crawler-politeness", r'''
import java.util.*;

public class PoliteCrawlerDemo {
    record Url(String host, String path, int priority) {}
    static final Map<String, Deque<Url>> perHost = new TreeMap<>();               // back queues: one per host
    static final PriorityQueue<Object[]> nextAllowed = new PriorityQueue<>(Comparator.comparingLong(a -> (Long) a[1]));   // {host, time}
    static final Set<String> seen = new HashSet<>();
    static final Map<String, Set<String>> robotsDisallow = Map.of("shop.com", Set.of("/cart"));
    static final Map<String, Long> crawlDelayMs = Map.of("shop.com", 1000L, "news.com", 500L, "blog.com", 500L);

    static void add(Url u) {
        if (!seen.add(u.host() + u.path())) return;                               // dedup (a Bloom filter at scale)
        if (robotsDisallow.getOrDefault(u.host(), Set.of()).stream().anyMatch(u.path()::startsWith)) { System.out.println("  robots.txt disallows " + u.host() + u.path()); return; }
        boolean newHost = !perHost.containsKey(u.host());
        perHost.computeIfAbsent(u.host(), k -> new ArrayDeque<>()).add(u);
        if (newHost) nextAllowed.add(new Object[]{u.host(), 0L});
    }

    public static void main(String[] args) {
        for (String p : List.of("/", "/a", "/b", "/cart", "/a")) add(new Url("shop.com", p, 1));
        for (String p : List.of("/", "/today")) add(new Url("news.com", p, 1));
        add(new Url("blog.com", "/", 2));
        long clock = 0; int fetched = 0;
        while (!nextAllowed.isEmpty() && fetched < 10) {
            Object[] slot = nextAllowed.poll(); String host = (String) slot[0]; clock = Math.max(clock, (Long) slot[1]);
            Url u = perHost.get(host).poll(); fetched++;
            System.out.printf("t=%4d ms fetch %s%s%n", clock, u.host(), u.path());
            if (!perHost.get(host).isEmpty()) nextAllowed.add(new Object[]{host, clock + crawlDelayMs.get(host)});    // politeness delay per host
        }
        System.out.println("each host is hit at most once per crawl-delay, while different hosts are fetched in parallel");
    }
}
''', ["Add front queues by priority so priority-1 URLs are routed to back queues before priority-2 ones.",
      "Back off: if a host returns 503, double its crawl delay.",
      "Parse links from a fake HTML string with a regex and add them to the frontier (with a max depth of 2)."])

J("recsys-ml", r'''
import java.util.*;

public class TwoStageRecsDemo {
    // Stage 1: cheap candidate generation (embedding similarity). Stage 2: richer ranking. Stage 3: diversity re-rank.
    record Item(String id, String category, double[] emb, double ctr, int ageDays) {}

    static double cos(double[] a, double[] b) { double d = 0, na = 0, nb = 0; for (int i = 0; i < a.length; i++) { d += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; } return d / Math.sqrt(na * nb); }

    public static void main(String[] args) {
        Random r = new Random(3); List<Item> catalog = new ArrayList<>(); String[] cats = {"cricket", "cooking", "tech", "music"};
        for (int i = 0; i < 2000; i++) { String c = cats[i % 4]; double[] e = new double[8]; for (int k = 0; k < 8; k++) e[k] = r.nextGaussian() * 0.3 + (k == i % 4 ? 1.5 : 0) + (k == 4 + (i % 2) ? 0.5 : 0); catalog.add(new Item("v" + i, c, e, 0.01 + r.nextDouble() * 0.1, r.nextInt(60))); }
        double[] user = {1.2, 0.1, 0.9, 0.0, 0.3, 0.2, 0, 0};                    // likes cricket and tech
        List<Item> candidates = catalog.stream().sorted(Comparator.comparingDouble((Item it) -> -cos(user, it.emb()))).limit(50).toList();
        System.out.println("stage 1: 2,000 items -> 50 candidates by embedding similarity (an ANN index at scale)");
        List<Item> ranked = new ArrayList<>(candidates);
        ranked.sort(Comparator.comparingDouble((Item it) -> -(0.6 * cos(user, it.emb()) + 3 * it.ctr() + 0.2 / (1 + it.ageDays()))));
        System.out.println("stage 2: ranked by similarity + predicted CTR + freshness");
        List<Item> page = new ArrayList<>(); Map<String, Integer> perCat = new HashMap<>();
        for (Item it : ranked) { if (perCat.merge(it.category(), 1, Integer::sum) <= 3) page.add(it); if (page.size() == 5) break; }
        System.out.println("stage 3: max 3 per category ->");
        for (Item it : page) System.out.printf("  %-6s %-8s sim %.2f ctr %.3f age %2dd%n", it.id(), it.category(), cos(user, it.emb()), it.ctr(), it.ageDays());
    }
}
''', ["Log 'impressions' and 'clicks' for the shown items and update each item's CTR online.",
      "Replace the full sort in stage 1 with a `PriorityQueue` of size 50 (top-k in O(n log k)).",
      "Add an A/B test: users with an even id get the ranking with freshness, odd ids without; compare simulated click rates."])

J("llm-systems", r'''
import java.util.*;

public class RagPipelineDemo {
    // Toy RAG: embed docs as word-count vectors, retrieve top-k by cosine, build a prompt, and estimate token cost.
    static Map<String, Integer> embed(String text) { Map<String, Integer> v = new HashMap<>(); for (String w : text.toLowerCase().split("\\W+")) if (w.length() > 2) v.merge(w, 1, Integer::sum); return v; }
    static double cos(Map<String, Integer> a, Map<String, Integer> b) {
        double d = 0; for (var e : a.entrySet()) d += e.getValue() * b.getOrDefault(e.getKey(), 0);
        return d / Math.sqrt(a.values().stream().mapToDouble(x -> x * x).sum() * b.values().stream().mapToDouble(x -> x * x).sum());
    }

    public static void main(String[] args) {
        List<String> chunks = List.of(
            "Refunds are processed within 5 business days to the original payment method.",
            "Shipping is free on orders above Rs 499 across India.",
            "You can cancel an order before it is shipped from the My Orders page.",
            "Gift cards cannot be refunded or exchanged for cash.");
        Map<String, Map<String, Integer>> index = new LinkedHashMap<>(); for (String c : chunks) index.put(c, embed(c));
        String question = "How many days do refunds take?";
        Map<String, Integer> q = embed(question);
        List<Map.Entry<String, Double>> top = index.entrySet().stream().map(e -> Map.entry(e.getKey(), cos(q, e.getValue())))
            .sorted(Map.Entry.<String, Double>comparingByValue().reversed()).limit(2).toList();
        System.out.println("retrieved:"); top.forEach(e -> System.out.printf("  %.2f  %s%n", e.getValue(), e.getKey()));
        String prompt = "Answer using only the context. Cite the line you used.\nContext:\n- " + top.get(0).getKey() + "\n- " + top.get(1).getKey() + "\nQuestion: " + question;
        int promptTokens = prompt.split("\\s+").length * 4 / 3, outputTokens = 40;
        System.out.println("prompt ~" + promptTokens + " tokens, answer ~" + outputTokens + " tokens");
        Map<String, String> cache = new HashMap<>();
        for (int i = 0; i < 2; i++) {
            String key = question.toLowerCase().trim();
            System.out.println(cache.containsKey(key) ? "ask again -> served from answer cache (0 GPU time)" : "ask -> LLM call, stream tokens back over SSE");
            cache.putIfAbsent(key, "Refunds take up to 5 business days [1]");
        }
        double reqPerSec = 200, tokPerReq = promptTokens + outputTokens, gpuTokPerSec = 2000;
        System.out.printf("capacity: %.0f req/s x %.0f tokens = %.0f tokens/s -> ~%.0f GPUs at %.0f tokens/s each%n", reqPerSec, tokPerReq, reqPerSec * tokPerReq, Math.ceil(reqPerSec * tokPerReq / gpuTokPerSec), gpuTokPerSec);
    }
}
''', ["Split a long document into overlapping chunks of 40 words with 10-word overlap before indexing.",
      "Add a per-user token budget (rate limit in tokens per minute, not requests).",
      "Route easy questions (short, matching an FAQ) to a 'small model' and the rest to a 'large model', and compute the cost saving."])

J("read-write-heavy", r'''
import java.util.*;

public class ReadWriteHeavyDemo {
    public static void main(String[] args) {
        // Read-heavy: a news article read 100,000 times, edited twice -> cache it
        int reads = 100_000, dbReads = 0; Map<String, String> cache = new HashMap<>();
        for (int i = 0; i < reads; i++) {
            if (i == 40_000 || i == 80_000) cache.remove("article:1");          // edit -> invalidate
            if (cache.get("article:1") == null) { dbReads++; cache.put("article:1", "<html>"); }
        }
        System.out.printf("read-heavy : %,d reads -> %d DB reads (cache absorbs %.3f%%)%n", reads, dbReads, 100.0 * (reads - dbReads) / reads);
        // Write-heavy: 1,000,000 sensor readings -> append to a log and write in batches instead of one row at a time
        int events = 1_000_000, batch = 5_000; List<int[]> log = new ArrayList<>(); int writeCalls = 0; List<int[]> buf = new ArrayList<>();
        Random r = new Random(1);
        for (int i = 0; i < events; i++) {
            buf.add(new int[]{i % 1000, r.nextInt(50)});
            if (buf.size() == batch) { log.addAll(buf); buf.clear(); writeCalls++; }
        }
        System.out.printf("write-heavy: %,d events -> %,d batched sequential appends instead of %,d single-row writes%n", events, writeCalls, events);
        // ...and aggregate asynchronously for reads (per-sensor average)
        double[] sum = new double[1000]; int[] cnt = new int[1000];
        for (int[] e : log) { sum[e[0]] += e[1]; cnt[e[0]]++; }
        System.out.printf("rollup for dashboards: sensor 7 avg %.1f over %d readings%n", sum[7] / cnt[7], cnt[7]);
    }
}
''', ["Add a CDN layer in front of the cache that serves 80% of article reads and recount DB reads.",
      "Write the batched log to a real file with `BufferedOutputStream` and time 1 big write vs 1,000,000 small `write` calls with `flush`.",
      "Keep a per-minute rollup updated incrementally as batches arrive instead of recomputing."])

J("hotspots", r'''
import java.util.*;

public class HotspotDemo {
    static int mix(int h) { h ^= h >>> 16; h *= 0x85ebca6b; h ^= h >>> 13; h *= 0xc2b2ae35; return h ^ (h >>> 16); }   // murmur3 finaliser
    public static void main(String[] args) {
        int shards = 5; Random r = new Random(2);
        int[] load = new int[shards], loadFixed = new int[shards];
        for (int i = 0; i < 100_000; i++) {
            String key = r.nextInt(100) < 40 ? "celebrity:1" : "user:" + r.nextInt(1_000_000);   // 40% of traffic hits one key
            load[Math.floorMod(mix(key.hashCode()), shards)]++;
            int home = Math.floorMod(mix(key.hashCode()), shards);
            if (key.equals("celebrity:1")) loadFixed[(home + r.nextInt(shards)) % shards]++;   // copy #i of the hot key lives on shard home+i; readers pick a random copy
            else loadFixed[home]++;
        }
        System.out.println("requests per shard, one hot key : " + Arrays.toString(load));
        System.out.println("hot key copied to all 5 shards   : " + Arrays.toString(loadFixed));
        // Time-based partition key: all of today's writes hit one partition; add a salt
        int[] byDate = new int[8], salted = new int[8];
        for (int i = 0; i < 10_000; i++) { byDate[Math.floorMod("2026-11-26".hashCode(), 8)]++; salted[Math.floorMod(("2026-11-26#" + (i % 8)).hashCode(), 8)]++; }
        System.out.println("partition key = date            : " + Arrays.toString(byDate));
        System.out.println("partition key = (date, i % 8)   : " + Arrays.toString(salted) + "  (reads must query all 8 salts)");
    }
}
''', ["Detect hot keys automatically: count accesses per key in a 1-second window and flag the top 1%.",
      "Add an in-process cache in front of the shards for keys flagged as hot and recount shard load.",
      "Choose a better salt function so the 8 salted partitions are perfectly even."])
