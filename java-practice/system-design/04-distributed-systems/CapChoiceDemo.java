import java.util.*;

public class CapChoiceDemo {
    // 3 replicas; a partition isolates replica C. CP mode requires a majority; AP mode accepts locally and reconciles.
    static class Replica { final String name; int value; long ts; Replica(String n) { name = n; } }
    static final Replica A = new Replica("A"), B = new Replica("B"), C = new Replica("C");
    static Set<Replica> partitionWithC = Set.of(C);

    static List<Replica> reachableFrom(Replica r) { return partitionWithC.contains(r) ? List.of(C) : List.of(A, B); }

    static String write(String mode, Replica at, int v, long ts) {
        List<Replica> reach = reachableFrom(at);
        if (mode.equals("CP") && reach.size() < 2) return "write " + v + " at " + at.name + ": REJECTED (no majority)";
        for (Replica r : reach) { r.value = v; r.ts = ts; }
        return "write " + v + " at " + at.name + ": OK on " + reach.stream().map(r -> r.name).toList();
    }
    static String read(String mode, Replica at) {
        if (mode.equals("CP") && reachableFrom(at).size() < 2) return "read at " + at.name + ": ERROR (can't guarantee latest)";
        return "read at " + at.name + ": " + at.value;
    }
    static void heal() {                                                     // last-write-wins reconciliation
        Replica newest = List.of(A, B, C).stream().max(Comparator.comparingLong(r -> r.ts)).get();
        for (Replica r : List.of(A, B, C)) { r.value = newest.value; r.ts = newest.ts; }
    }

    public static void main(String[] args) {
        for (String mode : List.of("CP", "AP")) {
            A.value = B.value = C.value = 0; A.ts = B.ts = C.ts = 0;
            System.out.println("== " + mode + " ==");
            System.out.println(write(mode, A, 10, 1));
            System.out.println(write(mode, C, 20, 2));
            System.out.println(read(mode, C));
            System.out.println(read(mode, B));
            heal();
            System.out.println("after healing (last write wins): A=" + A.value + " B=" + B.value + " C=" + C.value);
        }
    }
}
