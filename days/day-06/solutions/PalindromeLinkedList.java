import java.util.*;
import java.util.stream.*;

/**
 * Palindrome Linked List (Easy) - Day 6
 * https://leetcode.com/problems/palindrome-linked-list/
 *
 * Approach 1: Copy values into an array, two pointers  |  Time O(n)  |  Space O(n)
 * Approach 2: Stack of the values  |  Time O(n)  |  Space O(n)
 * Approach 3: Find middle, reverse second half, compare (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac PalindromeLinkedList.java && java PalindromeLinkedList
 */
public class PalindromeLinkedList {

    // Approach 1: Copy values into an array, two pointers
    // Time O(n), Space O(n)
    // Idea: Copy the values to an ArrayList and compare from both ends.
    static class Approach1 {
        public boolean isPalindrome(ListNode head) {
            List<Integer> v = new ArrayList<>();
            for (ListNode p = head; p != null; p = p.next) v.add(p.val);
            for (int l = 0, r = v.size() - 1; l < r; l++, r--) {
                if (!v.get(l).equals(v.get(r))) return false;
            }
            return true;
        }
    }

    // Approach 2: Stack of the values
    // Time O(n), Space O(n)
    // Idea: Push all values; popping returns them in reverse order. Compare with a second walk from the head.
    static class Approach2 {
        public boolean isPalindrome(ListNode head) {
            Deque<Integer> st = new ArrayDeque<>();
            for (ListNode p = head; p != null; p = p.next) st.push(p.val);
            for (ListNode p = head; p != null; p = p.next) {
                if (p.val != st.pop()) return false;
            }
            return true;
        }
    }

    // Approach 3: Find middle, reverse second half, compare (optimal)
    // Time O(n), Space O(1)
    // Idea: Fast/slow finds the middle; reverse the second half in place; compare it with the first half; reverse it back to restore the input.
    static class Approach3 {
        public boolean isPalindrome(ListNode head) {
            ListNode slow = head, fast = head;
            while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
            ListNode second = reverse(slow), p = head, q = second;
            boolean ok = true;
            while (q != null) {
                if (p.val != q.val) { ok = false; break; }
                p = p.next;
                q = q.next;
            }
            reverse(second);                                   // restore the list
            return ok;
        }
        private ListNode reverse(ListNode head) {
            ListNode prev = null;
            while (head != null) { ListNode nx = head.next; head.next = prev; prev = head; head = nx; }
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
        { Approach1 o = new Approach1(); Object r; ListNode h = list(1,2,2,1); r = o.isPalindrome(h) + toList(h); check("Approach 1", r, "true[1, 2, 2, 1]"); }
        { Approach1 o = new Approach1(); Object r; r = o.isPalindrome(list(1,2)); check("Approach 1", r, "false"); }
        { Approach1 o = new Approach1(); Object r; r = o.isPalindrome(list(1,2,3,2,1)); check("Approach 1", r, "true"); }
        { Approach1 o = new Approach1(); Object r; r = o.isPalindrome(list(1)); check("Approach 1", r, "true"); }
        { Approach2 o = new Approach2(); Object r; ListNode h = list(1,2,2,1); r = o.isPalindrome(h) + toList(h); check("Approach 2", r, "true[1, 2, 2, 1]"); }
        { Approach2 o = new Approach2(); Object r; r = o.isPalindrome(list(1,2)); check("Approach 2", r, "false"); }
        { Approach2 o = new Approach2(); Object r; r = o.isPalindrome(list(1,2,3,2,1)); check("Approach 2", r, "true"); }
        { Approach2 o = new Approach2(); Object r; r = o.isPalindrome(list(1)); check("Approach 2", r, "true"); }
        { Approach3 o = new Approach3(); Object r; ListNode h = list(1,2,2,1); r = o.isPalindrome(h) + toList(h); check("Approach 3", r, "true[1, 2, 2, 1]"); }
        { Approach3 o = new Approach3(); Object r; r = o.isPalindrome(list(1,2)); check("Approach 3", r, "false"); }
        { Approach3 o = new Approach3(); Object r; r = o.isPalindrome(list(1,2,3,2,1)); check("Approach 3", r, "true"); }
        { Approach3 o = new Approach3(); Object r; r = o.isPalindrome(list(1)); check("Approach 3", r, "true"); }
        System.out.println("PalindromeLinkedList: all 3 approaches passed " + passed + " checks");
    }
}
