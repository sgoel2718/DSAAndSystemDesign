import java.util.*;
import java.util.stream.*;

/**
 * Smallest Sum Contiguous Subarray (Medium) - Day 2
 * https://leetcode.com/problems/gfg-smallest-sum-contiguous-subarray/
 *
 * Approach 1: Brute force: every subarray  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Negate, then maximum-subarray Kadane  |  Time O(n)  |  Space O(1)
 * Approach 3: Kadane for the minimum (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac GfgSmallestSumContiguousSubarray.java && java GfgSmallestSumContiguousSubarray
 */
public class GfgSmallestSumContiguousSubarray {

    // Approach 1: Brute force: every subarray
    // Time O(n^2), Space O(1)
    // Idea: Running sum from each start; keep the smallest.
    static class Approach1 {
        public int smallestSumSubarray(int[] a) {
            int best = Integer.MAX_VALUE;
            for (int i = 0; i < a.length; i++) {
                int s = 0;
                for (int j = i; j < a.length; j++) { s += a[j]; best = Math.min(best, s); }
            }
            return best;
        }
    }

    // Approach 2: Negate, then maximum-subarray Kadane
    // Time O(n), Space O(1)
    // Idea: The smallest sum of a is minus the largest sum of -a.
    static class Approach2 {
        public int smallestSumSubarray(int[] a) {
            int cur = -a[0], best = -a[0];
            for (int i = 1; i < a.length; i++) {
                cur = Math.max(-a[i], cur - a[i]);
                best = Math.max(best, cur);
            }
            return -best;
        }
    }

    // Approach 3: Kadane for the minimum (optimal)
    // Time O(n), Space O(1)
    // Idea: Same rule with min: either extend the smallest subarray ending at the previous index or start fresh.
    static class Approach3 {
        public int smallestSumSubarray(int[] a) {
            int cur = a[0], best = a[0];
            for (int i = 1; i < a.length; i++) {
                cur = Math.min(a[i], cur + a[i]);
                best = Math.min(best, cur);
            }
            return best;
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
        check("Approach 1", new Approach1().smallestSumSubarray(new int[]{3,-4,2,-3,-1,7,-5}), "-6");
        check("Approach 1", new Approach1().smallestSumSubarray(new int[]{2,6,8,1,4}), "1");
        check("Approach 2", new Approach2().smallestSumSubarray(new int[]{3,-4,2,-3,-1,7,-5}), "-6");
        check("Approach 2", new Approach2().smallestSumSubarray(new int[]{2,6,8,1,4}), "1");
        check("Approach 3", new Approach3().smallestSumSubarray(new int[]{3,-4,2,-3,-1,7,-5}), "-6");
        check("Approach 3", new Approach3().smallestSumSubarray(new int[]{2,6,8,1,4}), "1");
        System.out.println("GfgSmallestSumContiguousSubarray: all 3 approaches passed " + passed + " checks");
    }
}
