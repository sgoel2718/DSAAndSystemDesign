"""Java practice programs: Building Blocks tab."""
from sd_j_util import J

J("load-balancer", r'''
import java.util.*;

public class LoadBalancerDemo {
    static class Backend {
        final String name; boolean alive = true, healthy = true; int failedChecks, served;
        Backend(String name) { this.name = name; }
        boolean healthCheck() { return alive; }                             // real LB: GET /health with a timeout
    }

    static class LoadBalancer {
        final List<Backend> pool; int next = 0; final int unhealthyAfter = 3;
        LoadBalancer(List<Backend> pool) { this.pool = pool; }
        void runHealthChecks() {
            for (Backend b : pool) {
                if (b.healthCheck()) { b.failedChecks = 0; if (!b.healthy) System.out.println("  health: " + b.name + " back in pool"); b.healthy = true; }
                else if (++b.failedChecks >= unhealthyAfter && b.healthy) { b.healthy = false; System.out.println("  health: " + b.name + " removed after 3 failed checks"); }
            }
        }
        String route(int reqId) {
            for (int i = 0; i < pool.size(); i++) {
                Backend b = pool.get(next++ % pool.size());
                if (!b.healthy) continue;
                if (!b.alive) return "req " + reqId + " -> " + b.name + " FAILED (not yet detected)";
                b.served++; return "req " + reqId + " -> " + b.name;
            }
            return "req " + reqId + " -> 503 no healthy backends";
        }
    }

    public static void main(String[] args) {
        List<Backend> pool = List.of(new Backend("app-1"), new Backend("app-2"), new Backend("app-3"));
        LoadBalancer lb = new LoadBalancer(pool);
        int req = 0;
        for (int tick = 1; tick <= 6; tick++) {
            if (tick == 2) { pool.get(1).alive = false; System.out.println("tick 2: app-2 crashes"); }
            if (tick == 6) { pool.get(1).alive = true; System.out.println("tick 6: app-2 restarted"); }
            lb.runHealthChecks();
            System.out.println("tick " + tick + ": " + lb.route(++req) + " | " + lb.route(++req) + " | " + lb.route(++req));
        }
        pool.forEach(b -> System.out.println(b.name + " served " + b.served));
    }
}
''', ["Retry a failed request once on the next healthy backend so users never see the failure.",
      "Add 'connection draining': when a backend is marked for removal, let in-flight requests finish but send no new ones.",
      "Add an active–standby pair of load balancers sharing a virtual IP, and fail over when the active one dies."])

J("lb-algorithms", r'''
import java.util.*;
import java.util.function.*;

public class LbAlgorithmsDemo {
    record Server(String name, int weight) {}
    static final List<Server> servers = List.of(new Server("A", 1), new Server("B", 1), new Server("C", 2));

    static int rr = 0;
    static Server roundRobin(String user) { return servers.get(rr++ % servers.size()); }

    static int wIdx = 0; static final List<Server> weighted = new ArrayList<>();
    static { for (Server s : servers) for (int i = 0; i < s.weight(); i++) weighted.add(s); }
    static Server weightedRoundRobin(String user) { return weighted.get(wIdx++ % weighted.size()); }

    static final Map<String, Integer> active = new HashMap<>();
    static int tie = 0;
    static Server leastConnections(String user) {
        int min = servers.stream().mapToInt(s -> active.getOrDefault(s.name(), 0)).min().getAsInt();
        List<Server> least = servers.stream().filter(s -> active.getOrDefault(s.name(), 0) == min).toList();
        return least.get(tie++ % least.size());                              // rotate among equally idle servers
    }

    static Server ipHash(String user) { return servers.get(Math.floorMod(user.hashCode(), servers.size())); }

    static final Random rnd = new Random(3);
    static Server powerOfTwo(String user) {
        Server a = servers.get(rnd.nextInt(3)), b = servers.get(rnd.nextInt(3));
        return active.getOrDefault(a.name(), 0) <= active.getOrDefault(b.name(), 0) ? a : b;
    }

    public static void main(String[] args) {
        String[] users = {"u1", "u2", "u3", "u1", "u4", "u5", "u2", "u6"};
        boolean[] slow = {false, false, false, true, false, false, false, false};   // request 4 is a long upload
        Map<String, Function<String, Server>> algos = new LinkedHashMap<>();
        algos.put("round robin      ", LbAlgorithmsDemo::roundRobin);
        algos.put("weighted RR      ", LbAlgorithmsDemo::weightedRoundRobin);
        algos.put("least connections", LbAlgorithmsDemo::leastConnections);
        algos.put("IP/user hash     ", LbAlgorithmsDemo::ipHash);
        algos.put("power of two     ", LbAlgorithmsDemo::powerOfTwo);
        for (var e : algos.entrySet()) {
            active.clear(); tie = 0; StringBuilder sb = new StringBuilder();
            for (int i = 0; i < users.length; i++) {
                Server s = e.getValue().apply(users[i]);
                sb.append(users[i]).append("→").append(s.name()).append("  ");
                if (slow[i]) active.merge(s.name(), 5, Integer::sum);            // long request keeps 5 connections busy
            }
            System.out.println(e.getKey() + ": " + sb);
        }
        System.out.println("IP hash always sends u1 and u2 to the same server (sticky); least connections avoids the server busy with the upload.");
    }
}
''', ["Add 'least response time': keep a moving average of each server's latency and pick the fastest.",
      "Implement smooth weighted round robin (Nginx's algorithm) so C's two turns are not back-to-back.",
      "Show the downside of `hash % N`: add server D and count how many of 1,000 users change server."])

