"""Java practice programs: HLD questions 37-49."""
from sd_j_util import J

J("zoom-hld", r'''
import java.util.*;

public class VideoConferencingSystem {
    // SFU (selective forwarding unit): each participant uploads one stream with simulcast layers; the SFU forwards a layer
    // per receiver based on their bandwidth and layout. Compare upload/download cost with mesh (peer-to-peer).
    record Layer(String name, int kbps) {}
    static final List<Layer> simulcast = List.of(new Layer("180p", 150), new Layer("360p", 500), new Layer("720p", 1500));

    public static void main(String[] args) {
        int n = 6;
        System.out.printf("%d participants, 720p = 1500 kbps%n", n);
        System.out.printf("mesh: each uploads %d copies = %,d kbps up, downloads %,d kbps -> phones melt beyond ~4 people%n", n - 1, (n - 1) * 1500, (n - 1) * 1500);
        int up = simulcast.stream().mapToInt(Layer::kbps).sum();
        System.out.printf("SFU : each uploads 3 simulcast layers once = %,d kbps up; the server picks what to forward%n", up);
        Map<String, Integer> downlink = new LinkedHashMap<>(); downlink.put("asha (fibre)", 20_000); downlink.put("ravi (4G)", 2_500); downlink.put("zoya (weak wifi)", 900);
        String speaker = "kiran";
        for (var e : downlink.entrySet()) {
            int budget = e.getValue(); List<String> plan = new ArrayList<>(); int used = 0;
            Layer sp = simulcast.stream().filter(l -> l.kbps() <= budget * 0.6).reduce((a, b) -> b).orElse(simulcast.get(0));
            plan.add(speaker + "@" + sp.name()); used += sp.kbps();
            for (int i = 0; i < n - 2; i++) { Layer th = used + 150 <= budget ? simulcast.get(0) : null; if (th == null) { plan.add("(+" + (n - 2 - i) + " paused)"); break; } plan.add("tile" + (i + 1) + "@180p"); used += 150; }
            System.out.printf("  %-17s %,6d kbps -> %s = %,d kbps%n", e.getKey(), budget, plan, used);
        }
        System.out.println("audio: mixed or forwarded separately (Opus ~32 kbps), prioritised over video when bandwidth drops");
    }
}
''', ["Add active-speaker detection: the participant with the highest audio level in the last 2 s becomes the speaker.",
      "Cascade two SFUs in different regions and compute the cross-region bandwidth for a 50-person call.",
      "React to packet loss: if a receiver reports > 5% loss, step them down one layer."])

J("spotify-hld", r'''
import java.util.*;

public class MusicStreamingSystem {
    // Audio files in object storage behind a CDN; client prefetches the next track; play events -> royalties count; offline downloads with licence expiry.
    record Track(String id, String title, int seconds, int kbps) {}

    public static void main(String[] args) {
        List<Track> queue = List.of(new Track("t1", "Kesariya", 268, 160), new Track("t2", "Shape of You", 233, 160), new Track("t3", "Naatu Naatu", 216, 320));
        Set<String> cdnEdge = new HashSet<>(List.of("t1", "t2"));                    // popular tracks already at the edge
        Map<String, Long> playCounts = new TreeMap<>(); long bytes = 0;
        for (int i = 0; i < queue.size(); i++) {
            Track t = queue.get(i);
            String src = cdnEdge.contains(t.id()) ? "CDN edge (hit)" : "origin -> CDN (miss, now cached)"; cdnEdge.add(t.id());
            long size = (long) t.seconds() * t.kbps() * 1000 / 8; bytes += size;
            System.out.printf("play %-13s %3ds @%dkbps from %-28s %.1f MB%s%n", t.title(), t.seconds(), t.kbps(), src, size / 1e6, i + 1 < queue.size() ? "  | prefetch next: " + queue.get(i + 1).title() : "");
            if (t.seconds() >= 30) playCounts.merge(t.id(), 1L, Long::sum);              // a 'stream' counts after 30 s
        }
        System.out.printf("session data: %.1f MB; play events for royalties: %s%n", bytes / 1e6, playCounts);
        long licenceExpires = 30; long[] checkDays = {10, 31};
        for (long day : checkDays) System.out.println("offline track on day " + day + ": " + (day < licenceExpires ? "plays (licence valid)" : "locked until the app comes online and renews the licence"));
        double monthlyPlays = 600e6 * 30 * 25;
        System.out.printf("scale: 600M users x 25 tracks/day = %.1e streams/month -> play events go to Kafka, counted in batch%n", monthlyPlays);
    }
}
''', ["Adapt bitrate: on a 2G connection choose 96 kbps, on wifi 320 kbps.",
      "Build 'Discover Weekly'-lite: recommend tracks played by users who share 2+ tracks with you.",
      "Shuffle without repeats until every track in the playlist has played once."])

