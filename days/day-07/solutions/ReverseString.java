import java.util.*;
import java.util.stream.*;

/**
 * Reverse String (Easy) - Day 7
 * https://leetcode.com/problems/reverse-string/
 *
 * Approach 1: Copy into a new array  |  Time O(n)  |  Space O(n)
 * Approach 2: Stack  |  Time O(n)  |  Space O(n)
 * Approach 3: Two pointers, swap in place (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac ReverseString.java && java ReverseString
 */
public class ReverseString {

    // Approach 1: Copy into a new array
    // Time O(n), Space O(n)
    // Idea: Write characters into a new array in reverse order, then copy back. Uses extra memory, which the problem forbids.
    static class Approach1 {
        public void reverseString(char[] s) {
            char[] copy = new char[s.length];
            for (int i = 0; i < s.length; i++) copy[i] = s[s.length - 1 - i];
            System.arraycopy(copy, 0, s, 0, s.length);
        }
    }

    // Approach 2: Stack
    // Time O(n), Space O(n)
    // Idea: Push every character, then pop them back in reverse order.
    static class Approach2 {
        public void reverseString(char[] s) {
            Deque<Character> st = new ArrayDeque<>();
            for (char c : s) st.push(c);
            for (int i = 0; i < s.length; i++) s[i] = st.pop();
        }
    }

    // Approach 3: Two pointers, swap in place (optimal)
    // Time O(n), Space O(1)
    // Idea: Swap the two ends and move inward.
    static class Approach3 {
        public void reverseString(char[] s) {
            for (int l = 0, r = s.length - 1; l < r; l++, r--) {
                char t = s[l]; s[l] = s[r]; s[r] = t;
            }
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
        { Approach1 o = new Approach1(); Object r; char[] a = "hello".toCharArray(); o.reverseString(a); r = new String(a); check("Approach 1", r, "olleh"); }
        { Approach1 o = new Approach1(); Object r; char[] a = "Hannah".toCharArray(); o.reverseString(a); r = new String(a); check("Approach 1", r, "hannaH"); }
        { Approach2 o = new Approach2(); Object r; char[] a = "hello".toCharArray(); o.reverseString(a); r = new String(a); check("Approach 2", r, "olleh"); }
        { Approach2 o = new Approach2(); Object r; char[] a = "Hannah".toCharArray(); o.reverseString(a); r = new String(a); check("Approach 2", r, "hannaH"); }
        { Approach3 o = new Approach3(); Object r; char[] a = "hello".toCharArray(); o.reverseString(a); r = new String(a); check("Approach 3", r, "olleh"); }
        { Approach3 o = new Approach3(); Object r; char[] a = "Hannah".toCharArray(); o.reverseString(a); r = new String(a); check("Approach 3", r, "hannaH"); }
        System.out.println("ReverseString: all 3 approaches passed " + passed + " checks");
    }
}