J("cdn", r'''
import java.util.*;

public class CdnDemo {
    record Cached(String body, long expiresAt) {}

    static class Origin { int hits; String get(String path) { hits++; return "content of " + path; } }

    static class Edge {
        final String city; final int rttMs; final Origin origin; final Map<String, Cached> cache = new HashMap<>();
        Edge(String city, int rttMs, Origin origin) { this.city = city; this.rttMs = rttMs; this.origin = origin; }
        String get(String path, long now, int maxAge) {
            Cached c = cache.get(path);
            if (c != null && c.expiresAt() > now) return String.format("%-8s HIT  %-22s %3d ms", city, path, rttMs);
            String body = origin.get(path);
            cache.put(path, new Cached(body, now + maxAge));
            return String.format("%-8s MISS %-22s %3d ms (went to origin in Virginia)", city, path, rttMs + 200);
        }
    }

    public static void main(String[] args) {
        Origin origin = new Origin();
        Edge mumbai = new Edge("Mumbai", 8, origin), london = new Edge("London", 10, origin);
        System.out.println(mumbai.get("/img/cat.jpg", 0, 86_400));
        System.out.println(mumbai.get("/img/cat.jpg", 5, 86_400));
        System.out.println(london.get("/img/cat.jpg", 6, 86_400));
        System.out.println(mumbai.get("/app.3f9c.js", 7, 31_536_000));
        System.out.println("-- deploy: new bundle gets a new versioned name, no purge needed --");
        System.out.println(mumbai.get("/app.8d21.js", 100, 31_536_000));
        System.out.println(mumbai.get("/api/price", 101, 0) + "  <- dynamic, max-age 0");
        System.out.println(mumbai.get("/img/cat.jpg", 90_000, 86_400) + "  <- next day, expired");
        System.out.println("origin served " + origin.hits + " of 8 requests");
    }
}
''', ["Add `stale-while-revalidate`: serve the expired copy instantly and refresh it in the background.",
      "Add a regional 'shield' cache between edges and origin so London and Mumbai misses share one origin fetch.",
      "Add a `purge(path)` API and compare it with the versioned-filename approach."])

J("caching", r'''
import java.util.*;

public class CachingDemo {
    static int dbReads = 0;
    static String slowDb(String key) { dbReads++; return "value-of-" + key; }        // pretend 10 ms

    public static void main(String[] args) {
        Map<String, String> cache = new HashMap<>();
        Random r = new Random(5);
        int requests = 10_000, hits = 0;
        // Zipf-like popularity: a few keys are very popular
        for (int i = 0; i < requests; i++) {
            int k = (int) Math.floor(Math.pow(r.nextDouble(), 3) * 1000);
            String key = "product:" + k;
            String v = cache.get(key);
            if (v != null) hits++;
            else cache.put(key, slowDb(key));
        }
        double hitRatio = hits / (double) requests;
        double avgMs = hitRatio * 0.5 + (1 - hitRatio) * 10;
        System.out.printf("requests %,d  cache hits %,d  hit ratio %.1f%%  db reads %,d%n", requests, hits, hitRatio * 100, dbReads);
        System.out.printf("average latency %.2f ms (vs 10 ms with no cache)%n", avgMs);
        System.out.printf("cache holds %d keys; most traffic goes to a few hot keys%n", cache.size());
    }
}
''', ["Limit the cache to 100 keys with LRU eviction (`LinkedHashMap` with `removeEldestEntry`) and see the hit ratio change.",
      "Add a TTL per entry and expire entries after 500 simulated requests.",
      "Make popularity uniform (`r.nextInt(1000)`) and explain why the hit ratio drops."])

J("cache-strategies", r'''
import java.util.*;

public class CacheStrategiesDemo {
    static final Map<String, Integer> db = new HashMap<>(Map.of("stock:ps5", 10));
    static final Map<String, Integer> cache = new HashMap<>();
    static final List<String> log = new ArrayList<>();

    // Cache-aside: app reads cache, loads from DB on miss; on write, update DB then DELETE the key
    static int readAside(String k) {
        Integer v = cache.get(k);
        if (v != null) { log.add("aside read " + k + " HIT " + v); return v; }
        v = db.get(k); cache.put(k, v); log.add("aside read " + k + " MISS -> DB " + v); return v;
    }
    static void writeAside(String k, int v) { db.put(k, v); cache.remove(k); log.add("aside write " + k + "=" + v + " -> DB, delete cache key"); }

    // Write-through: write cache and DB together
    static void writeThrough(String k, int v) { cache.put(k, v); db.put(k, v); log.add("write-through " + k + "=" + v + " -> cache + DB"); }

    // Write-behind: write cache now, flush to DB later in a batch
    static final Map<String, Integer> dirty = new LinkedHashMap<>();
    static void writeBehind(String k, int v) { cache.put(k, v); dirty.put(k, v); log.add("write-behind " + k + "=" + v + " -> cache only (DB=" + db.get(k) + ")"); }
    static void flush() { db.putAll(dirty); log.add("flush " + dirty.size() + " dirty keys -> DB=" + db); dirty.clear(); }

    public static void main(String[] args) {
        readAside("stock:ps5"); readAside("stock:ps5");
        writeAside("stock:ps5", 9); readAside("stock:ps5");
        writeThrough("stock:ps5", 8); readAside("stock:ps5");
        writeBehind("stock:ps5", 7); writeBehind("stock:ps5", 6); writeBehind("stock:xbox", 4);
        flush();
        log.forEach(System.out::println);
    }
}
''', ["Simulate the cache-aside race: reader A misses and reads 9 from DB, writer sets 8 and deletes the key, then A writes 9 into the cache. How do short TTLs limit the damage?",
      "Make write-behind lose data: 'crash' before `flush()` and show the DB is behind.",
      "Implement read-through: a `LoadingCache` class that takes a loader function and hides the DB from the caller."])

