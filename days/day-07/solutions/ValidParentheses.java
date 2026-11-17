import java.util.*;
import java.util.stream.*;

/**
 * Valid Parentheses (Easy) - Day 7
 * https://leetcode.com/problems/valid-parentheses/
 *
 * Approach 1: Repeatedly remove matched pairs  |  Time O(n^2)  |  Space O(n)
 * Approach 2: Stack of expected closers (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac ValidParentheses.java && java ValidParentheses
 */
public class ValidParentheses {

    // Approach 1: Repeatedly remove matched pairs
    // Time O(n^2), Space O(n)
    // Idea: Delete every '()', '[]' and '{}' until nothing changes; the string is valid if it becomes empty.
    static class Approach1 {
        public boolean isValid(String s) {
            String prev;
            do {
                prev = s;
                s = s.replace("()", "").replace("[]", "").replace("{}", "");
            } while (!s.equals(prev));
            return s.isEmpty();
        }
    }

    // Approach 2: Stack of expected closers (optimal)
    // Time O(n), Space O(n)
    // Idea: For each opener push the closer it needs; for each closer, the top of the stack must be exactly that closer. Valid if the stack is empty at the end.
    static class Approach2 {
        public boolean isValid(String s) {
            Deque<Character> st = new ArrayDeque<>();
            for (char c : s.toCharArray()) {
                if (c == '(') st.push(')');
                else if (c == '[') st.push(']');
                else if (c == '{') st.push('}');
                else if (st.isEmpty() || st.pop() != c) return false;
            }
            return st.isEmpty();
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
        check("Approach 1", new Approach1().isValid("()"), "true");
        check("Approach 1", new Approach1().isValid("()[]{}"), "true");
        check("Approach 1", new Approach1().isValid("(]"), "false");
        check("Approach 1", new Approach1().isValid("([)]"), "false");
        check("Approach 1", new Approach1().isValid("{[]}"), "true");
        check("Approach 1", new Approach1().isValid("("), "false");
        check("Approach 1", new Approach1().isValid("]"), "false");
        check("Approach 2", new Approach2().isValid("()"), "true");
        check("Approach 2", new Approach2().isValid("()[]{}"), "true");
        check("Approach 2", new Approach2().isValid("(]"), "false");
        check("Approach 2", new Approach2().isValid("([)]"), "false");
        check("Approach 2", new Approach2().isValid("{[]}"), "true");
        check("Approach 2", new Approach2().isValid("("), "false");
        check("Approach 2", new Approach2().isValid("]"), "false");
        System.out.println("ValidParentheses: all 2 approaches passed " + passed + " checks");
    }
}
