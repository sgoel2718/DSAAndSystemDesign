import java.util.*;
import java.util.stream.*;

/**
 * Longest K Unique Characters Substring (Medium) - Day 2
 * https://leetcode.com/problems/gfg-longest-k-unique-characters-substring/
 *
 * Approach 1: Brute force: grow from every start  |  Time O(n^2)  |  Space O(1) (128-slot array)
 * Approach 2: Variable sliding window with counts (optimal)  |  Time O(n)  |  Space O(1) (128-slot array)  <- best
 *
 * Run: javac GfgLongestKUniqueCharactersSubstring.java && java GfgLongestKUniqueCharactersSubstring
 */
public class GfgLongestKUniqueCharactersSubstring {

    // Approach 1: Brute force: grow from every start
    // Time O(n^2), Space O(1) (128-slot array)
    // Idea: From each start count distinct characters; record the length whenever exactly k are distinct and stop once there are more than k. Return -1 if no substring has exactly k.
    static class Approach1 {
        public int longestkSubstr(String s, int k) {
            int best = -1;
            for (int i = 0; i < s.length(); i++) {
                int[] c = new int[128];
                int distinct = 0;
                for (int j = i; j < s.length(); j++) {
                    if (c[s.charAt(j)]++ == 0) distinct++;
                    if (distinct == k) best = Math.max(best, j - i + 1);
                    else if (distinct > k) break;
                }
            }
            return best;
        }
    }

    // Approach 2: Variable sliding window with counts (optimal)
    // Time O(n), Space O(1) (128-slot array)
    // Idea: Grow right, shrink left while there are more than k distinct characters; whenever exactly k are distinct, record the window.
    static class Approach2 {
        public int longestkSubstr(String s, int k) {
            int[] c = new int[128];
            int l = 0, distinct = 0, best = -1;
            for (int r = 0; r < s.length(); r++) {
                if (c[s.charAt(r)]++ == 0) distinct++;
                while (distinct > k) {
                    if (--c[s.charAt(l++)] == 0) distinct--;
                }
                if (distinct == k) best = Math.max(best, r - l + 1);
            }
            return best;
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
        check("Approach 1", new Approach1().longestkSubstr("aabacbebebe", 3), "7");
        check("Approach 1", new Approach1().longestkSubstr("aaaa", 2), "-1");
        check("Approach 1", new Approach1().longestkSubstr("aabaaab", 2), "7");
        check("Approach 2", new Approach2().longestkSubstr("aabacbebebe", 3), "7");
        check("Approach 2", new Approach2().longestkSubstr("aaaa", 2), "-1");
        check("Approach 2", new Approach2().longestkSubstr("aabaaab", 2), "7");
        System.out.println("GfgLongestKUniqueCharactersSubstring: all 2 approaches passed " + passed + " checks");
    }
}