J("tinder-hld", r'''
import java.util.*;

public class MatchingSwipeSystem {
    // Recommendation deck from nearby users matching preferences, exclude already swiped; a match happens when both swiped right.
    record User(String id, int age, double km, String gender, Set<String> wants) {}
    static final Map<String, User> users = new TreeMap<>();
    static final Map<String, Set<String>> rightSwipes = new HashMap<>(), seen = new HashMap<>();
    static final List<String> matches = new ArrayList<>();

    static List<String> deck(String uid, double radiusKm) {
        User me = users.get(uid);
        return users.values().stream().filter(o -> !o.id().equals(uid) && o.km() <= radiusKm && me.wants().contains(o.gender()) && o.wants().contains(me.gender())
            && !seen.getOrDefault(uid, Set.of()).contains(o.id())).sorted(Comparator.comparingDouble(User::km)).map(User::id).toList();
    }
    static void swipe(String from, String to, boolean right) {
        seen.computeIfAbsent(from, k -> new HashSet<>()).add(to);
        if (!right) return;
        rightSwipes.computeIfAbsent(from, k -> new HashSet<>()).add(to);
        if (rightSwipes.getOrDefault(to, Set.of()).contains(from)) { matches.add(from + " ❤ " + to); System.out.println("  MATCH: " + from + " and " + to + " -> open chat"); }
    }

    public static void main(String[] args) {
        users.put("asha", new User("asha", 27, 0, "F", Set.of("M"))); users.put("ravi", new User("ravi", 29, 2.1, "M", Set.of("F")));
        users.put("kiran", new User("kiran", 26, 5.5, "M", Set.of("F"))); users.put("dev", new User("dev", 31, 40, "M", Set.of("F"))); users.put("neha", new User("neha", 28, 1.0, "F", Set.of("M")));
        System.out.println("asha's deck (10 km): " + deck("asha", 10));
        swipe("ravi", "asha", true);                                     // ravi already liked asha
        swipe("asha", "ravi", true); swipe("asha", "kiran", false);
        System.out.println("asha's deck after swiping: " + deck("asha", 10) + " (seen profiles are excluded)");
        swipe("neha", "ravi", true);
        System.out.println("ravi's deck: " + deck("ravi", 10)); swipe("ravi", "neha", true);
        System.out.println("matches: " + matches);
    }
}
''', ["Add an Elo-like desirability score that changes with right-swipes received, and sort the deck by it.",
      "Store `seen` in a Bloom filter per user to save memory, accepting a few false positives.",
      "Shard users by geohash so the deck query only scans the user's region."])

J("distributed-tracing-hld", r'''
import java.util.*;

public class DistributedTracingSystem {
    // Trace context (traceId, parent span) propagated through calls; spans reported to a collector; tree rebuilt; tail-based sampling.
    record Span(String traceId, String spanId, String parentId, String service, String op, long start, long end, boolean error) {}
    static final List<Span> collector = new ArrayList<>(); static int ids = 0;

    static long call(String traceId, String parent, String service, String op, long start, long selfMs, boolean error, List<Object[]> children) {
        String id = "s" + (++ids); long t = start + selfMs / 2; boolean childError = false;
        for (Object[] c : children) { long end = call(traceId, id, (String) c[0], (String) c[1], t, (Long) c[2], (Boolean) c[3], List.of()); t = end; childError |= (Boolean) c[3]; }
        long end = t + selfMs / 2;
        collector.add(new Span(traceId, id, parent, service, op, start, end, error || childError));
        return end;
    }
    static void print(List<Span> spans, String parent, int depth) {
        spans.stream().filter(s -> Objects.equals(s.parentId(), parent)).sorted(Comparator.comparingLong(Span::start)).forEach(s -> {
            System.out.printf("  %-34s %4d ms %s%n", "  ".repeat(depth) + s.service() + " " + s.op(), s.end() - s.start(), s.error() ? "ERROR" : "");
            print(spans, s.spanId(), depth + 1);
        });
    }

    public static void main(String[] args) {
        call("trace-A", null, "gateway", "GET /checkout", 0, 10, false, List.of(new Object[]{"order", "createOrder", 40L, false}, new Object[]{"payment", "charge", 320L, false}, new Object[]{"email", "send", 15L, false}));
        call("trace-B", null, "gateway", "GET /checkout", 1000, 10, false, List.of(new Object[]{"order", "createOrder", 35L, false}, new Object[]{"payment", "charge", 60L, true}));
        call("trace-C", null, "gateway", "GET /home", 2000, 30, false, List.of());
        Map<String, List<Span>> byTrace = new TreeMap<>(); for (Span s : collector) byTrace.computeIfAbsent(s.traceId(), k -> new ArrayList<>()).add(s);
        for (var e : byTrace.entrySet()) {
            Span root = e.getValue().stream().filter(s -> s.parentId() == null).findFirst().get();
            boolean keep = root.error() || root.end() - root.start() > 300;                     // tail sampling: keep slow or failed traces
            System.out.println(e.getKey() + " (" + (root.end() - root.start()) + " ms) -> " + (keep ? "KEPT" : "dropped (fast and healthy)"));
            if (keep) print(e.getValue(), null, 0);
        }
    }
}
''', ["Propagate the context through a `ThreadLocal` instead of method parameters, like OpenTelemetry does.",
      "Compute a service dependency graph (who calls whom, call counts) from all spans.",
      "Add head-based sampling (keep 10% decided at the gateway) and compare which interesting traces are lost."])