J("cache-eviction", r'''
import java.util.*;

public class CacheEvictionDemo {
    interface Cache { boolean access(String key); String contents(); }

    static class Lru implements Cache {
        final LinkedHashMap<String, Boolean> map; Lru(int cap) { map = new LinkedHashMap<>(16, 0.75f, true) { protected boolean removeEldestEntry(Map.Entry<String, Boolean> e) { return size() > cap; } }; }
        public boolean access(String k) { boolean hit = map.containsKey(k); map.put(k, true); return hit; }
        public String contents() { return map.keySet().toString(); }
    }

    static class Fifo implements Cache {
        final int cap; final Deque<String> q = new ArrayDeque<>(); Fifo(int cap) { this.cap = cap; }
        public boolean access(String k) { if (q.contains(k)) return true; if (q.size() == cap) q.pollFirst(); q.addLast(k); return false; }
        public String contents() { return q.toString(); }
    }

    static class Lfu implements Cache {
        final int cap; final Map<String, Integer> freq = new LinkedHashMap<>(); Lfu(int cap) { this.cap = cap; }
        public boolean access(String k) {
            if (freq.containsKey(k)) { freq.merge(k, 1, Integer::sum); return true; }
            if (freq.size() == cap) { String victim = Collections.min(freq.entrySet(), Map.Entry.comparingByValue()).getKey(); freq.remove(victim); }
            freq.put(k, 1); return false;
        }
        public String contents() { return freq.toString(); }
    }

    public static void main(String[] args) {
        String[] seq = "A B C A D B A E A B".split(" ");
        for (Cache c : List.of(new Lru(3), new Fifo(3), new Lfu(3))) {
            int hits = 0; StringBuilder trace = new StringBuilder();
            for (String k : seq) { boolean h = c.access(k); if (h) hits++; trace.append(k).append(h ? "✓ " : "· "); }
            System.out.printf("%-4s %s hits=%d final=%s%n", c.getClass().getSimpleName().toUpperCase(), trace, hits, c.contents());
        }
    }
}
''', ["Implement an O(1) LFU (frequency buckets + doubly linked lists), like LeetCode 460.",
      "Find an access sequence where FIFO beats LRU.",
      "Add a TTL to the LRU so entries older than 5 accesses are treated as misses."])

J("cache-problems", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class CacheProblemsDemo {
    static final AtomicInteger dbQueries = new AtomicInteger();
    static String db(String k) { dbQueries.incrementAndGet(); sleep(50); return "v:" + k; }
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException ignored) {} }

    // Stampede: 100 threads miss the same expired key at once
    static void stampede(boolean singleFlight) throws Exception {
        dbQueries.set(0);
        Map<String, String> cache = new ConcurrentHashMap<>();
        Map<String, CompletableFuture<String>> inFlight = new ConcurrentHashMap<>();
        ExecutorService pool = Executors.newFixedThreadPool(100);
        CountDownLatch go = new CountDownLatch(1);
        List<Future<String>> fs = new ArrayList<>();
        for (int i = 0; i < 100; i++) fs.add(pool.submit(() -> {
            go.await();
            String v = cache.get("hot");
            if (v != null) return v;
            if (!singleFlight) { v = db("hot"); cache.put("hot", v); return v; }
            CompletableFuture<String> f = inFlight.computeIfAbsent("hot", k -> CompletableFuture.supplyAsync(() -> db(k)));   // one loader, others wait on it
            v = f.get(); cache.put("hot", v); return v;
        }));
        go.countDown();
        for (Future<String> f : fs) f.get();
        pool.shutdown();
        System.out.println((singleFlight ? "with single-flight   " : "no protection        ") + ": 100 concurrent misses -> " + dbQueries.get() + " DB queries");
    }

    public static void main(String[] args) throws Exception {
        stampede(false);
        stampede(true);
        // Penetration: requests for ids that don't exist always miss; cache the 'not found'
        dbQueries.set(0);
        Map<String, Optional<String>> cache = new HashMap<>();
        for (int i = 0; i < 1000; i++) {
            String key = "user:-1";
            if (!cache.containsKey(key)) { dbQueries.incrementAndGet(); cache.put(key, Optional.empty()); }
        }
        System.out.println("penetration fix      : 1000 lookups of a missing id -> " + dbQueries.get() + " DB query (negative caching)");
        // Avalanche: jitter TTLs so keys don't expire together
        Random r = new Random(1); Map<Integer, Integer> expiresPerMinute = new TreeMap<>();
        for (int i = 0; i < 10_000; i++) expiresPerMinute.merge(60 + r.nextInt(10), 1, Integer::sum);
        System.out.println("avalanche fix        : TTL 60 min + random 0-9 min -> expiries per minute " + expiresPerMinute.values());
    }
}
''', ["Add the hot-key fix: replicate `hot` as `hot#0..hot#9` and pick a random copy per read.",
      "Add 'refresh ahead': when a key is within 10% of its TTL, refresh it in the background on the next read.",
      "Replace the negative cache with a Bloom filter of valid user ids."])

J("redis-memcached", r'''
import java.util.*;

