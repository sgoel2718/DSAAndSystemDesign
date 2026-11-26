"""Java practice programs: HLD questions 1-12 (core of each design as runnable code)."""
from sd_j_util import J

J("urlshortener-hld", r'''
import java.util.*;
import java.util.concurrent.atomic.*;

public class UrlShortenerSystem {
    // Key generation (counter ranges + base62), storage, cache-aside reads, 301/302 redirects, expiry and click counting.
    static final String B62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    static String base62(long n) { StringBuilder sb = new StringBuilder(); do { sb.append(B62.charAt((int) (n % 62))); n /= 62; } while (n > 0); return sb.reverse().toString(); }

    static class RangeAllocator {                                              // like ZooKeeper handing out id blocks to each app server
        private final AtomicLong next = new AtomicLong(1_000_000_000L);
        long[] lease(int size) { long s = next.getAndAdd(size); return new long[]{s, s + size}; }
    }
    static class AppServer {
        final String name; final RangeAllocator alloc; long cur, end;
        AppServer(String name, RangeAllocator a) { this.name = name; alloc = a; }
        long nextId() { if (cur == end) { long[] r = alloc.lease(1000); cur = r[0]; end = r[1]; } return cur++; }
    }
    record Link(String code, String longUrl, long expiresAt, String owner) {}

    static final Map<String, Link> db = new HashMap<>();
    static final Map<String, String> cache = new LinkedHashMap<>(16, .75f, true) { protected boolean removeEldestEntry(Map.Entry<String, String> e) { return size() > 2; } };
    static final Map<String, Long> clicks = new TreeMap<>();
    static int dbReads = 0;

    static String shorten(AppServer s, String url, String custom, long ttl, long now) {
        String code = custom != null ? custom : base62(s.nextId());
        if (db.containsKey(code)) return "409 alias taken";
        db.put(code, new Link(code, url, ttl > 0 ? now + ttl : Long.MAX_VALUE, "user-42"));
        return "https://sho.rt/" + code;
    }

    static String redirect(String code, long now) {
        String url = cache.get(code);
        if (url == null) {
            dbReads++; Link l = db.get(code);
            if (l == null) return "404";
            if (l.expiresAt() <= now) return "410 Gone (expired)";
            url = l.longUrl(); cache.put(code, url);
        }
        clicks.merge(code, 1L, Long::sum);                                     // in production: async event to Kafka
        return "302 Location: " + url;
    }

    public static void main(String[] args) {
        RangeAllocator zk = new RangeAllocator(); AppServer a = new AppServer("app-1", zk), b = new AppServer("app-2", zk);
        String s1 = shorten(a, "https://en.wikipedia.org/wiki/System_design", null, 0, 0);
        String s2 = shorten(b, "https://leetcode.com/problems/lru-cache/", null, 0, 0);
        String s3 = shorten(a, "https://sale.example.com/diwali", "diwali", 100, 0);
        System.out.println("app-1 -> " + s1 + "\napp-2 -> " + s2 + "  (different id ranges: no coordination per request)\ncustom -> " + s3);
        System.out.println("custom again -> " + shorten(b, "https://x.com", "diwali", 0, 0));
        String c1 = s1.substring(15);
        for (int i = 0; i < 5; i++) redirect(c1, 10);
        System.out.println("redirect " + c1 + " -> " + redirect(c1, 10) + " | db reads so far " + dbReads + " (rest from cache)");
        System.out.println("redirect diwali at t=50  -> " + redirect("diwali", 50));
        cache.clear();
        System.out.println("redirect diwali at t=150 -> " + redirect("diwali", 150));
        System.out.println("redirect nope            -> " + redirect("nope", 150));
        System.out.println("click counts: " + clicks);
        System.out.printf("7-char base62 codes give %,.0f possible links%n", Math.pow(62, 7));
    }
}
''', ["Replace the counter with a hash approach: first 7 chars of base62(MD5(url)), and handle collisions by appending a salt.",
      "Make the same long URL from the same user return the existing short code (dedup index).",
      "Add a per-user rate limit of 10 links per minute on `shorten`."])

