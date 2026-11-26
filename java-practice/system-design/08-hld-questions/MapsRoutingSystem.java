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
