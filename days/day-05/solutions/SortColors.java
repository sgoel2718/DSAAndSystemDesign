import java.util.*;
import java.util.stream.*;

/**
 * Sort Colors (Medium) - Day 5
 * https://leetcode.com/problems/sort-colors/
 *
 * Approach 1: Library sort  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 2: Counting sort (two passes)  |  Time O(n)  |  Space O(1)
 * Approach 3: Dutch National Flag, one pass (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac SortColors.java && java SortColors
 */
public class SortColors {

    // Approach 1: Library sort
    // Time O(n log n), Space O(log n) sort stack
    // Idea: Just sort the array. Correct, but ignores that there are only three values.
    static class Approach1 {
        public void sortColors(int[] nums) {
            Arrays.sort(nums);
        }
    }

    // Approach 2: Counting sort (two passes)
    // Time O(n), Space O(1)
    // Idea: Count how many 0s, 1s and 2s there are, then overwrite the array in order.
    static class Approach2 {
        public void sortColors(int[] nums) {
            int[] count = new int[3];
            for (int x : nums) count[x]++;
            int i = 0;
            for (int c = 0; c < 3; c++)
                while (count[c]-- > 0) nums[i++] = c;
        }
    }

    // Approach 3: Dutch National Flag, one pass (optimal)
    // Time O(n), Space O(1)
    // Idea: Three pointers: everything before low is 0, everything after high is 2, mid scans. Swap 0s to low and 2s to high; do not advance mid after swapping with high because the swapped-in value is unchecked.
    static class Approach3 {
        public void sortColors(int[] nums) {
            int low = 0, mid = 0, high = nums.length - 1;
            while (mid <= high) {
                if (nums[mid] == 0) {
                    int t = nums[low]; nums[low] = nums[mid]; nums[mid] = t;
                    low++; mid++;
                } else if (nums[mid] == 1) {
                    mid++;
                } else {
                    int t = nums[high]; nums[high] = nums[mid]; nums[mid] = t;
                    high--;
                }
            }
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
        { Approach1 o = new Approach1(); Object r; int[] a = {2,0,2,1,1,0}; o.sortColors(a); r = a; check("Approach 1", r, "[0, 0, 1, 1, 2, 2]"); }
        { Approach1 o = new Approach1(); Object r; int[] a = {2,0,1}; o.sortColors(a); r = a; check("Approach 1", r, "[0, 1, 2]"); }
        { Approach1 o = new Approach1(); Object r; int[] a = {1}; o.sortColors(a); r = a; check("Approach 1", r, "[1]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {2,0,2,1,1,0}; o.sortColors(a); r = a; check("Approach 2", r, "[0, 0, 1, 1, 2, 2]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {2,0,1}; o.sortColors(a); r = a; check("Approach 2", r, "[0, 1, 2]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {1}; o.sortColors(a); r = a; check("Approach 2", r, "[1]"); }
        { Approach3 o = new Approach3(); Object r; int[] a = {2,0,2,1,1,0}; o.sortColors(a); r = a; check("Approach 3", r, "[0, 0, 1, 1, 2, 2]"); }
        { Approach3 o = new Approach3(); Object r; int[] a = {2,0,1}; o.sortColors(a); r = a; check("Approach 3", r, "[0, 1, 2]"); }
        { Approach3 o = new Approach3(); Object r; int[] a = {1}; o.sortColors(a); r = a; check("Approach 3", r, "[1]"); }
        System.out.println("SortColors: all 3 approaches passed " + passed + " checks");
    }
}
