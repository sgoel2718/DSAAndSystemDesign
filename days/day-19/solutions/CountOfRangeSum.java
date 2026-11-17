import java.util.*;
import java.util.stream.*;

/**
 * Count of Range Sum (Hard) - Day 19
 * https://leetcode.com/problems/count-of-range-sum/
 *
 * Approach 1: Brute force: every subarray with a running sum  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Merge sort on prefix sums (optimal)  |  Time O(n log n)  |  Space O(n)  <- best
 *
 * Run: javac CountOfRangeSum.java && java CountOfRangeSum
 */
public class CountOfRangeSum {

    // Approach 1: Brute force: every subarray with a running sum
    // Time O(n^2), Space O(1)
    // Idea: Count subarray sums inside [lower, upper]. Use long to avoid overflow.
    static class Approach1 {
        public int countRangeSum(int[] nums, int lower, int upper) {
            int count = 0;
            for (int i = 0; i < nums.length; i++) {
                long s = 0;
                for (int j = i; j < nums.length; j++) {
                    s += nums[j];
                    if (s >= lower && s <= upper) count++;
                }
            }
            return count;
        }
    }

    // Approach 2: Merge sort on prefix sums (optimal)
    // Time O(n log n), Space O(n)
    // Idea: Count pairs i < j with lower <= pre[j] - pre[i] <= upper. During merge sort both halves are sorted, so for each i in the left half two moving pointers find the valid j range in the right half.
    static class Approach2 {
        public int countRangeSum(int[] nums, int lower, int upper) {
            long[] pre = new long[nums.length + 1];
            for (int i = 0; i < nums.length; i++) pre[i + 1] = pre[i] + nums[i];
            return sort(pre, 0, pre.length, lower, upper);
        }
        private int sort(long[] p, int lo, int hi, int lower, int upper) {
            if (hi - lo <= 1) return 0;
            int mid = (lo + hi) >>> 1;
            int count = sort(p, lo, mid, lower, upper) + sort(p, mid, hi, lower, upper);
            int a = mid, b = mid;
            for (int i = lo; i < mid; i++) {
                while (a < hi && p[a] - p[i] < lower) a++;
                while (b < hi && p[b] - p[i] <= upper) b++;
                count += b - a;
            }
            long[] t = new long[hi - lo];
            int x = lo, y = mid, k = 0;
            while (x < mid && y < hi) t[k++] = p[x] <= p[y] ? p[x++] : p[y++];
            while (x < mid) t[k++] = p[x++];
            while (y < hi) t[k++] = p[y++];
            System.arraycopy(t, 0, p, lo, t.length);
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
        check("Approach 1", new Approach1().countRangeSum(new int[]{-2,5,-1}, -2, 2), "3");
        check("Approach 1", new Approach1().countRangeSum(new int[]{0}, 0, 0), "1");
        check("Approach 1", new Approach1().countRangeSum(new int[]{-2147483647,0,-2147483647,2147483647}, -564, 3864), "3");
        check("Approach 2", new Approach2().countRangeSum(new int[]{-2,5,-1}, -2, 2), "3");
        check("Approach 2", new Approach2().countRangeSum(new int[]{0}, 0, 0), "1");
        check("Approach 2", new Approach2().countRangeSum(new int[]{-2147483647,0,-2147483647,2147483647}, -564, 3864), "3");
        System.out.println("CountOfRangeSum: all 2 approaches passed " + passed + " checks");
    }
}
