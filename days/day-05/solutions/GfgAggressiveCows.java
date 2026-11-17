import java.util.*;
import java.util.stream.*;

/**
 * Aggressive Cows (Medium) - Day 5
 * https://leetcode.com/problems/gfg-aggressive-cows/
 *
 * Approach 1: Try every distance from 1 upward  |  Time O(n x range)  |  Space O(1)
 * Approach 2: Binary search on the answer (optimal)  |  Time O(n log n + n log range)  |  Space O(1)  <- best
 *
 * Run: javac GfgAggressiveCows.java && java GfgAggressiveCows
 */
public class GfgAggressiveCows {

    // Approach 1: Try every distance from 1 upward
    // Time O(n x range), Space O(1)
    // Idea: Sort the stalls. Place cows greedily (first stall, then the next stall at least d away). The answer is the largest d that still fits all k cows.
    static class Approach1 {
        public int aggressiveCows(int[] stalls, int k) {
            int[] s = stalls.clone();
            Arrays.sort(s);
            int best = 0;
            for (int d = 1; d <= s[s.length - 1] - s[0]; d++) {
                if (canPlace(s, d, k)) best = d;
                else break;
            }
            return best;
        }
        private boolean canPlace(int[] s, int d, int k) {
            int cows = 1, last = s[0];
            for (int i = 1; i < s.length; i++) {
                if (s[i] - last >= d) { cows++; last = s[i]; }
            }
            return cows >= k;
        }
    }

    // Approach 2: Binary search on the answer (optimal)
    // Time O(n log n + n log range), Space O(1)
    // Idea: If k cows fit with gap d, they fit with any smaller gap. Binary search the largest d in [1, max - min] for which greedy placement works.
    static class Approach2 {
        public int aggressiveCows(int[] stalls, int k) {
            int[] s = stalls.clone();
            Arrays.sort(s);
            int lo = 1, hi = s[s.length - 1] - s[0], best = 0;
            while (lo <= hi) {
                int mid = lo + (hi - lo) / 2;
                if (canPlace(s, mid, k)) { best = mid; lo = mid + 1; }
                else hi = mid - 1;
            }
            return best;
        }
        private boolean canPlace(int[] s, int d, int k) {
            int cows = 1, last = s[0];
            for (int i = 1; i < s.length; i++) {
                if (s[i] - last >= d) { cows++; last = s[i]; }
            }
            return cows >= k;
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
        check("Approach 1", new Approach1().aggressiveCows(new int[]{1,2,4,8,9}, 3), "3");
        check("Approach 1", new Approach1().aggressiveCows(new int[]{10,1,2,7,5}, 3), "4");
        check("Approach 1", new Approach1().aggressiveCows(new int[]{2,12,11,3,26,7}, 5), "1");
        check("Approach 2", new Approach2().aggressiveCows(new int[]{1,2,4,8,9}, 3), "3");
        check("Approach 2", new Approach2().aggressiveCows(new int[]{10,1,2,7,5}, 3), "4");
        check("Approach 2", new Approach2().aggressiveCows(new int[]{2,12,11,3,26,7}, 5), "1");
        System.out.println("GfgAggressiveCows: all 2 approaches passed " + passed + " checks");
    }
}
