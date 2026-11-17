import java.util.*;
import java.util.stream.*;

/**
 * Search in an Infinite Sorted Array (Medium) - Day 5
 * https://leetcode.com/problems/gfg-search-in-infinite-sorted-array/
 *
 * Approach 1: Linear scan until the values pass the target  |  Time O(p) for answer position p  |  Space O(1)
 * Approach 2: Double the window, then binary search (optimal)  |  Time O(log p)  |  Space O(1)  <- best
 *
 * Run: javac GfgSearchInInfiniteSortedArray.java && java GfgSearchInInfiniteSortedArray
 */
public class GfgSearchInInfiniteSortedArray {

    // Approach 1: Linear scan until the values pass the target
    // Time O(p) for answer position p, Space O(1)
    // Idea: We cannot ask for the length, so walk forward until we find the target or pass it. get(i) returns Integer.MAX_VALUE beyond the data, like an infinite array.
    static class Approach1 {
        public int search(int[] arr, int target) {
            for (int i = 0; ; i++) {
                int v = get(arr, i);
                if (v == target) return i;
                if (v > target) return -1;
            }
        }
        private int get(int[] a, int i) { return i < a.length ? a[i] : Integer.MAX_VALUE; }
    }

    // Approach 2: Double the window, then binary search (optimal)
    // Time O(log p), Space O(1)
    // Idea: Grow hi = 1, 2, 4, 8, ... until get(hi) >= target; the target must lie in [hi / 2, hi]. Then run normal binary search there.
    static class Approach2 {
        public int search(int[] arr, int target) {
            int lo = 0, hi = 1;
            while (get(arr, hi) < target) { lo = hi; hi *= 2; }
            while (lo <= hi) {
                int mid = lo + (hi - lo) / 2, v = get(arr, mid);
                if (v == target) return mid;
                if (v < target) lo = mid + 1; else hi = mid - 1;
            }
            return -1;
        }
        private int get(int[] a, int i) { return i < a.length ? a[i] : Integer.MAX_VALUE; }
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
        check("Approach 1", new Approach1().search(new int[]{3,5,7,9,10,90,100,130,140,160,170}, 10), "4");
        check("Approach 1", new Approach1().search(new int[]{3,5,7,9,10,90,100,130,140,160,170}, 170), "10");
        check("Approach 1", new Approach1().search(new int[]{3,5,7,9,10,90,100,130,140,160,170}, 6), "-1");
        check("Approach 2", new Approach2().search(new int[]{3,5,7,9,10,90,100,130,140,160,170}, 10), "4");
        check("Approach 2", new Approach2().search(new int[]{3,5,7,9,10,90,100,130,140,160,170}, 170), "10");
        check("Approach 2", new Approach2().search(new int[]{3,5,7,9,10,90,100,130,140,160,170}, 6), "-1");
        System.out.println("GfgSearchInInfiniteSortedArray: all 2 approaches passed " + passed + " checks");
    }
}
