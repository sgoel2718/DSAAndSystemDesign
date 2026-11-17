import java.util.*;
import java.util.stream.*;

/**
 * Linked List Cycle (Easy) - Day 6
 * https://leetcode.com/problems/linked-list-cycle/
 *
 * Approach 1: HashSet of visited nodes  |  Time O(n)  |  Space O(n)
 * Approach 2: Floyd's fast & slow pointers (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac LinkedListCycle.java && java LinkedListCycle
 */
public class LinkedListCycle {

    // Approach 1: HashSet of visited nodes
    // Time O(n), Space O(n)
    // Idea: Walk the list; if a node is seen twice there is a cycle.
    static class Approach1 {
        public boolean hasCycle(ListNode head) {
            Set<ListNode> seen = new HashSet<>();
            for (ListNode p = head; p != null; p = p.next) {
                if (!seen.add(p)) return true;
            }
            return false;
        }
    }

    // Approach 2: Floyd's fast & slow pointers (optimal)
    // Time O(n), Space O(1)
    // Idea: Slow moves 1 step, fast moves 2. In a cycle fast gains one node per step and must land on slow; without a cycle fast reaches null.
    static class Approach2 {
        public boolean hasCycle(ListNode head) {
            ListNode slow = head, fast = head;
            while (fast != null && fast.next != null) {
                slow = slow.next;
                fast = fast.next.next;
                if (slow == fast) return true;
            }
            return false;
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
        { Approach1 o = new Approach1(); Object r; r = o.hasCycle(cyclic(new int[]{3,2,0,-4}, 1)); check("Approach 1", r, "true"); }
        { Approach1 o = new Approach1(); Object r; r = o.hasCycle(cyclic(new int[]{1,2}, 0)); check("Approach 1", r, "true"); }
        { Approach1 o = new Approach1(); Object r; r = o.hasCycle(cyclic(new int[]{1}, -1)); check("Approach 1", r, "false"); }
        { Approach1 o = new Approach1(); Object r; r = o.hasCycle(list()); check("Approach 1", r, "false"); }
        { Approach2 o = new Approach2(); Object r; r = o.hasCycle(cyclic(new int[]{3,2,0,-4}, 1)); check("Approach 2", r, "true"); }
        { Approach2 o = new Approach2(); Object r; r = o.hasCycle(cyclic(new int[]{1,2}, 0)); check("Approach 2", r, "true"); }
        { Approach2 o = new Approach2(); Object r; r = o.hasCycle(cyclic(new int[]{1}, -1)); check("Approach 2", r, "false"); }
        { Approach2 o = new Approach2(); Object r; r = o.hasCycle(list()); check("Approach 2", r, "false"); }
        System.out.println("LinkedListCycle: all 2 approaches passed " + passed + " checks");
    }
}
