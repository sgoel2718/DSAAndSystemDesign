"""Java practice programs: HLD questions 25-36."""
from sd_j_util import J

J("adclick-hld", r'''
import java.util.*;

public class AdClickAggregationSystem {
    // Click events -> dedupe by click id -> tumbling 1-minute windows by EVENT time with watermark -> per-ad counts -> reconcile with batch.
    record Click(String clickId, String adId, long eventSec, long arrivalSec) {}

    public static void main(String[] args) {
        List<Click> stream = List.of(new Click("c1", "ad7", 5, 6), new Click("c2", "ad7", 20, 21), new Click("c2", "ad7", 20, 22),      // c2 retried by the client
            new Click("c3", "ad9", 50, 51), new Click("c4", "ad7", 65, 66), new Click("c5", "ad9", 58, 75),                              // c5 arrives 17 s late
            new Click("c6", "ad9", 130, 131), new Click("c7", "ad7", 40, 200));                                                         // c7 is very late
        Set<String> seen = new HashSet<>(); Map<Long, Map<String, Integer>> open = new TreeMap<>(), emitted = new TreeMap<>();
        long watermark = 0, allowedLateness = 30; List<Click> lateForBatch = new ArrayList<>();
        for (Click c : stream) {
            if (!seen.add(c.clickId())) { System.out.println("dedupe: dropped duplicate " + c.clickId()); continue; }
            long window = c.eventSec() / 60 * 60;
            if (window + 60 + allowedLateness <= watermark) { lateForBatch.add(c); System.out.println("too late for streaming: " + c.clickId() + " (left for the batch job)"); continue; }
            open.computeIfAbsent(window, k -> new TreeMap<>()).merge(c.adId(), 1, Integer::sum);
            watermark = Math.max(watermark, c.arrivalSec() - 5);                   // watermark trails arrival time a little
            for (Iterator<Map.Entry<Long, Map<String, Integer>>> it = open.entrySet().iterator(); it.hasNext(); ) {
                var e = it.next();
                if (e.getKey() + 60 + allowedLateness <= watermark) { emitted.put(e.getKey(), e.getValue()); System.out.println("emit window [" + e.getKey() + "," + (e.getKey() + 60) + ") -> " + e.getValue()); it.remove(); }
            }
        }
        open.forEach((w, v) -> { emitted.put(w, v); System.out.println("emit window [" + w + "," + (w + 60) + ") at shutdown -> " + v); });
        Map<Long, Map<String, Integer>> batch = new TreeMap<>(); Set<String> s2 = new HashSet<>();
        for (Click c : stream) if (s2.add(c.clickId())) batch.computeIfAbsent(c.eventSec() / 60 * 60, k -> new TreeMap<>()).merge(c.adId(), 1, Integer::sum);
        System.out.println("nightly batch (exact) : " + batch);
        System.out.println("streaming (real-time) : " + emitted + " -> batch result replaces it for billing (lambda-style reconciliation)");
    }
}
''', ["Add click-fraud filtering: ignore more than 3 clicks from the same IP on the same ad within 60 seconds.",
      "Partition the aggregation by adId across 3 'workers' (hash) and merge their window outputs.",
      "Add a top-2 ads per window to the emitted result."])

