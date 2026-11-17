import java.util.*;
import java.util.stream.*;

/**
 * Count Triplets with Sum Smaller than X (Medium) - Day 2
 * https://leetcode.com/problems/gfg-count-triplets-with-sum-smaller-than-x/
 *
 * Approach 1: Brute force: every triplet  |  Time O(n^3)  |  Space O(1)
 * Approach 2: Sort + two pointers, count a whole block at once (optimal)  |  Time O(n^2)  |  Space O(log n) sort stack  <- best
 *
 * Run: javac GfgCountTripletsWithSumSmallerThanX.java && java GfgCountTripletsWithSumSmallerThanX
 */
public class GfgCountTripletsWithSumSmallerThanX {

    // Approach 1: Brute force: every triplet
    // Time O(n^3), Space O(1)
    // Idea: Count every triplet whose sum is below the target.
    static class Approach1 {
        public long countTriplets(int[] arr, int sum) {
            long count = 0;
            int n = arr.length;
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++)
                    for (int k = j + 1; k < n; k++)
                        if (arr[i] + arr[j] + arr[k] < sum) count++;
            return count;
        }
    }

    // Approach 2: Sort + two pointers, count a whole block at once (optimal)
    // Time O(n^2), Space O(log n) sort stack
    // Idea: Sort, fix i. If arr[i] + arr[l] + arr[r] < sum, then every r' in (l, r] also works with l, so add r - l and move l. Otherwise move r.
    static class Approach2 {
        public long countTriplets(int[] arr, int sum) {
            Arrays.sort(arr);
            long count = 0;
            for (int i = 0; i < arr.length - 2; i++) {
                int l = i + 1, r = arr.length - 1;
                while (l < r) {
                    if (arr[i] + arr[l] + arr[r] < sum) {
                        count += r - l;
                        l++;
                    } else r--;
                }
            }
            return count;
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
        check("Approach 1", new Approach1().countTriplets(new int[]{-2,0,1,3}, 2), "2");
        check("Approach 1", new Approach1().countTriplets(new int[]{5,1,3,4,7}, 12), "4");
        check("Approach 2", new Approach2().countTriplets(new int[]{-2,0,1,3}, 2), "2");
        check("Approach 2", new Approach2().countTriplets(new int[]{5,1,3,4,7}, 12), "4");
        System.out.println("GfgCountTripletsWithSumSmallerThanX: all 2 approaches passed " + passed + " checks");
    }
}
