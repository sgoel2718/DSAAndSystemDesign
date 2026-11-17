import java.util.*;
import java.util.stream.*;

/**
 * Maximum Candies Allocated to K Children (Medium) - Day 5
 * https://leetcode.com/problems/maximum-candies-allocated-to-k-children/
 *
 * Approach 1: Try every pile size from the largest down  |  Time O(max pile x n)  |  Space O(1)
 * Approach 2: Binary search on the size (optimal)  |  Time O(n log max)  |  Space O(1)  <- best
 *
 * Run: javac MaximumCandiesAllocatedToKChildren.java && java MaximumCandiesAllocatedToKChildren
 */
public class MaximumCandiesAllocatedToKChildren {

    // Approach 1: Try every pile size from the largest down
    // Time O(max pile x n), Space O(1)
    // Idea: For a size c, piles can be split into sum(p / c) portions. Return the largest c giving at least k portions.
    static class Approach1 {
        public int maximumCandies(int[] candies, long k) {
            int max = 0;
            for (int c : candies) max = Math.max(max, c);
            for (int size = max; size >= 1; size--) {
                long parts = 0;
                for (int c : candies) parts += c / size;
                if (parts >= k) return size;
            }
            return 0;
        }
    }

    // Approach 2: Binary search on the size (optimal)
    // Time O(n log max), Space O(1)
    // Idea: Portions only go down as the size grows, so binary search the largest size whose portion count is at least k.
    static class Approach2 {
        public int maximumCandies(int[] candies, long k) {
            int lo = 1, hi = 0, best = 0;
            for (int c : candies) hi = Math.max(hi, c);
            while (lo <= hi) {
                int mid = lo + (hi - lo) / 2;
                long parts = 0;
                for (int c : candies) parts += c / mid;
                if (parts >= k) { best = mid; lo = mid + 1; }
                else hi = mid - 1;
            }
            return best;
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
        check("Approach 1", new Approach1().maximumCandies(new int[]{5,8,6}, 3L), "5");
        check("Approach 1", new Approach1().maximumCandies(new int[]{2,5}, 11L), "0");
        check("Approach 1", new Approach1().maximumCandies(new int[]{4,7,5}, 4L), "3");
        check("Approach 2", new Approach2().maximumCandies(new int[]{5,8,6}, 3L), "5");
        check("Approach 2", new Approach2().maximumCandies(new int[]{2,5}, 11L), "0");
        check("Approach 2", new Approach2().maximumCandies(new int[]{4,7,5}, 4L), "3");
        System.out.println("MaximumCandiesAllocatedToKChildren: all 2 approaches passed " + passed + " checks");
    }
}
