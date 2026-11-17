import java.util.*;
import java.util.stream.*;

/**
 * Segregate 0s and 1s (Easy) - Day 2
 * https://leetcode.com/problems/gfg-segregate-0s-and-1s/
 *
 * Approach 1: Library sort  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 2: Count the zeros (two passes)  |  Time O(n)  |  Space O(1)
 * Approach 3: Two pointers from both ends (optimal, one pass)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac GfgSegregate0sAnd1s.java && java GfgSegregate0sAnd1s
 */
public class GfgSegregate0sAnd1s {

    // Approach 1: Library sort
    // Time O(n log n), Space O(log n) sort stack
    // Idea: Sorting puts all 0s before 1s.
    static class Approach1 {
        public void segregate0and1(int[] arr) {
            Arrays.sort(arr);
        }
    }

    // Approach 2: Count the zeros (two passes)
    // Time O(n), Space O(1)
    // Idea: Count the 0s, then write that many 0s followed by 1s.
    static class Approach2 {
        public void segregate0and1(int[] arr) {
            int zeros = 0;
            for (int x : arr) if (x == 0) zeros++;
            for (int i = 0; i < arr.length; i++) arr[i] = i < zeros ? 0 : 1;
        }
    }

    // Approach 3: Two pointers from both ends (optimal, one pass)
    // Time O(n), Space O(1)
    // Idea: Move l right past 0s and r left past 1s; when l sees a 1 and r sees a 0, swap them.
    static class Approach3 {
        public void segregate0and1(int[] arr) {
            int l = 0, r = arr.length - 1;
            while (l < r) {
                if (arr[l] == 0) l++;
                else if (arr[r] == 1) r--;
                else { arr[l] = 0; arr[r] = 1; l++; r--; }
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
        { Approach1 o = new Approach1(); Object r; int[] a = {0,0,1,1,0}; o.segregate0and1(a); r = a; check("Approach 1", r, "[0, 0, 0, 1, 1]"); }
        { Approach1 o = new Approach1(); Object r; int[] a = {1,1,1,1}; o.segregate0and1(a); r = a; check("Approach 1", r, "[1, 1, 1, 1]"); }
        { Approach1 o = new Approach1(); Object r; int[] a = {1,0,1,0,1,0}; o.segregate0and1(a); r = a; check("Approach 1", r, "[0, 0, 0, 1, 1, 1]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {0,0,1,1,0}; o.segregate0and1(a); r = a; check("Approach 2", r, "[0, 0, 0, 1, 1]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {1,1,1,1}; o.segregate0and1(a); r = a; check("Approach 2", r, "[1, 1, 1, 1]"); }
        { Approach2 o = new Approach2(); Object r; int[] a = {1,0,1,0,1,0}; o.segregate0and1(a); r = a; check("Approach 2", r, "[0, 0, 0, 1, 1, 1]"); }
        { Approach3 o = new Approach3(); Object r; int[] a = {0,0,1,1,0}; o.segregate0and1(a); r = a; check("Approach 3", r, "[0, 0, 0, 1, 1]"); }
        { Approach3 o = new Approach3(); Object r; int[] a = {1,1,1,1}; o.segregate0and1(a); r = a; check("Approach 3", r, "[1, 1, 1, 1]"); }
        { Approach3 o = new Approach3(); Object r; int[] a = {1,0,1,0,1,0}; o.segregate0and1(a); r = a; check("Approach 3", r, "[0, 0, 0, 1, 1, 1]"); }
        System.out.println("GfgSegregate0sAnd1s: all 3 approaches passed " + passed + " checks");
    }
}
