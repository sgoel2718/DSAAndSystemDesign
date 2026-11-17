import java.util.*;
import java.util.stream.*;

/**
 * Find All Duplicates in an Array (Medium) - Day 2
 * https://leetcode.com/problems/find-all-duplicates-in-an-array/
 *
 * Approach 1: Sort and compare neighbours  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 2: HashSet  |  Time O(n)  |  Space O(n)
 * Approach 3: Cyclic sort  |  Time O(n)  |  Space O(1) besides output
 * Approach 4: Mark visits by negating (optimal)  |  Time O(n)  |  Space O(1) besides output  <- best
 *
 * Run: javac FindAllDuplicatesInAnArray.java && java FindAllDuplicatesInAnArray
 */
public class FindAllDuplicatesInAnArray {

    // Approach 1: Sort and compare neighbours
    // Time O(n log n), Space O(log n) sort stack
    // Idea: Duplicates sit next to each other after sorting.
    static class Approach1 {
        public List<Integer> findDuplicates(int[] nums) {
            Arrays.sort(nums);
            List<Integer> out = new ArrayList<>();
            for (int i = 1; i < nums.length; i++) if (nums[i] == nums[i - 1]) out.add(nums[i]);
            return out;
        }
    }

    // Approach 2: HashSet
    // Time O(n), Space O(n)
    // Idea: add() returns false the second time a value appears.
    static class Approach2 {
        public List<Integer> findDuplicates(int[] nums) {
            Set<Integer> seen = new HashSet<>();
            List<Integer> out = new ArrayList<>();
            for (int x : nums) if (!seen.add(x)) out.add(x);
            return out;
        }
    }

    // Approach 3: Cyclic sort
    // Time O(n), Space O(1) besides output
    // Idea: Swap each value v to index v-1. Afterwards, any index i not holding i+1 holds a duplicate.
    static class Approach3 {
        public List<Integer> findDuplicates(int[] nums) {
            int i = 0;
            while (i < nums.length) {
                int home = nums[i] - 1;
                if (nums[i] != nums[home]) { int t = nums[i]; nums[i] = nums[home]; nums[home] = t; }
                else i++;
            }
            List<Integer> out = new ArrayList<>();
            for (i = 0; i < nums.length; i++) if (nums[i] != i + 1) out.add(nums[i]);
            return out;
        }
    }

    // Approach 4: Mark visits by negating (optimal)
    // Time O(n), Space O(1) besides output
    // Idea: Values are 1..n, so value v points at index v-1. Flip that cell negative on the first visit; if it is already negative, v is a duplicate.
    static class Approach4 {
        public List<Integer> findDuplicates(int[] nums) {
            List<Integer> out = new ArrayList<>();
            for (int x : nums) {
                int idx = Math.abs(x) - 1;
                if (nums[idx] < 0) out.add(Math.abs(x));
                else nums[idx] = -nums[idx];
            }
            return out;
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
        { Approach1 o = new Approach1(); Object r; r = sorted(o.findDuplicates(new int[]{4,3,2,7,8,2,3,1})); check("Approach 1", r, "[2, 3]"); }
        { Approach1 o = new Approach1(); Object r; r = sorted(o.findDuplicates(new int[]{1,1,2})); check("Approach 1", r, "[1]"); }
        { Approach1 o = new Approach1(); Object r; r = sorted(o.findDuplicates(new int[]{1})); check("Approach 1", r, "[]"); }
        { Approach2 o = new Approach2(); Object r; r = sorted(o.findDuplicates(new int[]{4,3,2,7,8,2,3,1})); check("Approach 2", r, "[2, 3]"); }
        { Approach2 o = new Approach2(); Object r; r = sorted(o.findDuplicates(new int[]{1,1,2})); check("Approach 2", r, "[1]"); }
        { Approach2 o = new Approach2(); Object r; r = sorted(o.findDuplicates(new int[]{1})); check("Approach 2", r, "[]"); }
        { Approach3 o = new Approach3(); Object r; r = sorted(o.findDuplicates(new int[]{4,3,2,7,8,2,3,1})); check("Approach 3", r, "[2, 3]"); }
        { Approach3 o = new Approach3(); Object r; r = sorted(o.findDuplicates(new int[]{1,1,2})); check("Approach 3", r, "[1]"); }
        { Approach3 o = new Approach3(); Object r; r = sorted(o.findDuplicates(new int[]{1})); check("Approach 3", r, "[]"); }
        { Approach4 o = new Approach4(); Object r; r = sorted(o.findDuplicates(new int[]{4,3,2,7,8,2,3,1})); check("Approach 4", r, "[2, 3]"); }
        { Approach4 o = new Approach4(); Object r; r = sorted(o.findDuplicates(new int[]{1,1,2})); check("Approach 4", r, "[1]"); }
        { Approach4 o = new Approach4(); Object r; r = sorted(o.findDuplicates(new int[]{1})); check("Approach 4", r, "[]"); }
        System.out.println("FindAllDuplicatesInAnArray: all 4 approaches passed " + passed + " checks");
    }
}