J("jobscheduler-hld", r'''
import java.util.*;
import java.util.concurrent.*;

public class DistributedJobSchedulerSystem {
    // Jobs bucketed by due minute (time-bucketed table), workers claim with leases, retries with backoff, at-least-once execution.
    record Job(String id, long dueAt, int attempt, int maxAttempts) {}
    static final TreeMap<Long, List<Job>> buckets = new TreeMap<>();
    static final Map<String, Long> leases = new HashMap<>(); static final Map<String, String> results = new TreeMap<>();

    static void schedule(Job j) { buckets.computeIfAbsent(j.dueAt() / 60 * 60, k -> new ArrayList<>()).add(j); }

    public static void main(String[] args) {
        schedule(new Job("send-report", 0, 1, 3)); schedule(new Job("charge-subscription", 30, 1, 3)); schedule(new Job("flaky-webhook", 30, 1, 3));
        schedule(new Job("cleanup", 300, 1, 1));
        Map<String, Integer> failuresLeft = new HashMap<>(Map.of("flaky-webhook", 2));
        for (long now = 0; now <= 420; now += 60) {
            var due = new ArrayList<Job>(); buckets.headMap(now, true).values().forEach(due::addAll); buckets.headMap(now, true).clear();   // only scan buckets that are due
            for (Job j : due) {
                String worker = "worker-" + (Math.abs(j.id().hashCode()) % 3 + 1);
                leases.put(j.id(), now + 30);
                boolean fail = failuresLeft.merge(j.id(), -1, Integer::sum) >= 0 && failuresLeft.get(j.id()) >= 0 && j.id().equals("flaky-webhook");
                if (!fail) { results.put(j.id(), "DONE at t=" + now + " by " + worker + " (attempt " + j.attempt() + ")"); System.out.println("t=" + now + " " + worker + " ran " + j.id() + " ✔"); }
                else if (j.attempt() < j.maxAttempts()) { long backoff = 60L << (j.attempt() - 1); schedule(new Job(j.id(), now + backoff, j.attempt() + 1, j.maxAttempts())); System.out.println("t=" + now + " " + worker + " ran " + j.id() + " ✘ -> retry in " + backoff + " s"); }
                else { results.put(j.id(), "FAILED after " + j.attempt() + " attempts -> dead-letter + alert"); }
                leases.remove(j.id());
            }
        }
        results.forEach((k, v) -> System.out.println(k + ": " + v));
    }
}
''', ["Add recurring jobs: after a run, compute the next due time from an interval and reschedule.",
      "Simulate a worker crash (lease not removed) and have the next tick re-run jobs whose lease expired.",
      "Run the due jobs on a real `ScheduledExecutorService` with a thread pool of 3."])

J("email-hld", r'''
import java.util.*;

public class EmailServiceSystem {
    // SMTP receive -> spam score -> store message once + per-user mailbox entries -> labels/threads -> full-text search.
    record Message(String id, String from, List<String> to, String subject, String body, String threadId) {}
    static final Map<String, Message> messageStore = new LinkedHashMap<>();
    static final Map<String, Map<String, Set<String>>> mailboxes = new TreeMap<>();      // user -> messageId -> labels
    static final Map<String, Map<String, Set<String>>> searchIndex = new HashMap<>();   // user -> word -> messageIds
    static int seq = 0;

    static double spamScore(Message m) { double s = 0; String t = (m.subject() + " " + m.body()).toLowerCase(); for (String w : List.of("lottery", "winner", "free money", "click here")) if (t.contains(w)) s += 0.3; if (!m.from().endsWith(".com") && !m.from().endsWith(".in")) s += 0.2; return s; }

    static void receive(String from, List<String> to, String subject, String body, String inReplyTo) {
        String id = "m" + (++seq); String thread = inReplyTo != null ? messageStore.get(inReplyTo).threadId() : id;
        Message m = new Message(id, from, to, subject, body, thread); messageStore.put(id, m);           // stored once, even for many recipients
        String label = spamScore(m) >= 0.5 ? "SPAM" : "INBOX";
        for (String u : to) {
            mailboxes.computeIfAbsent(u, k -> new LinkedHashMap<>()).put(id, new TreeSet<>(Set.of(label, "UNREAD")));
            for (String w : (subject + " " + body).toLowerCase().split("\\W+")) searchIndex.computeIfAbsent(u, k -> new HashMap<>()).computeIfAbsent(w, k -> new TreeSet<>()).add(id);
        }
        System.out.printf("%s from %-20s -> %s [%s, spam score %.1f]%n", id, from, to, label, spamScore(m));
    }

    public static void main(String[] args) {
        receive("hr@company.com", List.of("asha@mail.com", "ravi@mail.com"), "Offsite on Friday", "Team offsite at Lonavala", null);
        receive("asha@mail.com", List.of("hr@company.com", "ravi@mail.com"), "Re: Offsite on Friday", "Count me in", "m1");
        receive("prize@win.biz", List.of("asha@mail.com"), "You are a WINNER", "Claim your lottery prize, click here", null);
        System.out.println("asha's inbox: " + mailboxes.get("asha@mail.com"));
        System.out.println("ravi's thread view: " + messageStore.values().stream().filter(m -> m.threadId().equals("m1") && mailboxes.get("ravi@mail.com").containsKey(m.id())).map(Message::subject).toList());
        System.out.println("asha searches 'offsite': " + searchIndex.get("asha@mail.com").get("offsite"));
        System.out.println("messages stored: " + messageStore.size() + ", mailbox entries: " + mailboxes.values().stream().mapToInt(Map::size).sum());
    }
}
''', ["Add 'mark as read' and an unread count per label.",
      "Store large attachments in an object store keyed by hash and keep only the key in the message.",
      "Add a rule engine: 'if from contains @company.com then add label Work'."])

