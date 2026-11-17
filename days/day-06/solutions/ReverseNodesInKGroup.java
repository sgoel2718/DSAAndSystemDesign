import java.util.*;
import java.util.stream.*;

/**
 * Reverse Nodes in k-Group (Hard) - Day 6
 * https://leetcode.com/problems/reverse-nodes-in-k-group/
 *
 * Approach 1: Stack per group  |  Time O(n)  |  Space O(k)
 * Approach 2: Recursion  |  Time O(n)  |  Space O(n / k) recursion stack
 * Approach 3: Iterative, group by group (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac ReverseNodesInKGroup.java && java ReverseNodesInKGroup
 */
public class ReverseNodesInKGroup {

    // Approach 1: Stack per group
    // Time O(n), Space O(k)
    // Idea: Push k nodes; if there are k, pop them to relink reversed; a final short group stays as it is.
    static class Approach1 {
        public ListNode reverseKGroup(ListNode head, int k) {
            ListNode dummy = new ListNode(0), tail = dummy, p = head;
            Deque<ListNode> st = new ArrayDeque<>();
            while (p != null) {
                ListNode q = p;
                int c = 0;
                while (q != null && c < k) { st.push(q); q = q.next; c++; }
                if (c < k) { tail.next = p; return dummy.next; }
                while (!st.isEmpty()) { tail.next = st.pop(); tail = tail.next; }
                tail.next = null;
                p = q;
            }
            return dummy.next;
        }
    }

    // Approach 2: Recursion
    // Time O(n), Space O(n / k) recursion stack
    // Idea: Check that k nodes exist; reverse them; their old head becomes the tail and links to the recursively processed rest.
    static class Approach2 {
        public ListNode reverseKGroup(ListNode head, int k) {
            ListNode p = head;
            for (int i = 0; i < k; i++) { if (p == null) return head; p = p.next; }
            ListNode prev = reverseKGroup(p, k), cur = head;
            for (int i = 0; i < k; i++) {
                ListNode nx = cur.next;
                cur.next = prev;
                prev = cur;
                cur = nx;
            }
            return prev;
        }
    }

    // Approach 3: Iterative, group by group (optimal)
    // Time O(n), Space O(1)
    // Idea: groupPrev sits before each group. Find the k-th node; if missing, stop. Reverse the group with its next node as the starting 'prev', then reconnect and move groupPrev to the group's new tail.
    static class Approach3 {
        public ListNode reverseKGroup(ListNode head, int k) {
            ListNode dummy = new ListNode(0, head), groupPrev = dummy;
            while (true) {
                ListNode kth = groupPrev;
                for (int i = 0; i < k && kth != null; i++) kth = kth.next;
                if (kth == null) break;
                ListNode groupNext = kth.next, prev = groupNext, cur = groupPrev.next;
                while (cur != groupNext) {
                    ListNode nx = cur.next;
                    cur.next = prev;
                    prev = cur;
                    cur = nx;
                }
                ListNode newTail = groupPrev.next;
                groupPrev.next = kth;
                groupPrev = newTail;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4,5), 2)); check("Approach 1", r, "[2, 1, 4, 3, 5]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4,5), 3)); check("Approach 1", r, "[3, 2, 1, 4, 5]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseKGroup(list(1,2,3), 1)); check("Approach 1", r, "[1, 2, 3]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4), 4)); check("Approach 1", r, "[4, 3, 2, 1]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4,5), 2)); check("Approach 2", r, "[2, 1, 4, 3, 5]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4,5), 3)); check("Approach 2", r, "[3, 2, 1, 4, 5]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseKGroup(list(1,2,3), 1)); check("Approach 2", r, "[1, 2, 3]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4), 4)); check("Approach 2", r, "[4, 3, 2, 1]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4,5), 2)); check("Approach 3", r, "[2, 1, 4, 3, 5]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4,5), 3)); check("Approach 3", r, "[3, 2, 1, 4, 5]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.reverseKGroup(list(1,2,3), 1)); check("Approach 3", r, "[1, 2, 3]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.reverseKGroup(list(1,2,3,4), 4)); check("Approach 3", r, "[4, 3, 2, 1]"); }
        System.out.println("ReverseNodesInKGroup: all 3 approaches passed " + passed + " checks");
    }
}
