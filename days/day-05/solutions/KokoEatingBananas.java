import java.util.*;
import java.util.stream.*;

/**
 * Koko Eating Bananas (Medium) - Day 5
 * https://leetcode.com/problems/koko-eating-bananas/
 *
 * Approach 1: Try every speed from 1 upward  |  Time O(max pile x n)  |  Space O(1)
 * Approach 2: Binary search on the speed (optimal)  |  Time O(n log max)  |  Space O(1)  <- best
 *
 * Run: javac KokoEatingBananas.java && java KokoEatingBananas
 */
public class KokoEatingBananas {

    // Approach 1: Try every speed from 1 upward
    // Time O(max pile x n), Space O(1)
    // Idea: The first speed that finishes within h hours is the answer.
    static class Approach1 {
        public int minEatingSpeed(int[] piles, int h) {
            for (int k = 1; ; k++) {
                long hours = 0;
                for (int p : piles) hours += (p + k - 1) / k;
                if (hours <= h) return k;
            }
        }
    }

    // Approach 2: Binary search on the speed (optimal)
    // Time O(n log max), Space O(1)
    // Idea: Hours needed only goes down as speed goes up, so binary search the smallest speed in [1, max pile] that finishes in time.
    static class Approach2 {
        public int minEatingSpeed(int[] piles, int h) {
            int lo = 1, hi = 0;
            for (int p : piles) hi = Math.max(hi, p);
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                long hours = 0;
                for (int p : piles) hours += (p + mid - 1) / mid;
                if (hours <= h) hi = mid;
                else lo = mid + 1;
            }
            return lo;
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
        check("Approach 1", new Approach1().minEatingSpeed(new int[]{3,6,7,11}, 8), "4");
        check("Approach 1", new Approach1().minEatingSpeed(new int[]{30,11,23,4,20}, 5), "30");
        check("Approach 1", new Approach1().minEatingSpeed(new int[]{30,11,23,4,20}, 6), "23");
        check("Approach 2", new Approach2().minEatingSpeed(new int[]{3,6,7,11}, 8), "4");
        check("Approach 2", new Approach2().minEatingSpeed(new int[]{30,11,23,4,20}, 5), "30");
        check("Approach 2", new Approach2().minEatingSpeed(new int[]{30,11,23,4,20}, 6), "23");
        System.out.println("KokoEatingBananas: all 2 approaches passed " + passed + " checks");
    }
}
