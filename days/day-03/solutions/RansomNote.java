import java.util.*;
import java.util.stream.*;

/**
 * Ransom Note (Easy) - Day 3
 * https://leetcode.com/problems/ransom-note/
 *
 * Approach 1: Remove each used letter from the magazine  |  Time O(m x n)  |  Space O(n)
 * Approach 2: HashMap of counts  |  Time O(m + n)  |  Space O(k)
 * Approach 3: int[26] counts (optimal)  |  Time O(m + n)  |  Space O(1)  <- best
 *
 * Run: javac RansomNote.java && java RansomNote
 */
public class RansomNote {

    // Approach 1: Remove each used letter from the magazine
    // Time O(m x n), Space O(n)
    // Idea: For every note letter, find and delete one copy in a StringBuilder of the magazine.
    static class Approach1 {
        public boolean canConstruct(String ransomNote, String magazine) {
            StringBuilder mag = new StringBuilder(magazine);
            for (char c : ransomNote.toCharArray()) {
                int i = mag.indexOf(String.valueOf(c));
                if (i < 0) return false;
                mag.deleteCharAt(i);
            }
            return true;
        }
    }

    // Approach 2: HashMap of counts
    // Time O(m + n), Space O(k)
    // Idea: Count the magazine's letters, then spend one for each note letter; fail if a count goes below zero.
    static class Approach2 {
        public boolean canConstruct(String ransomNote, String magazine) {
            Map<Character, Integer> have = new HashMap<>();
            for (char c : magazine.toCharArray()) have.merge(c, 1, Integer::sum);
            for (char c : ransomNote.toCharArray()) {
                if (have.merge(c, -1, Integer::sum) < 0) return false;
            }
            return true;
        }
    }

    // Approach 3: int[26] counts (optimal)
    // Time O(m + n), Space O(1)
    // Idea: Same with an array of 26 counts.
    static class Approach3 {
        public boolean canConstruct(String ransomNote, String magazine) {
            if (ransomNote.length() > magazine.length()) return false;
            int[] have = new int[26];
            for (char c : magazine.toCharArray()) have[c - 'a']++;
            for (char c : ransomNote.toCharArray()) if (--have[c - 'a'] < 0) return false;
            return true;
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
        check("Approach 1", new Approach1().canConstruct("a", "b"), "false");
        check("Approach 1", new Approach1().canConstruct("aa", "ab"), "false");
        check("Approach 1", new Approach1().canConstruct("aa", "aab"), "true");
        check("Approach 2", new Approach2().canConstruct("a", "b"), "false");
        check("Approach 2", new Approach2().canConstruct("aa", "ab"), "false");
        check("Approach 2", new Approach2().canConstruct("aa", "aab"), "true");
        check("Approach 3", new Approach3().canConstruct("a", "b"), "false");
        check("Approach 3", new Approach3().canConstruct("aa", "ab"), "false");
        check("Approach 3", new Approach3().canConstruct("aa", "aab"), "true");
        System.out.println("RansomNote: all 3 approaches passed " + passed + " checks");
    }
}