J("pastebin-hld", r'''
import java.security.MessageDigest;
import java.util.*;

public class PastebinSystem {
    // Metadata in a DB, content in object storage (keyed by content hash), expiry cleanup, and a size limit.
    record Paste(String id, String owner, String objectKey, int sizeBytes, long expiresAt, String visibility) {}
    static final Map<String, Paste> metadata = new LinkedHashMap<>();
    static final Map<String, String> objectStore = new HashMap<>();
    static final int MAX = 1_000_000; static int seq = 0;

    static String sha(String s) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getBytes())).substring(0, 10); }

    static String create(String owner, String text, long ttl, String visibility, long now) throws Exception {
        if (text.length() > MAX) return "413 too large";
        String key = "pastes/" + sha(text);
        objectStore.putIfAbsent(key, text);                                     // identical content stored once
        String id = Long.toString(1_000_000L + (++seq) * 7919, 36);
        metadata.put(id, new Paste(id, owner, key, text.length(), now + ttl, visibility));
        return id;
    }
    static String read(String id, String viewer, long now) {
        Paste p = metadata.get(id);
        if (p == null || p.expiresAt() <= now) return "404";
        if (p.visibility().equals("private") && !p.owner().equals(viewer)) return "403";
        return objectStore.get(p.objectKey());
    }
    static int cleanup(long now) {                                              // background job: delete expired metadata, then orphaned blobs
        int removed = 0;
        for (Iterator<Paste> it = metadata.values().iterator(); it.hasNext(); ) if (it.next().expiresAt() <= now) { it.remove(); removed++; }
        Set<String> live = new HashSet<>(); metadata.values().forEach(p -> live.add(p.objectKey()));
        objectStore.keySet().retainAll(live);
        return removed;
    }

    public static void main(String[] args) throws Exception {
        String a = create("asha", "public static void main(String[] args) {}", 3600, "public", 0);
        String b = create("ravi", "public static void main(String[] args) {}", 60, "public", 0);
        String c = create("asha", "my secret notes", 3600, "private", 0);
        System.out.println("created " + a + ", " + b + ", " + c + "; blobs stored: " + objectStore.size() + " (duplicate content shared)");
        System.out.println("ravi reads " + a + " -> " + read(a, "ravi", 10));
        System.out.println("ravi reads " + c + " -> " + read(c, "ravi", 10));
        System.out.println("t=100 read " + b + " -> " + read(b, "x", 100) + " (expired)");
        System.out.println("cleanup removed " + cleanup(100) + " paste(s); blobs left " + objectStore.size());
        System.out.println("huge paste -> " + create("asha", "x".repeat(MAX + 1), 60, "public", 0));
    }
}
''', ["Add reference counting so a blob is deleted only when no paste uses it (instead of the full scan).",
      "Add 'burn after reading': the paste is deleted after its first successful read.",
      "Compress text with `GZIPOutputStream` before storing and print the size saving for a 50 KB paste."])

J("ratelimiter-hld", r'''
import java.util.*;
import java.util.concurrent.*;

public class DistributedRateLimiterSystem {
    // Gateways share counters in one "Redis" (here a synchronized store). Sliding-window-counter algorithm per (user, rule).
    static class RedisLike {
        private final Map<String, Long> kv = new HashMap<>();
        synchronized long[] incrAndGetWindows(String key, long windowStart, long prevStart) {   // atomic like a Lua script
            long cur = kv.merge(key + ":" + windowStart, 1L, Long::sum);
            long prev = kv.getOrDefault(key + ":" + prevStart, 0L);
            return new long[]{cur, prev};
        }
    }
    record Rule(String name, int limit, long windowMs) {}
    static final Map<String, Rule> rules = Map.of("free", new Rule("free", 5, 1000), "pro", new Rule("pro", 20, 1000));

    static class Gateway {
        final String name; final RedisLike redis; boolean redisDown = false;
        Gateway(String n, RedisLike r) { name = n; redis = r; }
        String handle(String user, String plan, long now) {
            Rule r = rules.get(plan);
            if (redisDown) return "200 (fail-open: limiter unavailable)";
            long win = now / r.windowMs() * r.windowMs();
            long[] c = redis.incrAndGetWindows("rl:" + user, win, win - r.windowMs());
            double weight = 1 - (now - win) / (double) r.windowMs();               // how much of the previous window still overlaps
            double estimate = c[1] * weight + c[0];
            if (estimate > r.limit()) return String.format("429 (est %.1f > %d) Retry-After: %d ms", estimate, r.limit(), win + r.windowMs() - now);
            return String.format("200 (est %.1f of %d)", estimate, r.limit());
        }
    }

    public static void main(String[] args) {
        RedisLike redis = new RedisLike(); Gateway g1 = new Gateway("gw-1", redis), g2 = new Gateway("gw-2", redis);
        long[] times = {100, 200, 300, 400, 500, 600, 1100, 1500};
        for (int i = 0; i < times.length; i++) {
            Gateway g = i % 2 == 0 ? g1 : g2;                                          // requests spread over two gateways
            System.out.printf("t=%4d %s asha(free) -> %s%n", times[i], g.name, g.handle("asha", "free", times[i]));
        }
        System.out.println("pro user ravi, 8 quick requests -> " + (int) java.util.stream.IntStream.range(0, 8).filter(i -> g1.handle("ravi", "pro", 2000 + i).startsWith("200")).count() + " allowed");
        g2.redisDown = true;
        System.out.println("redis outage, gw-2 -> " + g2.handle("asha", "free", 2100));
    }
}
''', ["Make the counters expire (TTL = 2 windows) so memory doesn't grow forever.",
      "Add a local in-memory pre-check per gateway (each allows limit/N) to reduce Redis calls, and discuss accuracy.",
      "Switch the outage policy to fail-closed for the `/login` endpoint only."])

