import java.util.*;
import java.util.stream.*;

/**
 * Remove Nodes From Linked List (Medium) - Day 7
 * https://leetcode.com/problems/remove-nodes-from-linked-list/
 *
 * Approach 1: Brute force: check everything to the right  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Monotonic stack  |  Time O(n)  |  Space O(n)
 * Approach 3: Recursion  |  Time O(n)  |  Space O(n) recursion stack
 * Approach 4: Reverse, keep a running maximum, reverse back (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac RemoveNodesFromLinkedList.java && java RemoveNodesFromLinkedList
 */
public class RemoveNodesFromLinkedList {

    // Approach 1: Brute force: check everything to the right
    // Time O(n^2), Space O(1)
    // Idea: Keep a node only if no node after it has a larger value.
    static class Approach1 {
        public ListNode removeNodes(ListNode head) {
            ListNode dummy = new ListNode(0), tail = dummy;
            for (ListNode p = head; p != null; p = p.next) {
                boolean keep = true;
                for (ListNode q = p.next; q != null; q = q.next) if (q.val > p.val) { keep = false; break; }
                if (keep) { tail.next = p; tail = p; }
            }
            tail.next = null;
            return dummy.next;
        }
    }

    // Approach 2: Monotonic stack
    // Time O(n), Space O(n)
    // Idea: Push nodes; before pushing, pop every node smaller than the new one (it has a greater node to its right). The stack, bottom to top, is the answer.
    static class Approach2 {
        public ListNode removeNodes(ListNode head) {
            Deque<ListNode> st = new ArrayDeque<>();
            for (ListNode p = head; p != null; p = p.next) {
                while (!st.isEmpty() && st.peek().val < p.val) st.pop();
                st.push(p);
            }
            ListNode next = null;
            while (!st.isEmpty()) { ListNode cur = st.pop(); cur.next = next; next = cur; }
            return next;
        }
    }

    // Approach 3: Recursion
    // Time O(n), Space O(n) recursion stack
    // Idea: Process the rest first; then keep head only if it is not smaller than the first kept node after it.
    static class Approach3 {
        public ListNode removeNodes(ListNode head) {
            if (head == null) return null;
            head.next = removeNodes(head.next);
            return (head.next != null && head.next.val > head.val) ? head.next : head;
        }
    }

    // Approach 4: Reverse, keep a running maximum, reverse back (optimal)
    // Time O(n), Space O(1)
    // Idea: From the right, a node survives if it is at least the maximum seen so far. Reverse the list to walk it right-to-left, drop smaller nodes, and reverse again.
    static class Approach4 {
        public ListNode removeNodes(ListNode head) {
            head = reverse(head);
            int max = head.val;
            ListNode cur = head;
            while (cur.next != null) {
                if (cur.next.val < max) cur.next = cur.next.next;
                else { cur = cur.next; max = cur.val; }
            }
            return reverse(head);
        }
        private ListNode reverse(ListNode h) {
            ListNode prev = null;
            while (h != null) { ListNode nx = h.next; h.next = prev; prev = h; h = nx; }
            return prev;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.removeNodes(list(5,2,13,3,8))); check("Approach 1", r, "[13, 8]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.removeNodes(list(1,1,1,1))); check("Approach 1", r, "[1, 1, 1, 1]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.removeNodes(list(3,2,1))); check("Approach 1", r, "[3, 2, 1]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.removeNodes(list(5,2,13,3,8))); check("Approach 2", r, "[13, 8]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.removeNodes(list(1,1,1,1))); check("Approach 2", r, "[1, 1, 1, 1]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.removeNodes(list(3,2,1))); check("Approach 2", r, "[3, 2, 1]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.removeNodes(list(5,2,13,3,8))); check("Approach 3", r, "[13, 8]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.removeNodes(list(1,1,1,1))); check("Approach 3", r, "[1, 1, 1, 1]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.removeNodes(list(3,2,1))); check("Approach 3", r, "[3, 2, 1]"); }
        { Approach4 o = new Approach4(); Object r; r = toList(o.removeNodes(list(5,2,13,3,8))); check("Approach 4", r, "[13, 8]"); }
        { Approach4 o = new Approach4(); Object r; r = toList(o.removeNodes(list(1,1,1,1))); check("Approach 4", r, "[1, 1, 1, 1]"); }
        { Approach4 o = new Approach4(); Object r; r = toList(o.removeNodes(list(3,2,1))); check("Approach 4", r, "[3, 2, 1]"); }
        System.out.println("RemoveNodesFromLinkedList: all 4 approaches passed " + passed + " checks");
    }
}