J("s3-hld", r'''
import java.security.MessageDigest;
import java.util.*;

public class ObjectStorageSystem {
    // Metadata service (bucket/key -> object version, placement) + data nodes; erasure-coding-lite with XOR parity; recovery from a lost node.
    static final Map<String, byte[][]> dataNodes = new TreeMap<>();                // node -> stored fragment (one per object here)
    record ObjectMeta(String bucket, String key, int size, String etag, List<String> placement) {}
    static final Map<String, ObjectMeta> metadata = new TreeMap<>();

    static String md5(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("MD5").digest(b)).substring(0, 12); }

    static void put(String bucket, String key, byte[] data) throws Exception {
        int half = (data.length + 1) / 2;
        byte[] a = Arrays.copyOfRange(data, 0, half), b = Arrays.copyOf(Arrays.copyOfRange(data, half, data.length), half), parity = new byte[half];
        for (int i = 0; i < half; i++) parity[i] = (byte) (a[i] ^ b[i]);          // 2 data + 1 parity: survives losing any one node (1.5x storage, not 3x)
        List<String> nodes = List.of("node-1", "node-2", "node-3");
        dataNodes.put("node-1", new byte[][]{a}); dataNodes.put("node-2", new byte[][]{b}); dataNodes.put("node-3", new byte[][]{parity});
        metadata.put(bucket + "/" + key, new ObjectMeta(bucket, key, data.length, md5(data), nodes));
    }
    static byte[] get(String bucket, String key) {
        ObjectMeta m = metadata.get(bucket + "/" + key);
        byte[][] a = dataNodes.get("node-1"), b = dataNodes.get("node-2"), p = dataNodes.get("node-3");
        byte[] x = a != null ? a[0] : null, y = b != null ? b[0] : null;
        if (x == null) { x = new byte[y.length]; for (int i = 0; i < y.length; i++) x[i] = (byte) (y[i] ^ p[0][i]); System.out.println("  node-1 lost -> rebuilt its fragment from node-2 XOR parity"); }
        if (y == null) { y = new byte[x.length]; for (int i = 0; i < x.length; i++) y[i] = (byte) (x[i] ^ p[0][i]); }
        byte[] out = new byte[m.size()]; System.arraycopy(x, 0, out, 0, x.length); System.arraycopy(y, 0, out, x.length, m.size() - x.length);
        return out;
    }

    public static void main(String[] args) throws Exception {
        byte[] photo = "PRETEND-JPEG-BYTES-OF-A-CAT-PHOTO".getBytes();
        put("photos", "2026/11/cat.jpg", photo);
        System.out.println("PUT photos/2026/11/cat.jpg -> " + metadata.get("photos/2026/11/cat.jpg"));
        System.out.println("GET -> " + new String(get("photos", "2026/11/cat.jpg")));
        dataNodes.remove("node-1");
        byte[] back = get("photos", "2026/11/cat.jpg");
        System.out.println("GET after losing node-1 -> " + new String(back) + " | etag matches: " + md5(back).equals(metadata.get("photos/2026/11/cat.jpg").etag()));
        System.out.println("storage overhead: 3 fragments of " + (photo.length + 1) / 2 + " bytes = 1.5x (3-way replication would be 3x)");
    }
}
''', ["Add object versioning: keep older versions in metadata and support GET by version id.",
      "Spread fragments of different objects across 6 nodes using consistent hashing.",
      "Add multipart upload: upload parts separately, then `complete` assembles them and computes the final etag."])