public class MiniRedisDemo {
    // A tiny in-memory Redis: strings with TTL, INCR, lists, sorted sets. Single-threaded command loop = atomic commands.
    final Map<String, Object> data = new HashMap<>();
    final Map<String, Long> expiry = new HashMap<>();
    long now = 0;

    Object get(String k) { if (expiry.containsKey(k) && expiry.get(k) <= now) { data.remove(k); expiry.remove(k); } return data.get(k); }
    String set(String k, String v, Long exSeconds, boolean nx) {
        if (nx && get(k) != null) return "nil";
        data.put(k, v); if (exSeconds != null) expiry.put(k, now + exSeconds * 1000); else expiry.remove(k); return "OK";
    }
    long incr(String k) { long v = Long.parseLong((String) Optional.ofNullable(get(k)).orElse("0")) + 1; data.put(k, String.valueOf(v)); return v; }
    @SuppressWarnings("unchecked") long lpush(String k, String v) { Deque<String> d = (Deque<String>) data.computeIfAbsent(k, x -> new ArrayDeque<>()); d.addFirst(v); return d.size(); }
    @SuppressWarnings("unchecked") List<String> lrange(String k, int a, int b) { List<String> l = new ArrayList<>((Deque<String>) data.getOrDefault(k, new ArrayDeque<>())); return l.subList(a, Math.min(b + 1, l.size())); }
    @SuppressWarnings("unchecked") double zincrby(String k, double by, String m) { Map<String, Double> z = (Map<String, Double>) data.computeIfAbsent(k, x -> new HashMap<>()); return z.merge(m, by, Double::sum); }
    @SuppressWarnings("unchecked") List<String> zrevrange(String k, int n) {
        Map<String, Double> z = (Map<String, Double>) data.get(k);
        return z.entrySet().stream().sorted(Map.Entry.<String, Double>comparingByValue().reversed()).limit(n).map(e -> e.getKey() + "=" + e.getValue().intValue()).toList();
    }

    public static void main(String[] args) {
        MiniRedisDemo r = new MiniRedisDemo();
        System.out.println("SET session:abc asha EX 60 -> " + r.set("session:abc", "asha", 60L, false));
        System.out.println("INCR views:post:9 x3       -> " + r.incr("views:post:9") + "," + r.incr("views:post:9") + "," + r.incr("views:post:9"));
        System.out.println("SET lock:order NX EX 5     -> " + r.set("lock:order", "worker-1", 5L, true));
        System.out.println("SET lock:order NX EX 5     -> " + r.set("lock:order", "worker-2", 5L, true) + " (already locked)");
        for (String p : List.of("p1", "p2", "p3")) r.lpush("feed:42", p);
        System.out.println("LRANGE feed:42 0 1         -> " + r.lrange("feed:42", 0, 1));
        r.zincrby("lb", 50, "asha"); r.zincrby("lb", 80, "ravi"); r.zincrby("lb", 40, "asha");
        System.out.println("ZREVRANGE lb 0 1           -> " + r.zrevrange("lb", 2));
        r.now += 61_000;
        System.out.println("61 s later GET session:abc -> " + r.get("session:abc") + " (expired)");
        System.out.println("            GET lock:order -> " + r.get("lock:order") + " (lock auto-released)");
    }
}
''', ["Add `HSET/HGET` for hashes and `SADD/SISMEMBER` for sets.",
      "Add an append-only file: log every write command to a list and rebuild the data by replaying it (AOF persistence).",
      "Add `ZREVRANK` returning a member's 0-based rank."])

J("message-queues", r'''
import java.util.*;

public class MessageQueueDemo {
    // An SQS-style queue: receive hides the message for a visibility timeout; ACK deletes it; un-acked messages reappear;
    // after maxReceives the message goes to a dead-letter queue.
    record Msg(String id, String body) {}
    static class Queue {
        final Deque<Msg> ready = new ArrayDeque<>(); final Map<String, Long> invisibleUntil = new HashMap<>(); final Map<String, Msg> inFlight = new HashMap<>();
        final Map<String, Integer> receives = new HashMap<>(); final List<Msg> dlq = new ArrayList<>(); final long visibility = 30; final int maxReceives = 3;
        void send(Msg m) { ready.addLast(m); }
        Optional<Msg> receive(long now) {
            inFlight.entrySet().removeIf(e -> { if (invisibleUntil.get(e.getKey()) <= now) { ready.addLast(e.getValue()); return true; } return false; });
            Msg m = ready.pollFirst(); if (m == null) return Optional.empty();
            int n = receives.merge(m.id(), 1, Integer::sum);
            if (n > maxReceives) { dlq.add(m); return receive(now); }
            inFlight.put(m.id(), m); invisibleUntil.put(m.id(), now + visibility); return Optional.of(m);
        }
        void ack(String id) { inFlight.remove(id); }
    }

