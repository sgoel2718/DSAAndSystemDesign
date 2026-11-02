import java.util.*;
import java.util.stream.*;

/**
 * Longest Substring Without Repeating Characters (Medium) - Day 2
 * https://leetcode.com/problems/longest-substring-without-repeating-characters/
 *
 * Approach 1: Brute force: grow from every start  |  Time O(n^2)  |  Space O(min(n, charset))
 * Approach 2: Sliding window + HashSet  |  Time O(n)  |  Space O(min(n, charset))
 * Approach 3: Sliding window + last-seen index (optimal)  |  Time O(n)  |  Space O(1) (128-slot array)  <- best
 *
 * Run: javac LongestSubstringWithoutRepeatingCharacters.java && java LongestSubstringWithoutRepeatingCharacters
 */
public class LongestSubstringWithoutRepeatingCharacters {

    // Approach 1: Brute force: grow from every start
    // Time O(n^2), Space O(min(n, charset))
    // Idea: From each start index, extend while characters stay unique (tracked in a Set).
    static class Approach1 {
        public int lengthOfLongestSubstring(String s) {
            int best = 0;
            for (int i = 0; i < s.length(); i++) {
                Set<Character> seen = new HashSet<>();
                for (int j = i; j < s.length() && seen.add(s.charAt(j)); j++) {
                    best = Math.max(best, j - i + 1);
                }
            }
            return best;
        }
    }

    // Approach 2: Sliding window + HashSet
    // Time O(n), Space O(min(n, charset))
    // Idea: Expand right; while the new char is already in the window, remove from the left.
    static class Approach2 {
        public int lengthOfLongestSubstring(String s) {
            Set<Character> window = new HashSet<>();
            int l = 0, best = 0;
            for (int r = 0; r < s.length(); r++) {
                while (!window.add(s.charAt(r))) {
                    window.remove(s.charAt(l++));
                }
                best = Math.max(best, r - l + 1);
            }
            return best;
        }
    }

    // Approach 3: Sliding window + last-seen index (optimal)
    // Time O(n), Space O(1) (128-slot array)
    // Idea: Remember where each char was last seen; on a repeat, jump the left edge straight past it instead of shrinking one step at a time.
    static class Approach3 {
        public int lengthOfLongestSubstring(String s) {
            int[] last = new int[128];
            Arrays.fill(last, -1);
            int l = 0, best = 0;
            for (int r = 0; r < s.length(); r++) {
                char c = s.charAt(r);
                if (last[c] >= l) l = last[c] + 1;
                last[c] = r;
                best = Math.max(best, r - l + 1);
            }
            return best;
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
        check("Approach 1", new Approach1().lengthOfLongestSubstring("abcabcbb"), "3");
        check("Approach 1", new Approach1().lengthOfLongestSubstring("bbbbb"), "1");
        check("Approach 1", new Approach1().lengthOfLongestSubstring("pwwkew"), "3");
        check("Approach 1", new Approach1().lengthOfLongestSubstring(""), "0");
        check("Approach 1", new Approach1().lengthOfLongestSubstring("abba"), "2");
        check("Approach 2", new Approach2().lengthOfLongestSubstring("abcabcbb"), "3");
        check("Approach 2", new Approach2().lengthOfLongestSubstring("bbbbb"), "1");
        check("Approach 2", new Approach2().lengthOfLongestSubstring("pwwkew"), "3");
        check("Approach 2", new Approach2().lengthOfLongestSubstring(""), "0");
        check("Approach 2", new Approach2().lengthOfLongestSubstring("abba"), "2");
        check("Approach 3", new Approach3().lengthOfLongestSubstring("abcabcbb"), "3");
        check("Approach 3", new Approach3().lengthOfLongestSubstring("bbbbb"), "1");
        check("Approach 3", new Approach3().lengthOfLongestSubstring("pwwkew"), "3");
        check("Approach 3", new Approach3().lengthOfLongestSubstring(""), "0");
        check("Approach 3", new Approach3().lengthOfLongestSubstring("abba"), "2");
        System.out.println("LongestSubstringWithoutRepeatingCharacters: all 3 approaches passed " + passed + " checks");
    }
}