J("fooddelivery-hld", r'''
import java.util.*;

public class FoodDeliverySystem {
    // Order state machine across restaurant + rider; rider assignment by ETA (distance + current load); live ETA updates.
    enum S { PLACED, ACCEPTED, PREPARING, RIDER_ASSIGNED, PICKED_UP, DELIVERED, CANCELLED }
    static final Map<S, Set<S>> allowed = new EnumMap<>(Map.of(S.PLACED, EnumSet.of(S.ACCEPTED, S.CANCELLED), S.ACCEPTED, EnumSet.of(S.PREPARING, S.CANCELLED),
        S.PREPARING, EnumSet.of(S.RIDER_ASSIGNED), S.RIDER_ASSIGNED, EnumSet.of(S.PICKED_UP), S.PICKED_UP, EnumSet.of(S.DELIVERED), S.DELIVERED, EnumSet.noneOf(S.class), S.CANCELLED, EnumSet.noneOf(S.class)));
    record Rider(String id, double kmFromRestaurant, int activeOrders) {}

    static S move(S from, S to) { if (!allowed.get(from).contains(to)) throw new IllegalStateException(from + " -> " + to + " not allowed"); System.out.println("  order: " + from + " -> " + to); return to; }

    public static void main(String[] args) {
        S s = S.PLACED;
        s = move(s, S.ACCEPTED); s = move(s, S.PREPARING);
        int prepMin = 15;
        List<Rider> riders = List.of(new Rider("r1", 0.5, 2), new Rider("r2", 1.8, 0), new Rider("r3", 4.0, 0));
        Rider best = riders.stream().min(Comparator.comparingDouble(r -> Math.max(r.kmFromRestaurant() / 20 * 60 + r.activeOrders() * 8, prepMin))).get();
        riders.forEach(r -> System.out.printf("  rider %s: %.1f km away, %d active -> ready to pick up in %.0f min%n", r.id(), r.kmFromRestaurant(), r.activeOrders(), Math.max(r.kmFromRestaurant() / 20 * 60 + r.activeOrders() * 8, prepMin)));
        System.out.println("  assign " + best.id() + " (arrives as food is ready, not the nearest one who is busy)");
        s = move(s, S.RIDER_ASSIGNED); s = move(s, S.PICKED_UP);
        double kmToCustomer = 3.2;
        for (int minute = 0; minute <= 9; minute += 3) System.out.printf("  live ETA at +%d min: %.0f min (rider location every 5 s, sent to the customer app)%n", minute, Math.max(0, kmToCustomer / 20 * 60 - minute));
        s = move(s, S.DELIVERED);
        try { move(s, S.CANCELLED); } catch (IllegalStateException e) { System.out.println("  rejected: " + e.getMessage()); }
    }
}
''', ["Batch orders: let a rider take 2 orders from the same restaurant if both customers are within 1 km of each other.",
      "Add a restaurant timeout: if not ACCEPTED within 3 minutes, auto-cancel and refund.",
      "Compute delivery fee by distance with surge when riders are scarce."])

J("onlinejudge-hld", r'''
import javax.tools.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public class OnlineJudgeSystem {
    // Submission -> queue -> sandboxed worker compiles & runs against test cases with a time limit -> verdict.
    // Here the 'sandbox' is a separate JVM process with a timeout; production adds containers, seccomp, memory/CPU limits.
    static String judge(String code, List<String[]> tests) throws Exception {
        Path dir = Files.createTempDirectory("judge"); Path src = dir.resolve("Solution.java"); Files.writeString(src, code);
        JavaCompiler javac = ToolProvider.getSystemJavaCompiler();
        ByteArrayOutputStream err = new ByteArrayOutputStream();
        if (javac.run(null, null, err, src.toString()) != 0) return "Compilation Error";
        int passed = 0;
        for (String[] t : tests) {
            ProcessBuilder pb = new ProcessBuilder("java", "-Xmx64m", "-cp", dir.toString(), "Solution");
            pb.environment().remove("JAVA_TOOL_OPTIONS"); pb.redirectError(ProcessBuilder.Redirect.DISCARD);
            Process p = pb.start();
            try (Writer w = new OutputStreamWriter(p.getOutputStream())) { w.write(t[0]); }
            if (!p.waitFor(2, TimeUnit.SECONDS)) { p.destroyForcibly(); return "Time Limit Exceeded on test " + (passed + 1); }
            String out = new String(p.getInputStream().readAllBytes()).trim();
            if (p.exitValue() != 0) return "Runtime Error on test " + (passed + 1);
            if (!out.equals(t[1])) return "Wrong Answer on test " + (passed + 1) + " (expected " + t[1] + ", got " + out + ")";
            passed++;
        }
        return "Accepted (" + passed + "/" + tests.size() + ")";
    }

    public static void main(String[] args) throws Exception {
        List<String[]> twoSumTests = List.of(new String[]{"2 7 11 15\n9", "0 1"}, new String[]{"3 2 4\n6", "1 2"}, new String[]{"3 3\n6", "0 1"});
        String good = "import java.util.*; public class Solution { public static void main(String[] a) { Scanner s = new Scanner(System.in); String[] p = s.nextLine().trim().split(\" \"); int t = Integer.parseInt(s.nextLine().trim()); Map<Integer,Integer> m = new HashMap<>(); for (int i = 0; i < p.length; i++) { int x = Integer.parseInt(p[i]); if (m.containsKey(t - x)) { System.out.println(m.get(t - x) + \" \" + i); return; } m.put(x, i); } } }";
        String wrong = good.replace("m.get(t - x) + \" \" + i", "i + \" \" + m.get(t - x)");
        String slow = "public class Solution { public static void main(String[] a) { while (true) {} } }";
        String broken = "public class Solution { void x( }";
        Map<String, String> subs = new LinkedHashMap<>(); subs.put("asha (hash map)", good); subs.put("ravi (swapped output)", wrong); subs.put("zoya (infinite loop)", slow); subs.put("kiran (syntax error)", broken);
        ExecutorService workers = Executors.newFixedThreadPool(2); Map<String, Future<String>> verdicts = new LinkedHashMap<>();
        for (var e : subs.entrySet()) verdicts.put(e.getKey(), workers.submit(() -> judge(e.getValue(), twoSumTests)));
        for (var e : verdicts.entrySet()) System.out.printf("%-22s -> %s%n", e.getKey(), e.getValue().get());
        workers.shutdown();
    }
}
''', ["Measure and report the run time per test and the maximum across tests.",
      "Add a 'memory limit exceeded' verdict by running with `-Xmx16m` and a solution that allocates a huge array.",
      "Cache verdicts by hash of (code + problem id) so resubmitting identical code is instant."])

