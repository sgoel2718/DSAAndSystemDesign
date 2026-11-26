import java.util.*;

public class KeyValueStoreSystem {
    // Dynamo-style: consistent hashing ring, replication to N=3 successors, quorum W=2/R=2, versioned values, read repair, hinted handoff.
    record Versioned(String value, long version) {}
    static class Node { final String name; boolean up = true; final Map<String, Versioned> data = new HashMap<>(); final List<String[]> hints = new ArrayList<>(); Node(String n) { name = n; } }
    static final TreeMap<Integer, Node> ring = new TreeMap<>();
    static final List<Node> nodes = new ArrayList<>();
    static final int N = 3, W = 2, R = 2;

    static int h(String s) { int x = s.hashCode(); x ^= x >>> 16; x *= 0x45d9f3b; return Math.floorMod(x ^ (x >>> 16), 1 << 16); }
    static List<Node> preferenceList(String key) {
        List<Node> out = new ArrayList<>(); Integer pos = ring.ceilingKey(h(key));
        Iterator<Node> it = (pos == null ? ring.values() : ring.tailMap(pos).values()).iterator();
        while (out.size() < N) { if (!it.hasNext()) it = ring.values().iterator(); Node n = it.next(); if (!out.contains(n)) out.add(n); }
        return out;
    }
    static String put(String key, String value, long version) {
        int acks = 0;
        for (Node n : preferenceList(key)) {
            if (n.up) { n.data.put(key, new Versioned(value, version)); acks++; }
            else { Node spare = nodes.stream().filter(x -> x.up && !preferenceList(key).contains(x)).findFirst().get(); spare.hints.add(new String[]{n.name, key, value, "" + version}); acks++; }
        }
        return acks >= W ? "OK (" + acks + " acks)" : "FAIL";
    }
    static String get(String key) {
        List<Node> replies = preferenceList(key).stream().filter(n -> n.up).limit(R).toList();
        if (replies.size() < R) return "FAIL (quorum not met)";
        Versioned best = replies.stream().map(n -> n.data.get(key)).filter(Objects::nonNull).max(Comparator.comparingLong(Versioned::version)).orElse(null);
        for (Node n : replies) if (best != null && !best.equals(n.data.get(key))) { n.data.put(key, best); System.out.println("    read repair: " + n.name + " updated"); }
        return best == null ? "null" : best.value() + " (v" + best.version() + ") from " + replies.stream().map(n -> n.name).toList();
    }

    public static void main(String[] args) {
        for (String n : List.of("A", "B", "C", "D", "E")) { Node node = new Node(n); nodes.add(node); for (int v = 0; v < 50; v++) ring.put(h(n + "#" + v), node); }
        System.out.println("preference list for 'cart:42': " + preferenceList("cart:42").stream().map(n -> n.name).toList());
        System.out.println("put cart:42=[shoes] v1 -> " + put("cart:42", "[shoes]", 1));
        Node second = preferenceList("cart:42").get(1); second.up = false;
        System.out.println(second.name + " goes down; put cart:42=[shoes,socks] v2 -> " + put("cart:42", "[shoes,socks]", 2) + " (hint stored on a spare node)");
        second.up = true;
        for (Node n : nodes) for (Iterator<String[]> it = n.hints.iterator(); it.hasNext(); ) { String[] hnt = it.next(); Node target = nodes.stream().filter(x -> x.name.equals(hnt[0])).findFirst().get(); target.data.put(hnt[1], new Versioned(hnt[2], Long.parseLong(hnt[3]))); it.remove(); System.out.println("hinted handoff: " + n.name + " -> " + hnt[0]); }
        preferenceList("cart:42").get(0).data.put("cart:42", new Versioned("[shoes]", 1));   // simulate one stale replica
        System.out.println("get cart:42 -> " + get("cart:42"));
    }
}
