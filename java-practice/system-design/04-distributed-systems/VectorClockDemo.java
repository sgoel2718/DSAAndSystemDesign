import java.util.*;

public class VectorClockDemo {
    record VC(Map<String, Integer> c) {
        VC tick(String node) { Map<String, Integer> m = new TreeMap<>(c); m.merge(node, 1, Integer::sum); return new VC(m); }
        VC merge(VC o) { Map<String, Integer> m = new TreeMap<>(c); o.c.forEach((k, v) -> m.merge(k, v, Math::max)); return new VC(m); }
        String compare(VC o) {
            boolean le = true, ge = true;
            Set<String> keys = new TreeSet<>(c.keySet()); keys.addAll(o.c.keySet());
            for (String k : keys) { int a = c.getOrDefault(k, 0), b = o.c.getOrDefault(k, 0); if (a > b) le = false; if (a < b) ge = false; }
            return le && ge ? "equal" : le ? "happened-before" : ge ? "happened-after" : "CONCURRENT (conflict)";
        }
        public String toString() { return c.toString(); }
    }
    record Cart(Set<String> items, VC clock) {}

    public static void main(String[] args) {
        Cart start = new Cart(Set.of("milk"), new VC(new TreeMap<>()).tick("A"));
        Cart onA = new Cart(new TreeSet<>(Set.of("milk", "eggs")), start.clock().tick("A"));        // Asha on replica A
        Cart onB = new Cart(new TreeSet<>(Set.of("milk", "bread")), start.clock().tick("B"));       // Ravi on replica B, during a partition
        System.out.println("start " + start.clock() + "  A " + onA.clock() + " " + onA.items() + "  B " + onB.clock() + " " + onB.items());
        System.out.println("start vs A: " + start.clock().compare(onA.clock()));
        System.out.println("A vs B   : " + onA.clock().compare(onB.clock()));
        Set<String> merged = new TreeSet<>(onA.items()); merged.addAll(onB.items());
        Cart resolved = new Cart(merged, onA.clock().merge(onB.clock()).tick("A"));
        System.out.println("merge    : " + resolved.items() + " clock " + resolved.clock());
        System.out.println("resolved vs B: " + resolved.clock().compare(onB.clock()) + " -> B's version can be discarded");
    }
}