J("leaderboard-hld", r'''
import java.util.*;
import java.util.concurrent.*;

public class GamingLeaderboardSystem {
    // Score events -> per-season sorted set (ConcurrentSkipListSet) -> top-N, my rank, and friends leaderboard.
    record Entry(long score, long achievedAt, String player) implements Comparable<Entry> {
        public int compareTo(Entry o) { int c = Long.compare(o.score, score); if (c != 0) return c; c = Long.compare(achievedAt, o.achievedAt); return c != 0 ? c : player.compareTo(o.player); }
    }
    static final ConcurrentSkipListSet<Entry> board = new ConcurrentSkipListSet<>();
    static final ConcurrentHashMap<String, Entry> current = new ConcurrentHashMap<>();

    static void addScore(String p, long points, long ts) {
        current.compute(p, (k, old) -> { if (old != null) board.remove(old); Entry e = new Entry((old == null ? 0 : old.score()) + points, ts, p); board.add(e); return e; });
    }
    static int rank(String p) { return board.headSet(current.get(p)).size() + 1; }

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4); Random r = new Random(7); List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < 4; i++) { final int part = i; fs.add(pool.submit(() -> { for (int g = 0; g < 25_000; g++) { int p = part * 25_000 + g; synchronized (GamingLeaderboardSystem.class) { addScore("p" + (p % 50_000), (p * 7919L) % 1000, p); } } })); }
        for (Future<?> f : fs) f.get(); pool.shutdown();
        addScore("asha", 1500, 200_000); addScore("ravi", 900, 200_001); addScore("zoya", 1500, 200_002);
        System.out.println("players: " + current.size());
        System.out.println("top 5: " + board.stream().limit(5).map(e -> e.player() + "=" + e.score()).toList());
        System.out.println("asha rank " + rank("asha") + ", zoya rank " + rank("zoya") + " (same score, asha got there first)");
        List<String> friends = List.of("asha", "ravi", "zoya", "p42");
        System.out.println("friends board: " + friends.stream().map(current::get).sorted().map(e -> e.player() + "=" + e.score()).toList());
        if (r.nextInt() == 42) System.out.println();
    }
}
''', ["Add 'players around me' (2 above, 2 below asha).",
      "Reset the board for a new season while keeping last season's top 100 in a 'hall of fame' list.",
      "Replace `synchronized` with per-player striping (lock on `player.hashCode() % 16`) and check correctness."])

