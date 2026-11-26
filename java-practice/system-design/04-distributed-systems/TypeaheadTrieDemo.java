import java.util.*;

public class TypeaheadTrieDemo {
    static class Node { final TreeMap<Character, Node> kids = new TreeMap<>(); long count; List<String> top = new ArrayList<>(); }
    final Node root = new Node(); final int K = 3;

    void add(String q, long count) {
        Node n = root;
        List<Node> path = new ArrayList<>(List.of(root));
        for (char c : q.toCharArray()) { n = n.kids.computeIfAbsent(c, x -> new Node()); path.add(n); }
        n.count += count;
        final long total = n.count;
        for (Node p : path) {                                                     // update cached top-K on the path
            p.top.remove(q); p.top.add(q);
            p.top.sort(Comparator.comparingLong((String s) -> -countOf(s)).thenComparing(s -> s));
            if (p.top.size() > K) p.top.remove(K);
        }
    }
    long countOf(String q) { Node n = root; for (char c : q.toCharArray()) { n = n.kids.get(c); if (n == null) return 0; } return n.count; }
    List<String> suggest(String prefix) {
        Node n = root;
        for (char c : prefix.toCharArray()) { n = n.kids.get(c); if (n == null) return List.of(); }
        return n.top;                                                             // cached: no subtree search
    }

    public static void main(String[] args) {
        TypeaheadTrieDemo t = new TypeaheadTrieDemo();
        Object[][] logs = {{"car", 500}, {"cart", 300}, {"cat", 900}, {"cat videos", 700}, {"catalog", 50}, {"dog", 400}, {"career", 250}};
        for (Object[] l : logs) t.add((String) l[0], (Integer) l[1]);
        for (String p : List.of("c", "ca", "car", "cat", "d", "x")) System.out.println("'" + p + "' -> " + t.suggest(p) + "  (" + p.length() + " node hops)");
        t.add("cart", 1000);                                                      // 'cart' trends
        System.out.println("after 'cart' trends: 'ca' -> " + t.suggest("ca"));
    }
}