J("llmserving-hld", r'''
import java.util.*;

public class LlmServingSystem {
    // Continuous batching on a GPU: each step generates one token for every active request; finished requests leave,
    // waiting ones join immediately. Compare with static batching (wait for the whole batch to finish).
    record Req(String id, int arrivalStep, int outputTokens) {}

    static Map<String, Integer> simulate(List<Req> reqs, int maxBatch, boolean continuous) {
        Map<String, Integer> done = new TreeMap<>(); Map<String, Integer> remaining = new HashMap<>(); Deque<Req> waiting = new ArrayDeque<>(reqs);
        List<Req> active = new ArrayList<>(); int step = 0;
        while (done.size() < reqs.size()) {
            boolean canJoin = continuous || active.isEmpty();
            while (canJoin && active.size() < maxBatch && !waiting.isEmpty() && waiting.peek().arrivalStep() <= step) { Req r = waiting.poll(); active.add(r); remaining.put(r.id(), r.outputTokens()); }
            for (Req r : active) remaining.merge(r.id(), -1, Integer::sum);           // one forward pass = one token for each active request
            step++;
            for (Iterator<Req> it = active.iterator(); it.hasNext(); ) { Req r = it.next(); if (remaining.get(r.id()) == 0) { done.put(r.id(), step - r.arrivalStep()); it.remove(); } }
        }
        return done;
    }

    public static void main(String[] args) {
        List<Req> reqs = List.of(new Req("long-essay", 0, 400), new Req("hi", 0, 5), new Req("code", 0, 120), new Req("joke", 2, 30), new Req("sum", 3, 60), new Req("q6", 5, 10));
        Map<String, Integer> stat = simulate(reqs, 4, false), cont = simulate(reqs, 4, true);
        System.out.println("request      tokens  static-batch latency  continuous-batch latency (steps)");
        for (Req r : reqs) System.out.printf("%-12s %5d   %8d              %8d%n", r.id(), r.outputTokens(), stat.get(r.id()), cont.get(r.id()));
        System.out.printf("average: static %.0f vs continuous %.0f steps; short requests no longer wait for the long essay%n",
            stat.values().stream().mapToInt(i -> i).average().orElse(0), cont.values().stream().mapToInt(i -> i).average().orElse(0));
        int kvBytesPerToken = 2 * 32 * 4096 * 2;                                          // K and V, 32 layers, 4096 hidden, fp16
        System.out.printf("KV cache: %,d KB per token -> a 4,000-token conversation holds %.1f GB of GPU memory%n", kvBytesPerToken / 1024, kvBytesPerToken * 4000 / 1e9);
    }
}
''', ["Add a per-user token rate limit (tokens/minute) in front of the queue.",
      "Add prefix caching: requests sharing the same 500-token system prompt skip those prefill steps.",
      "Add priority: paid users' requests jump ahead of free users in the waiting queue."])