J("googledocs-hld", r'''
import java.util.*;

public class CollaborativeEditingSystem {
    // Operational Transformation for concurrent inserts/deletes on one text: the server orders ops and transforms late ones.
    record Op(String type, int pos, String text, String user, int baseVersion) {}
    static String doc = "Hello world"; static final List<Op> history = new ArrayList<>();

    static Op transform(Op op, Op applied) {                       // shift op's position by an op that was applied before it
        int pos = op.pos();
        if (applied.type().equals("ins") && (applied.pos() < pos || (applied.pos() == pos && applied.user().compareTo(op.user()) < 0))) pos += applied.text().length();
        if (applied.type().equals("del") && applied.pos() < pos) pos -= Math.min(applied.text().length(), pos - applied.pos());
        return new Op(op.type(), pos, op.text(), op.user(), op.baseVersion());
    }
    static void receive(Op op) {
        Op t = op;
        for (int v = op.baseVersion(); v < history.size(); v++) t = transform(t, history.get(v));      // ops the client hadn't seen
        if (t.type().equals("ins")) doc = doc.substring(0, t.pos()) + t.text() + doc.substring(t.pos());
        else doc = doc.substring(0, t.pos()) + doc.substring(t.pos() + t.text().length());
        history.add(t);
        System.out.printf("v%d %-5s %s %-9s at %2d (sent at %2d, base v%d) -> \"%s\"%n", history.size(), t.user(), t.type(), "'" + t.text() + "'", t.pos(), op.pos(), op.baseVersion(), doc);
    }

    public static void main(String[] args) {
        System.out.println("v0 \"" + doc + "\"");
        // Asha and Ravi both edit version 0 at the same time
        receive(new Op("ins", 5, ",", "asha", 0));                 // "Hello, world"
        receive(new Op("ins", 11, "!", "ravi", 0));                // Ravi meant the end of "Hello world" -> shifted by 1
        receive(new Op("del", 0, "Hello", "zoya", 0));             // Zoya deletes "Hello" at the start
        receive(new Op("ins", 0, "Hi", "kiran", 3));               // Kiran saw v3 and inserts at the start
        System.out.println("everyone converges to: \"" + doc + "\"");
    }
}
''', ["Apply the same 4 ops without transformation and show the corrupted result.",
      "Add cursors: transform each user's cursor position through every op so it stays on the same character.",
      "Implement a simple CRDT alternative (each character gets a unique id + 'after' reference) and compare."])

J("searchengine-hld", r'''
import java.util.*;

public class SearchEngineSystem {
    // Crawl graph -> PageRank (power iteration) -> inverted index -> query = BM25-ish text score x PageRank.
    public static void main(String[] args) {
        Map<String, List<String>> links = new TreeMap<>(Map.of("wiki", List.of("blog", "docs"), "blog", List.of("wiki"), "docs", List.of("wiki", "blog"), "spam", List.of("spam2"), "spam2", List.of("spam")));
        Map<String, String> text = Map.of("wiki", "java concurrency guide threads locks", "blog", "my java journey and threads", "docs", "official java docs streams",
            "spam", "java java java java cheap pills", "spam2", "buy pills");
        Map<String, Double> pr = new TreeMap<>(); links.keySet().forEach(p -> pr.put(p, 1.0 / links.size()));
        for (int it = 0; it < 30; it++) {
            Map<String, Double> next = new TreeMap<>(); links.keySet().forEach(p -> next.put(p, 0.15 / links.size()));
            links.forEach((p, outs) -> outs.forEach(o -> next.merge(o, 0.85 * pr.get(p) / outs.size(), Double::sum)));
            pr.putAll(next);
        }
        System.out.println("PageRank: " + pr.entrySet().stream().map(e -> String.format("%s=%.3f", e.getKey(), e.getValue())).toList());
        Map<String, Map<String, Integer>> index = new TreeMap<>();
        text.forEach((doc, t) -> { for (String w : t.split(" ")) index.computeIfAbsent(w, k -> new TreeMap<>()).merge(doc, 1, Integer::sum); });
        String q = "java threads";
        Map<String, Double> score = new HashMap<>();
        for (String term : q.split(" ")) {
            Map<String, Integer> post = index.getOrDefault(term, Map.of()); double idf = Math.log(1 + text.size() / (double) post.size());
            post.forEach((doc, tf) -> score.merge(doc, idf * (tf / (tf + 1.2)), Double::sum));               // saturating tf: repeating a word 4x helps little
        }
        System.out.println("query '" + q + "':");
        score.entrySet().stream().sorted(Comparator.comparingDouble((Map.Entry<String, Double> e) -> -(e.getValue() * pr.get(e.getKey()))))
            .forEach(e -> System.out.printf("  %-5s text %.2f x pagerank %.3f = %.3f%n", e.getKey(), e.getValue(), pr.get(e.getKey()), e.getValue() * pr.get(e.getKey())));
    }
}
''', ["Shard the index by document across 2 'servers', query both, and merge the top results.",
      "Add phrase search: store word positions and require 'java concurrency' as consecutive words.",
      "Add a spell-correct step: if a query word has no postings, try words within edit distance 1."])

