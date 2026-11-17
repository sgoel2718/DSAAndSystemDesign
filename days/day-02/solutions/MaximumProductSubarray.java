import java.util.*;
import java.util.stream.*;

/**
 * Maximum Product Subarray (Medium) - Day 2
 * https://leetcode.com/problems/maximum-product-subarray/
 *
 * Approach 1: Brute force: every subarray  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix and suffix products  |  Time O(n)  |  Space O(1)
 * Approach 3: Kadane tracking max and min (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MaximumProductSubarray.java && java MaximumProductSubarray
 */
public class MaximumProductSubarray {

    // Approach 1: Brute force: every subarray
    // Time O(n^2), Space O(1)
    // Idea: Running product from each start; keep the largest.
    static class Approach1 {
        public int maxProduct(int[] nums) {
            int best = nums[0];
            for (int i = 0; i < nums.length; i++) {
                int p = 1;
                for (int j = i; j < nums.length; j++) { p *= nums[j]; best = Math.max(best, p); }
            }
            return best;
        }
    }

    // Approach 2: Prefix and suffix products
    // Time O(n), Space O(1)
    // Idea: The best product starts at the array start, ends at the array end, or sits between zeros. Scan running products from both ends, restarting after a zero.
    static class Approach2 {
        public int maxProduct(int[] nums) {
            int n = nums.length, pre = 1, suf = 1, best = Integer.MIN_VALUE;
            for (int i = 0; i < n; i++) {
                pre = (pre == 0 ? 1 : pre) * nums[i];
                suf = (suf == 0 ? 1 : suf) * nums[n - 1 - i];
                best = Math.max(best, Math.max(pre, suf));
            }
            return best;
        }
    }

    // Approach 3: Kadane tracking max and min (optimal)
    // Time O(n), Space O(1)
    // Idea: A negative number turns the smallest product into the largest, so keep both the max and the min product ending here.
    static class Approach3 {
        public int maxProduct(int[] nums) {
            int hi = nums[0], lo = nums[0], best = nums[0];
            for (int i = 1; i < nums.length; i++) {
                int x = nums[i], h = hi;
                hi = Math.max(x, Math.max(h * x, lo * x));
                lo = Math.min(x, Math.min(h * x, lo * x));
                best = Math.max(best, hi);
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
        check("Approach 1", new Approach1().maxProduct(new int[]{2,3,-2,4}), "6");
        check("Approach 1", new Approach1().maxProduct(new int[]{-2,0,-1}), "0");
        check("Approach 1", new Approach1().maxProduct(new int[]{-2,3,-4}), "24");
        check("Approach 1", new Approach1().maxProduct(new int[]{-2}), "-2");
        check("Approach 2", new Approach2().maxProduct(new int[]{2,3,-2,4}), "6");
        check("Approach 2", new Approach2().maxProduct(new int[]{-2,0,-1}), "0");
        check("Approach 2", new Approach2().maxProduct(new int[]{-2,3,-4}), "24");
        check("Approach 2", new Approach2().maxProduct(new int[]{-2}), "-2");
        check("Approach 3", new Approach3().maxProduct(new int[]{2,3,-2,4}), "6");
        check("Approach 3", new Approach3().maxProduct(new int[]{-2,0,-1}), "0");
        check("Approach 3", new Approach3().maxProduct(new int[]{-2,3,-4}), "24");
        check("Approach 3", new Approach3().maxProduct(new int[]{-2}), "-2");
        System.out.println("MaximumProductSubarray: all 3 approaches passed " + passed + " checks");
    }
}
