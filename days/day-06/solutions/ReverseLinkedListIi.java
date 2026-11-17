import java.util.*;
import java.util.stream.*;

/**
 * Reverse Linked List II (Medium) - Day 6
 * https://leetcode.com/problems/reverse-linked-list-ii/
 *
 * Approach 1: Copy values, reverse the range, write back  |  Time O(n)  |  Space O(n)
 * Approach 2: One pass: move each node to the front of the range (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac ReverseLinkedListIi.java && java ReverseLinkedListIi
 */
public class ReverseLinkedListIi {

    // Approach 1: Copy values, reverse the range, write back
    // Time O(n), Space O(n)
    // Idea: Read values into an array, reverse positions left..right, write them back. Changes values instead of links.
    static class Approach1 {
        public ListNode reverseBetween(ListNode head, int left, int right) {
            List<Integer> v = new ArrayList<>();
            for (ListNode p = head; p != null; p = p.next) v.add(p.val);
            Collections.reverse(v.subList(left - 1, right));
            ListNode p = head;
            for (int x : v) { p.val = x; p = p.next; }
            return head;
        }
    }

    // Approach 2: One pass: move each node to the front of the range (optimal)
    // Time O(n), Space O(1)
    // Idea: With a dummy head, walk to the node before position left. Then right - left times, take the node after the range start and insert it right after that node.
    static class Approach2 {
        public ListNode reverseBetween(ListNode head, int left, int right) {
            ListNode dummy = new ListNode(0, head), before = dummy;
            for (int i = 1; i < left; i++) before = before.next;
            ListNode start = before.next;
            for (int i = 0; i < right - left; i++) {
                ListNode move = start.next;
                start.next = move.next;
                move.next = before.next;
                before.next = move;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseBetween(list(1,2,3,4,5), 2, 4)); check("Approach 1", r, "[1, 4, 3, 2, 5]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseBetween(list(5), 1, 1)); check("Approach 1", r, "[5]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseBetween(list(3,5), 1, 2)); check("Approach 1", r, "[5, 3]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseBetween(list(1,2,3,4,5), 2, 4)); check("Approach 2", r, "[1, 4, 3, 2, 5]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseBetween(list(5), 1, 1)); check("Approach 2", r, "[5]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseBetween(list(3,5), 1, 2)); check("Approach 2", r, "[5, 3]"); }
        System.out.println("ReverseLinkedListIi: all 2 approaches passed " + passed + " checks");
    }
}
