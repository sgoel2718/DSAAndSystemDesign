import java.util.*;
import java.util.stream.*;

/**
 * Remove All Adjacent Duplicates in String II (Medium) - Day 7
 * https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string-ii/
 *
 * Approach 1: Repeatedly remove a run of k  |  Time O(n^2 / k)  |  Space O(n)
 * Approach 2: Stack of (character, count) (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac RemoveAllAdjacentDuplicatesInStringIi.java && java RemoveAllAdjacentDuplicatesInStringIi
 */
public class RemoveAllAdjacentDuplicatesInStringIi {

    // Approach 1: Repeatedly remove a run of k
    // Time O(n^2 / k), Space O(n)
    // Idea: Find any run of k equal characters, delete it, and repeat until no run of k remains.
    static class Approach1 {
        public String removeDuplicates(String s, int k) {
            StringBuilder sb = new StringBuilder(s);
            boolean changed = true;
            while (changed) {
                changed = false;
                int run = 1;
                for (int i = 1; i < sb.length(); i++) {
                    run = sb.charAt(i) == sb.charAt(i - 1) ? run + 1 : 1;
                    if (run == k) { sb.delete(i - k + 1, i + 1); changed = true; break; }
                }
            }
            return sb.toString();
        }
    }

    // Approach 2: Stack of (character, count) (optimal)
    // Time O(n), Space O(n)
    // Idea: Keep the current run length on a count stack alongside the characters. When a run reaches k, delete those k characters at once.
    static class Approach2 {
        public String removeDuplicates(String s, int k) {
            StringBuilder sb = new StringBuilder();
            int[] count = new int[s.length()];
            for (char c : s.toCharArray()) {
                int n = sb.length();
                sb.append(c);
                count[n] = (n > 0 && sb.charAt(n - 1) == c) ? count[n - 1] + 1 : 1;
                if (count[n] == k) sb.setLength(n + 1 - k);
            }
            return sb.toString();
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
        check("Approach 1", new Approach1().removeDuplicates("abcd", 2), "abcd");
        check("Approach 1", new Approach1().removeDuplicates("deeedbbcccbdaa", 3), "aa");
        check("Approach 1", new Approach1().removeDuplicates("pbbcggttciiippooaais", 2), "ps");
        check("Approach 2", new Approach2().removeDuplicates("abcd", 2), "abcd");
        check("Approach 2", new Approach2().removeDuplicates("deeedbbcccbdaa", 3), "aa");
        check("Approach 2", new Approach2().removeDuplicates("pbbcggttciiippooaais", 2), "ps");
        System.out.println("RemoveAllAdjacentDuplicatesInStringIi: all 2 approaches passed " + passed + " checks");
    }
}
