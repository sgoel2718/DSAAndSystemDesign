import java.util.*;
import java.util.stream.*;

/**
 * Minimum Size Subarray Sum (Medium) - Day 2
 * https://leetcode.com/problems/minimum-size-subarray-sum/
 *
 * Approach 1: Brute force: grow from every start  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix sums + binary search  |  Time O(n log n)  |  Space O(n)
 * Approach 3: Variable sliding window (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MinimumSizeSubarraySum.java && java MinimumSizeSubarraySum
 */
public class MinimumSizeSubarraySum {

    // Approach 1: Brute force: grow from every start
    // Time O(n^2), Space O(1)
    // Idea: From each start, extend until the sum reaches the target; stop early because numbers are positive.
    static class Approach1 {
        public int minSubArrayLen(int target, int[] nums) {
            int best = Integer.MAX_VALUE;
            for (int i = 0; i < nums.length; i++) {
                int s = 0;
                for (int j = i; j < nums.length; j++) {
                    s += nums[j];
                    if (s >= target) { best = Math.min(best, j - i + 1); break; }
                }
            }
            return best == Integer.MAX_VALUE ? 0 : best;
        }
    }

    // Approach 2: Prefix sums + binary search
    // Time O(n log n), Space O(n)
    // Idea: Prefix sums are increasing (positive numbers). For each start i, binary search the first end j with pre[j] >= pre[i] + target.
    static class Approach2 {
        public int minSubArrayLen(int target, int[] nums) {
            int n = nums.length, best = Integer.MAX_VALUE;
            long[] pre = new long[n + 1];
            for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
            for (int i = 0; i < n; i++) {
                long need = pre[i] + target;
                int lo = i + 1, hi = n + 1;
                while (lo < hi) {
                    int mid = (lo + hi) >>> 1;
                    if (pre[mid] >= need) hi = mid; else lo = mid + 1;
                }
                if (lo <= n) best = Math.min(best, lo - i);
            }
            return best == Integer.MAX_VALUE ? 0 : best;
        }
    }

    // Approach 3: Variable sliding window (optimal)
    // Time O(n), Space O(1)
    // Idea: Grow right; while the sum is at least the target, record the length and shrink from the left.
    static class Approach3 {
        public int minSubArrayLen(int target, int[] nums) {
            int l = 0, sum = 0, best = Integer.MAX_VALUE;
            for (int r = 0; r < nums.length; r++) {
                sum += nums[r];
                while (sum >= target) {
                    best = Math.min(best, r - l + 1);
                    sum -= nums[l++];
                }
            }
            return best == Integer.MAX_VALUE ? 0 : best;
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
        check("Approach 1", new Approach1().minSubArrayLen(7, new int[]{2,3,1,2,4,3}), "2");
        check("Approach 1", new Approach1().minSubArrayLen(4, new int[]{1,4,4}), "1");
        check("Approach 1", new Approach1().minSubArrayLen(11, new int[]{1,1,1,1,1,1,1,1}), "0");
        check("Approach 2", new Approach2().minSubArrayLen(7, new int[]{2,3,1,2,4,3}), "2");
        check("Approach 2", new Approach2().minSubArrayLen(4, new int[]{1,4,4}), "1");
        check("Approach 2", new Approach2().minSubArrayLen(11, new int[]{1,1,1,1,1,1,1,1}), "0");
        check("Approach 3", new Approach3().minSubArrayLen(7, new int[]{2,3,1,2,4,3}), "2");
        check("Approach 3", new Approach3().minSubArrayLen(4, new int[]{1,4,4}), "1");
        check("Approach 3", new Approach3().minSubArrayLen(11, new int[]{1,1,1,1,1,1,1,1}), "0");
        System.out.println("MinimumSizeSubarraySum: all 3 approaches passed " + passed + " checks");
    }
}
