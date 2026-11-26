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
