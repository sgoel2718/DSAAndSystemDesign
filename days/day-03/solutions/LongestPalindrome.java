import java.util.*;
import java.util.stream.*;

/**
 * Longest Palindrome (Easy) - Day 3
 * https://leetcode.com/problems/longest-palindrome/
 *
 * Approach 1: HashSet pairing  |  Time O(n)  |  Space O(k) distinct characters
 * Approach 2: HashMap of counts  |  Time O(n)  |  Space O(k)
 * Approach 3: int[128] counts (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac LongestPalindrome.java && java LongestPalindrome
 */
public class LongestPalindrome {

    // Approach 1: HashSet pairing
    // Time O(n), Space O(k) distinct characters
    // Idea: Add a character to a set; when it appears again, remove it and count a pair. If any unpaired character is left, one can sit in the middle.
    static class Approach1 {
        public int longestPalindrome(String s) {
            Set<Character> odd = new HashSet<>();
            int pairs = 0;
            for (char c : s.toCharArray()) {
                if (!odd.add(c)) { odd.remove(c); pairs++; }
            }
            return pairs * 2 + (odd.isEmpty() ? 0 : 1);
        }
    }

    // Approach 2: HashMap of counts
    // Time O(n), Space O(k)
    // Idea: Use count / 2 * 2 of every character; add 1 if any count is odd (for the middle).
    static class Approach2 {
        public int longestPalindrome(String s) {
            Map<Character, Integer> count = new HashMap<>();
            for (char c : s.toCharArray()) count.merge(c, 1, Integer::sum);
            int len = 0;
            boolean odd = false;
            for (int v : count.values()) { len += v / 2 * 2; if (v % 2 == 1) odd = true; }
            return len + (odd ? 1 : 0);
        }
    }

    // Approach 3: int[128] counts (optimal)
    // Time O(n), Space O(1)
    // Idea: Same rule with an array that covers upper and lower case letters.
    static class Approach3 {
        public int longestPalindrome(String s) {
            int[] count = new int[128];
            for (char c : s.toCharArray()) count[c]++;
            int len = 0;
            for (int v : count) len += v / 2 * 2;
            return len < s.length() ? len + 1 : len;
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
        check("Approach 1", new Approach1().longestPalindrome("abccccdd"), "7");
        check("Approach 1", new Approach1().longestPalindrome("a"), "1");
        check("Approach 1", new Approach1().longestPalindrome("Aa"), "1");
        check("Approach 1", new Approach1().longestPalindrome("aaabbb"), "5");
        check("Approach 2", new Approach2().longestPalindrome("abccccdd"), "7");
        check("Approach 2", new Approach2().longestPalindrome("a"), "1");
        check("Approach 2", new Approach2().longestPalindrome("Aa"), "1");
        check("Approach 2", new Approach2().longestPalindrome("aaabbb"), "5");
        check("Approach 3", new Approach3().longestPalindrome("abccccdd"), "7");
        check("Approach 3", new Approach3().longestPalindrome("a"), "1");
        check("Approach 3", new Approach3().longestPalindrome("Aa"), "1");
        check("Approach 3", new Approach3().longestPalindrome("aaabbb"), "5");
        System.out.println("LongestPalindrome: all 3 approaches passed " + passed + " checks");
    }
}
