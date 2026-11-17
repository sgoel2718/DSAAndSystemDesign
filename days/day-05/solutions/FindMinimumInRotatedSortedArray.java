import java.util.*;
import java.util.stream.*;

/**
 * Find Minimum in Rotated Sorted Array (Medium) - Day 5
 * https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/
 *
 * Approach 1: Linear scan for the minimum  |  Time O(n)  |  Space O(1)
 * Approach 2: Binary search against the right end (optimal)  |  Time O(log n)  |  Space O(1)  <- best
 *
 * Run: javac FindMinimumInRotatedSortedArray.java && java FindMinimumInRotatedSortedArray
 */
public class FindMinimumInRotatedSortedArray {

    // Approach 1: Linear scan for the minimum
    // Time O(n), Space O(1)
    // Idea: Look at every element.
    static class Approach1 {
        public int findMin(int[] nums) {
            int min = nums[0];
            for (int x : nums) min = Math.min(min, x);
            return min;
        }
    }

    // Approach 2: Binary search against the right end (optimal)
    // Time O(log n), Space O(1)
    // Idea: If nums[mid] > nums[hi], the drop (minimum) is to the right of mid; otherwise the minimum is at mid or to its left.
    static class Approach2 {
        public int findMin(int[] nums) {
            int lo = 0, hi = nums.length - 1;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (nums[mid] > nums[hi]) lo = mid + 1;
                else hi = mid;
            }
            return nums[lo];
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
        check("Approach 1", new Approach1().findMin(new int[]{3,4,5,1,2}), "1");
        check("Approach 1", new Approach1().findMin(new int[]{4,5,6,7,0,1,2}), "0");
        check("Approach 1", new Approach1().findMin(new int[]{11,13,15,17}), "11");
        check("Approach 1", new Approach1().findMin(new int[]{2,1}), "1");
        check("Approach 2", new Approach2().findMin(new int[]{3,4,5,1,2}), "1");
        check("Approach 2", new Approach2().findMin(new int[]{4,5,6,7,0,1,2}), "0");
        check("Approach 2", new Approach2().findMin(new int[]{11,13,15,17}), "11");
        check("Approach 2", new Approach2().findMin(new int[]{2,1}), "1");
        System.out.println("FindMinimumInRotatedSortedArray: all 2 approaches passed " + passed + " checks");
    }
}
