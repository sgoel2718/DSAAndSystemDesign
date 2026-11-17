import java.util.*;
import java.util.stream.*;

/**
 * Minimum Number of Days to Make m Bouquets (Medium) - Day 5
 * https://leetcode.com/problems/minimum-number-of-days-to-make-m-bouquets/
 *
 * Approach 1: Try every distinct bloom day in order  |  Time O(n^2)  |  Space O(n)
 * Approach 2: Binary search on the day (optimal)  |  Time O(n log(max day))  |  Space O(1)  <- best
 *
 * Run: javac MinimumNumberOfDaysToMakeMBouquets.java && java MinimumNumberOfDaysToMakeMBouquets
 */
public class MinimumNumberOfDaysToMakeMBouquets {

    // Approach 1: Try every distinct bloom day in order
    // Time O(n^2), Space O(n)
    // Idea: The answer is one of the bloom days. Sort the distinct days and return the first on which m bouquets of k adjacent flowers can be made.
    static class Approach1 {
        public int minDays(int[] bloomDay, int m, int k) {
            if ((long) m * k > bloomDay.length) return -1;
            int[] days = Arrays.stream(bloomDay).distinct().sorted().toArray();
            for (int d : days) if (canMake(bloomDay, d, m, k)) return d;
            return -1;
        }
        private boolean canMake(int[] b, int day, int m, int k) {
            int made = 0, run = 0;
            for (int x : b) {
                run = x <= day ? run + 1 : 0;
                if (run == k) { made++; run = 0; }
            }
            return made >= m;
        }
    }

    // Approach 2: Binary search on the day (optimal)
    // Time O(n log(max day)), Space O(1)
    // Idea: If it is possible by day d, it is possible on any later day. Binary search the smallest such day between min and max bloom day.
    static class Approach2 {
        public int minDays(int[] bloomDay, int m, int k) {
            if ((long) m * k > bloomDay.length) return -1;
            int lo = Integer.MAX_VALUE, hi = 0;
            for (int x : bloomDay) { lo = Math.min(lo, x); hi = Math.max(hi, x); }
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (canMake(bloomDay, mid, m, k)) hi = mid;
                else lo = mid + 1;
            }
            return lo;
        }
        private boolean canMake(int[] b, int day, int m, int k) {
            int made = 0, run = 0;
            for (int x : b) {
                run = x <= day ? run + 1 : 0;
                if (run == k) { made++; run = 0; }
            }
            return made >= m;
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
        check("Approach 1", new Approach1().minDays(new int[]{1,10,3,10,2}, 3, 1), "3");
        check("Approach 1", new Approach1().minDays(new int[]{1,10,3,10,2}, 3, 2), "-1");
        check("Approach 1", new Approach1().minDays(new int[]{7,7,7,7,12,7,7}, 2, 3), "12");
        check("Approach 2", new Approach2().minDays(new int[]{1,10,3,10,2}, 3, 1), "3");
        check("Approach 2", new Approach2().minDays(new int[]{1,10,3,10,2}, 3, 2), "-1");
        check("Approach 2", new Approach2().minDays(new int[]{7,7,7,7,12,7,7}, 2, 3), "12");
        System.out.println("MinimumNumberOfDaysToMakeMBouquets: all 2 approaches passed " + passed + " checks");
    }
}
