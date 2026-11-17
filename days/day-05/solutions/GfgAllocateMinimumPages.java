import java.util.*;
import java.util.stream.*;

/**
 * Allocate Minimum Pages (Medium) - Day 5
 * https://leetcode.com/problems/gfg-allocate-minimum-pages/
 *
 * Approach 1: Dynamic programming over split points  |  Time O(k x n^2)  |  Space O(k x n)
 * Approach 2: Binary search on the answer (optimal)  |  Time O(n log total)  |  Space O(1)  <- best
 *
 * Run: javac GfgAllocateMinimumPages.java && java GfgAllocateMinimumPages
 */
public class GfgAllocateMinimumPages {

    // Approach 1: Dynamic programming over split points
    // Time O(k x n^2), Space O(k x n)
    // Idea: dp[j][i] = smallest possible maximum when the first i books go to j students. Try every position for the last student's first book.
    static class Approach1 {
        public int findPages(int[] arr, int k) {
            int n = arr.length;
            if (k > n) return -1;
            long[] pre = new long[n + 1];
            for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + arr[i];
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
    // Time O(n log total), Space O(1)
    // Idea: For a page limit L, give books to a student until the next book would exceed L. If that needs <= k students, L works. Binary search L in [max book, total].
    static class Approach2 {
        public int findPages(int[] arr, int k) {
            if (k > arr.length) return -1;
            long lo = 0, hi = 0;
            for (int x : arr) { lo = Math.max(lo, x); hi += x; }
            while (lo < hi) {
                long mid = lo + (hi - lo) / 2;
                if (studentsNeeded(arr, mid) <= k) hi = mid;
                else lo = mid + 1;
            }
            return (int) lo;
        }
        private int studentsNeeded(int[] a, long limit) {
            int s = 1;
            long pages = 0;
            for (int x : a) {
                if (pages + x > limit) { s++; pages = 0; }
                pages += x;
            }
            return s;
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
        check("Approach 1", new Approach1().findPages(new int[]{12,34,67,90}, 2), "113");
        check("Approach 1", new Approach1().findPages(new int[]{15,17,20}, 5), "-1");
        check("Approach 1", new Approach1().findPages(new int[]{22,23,67}, 1), "112");
        check("Approach 2", new Approach2().findPages(new int[]{12,34,67,90}, 2), "113");
        check("Approach 2", new Approach2().findPages(new int[]{15,17,20}, 5), "-1");
        check("Approach 2", new Approach2().findPages(new int[]{22,23,67}, 1), "112");
        System.out.println("GfgAllocateMinimumPages: all 2 approaches passed " + passed + " checks");
    }
}
