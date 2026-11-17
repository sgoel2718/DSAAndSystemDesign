import java.util.*;
import java.util.stream.*;

/**
 * Peak Index in a Mountain Array (Medium) - Day 5
 * https://leetcode.com/problems/peak-index-in-a-mountain-array/
 *
 * Approach 1: Linear scan  |  Time O(n)  |  Space O(1)
 * Approach 2: Binary search on the slope (optimal)  |  Time O(log n)  |  Space O(1)  <- best
 *
 * Run: javac PeakIndexInAMountainArray.java && java PeakIndexInAMountainArray
 */
public class PeakIndexInAMountainArray {

    // Approach 1: Linear scan
    // Time O(n), Space O(1)
    // Idea: The peak is the first index whose next value is smaller.
    static class Approach1 {
        public int peakIndexInMountainArray(int[] arr) {
            int i = 0;
            while (arr[i] < arr[i + 1]) i++;
            return i;
        }
    }

    // Approach 2: Binary search on the slope (optimal)
    // Time O(log n), Space O(1)
    // Idea: If arr[mid] < arr[mid + 1] we are on the rising side, so the peak is to the right; otherwise it is at mid or to the left.
    static class Approach2 {
        public int peakIndexInMountainArray(int[] arr) {
            int lo = 0, hi = arr.length - 1;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (arr[mid] < arr[mid + 1]) lo = mid + 1;
                else hi = mid;
            }
            return lo;
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
        check("Approach 1", new Approach1().peakIndexInMountainArray(new int[]{0,1,0}), "1");
        check("Approach 1", new Approach1().peakIndexInMountainArray(new int[]{0,2,1,0}), "1");
        check("Approach 1", new Approach1().peakIndexInMountainArray(new int[]{0,10,5,2}), "1");
        check("Approach 1", new Approach1().peakIndexInMountainArray(new int[]{0,1,2,5,3}), "3");
        check("Approach 2", new Approach2().peakIndexInMountainArray(new int[]{0,1,0}), "1");
        check("Approach 2", new Approach2().peakIndexInMountainArray(new int[]{0,2,1,0}), "1");
        check("Approach 2", new Approach2().peakIndexInMountainArray(new int[]{0,10,5,2}), "1");
        check("Approach 2", new Approach2().peakIndexInMountainArray(new int[]{0,1,2,5,3}), "3");
        System.out.println("PeakIndexInAMountainArray: all 2 approaches passed " + passed + " checks");
    }
}
