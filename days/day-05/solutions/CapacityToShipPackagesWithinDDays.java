import java.util.*;
import java.util.stream.*;

/**
 * Capacity To Ship Packages Within D Days (Medium) - Day 5
 * https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/
 *
 * Approach 1: Try every capacity from the heaviest package upward  |  Time O(n x (sum - max))  |  Space O(1)
 * Approach 2: Binary search on the capacity (optimal)  |  Time O(n log sum)  |  Space O(1)  <- best
 *
 * Run: javac CapacityToShipPackagesWithinDDays.java && java CapacityToShipPackagesWithinDDays
 */
public class CapacityToShipPackagesWithinDDays {

    // Approach 1: Try every capacity from the heaviest package upward
    // Time O(n x (sum - max)), Space O(1)
    // Idea: The capacity must be at least the heaviest package. Simulate loading for each capacity and return the first that needs <= days.
    static class Approach1 {
        public int shipWithinDays(int[] weights, int days) {
            int max = 0, sum = 0;
            for (int w : weights) { max = Math.max(max, w); sum += w; }
            for (int cap = max; cap <= sum; cap++) if (daysNeeded(weights, cap) <= days) return cap;
            return sum;
        }
        private int daysNeeded(int[] w, int cap) {
            int d = 1, load = 0;
            for (int x : w) {
                if (load + x > cap) { d++; load = 0; }
                load += x;
            }
            return d;
        }
    }

    // Approach 2: Binary search on the capacity (optimal)
    // Time O(n log sum), Space O(1)
    // Idea: Days needed only goes down as capacity grows; binary search the smallest capacity in [max, sum] that fits.
    static class Approach2 {
        public int shipWithinDays(int[] weights, int days) {
            int lo = 0, hi = 0;
            for (int w : weights) { lo = Math.max(lo, w); hi += w; }
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2;
                if (daysNeeded(weights, mid) <= days) hi = mid;
                else lo = mid + 1;
            }
            return lo;
        }
        private int daysNeeded(int[] w, int cap) {
            int d = 1, load = 0;
            for (int x : w) {
                if (load + x > cap) { d++; load = 0; }
                load += x;
            }
            return d;
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
        check("Approach 1", new Approach1().shipWithinDays(new int[]{1,2,3,4,5,6,7,8,9,10}, 5), "15");
        check("Approach 1", new Approach1().shipWithinDays(new int[]{3,2,2,4,1,4}, 3), "6");
        check("Approach 1", new Approach1().shipWithinDays(new int[]{1,2,3,1,1}, 4), "3");
        check("Approach 2", new Approach2().shipWithinDays(new int[]{1,2,3,4,5,6,7,8,9,10}, 5), "15");
        check("Approach 2", new Approach2().shipWithinDays(new int[]{3,2,2,4,1,4}, 3), "6");
        check("Approach 2", new Approach2().shipWithinDays(new int[]{1,2,3,1,1}, 4), "3");
        System.out.println("CapacityToShipPackagesWithinDDays: all 2 approaches passed " + passed + " checks");
    }
}