J("idgen-hld", r'''
import java.util.*;
import java.util.concurrent.*;

public class IdGeneratorSystem {
    // Three designs side by side: Snowflake (time+machine+seq), ticket server ranges, and UUIDv7-style.
    static class Snowflake {
        final long machine; long last = -1, seq;
        Snowflake(long m) { machine = m; }
        synchronized long next(long ms) { if (ms == last) { seq = (seq + 1) & 4095; } else { seq = 0; last = ms; } return (ms - 1_700_000_000_000L) << 22 | machine << 12 | seq; }
    }
    static class TicketServer { long next = 1; synchronized long[] range(int n) { long s = next; next += n; return new long[]{s, s + n - 1}; } }
    static String uuidV7(long ms, Random r) { return String.format("%012x-7%03x-%016x", ms, r.nextInt(4096), r.nextLong() & 0x3fffffffffffffffL | 0x8000000000000000L); }

    public static void main(String[] args) throws Exception {
        Map<Long, Snowflake> fleet = new TreeMap<>(); for (long m = 1; m <= 3; m++) fleet.put(m, new Snowflake(m));
        long now = 1_764_140_000_000L;
        System.out.println("Snowflake ids from 3 machines in the same millisecond:");
        for (Snowflake s : fleet.values()) System.out.println("  machine " + s.machine + " -> " + s.next(now) + ", " + s.next(now));
        Set<Long> ids = ConcurrentHashMap.newKeySet(); ExecutorService pool = Executors.newFixedThreadPool(3); List<Future<?>> fs = new ArrayList<>();
        for (Snowflake s : fleet.values()) fs.add(pool.submit(() -> { for (int ms = 0; ms < 100; ms++) for (int i = 0; i < 1000; i++) ids.add(s.next(now + 10 + ms)); }));
        for (Future<?> f : fs) f.get(); pool.shutdown();
        System.out.println("  300,000 ids generated in parallel -> unique: " + ids.size());
        TicketServer ts = new TicketServer();
        System.out.println("Ticket server ranges: app-1 " + Arrays.toString(ts.range(1000)) + ", app-2 " + Arrays.toString(ts.range(1000)) + " (one DB call per 1,000 ids)");
        Random r = new Random(1);
        String u1 = uuidV7(now, r), u2 = uuidV7(now + 5, r);
        System.out.println("UUIDv7-style: " + u1 + " < " + u2 + " ? " + (u1.compareTo(u2) < 0) + " (time-sortable, no coordination, 128 bits)");
    }
}
''', ["Add a clock-backwards guard to `Snowflake.next` that waits if the clock moved back less than 5 ms.",
      "Give machine ids out from a 'ZooKeeper' map with leases so a restarted machine can't reuse a live id.",
      "Encode Snowflake ids as 11-character base62 strings and check the order is preserved when sorting the strings (hint: pad them)."])

