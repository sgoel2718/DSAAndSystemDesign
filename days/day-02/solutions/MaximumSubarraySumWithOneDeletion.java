import java.util.*;
import java.util.stream.*;

/**
 * Maximum Subarray Sum with One Deletion (Medium) - Day 2
 * https://leetcode.com/problems/maximum-subarray-sum-with-one-deletion/
 *
 * Approach 1: Try every deletion, run Kadane each time  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Best ending here + best starting here  |  Time O(n)  |  Space O(n)
 * Approach 3: Two-state Kadane (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MaximumSubarraySumWithOneDeletion.java && java MaximumSubarraySumWithOneDeletion
 */
public class MaximumSubarraySumWithOneDeletion {

    // Approach 1: Try every deletion, run Kadane each time
    // Time O(n^2), Space O(1)
    // Idea: For no deletion and for each index d, run Kadane on the array without d (the result must stay non-empty).
    static class Approach1 {
        public int maximumSum(int[] arr) {
            int best = kadane(arr, -1);
            if (arr.length > 1) for (int d = 0; d < arr.length; d++) best = Math.max(best, kadane(arr, d));
            return best;
        }
        private int kadane(int[] a, int skip) {
            int cur = 0, best = Integer.MIN_VALUE;
            boolean started = false;
            for (int i = 0; i < a.length; i++) {
                if (i == skip) continue;
                cur = started ? Math.max(a[i], cur + a[i]) : a[i];
                started = true;
                best = Math.max(best, cur);
            }
            return best;
        }
    }

    // Approach 2: Best ending here + best starting here
    // Time O(n), Space O(n)
    // Idea: fw[i] = best sum ending at i, bw[i] = best sum starting at i. Deleting i joins fw[i-1] and bw[i+1].
    static class Approach2 {
        public int maximumSum(int[] arr) {
            int n = arr.length;
            int[] fw = new int[n], bw = new int[n];
            fw[0] = arr[0];
            int best = arr[0];
            for (int i = 1; i < n; i++) { fw[i] = Math.max(arr[i], fw[i - 1] + arr[i]); best = Math.max(best, fw[i]); }
            bw[n - 1] = arr[n - 1];
            for (int i = n - 2; i >= 0; i--) bw[i] = Math.max(arr[i], bw[i + 1] + arr[i]);
            for (int i = 1; i < n - 1; i++) best = Math.max(best, fw[i - 1] + bw[i + 1]);
            return best;
        }
    }

    // Approach 3: Two-state Kadane (optimal)
    // Time O(n), Space O(1)
    // Idea: noDel = best sum ending here with no deletion; oneDel = best ending here with one deletion used (either delete this element, or extend an earlier deletion).
    static class Approach3 {
        public int maximumSum(int[] arr) {
            int noDel = arr[0], oneDel = Integer.MIN_VALUE / 2, best = arr[0];
            for (int i = 1; i < arr.length; i++) {
                oneDel = Math.max(oneDel + arr[i], noDel);   // extend a deletion, or delete arr[i]
                noDel = Math.max(noDel + arr[i], arr[i]);
                best = Math.max(best, Math.max(noDel, oneDel));
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
        check("Approach 1", new Approach1().maximumSum(new int[]{1,-2,0,3}), "4");
        check("Approach 1", new Approach1().maximumSum(new int[]{1,-2,-2,3}), "3");
        check("Approach 1", new Approach1().maximumSum(new int[]{-1,-1,-1,-1}), "-1");
        check("Approach 1", new Approach1().maximumSum(new int[]{5}), "5");
        check("Approach 2", new Approach2().maximumSum(new int[]{1,-2,0,3}), "4");
        check("Approach 2", new Approach2().maximumSum(new int[]{1,-2,-2,3}), "3");
        check("Approach 2", new Approach2().maximumSum(new int[]{-1,-1,-1,-1}), "-1");
        check("Approach 2", new Approach2().maximumSum(new int[]{5}), "5");
        check("Approach 3", new Approach3().maximumSum(new int[]{1,-2,0,3}), "4");
        check("Approach 3", new Approach3().maximumSum(new int[]{1,-2,-2,3}), "3");
        check("Approach 3", new Approach3().maximumSum(new int[]{-1,-1,-1,-1}), "-1");
        check("Approach 3", new Approach3().maximumSum(new int[]{5}), "5");
        System.out.println("MaximumSubarraySumWithOneDeletion: all 3 approaches passed " + passed + " checks");
    }
}
