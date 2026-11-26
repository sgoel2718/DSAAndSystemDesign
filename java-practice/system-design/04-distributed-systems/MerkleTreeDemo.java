import java.security.MessageDigest;
import java.util.*;

public class MerkleTreeDemo {
    static String h(String s) { try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getBytes())).substring(0, 8); } catch (Exception e) { throw new RuntimeException(e); } }

    // Build a tree over 8 key ranges; level 0 = leaves
    static List<List<String>> build(TreeMap<String, String> data) {
        List<String> leaves = new ArrayList<>();
        for (int b = 0; b < 8; b++) { StringBuilder sb = new StringBuilder(); for (var e : data.entrySet()) if (Math.floorMod(e.getKey().hashCode(), 8) == b) sb.append(e); leaves.add(h(sb.toString())); }
        List<List<String>> levels = new ArrayList<>(List.of(leaves));
        while (levels.get(levels.size() - 1).size() > 1) {
            List<String> prev = levels.get(levels.size() - 1), up = new ArrayList<>();
            for (int i = 0; i < prev.size(); i += 2) up.add(h(prev.get(i) + prev.get(i + 1)));
            levels.add(up);
        }
        return levels;
    }

    static int comparisons = 0;
    static void diff(List<List<String>> a, List<List<String>> b, int level, int idx, List<Integer> out) {
        comparisons++;
        if (a.get(level).get(idx).equals(b.get(level).get(idx))) return;      // identical subtree: skip it entirely
        if (level == 0) { out.add(idx); return; }
        diff(a, b, level - 1, idx * 2, out); diff(a, b, level - 1, idx * 2 + 1, out);
    }

    public static void main(String[] args) {
        TreeMap<String, String> r1 = new TreeMap<>(), r2 = new TreeMap<>();
        for (int i = 0; i < 10_000; i++) { r1.put("k" + i, "v" + i); r2.put("k" + i, "v" + i); }
        r2.put("k4242", "STALE"); r2.remove("k777");
        List<List<String>> t1 = build(r1), t2 = build(r2);
        System.out.println("root hashes: " + t1.get(3).get(0) + " vs " + t2.get(3).get(0) + " -> " + (t1.get(3).get(0).equals(t2.get(3).get(0)) ? "in sync" : "differ"));
        List<Integer> bad = new ArrayList<>(); diff(t1, t2, 3, 0, bad);
        int keysToSync = 0; for (String k : r1.keySet()) if (bad.contains(Math.floorMod(k.hashCode(), 8))) keysToSync++;
        System.out.println("differing key ranges " + bad + " found with " + comparisons + " hash comparisons");
        System.out.println("only " + keysToSync + " of 10,000 keys need to be compared/streamed");
    }
}
