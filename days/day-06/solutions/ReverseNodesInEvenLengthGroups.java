import java.util.*;
import java.util.stream.*;

/**
 * Reverse Nodes in Even Length Groups (Medium) - Day 6
 * https://leetcode.com/problems/reverse-nodes-in-even-length-groups/
 *
 * Approach 1: Copy values, reverse even-length groups, write back  |  Time O(n)  |  Space O(n)
 * Approach 2: Walk group by group, reverse links in place (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac ReverseNodesInEvenLengthGroups.java && java ReverseNodesInEvenLengthGroups
 */
public class ReverseNodesInEvenLengthGroups {

    // Approach 1: Copy values, reverse even-length groups, write back
    // Time O(n), Space O(n)
    // Idea: Groups have sizes 1, 2, 3, ... (the last may be shorter). Reverse the values of every group whose actual length is even.
    static class Approach1 {
        public ListNode reverseEvenLengthGroups(ListNode head) {
            List<Integer> v = new ArrayList<>();
            for (ListNode p = head; p != null; p = p.next) v.add(p.val);
            int start = 0, size = 1, n = v.size();
            while (start < n) {
                int len = Math.min(size, n - start);
                if (len % 2 == 0) Collections.reverse(v.subList(start, start + len));
                start += len;
                size++;
            }
            ListNode p = head;
            for (int x : v) { p.val = x; p = p.next; }
            return head;
        }
    }

    // Approach 2: Walk group by group, reverse links in place (optimal)
    // Time O(n), Space O(1)
    // Idea: prev is the node before the group. Count the group's real length; if even, reverse exactly that many nodes and reconnect; otherwise just skip them.
    static class Approach2 {
        public ListNode reverseEvenLengthGroups(ListNode head) {
            ListNode prev = head;
            int size = 2;
            while (prev.next != null) {
                int cnt = 0;
                ListNode after = prev.next;
                while (cnt < size && after != null) { cnt++; after = after.next; }
                if (cnt % 2 == 0) {
                    ListNode cur = prev.next, groupTail = cur, pr = after;
                    for (int i = 0; i < cnt; i++) {
                        ListNode nx = cur.next;
                        cur.next = pr;
                        pr = cur;
                        cur = nx;
                    }
                    prev.next = pr;
                    prev = groupTail;
                } else {
                    for (int i = 0; i < cnt; i++) prev = prev.next;
                }
                size++;
            }
            return head;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseEvenLengthGroups(list(5,2,6,3,9,1,7,3,8,4))); check("Approach 1", r, "[5, 6, 2, 3, 9, 1, 4, 8, 3, 7]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseEvenLengthGroups(list(1,1,0,6))); check("Approach 1", r, "[1, 0, 1, 6]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseEvenLengthGroups(list(1,1,0,6,5))); check("Approach 1", r, "[1, 0, 1, 5, 6]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.reverseEvenLengthGroups(list(2))); check("Approach 1", r, "[2]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseEvenLengthGroups(list(5,2,6,3,9,1,7,3,8,4))); check("Approach 2", r, "[5, 6, 2, 3, 9, 1, 4, 8, 3, 7]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseEvenLengthGroups(list(1,1,0,6))); check("Approach 2", r, "[1, 0, 1, 6]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseEvenLengthGroups(list(1,1,0,6,5))); check("Approach 2", r, "[1, 0, 1, 5, 6]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.reverseEvenLengthGroups(list(2))); check("Approach 2", r, "[2]"); }
        System.out.println("ReverseNodesInEvenLengthGroups: all 2 approaches passed " + passed + " checks");
    }
}