J("kvstore-hld", r'''
import java.util.*;

public class KeyValueStoreSystem {
    // Dynamo-style: consistent hashing ring, replication to N=3 successors, quorum W=2/R=2, versioned values, read repair, hinted handoff.
    record Versioned(String value, long version) {}
    static class Node { final String name; boolean up = true; final Map<String, Versioned> data = new HashMap<>(); final List<String[]> hints = new ArrayList<>(); Node(String n) { name = n; } }
    static final TreeMap<Integer, Node> ring = new TreeMap<>();
    static final List<Node> nodes = new ArrayList<>();
    static final int N = 3, W = 2, R = 2;

    static int h(String s) { int x = s.hashCode(); x ^= x >>> 16; x *= 0x45d9f3b; return Math.floorMod(x ^ (x >>> 16), 1 << 16); }
    static List<Node> preferenceList(String key) {
        List<Node> out = new ArrayList<>(); Integer pos = ring.ceilingKey(h(key));
        Iterator<Node> it = (pos == null ? ring.values() : ring.tailMap(pos).values()).iterator();
        while (out.size() < N) { if (!it.hasNext()) it = ring.values().iterator(); Node n = it.next(); if (!out.contains(n)) out.add(n); }
        return out;
    }
    static String put(String key, String value, long version) {
        int acks = 0;
        for (Node n : preferenceList(key)) {
            if (n.up) { n.data.put(key, new Versioned(value, version)); acks++; }
            else { Node spare = nodes.stream().filter(x -> x.up && !preferenceList(key).contains(x)).findFirst().get(); spare.hints.add(new String[]{n.name, key, value, "" + version}); acks++; }
        }
        return acks >= W ? "OK (" + acks + " acks)" : "FAIL";
    }
    static String get(String key) {
        List<Node> replies = preferenceList(key).stream().filter(n -> n.up).limit(R).toList();
        if (replies.size() < R) return "FAIL (quorum not met)";
        Versioned best = replies.stream().map(n -> n.data.get(key)).filter(Objects::nonNull).max(Comparator.comparingLong(Versioned::version)).orElse(null);
        for (Node n : replies) if (best != null && !best.equals(n.data.get(key))) { n.data.put(key, best); System.out.println("    read repair: " + n.name + " updated"); }
        return best == null ? "null" : best.value() + " (v" + best.version() + ") from " + replies.stream().map(n -> n.name).toList();
    }

    public static void main(String[] args) {
        for (String n : List.of("A", "B", "C", "D", "E")) { Node node = new Node(n); nodes.add(node); for (int v = 0; v < 50; v++) ring.put(h(n + "#" + v), node); }
        System.out.println("preference list for 'cart:42': " + preferenceList("cart:42").stream().map(n -> n.name).toList());
        System.out.println("put cart:42=[shoes] v1 -> " + put("cart:42", "[shoes]", 1));
        Node second = preferenceList("cart:42").get(1); second.up = false;
        System.out.println(second.name + " goes down; put cart:42=[shoes,socks] v2 -> " + put("cart:42", "[shoes,socks]", 2) + " (hint stored on a spare node)");
        second.up = true;
        for (Node n : nodes) for (Iterator<String[]> it = n.hints.iterator(); it.hasNext(); ) { String[] hnt = it.next(); Node target = nodes.stream().filter(x -> x.name.equals(hnt[0])).findFirst().get(); target.data.put(hnt[1], new Versioned(hnt[2], Long.parseLong(hnt[3]))); it.remove(); System.out.println("hinted handoff: " + n.name + " -> " + hnt[0]); }
        preferenceList("cart:42").get(0).data.put("cart:42", new Versioned("[shoes]", 1));   // simulate one stale replica
        System.out.println("get cart:42 -> " + get("cart:42"));
    }
}
''', ["Replace integer versions with vector clocks and return both siblings when two writes are concurrent.",
      "Add an anti-entropy job that compares replicas key by key and fixes differences (later: Merkle trees).",
      "Add node F to the ring and count how many keys (out of 10,000) change their preference list."])

J("cache-hld", r'''
import java.util.*;

public class DistributedCacheSystem {
    // Client-side consistent hashing over cache nodes, each an LRU with TTL; hot-key local cache; node failure.
    static class CacheNode {
        final String name; boolean up = true; int hits, misses;
        final LinkedHashMap<String, long[]> lru;                                  // value is {data, expiresAt}
        CacheNode(String name, int cap) { this.name = name; lru = new LinkedHashMap<>(16, .75f, true) { protected boolean removeEldestEntry(Map.Entry<String, long[]> e) { return size() > cap; } }; }
        Long get(String k, long now) { long[] v = lru.get(k); if (v == null || v[1] <= now) { misses++; lru.remove(k); return null; } hits++; return v[0]; }
        void set(String k, long v, long ttl, long now) { lru.put(k, new long[]{v, now + ttl}); }
    }
    static final TreeMap<Integer, CacheNode> ring = new TreeMap<>();
    static int h(String s) { int x = s.hashCode() * 0x9E3779B9; return x ^ (x >>> 15); }
    static CacheNode nodeFor(String key) {
        for (Map.Entry<Integer, CacheNode> e = ring.ceilingEntry(h(key)); ; e = ring.higherEntry(e.getKey())) {
            if (e == null) e = ring.firstEntry();
            if (e.getValue().up) return e.getValue();
        }
    }
    static int dbReads = 0;
    static long read(String key, long now, Map<String, Long> localHot) {
        if (localHot.containsKey(key)) return localHot.get(key);
        CacheNode n = nodeFor(key); Long v = n.get(key, now);
        if (v == null) { dbReads++; v = (long) key.length() * 100; n.set(key, v, 60, now); }
        return v;
    }

    public static void main(String[] args) {
        List<CacheNode> nodes = List.of(new CacheNode("cache-1", 400), new CacheNode("cache-2", 400), new CacheNode("cache-3", 400));
        for (CacheNode n : nodes) for (int v = 0; v < 100; v++) ring.put(h(n.name + "#" + v), n);
        Random r = new Random(4); Map<String, Long> localHot = new HashMap<>();
        for (int i = 0; i < 30_000; i++) read("product:" + (int) Math.floor(Math.pow(r.nextDouble(), 2.5) * 1500), i / 1000, localHot);
        nodes.forEach(n -> System.out.printf("%s keys=%d hits=%d misses=%d%n", n.name, n.lru.size(), n.hits, n.misses));
        System.out.println("db reads: " + dbReads + " of 30,000");
        nodes.get(1).up = false; int before = dbReads;
        for (int i = 0; i < 3000; i++) read("product:" + (int) Math.floor(Math.pow(r.nextDouble(), 2.5) * 1500), 30, localHot);
        System.out.println("cache-2 dies: its keys move to the next nodes on the ring; extra db reads in next 3,000 requests: " + (dbReads - before));
        localHot.put("product:0", 0L);
        System.out.println("hot key product:0 now served from each app server's local cache (no network hop)");
    }
}
''', ["Add replication: write each key to 2 nodes and read from the second when the first is down; compare db reads after the failure.",
      "Add a 'single-flight' guard so concurrent misses for one key load the DB once.",
      "Track per-key request counts and automatically put the top 5 keys into `localHot`."])

