import java.util.*;
import java.util.stream.*;

/**
 * Reorder List (Medium) - Day 6
 * https://leetcode.com/problems/reorder-list/
 *
 * Approach 1: Copy nodes into an array, relink with two pointers  |  Time O(n)  |  Space O(n)
 * Approach 2: Middle + reverse second half + merge (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac ReorderList.java && java ReorderList
 */
public class ReorderList {

    // Approach 1: Copy nodes into an array, relink with two pointers
    // Time O(n), Space O(n)
    // Idea: Store nodes in a list, then link first, last, second, second-last, ... and terminate the end.
    static class Approach1 {
        public void reorderList(ListNode head) {
            List<ListNode> a = new ArrayList<>();
            for (ListNode p = head; p != null; p = p.next) a.add(p);
            int l = 0, r = a.size() - 1;
            while (l < r) {
                a.get(l).next = a.get(r);
                l++;
                if (l == r) break;
                a.get(r).next = a.get(l);
                r--;
            }
            if (!a.isEmpty()) a.get(l).next = null;
        }
    }

    // Approach 2: Middle + reverse second half + merge (optimal)
    // Time O(n), Space O(1)
    // Idea: Three Day-6 tools in one: fast/slow to split, in-place reversal of the second half, then weave the two halves together.
    static class Approach2 {
        public void reorderList(ListNode head) {
            if (head == null || head.next == null) return;
            ListNode slow = head, fast = head;
            while (fast.next != null && fast.next.next != null) { slow = slow.next; fast = fast.next.next; }
            ListNode second = null, cur = slow.next;
            slow.next = null;
            while (cur != null) { ListNode nx = cur.next; cur.next = second; second = cur; cur = nx; }
            ListNode first = head;
            while (second != null) {
                ListNode n1 = first.next, n2 = second.next;
                first.next = second;
                second.next = n1;
                first = n1;
                second = n2;
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
        { Approach1 o = new Approach1(); Object r; ListNode h = list(1,2,3,4); o.reorderList(h); r = toList(h); check("Approach 1", r, "[1, 4, 2, 3]"); }
        { Approach1 o = new Approach1(); Object r; ListNode h = list(1,2,3,4,5); o.reorderList(h); r = toList(h); check("Approach 1", r, "[1, 5, 2, 4, 3]"); }
        { Approach1 o = new Approach1(); Object r; ListNode h = list(1); o.reorderList(h); r = toList(h); check("Approach 1", r, "[1]"); }
        { Approach2 o = new Approach2(); Object r; ListNode h = list(1,2,3,4); o.reorderList(h); r = toList(h); check("Approach 2", r, "[1, 4, 2, 3]"); }
        { Approach2 o = new Approach2(); Object r; ListNode h = list(1,2,3,4,5); o.reorderList(h); r = toList(h); check("Approach 2", r, "[1, 5, 2, 4, 3]"); }
        { Approach2 o = new Approach2(); Object r; ListNode h = list(1); o.reorderList(h); r = toList(h); check("Approach 2", r, "[1]"); }
        System.out.println("ReorderList: all 2 approaches passed " + passed + " checks");
    }
}