J("gfs-hld", r'''
import java.util.*;

public class DistributedFileSystemSystem {
    // Master keeps namespace + chunk locations; chunkservers store 64 MB chunks x3 replicas; client asks master once, then talks to chunkservers;
    // heartbeats detect dead servers and the master re-replicates under-replicated chunks.
    static final long CHUNK = 64L << 20;
    static final Map<String, List<String>> fileChunks = new TreeMap<>();                // path -> chunk handles
    static final Map<String, Set<String>> chunkLocations = new TreeMap<>();             // handle -> servers
    static final Map<String, Long> lastHeartbeat = new TreeMap<>();
    static int handleSeq = 0; static int rr = 0;

    static void create(String path, long size, List<String> servers) {
        List<String> handles = new ArrayList<>();
        for (long off = 0; off < size; off += CHUNK) {
            String h = "chunk-" + (++handleSeq); handles.add(h); Set<String> reps = new TreeSet<>();
            while (reps.size() < 3) reps.add(servers.get(rr++ % servers.size()));        // rack-aware placement in real life
            chunkLocations.put(h, reps);
        }
        fileChunks.put(path, handles);
    }

    public static void main(String[] args) {
        List<String> servers = List.of("cs1", "cs2", "cs3", "cs4", "cs5"); servers.forEach(s -> lastHeartbeat.put(s, 0L));
        create("/logs/2026-11-26.log", 200L << 20, servers);
        System.out.println("/logs/2026-11-26.log (200 MB) -> " + fileChunks.get("/logs/2026-11-26.log").size() + " chunks");
        chunkLocations.forEach((h, rs) -> System.out.println("  " + h + " on " + rs));
        long offset = 150L << 20; String h = fileChunks.get("/logs/2026-11-26.log").get((int) (offset / CHUNK));
        System.out.println("client reads offset 150 MB -> master says " + h + " on " + chunkLocations.get(h) + "; data flows directly from a chunkserver, not the master");
        for (String s : servers) if (!s.equals("cs2")) lastHeartbeat.put(s, 60L);           // cs2 stopped sending heartbeats
        long now = 60;
        List<String> dead = lastHeartbeat.entrySet().stream().filter(e -> now - e.getValue() > 30).map(Map.Entry::getKey).toList();
        System.out.println("t=60 heartbeat check -> dead: " + dead);
        for (var e : chunkLocations.entrySet()) {
            if (e.getValue().removeAll(dead)) {
                String target = servers.stream().filter(s -> !dead.contains(s) && !e.getValue().contains(s)).findFirst().get();
                e.getValue().add(target);
                System.out.println("  re-replicate " + e.getKey() + " to " + target + " -> " + e.getValue());
            }
        }
    }
}
''', ["Add an append operation: the master picks a primary replica (lease) that orders concurrent appends.",
      "Make the master's namespace durable with an operation log and rebuild it by replaying.",
      "Balance load: move chunks from the fullest chunkserver to the emptiest until they differ by less than 1 chunk."])

J("reddit-hld", r'''
import java.util.*;

public class VotingRankingSystem {
    // One vote per user per post (upsert), score = ups - downs, and Reddit's 'hot' formula: log10(score) + age/45000 s.
    record Post(String id, String title, long createdSec) {}
    static final Map<String, Map<String, Integer>> votes = new HashMap<>();           // post -> user -> +1 / -1

    static void vote(String post, String user, int dir) { votes.computeIfAbsent(post, k -> new HashMap<>()).put(user, dir); }   // changing a vote just overwrites it
    static int score(String post) { return votes.getOrDefault(post, Map.of()).values().stream().mapToInt(i -> i).sum(); }
    static double hot(Post p) { int s = score(p.id()); double order = Math.log10(Math.max(Math.abs(s), 1)); int sign = Integer.signum(s); return sign * order + (p.createdSec() - 1_134_028_003L) / 45000.0; }

    public static void main(String[] args) {
        long now = 1_764_140_000L;
        List<Post> posts = List.of(new Post("p1", "Old viral meme", now - 30 * 3600), new Post("p2", "Fresh system design tip", now - 1 * 3600), new Post("p3", "Controversial take", now - 2 * 3600));
        for (int i = 0; i < 5000; i++) vote("p1", "u" + i, 1);
        for (int i = 0; i < 120; i++) vote("p2", "u" + i, 1);
        for (int i = 0; i < 300; i++) vote("p3", "u" + i, i % 2 == 0 ? 1 : -1);
        vote("p2", "u5", -1); vote("p2", "u5", 1); vote("p2", "u5", 1);                    // flip-flopping and double-voting count once
        for (Post p : posts) System.out.printf("%-24s score %5d  hot %.4f%n", p.title(), score(p.id()), hot(p));
        System.out.println("front page (hot): " + posts.stream().sorted(Comparator.comparingDouble(VotingRankingSystem::hot).reversed()).map(Post::title).toList());
        System.out.println("top (all time)  : " + posts.stream().sorted(Comparator.comparingInt((Post p) -> score(p.id())).reversed()).map(Post::title).toList());
        System.out.println("12.5 hours of age = 10x the votes: new posts get a chance; votes are buffered and the hot list is cached per subreddit");
    }
}
''', ["Add 'controversial' ranking: high total votes with ups ≈ downs ranks highest.",
      "Store comment trees and render them depth-first sorted by score at each level.",
      "Detect vote rings: many accounts created the same day all upvoting the same posts."])