J("crawler-hld", r'''
import java.util.*;
import java.util.regex.*;

public class WebCrawlerSystem {
    // Frontier (priority + per-host politeness), fetcher, parser, URL dedup, content dedup (SimHash-lite), robots rules, max depth.
    static final Map<String, String> web = Map.of(
        "https://a.com/", "<a href='https://a.com/x'> <a href='https://b.com/'> <a href='https://a.com/private'> hello world from a",
        "https://a.com/x", "<a href='https://a.com/'> <a href='https://c.com/'> news about cricket",
        "https://b.com/", "<a href='https://b.com/copy'> hello world from a",
        "https://b.com/copy", "hello world from a",
        "https://c.com/", "<a href='https://c.com/deep'> recipes",
        "https://c.com/deep", "<a href='https://c.com/deeper'> more recipes");
    static final Set<String> disallowed = Set.of("https://a.com/private");
    record Task(String url, int depth) {}

    public static void main(String[] args) {
        Deque<Task> frontier = new ArrayDeque<>(List.of(new Task("https://a.com/", 0)));
        Set<String> seenUrls = new HashSet<>(List.of("https://a.com/")); Set<Integer> seenContent = new HashSet<>();
        Map<String, Long> hostReadyAt = new HashMap<>(); long clock = 0; int maxDepth = 2;
        Pattern link = Pattern.compile("href='([^']+)'");
        while (!frontier.isEmpty()) {
            Task t = frontier.poll(); String host = t.url().split("/")[2];
            clock = Math.max(clock, hostReadyAt.getOrDefault(host, 0L)); hostReadyAt.put(host, clock + 1000);    // 1 request/second per host
            String html = web.get(t.url());
            if (html == null) { System.out.printf("t=%4d 404  %s%n", clock, t.url()); continue; }
            int fingerprint = html.replaceAll("<[^>]+>", "").trim().hashCode();
            boolean dupContent = !seenContent.add(fingerprint);
            System.out.printf("t=%4d GET  %-22s depth %d%s%n", clock, t.url(), t.depth(), dupContent ? "  (duplicate content, not indexed)" : "");
            Matcher m = link.matcher(html);
            while (m.find()) {
                String u = m.group(1);
                if (disallowed.contains(u)) { System.out.println("        skip " + u + " (robots.txt)"); continue; }
                if (t.depth() + 1 > maxDepth) continue;
                if (seenUrls.add(u)) frontier.add(new Task(u, t.depth() + 1));
            }
        }
        System.out.println("crawled " + seenUrls.size() + " unique URLs, " + seenContent.size() + " unique pages indexed");
    }
}
''', ["Fetch different hosts in parallel with an `ExecutorService` while keeping one request per second per host.",
      "Replace the exact content hash with SimHash over words so near-duplicates (one word changed) are also caught.",
      "Add a priority: URLs from `a.com` (high PageRank) are always crawled before others."])

