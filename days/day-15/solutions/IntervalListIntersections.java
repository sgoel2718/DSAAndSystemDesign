import java.util.*;
import java.util.stream.*;

/**
 * Interval List Intersections (Medium) - Day 15
 * https://leetcode.com/problems/interval-list-intersections/
 *
 * Approach 1: Check every pair  |  Time O(m x n)  |  Space O(1) besides output
 * Approach 2: Two pointers (optimal)  |  Time O(m + n)  |  Space O(1) besides output  <- best
 *
 * Run: javac IntervalListIntersections.java && java IntervalListIntersections
 */
public class IntervalListIntersections {

    // Approach 1: Check every pair
    // Time O(m x n), Space O(1) besides output
    // Idea: Intersect every interval of the first list with every interval of the second. Both lists are sorted and disjoint, so the results come out in order.
    static class Approach1 {
        public int[][] intervalIntersection(int[][] firstList, int[][] secondList) {
            List<int[]> out = new ArrayList<>();
            for (int[] a : firstList)
                for (int[] b : secondList) {
                    int lo = Math.max(a[0], b[0]), hi = Math.min(a[1], b[1]);
                    if (lo <= hi) out.add(new int[]{lo, hi});
                }
            return out.toArray(new int[0][]);
        }
    }

    // Approach 2: Two pointers (optimal)
    // Time O(m + n), Space O(1) besides output
    // Idea: The intersection of the current pair is [max start, min end] if non-empty. Then advance whichever interval ends first, because it cannot meet anything later.
    static class Approach2 {
        public int[][] intervalIntersection(int[][] firstList, int[][] secondList) {
            List<int[]> out = new ArrayList<>();
            int i = 0, j = 0;
            while (i < firstList.length && j < secondList.length) {
                int lo = Math.max(firstList[i][0], secondList[j][0]);
                int hi = Math.min(firstList[i][1], secondList[j][1]);
                if (lo <= hi) out.add(new int[]{lo, hi});
                if (firstList[i][1] < secondList[j][1]) i++;
                else j++;
            }
            return out.toArray(new int[0][]);
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
        check("Approach 1", new Approach1().intervalIntersection(new int[][]{{0,2},{5,10},{13,23},{24,25}}, new int[][]{{1,5},{8,12},{15,24},{25,26}}), "[[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]");
        check("Approach 1", new Approach1().intervalIntersection(new int[][]{{1,3},{5,9}}, new int[][]{}), "[]");
        check("Approach 2", new Approach2().intervalIntersection(new int[][]{{0,2},{5,10},{13,23},{24,25}}, new int[][]{{1,5},{8,12},{15,24},{25,26}}), "[[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]");
        check("Approach 2", new Approach2().intervalIntersection(new int[][]{{1,3},{5,9}}, new int[][]{}), "[]");
        System.out.println("IntervalListIntersections: all 2 approaches passed " + passed + " checks");
    }
}