J("stockexchange-hld", r'''
import java.util.*;

public class MatchingEngineSystem {
    // Limit order book per symbol: bids (highest first) and asks (lowest first), price-time priority and partial fills.
    record Order(long id, String side, long price, long qty, long seq) {}
    static final TreeMap<Long, Deque<Order>> bids = new TreeMap<>(Comparator.reverseOrder()), asks = new TreeMap<>();
    static long seq = 0; static final List<String> trades = new ArrayList<>();

    static void submit(String side, long price, long qty) {
        Order o = new Order(++seq, side, price, qty, seq); long remaining = qty;
        TreeMap<Long, Deque<Order>> book = side.equals("BUY") ? asks : bids;
        while (remaining > 0 && !book.isEmpty()) {
            long best = book.firstKey();
            if (side.equals("BUY") ? best > price : best < price) break;          // no crossing
            Deque<Order> level = book.firstEntry().getValue(); Order resting = level.peekFirst();
            long fill = Math.min(remaining, resting.qty()); remaining -= fill;
            trades.add(String.format("trade %d @ %d (taker #%d %s, maker #%d)", fill, best, o.id(), side, resting.id()));
            level.pollFirst();
            if (resting.qty() > fill) level.addFirst(new Order(resting.id(), resting.side(), resting.price(), resting.qty() - fill, resting.seq()));
            if (level.isEmpty()) book.pollFirstEntry();
        }
        if (remaining > 0) (side.equals("BUY") ? bids : asks).computeIfAbsent(price, k -> new ArrayDeque<>()).addLast(new Order(o.id(), side, price, remaining, o.seq()));
    }
    static String book() { return "bids " + summary(bids) + " | asks " + summary(asks); }
    static String summary(TreeMap<Long, Deque<Order>> b) { List<String> out = new ArrayList<>(); b.forEach((p, q) -> out.add(q.stream().mapToLong(Order::qty).sum() + "@" + p)); return out.toString(); }

    public static void main(String[] args) {
        submit("SELL", 101, 50); submit("SELL", 102, 100); submit("SELL", 101, 30); submit("BUY", 99, 40); submit("BUY", 100, 25);
        System.out.println("book: " + book());
        submit("BUY", 102, 120);                                                   // sweeps 101 (two orders, time priority) then part of 102
        trades.forEach(t -> System.out.println("  " + t));
        System.out.println("book: " + book());
        submit("SELL", 99, 70);
        System.out.println("after aggressive sell: " + trades.subList(trades.size() - 2, trades.size()) + "\nbook: " + book());
    }
}
''', ["Add cancel(orderId) that removes a resting order from its price level.",
      "Add market orders (no price: take the best available until filled).",
      "Write every incoming order to a sequenced log and rebuild the book by replaying it (how exchanges recover)."])

