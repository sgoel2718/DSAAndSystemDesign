import java.util.*;
import java.util.stream.*;

/**
 * Number of Occurrence (Easy) - Day 5
 * https://leetcode.com/problems/gfg-number-of-occurrence/
 *
 * Approach 1: Linear count  |  Time O(n)  |  Space O(1)
 * Approach 2: Two binary searches (optimal)  |  Time O(log n)  |  Space O(1)  <- best
 *
 * Run: javac GfgNumberOfOccurrence.java && java GfgNumberOfOccurrence
 */
public class GfgNumberOfOccurrence {

    // Approach 1: Linear count
    // Time O(n), Space O(1)
    // Idea: Count matching elements.
    static class Approach1 {
        public int countFreq(int[] arr, int target) {
            int c = 0;
            for (int x : arr) if (x == target) c++;
            return c;
        }
    }

    // Approach 2: Two binary searches (optimal)
    // Time O(log n), Space O(1)
    // Idea: count = lowerBound(target + 1) - lowerBound(target): the size of the block of equal values.
    static class Approach2 {
        public int countFreq(int[] arr, int target) {
            return lowerBound(arr, target + 1) - lowerBound(arr, target);
        }
        private int lowerBound(int[] a, int x) {
            int lo = 0, hi = a.length;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (a[mid] >= x) hi = mid; else lo = mid + 1;
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
        check("Approach 1", new Approach1().countFreq(new int[]{1,1,2,2,2,2,3}, 2), "4");
        check("Approach 1", new Approach1().countFreq(new int[]{1,1,2,2,2,2,3}, 4), "0");
        check("Approach 1", new Approach1().countFreq(new int[]{8,9,10,12,12,12}, 12), "3");
        check("Approach 2", new Approach2().countFreq(new int[]{1,1,2,2,2,2,3}, 2), "4");
        check("Approach 2", new Approach2().countFreq(new int[]{1,1,2,2,2,2,3}, 4), "0");
        check("Approach 2", new Approach2().countFreq(new int[]{8,9,10,12,12,12}, 12), "3");
        System.out.println("GfgNumberOfOccurrence: all 2 approaches passed " + passed + " checks");
    }
}
