import java.util.*;
import java.util.stream.*;

/**
 * Remove Duplicates from Sorted Array (Easy) - Day 2
 * https://leetcode.com/problems/remove-duplicates-from-sorted-array/
 *
 * Approach 1: LinkedHashSet, then copy back  |  Time O(n)  |  Space O(n)
 * Approach 2: Two pointers: read and write (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac RemoveDuplicatesFromSortedArray.java && java RemoveDuplicatesFromSortedArray
 */
public class RemoveDuplicatesFromSortedArray {

    // Approach 1: LinkedHashSet, then copy back
    // Time O(n), Space O(n)
    // Idea: Collect unique values in order with a LinkedHashSet and write them back to the front.
    static class Approach1 {
        public int removeDuplicates(int[] nums) {
            Set<Integer> uniq = new LinkedHashSet<>();
            for (int x : nums) uniq.add(x);
            int k = 0;
            for (int x : uniq) nums[k++] = x;
            return k;
        }
    }

    // Approach 2: Two pointers: read and write (optimal)
    // Time O(n), Space O(1)
    // Idea: The array is sorted, so a value is new exactly when it differs from the last value written. Copy only those to the write pointer.
    static class Approach2 {
        public int removeDuplicates(int[] nums) {
            if (nums.length == 0) return 0;
            int write = 1;
            for (int read = 1; read < nums.length; read++) {
                if (nums[read] != nums[write - 1]) nums[write++] = nums[read];
            }
            return write;
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
        { Approach1 o = new Approach1(); Object r; int[] a = {1,1,2}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 1", r, "[1, 2]"); }
        { Approach1 o = new Approach1(); Object r; int[] a = {0,0,1,1,1,2,2,3,3,4}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 1", r, "[0, 1, 2, 3, 4]"); }
        { Approach1 o = new Approach1(); Object r; int[] a = {7}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 1", r, "[7]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {1,1,2}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 2", r, "[1, 2]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {0,0,1,1,1,2,2,3,3,4}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 2", r, "[0, 1, 2, 3, 4]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {7}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 2", r, "[7]"); }
        System.out.println("RemoveDuplicatesFromSortedArray: all 2 approaches passed " + passed + " checks");
    }
}
