import java.util.*;
import java.util.stream.*;

/**
 * Longest Repeating Character Replacement (Medium) - Day 2
 * https://leetcode.com/problems/longest-repeating-character-replacement/
 *
 * Approach 1: Brute force: every substring with counts  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sliding window, recompute the max count  |  Time O(26 n)  |  Space O(1)
 * Approach 3: Sliding window, max count never decreases (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac LongestRepeatingCharacterReplacement.java && java LongestRepeatingCharacterReplacement
 */
public class LongestRepeatingCharacterReplacement {

    // Approach 1: Brute force: every substring with counts
    // Time O(n^2), Space O(1)
    // Idea: A substring is fixable if length - (count of its most common letter) <= k. Check all substrings, updating counts as the end grows.
    static class Approach1 {
        public int characterReplacement(String s, int k) {
            int best = 0;
            for (int i = 0; i < s.length(); i++) {
                int[] c = new int[26];
                int maxF = 0;
                for (int j = i; j < s.length(); j++) {
                    maxF = Math.max(maxF, ++c[s.charAt(j) - 'A']);
                    if (j - i + 1 - maxF <= k) best = Math.max(best, j - i + 1);
                }
            }
            return best;
        }
    }

    // Approach 2: Sliding window, recompute the max count
    // Time O(26 n), Space O(1)
    // Idea: Grow right; while the window needs more than k replacements (length - max count), shrink left. Find the max count by scanning the 26 letters.
    static class Approach2 {
        public int characterReplacement(String s, int k) {
            int[] c = new int[26];
            int l = 0, best = 0;
            for (int r = 0; r < s.length(); r++) {
                c[s.charAt(r) - 'A']++;
                while (r - l + 1 - max(c) > k) c[s.charAt(l++) - 'A']--;
                best = Math.max(best, r - l + 1);
            }
            return best;
        }
        private int max(int[] c) { int m = 0; for (int x : c) m = Math.max(m, x); return m; }
    }

    // Approach 3: Sliding window, max count never decreases (optimal)
    // Time O(n), Space O(1)
    // Idea: Only a larger max count can give a longer answer, so keep the highest max count seen and never lower it. The window then slides instead of shrinking.
    static class Approach3 {
        public int characterReplacement(String s, int k) {
            int[] c = new int[26];
            int l = 0, maxF = 0, best = 0;
            for (int r = 0; r < s.length(); r++) {
                maxF = Math.max(maxF, ++c[s.charAt(r) - 'A']);
                if (r - l + 1 - maxF > k) c[s.charAt(l++) - 'A']--;
                best = Math.max(best, r - l + 1);
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
        check("Approach 1", new Approach1().characterReplacement("ABAB", 2), "4");
        check("Approach 1", new Approach1().characterReplacement("AABABBA", 1), "4");
        check("Approach 1", new Approach1().characterReplacement("A", 0), "1");
        check("Approach 1", new Approach1().characterReplacement("ABBB", 0), "3");
        check("Approach 2", new Approach2().characterReplacement("ABAB", 2), "4");
        check("Approach 2", new Approach2().characterReplacement("AABABBA", 1), "4");
        check("Approach 2", new Approach2().characterReplacement("A", 0), "1");
        check("Approach 2", new Approach2().characterReplacement("ABBB", 0), "3");
        check("Approach 3", new Approach3().characterReplacement("ABAB", 2), "4");
        check("Approach 3", new Approach3().characterReplacement("AABABBA", 1), "4");
        check("Approach 3", new Approach3().characterReplacement("A", 0), "1");
        check("Approach 3", new Approach3().characterReplacement("ABBB", 0), "3");
        System.out.println("LongestRepeatingCharacterReplacement: all 3 approaches passed " + passed + " checks");
    }
}
