import java.util.*;
import java.util.stream.*;

/**
 * Check if Any Two Intervals Overlap (Easy) - Day 15
 * https://leetcode.com/problems/gfg-check-if-any-two-intervals-overlap/
 *
 * Approach 1: Check every pair  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sort by start, compare neighbours (optimal for any values)  |  Time O(n log n)  |  Space O(log n) sort stack  <- best
 * Approach 3: Difference array over the time range  |  Time O(n + maxTime)  |  Space O(maxTime)
 *
 * Run: javac GfgCheckIfAnyTwoIntervalsOverlap.java && java GfgCheckIfAnyTwoIntervalsOverlap
 */
public class GfgCheckIfAnyTwoIntervalsOverlap {

    // Approach 1: Check every pair
    // Time O(n^2), Space O(1)
    // Idea: Two intervals overlap when each starts before the other ends.
    static class Approach1 {
        public boolean isOverlap(int[][] arr) {
            for (int i = 0; i < arr.length; i++)
                for (int j = i + 1; j < arr.length; j++)
                    if (arr[i][0] < arr[j][1] && arr[j][0] < arr[i][1]) return true;
            return false;
        }
    }

    // Approach 2: Sort by start, compare neighbours (optimal for any values)
    // Time O(n log n), Space O(log n) sort stack
    // Idea: After sorting by start, if any two intervals overlap then some adjacent pair overlaps: check start[i] < end[i-1].
    static class Approach2 {
        public boolean isOverlap(int[][] arr) {
            int[][] a = arr.clone();
            Arrays.sort(a, (x, y) -> Integer.compare(x[0], y[0]));
            for (int i = 1; i < a.length; i++) if (a[i][0] < a[i - 1][1]) return true;
            return false;
        }
    }

    // Approach 3: Difference array over the time range
    // Time O(n + maxTime), Space O(maxTime)
    // Idea: When times are small non-negative integers, mark +1 at each start and -1 at each end; if the running count ever exceeds 1, two intervals overlap.
    static class Approach3 {
        public boolean isOverlap(int[][] arr) {
            int max = 0;
            for (int[] x : arr) max = Math.max(max, x[1]);
            int[] diff = new int[max + 2];
            for (int[] x : arr) { diff[x[0]]++; diff[x[1]]--; }
            int run = 0;
            for (int t = 0; t <= max; t++) {
                run += diff[t];
                if (run > 1) return true;
            }
            return false;
        }
    }

    static String show(Object r) {
        if (r instanceof int[] a) return Arrays.toString(a);
        if (r instanceof int[][] a) return Arrays.deepToString(a);
        if (r instanceof ListNode l) return toList(l);
        return String.valueOf(r);
    }
    static String norm(List<List<Integer>> x) {                 // order-independent view of a list of lists
        List<List<Integer>> c = new ArrayList<>();
        for (List<Integer> t : x) { List<Integer> s = new ArrayList<>(t); Collections.sort(s); c.add(s); }
        c.sort((p, q) -> { for (int i = 0; i < Math.min(p.size(), q.size()); i++) { int d = Integer.compare(p.get(i), q.get(i)); if (d != 0) return d; } return p.size() - q.size(); });
        return c.toString();
    }
    static String sorted(List<Integer> x) { List<Integer> c = new ArrayList<>(x); Collections.sort(c); return c.toString(); }
    static class ListNode {
        int val; ListNode next;
        ListNode() {}
        ListNode(int val) { this.val = val; }
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
    }
    static ListNode list(int... v) { ListNode d = new ListNode(0), t = d; for (int x : v) { t.next = new ListNode(x); t = t.next; } return d.next; }
    static ListNode cyclic(int[] v, int pos) {                   // list whose tail links back to index pos (-1 = no cycle)
        ListNode h = list(v), t = h, at = null;
        for (int i = 0; t != null; i++, t = t.next) { if (i == pos) at = t; if (t.next == null) { t.next = at; break; } }
        return h;
    }
    static String toList(ListNode h) { List<Integer> o = new ArrayList<>(); for (int i = 0; h != null && i < 1000; i++, h = h.next) o.add(h.val); return o.toString(); }
    static int passed = 0;
    static void check(String what, Object r, String want) {
        String got = show(r);
        if (!got.equals(want)) throw new AssertionError(what + ": got " + got + ", want " + want);
        passed++;
    }

    public static void main(String[] args) {
        check("Approach 1", new Approach1().isOverlap(new int[][]{{1,3},{5,7},{2,4},{6,8}}), "true");
        check("Approach 1", new Approach1().isOverlap(new int[][]{{1,3},{7,9},{4,6},{10,13}}), "false");
        check("Approach 1", new Approach1().isOverlap(new int[][]{{1,3},{3,5}}), "false");
        check("Approach 2", new Approach2().isOverlap(new int[][]{{1,3},{5,7},{2,4},{6,8}}), "true");
        check("Approach 2", new Approach2().isOverlap(new int[][]{{1,3},{7,9},{4,6},{10,13}}), "false");
        check("Approach 2", new Approach2().isOverlap(new int[][]{{1,3},{3,5}}), "false");
        check("Approach 3", new Approach3().isOverlap(new int[][]{{1,3},{5,7},{2,4},{6,8}}), "true");
        check("Approach 3", new Approach3().isOverlap(new int[][]{{1,3},{7,9},{4,6},{10,13}}), "false");
        check("Approach 3", new Approach3().isOverlap(new int[][]{{1,3},{3,5}}), "false");
        System.out.println("GfgCheckIfAnyTwoIntervalsOverlap: all 3 approaches passed " + passed + " checks");
    }
}
