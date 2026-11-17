import java.util.*;
import java.util.stream.*;

/**
 * Middle of the Linked List (Easy) - Day 6
 * https://leetcode.com/problems/middle-of-the-linked-list/
 *
 * Approach 1: Copy nodes into an array  |  Time O(n)  |  Space O(n)
 * Approach 2: Count, then walk half way  |  Time O(n)  |  Space O(1)
 * Approach 3: Fast & slow pointers (optimal, one pass)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MiddleOfTheLinkedList.java && java MiddleOfTheLinkedList
 */
public class MiddleOfTheLinkedList {

    // Approach 1: Copy nodes into an array
    // Time O(n), Space O(n)
    // Idea: Store every node in a list and return the one at index size / 2.
    static class Approach1 {
        public ListNode middleNode(ListNode head) {
            List<ListNode> nodes = new ArrayList<>();
            for (ListNode p = head; p != null; p = p.next) nodes.add(p);
            return nodes.get(nodes.size() / 2);
        }
    }

    // Approach 2: Count, then walk half way
    // Time O(n), Space O(1)
    // Idea: First pass counts n; second pass walks n / 2 steps.
    static class Approach2 {
        public ListNode middleNode(ListNode head) {
            int n = 0;
            for (ListNode p = head; p != null; p = p.next) n++;
            ListNode p = head;
            for (int i = 0; i < n / 2; i++) p = p.next;
            return p;
        }
    }

    // Approach 3: Fast & slow pointers (optimal, one pass)
    // Time O(n), Space O(1)
    // Idea: When fast reaches the end, slow has moved half as far. For even length this returns the second middle, as the problem asks.
    static class Approach3 {
        public ListNode middleNode(ListNode head) {
            ListNode slow = head, fast = head;
            while (fast != null && fast.next != null) {
                slow = slow.next;
                fast = fast.next.next;
            }
            return slow;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.middleNode(list(1,2,3,4,5))); check("Approach 1", r, "[3, 4, 5]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.middleNode(list(1,2,3,4,5,6))); check("Approach 1", r, "[4, 5, 6]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.middleNode(list(1))); check("Approach 1", r, "[1]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.middleNode(list(1,2,3,4,5))); check("Approach 2", r, "[3, 4, 5]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.middleNode(list(1,2,3,4,5,6))); check("Approach 2", r, "[4, 5, 6]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.middleNode(list(1))); check("Approach 2", r, "[1]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.middleNode(list(1,2,3,4,5))); check("Approach 3", r, "[3, 4, 5]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.middleNode(list(1,2,3,4,5,6))); check("Approach 3", r, "[4, 5, 6]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.middleNode(list(1))); check("Approach 3", r, "[1]"); }
        System.out.println("MiddleOfTheLinkedList: all 3 approaches passed " + passed + " checks");
    }
}