J("newsagg-hld", r'''
import java.util.*;

public class NewsAggregatorSystem {
    // Fetch articles from sources -> normalise -> cluster near-duplicate stories by word-shingle Jaccard similarity -> rank clusters.
    record Article(String source, String title, int ageHours) {}

    static Set<String> shingles(String t) { String[] w = t.toLowerCase().replaceAll("[^a-z0-9 ]", "").split(" "); Set<String> s = new HashSet<>(); for (int i = 0; i + 1 < w.length; i++) s.add(w[i] + " " + w[i + 1]); return s; }
    static double jaccard(Set<String> a, Set<String> b) { Set<String> i = new HashSet<>(a); i.retainAll(b); Set<String> u = new HashSet<>(a); u.addAll(b); return u.isEmpty() ? 0 : i.size() / (double) u.size(); }

    public static void main(String[] args) {
        List<Article> feed = List.of(new Article("NDTV", "India beat Australia by 6 wickets in Perth Test", 2), new Article("TOI", "India beat Australia by 6 wickets in the Perth Test match", 1),
            new Article("ESPN", "Perth Test: India beat Australia by 6 wickets", 3), new Article("Reuters", "RBI keeps repo rate unchanged at 6.5 percent", 4),
            new Article("Mint", "RBI keeps repo rate unchanged at 6.5 percent for tenth time", 5), new Article("Verge", "New phone launched with bigger battery", 1));
        List<List<Article>> clusters = new ArrayList<>(); List<Set<String>> reps = new ArrayList<>();
        for (Article a : feed) {
            Set<String> sh = shingles(a.title()); int best = -1; double bestSim = 0.3;
            for (int i = 0; i < reps.size(); i++) { double s = jaccard(sh, reps.get(i)); if (s >= bestSim) { bestSim = s; best = i; } }
            if (best < 0) { clusters.add(new ArrayList<>(List.of(a))); reps.add(sh); } else clusters.get(best).add(a);
        }
        clusters.sort(Comparator.comparingDouble((List<Article> c) -> -(c.size() * 10 - c.stream().mapToInt(Article::ageHours).min().getAsInt())));
        for (List<Article> c : clusters) System.out.printf("story (%d sources, freshest %dh): %s%n   covered by %s%n", c.size(), c.stream().mapToInt(Article::ageHours).min().getAsInt(), c.get(0).title(), c.stream().map(Article::source).toList());
    }
}
''', ["Use MinHash (k random hash functions over the shingles) so clustering scales to millions of articles.",
      "Personalise ranking with a user's topic weights (e.g. cricket 2.0, finance 0.5).",
      "Add source diversity: never show 2 stories in a row from the same source."])

