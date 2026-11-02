import java.util.*;

/**
 * Day 2 - Live demo 1: watch a sliding window move.
 *   Part A: fixed-size window  -> maximum sum of any k consecutive numbers
 *   Part B: variable window    -> longest substring without repeating characters
 *
 * Run:  javac SlidingWindowDemo.java && java SlidingWindowDemo
 */
public class SlidingWindowDemo {

    public static void main(String[] args) {
        fixedWindow(new int[]{2, 1, 5, 1, 3, 2, 9, 1}, 3);
        variableWindow("abcabcbb");
    }

    // ---------- Part A: window of exactly k elements ----------
    static void fixedWindow(int[] a, int k) {
        System.out.println("PART A: max sum of " + k + " consecutive numbers in " + Arrays.toString(a));
        int sum = 0;
        for (int i = 0; i < k; i++) sum += a[i];               // first window
        int best = sum;
        print(a, 0, k - 1, "sum=" + sum + "  (first window)");
        for (int r = k; r < a.length; r++) {
            sum += a[r] - a[r - k];                            // add the new right, drop the old left
            best = Math.max(best, sum);
            print(a, r - k + 1, r, "sum=" + sum + "  (+" + a[r] + " -" + a[r - k] + ")  best=" + best);
        }
        System.out.println("Answer: " + best + "   Work done: O(n), not O(n*k)\n");
    }

    // ---------- Part B: window grows and shrinks ----------
    static void variableWindow(String s) {
        System.out.println("PART B: longest substring without repeats in \"" + s + "\"");
        int[] last = new int[128];
        Arrays.fill(last, -1);
        int l = 0, best = 0;
        for (int r = 0; r < s.length(); r++) {
            char c = s.charAt(r);
            String note = "";
            if (last[c] >= l) {                                // repeat inside the window
                note = "  '" + c + "' repeats -> left jumps " + l + " -> " + (last[c] + 1);
                l = last[c] + 1;
            }
            last[c] = r;
            best = Math.max(best, r - l + 1);
            System.out.printf("  r=%d  window=[%d..%d] \"%s\"  len=%d  best=%d%s%n", r, l, r, s.substring(l, r + 1), r - l + 1, best, note);
        }
        System.out.println("Answer: " + best + "   Each index enters and leaves the window at most once -> O(n)");
    }

    static void print(int[] a, int l, int r, String info) {
        StringBuilder sb = new StringBuilder("  ");
        for (int i = 0; i < a.length; i++) sb.append(i == l ? "[" : " ").append(a[i]).append(i == r ? "]" : " ");
        System.out.println(sb + "   " + info);
    }
}
