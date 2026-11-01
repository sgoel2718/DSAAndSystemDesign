import java.util.HashSet;
import java.util.Random;
import java.util.Set;

/**
 * Day 1 - Demo 1: watch Big-O happen.
 * Part A prints how many "steps" each complexity class needs as n grows.
 * Part B times two real solutions to the SAME problem (does the array have a duplicate?):
 *   O(n^2) nested loops vs O(n) HashSet.
 *
 * Run:  javac GrowthRates.java && java GrowthRates
 */
public class GrowthRates {

    public static void main(String[] args) {
        partA_countSteps();
        partB_timeRealCode();
    }

    // ---------- Part A: pure step counts ----------
    static void partA_countSteps() {
        System.out.println("PART A: steps needed as n grows");
        System.out.printf("%-10s %8s %10s %12s %14s %18s%n", "n", "O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)");
        for (long n = 10; n <= 1_000_000; n *= 10) {
            long log = Math.round(Math.log(n) / Math.log(2));
            System.out.printf("%-10d %8d %10d %12d %14d %18d%n", n, 1, log, n, n * log, n * n);
        }
        System.out.println("Rule of thumb: about 10^8 simple steps run in ~1 second.");
        System.out.println("So n = 10^5 rules out O(n^2) (10^10 steps) but O(n log n) (~1.7 x 10^6) is instant.\n");
    }

    // ---------- Part B: same problem, two complexities ----------
    static boolean hasDuplicateQuadratic(int[] a) {          // O(n^2) time, O(1) space
        for (int i = 0; i < a.length; i++)
            for (int j = i + 1; j < a.length; j++)
                if (a[i] == a[j]) return true;
        return false;
    }

    static boolean hasDuplicateLinear(int[] a) {             // O(n) time, O(n) space
        Set<Integer> seen = new HashSet<>();
        for (int x : a)
            if (!seen.add(x)) return true;                   // add() returns false if x was already there
        return false;
    }

    static void partB_timeRealCode() {
        System.out.println("PART B: duplicate check on arrays with NO duplicates (worst case)");
        System.out.printf("%-10s %16s %16s%n", "n", "O(n^2) ms", "O(n) ms");
        for (int n : new int[]{1_000, 10_000, 50_000, 100_000}) {
            int[] a = distinctShuffled(n);
            hasDuplicateQuadratic(a); hasDuplicateLinear(a);  // warm-up so the JIT compiles both
            long t1 = System.nanoTime(); hasDuplicateQuadratic(a); long t2 = System.nanoTime();
            hasDuplicateLinear(a); long t3 = System.nanoTime();
            System.out.printf("%-10d %16.2f %16.2f%n", n, (t2 - t1) / 1e6, (t3 - t2) / 1e6);
        }
        System.out.println("10x more data -> about 100x slower for O(n^2), about 10x for O(n).");
    }

    static int[] distinctShuffled(int n) {
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = i;
        Random r = new Random(42);
        for (int i = n - 1; i > 0; i--) {                    // Fisher-Yates shuffle (Day 18)
            int j = r.nextInt(i + 1);
            int t = a[i]; a[i] = a[j]; a[j] = t;
        }
        return a;
    }
}
