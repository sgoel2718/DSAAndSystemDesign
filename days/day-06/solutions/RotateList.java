import java.util.*;
import java.util.stream.*;

/**
 * Rotate List (Medium) - Day 6
 * https://leetcode.com/problems/rotate-list/
 *
 * Approach 1: Rotate one step at a time  |  Time O(n x (k mod n))  |  Space O(1)
 * Approach 2: Copy values into an array  |  Time O(n)  |  Space O(n)
 * Approach 3: Close into a ring, cut at the right place (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac RotateList.java && java RotateList
 */
public class RotateList {

    // Approach 1: Rotate one step at a time
    // Time O(n x (k mod n)), Space O(1)
    // Idea: Move the last node to the front, k mod n times.
    static class Approach1 {
        public ListNode rotateRight(ListNode head, int k) {
            if (head == null || head.next == null) return head;
            int n = 0;
            for (ListNode p = head; p != null; p = p.next) n++;
            for (int step = 0; step < k % n; step++) {
                ListNode prev = null, last = head;
                while (last.next != null) { prev = last; last = last.next; }
                prev.next = null;
                last.next = head;
                head = last;
            }
            return head;
        }
    }

    // Approach 2: Copy values into an array
    // Time O(n), Space O(n)
    // Idea: Value at new position (i + k) mod n comes from position i; write the rotated values back.
    static class Approach2 {
        public ListNode rotateRight(ListNode head, int k) {
            List<Integer> v = new ArrayList<>();
            for (ListNode p = head; p != null; p = p.next) v.add(p.val);
            int n = v.size();
            if (n == 0) return head;
            Collections.rotate(v, k % n);
            ListNode p = head;
            for (int x : v) { p.val = x; p = p.next; }
            return head;
        }
    }

    // Approach 3: Close into a ring, cut at the right place (optimal)
    // Time O(n), Space O(1)
    // Idea: Find the length and tail, link tail to head, walk n - k mod n steps to the new tail, and break the ring there.
    static class Approach3 {
        public ListNode rotateRight(ListNode head, int k) {
            if (head == null || head.next == null || k == 0) return head;
            int n = 1;
            ListNode tail = head;
            while (tail.next != null) { tail = tail.next; n++; }
            k %= n;
            if (k == 0) return head;
            tail.next = head;
            ListNode newTail = head;
            for (int i = 1; i < n - k; i++) newTail = newTail.next;
            ListNode newHead = newTail.next;
            newTail.next = null;
            return newHead;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.rotateRight(list(1,2,3,4,5), 2)); check("Approach 1", r, "[4, 5, 1, 2, 3]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.rotateRight(list(0,1,2), 4)); check("Approach 1", r, "[2, 0, 1]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.rotateRight(list(), 0)); check("Approach 1", r, "[]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.rotateRight(list(1,2), 2)); check("Approach 1", r, "[1, 2]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.rotateRight(list(1,2,3,4,5), 2)); check("Approach 2", r, "[4, 5, 1, 2, 3]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.rotateRight(list(0,1,2), 4)); check("Approach 2", r, "[2, 0, 1]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.rotateRight(list(), 0)); check("Approach 2", r, "[]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.rotateRight(list(1,2), 2)); check("Approach 2", r, "[1, 2]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.rotateRight(list(1,2,3,4,5), 2)); check("Approach 3", r, "[4, 5, 1, 2, 3]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.rotateRight(list(0,1,2), 4)); check("Approach 3", r, "[2, 0, 1]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.rotateRight(list(), 0)); check("Approach 3", r, "[]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.rotateRight(list(1,2), 2)); check("Approach 3", r, "[1, 2]"); }
        System.out.println("RotateList: all 3 approaches passed " + passed + " checks");
    }
}
