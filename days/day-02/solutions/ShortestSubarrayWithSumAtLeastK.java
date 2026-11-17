import java.util.*;
import java.util.stream.*;

/**
 * Shortest Subarray with Sum at Least K (Hard) - Day 2
 * https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/
 *
 * Approach 1: Brute force: every subarray  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix sums + monotonic deque (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac ShortestSubarrayWithSumAtLeastK.java && java ShortestSubarrayWithSumAtLeastK
 */
public class ShortestSubarrayWithSumAtLeastK {

    // Approach 1: Brute force: every subarray
    // Time O(n^2), Space O(1)
    // Idea: Running sum from each start; record the shortest subarray reaching k. Negative numbers mean we cannot stop early.
    static class Approach1 {
        public int shortestSubarray(int[] nums, int k) {
            int best = Integer.MAX_VALUE;
            for (int i = 0; i < nums.length; i++) {
                long s = 0;
                for (int j = i; j < nums.length && j - i + 1 < best; j++) {
                    s += nums[j];
                    if (s >= k) best = j - i + 1;
                }
            }
            return best == Integer.MAX_VALUE ? -1 : best;
        }
    }

    // Approach 2: Prefix sums + monotonic deque (optimal)
    // Time O(n), Space O(n)
    // Idea: Keep prefix indices with increasing prefix sums in a deque. From the front, pop while pre[i] - pre[front] >= k (record lengths). From the back, pop larger prefixes: a smaller, later prefix is always a better start.
    static class Approach2 {
        public int shortestSubarray(int[] nums, int k) {
            int n = nums.length, best = n + 1;
            long[] pre = new long[n + 1];
            for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
            Deque<Integer> dq = new ArrayDeque<>();
            for (int i = 0; i <= n; i++) {
                while (!dq.isEmpty() && pre[i] - pre[dq.peekFirst()] >= k) best = Math.min(best, i - dq.pollFirst());
                while (!dq.isEmpty() && pre[i] <= pre[dq.peekLast()]) dq.pollLast();
                dq.addLast(i);
            }
            return best <= n ? best : -1;
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
        check("Approach 1", new Approach1().shortestSubarray(new int[]{1}, 1), "1");
        check("Approach 1", new Approach1().shortestSubarray(new int[]{1,2}, 4), "-1");
        check("Approach 1", new Approach1().shortestSubarray(new int[]{2,-1,2}, 3), "3");
        check("Approach 1", new Approach1().shortestSubarray(new int[]{84,-37,32,40,95}, 167), "3");
        check("Approach 2", new Approach2().shortestSubarray(new int[]{1}, 1), "1");
        check("Approach 2", new Approach2().shortestSubarray(new int[]{1,2}, 4), "-1");
        check("Approach 2", new Approach2().shortestSubarray(new int[]{2,-1,2}, 3), "3");
        check("Approach 2", new Approach2().shortestSubarray(new int[]{84,-37,32,40,95}, 167), "3");
        System.out.println("ShortestSubarrayWithSumAtLeastK: all 2 approaches passed " + passed + " checks");
    }
}
