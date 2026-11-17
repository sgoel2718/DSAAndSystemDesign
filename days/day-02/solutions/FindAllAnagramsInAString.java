import java.util.*;
import java.util.stream.*;

/**
 * Find All Anagrams in a String (Medium) - Day 2
 * https://leetcode.com/problems/find-all-anagrams-in-a-string/
 *
 * Approach 1: Sort every window and compare  |  Time O(n x m log m)  |  Space O(m)
 * Approach 2: Fixed window of letter counts  |  Time O(26 n)  |  Space O(1)
 * Approach 3: Fixed window with a 'still needed' counter (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac FindAllAnagramsInAString.java && java FindAllAnagramsInAString
 */
public class FindAllAnagramsInAString {

    // Approach 1: Sort every window and compare
    // Time O(n x m log m), Space O(m)
    // Idea: Sort p once; sort each window of s of the same length and compare.
    static class Approach1 {
        public List<Integer> findAnagrams(String s, String p) {
            List<Integer> res = new ArrayList<>();
            char[] a = p.toCharArray();
            Arrays.sort(a);
            String key = new String(a);
            for (int i = 0; i + p.length() <= s.length(); i++) {
                char[] w = s.substring(i, i + p.length()).toCharArray();
                Arrays.sort(w);
                if (key.equals(new String(w))) res.add(i);
            }
            return res;
        }
    }

    // Approach 2: Fixed window of letter counts
    // Time O(26 n), Space O(1)
    // Idea: Slide a window of length |p| over s keeping letter counts; record the start whenever the counts equal p's counts.
    static class Approach2 {
        public List<Integer> findAnagrams(String s, String p) {
            List<Integer> res = new ArrayList<>();
            int m = p.length();
            int[] need = new int[26], win = new int[26];
            for (char c : p.toCharArray()) need[c - 'a']++;
            for (int r = 0; r < s.length(); r++) {
                win[s.charAt(r) - 'a']++;
                if (r >= m) win[s.charAt(r - m) - 'a']--;
                if (r >= m - 1 && Arrays.equals(need, win)) res.add(r - m + 1);
            }
            return res;
        }
    }

    // Approach 3: Fixed window with a 'still needed' counter (optimal)
    // Time O(n), Space O(1)
    // Idea: One count array of what p still needs and a counter of missing letters. The window is an anagram exactly when nothing is missing.
    static class Approach3 {
        public List<Integer> findAnagrams(String s, String p) {
            List<Integer> res = new ArrayList<>();
            int m = p.length();
            if (m > s.length()) return res;
            int[] need = new int[26];
            for (char c : p.toCharArray()) need[c - 'a']++;
            int missing = m;
            for (int r = 0; r < s.length(); r++) {
                if (need[s.charAt(r) - 'a']-- > 0) missing--;
                if (r >= m && ++need[s.charAt(r - m) - 'a'] > 0) missing++;
                if (missing == 0) res.add(r - m + 1);
            }
            return res;
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
        check("Approach 1", new Approach1().findAnagrams("cbaebabacd", "abc"), "[0, 6]");
        check("Approach 1", new Approach1().findAnagrams("abab", "ab"), "[0, 1, 2]");
        check("Approach 1", new Approach1().findAnagrams("a", "ab"), "[]");
        check("Approach 2", new Approach2().findAnagrams("cbaebabacd", "abc"), "[0, 6]");
        check("Approach 2", new Approach2().findAnagrams("abab", "ab"), "[0, 1, 2]");
        check("Approach 2", new Approach2().findAnagrams("a", "ab"), "[]");
        check("Approach 3", new Approach3().findAnagrams("cbaebabacd", "abc"), "[0, 6]");
        check("Approach 3", new Approach3().findAnagrams("abab", "ab"), "[0, 1, 2]");
        check("Approach 3", new Approach3().findAnagrams("a", "ab"), "[]");
        System.out.println("FindAllAnagramsInAString: all 3 approaches passed " + passed + " checks");
    }
}