J("wallet-hld", r'''
import java.util.*;
import java.util.concurrent.*;

public class DigitalWalletSystem {
    // UPI-style transfer: idempotent request id, PIN-less here, per-account locking in a fixed order (no deadlocks),
    // double-entry ledger, daily limit, and a pending state when the bank switch times out.
    static final Map<String, Long> balance = new ConcurrentHashMap<>(Map.of("asha@upi", 10_000_00L, "ravi@upi", 2_000_00L, "shop@upi", 0L));
    static final Map<String, Object> locks = new ConcurrentHashMap<>();
    static final Map<String, String> requests = new ConcurrentHashMap<>();
    static final List<String> ledger = Collections.synchronizedList(new ArrayList<>());
    static final Map<String, Long> sentToday = new ConcurrentHashMap<>();
    static final long DAILY_LIMIT = 1_00_000_00L;

    static String transfer(String reqId, String from, String to, long paise) {
        return requests.computeIfAbsent(reqId, k -> {
            if (sentToday.getOrDefault(from, 0L) + paise > DAILY_LIMIT) return "DECLINED daily limit";
            String a = from.compareTo(to) < 0 ? from : to, b = from.compareTo(to) < 0 ? to : from;          // lock in a global order
            synchronized (locks.computeIfAbsent(a, x -> new Object())) { synchronized (locks.computeIfAbsent(b, x -> new Object())) {
                if (balance.get(from) < paise) return "DECLINED insufficient balance";
                balance.merge(from, -paise, Long::sum); balance.merge(to, paise, Long::sum); sentToday.merge(from, paise, Long::sum);
                ledger.add(reqId + " DR " + from + " " + paise); ledger.add(reqId + " CR " + to + " " + paise);
            } }
            return "SUCCESS " + reqId;
        });
    }

    public static void main(String[] args) throws Exception {
        System.out.println(transfer("r1", "asha@upi", "shop@upi", 499_00));
        System.out.println(transfer("r1", "asha@upi", "shop@upi", 499_00) + " (retry returns the same result, no double debit)");
        System.out.println(transfer("r2", "ravi@upi", "asha@upi", 5_000_00));
        ExecutorService pool = Executors.newFixedThreadPool(8); List<Future<String>> fs = new ArrayList<>();
        for (int i = 0; i < 200; i++) { final int n = i; fs.add(pool.submit(() -> n % 2 == 0 ? transfer("x" + n, "asha@upi", "ravi@upi", 10_00) : transfer("x" + n, "ravi@upi", "asha@upi", 10_00))); }
        long ok = 0; for (Future<String> f : fs) if (f.get().startsWith("SUCCESS")) ok++; pool.shutdown();
        System.out.println("200 concurrent opposite-direction transfers: " + ok + " succeeded, no deadlock");
        long total = balance.values().stream().mapToLong(Long::longValue).sum();
        System.out.printf("balances %s, total Rs %,.2f (money is conserved)%n", new TreeMap<>(balance), total / 100.0);
        System.out.println("ledger entries: " + ledger.size() + " (2 per successful transfer)");
    }
}
''', ["Add a PENDING state when the bank switch doesn't answer in 30 s, and a reconciliation step that resolves it to SUCCESS or REVERSED.",
      "Add a UPI PIN check with 3 attempts and a 24-hour lock.",
      "Add cashback: 5% up to Rs 50 on the first payment to a merchant, written as its own ledger entries."])

