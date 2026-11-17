import java.util.*;
import java.util.stream.*;

/**
 * Linked List Cycle II (Medium) - Day 6
 * https://leetcode.com/problems/linked-list-cycle-ii/
 *
 * Approach 1: HashSet of visited nodes  |  Time O(n)  |  Space O(n)
 * Approach 2: Floyd: meet, then restart one pointer from head (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac LinkedListCycleIi.java && java LinkedListCycleIi
 */
public class LinkedListCycleIi {

    // Approach 1: HashSet of visited nodes
    // Time O(n), Space O(n)
    // Idea: The first node seen twice is where the cycle starts.
    static class Approach1 {
        public ListNode detectCycle(ListNode head) {
            Set<ListNode> seen = new HashSet<>();
            for (ListNode p = head; p != null; p = p.next) {
                if (!seen.add(p)) return p;
            }
            return null;
        }
    }

    // Approach 2: Floyd: meet, then restart one pointer from head (optimal)
    // Time O(n), Space O(1)
    // Idea: After slow and fast meet, the distance from head to the cycle start equals the distance from the meeting point to the start (mod cycle length). Move one pointer from head and one from the meeting point, one step each; they meet at the start.
    static class Approach2 {
        public ListNode detectCycle(ListNode head) {
            ListNode slow = head, fast = head;
            while (fast != null && fast.next != null) {
                slow = slow.next;
                fast = fast.next.next;
                if (slow == fast) {
                    ListNode p = head;
                    while (p != slow) { p = p.next; slow = slow.next; }
                    return p;
                }
            }
            return null;
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
        { Approach1 o = new Approach1(); Object r; ListNode x = o.detectCycle(cyclic(new int[]{3,2,0,-4}, 1)); r = x == null ? null : x.val; check("Approach 1", r, "2"); }
        { Approach1 o = new Approach1(); Object r; ListNode x = o.detectCycle(cyclic(new int[]{1,2}, 0)); r = x == null ? null : x.val; check("Approach 1", r, "1"); }
        { Approach1 o = new Approach1(); Object r; ListNode x = o.detectCycle(cyclic(new int[]{1}, -1)); r = x == null ? null : x.val; check("Approach 1", r, "null"); }
        { Approach2 o = new Approach2(); Object r; ListNode x = o.detectCycle(cyclic(new int[]{3,2,0,-4}, 1)); r = x == null ? null : x.val; check("Approach 2", r, "2"); }
        { Approach2 o = new Approach2(); Object r; ListNode x = o.detectCycle(cyclic(new int[]{1,2}, 0)); r = x == null ? null : x.val; check("Approach 2", r, "1"); }
        { Approach2 o = new Approach2(); Object r; ListNode x = o.detectCycle(cyclic(new int[]{1}, -1)); r = x == null ? null : x.val; check("Approach 2", r, "null"); }
        System.out.println("LinkedListCycleIi: all 2 approaches passed " + passed + " checks");
    }
}
