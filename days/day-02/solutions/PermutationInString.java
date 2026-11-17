import java.util.*;
import java.util.stream.*;

/**
 * Permutation in String (Medium) - Day 2
 * https://leetcode.com/problems/permutation-in-string/
 *
 * Approach 1: Sort every window and compare  |  Time O(n x m log m)  |  Space O(m)
 * Approach 2: Fixed window of letter counts  |  Time O(26 n)  |  Space O(1)
 * Approach 3: Fixed window with a 'matching letters' counter (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac PermutationInString.java && java PermutationInString
 */
public class PermutationInString {

    // Approach 1: Sort every window and compare
    // Time O(n x m log m), Space O(m)
    // Idea: Two strings are permutations of each other if their sorted forms match. Sort s1 once and every window of s2.
    static class Approach1 {
        public boolean checkInclusion(String s1, String s2) {
            char[] a = s1.toCharArray();
            Arrays.sort(a);
            String key = new String(a);
            for (int i = 0; i + s1.length() <= s2.length(); i++) {
                char[] w = s2.substring(i, i + s1.length()).toCharArray();
                Arrays.sort(w);
                if (key.equals(new String(w))) return true;
            }
            return false;
        }
    }

    // Approach 2: Fixed window of letter counts
    // Time O(26 n), Space O(1)
    // Idea: Keep counts for the current window of length |s1|; compare the two 26-slot arrays at each step.
    static class Approach2 {
        public boolean checkInclusion(String s1, String s2) {
            int m = s1.length();
            if (m > s2.length()) return false;
            int[] need = new int[26], win = new int[26];
            for (char c : s1.toCharArray()) need[c - 'a']++;
            for (int r = 0; r < s2.length(); r++) {
                win[s2.charAt(r) - 'a']++;
                if (r >= m) win[s2.charAt(r - m) - 'a']--;
                if (r >= m - 1 && Arrays.equals(need, win)) return true;
            }
            return false;
        }
    }

    // Approach 3: Fixed window with a 'matching letters' counter (optimal)
    // Time O(n), Space O(1)
    // Idea: Track how many of the 26 letters currently have equal counts. Each slide changes two letters, so the counter updates in O(1); all 26 matching means a permutation.
    static class Approach3 {
        public boolean checkInclusion(String s1, String s2) {
            int m = s1.length(), n = s2.length();
            if (m > n) return false;
            int[] a = new int[26], b = new int[26];
            for (int i = 0; i < m; i++) { a[s1.charAt(i) - 'a']++; b[s2.charAt(i) - 'a']++; }
            int matches = 0;
            for (int i = 0; i < 26; i++) if (a[i] == b[i]) matches++;
            for (int r = m; r < n; r++) {
                if (matches == 26) return true;
                int in = s2.charAt(r) - 'a';
                b[in]++;
                if (b[in] == a[in]) matches++; else if (b[in] == a[in] + 1) matches--;
                int out = s2.charAt(r - m) - 'a';
                b[out]--;
                if (b[out] == a[out]) matches++; else if (b[out] == a[out] - 1) matches--;
            }
            return matches == 26;
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
        check("Approach 1", new Approach1().checkInclusion("ab", "eidbaooo"), "true");
        check("Approach 1", new Approach1().checkInclusion("ab", "eidboaoo"), "false");
        check("Approach 1", new Approach1().checkInclusion("adc", "dcda"), "true");
        check("Approach 1", new Approach1().checkInclusion("abc", "ab"), "false");
        check("Approach 2", new Approach2().checkInclusion("ab", "eidbaooo"), "true");
        check("Approach 2", new Approach2().checkInclusion("ab", "eidboaoo"), "false");
        check("Approach 2", new Approach2().checkInclusion("adc", "dcda"), "true");
        check("Approach 2", new Approach2().checkInclusion("abc", "ab"), "false");
        check("Approach 3", new Approach3().checkInclusion("ab", "eidbaooo"), "true");
        check("Approach 3", new Approach3().checkInclusion("ab", "eidboaoo"), "false");
        check("Approach 3", new Approach3().checkInclusion("adc", "dcda"), "true");
        check("Approach 3", new Approach3().checkInclusion("abc", "ab"), "false");
        System.out.println("PermutationInString: all 3 approaches passed " + passed + " checks");
    }
}
