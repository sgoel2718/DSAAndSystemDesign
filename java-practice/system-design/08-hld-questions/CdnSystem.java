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