J("mq-hld", r'''
import java.util.*;

public class DistributedLogQueueSystem {
    // Partitioned, replicated log: leader + followers per partition, acks=all with ISR, high-watermark, consumer offsets, leader failover.
    static class Replica { final String broker; final List<String> log = new ArrayList<>(); boolean alive = true; Replica(String b) { broker = b; } }
    static class Partition {
        final List<Replica> replicas; Replica leader; long highWatermark = 0;
        Partition(List<Replica> r) { replicas = r; leader = r.get(0); }
        String produce(String msg, int minInSync) {
            List<Replica> isr = replicas.stream().filter(r -> r.alive).toList();
            if (isr.size() < minInSync) return "REJECTED (not enough in-sync replicas)";
            for (Replica r : isr) r.log.add(msg);                                   // leader appends, followers fetch
            highWatermark = leader.log.size();                                       // committed = replicated to all ISR
            return "acked at offset " + (highWatermark - 1) + " on " + isr.stream().map(r -> r.broker).toList();
        }
        List<String> consume(long from) { return leader.log.subList((int) from, (int) highWatermark); }
        void failover() { leader.alive = false; leader = replicas.stream().filter(r -> r.alive).max(Comparator.comparingInt(r -> r.log.size())).get(); }
    }

    public static void main(String[] args) {
        Partition p0 = new Partition(List.of(new Replica("broker-1"), new Replica("broker-2"), new Replica("broker-3")));
        for (String m : List.of("order-1", "order-2", "order-3")) System.out.println("produce " + m + " -> " + p0.produce(m, 2));
        long committedOffset = 0;
        List<String> batch = p0.consume(committedOffset); committedOffset += batch.size();
        System.out.println("consumer group 'billing' read " + batch + ", committed offset " + committedOffset);
        p0.failover(); System.out.println("broker-1 (leader) dies -> new leader " + p0.leader.broker + " with " + p0.leader.log.size() + " messages (nothing committed was lost)");
        System.out.println("produce order-4 -> " + p0.produce("order-4", 2));
        System.out.println("billing resumes from offset " + committedOffset + " -> " + p0.consume(committedOffset));
        p0.replicas.get(1).alive = false;
        System.out.println("broker-2 also dies; produce order-5 with min.insync=2 -> " + p0.produce("order-5", 2));
    }
}
''', ["Add 3 partitions and a producer that picks the partition by hash(key).",
      "Make a follower lag (it misses the last message) and show it is dropped from the ISR, so acks don't wait for it.",
      "Add a consumer group rebalance when a second consumer joins (assign partitions round-robin)."])

J("maps-hld", r'''
import java.util.*;

public class MapsRoutingSystem {
    // Road graph with travel times; Dijkstra for the fastest route; live traffic changes edge weights; ETA recomputed.
    static final Map<String, Map<String, Integer>> g = new TreeMap<>();            // node -> (neighbour -> minutes)
    static void road(String a, String b, int min) { g.computeIfAbsent(a, k -> new TreeMap<>()).put(b, min); g.computeIfAbsent(b, k -> new TreeMap<>()).put(a, min); }

    static List<String> fastest(String src, String dst, int[] totalOut) {
        Map<String, Integer> dist = new HashMap<>(); Map<String, String> prev = new HashMap<>();
        PriorityQueue<Map.Entry<String, Integer>> pq = new PriorityQueue<>(Map.Entry.comparingByValue());
        dist.put(src, 0); pq.add(Map.entry(src, 0)); int settled = 0;
        while (!pq.isEmpty()) {
            var cur = pq.poll(); String u = cur.getKey(); if (cur.getValue() > dist.get(u)) continue; settled++;
            if (u.equals(dst)) break;
            for (var e : g.get(u).entrySet()) { int nd = dist.get(u) + e.getValue(); if (nd < dist.getOrDefault(e.getKey(), Integer.MAX_VALUE)) { dist.put(e.getKey(), nd); prev.put(e.getKey(), u); pq.add(Map.entry(e.getKey(), nd)); } }
        }
        LinkedList<String> path = new LinkedList<>(); for (String at = dst; at != null; at = prev.get(at)) path.addFirst(at);
        totalOut[0] = dist.get(dst); totalOut[1] = settled; return path;
    }

    public static void main(String[] args) {
        road("Home", "Ring Rd", 6); road("Ring Rd", "Highway", 5); road("Highway", "Airport", 12); road("Home", "Old Town", 4);
        road("Old Town", "Market", 7); road("Market", "Airport", 15); road("Ring Rd", "Market", 6); road("Old Town", "Ring Rd", 3);
        int[] t = new int[2];
        System.out.println("fastest Home -> Airport: " + fastest("Home", "Airport", t) + " = " + t[0] + " min (" + t[1] + " nodes settled)");
        g.get("Highway").put("Airport", 35); g.get("Airport").put("Highway", 35);   // traffic jam reported by phones' GPS speeds
        System.out.println("traffic jam on Highway -> reroute: " + fastest("Home", "Airport", t) + " = " + t[0] + " min");
        System.out.println("at country scale: precompute shortcuts (contraction hierarchies) and split the map into tiles/regions so a query settles thousands of nodes, not millions");
    }
}
''', ["Add A*: use straight-line distance / max speed as the heuristic and compare nodes settled.",
      "Return the top 2 alternative routes (run Dijkstra again with the first route's edges penalised).",
      "Model traffic per time of day: edge weight = base × factor[hour] and plan a trip leaving at 9 am vs 11 pm."])
