import java.util.*;
import java.util.stream.*;

/**
 * Binary Search (Easy) - Day 5
 * https://leetcode.com/problems/binary-search/
 *
 * Approach 1: Linear scan  |  Time O(n)  |  Space O(1)
 * Approach 2: Recursive binary search  |  Time O(log n)  |  Space O(log n) recursion stack
 * Approach 3: Iterative binary search (optimal)  |  Time O(log n)  |  Space O(1)  <- best
 *
 * Run: javac BinarySearch.java && java BinarySearch
 */
public class BinarySearch {

    // Approach 1: Linear scan
    // Time O(n), Space O(1)
    // Idea: Check every element. Ignores that the array is sorted.
    static class Approach1 {
        public int search(int[] nums, int target) {
            for (int i = 0; i < nums.length; i++) if (nums[i] == target) return i;
            return -1;
        }
    }

    // Approach 2: Recursive binary search
    // Time O(log n), Space O(log n) recursion stack
    // Idea: Compare with the middle element and recurse into the half that can still contain the target.
    static class Approach2 {
        public int search(int[] nums, int target) {
            return go(nums, target, 0, nums.length - 1);
        }
        private int go(int[] a, int t, int lo, int hi) {
            if (lo > hi) return -1;
            int mid = lo + (hi - lo) / 2;
            if (a[mid] == t) return mid;
            return a[mid] < t ? go(a, t, mid + 1, hi) : go(a, t, lo, mid - 1);
        }
    }

    // Approach 3: Iterative binary search (optimal)
    // Time O(log n), Space O(1)
    // Idea: Keep [lo, hi] as the range that may contain the target; halve it each step. mid = lo + (hi - lo) / 2 avoids overflow.
    static class Approach3 {
        public int search(int[] nums, int target) {
            int lo = 0, hi = nums.length - 1;
            while (lo <= hi) {
                int mid = lo + (hi - lo) / 2;
                if (nums[mid] == target) return mid;
                if (nums[mid] < target) lo = mid + 1;
                else hi = mid - 1;
            }
            return -1;
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
        check("Approach 1", new Approach1().search(new int[]{-1,0,3,5,9,12}, 9), "4");
        check("Approach 1", new Approach1().search(new int[]{-1,0,3,5,9,12}, 2), "-1");
        check("Approach 1", new Approach1().search(new int[]{5}, 5), "0");
        check("Approach 2", new Approach2().search(new int[]{-1,0,3,5,9,12}, 9), "4");
        check("Approach 2", new Approach2().search(new int[]{-1,0,3,5,9,12}, 2), "-1");
        check("Approach 2", new Approach2().search(new int[]{5}, 5), "0");
        check("Approach 3", new Approach3().search(new int[]{-1,0,3,5,9,12}, 9), "4");
        check("Approach 3", new Approach3().search(new int[]{-1,0,3,5,9,12}, 2), "-1");
        check("Approach 3", new Approach3().search(new int[]{5}, 5), "0");
        System.out.println("BinarySearch: all 3 approaches passed " + passed + " checks");
    }
}