    public static void main(String[] args) {
        Queue q = new Queue();
        q.send(new Msg("m1", "transcode video 7")); q.send(new Msg("m2", "send email 9")); q.send(new Msg("m3", "corrupt file"));
        long t = 0;
        for (int round = 0; round < 7; round++, t += 31) {
            Optional<Msg> m = q.receive(t);
            if (m.isEmpty()) { System.out.println("t=" + t + " queue empty, DLQ=" + q.dlq); continue; }
            Msg msg = m.get();
            boolean workerCrashes = msg.id().equals("m1") && round == 0;
            boolean poison = msg.id().equals("m3");
            if (workerCrashes) System.out.println("t=" + t + " worker took " + msg.id() + " and crashed (no ACK) -> will reappear after 30 s");
            else if (poison) System.out.println("t=" + t + " worker failed on " + msg.id() + " (receive #" + q.receives.get("m3") + ")");
            else { q.ack(msg.id()); System.out.println("t=" + t + " processed " + msg.id() + " '" + msg.body() + "' and ACKed"); }
        }
    }
}
''', ["Run 3 consumer threads on a `BlockingQueue` and show the work is spread across them.",
      "Add exponential backoff: a failed message becomes visible after 30 s, then 60 s, then 120 s.",
      "Add a FIFO group key so messages for the same order are never processed in parallel."])

J("kafka", r'''
import java.util.*;

public class MiniKafkaDemo {
    // A topic = N append-only partitions. Producers pick partition = hash(key) % N. Consumers in a group split partitions
    // and keep their own offsets; messages are NOT deleted when read, so another group can read them again.
    static class Topic {
        final List<List<String>> partitions = new ArrayList<>();
        Topic(int n) { for (int i = 0; i < n; i++) partitions.add(new ArrayList<>()); }
        int send(String key, String value) { int p = Math.floorMod(key.hashCode(), partitions.size()); partitions.get(p).add(key + ":" + value); return p; }
    }

    static class ConsumerGroup {
        final String name; final Map<Integer, Integer> committed = new HashMap<>();
        ConsumerGroup(String name) { this.name = name; }
        Map<String, List<Integer>> assign(int partitions, List<String> members) {
            Map<String, List<Integer>> a = new TreeMap<>();
            for (int p = 0; p < partitions; p++) a.computeIfAbsent(members.get(p % members.size()), k -> new ArrayList<>()).add(p);
            return a;
        }
        List<String> poll(Topic t, int partition, int max) {
            int from = committed.getOrDefault(partition, 0);
            List<String> log = t.partitions.get(partition);
            List<String> batch = log.subList(from, Math.min(log.size(), from + max));
            committed.put(partition, from + batch.size());                 // commit after processing -> at-least-once
            return batch;
        }
    }

    public static void main(String[] args) {
        Topic orders = new Topic(3);
        String[][] events = {{"asha", "created"}, {"meera", "created"}, {"asha", "paid"}, {"zoya", "created"}, {"asha", "shipped"}, {"meera", "paid"}};
        for (String[] e : events) System.out.println("produce " + e[0] + ":" + e[1] + " -> partition " + orders.send(e[0], e[1]));
        for (int p = 0; p < 3; p++) System.out.println("partition " + p + " = " + orders.partitions.get(p));
        ConsumerGroup billing = new ConsumerGroup("billing");
        System.out.println("\ngroup 'billing' with 2 consumers: " + billing.assign(3, List.of("c1", "c2")));
        for (int p = 0; p < 3; p++) System.out.println("  billing reads p" + p + " " + billing.poll(orders, p, 10));
        ConsumerGroup analytics = new ConsumerGroup("analytics");
        System.out.println("group 'analytics' reads the same p0 from offset 0: " + analytics.poll(orders, 0, 1) + " then " + analytics.poll(orders, 0, 1));
        System.out.println("asha's events stay in order because they share a key -> same partition.");
    }
}
''', ["Add a third consumer to 'billing' and a fourth: show the fourth gets no partition (max parallelism = partitions).",
      "Add retention: drop messages older than 3 'ticks' and make a consumer with an old offset jump to the earliest available.",
      "Add log compaction: keep only the latest value for each key."])

J("delivery-semantics", r'''
import java.util.*;

public class DeliverySemanticsDemo {
    // The consumer may crash after applying a message but before committing its offset -> the message is redelivered.
    record Msg(String id, String user, int amount) {}
    static final List<Msg> log = List.of(new Msg("m1", "asha", 500), new Msg("m2", "asha", 200), new Msg("m3", "ravi", 300));

    static Map<String, Integer> run(String mode) {
        Map<String, Integer> wallet = new TreeMap<>(Map.of("asha", 1000, "ravi", 1000));
        Set<String> processed = new HashSet<>();
        int offset = 0; boolean crashedOnce = false;
        while (offset < log.size()) {
            Msg m = log.get(offset);
            if (mode.equals("at-most-once")) offset++;                                 // commit BEFORE processing
            boolean crash = m.id().equals("m2") && !crashedOnce;
            if (mode.equals("at-most-once") && crash) { crashedOnce = true; continue; }  // crashed: m2 is lost
            if (mode.equals("exactly-once") && processed.contains(m.id())) { offset++; continue; }
            wallet.merge(m.user(), -m.amount(), Integer::sum);                         // the side effect (charge)
            if (mode.equals("exactly-once")) processed.add(m.id());                    // same transaction as the charge
            if (crash && !mode.equals("at-most-once")) { crashedOnce = true; continue; } // crash before committing -> redelivered
            if (!mode.equals("at-most-once")) offset++;                                // commit AFTER processing
        }
        return wallet;
    }

