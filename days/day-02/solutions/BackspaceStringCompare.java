import java.util.*;
import java.util.stream.*;

/**
 * Backspace String Compare (Easy) - Day 2
 * https://leetcode.com/problems/backspace-string-compare/
 *
 * Approach 1: Build both strings with a stack  |  Time O(n + m)  |  Space O(n + m)
 * Approach 2: Two pointers from the end (optimal)  |  Time O(n + m)  |  Space O(1)  <- best
 *
 * Run: javac BackspaceStringCompare.java && java BackspaceStringCompare
 */
public class BackspaceStringCompare {

    // Approach 1: Build both strings with a stack
    // Time O(n + m), Space O(n + m)
    // Idea: Process each string: a letter is pushed, '#' pops. Compare the results.
    static class Approach1 {
        public boolean backspaceCompare(String s, String t) {
            return build(s).equals(build(t));
        }
        private String build(String s) {
            StringBuilder sb = new StringBuilder();
            for (char c : s.toCharArray()) {
                if (c != '#') sb.append(c);
                else if (sb.length() > 0) sb.deleteCharAt(sb.length() - 1);
            }
            return sb.toString();
        }
    }

    // Approach 2: Two pointers from the end (optimal)
    // Time O(n + m), Space O(1)
    // Idea: Walk both strings backwards, skipping characters that a later '#' deletes. Compare the next surviving character of each.
    static class Approach2 {
        public boolean backspaceCompare(String s, String t) {
            int i = s.length() - 1, j = t.length() - 1;
            while (i >= 0 || j >= 0) {
                i = nextValid(s, i);
                j = nextValid(t, j);
                if (i < 0 || j < 0) return i < 0 && j < 0;
                if (s.charAt(i) != t.charAt(j)) return false;
                i--;
                j--;
            }
            return true;
        }
        private int nextValid(String s, int i) {
            int skip = 0;
            while (i >= 0) {
                if (s.charAt(i) == '#') { skip++; i--; }
                else if (skip > 0) { skip--; i--; }
                else break;
            }
            return i;
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
        check("Approach 1", new Approach1().backspaceCompare("ab#c", "ad#c"), "true");
        check("Approach 1", new Approach1().backspaceCompare("ab##", "c#d#"), "true");
        check("Approach 1", new Approach1().backspaceCompare("a#c", "b"), "false");
        check("Approach 1", new Approach1().backspaceCompare("bxj##tw", "bxo#j##tw"), "true");
        check("Approach 2", new Approach2().backspaceCompare("ab#c", "ad#c"), "true");
        check("Approach 2", new Approach2().backspaceCompare("ab##", "c#d#"), "true");
        check("Approach 2", new Approach2().backspaceCompare("a#c", "b"), "false");
        check("Approach 2", new Approach2().backspaceCompare("bxj##tw", "bxo#j##tw"), "true");
        System.out.println("BackspaceStringCompare: all 2 approaches passed " + passed + " checks");
    }
}
