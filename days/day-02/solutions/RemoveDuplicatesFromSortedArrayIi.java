import java.util.*;
import java.util.stream.*;

/**
 * Remove Duplicates from Sorted Array II (Medium) - Day 2
 * https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/
 *
 * Approach 1: Count occurrences, write at most two  |  Time O(n log n)  |  Space O(n)
 * Approach 2: Two pointers: compare with the element two places back (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac RemoveDuplicatesFromSortedArrayIi.java && java RemoveDuplicatesFromSortedArrayIi
 */
public class RemoveDuplicatesFromSortedArrayIi {

    // Approach 1: Count occurrences, write at most two
    // Time O(n log n), Space O(n)
    // Idea: Count each value with a TreeMap (keeps sorted order), then write each value min(count, 2) times.
    static class Approach1 {
        public int removeDuplicates(int[] nums) {
            Map<Integer, Integer> count = new TreeMap<>();
            for (int x : nums) count.merge(x, 1, Integer::sum);
            int k = 0;
            for (Map.Entry<Integer, Integer> e : count.entrySet())
                for (int c = 0; c < Math.min(2, e.getValue()); c++) nums[k++] = e.getKey();
            return k;
        }
    }

    // Approach 2: Two pointers: compare with the element two places back (optimal)
    // Time O(n), Space O(1)
    // Idea: A value may be written if it differs from the value written two slots earlier; that allows at most two copies. Generalises to 'at most k'.
    static class Approach2 {
        public int removeDuplicates(int[] nums) {
            int write = 0;
            for (int x : nums) {
                if (write < 2 || x != nums[write - 2]) nums[write++] = x;
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
        { Approach1 o = new Approach1(); Object r; int[] a = {1,1,1,2,2,3}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 1", r, "[1, 1, 2, 2, 3]"); }
        { Approach1 o = new Approach1(); Object r; int[] a = {0,0,1,1,1,1,2,3,3}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 1", r, "[0, 0, 1, 1, 2, 3, 3]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {1,1,1,2,2,3}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 2", r, "[1, 1, 2, 2, 3]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {0,0,1,1,1,1,2,3,3}; int n = o.removeDuplicates(a); r = Arrays.toString(Arrays.copyOf(a, n)); check("Approach 2", r, "[0, 0, 1, 1, 2, 3, 3]"); }
        System.out.println("RemoveDuplicatesFromSortedArrayIi: all 2 approaches passed " + passed + " checks");
    }
}