J("auction-hld", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class AuctionSystem {
    // Bids accepted only if higher than current by a minimum increment (atomic compare-and-set), anti-sniping extension, proxy bidding.
    record State(long price, String leader, long endsAt) {}
    static final AtomicReference<State> auction = new AtomicReference<>(new State(1000, null, 600));
    static final Map<String, Long> proxyMax = new ConcurrentHashMap<>();
    static final long INCREMENT = 50;

    static String bid(String user, long amount, long now) {
        while (true) {
            State s = auction.get();
            if (now >= s.endsAt()) return user + " " + amount + " rejected: auction ended";
            if (amount < s.price() + INCREMENT) return user + " " + amount + " rejected: must be >= " + (s.price() + INCREMENT);
            long newEnd = s.endsAt() - now < 60 ? now + 60 : s.endsAt();          // a bid in the last minute extends the auction
            if (auction.compareAndSet(s, new State(amount, user, newEnd))) {
                String r = user + " leads at " + amount + (newEnd != s.endsAt() ? " (extended to t=" + newEnd + ")" : "");
                String rival = s.leader();
                if (rival != null && proxyMax.getOrDefault(rival, 0L) >= amount + INCREMENT) { r += "\n  proxy for " + rival + " -> " + bid(rival, amount + INCREMENT, now); }
                return r;
            }
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println(bid("asha", 1100, 10));
        proxyMax.put("asha", 1500L);                                                     // asha: 'bid for me up to 1500'
        System.out.println(bid("ravi", 1200, 100));
        System.out.println(bid("ravi", 1520, 200));
        System.out.println(bid("zoya", 1550, 300));
        ExecutorService pool = Executors.newFixedThreadPool(8); List<Future<String>> fs = new ArrayList<>();
        for (int i = 0; i < 100; i++) { final long amt = 1600 + i * 10; fs.add(pool.submit(() -> bid("bot" + amt, amt, 400))); }
        int accepted = 0; for (Future<String> f : fs) if (f.get().contains("leads")) accepted++; pool.shutdown();
        System.out.println("100 concurrent bot bids: " + accepted + " accepted in order; leader " + auction.get().leader() + " at " + auction.get().price() + " (never a lower price over a higher one)");
        System.out.println(bid("kiran", 2700, 570));
        System.out.println(bid("asha", 3000, 610) + " | ends at t=" + auction.get().endsAt());
        System.out.println(bid("ravi", 3100, 700));
    }
}
''', ["Broadcast every new leading bid to watchers through an observer list (WebSocket fan-out in production).",
      "Add a reserve price: the item sells only if the final price is above it.",
      "Persist every accepted bid to an append-only log and rebuild the final state from it."])

J("calendar-hld", r'''
import java.util.*;

public class CalendarSchedulingSystem {
    // Events stored per user (sorted by start), free/busy merge across attendees, find the earliest common slot, recurring events expanded.
    record Event(String title, int start, int end) {}                                       // minutes from 00:00
    static final Map<String, List<Event>> calendars = new TreeMap<>();

    static void add(String user, Event e) { calendars.computeIfAbsent(user, k -> new ArrayList<>()).add(e); calendars.get(user).sort(Comparator.comparingInt(Event::start)); }
    static List<int[]> busy(List<String> people) {
        List<int[]> all = new ArrayList<>(); for (String p : people) for (Event e : calendars.getOrDefault(p, List.of())) all.add(new int[]{e.start(), e.end()});
        all.sort(Comparator.comparingInt(a -> a[0])); List<int[]> merged = new ArrayList<>();
        for (int[] iv : all) if (merged.isEmpty() || merged.get(merged.size() - 1)[1] < iv[0]) merged.add(iv.clone()); else merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], iv[1]);
        return merged;
    }
    static String t(int m) { return String.format("%02d:%02d", m / 60, m % 60); }

    public static void main(String[] args) {
        for (int day = 0; day < 1; day++) for (String u : List.of("asha", "ravi", "zoya")) add(u, new Event("standup", 9 * 60 + 30, 9 * 60 + 45));   // recurring daily event, expanded for today
        add("asha", new Event("design review", 10 * 60, 11 * 60)); add("ravi", new Event("1:1", 11 * 60, 11 * 60 + 30));
        add("zoya", new Event("interview", 12 * 60, 13 * 60)); add("ravi", new Event("lunch", 13 * 60, 14 * 60));
        List<String> people = List.of("asha", "ravi", "zoya");
        List<int[]> b = busy(people);
        System.out.println("merged busy: " + b.stream().map(iv -> t(iv[0]) + "-" + t(iv[1])).toList());
        int dayStart = 9 * 60, dayEnd = 18 * 60, need = 45, cursor = dayStart;
        for (int[] iv : b) { if (iv[0] - cursor >= need) break; cursor = Math.max(cursor, iv[1]); }
        System.out.println("earliest 45-min slot for " + people + ": " + (cursor + need <= dayEnd ? t(cursor) + "-" + t(cursor + need) : "none today"));
        int finalCursor = cursor;
        people.forEach(p -> add(p, new Event("planning", finalCursor, finalCursor + need)));
        System.out.println("invites sent; zoya's day: " + calendars.get("zoya").stream().map(e -> t(e.start()) + " " + e.title()).toList());
    }
}
''', ["Respect time zones: store events in UTC and display each attendee's day in their own zone.",
      "Support recurring rules ('every Mon/Wed/Fri until Dec 31') and expand them lazily for the visible week only.",
      "Add reminders: produce (time, user, message) entries 10 minutes before each event, sorted for a scheduler."])

J("cdn-hld", r'''
import java.util.*;

public class CdnSystem {
    // GeoDNS picks the nearest healthy PoP; each PoP has an LRU cache; misses go to a regional shield then origin; byte-hit ratio tracked.
    record Pop(String name, String region, int rttFrom) {}
    static final Map<String, LinkedHashMap<String, Integer>> caches = new HashMap<>();
    static final Map<String, Integer> shield = new HashMap<>(); static int originHits = 0;

    static LinkedHashMap<String, Integer> lru(int cap) { return new LinkedHashMap<>(16, .75f, true) { protected boolean removeEldestEntry(Map.Entry<String, Integer> e) { return size() > cap; } }; }
    static String serve(Pop pop, String path, int sizeKb) {
        LinkedHashMap<String, Integer> c = caches.computeIfAbsent(pop.name(), k -> lru(3));
        if (c.containsKey(path)) { c.get(path); return "HIT  at " + pop.name(); }
        String via;
        if (shield.containsKey(path)) via = "MISS at " + pop.name() + " -> shield HIT"; else { originHits++; shield.put(path, sizeKb); via = "MISS at " + pop.name() + " -> shield MISS -> origin"; }
        c.put(path, sizeKb); return via;
    }

