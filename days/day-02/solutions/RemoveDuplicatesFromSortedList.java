import java.util.*;
import java.util.stream.*;

/**
 * Remove Duplicates from Sorted List (Easy) - Day 2
 * https://leetcode.com/problems/remove-duplicates-from-sorted-list/
 *
 * Approach 1: Rebuild from a LinkedHashSet  |  Time O(n)  |  Space O(n)
 * Approach 2: Recursion  |  Time O(n)  |  Space O(n) recursion stack
 * Approach 3: One pass, skip equal neighbours (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac RemoveDuplicatesFromSortedList.java && java RemoveDuplicatesFromSortedList
 */
public class RemoveDuplicatesFromSortedList {

    // Approach 1: Rebuild from a LinkedHashSet
    // Time O(n), Space O(n)
    // Idea: Collect unique values in order, then build a fresh list.
    static class Approach1 {
        public ListNode deleteDuplicates(ListNode head) {
            Set<Integer> uniq = new LinkedHashSet<>();
            for (ListNode p = head; p != null; p = p.next) uniq.add(p.val);
            ListNode dummy = new ListNode(0), tail = dummy;
            for (int v : uniq) { tail.next = new ListNode(v); tail = tail.next; }
            return dummy.next;
        }
    }

    // Approach 2: Recursion
    // Time O(n), Space O(n) recursion stack
    // Idea: Clean the rest of the list first, then skip the head's next node if it has the same value.
    static class Approach2 {
        public ListNode deleteDuplicates(ListNode head) {
            if (head == null || head.next == null) return head;
            head.next = deleteDuplicates(head.next);
            return head.val == head.next.val ? head.next : head;
        }
    }

    // Approach 3: One pass, skip equal neighbours (optimal)
    // Time O(n), Space O(1)
    // Idea: The list is sorted, so duplicates are adjacent: while the next node has the same value, unlink it.
    static class Approach3 {
        public ListNode deleteDuplicates(ListNode head) {
            ListNode cur = head;
            while (cur != null && cur.next != null) {
                if (cur.next.val == cur.val) cur.next = cur.next.next;
                else cur = cur.next;
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
        { Approach1 o = new Approach1(); Object r; r = toList(o.deleteDuplicates(list(1,1,2))); check("Approach 1", r, "[1, 2]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.deleteDuplicates(list(1,1,2,3,3))); check("Approach 1", r, "[1, 2, 3]"); }
        { Approach1 o = new Approach1(); Object r; r = toList(o.deleteDuplicates(list())); check("Approach 1", r, "[]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.deleteDuplicates(list(1,1,2))); check("Approach 2", r, "[1, 2]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.deleteDuplicates(list(1,1,2,3,3))); check("Approach 2", r, "[1, 2, 3]"); }
        { Approach2 o = new Approach2(); Object r; r = toList(o.deleteDuplicates(list())); check("Approach 2", r, "[]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.deleteDuplicates(list(1,1,2))); check("Approach 3", r, "[1, 2]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.deleteDuplicates(list(1,1,2,3,3))); check("Approach 3", r, "[1, 2, 3]"); }
        { Approach3 o = new Approach3(); Object r; r = toList(o.deleteDuplicates(list())); check("Approach 3", r, "[]"); }
        System.out.println("RemoveDuplicatesFromSortedList: all 3 approaches passed " + passed + " checks");
    }
}
