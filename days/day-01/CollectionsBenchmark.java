import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

/**
 * Day 1 - Demo 2 (the planned live demo): ArrayList vs LinkedList vs ArrayDeque.
 * Same operations, very different costs, because of how each is stored in memory.
 *
 *   ArrayList  = resizable array  -> get(i) O(1), add at end amortised O(1), add at front O(n)
 *   LinkedList = doubly linked    -> get(i) O(n), add at either end O(1)
 *   ArrayDeque = circular array   -> add/remove at either end O(1), no get(i)
 *
 * Run:  javac CollectionsBenchmark.java && java CollectionsBenchmark
 */
public class CollectionsBenchmark {
    static final int N = 100_000;

    public static void main(String[] args) {
        for (int round = 0; round < 2; round++) {           // round 0 = JIT warm-up, round 1 = measured
            boolean print = round == 1;
            if (print) System.out.printf("%-28s %12s %12s %12s%n", "operation (n = 100,000)", "ArrayList", "LinkedList", "ArrayDeque");

            // 1) add at the END
            double al = time(() -> { List<Integer> l = new ArrayList<>(); for (int i = 0; i < N; i++) l.add(i); });
            double ll = time(() -> { List<Integer> l = new LinkedList<>(); for (int i = 0; i < N; i++) l.add(i); });
            double dq = time(() -> { ArrayDeque<Integer> d = new ArrayDeque<>(); for (int i = 0; i < N; i++) d.addLast(i); });
            if (print) row("add at end", al, ll, dq);

            // 2) add at the FRONT
            al = time(() -> { List<Integer> l = new ArrayList<>(); for (int i = 0; i < N; i++) l.add(0, i); });
            ll = time(() -> { LinkedList<Integer> l = new LinkedList<>(); for (int i = 0; i < N; i++) l.addFirst(i); });
            dq = time(() -> { ArrayDeque<Integer> d = new ArrayDeque<>(); for (int i = 0; i < N; i++) d.addFirst(i); });
            if (print) row("add at front", al, ll, dq);

            // 3) get(i) for 10,000 indexes in the middle area
            List<Integer> a = new ArrayList<>(), b = new LinkedList<>();
            for (int i = 0; i < N; i++) { a.add(i); b.add(i); }
            al = time(() -> { long s = 0; for (int i = 0; i < 10_000; i++) s += a.get(N / 2 + i); sink(s); });
            ll = time(() -> { long s = 0; for (int i = 0; i < 10_000; i++) s += b.get(N / 2 + i); sink(s); });
            if (print) System.out.printf("%-28s %10.2fms %10.2fms %12s%n", "get(i) x 10,000 (middle)", al, ll, "n/a");
        }
        System.out.println("\nTakeaways:");
        System.out.println("- ArrayList: default list. Fast index access, cheap appends.");
        System.out.println("- LinkedList: almost never the right choice in interviews (slow get, poor cache locality).");
        System.out.println("- ArrayDeque: use it for stacks AND queues.");
    }

    static void row(String op, double a, double b, double c) {
        System.out.printf("%-28s %10.2fms %10.2fms %10.2fms%n", op, a, b, c);
    }

    static double time(Runnable r) {
        long t = System.nanoTime();
        r.run();
        return (System.nanoTime() - t) / 1e6;
    }

    static volatile long blackhole;
    static void sink(long v) { blackhole = v; }               // stops the JIT from deleting the loop
}
