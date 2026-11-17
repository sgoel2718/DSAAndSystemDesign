import java.util.*;
import java.util.stream.*;

/**
 * Merge Intervals (Medium) - Day 15
 * https://leetcode.com/problems/merge-intervals/
 *
 * Approach 1: Merge each interval into everything it overlaps  |  Time O(n^2)  |  Space O(n)
 * Approach 2: Sort by start, then one merge pass (optimal)  |  Time O(n log n)  |  Space O(n) output  <- best
 *
 * Run: javac MergeIntervals.java && java MergeIntervals
 */
public class MergeIntervals {

    // Approach 1: Merge each interval into everything it overlaps
    // Time O(n^2), Space O(n)
    // Idea: Process intervals one by one; absorb every already-kept interval that overlaps the current one, then keep the merged result. Sort the output at the end.
    static class Approach1 {
        public int[][] merge(int[][] intervals) {
            List<int[]> kept = new ArrayList<>();
            for (int[] in : intervals) {
                int[] cur = {in[0], in[1]};
                Iterator<int[]> it = kept.iterator();
                while (it.hasNext()) {
                    int[] k = it.next();
                    if (k[0] <= cur[1] && cur[0] <= k[1]) {
                        cur[0] = Math.min(cur[0], k[0]);
                        cur[1] = Math.max(cur[1], k[1]);
                        it.remove();
                    }
                }
                kept.add(cur);
            }
            kept.sort((a, b) -> Integer.compare(a[0], b[0]));
            return kept.toArray(new int[0][]);
        }
    }

    // Approach 2: Sort by start, then one merge pass (optimal)
    // Time O(n log n), Space O(n) output
    // Idea: After sorting, an interval overlaps the last merged one exactly when its start <= that end; extend the end, otherwise start a new interval.
    static class Approach2 {
        public int[][] merge(int[][] intervals) {
            Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
            List<int[]> out = new ArrayList<>();
            for (int[] cur : intervals) {
                if (out.isEmpty() || out.get(out.size() - 1)[1] < cur[0]) out.add(new int[]{cur[0], cur[1]});
                else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);
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
        check("Approach 1", new Approach1().merge(new int[][]{{1,3},{2,6},{8,10},{15,18}}), "[[1, 6], [8, 10], [15, 18]]");
        check("Approach 1", new Approach1().merge(new int[][]{{1,4},{4,5}}), "[[1, 5]]");
        check("Approach 1", new Approach1().merge(new int[][]{{1,4},{0,4}}), "[[0, 4]]");
        check("Approach 1", new Approach1().merge(new int[][]{{2,3},{4,5},{6,7},{8,9},{1,10}}), "[[1, 10]]");
        check("Approach 2", new Approach2().merge(new int[][]{{1,3},{2,6},{8,10},{15,18}}), "[[1, 6], [8, 10], [15, 18]]");
        check("Approach 2", new Approach2().merge(new int[][]{{1,4},{4,5}}), "[[1, 5]]");
        check("Approach 2", new Approach2().merge(new int[][]{{1,4},{0,4}}), "[[0, 4]]");
        check("Approach 2", new Approach2().merge(new int[][]{{2,3},{4,5},{6,7},{8,9},{1,10}}), "[[1, 10]]");
        System.out.println("MergeIntervals: all 2 approaches passed " + passed + " checks");
    }
}
