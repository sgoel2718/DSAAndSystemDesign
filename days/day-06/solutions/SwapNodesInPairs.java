import java.util.*;
import java.util.stream.*;

/**
 * Swap Nodes in Pairs (Medium) - Day 6
 * https://leetcode.com/problems/swap-nodes-in-pairs/
 *
 * Approach 1: Swap the values  |  Time O(n)  |  Space O(1)
 * Approach 2: Recursion  |  Time O(n)  |  Space O(n) recursion stack
 * Approach 3: Iterative with a dummy head (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac SwapNodesInPairs.java && java SwapNodesInPairs
 */
public class SwapNodesInPairs {

    // Approach 1: Swap the values
    // Time O(n), Space O(1)
    // Idea: Swap the values of each pair. Simple, but interviewers usually forbid changing values (only links), so mention it and move on.
    static class Approach1 {
        public ListNode swapPairs(ListNode head) {
            for (ListNode p = head; p != null && p.next != null; p = p.next.next) {
                int t = p.val; p.val = p.next.val; p.next.val = t;
            }
            return head;
        }
    }

    // Approach 2: Recursion
    // Time O(n), Space O(n) recursion stack
    // Idea: Swap the first two nodes, and attach the result of swapping the rest.
    static class Approach2 {
        public ListNode swapPairs(ListNode head) {
            if (head == null || head.next == null) return head;
            ListNode second = head.next;
            head.next = swapPairs(second.next);
            second.next = head;
            return second;
        }
    }

    // Approach 3: Iterative with a dummy head (optimal)
    // Time O(n), Space O(1)
    // Idea: prev points to the node before the pair; relink prev -> second -> first -> rest, then move prev to first.
    static class Approach3 {
        public ListNode swapPairs(ListNode head) {
            ListNode dummy = new ListNode(0, head), prev = dummy;
            while (prev.next != null && prev.next.next != null) {
                ListNode a = prev.next, b = a.next;
                a.next = b.next;
                b.next = a;
                prev.next = b;
                prev = a;
            }
            return dummy.next;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.swapPairs(list(1,2,3,4))); check("Approach 1", r, "[2, 1, 4, 3]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.swapPairs(list())); check("Approach 1", r, "[]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.swapPairs(list(1))); check("Approach 1", r, "[1]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.swapPairs(list(1,2,3))); check("Approach 1", r, "[2, 1, 3]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.swapPairs(list(1,2,3,4))); check("Approach 2", r, "[2, 1, 4, 3]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.swapPairs(list())); check("Approach 2", r, "[]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.swapPairs(list(1))); check("Approach 2", r, "[1]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.swapPairs(list(1,2,3))); check("Approach 2", r, "[2, 1, 3]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.swapPairs(list(1,2,3,4))); check("Approach 3", r, "[2, 1, 4, 3]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.swapPairs(list())); check("Approach 3", r, "[]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.swapPairs(list(1))); check("Approach 3", r, "[1]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.swapPairs(list(1,2,3))); check("Approach 3", r, "[2, 1, 3]"); }
        System.out.println("SwapNodesInPairs: all 3 approaches passed " + passed + " checks");
    }
}
