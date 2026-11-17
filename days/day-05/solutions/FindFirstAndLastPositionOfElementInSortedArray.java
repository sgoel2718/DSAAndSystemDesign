import java.util.*;
import java.util.stream.*;

/**
 * Find First and Last Position of Element in Sorted Array (Medium) - Day 5
 * https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/
 *
 * Approach 1: Linear scan  |  Time O(n)  |  Space O(1)
 * Approach 2: Binary search once, then expand  |  Time O(log n + k)  |  Space O(1)
 * Approach 3: Two lower-bound searches (optimal)  |  Time O(log n)  |  Space O(1)  <- best
 *
 * Run: javac FindFirstAndLastPositionOfElementInSortedArray.java && java FindFirstAndLastPositionOfElementInSortedArray
 */
public class FindFirstAndLastPositionOfElementInSortedArray {

    // Approach 1: Linear scan
    // Time O(n), Space O(1)
    // Idea: Record the first and last index where the value equals the target.
    static class Approach1 {
        public int[] searchRange(int[] nums, int target) {
            int first = -1, last = -1;
            for (int i = 0; i < nums.length; i++)
                if (nums[i] == target) { if (first == -1) first = i; last = i; }
            return new int[]{first, last};
        }
    }

    // Approach 2: Binary search once, then expand
    // Time O(log n + k), Space O(1)
    // Idea: Find any occurrence with binary search, then walk left and right. Degrades to O(n) when the target repeats many times.
    static class Approach2 {
        public int[] searchRange(int[] nums, int target) {
            int lo = 0, hi = nums.length - 1, at = -1;
            while (lo <= hi) {
                int mid = lo + (hi - lo) / 2;
                if (nums[mid] == target) { at = mid; break; }
                if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;
            }
            if (at == -1) return new int[]{-1, -1};
            int l = at, r = at;
            while (l > 0 && nums[l - 1] == target) l--;
            while (r < nums.length - 1 && nums[r + 1] == target) r++;
            return new int[]{l, r};
        }
    }

    // Approach 3: Two lower-bound searches (optimal)
    // Time O(log n), Space O(1)
    // Idea: first = lowerBound(target); last = lowerBound(target + 1) - 1. If first is out of range or not the target, it is absent.
    static class Approach3 {
        public int[] searchRange(int[] nums, int target) {
            int first = lowerBound(nums, target);
            if (first == nums.length || nums[first] != target) return new int[]{-1, -1};
            return new int[]{first, lowerBound(nums, target + 1) - 1};
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
        check("Approach 1", new Approach1().searchRange(new int[]{5,7,7,8,8,10}, 8), "[3, 4]");
        check("Approach 1", new Approach1().searchRange(new int[]{5,7,7,8,8,10}, 6), "[-1, -1]");
        check("Approach 1", new Approach1().searchRange(new int[]{}, 0), "[-1, -1]");
        check("Approach 1", new Approach1().searchRange(new int[]{2,2}, 2), "[0, 1]");
        check("Approach 2", new Approach2().searchRange(new int[]{5,7,7,8,8,10}, 8), "[3, 4]");
        check("Approach 2", new Approach2().searchRange(new int[]{5,7,7,8,8,10}, 6), "[-1, -1]");
        check("Approach 2", new Approach2().searchRange(new int[]{}, 0), "[-1, -1]");
        check("Approach 2", new Approach2().searchRange(new int[]{2,2}, 2), "[0, 1]");
        check("Approach 3", new Approach3().searchRange(new int[]{5,7,7,8,8,10}, 8), "[3, 4]");
        check("Approach 3", new Approach3().searchRange(new int[]{5,7,7,8,8,10}, 6), "[-1, -1]");
        check("Approach 3", new Approach3().searchRange(new int[]{}, 0), "[-1, -1]");
        check("Approach 3", new Approach3().searchRange(new int[]{2,2}, 2), "[0, 1]");
        System.out.println("FindFirstAndLastPositionOfElementInSortedArray: all 3 approaches passed " + passed + " checks");
    }
}