J("notification-hld", r'''
import java.util.*;
import java.util.concurrent.*;

public class NotificationSystem {
    // API -> validation + prefs + dedupe -> per-channel queues (priority) -> workers -> provider with retry/failover -> status tracking.
    record Notification(String id, String user, String channel, String template, Map<String, String> vars, int priority) {}
    static final Map<String, String> templates = Map.of("ORDER_SHIPPED", "Hi {name}, order {orderId} has shipped", "OTP", "Your OTP is {code}");
    static final Map<String, Set<String>> optedOut = Map.of("ravi", Set.of("sms"));
    static final Set<String> dedupe = new HashSet<>();
    static final Map<String, String> status = new TreeMap<>();
    static final Map<String, PriorityQueue<Notification>> queues = new TreeMap<>();

    static String accept(Notification n) {
        if (!dedupe.add(n.id() + ":" + n.channel())) return "duplicate ignored";
        if (optedOut.getOrDefault(n.user(), Set.of()).contains(n.channel())) { status.put(n.id(), "SKIPPED (opted out)"); return "skipped"; }
        queues.computeIfAbsent(n.channel(), k -> new PriorityQueue<>(Comparator.comparingInt(Notification::priority))).add(n);
        status.put(n.id(), "QUEUED"); return "202 queued";
    }
    static String render(Notification n) { String s = templates.get(n.template()); for (var e : n.vars().entrySet()) s = s.replace("{" + e.getKey() + "}", e.getValue()); return s; }

    public static void main(String[] args) {
        System.out.println(accept(new Notification("n1", "asha", "push", "ORDER_SHIPPED", Map.of("name", "Asha", "orderId", "987"), 2)));
        System.out.println(accept(new Notification("n2", "asha", "sms", "OTP", Map.of("code", "482913"), 0)));
        System.out.println(accept(new Notification("n3", "ravi", "sms", "OTP", Map.of("code", "111222"), 0)));
        System.out.println(accept(new Notification("n1", "asha", "push", "ORDER_SHIPPED", Map.of("name", "Asha", "orderId", "987"), 2)));
        System.out.println(accept(new Notification("n4", "zoya", "push", "ORDER_SHIPPED", Map.of("name", "Zoya", "orderId", "990"), 2)));
        int[] smsAttempts = {0};
        Map<String, java.util.function.Predicate<String>> providers = new LinkedHashMap<>();
        providers.put("twilio", msg -> ++smsAttempts[0] > 2);                  // primary SMS provider fails twice
        providers.put("msg91", msg -> true);
        queues.forEach((channel, q) -> {
            while (!q.isEmpty()) {
                Notification n = q.poll(); String msg = render(n); String used = null;
                if (channel.equals("sms")) {
                    for (var p : providers.entrySet()) { for (int attempt = 1; attempt <= 2 && used == null; attempt++) { if (p.getValue().test(msg)) used = p.getKey() + " (attempt " + attempt + ")"; else System.out.println("    " + p.getKey() + " attempt " + attempt + " failed"); } if (used != null) break; }
                } else used = "FCM/APNs";
                status.put(n.id(), "SENT via " + used);
                System.out.println("[" + channel + "] to " + n.user() + ": '" + msg + "' -> " + used);
            }
        });
        System.out.println("status: " + status);
    }
}
''', ["Add per-user rate limiting: at most 3 marketing pushes per day.",
      "Add scheduled sends (`sendAt`) using a `DelayQueue`.",
      "Run each channel's worker on its own thread with a `BlockingQueue` instead of the loop."])

J("newsfeed-hld", r'''
import java.util.*;

public class NewsFeedSystem {
    // Hybrid fan-out + ranking: push for normal authors, pull for celebrities, then rank by affinity x recency x engagement.
    record Post(long id, String author, long ts, int likes) {}
    static final Map<String, Set<String>> followers = new HashMap<>(), following = new HashMap<>();
    static final Map<String, Deque<Long>> feedCache = new HashMap<>();
    static final Map<String, List<Post>> timelines = new HashMap<>();
    static final Map<Long, Post> posts = new HashMap<>();
    static final Map<String, Map<String, Double>> affinity = new HashMap<>();  // how much a user interacts with an author
    static long seq = 0; static final int CELEB = 3;

    static void follow(String u, String a, double aff) { followers.computeIfAbsent(a, k -> new HashSet<>()).add(u); following.computeIfAbsent(u, k -> new TreeSet<>()).add(a); affinity.computeIfAbsent(u, k -> new HashMap<>()).put(a, aff); }
    static void publish(String author, long ts, int likes) {
        Post p = new Post(++seq, author, ts, likes); posts.put(p.id(), p); timelines.computeIfAbsent(author, k -> new ArrayList<>()).add(p);
        if (followers.getOrDefault(author, Set.of()).size() < CELEB) for (String f : followers.getOrDefault(author, Set.of())) feedCache.computeIfAbsent(f, k -> new ArrayDeque<>()).addFirst(p.id());
    }
    static List<String> feed(String user, long now) {
        List<Post> cand = new ArrayList<>();
        for (long id : feedCache.getOrDefault(user, new ArrayDeque<>())) cand.add(posts.get(id));
        for (String a : following.getOrDefault(user, Set.of())) if (followers.get(a).size() >= CELEB) cand.addAll(timelines.getOrDefault(a, List.of()));
        return cand.stream().sorted(Comparator.comparingDouble((Post p) -> -score(user, p, now)))
            .map(p -> String.format("%s#%d(%.2f)", p.author(), p.id(), score(user, p, now))).toList();
    }
    static double score(String u, Post p, long now) {
        double aff = affinity.get(u).getOrDefault(p.author(), 0.1), recency = Math.exp(-(now - p.ts()) / 24.0), engagement = Math.log(2 + p.likes());
        return aff * recency * engagement;
    }

    public static void main(String[] args) {
        follow("asha", "ravi", 0.9); follow("asha", "zoya", 0.3); for (String u : List.of("asha", "kiran", "meera")) follow(u, "bollywood", 0.5);
        publish("ravi", 10, 5); publish("zoya", 20, 300); publish("bollywood", 22, 90_000); publish("ravi", 23, 2); publish("zoya", 2, 50);
        System.out.println("asha's ranked feed at hour 24: " + feed("asha", 24));
        System.out.println("pushed entries in asha's cache: " + feedCache.get("asha") + " (bollywood posts pulled at read time)");
    }
}
''', ["Add pagination with a cursor (the score and id of the last item shown).",
      "Increase affinity automatically when the user likes an author's post, and re-rank.",
      "Add 'seen' tracking so posts already shown are pushed down the feed."])

