import java.util.*;
import java.util.stream.*;

/**
 * Subarray Product Less Than K (Medium) - Day 2
 * https://leetcode.com/problems/subarray-product-less-than-k/
 *
 * Approach 1: Brute force with early stop  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sliding window (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac SubarrayProductLessThanK.java && java SubarrayProductLessThanK
 */
public class SubarrayProductLessThanK {

    // Approach 1: Brute force with early stop
    // Time O(n^2), Space O(1)
    // Idea: From each start, multiply forward while the product stays below k (all numbers are positive, so it only grows).
    static class Approach1 {
        public int numSubarrayProductLessThanK(int[] nums, int k) {
            int count = 0;
            for (int i = 0; i < nums.length; i++) {
                long p = 1;
                for (int j = i; j < nums.length; j++) {
                    p *= nums[j];
                    if (p >= k) break;
                    count++;
                }
            }
            return count;
        }
    }

    // Approach 2: Sliding window (optimal)
    // Time O(n), Space O(1)
    // Idea: Grow the window to the right; while the product is >= k, divide out the left element. Every window ending at r contributes r - l + 1 subarrays.
    static class Approach2 {
        public int numSubarrayProductLessThanK(int[] nums, int k) {
            if (k <= 1) return 0;
            long prod = 1;
            int l = 0, count = 0;
            for (int r = 0; r < nums.length; r++) {
                prod *= nums[r];
                while (prod >= k) prod /= nums[l++];
                count += r - l + 1;
            }
            return count;
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
        check("Approach 1", new Approach1().numSubarrayProductLessThanK(new int[]{10,5,2,6}, 100), "8");
        check("Approach 1", new Approach1().numSubarrayProductLessThanK(new int[]{1,2,3}, 0), "0");
        check("Approach 1", new Approach1().numSubarrayProductLessThanK(new int[]{1,1,1}, 2), "6");
        check("Approach 2", new Approach2().numSubarrayProductLessThanK(new int[]{10,5,2,6}, 100), "8");
        check("Approach 2", new Approach2().numSubarrayProductLessThanK(new int[]{1,2,3}, 0), "0");
        check("Approach 2", new Approach2().numSubarrayProductLessThanK(new int[]{1,1,1}, 2), "6");
        System.out.println("SubarrayProductLessThanK: all 2 approaches passed " + passed + " checks");
    }
}
