import java.util.*;
import java.util.stream.*;

/**
 * Split Array Largest Sum (Hard) - Day 5
 * https://leetcode.com/problems/split-array-largest-sum/
 *
 * Approach 1: Dynamic programming over split points  |  Time O(k x n^2)  |  Space O(k x n)
 * Approach 2: Binary search on the answer (optimal)  |  Time O(n log sum)  |  Space O(1)  <- best
 *
 * Run: javac SplitArrayLargestSum.java && java SplitArrayLargestSum
 */
public class SplitArrayLargestSum {

    // Approach 1: Dynamic programming over split points
    // Time O(k x n^2), Space O(k x n)
    // Idea: dp[j][i] = minimal largest sum when the first i numbers form j subarrays; the last subarray starts at some p.
    static class Approach1 {
        public int splitArray(int[] nums, int k) {
            int n = nums.length;
            long[] pre = new long[n + 1];
            for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
            long[][] dp = new long[k + 1][n + 1];
            for (long[] row : dp) Arrays.fill(row, Long.MAX_VALUE);
            dp[0][0] = 0;
            for (int j = 1; j <= k; j++)
                for (int i = j; i <= n; i++)
                    for (int p = j - 1; p < i; p++)
                        if (dp[j - 1][p] != Long.MAX_VALUE)
                            dp[j][i] = Math.min(dp[j][i], Math.max(dp[j - 1][p], pre[i] - pre[p]));
            return (int) dp[k][n];
        }
    }

    // Approach 2: Binary search on the answer (optimal)
    // Time O(n log sum), Space O(1)
    // Idea: Same structure as Allocate Minimum Pages: for a limit L, count greedy subarrays; binary search the smallest L needing <= k pieces.
    static class Approach2 {
        public int splitArray(int[] nums, int k) {
            long lo = 0, hi = 0;
            for (int x : nums) { lo = Math.max(lo, x); hi += x; }
            while (lo < hi) {
                long mid = lo + (hi - lo) / 2;
                int pieces = 1;
                long sum = 0;
                for (int x : nums) {
                    if (sum + x > mid) { pieces++; sum = 0; }
                    sum += x;
                }
                if (pieces <= k) hi = mid;
                else lo = mid + 1;
            }
            return (int) lo;
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
        check("Approach 1", new Approach1().splitArray(new int[]{7,2,5,10,8}, 2), "18");
        check("Approach 1", new Approach1().splitArray(new int[]{1,2,3,4,5}, 2), "9");
        check("Approach 1", new Approach1().splitArray(new int[]{1,4,4}, 3), "4");
        check("Approach 2", new Approach2().splitArray(new int[]{7,2,5,10,8}, 2), "18");
        check("Approach 2", new Approach2().splitArray(new int[]{1,2,3,4,5}, 2), "9");
        check("Approach 2", new Approach2().splitArray(new int[]{1,4,4}, 3), "4");
        System.out.println("SplitArrayLargestSum: all 2 approaches passed " + passed + " checks");
    }
}
