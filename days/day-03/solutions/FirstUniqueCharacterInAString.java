import java.util.*;
import java.util.stream.*;

/**
 * First Unique Character in a String (Easy) - Day 3
 * https://leetcode.com/problems/first-unique-character-in-a-string/
 *
 * Approach 1: Brute force: compare with every other character  |  Time O(n^2)  |  Space O(1)
 * Approach 2: HashMap of counts, two passes  |  Time O(n)  |  Space O(k) distinct characters
 * Approach 3: int[26] counts, two passes (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac FirstUniqueCharacterInAString.java && java FirstUniqueCharacterInAString
 */
public class FirstUniqueCharacterInAString {

    // Approach 1: Brute force: compare with every other character
    // Time O(n^2), Space O(1)
    // Idea: For each index, scan the whole string for another copy of the same character.
    static class Approach1 {
        public int firstUniqChar(String s) {
            for (int i = 0; i < s.length(); i++) {
                boolean unique = true;
                for (int j = 0; j < s.length() && unique; j++)
                    if (i != j && s.charAt(i) == s.charAt(j)) unique = false;
                if (unique) return i;
            }
            return -1;
        }
    }

    // Approach 2: HashMap of counts, two passes
    // Time O(n), Space O(k) distinct characters
    // Idea: Count every character, then return the first index whose count is 1.
    static class Approach2 {
        public int firstUniqChar(String s) {
            Map<Character, Integer> count = new HashMap<>();
            for (char c : s.toCharArray()) count.merge(c, 1, Integer::sum);
            for (int i = 0; i < s.length(); i++) if (count.get(s.charAt(i)) == 1) return i;
            return -1;
        }
    }

    // Approach 3: int[26] counts, two passes (optimal)
    // Time O(n), Space O(1)
    // Idea: Same idea with an array indexed by c - 'a', which is faster than a map for lowercase letters.
    static class Approach3 {
        public int firstUniqChar(String s) {
            int[] count = new int[26];
            for (char c : s.toCharArray()) count[c - 'a']++;
            for (int i = 0; i < s.length(); i++) if (count[s.charAt(i) - 'a'] == 1) return i;
            return -1;
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
        check("Approach 1", new Approach1().firstUniqChar("leetcode"), "0");
        check("Approach 1", new Approach1().firstUniqChar("loveleetcode"), "2");
        check("Approach 1", new Approach1().firstUniqChar("aabb"), "-1");
        check("Approach 2", new Approach2().firstUniqChar("leetcode"), "0");
        check("Approach 2", new Approach2().firstUniqChar("loveleetcode"), "2");
        check("Approach 2", new Approach2().firstUniqChar("aabb"), "-1");
        check("Approach 3", new Approach3().firstUniqChar("leetcode"), "0");
        check("Approach 3", new Approach3().firstUniqChar("loveleetcode"), "2");
        check("Approach 3", new Approach3().firstUniqChar("aabb"), "-1");
        System.out.println("FirstUniqueCharacterInAString: all 3 approaches passed " + passed + " checks");
    }
}