    public static void main(String[] args) {
        Map<String, List<Pop>> geoDns = Map.of("Chennai", List.of(new Pop("chennai-pop", "IN", 5), new Pop("mumbai-pop", "IN", 25)), "Delhi", List.of(new Pop("delhi-pop", "IN", 6), new Pop("mumbai-pop", "IN", 22)));
        Set<String> unhealthy = new HashSet<>();
        String[][] reqs = {{"Chennai", "/logo.png"}, {"Chennai", "/logo.png"}, {"Delhi", "/logo.png"}, {"Chennai", "/v.mp4"}, {"Chennai", "/a.js"}, {"Chennai", "/b.css"}, {"Chennai", "/logo.png"}};
        for (String[] r : reqs) {
            Pop pop = geoDns.get(r[0]).stream().filter(p -> !unhealthy.contains(p.name())).findFirst().get();
            System.out.printf("%-8s %-10s -> %s%n", r[0], r[1], serve(pop, r[1], 50));
        }
        unhealthy.add("chennai-pop");
        Pop failover = geoDns.get("Chennai").stream().filter(p -> !unhealthy.contains(p.name())).findFirst().get();
        System.out.println("chennai-pop fails health checks -> GeoDNS sends Chennai users to " + failover.name() + " (+" + (failover.rttFrom() - 5) + " ms)");
        System.out.println("Chennai  /logo.png -> " + serve(failover, "/logo.png", 50));
        System.out.println("origin was hit " + originHits + " times for " + (reqs.length + 1) + " requests (the shield protects the origin)");
    }
}
''', ["Add TTLs and `stale-while-revalidate` to the PoP caches.",
      "Track byte-hit ratio (bytes served from cache / total bytes) with different object sizes.",
      "Use consistent hashing inside a PoP to spread objects over 4 cache servers."])

J("pricealert-hld", r'''
import java.util.*;

public class PriceAlertSystem {
    // Millions of alerts indexed by product and sorted by target price: a price update only scans alerts whose target >= new price.
    record Alert(String user, String product, long targetPaise, String id) {}
    static final Map<String, TreeMap<Long, List<Alert>>> index = new HashMap<>();      // product -> target -> alerts
    static final Set<String> fired = new HashSet<>();

    static void subscribe(Alert a) { index.computeIfAbsent(a.product(), k -> new TreeMap<>()).computeIfAbsent(a.targetPaise(), k -> new ArrayList<>()).add(a); }
    static void onPriceChange(String product, long newPrice) {
        NavigableMap<Long, List<Alert>> hit = index.getOrDefault(product, new TreeMap<>()).tailMap(newPrice, true);   // all targets >= new price
        int checked = hit.values().stream().mapToInt(List::size).sum();
        System.out.printf("%s now Rs %,d -> %d alert(s) triggered (no scan of the rest)%n", product, newPrice / 100, checked);
        for (List<Alert> l : hit.values()) for (Alert a : l) if (fired.add(a.id())) System.out.println("   notify " + a.user() + ": " + product + " dropped below Rs " + String.format("%,d", a.targetPaise() / 100));
        hit.clear();                                                                       // one-shot alerts are removed after firing
    }

    public static void main(String[] args) {
        subscribe(new Alert("asha", "iphone-16", 65_000_00, "a1")); subscribe(new Alert("ravi", "iphone-16", 60_000_00, "a2"));
        subscribe(new Alert("zoya", "iphone-16", 70_000_00, "a3")); subscribe(new Alert("kiran", "ps5", 40_000_00, "a4"));
        Random r = new Random(1); for (int i = 0; i < 100_000; i++) subscribe(new Alert("u" + i, "iphone-16", (30_000 + r.nextInt(20_000)) * 100L, "b" + i));
        System.out.println("alerts indexed: " + index.get("iphone-16").values().stream().mapToInt(List::size).sum() + " for iphone-16");
        onPriceChange("iphone-16", 72_000_00);
        onPriceChange("iphone-16", 68_000_00);
        onPriceChange("iphone-16", 64_999_00);
        onPriceChange("ps5", 44_990_00);
        System.out.println("prices come from scrapers/partner feeds into a stream; only changed prices trigger this check");
    }
}
''', ["Add recurring alerts that re-arm when the price goes back above the target by 5%.",
      "Throttle notifications: at most one alert per user per product per day.",
      "Partition the index by product across 4 'workers' and route each price update to its worker."])