J("twitter-hld", r'''
import java.util.*;
import java.util.regex.*;

public class TwitterSystem {
    // Tweet write path: id, store, fan-out to home timelines (capped), hashtag index, trending counts in a time window.
    record Tweet(long id, String user, String text, long minute) {}
    static final Map<Long, Tweet> tweets = new HashMap<>();
    static final Map<String, Set<String>> followers = new HashMap<>();
    static final Map<String, Deque<Long>> homeTimeline = new HashMap<>();
    static final Map<String, List<Long>> hashtagIndex = new TreeMap<>();
    static final Map<Long, Map<String, Integer>> tagCountsPerMinute = new TreeMap<>();
    static long seq = 0; static final int TIMELINE_CAP = 3;

    static void tweet(String user, String text, long minute) {
        Tweet t = new Tweet(++seq, user, text, minute); tweets.put(t.id(), t);
        for (String f : followers.getOrDefault(user, Set.of())) {
            Deque<Long> tl = homeTimeline.computeIfAbsent(f, k -> new ArrayDeque<>()); tl.addFirst(t.id()); if (tl.size() > TIMELINE_CAP) tl.removeLast();
        }
        Matcher m = Pattern.compile("#(\\w+)").matcher(text);
        while (m.find()) { String tag = m.group(1).toLowerCase(); hashtagIndex.computeIfAbsent(tag, k -> new ArrayList<>()).add(t.id()); tagCountsPerMinute.computeIfAbsent(minute, k -> new HashMap<>()).merge(tag, 1, Integer::sum); }
    }
    static List<String> trending(long now, int windowMin) {
        Map<String, Integer> sum = new HashMap<>();
        tagCountsPerMinute.forEach((min, c) -> { if (min > now - windowMin) c.forEach((k, v) -> sum.merge(k, v, Integer::sum)); });
        return sum.entrySet().stream().sorted(Map.Entry.<String, Integer>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey())).limit(3).map(e -> "#" + e.getKey() + "=" + e.getValue()).toList();
    }

    public static void main(String[] args) {
        followers.put("ravi", Set.of("asha")); followers.put("zoya", Set.of("asha", "kiran"));
        tweet("ravi", "Watching #INDvAUS tonight", 1); tweet("zoya", "#INDvAUS what a catch!", 2); tweet("zoya", "Learning #SystemDesign", 3);
        tweet("kiran", "#INDvAUS #INDvAUS crazy finish", 9); tweet("ravi", "New blog on #SystemDesign and #Kafka", 9); tweet("zoya", "Lunch", 10);
        System.out.println("asha's home timeline (capped at " + TIMELINE_CAP + "): " + homeTimeline.get("asha").stream().map(id -> tweets.get(id).user() + ": " + tweets.get(id).text()).toList());
        System.out.println("search #systemdesign -> tweet ids " + hashtagIndex.get("systemdesign"));
        System.out.println("trending last 10 min at minute 10: " + trending(10, 10));
        System.out.println("trending last 3 min at minute 10 : " + trending(10, 3));
    }
}
''', ["Add retweets that reference the original tweet id instead of copying text, and count retweets.",
      "Rebuild a user's home timeline from scratch (pull from everyone they follow) for users whose cache was evicted.",
      "Make trending relative: score = count in last 10 min / (average count per 10 min over the last hour + 1)."])

