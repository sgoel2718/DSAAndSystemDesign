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
