import java.util.*;

public class CrdtDemo {
    // PN-Counter: one increment and one decrement slot per replica; merge = max per slot.
    static class PNCounter {
        final String me; final Map<String, Integer> p = new TreeMap<>(), n = new TreeMap<>();
        PNCounter(String me) { this.me = me; }
        void inc(int k) { p.merge(me, k, Integer::sum); }
        void dec(int k) { n.merge(me, k, Integer::sum); }
        int value() { return p.values().stream().mapToInt(i -> i).sum() - n.values().stream().mapToInt(i -> i).sum(); }
        void merge(PNCounter o) { o.p.forEach((k, v) -> p.merge(k, v, Math::max)); o.n.forEach((k, v) -> n.merge(k, v, Math::max)); }
    }

    // OR-Set: each add gets a unique tag; remove deletes only the tags it has seen, so a concurrent add survives.
    static class ORSet {
        final Map<String, Set<String>> adds = new TreeMap<>(); final Set<String> removedTags = new TreeSet<>(); int seq = 0; final String me;
        ORSet(String me) { this.me = me; }
        void add(String x) { adds.computeIfAbsent(x, k -> new TreeSet<>()).add(me + (++seq)); }
        void remove(String x) { removedTags.addAll(adds.getOrDefault(x, Set.of())); }
        Set<String> value() { Set<String> v = new TreeSet<>(); adds.forEach((x, tags) -> { for (String t : tags) if (!removedTags.contains(t)) { v.add(x); break; } }); return v; }
        void merge(ORSet o) { o.adds.forEach((x, t) -> adds.computeIfAbsent(x, k -> new TreeSet<>()).addAll(t)); removedTags.addAll(o.removedTags); }
    }

    public static void main(String[] args) {
        PNCounter a = new PNCounter("A"), b = new PNCounter("B");
        a.inc(3); b.inc(2); b.dec(1);
        System.out.println("likes: A sees " + a.value() + ", B sees " + b.value());
        a.merge(b); b.merge(a); a.merge(b);                                    // duplicate merges are harmless
        System.out.println("after merging both ways (twice): A=" + a.value() + " B=" + b.value());
        ORSet cartA = new ORSet("A"), cartB = new ORSet("B");
        cartA.add("milk"); cartB.merge(cartA);
        cartA.remove("milk");                                                 // Asha removes milk...
        cartB.add("milk");                                                    // ...while Ravi adds milk again, concurrently
        cartB.add("bread");
        cartA.merge(cartB); cartB.merge(cartA);
        System.out.println("cart after concurrent remove/add: A=" + cartA.value() + " B=" + cartB.value() + " (add wins, both converge)");
    }
}