J("instagram-hld", r'''
import java.util.*;

public class InstagramSystem {
    // Upload flow (pre-signed URL -> object store -> async thumbnail job -> ready), likes with buffered counters, profile grid query.
    record Photo(long id, String owner, String objectKey, List<String> thumbs, String status, long ts) {}
    static final Map<Long, Photo> photos = new TreeMap<>(); static final Map<String, byte[]> objectStore = new HashMap<>();
    static final Deque<Long> thumbnailQueue = new ArrayDeque<>(); static final Map<Long, Long> likeBuffer = new HashMap<>(), likesDb = new HashMap<>();
    static long seq = 0;

    static long requestUpload(String owner, long ts) { long id = ++seq; photos.put(id, new Photo(id, owner, "raw/" + id + ".jpg", List.of(), "PENDING", ts)); return id; }
    static void clientUploads(long id, int bytes) { objectStore.put(photos.get(id).objectKey(), new byte[bytes]); thumbnailQueue.add(id); }   // storage event -> queue
    static void thumbnailWorker() {
        while (!thumbnailQueue.isEmpty()) {
            Photo p = photos.get(thumbnailQueue.poll()); List<String> t = new ArrayList<>();
            for (int size : new int[]{150, 640, 1080}) { String k = "thumb/" + p.id() + "_" + size + ".jpg"; objectStore.put(k, new byte[size * 50]); t.add(k); }
            photos.put(p.id(), new Photo(p.id(), p.owner(), p.objectKey(), t, "READY", p.ts()));
        }
    }
    static void like(long photoId) { likeBuffer.merge(photoId, 1L, Long::sum); }
    static void flushLikes() { likeBuffer.forEach((k, v) -> likesDb.merge(k, v, Long::sum)); likeBuffer.clear(); }

    public static void main(String[] args) {
        long a = requestUpload("asha", 100), b = requestUpload("asha", 200), c = requestUpload("ravi", 150);
        clientUploads(a, 3_000_000); clientUploads(b, 2_500_000);
        System.out.println("before worker: " + photos.values().stream().map(p -> p.id() + "=" + p.status()).toList());
        thumbnailWorker();
        System.out.println("after worker : " + photos.values().stream().map(p -> p.id() + "=" + p.status()).toList() + " (photo " + c + " never uploaded: cleanup job deletes it later)");
        for (int i = 0; i < 10_000; i++) like(i % 10 == 0 ? b : a);
        flushLikes();
        System.out.println("likes after buffered flush: " + likesDb + " (1 DB write per photo per flush, not 10,000)");
        List<String> grid = photos.values().stream().filter(p -> p.owner().equals("asha") && p.status().equals("READY")).sorted(Comparator.comparingLong(Photo::ts).reversed()).map(p -> p.thumbs().get(0)).toList();
        System.out.println("asha's profile grid (newest first, 150px thumbs via CDN): " + grid);
    }
}
''', ["Add a feed for followers using the fan-out code from the news feed question.",
      "Add stories that expire after 24 hours and are removed by a cleanup job.",
      "Make the thumbnail worker run on 3 threads consuming a `BlockingQueue`."])

J("chat-hld", r'''
import java.util.*;

public class ChatSystem {
    // Connection registry (which gateway holds each user), per-conversation sequence numbers, persistence before ack,
    // offline delivery + sync, group fan-out, and delivered/read receipts.
    record Message(String conv, long seq, String from, String text) {}
    static final Map<String, String> sessions = new HashMap<>();                    // user -> gateway server
    static final Map<String, List<Message>> store = new HashMap<>();
    static final Map<String, List<String>> members = new HashMap<>();
    static final Map<String, Map<String, Long>> readUpTo = new HashMap<>();          // conv -> user -> seq
    static final Map<String, List<String>> pushQueue = new TreeMap<>();

    static void send(String conv, String from, String text) {
        List<Message> log = store.computeIfAbsent(conv, k -> new ArrayList<>());
        Message m = new Message(conv, log.size() + 1, from, text); log.add(m);           // 1. persist
        System.out.println(from + " -> " + conv + " #" + m.seq() + " '" + text + "' ✓ (stored)");
        for (String u : members.get(conv)) {                                         // 2. fan out to members
            if (u.equals(from)) continue;
            String gw = sessions.get(u);
            if (gw != null) System.out.println("    deliver to " + u + " via " + gw + " ✓✓");
            else pushQueue.computeIfAbsent(u, k -> new ArrayList<>()).add(conv + "#" + m.seq());
        }
    }
    static void connect(String user, String gw) {
        sessions.put(user, gw);
        for (var e : members.entrySet()) if (e.getValue().contains(user)) {
            long last = readUpTo.computeIfAbsent(e.getKey(), k -> new HashMap<>()).getOrDefault(user, 0L);
            List<String> missed = store.getOrDefault(e.getKey(), List.of()).stream().filter(m -> m.seq() > last && !m.from().equals(user)).map(m -> m.seq() + ":" + m.text()).toList();
            if (!missed.isEmpty()) System.out.println(user + " connects to " + gw + ", syncs " + e.getKey() + " after #" + last + " -> " + missed);
        }
    }
    static void read(String user, String conv) { long top = store.get(conv).size(); readUpTo.computeIfAbsent(conv, k -> new HashMap<>()).put(user, top); System.out.println(user + " read " + conv + " up to #" + top + " (blue ticks sent to sender)"); }

    public static void main(String[] args) {
        members.put("dm:asha:ravi", List.of("asha", "ravi")); members.put("group:trip", List.of("asha", "ravi", "zoya", "kiran"));
        sessions.put("asha", "gw-1"); sessions.put("zoya", "gw-3");
        send("dm:asha:ravi", "asha", "Are you coming?");
        send("group:trip", "asha", "Goa in December?");
        send("group:trip", "zoya", "Yes!!");
        System.out.println("offline push notifications: " + pushQueue);
        connect("ravi", "gw-2"); read("ravi", "group:trip");
        send("group:trip", "ravi", "Count me in");
    }
}
''', ["Add typing indicators and presence ('last seen') that are NOT persisted, only forwarded if the user is online.",
      "Make a large group (1,000 members) send one message to each gateway with the list of its local members instead of one per user.",
      "Add end-to-end encryption placeholders: the server only ever stores `byte[]` ciphertext."])
