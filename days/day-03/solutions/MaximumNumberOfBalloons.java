import java.util.*;
import java.util.stream.*;

/**
 * Maximum Number of Balloons (Easy) - Day 3
 * https://leetcode.com/problems/maximum-number-of-balloons/
 *
 * Approach 1: Simulate: build balloons one at a time  |  Time O(n + answer)  |  Space O(1)
 * Approach 2: HashMap of counts  |  Time O(n)  |  Space O(1)
 * Approach 3: int[26] counts (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MaximumNumberOfBalloons.java && java MaximumNumberOfBalloons
 */
public class MaximumNumberOfBalloons {

    // Approach 1: Simulate: build balloons one at a time
    // Time O(n + answer), Space O(1)
    // Idea: Count the letters, then keep spending b, a, l, l, o, o, n until one runs out.
    static class Approach1 {
        public int maxNumberOfBalloons(String text) {
            int[] c = new int[26];
            for (char ch : text.toCharArray()) c[ch - 'a']++;
            int made = 0;
            while (true) {
                for (char ch : "balloon".toCharArray()) {
                    if (c[ch - 'a'] == 0) return made;
                    c[ch - 'a']--;
                }
                made++;
            }
        }
    }

    // Approach 2: HashMap of counts
    // Time O(n), Space O(1)
    // Idea: Each balloon needs b, a, n once and l, o twice: the answer is the smallest of count / need over those letters.
    static class Approach2 {
        public int maxNumberOfBalloons(String text) {
            Map<Character, Integer> have = new HashMap<>(), need = new HashMap<>();
            for (char ch : text.toCharArray()) have.merge(ch, 1, Integer::sum);
            for (char ch : "balloon".toCharArray()) need.merge(ch, 1, Integer::sum);
            int best = Integer.MAX_VALUE;
            for (Map.Entry<Character, Integer> e : need.entrySet())
                best = Math.min(best, have.getOrDefault(e.getKey(), 0) / e.getValue());
            return best;
        }
    }

    // Approach 3: int[26] counts (optimal)
    // Time O(n), Space O(1)
    // Idea: Same formula with an array: min(b, a, l / 2, o / 2, n).
    static class Approach3 {
        public int maxNumberOfBalloons(String text) {
            int[] c = new int[26];
            for (char ch : text.toCharArray()) c[ch - 'a']++;
            return Math.min(Math.min(c['b' - 'a'], c['a' - 'a']),
                   Math.min(Math.min(c['l' - 'a'] / 2, c['o' - 'a'] / 2), c['n' - 'a']));
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
        check("Approach 1", new Approach1().maxNumberOfBalloons("nlaebolko"), "1");
        check("Approach 1", new Approach1().maxNumberOfBalloons("loonbalxballpoon"), "2");
        check("Approach 1", new Approach1().maxNumberOfBalloons("leetcode"), "0");
        check("Approach 2", new Approach2().maxNumberOfBalloons("nlaebolko"), "1");
        check("Approach 2", new Approach2().maxNumberOfBalloons("loonbalxballpoon"), "2");
        check("Approach 2", new Approach2().maxNumberOfBalloons("leetcode"), "0");
        check("Approach 3", new Approach3().maxNumberOfBalloons("nlaebolko"), "1");
        check("Approach 3", new Approach3().maxNumberOfBalloons("loonbalxballpoon"), "2");
        check("Approach 3", new Approach3().maxNumberOfBalloons("leetcode"), "0");
        System.out.println("MaximumNumberOfBalloons: all 3 approaches passed " + passed + " checks");
    }
}
