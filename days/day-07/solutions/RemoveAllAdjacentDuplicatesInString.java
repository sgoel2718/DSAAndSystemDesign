import java.util.*;
import java.util.stream.*;

/**
 * Remove All Adjacent Duplicates In String (Easy) - Day 7
 * https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string/
 *
 * Approach 1: Repeatedly remove a pair  |  Time O(n^2)  |  Space O(n)
 * Approach 2: Stack (a StringBuilder used as one) (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac RemoveAllAdjacentDuplicatesInString.java && java RemoveAllAdjacentDuplicatesInString
 */
public class RemoveAllAdjacentDuplicatesInString {

    // Approach 1: Repeatedly remove a pair
    // Time O(n^2), Space O(n)
    // Idea: Scan for two equal neighbours, remove them, and start again until there are none.
    static class Approach1 {
        public String removeDuplicates(String s) {
            StringBuilder sb = new StringBuilder(s);
            boolean changed = true;
            while (changed) {
                changed = false;
                for (int i = 0; i + 1 < sb.length(); i++) {
                    if (sb.charAt(i) == sb.charAt(i + 1)) { sb.delete(i, i + 2); changed = true; break; }
                }
            }
            return sb.toString();
        }
    }

    // Approach 2: Stack (a StringBuilder used as one) (optimal)
    // Time O(n), Space O(n)
    // Idea: Push each character; if it equals the top, pop instead. What is left is the answer.
    static class Approach2 {
        public String removeDuplicates(String s) {
            StringBuilder st = new StringBuilder();
            for (char c : s.toCharArray()) {
                int n = st.length();
                if (n > 0 && st.charAt(n - 1) == c) st.deleteCharAt(n - 1);
                else st.append(c);
            }
            return st.toString();
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
        check("Approach 1", new Approach1().removeDuplicates("abbaca"), "ca");
        check("Approach 1", new Approach1().removeDuplicates("azxxzy"), "ay");
        check("Approach 1", new Approach1().removeDuplicates("aa"), "");
        check("Approach 2", new Approach2().removeDuplicates("abbaca"), "ca");
        check("Approach 2", new Approach2().removeDuplicates("azxxzy"), "ay");
        check("Approach 2", new Approach2().removeDuplicates("aa"), "");
        System.out.println("RemoveAllAdjacentDuplicatesInString: all 2 approaches passed " + passed + " checks");
    }
}
