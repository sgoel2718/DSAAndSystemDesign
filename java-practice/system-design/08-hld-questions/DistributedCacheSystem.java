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
