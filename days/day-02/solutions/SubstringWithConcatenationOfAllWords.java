import java.util.*;
import java.util.stream.*;

/**
 * Substring with Concatenation of All Words (Hard) - Day 2
 * https://leetcode.com/problems/substring-with-concatenation-of-all-words/
 *
 * Approach 1: Check every start index  |  Time O(n x w x L)  |  Space O(w)
 * Approach 2: Sliding window per offset, one word at a time (optimal)  |  Time O(n x L)  |  Space O(w)  <- best
 *
 * Run: javac SubstringWithConcatenationOfAllWords.java && java SubstringWithConcatenationOfAllWords
 */
public class SubstringWithConcatenationOfAllWords {

    // Approach 1: Check every start index
    // Time O(n x w x L), Space O(w)
    // Idea: All words have the same length L. From each start, read w words of length L and check them against the word counts.
    static class Approach1 {
        public List<Integer> findSubstring(String s, String[] words) {
            List<Integer> res = new ArrayList<>();
            int L = words[0].length(), w = words.length, n = s.length();
            Map<String, Integer> need = new HashMap<>();
            for (String x : words) need.merge(x, 1, Integer::sum);
            for (int i = 0; i + w * L <= n; i++) {
                Map<String, Integer> seen = new HashMap<>();
                int j = 0;
                for (; j < w; j++) {
                    String x = s.substring(i + j * L, i + (j + 1) * L);
                    if (!need.containsKey(x) || seen.merge(x, 1, Integer::sum) > need.get(x)) break;
                }
                if (j == w) res.add(i);
            }
            return res;
        }
    }

    // Approach 2: Sliding window per offset, one word at a time (optimal)
    // Time O(n x L), Space O(w)
    // Idea: Run L separate sliding windows (offsets 0..L-1) that step a whole word at a time. Shrink from the left when a word appears too often; reset when an unknown word appears.
    static class Approach2 {
        public List<Integer> findSubstring(String s, String[] words) {
            List<Integer> res = new ArrayList<>();
            int L = words[0].length(), w = words.length, n = s.length();
            Map<String, Integer> need = new HashMap<>();
            for (String x : words) need.merge(x, 1, Integer::sum);
            for (int off = 0; off < L; off++) {
                Map<String, Integer> have = new HashMap<>();
                int left = off, count = 0;
                for (int r = off; r + L <= n; r += L) {
                    String word = s.substring(r, r + L);
                    if (!need.containsKey(word)) { have.clear(); count = 0; left = r + L; continue; }
                    have.merge(word, 1, Integer::sum);
                    count++;
                    while (have.get(word) > need.get(word)) {
                        have.merge(s.substring(left, left + L), -1, Integer::sum);
                        count--;
                        left += L;
                    }
                    if (count == w) {
                        res.add(left);
                        have.merge(s.substring(left, left + L), -1, Integer::sum);
                        count--;
                        left += L;
                    }
                }
            }
            Collections.sort(res);
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
        check("Approach 1", new Approach1().findSubstring("barfoothefoobarman", new String[]{"foo","bar"}), "[0, 9]");
        check("Approach 1", new Approach1().findSubstring("wordgoodgoodgoodbestword", new String[]{"word","good","best","word"}), "[]");
        check("Approach 1", new Approach1().findSubstring("barfoofoobarthefoobarman", new String[]{"bar","foo","the"}), "[6, 9, 12]");
        check("Approach 1", new Approach1().findSubstring("aaaaaa", new String[]{"aa","aa"}), "[0, 1, 2]");
        check("Approach 2", new Approach2().findSubstring("barfoothefoobarman", new String[]{"foo","bar"}), "[0, 9]");
        check("Approach 2", new Approach2().findSubstring("wordgoodgoodgoodbestword", new String[]{"word","good","best","word"}), "[]");
        check("Approach 2", new Approach2().findSubstring("barfoofoobarthefoobarman", new String[]{"bar","foo","the"}), "[6, 9, 12]");
        check("Approach 2", new Approach2().findSubstring("aaaaaa", new String[]{"aa","aa"}), "[0, 1, 2]");
        System.out.println("SubstringWithConcatenationOfAllWords: all 2 approaches passed " + passed + " checks");
    }
}