    public static void main(String[] args) {
        System.out.println("expected                : {asha=300, ravi=700}");
        for (String mode : List.of("at-most-once", "at-least-once", "exactly-once"))
            System.out.printf("%-24s: %s%n", mode, run(mode));
        System.out.println("at-most-once lost m2; at-least-once charged m2 twice; dedup by message id fixes it.");
    }
}
''', ["Store `processed` ids with a time limit (e.g. keep the last 10,000) and discuss what happens to very late duplicates.",
      "Make the producer side duplicate too: send m1 twice (lost ack) and check exactly-once still holds.",
      "Replace the `processed` set with a natural idempotency rule: `UPDATE ... WHERE last_msg_id < :id`."])

J("backpressure", r'''
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class BackpressureDemo {
    // Fast producer (1 item/ms) vs slow consumer (1 item / 3 ms) for 300 ms.
    static void run(String name, BlockingQueue<Integer> q, boolean dropWhenFull) throws Exception {
        AtomicInteger produced = new AtomicInteger(), dropped = new AtomicInteger(), consumed = new AtomicInteger(), maxQueue = new AtomicInteger();
        AtomicBoolean done = new AtomicBoolean();
        Thread consumer = new Thread(() -> {
            while (!done.get() || !q.isEmpty()) {
                try { if (q.poll(10, TimeUnit.MILLISECONDS) != null) { consumed.incrementAndGet(); Thread.sleep(3); } } catch (InterruptedException e) { return; }
            }
        });
        consumer.start();
        long end = System.currentTimeMillis() + 300;
        while (System.currentTimeMillis() < end) {
            int item = produced.incrementAndGet();
            if (dropWhenFull) { if (!q.offer(item)) dropped.incrementAndGet(); }
            else q.put(item);                                              // blocks when full: producer slows down
            maxQueue.accumulateAndGet(q.size(), Math::max);
            Thread.sleep(1);
        }
        done.set(true); consumer.join();
        System.out.printf("%-26s produced %4s  dropped %4s  max queue %5s%n", name, bucket(produced.get()), bucket(dropped.get()), bucket(maxQueue.get()));
    }
    static String bucket(int n) { return n < 20 ? String.valueOf(n) : "~" + (n / 10 * 10); }

    public static void main(String[] args) throws Exception {
        run("unbounded queue", new LinkedBlockingQueue<>(), false);
        run("bounded(20), block", new ArrayBlockingQueue<>(20), false);
        run("bounded(20), drop/shed", new ArrayBlockingQueue<>(20), true);
        System.out.println("Unbounded: the backlog (and memory, and latency) keeps growing.");
        System.out.println("Blocking: the producer is slowed to the consumer's pace. Dropping: the queue stays small, extra work is shed.");
    }
}
''', ["Add a second consumer thread and see how the bounded-block producer speeds up.",
      "Instead of dropping the newest item, drop the oldest (useful for live sensor data).",
      "Measure each item's wait time in the queue and print p99 for the unbounded case."])

J("stream-batch", r'''
import java.util.*;

public class StreamWindowsDemo {
    record Click(String page, long tsSec) {}

    public static void main(String[] args) {
        List<Click> clicks = List.of(new Click("home", 2), new Click("cart", 15), new Click("home", 59), new Click("home", 61),
            new Click("cart", 70), new Click("home", 125), new Click("home", 45));          // last one arrives late (event time 45)
        // Batch: one job over the complete data
        Map<String, Long> batch = new TreeMap<>();
        for (Click c : clicks) batch.merge(c.page(), 1L, Long::sum);
        System.out.println("batch (all data, run once)   : " + batch);
        // Stream: tumbling 60 s windows by event time, emitted when the watermark passes the window end
        Map<Long, Map<String, Long>> windows = new TreeMap<>();
        long watermark = 0, allowedLateness = 10;
        for (Click c : clicks) {
            long w = c.tsSec() / 60 * 60;
            if (w + 60 + allowedLateness <= watermark) { System.out.println("  late event dropped: " + c); continue; }
            windows.computeIfAbsent(w, k -> new TreeMap<>()).merge(c.page(), 1L, Long::sum);
            watermark = Math.max(watermark, c.tsSec());
            for (Iterator<Map.Entry<Long, Map<String, Long>>> it = windows.entrySet().iterator(); it.hasNext(); ) {
                var e = it.next();
                if (e.getKey() + 60 + allowedLateness <= watermark) { System.out.println("stream window [" + e.getKey() + "," + (e.getKey() + 60) + ") : " + e.getValue()); it.remove(); }
            }
        }
        windows.forEach((w, v) -> System.out.println("stream window [" + w + "," + (w + 60) + ") : " + v + " (flushed at end)"));
    }
}
''', ["Increase `allowedLateness` to 90 s and see the late click get counted.",
      "Implement a sliding window of 60 s that slides every 30 s.",
      "Implement session windows: a user's session ends after 30 s with no clicks."])

J("scheduler-cron", r'''
import java.util.*;

