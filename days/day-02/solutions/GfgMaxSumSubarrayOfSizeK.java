import java.util.*;
import java.util.stream.*;

/**
 * Max Sum Subarray of Size K (Easy) - Day 2
 * https://leetcode.com/problems/gfg-max-sum-subarray-of-size-k/
 *
 * Approach 1: Brute force: sum every window  |  Time O(n x k)  |  Space O(1)
 * Approach 2: Prefix sums  |  Time O(n)  |  Space O(n)
 * Approach 3: Fixed sliding window (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac GfgMaxSumSubarrayOfSizeK.java && java GfgMaxSumSubarrayOfSizeK
 */
public class GfgMaxSumSubarrayOfSizeK {

    // Approach 1: Brute force: sum every window
    // Time O(n x k), Space O(1)
    // Idea: For each start, add the next k numbers.
    static class Approach1 {
        public long maximumSumSubarray(int[] arr, int k) {
            long best = Long.MIN_VALUE;
            for (int i = 0; i + k <= arr.length; i++) {
                long s = 0;
                for (int j = i; j < i + k; j++) s += arr[j];
                best = Math.max(best, s);
            }
            return best;
        }
    }

    // Approach 2: Prefix sums
    // Time O(n), Space O(n)
    // Idea: Window sum = pre[i + k] - pre[i], each in O(1) after an O(n) build.
    static class Approach2 {
        public long maximumSumSubarray(int[] arr, int k) {
            long[] pre = new long[arr.length + 1];
            for (int i = 0; i < arr.length; i++) pre[i + 1] = pre[i] + arr[i];
            long best = Long.MIN_VALUE;
            for (int i = 0; i + k <= arr.length; i++) best = Math.max(best, pre[i + k] - pre[i]);
            return best;
        }
    }

    // Approach 3: Fixed sliding window (optimal)
    // Time O(n), Space O(1)
    // Idea: Add the element entering on the right and subtract the one leaving on the left.
    static class Approach3 {
        public long maximumSumSubarray(int[] arr, int k) {
            long sum = 0, best;
            for (int i = 0; i < k; i++) sum += arr[i];
            best = sum;
            for (int r = k; r < arr.length; r++) {
                sum += arr[r] - arr[r - k];
                best = Math.max(best, sum);
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
        check("Approach 1", new Approach1().maximumSumSubarray(new int[]{100,200,300,400}, 2), "700");
        check("Approach 1", new Approach1().maximumSumSubarray(new int[]{1,4,2,10,23,3,1,0,20}, 4), "39");
        check("Approach 1", new Approach1().maximumSumSubarray(new int[]{-3,-1,-2}, 1), "-1");
        check("Approach 2", new Approach2().maximumSumSubarray(new int[]{100,200,300,400}, 2), "700");
        check("Approach 2", new Approach2().maximumSumSubarray(new int[]{1,4,2,10,23,3,1,0,20}, 4), "39");
        check("Approach 2", new Approach2().maximumSumSubarray(new int[]{-3,-1,-2}, 1), "-1");
        check("Approach 3", new Approach3().maximumSumSubarray(new int[]{100,200,300,400}, 2), "700");
        check("Approach 3", new Approach3().maximumSumSubarray(new int[]{1,4,2,10,23,3,1,0,20}, 4), "39");
        check("Approach 3", new Approach3().maximumSumSubarray(new int[]{-3,-1,-2}, 1), "-1");
        System.out.println("GfgMaxSumSubarrayOfSizeK: all 3 approaches passed " + passed + " checks");
    }
}
