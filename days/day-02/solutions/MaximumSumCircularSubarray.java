import java.util.*;
import java.util.stream.*;

/**
 * Maximum Sum Circular Subarray (Medium) - Day 2
 * https://leetcode.com/problems/maximum-sum-circular-subarray/
 *
 * Approach 1: Brute force: every start, every length  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Kadane + best prefix joined with each suffix  |  Time O(n)  |  Space O(n)
 * Approach 3: Total minus minimum subarray (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MaximumSumCircularSubarray.java && java MaximumSumCircularSubarray
 */
public class MaximumSumCircularSubarray {

    // Approach 1: Brute force: every start, every length
    // Time O(n^2), Space O(1)
    // Idea: From each start, walk up to n elements around the circle keeping a running sum.
    static class Approach1 {
        public int maxSubarraySumCircular(int[] nums) {
            int n = nums.length, best = Integer.MIN_VALUE;
            for (int i = 0; i < n; i++) {
                int s = 0;
                for (int len = 1; len <= n; len++) { s += nums[(i + len - 1) % n]; best = Math.max(best, s); }
            }
            return best;
        }
    }

    // Approach 2: Kadane + best prefix joined with each suffix
    // Time O(n), Space O(n)
    // Idea: A wrapping subarray is a suffix plus a prefix. Precompute the best prefix sum up to each index, then try every suffix.
    static class Approach2 {
        public int maxSubarraySumCircular(int[] nums) {
            int n = nums.length, cur = nums[0], best = nums[0];
            for (int i = 1; i < n; i++) { cur = Math.max(nums[i], cur + nums[i]); best = Math.max(best, cur); }
            int[] leftMax = new int[n];
            int pre = nums[0];
            leftMax[0] = nums[0];
            for (int i = 1; i < n; i++) { pre += nums[i]; leftMax[i] = Math.max(leftMax[i - 1], pre); }
            int suf = 0;
            for (int i = n - 1; i >= 1; i--) { suf += nums[i]; best = Math.max(best, suf + leftMax[i - 1]); }
            return best;
        }
    }

    // Approach 3: Total minus minimum subarray (optimal)
    // Time O(n), Space O(1)
    // Idea: A wrapping subarray = total - (a middle subarray left out); to maximise it, leave out the minimum subarray. If every number is negative, return the normal Kadane max.
    static class Approach3 {
        public int maxSubarraySumCircular(int[] nums) {
            int total = 0, curMax = 0, curMin = 0, maxS = Integer.MIN_VALUE, minS = Integer.MAX_VALUE;
            for (int x : nums) {
                curMax = Math.max(x, curMax + x);
                maxS = Math.max(maxS, curMax);
                curMin = Math.min(x, curMin + x);
                minS = Math.min(minS, curMin);
                total += x;
            }
            return maxS < 0 ? maxS : Math.max(maxS, total - minS);
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
        check("Approach 1", new Approach1().maxSubarraySumCircular(new int[]{1,-2,3,-2}), "3");
        check("Approach 1", new Approach1().maxSubarraySumCircular(new int[]{5,-3,5}), "10");
        check("Approach 1", new Approach1().maxSubarraySumCircular(new int[]{-3,-2,-3}), "-2");
        check("Approach 2", new Approach2().maxSubarraySumCircular(new int[]{1,-2,3,-2}), "3");
        check("Approach 2", new Approach2().maxSubarraySumCircular(new int[]{5,-3,5}), "10");
        check("Approach 2", new Approach2().maxSubarraySumCircular(new int[]{-3,-2,-3}), "-2");
        check("Approach 3", new Approach3().maxSubarraySumCircular(new int[]{1,-2,3,-2}), "3");
        check("Approach 3", new Approach3().maxSubarraySumCircular(new int[]{5,-3,5}), "10");
        check("Approach 3", new Approach3().maxSubarraySumCircular(new int[]{-3,-2,-3}), "-2");
        System.out.println("MaximumSumCircularSubarray: all 3 approaches passed " + passed + " checks");
    }
}