public class SchedulerDemo {
    // Jobs table + leases: several scheduler nodes poll; each job is claimed by exactly one node; an expired lease is re-claimed.
    static class Job { final String id; long nextRun; final long every; String owner; long leaseUntil; int runs; Job(String id, long nextRun, long every) { this.id = id; this.nextRun = nextRun; this.every = every; } }
    static final List<Job> jobs = new ArrayList<>(List.of(new Job("daily-report", 0, 60), new Job("cleanup", 10, 30), new Job("invoice", 20, 60)));

    static synchronized List<Job> claimDue(String node, long now) {       // like SELECT ... FOR UPDATE SKIP LOCKED
        List<Job> claimed = new ArrayList<>();
        for (Job j : jobs) if (j.nextRun <= now && (j.owner == null || j.leaseUntil <= now)) { j.owner = node; j.leaseUntil = now + 15; claimed.add(j); }
        return claimed;
    }
    static synchronized void complete(Job j, long now) { j.runs++; j.owner = null; j.nextRun = now + j.every; }

    static boolean invoiceCrashed = false;

    public static void main(String[] args) {
        for (long now = 0; now <= 90; now += 10) {
            List<String> nodes = (now / 10) % 2 == 0 ? List.of("node-A", "node-B") : List.of("node-B", "node-A");   // nodes poll in varying order
            for (String node : nodes) {
                for (Job j : claimDue(node, now)) {
                    boolean crash = j.id.equals("invoice") && !invoiceCrashed;
                    if (crash) { invoiceCrashed = true; System.out.printf("t=%2d %s claimed %-12s and CRASHED (lease until t=%d)%n", now, node, j.id, j.leaseUntil); continue; }
                    complete(j, now);
                    System.out.printf("t=%2d %s ran %-12s next at t=%d%n", now, node, j.id, j.nextRun);
                }
            }
        }
        jobs.forEach(j -> System.out.println(j.id + " ran " + j.runs + " times"));
    }
}
''', ["Parse a simple cron expression like `*/15 * * * *` to compute `nextRun` instead of a fixed `every`.",
      "Add max attempts: after 3 crashed leases mark the job FAILED and alert.",
      "Run node-A and node-B as real threads with `ScheduledExecutorService` and keep `claimDue` safe."])

J("storage-types", r'''
import java.security.*;
import java.util.*;

public class ObjectStoreDemo {
    // Object storage: flat key -> bytes + metadata, whole-object PUT/GET, multipart upload, pre-signed URLs.
    record Obj(byte[] data, Map<String, String> meta) {}
    static final Map<String, Obj> bucket = new TreeMap<>();
    static final Map<String, List<byte[]>> multipart = new HashMap<>();
    static final String SECRET = "server-secret";

    static String presign(String key, long expiresAt) throws Exception {
        String sig = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest((key + expiresAt + SECRET).getBytes())).substring(0, 16);
        return "/" + key + "?expires=" + expiresAt + "&sig=" + sig;
    }
    static boolean verify(String key, long expiresAt, String sig, long now) throws Exception {
        return now < expiresAt && presign(key, expiresAt).endsWith("sig=" + sig);
    }

    public static void main(String[] args) throws Exception {
        String url = presign("videos/7/raw.mp4", 900);
        System.out.println("API hands the client a pre-signed URL: " + url);
        String sig = url.substring(url.indexOf("sig=") + 4);
        System.out.println("client PUT at t=100 allowed? " + verify("videos/7/raw.mp4", 900, sig, 100));
        System.out.println("client PUT at t=1000 allowed? " + verify("videos/7/raw.mp4", 900, sig, 1000) + " (expired)");
        multipart.put("up-1", new ArrayList<>());
        for (int part = 1; part <= 3; part++) multipart.get("up-1").add(new byte[5 * 1024 * 1024]);   // 3 x 5 MB parts, uploaded in parallel in real life
        int size = multipart.get("up-1").stream().mapToInt(b -> b.length).sum();
        bucket.put("videos/7/raw.mp4", new Obj(new byte[size], Map.of("content-type", "video/mp4", "owner", "user-42")));
        System.out.println("multipart complete -> object size " + size / (1024 * 1024) + " MB, metadata " + bucket.get("videos/7/raw.mp4").meta());
        bucket.put("videos/7/thumb.jpg", new Obj(new byte[40_000], Map.of("content-type", "image/jpeg")));
        System.out.println("LIST prefix videos/7/ -> " + bucket.keySet().stream().filter(k -> k.startsWith("videos/7/")).toList());
        System.out.println("Keys look like paths, but the namespace is flat: there are no real folders.");
    }
}
''', ["Add lifecycle rules: move objects not read for 30 'days' to an ARCHIVE tier and print the monthly cost saving.",
      "Add content-addressed dedup: store bytes under their SHA-256 and point several keys at the same blob.",
      "Add object versioning: keep old versions on overwrite and support GET with a version id."])

J("search-engines", r'''
import java.util.*;

public class InvertedIndexDemo {
    static final Map<String, Map<Integer, Integer>> index = new TreeMap<>();      // term -> (doc -> term frequency)
    static final Map<Integer, String> docs = new TreeMap<>();
    static final Map<Integer, Integer> docLen = new HashMap<>();

