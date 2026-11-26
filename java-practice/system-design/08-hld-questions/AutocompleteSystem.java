import java.util.*;

public class AutocompleteSystem {
    // Offline: aggregate query logs -> build a trie with top-k per node -> publish snapshot. Online: prefix lookup + cache.
    static class Node { final Map<Character, Node> kids = new TreeMap<>(); List<Map.Entry<String, Long>> top = List.of(); }
    static Node build(Map<String, Long> counts, int k) {
        Node root = new Node();
        for (var e : counts.entrySet()) { Node n = root; for (char c : e.getKey().toCharArray()) n = n.kids.computeIfAbsent(c, x -> new Node()); }
        fill(root, "", counts, k); return root;
    }
    static List<Map.Entry<String, Long>> fill(Node n, String prefix, Map<String, Long> counts, int k) {
        List<Map.Entry<String, Long>> all = new ArrayList<>();
        if (counts.containsKey(prefix)) all.add(Map.entry(prefix, counts.get(prefix)));
        for (var e : n.kids.entrySet()) all.addAll(fill(e.getValue(), prefix + e.getKey(), counts, k));
        all.sort(Map.Entry.<String, Long>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey()));
        n.top = all.subList(0, Math.min(k, all.size())); return n.top;
    }
    static final Map<String, List<String>> prefixCache = new HashMap<>(); static int trieLookups = 0;
    static List<String> suggest(Node root, String prefix) {
        String p = prefix.toLowerCase().trim();
        if (prefixCache.containsKey(p)) return prefixCache.get(p);
        trieLookups++; Node n = root;
        for (char c : p.toCharArray()) { n = n.kids.get(c); if (n == null) return List.of(); }
        List<String> res = n.top.stream().map(Map.Entry::getKey).toList(); prefixCache.put(p, res); return res;
    }

    public static void main(String[] args) {
        String[] log = {"iphone 16", "iphone 16", "iphone 16 pro", "ipl score", "ipl score", "ipl score", "ipl schedule", "india vs australia", "iphone 16", "ikea", "ipl score"};
        Map<String, Long> counts = new TreeMap<>(); for (String q : log) counts.merge(q, 1L, Long::sum);
        System.out.println("weekly aggregation: " + counts);
        Node v1 = build(counts, 3);
        for (String p : List.of("i", "ip", "iph", "IPL ", "x")) System.out.println("'" + p + "' -> " + suggest(v1, p));
        suggest(v1, "ip"); System.out.println("trie lookups: " + trieLookups + " (repeats served from the prefix cache / CDN)");
        for (int i = 0; i < 6; i++) counts.merge("iphone 17 launch", 1L, Long::sum);           // hourly delta for a trending query
        Node v2 = build(counts, 3); prefixCache.clear();
        System.out.println("after the hourly rebuild, 'iph' -> " + suggest(v2, "iph"));
    }
}
