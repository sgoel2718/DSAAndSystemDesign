import java.util.*;
import java.util.stream.*;

/**
 * Minimum Window Substring (Hard) - Day 2
 * https://leetcode.com/problems/minimum-window-substring/
 *
 * Approach 1: Brute force: grow from every start  |  Time O(n^2)  |  Space O(1) (128-slot arrays)
 * Approach 2: Sliding window with counts (optimal)  |  Time O(|s| + |t|)  |  Space O(1) (128-slot array)  <- best
 *
 * Run: javac MinimumWindowSubstring.java && java MinimumWindowSubstring
 */
public class MinimumWindowSubstring {

    // Approach 1: Brute force: grow from every start
    // Time O(n^2), Space O(1) (128-slot arrays)
    // Idea: From each start, extend until the window covers t (count of still-missing chars hits 0); keep the shortest.
    static class Approach1 {
        public String minWindow(String s, String t) {
            int[] need = new int[128];
            for (char c : t.toCharArray()) need[c]++;
            int bestLen = Integer.MAX_VALUE, bestStart = 0;
            for (int i = 0; i < s.length(); i++) {
                int[] have = new int[128];
                int missing = t.length();
                for (int j = i; j < s.length(); j++) {
                    char c = s.charAt(j);
                    if (have[c]++ < need[c]) missing--;
                    if (missing == 0) {
                        if (j - i + 1 < bestLen) { bestLen = j - i + 1; bestStart = i; }
                        break;
                    }
                }
            }
            return bestLen == Integer.MAX_VALUE ? "" : s.substring(bestStart, bestStart + bestLen);
        }
    }

    // Approach 2: Sliding window with counts (optimal)
    // Time O(|s| + |t|), Space O(1) (128-slot array)
    // Idea: Expand right until every needed char is covered, then shrink from the left while it stays covered, recording the smallest window.
    static class Approach2 {
        public String minWindow(String s, String t) {
            int[] need = new int[128];
            for (char c : t.toCharArray()) need[c]++;
            int missing = t.length(), l = 0, bestLen = Integer.MAX_VALUE, bestStart = 0;
            for (int r = 0; r < s.length(); r++) {
                if (need[s.charAt(r)]-- > 0) missing--;          // this char was still needed
                while (missing == 0) {                           // window covers t: try to shrink
                    if (r - l + 1 < bestLen) { bestLen = r - l + 1; bestStart = l; }
                    if (++need[s.charAt(l++)] > 0) missing++;    // removed a needed char
                }
            }
            return bestLen == Integer.MAX_VALUE ? "" : s.substring(bestStart, bestStart + bestLen);
        }
    }

    static String show(Object r) {
        if (r instanceof int[] a) return Arrays.toString(a);
        if (r instanceof int[][] a) return Arrays.deepToString(a);
        return String.valueOf(r);
    }
    static String norm(List<List<Integer>> x) {                 // order-independent view of a list of lists
        List<List<Integer>> c = new ArrayList<>();
        for (List<Integer> t : x) { List<Integer> s = new ArrayList<>(t); Collections.sort(s); c.add(s); }
        c.sort((p, q) -> { for (int i = 0; i < Math.min(p.size(), q.size()); i++) { int d = Integer.compare(p.get(i), q.get(i)); if (d != 0) return d; } return p.size() - q.size(); });
        return c.toString();
    }
    static String sorted(List<Integer> x) { List<Integer> c = new ArrayList<>(x); Collections.sort(c); return c.toString(); }
    static int passed = 0;
    static void check(String what, Object r, String want) {
        String got = show(r);
        if (!got.equals(want)) throw new AssertionError(what + ": got " + got + ", want " + want);
        passed++;
    }

    public static void main(String[] args) {
        check("Approach 1", new Approach1().minWindow("ADOBECODEBANC", "ABC"), "BANC");
        check("Approach 1", new Approach1().minWindow("a", "a"), "a");
        check("Approach 1", new Approach1().minWindow("a", "aa"), "");
        check("Approach 2", new Approach2().minWindow("ADOBECODEBANC", "ABC"), "BANC");
        check("Approach 2", new Approach2().minWindow("a", "a"), "a");
        check("Approach 2", new Approach2().minWindow("a", "aa"), "");
        System.out.println("MinimumWindowSubstring: all 2 approaches passed " + passed + " checks");
    }
}
