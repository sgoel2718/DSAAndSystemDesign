import java.util.*;
import java.util.stream.*;

/**
 * Maximum Absolute Sum of Any Subarray (Medium) - Day 2
 * https://leetcode.com/problems/maximum-absolute-sum-of-any-subarray/
 *
 * Approach 1: Brute force: every subarray  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix sums: largest prefix minus smallest prefix  |  Time O(n)  |  Space O(1)
 * Approach 3: Kadane for the max and for the min (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MaximumAbsoluteSumOfAnySubarray.java && java MaximumAbsoluteSumOfAnySubarray
 */
public class MaximumAbsoluteSumOfAnySubarray {

    // Approach 1: Brute force: every subarray
    // Time O(n^2), Space O(1)
    // Idea: Running sum from each start; keep the largest absolute value.
    static class Approach1 {
        public int maxAbsoluteSum(int[] nums) {
            int best = 0;
            for (int i = 0; i < nums.length; i++) {
                int s = 0;
                for (int j = i; j < nums.length; j++) { s += nums[j]; best = Math.max(best, Math.abs(s)); }
            }
            return best;
        }
    }

    // Approach 2: Prefix sums: largest prefix minus smallest prefix
    // Time O(n), Space O(1)
    // Idea: Any subarray sum is a difference of two prefix sums, so the largest absolute sum is max prefix - min prefix (including the empty prefix 0).
    static class Approach2 {
        public int maxAbsoluteSum(int[] nums) {
            int pre = 0, hi = 0, lo = 0;
            for (int x : nums) {
                pre += x;
                hi = Math.max(hi, pre);
                lo = Math.min(lo, pre);
            }
            return hi - lo;
        }
    }

    // Approach 3: Kadane for the max and for the min (optimal)
    // Time O(n), Space O(1)
    // Idea: The answer is the larger of |best max subarray| and |best min subarray|; run both Kadanes in one pass.
    static class Approach3 {
        public int maxAbsoluteSum(int[] nums) {
            int curMax = 0, curMin = 0, best = 0;
            for (int x : nums) {
                curMax = Math.max(x, curMax + x);
                curMin = Math.min(x, curMin + x);
                best = Math.max(best, Math.max(curMax, -curMin));
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
        check("Approach 1", new Approach1().maxAbsoluteSum(new int[]{1,-3,2,3,-4}), "5");
        check("Approach 1", new Approach1().maxAbsoluteSum(new int[]{2,-5,1,-4,3,-2}), "8");
        check("Approach 2", new Approach2().maxAbsoluteSum(new int[]{1,-3,2,3,-4}), "5");
        check("Approach 2", new Approach2().maxAbsoluteSum(new int[]{2,-5,1,-4,3,-2}), "8");
        check("Approach 3", new Approach3().maxAbsoluteSum(new int[]{1,-3,2,3,-4}), "5");
        check("Approach 3", new Approach3().maxAbsoluteSum(new int[]{2,-5,1,-4,3,-2}), "8");
        System.out.println("MaximumAbsoluteSumOfAnySubarray: all 3 approaches passed " + passed + " checks");
    }
}
