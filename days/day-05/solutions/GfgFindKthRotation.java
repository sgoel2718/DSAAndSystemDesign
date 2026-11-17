import java.util.*;
import java.util.stream.*;

/**
 * Find Kth Rotation (rotation count) (Easy) - Day 5
 * https://leetcode.com/problems/gfg-find-kth-rotation/
 *
 * Approach 1: Linear scan for the minimum's index  |  Time O(n)  |  Space O(1)
 * Approach 2: Binary search for the minimum's index (optimal)  |  Time O(log n)  |  Space O(1)  <- best
 *
 * Run: javac GfgFindKthRotation.java && java GfgFindKthRotation
 */
public class GfgFindKthRotation {

    // Approach 1: Linear scan for the minimum's index
    // Time O(n), Space O(1)
    // Idea: The number of rotations equals the index of the smallest element.
    static class Approach1 {
        public int findKRotation(int[] arr) {
            int idx = 0;
            for (int i = 1; i < arr.length; i++) if (arr[i] < arr[idx]) idx = i;
            return idx;
        }
    }

    // Approach 2: Binary search for the minimum's index (optimal)
    // Time O(log n), Space O(1)
    // Idea: Same search as Find Minimum in Rotated Sorted Array, but return the index.
    static class Approach2 {
        public int findKRotation(int[] arr) {
            int lo = 0, hi = arr.length - 1;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (arr[mid] > arr[hi]) lo = mid + 1;
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
        check("Approach 1", new Approach1().findKRotation(new int[]{5,1,2,3,4}), "1");
        check("Approach 1", new Approach1().findKRotation(new int[]{1,2,3,4,5}), "0");
        check("Approach 1", new Approach1().findKRotation(new int[]{15,18,2,3,6,12}), "2");
        check("Approach 2", new Approach2().findKRotation(new int[]{5,1,2,3,4}), "1");
        check("Approach 2", new Approach2().findKRotation(new int[]{1,2,3,4,5}), "0");
        check("Approach 2", new Approach2().findKRotation(new int[]{15,18,2,3,6,12}), "2");
        System.out.println("GfgFindKthRotation: all 2 approaches passed " + passed + " checks");
    }
}