    static List<String> analyze(String text) {
        List<String> out = new ArrayList<>();
        for (String w : text.toLowerCase().split("\\W+")) {
            if (w.isBlank() || Set.of("the", "a", "and").contains(w)) continue;
            out.add(w.replaceAll("(ning|ing|s)$", ""));                         // toy stemmer: running -> run, shoes -> shoe
        }
        return out;
    }

    static void add(int id, String text) {
        docs.put(id, text); List<String> terms = analyze(text); docLen.put(id, terms.size());
        for (String t : terms) index.computeIfAbsent(t, k -> new TreeMap<>()).merge(id, 1, Integer::sum);
    }

    static List<String> search(String q) {                                   // BM25 ranking, OR semantics
        double avgLen = docLen.values().stream().mapToInt(i -> i).average().orElse(1), k1 = 1.2, b = 0.75; int n = docs.size();
        Map<Integer, Double> score = new HashMap<>();
        for (String t : analyze(q)) {
            Map<Integer, Integer> postings = index.getOrDefault(t, Map.of());
            double idf = Math.log(1 + (n - postings.size() + 0.5) / (postings.size() + 0.5));
            postings.forEach((doc, tf) -> score.merge(doc, idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * docLen.get(doc) / avgLen)), Double::sum));
        }
        return score.entrySet().stream().sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
            .map(e -> String.format("doc%d(%.2f) %s", e.getKey(), e.getValue(), docs.get(e.getKey()))).toList();
    }

    public static void main(String[] args) {
        add(1, "Red running shoes"); add(2, "Blue running jacket"); add(3, "Red jacket"); add(4, "Shoes and socks bundle");
        System.out.println("inverted index:"); index.forEach((t, p) -> System.out.println("  " + t + " -> " + p.keySet()));
        System.out.println("search 'red shoes':"); search("red shoes").forEach(r -> System.out.println("  " + r));
        System.out.println("search 'jackets':"); search("jackets").forEach(r -> System.out.println("  " + r));
    }
}
''', ["Add AND semantics: only return documents containing every query term (intersect posting lists).",
      "Add a popularity boost: final score = BM25 × log(1 + sales).",
      "Support prefix search (`sho*`) using the sorted `TreeMap` of terms with `subMap`."])

J("timeseries-analytics", r'''
import java.util.*;

public class ColumnStoreDemo {
    // Same 1,000,000 orders stored row-wise and column-wise; an analytics query only needs 2 columns.
    record Order(long id, int customerId, String city, String product, int qty, int priceRs, int year, String status) {}

    public static void main(String[] args) {
        int n = 1_000_000; Random r = new Random(9);
        String[] cities = {"Pune", "Delhi", "Chennai", "Mumbai"};
        Order[] rows = new Order[n];
        int[] priceCol = new int[n]; short[] yearCol = new short[n];
        for (int i = 0; i < n; i++) {
            Order o = new Order(i, r.nextInt(100_000), cities[r.nextInt(4)], "sku-" + r.nextInt(5000), 1 + r.nextInt(3), 100 + r.nextInt(5000), 2023 + r.nextInt(3), "PAID");
            rows[i] = o; priceCol[i] = o.priceRs(); yearCol[i] = (short) o.year();
        }
        long t = System.nanoTime(); long s1 = 0, c1 = 0;
        for (Order o : rows) if (o.year() == 2025) { s1 += o.priceRs(); c1++; }
        double rowMs = (System.nanoTime() - t) / 1e6;
        t = System.nanoTime(); long s2 = 0, c2 = 0;
        for (int i = 0; i < n; i++) if (yearCol[i] == 2025) { s2 += priceCol[i]; c2++; }
        double colMs = (System.nanoTime() - t) / 1e6;
        System.out.printf("AVG(price) WHERE year=2025 -> row store %.1f (scanned whole records), column store %.1f%n", s1 / (double) c1, s2 / (double) c2);
        System.out.printf("columns touched: row store all 8, column store 2 (%d bytes per row instead of ~80)%n", 4 + 2);
        System.out.println("column store was " + (colMs < rowMs ? "faster" : "not faster this run") + " (timings vary; the I/O saving on disk is the big win)");
        // Rollup / downsampling: 1-second CPU samples -> 1-minute averages
        double[] perSecond = new double[3600]; for (int i = 0; i < 3600; i++) perSecond[i] = 40 + 20 * Math.sin(i / 600.0) + r.nextInt(5);
        double[] perMinute = new double[60];
        for (int m = 0; m < 60; m++) { double sum = 0; for (int s = 0; s < 60; s++) sum += perSecond[m * 60 + s]; perMinute[m] = sum / 60; }
        System.out.printf("downsampling: 3600 points -> 60 points; minute 0 avg %.1f%%, minute 30 avg %.1f%%%n", perMinute[0], perMinute[30]);
        // Delta encoding of timestamps
        long[] ts = {1764140000, 1764140010, 1764140020, 1764140031};
        List<Long> deltas = new ArrayList<>(); for (int i = 1; i < ts.length; i++) deltas.add(ts[i] - ts[i - 1]);
        System.out.println("delta encoding: " + Arrays.toString(ts) + " -> first " + ts[0] + " + deltas " + deltas + " (tiny numbers compress well)");
    }
}
''', ["Add run-length encoding to the `city` column after sorting by city, and print the compressed size.",
      "Partition the data by year (one array per year) so the query skips the other years entirely.",
      "Add a 1-hour rollup computed from the 1-minute rollup and keep max as well as average."])
