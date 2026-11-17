import java.util.*;
import java.util.stream.*;

/**
 * Insert Interval (Medium) - Day 15
 * https://leetcode.com/problems/insert-interval/
 *
 * Approach 1: Append, sort, merge  |  Time O(n log n)  |  Space O(n)
 * Approach 2: One linear pass in three phases (optimal)  |  Time O(n)  |  Space O(n) output  <- best
 *
 * Run: javac InsertInterval.java && java InsertInterval
 */
public class InsertInterval {

    // Approach 1: Append, sort, merge
    // Time O(n log n), Space O(n)
    // Idea: Add the new interval and reuse the Merge Intervals solution. Ignores that the input is already sorted.
    static class Approach1 {
        public int[][] insert(int[][] intervals, int[] newInterval) {
            List<int[]> all = new ArrayList<>(Arrays.asList(intervals));
            all.add(newInterval);
            all.sort((a, b) -> Integer.compare(a[0], b[0]));
            List<int[]> out = new ArrayList<>();
            for (int[] cur : all) {
                if (out.isEmpty() || out.get(out.size() - 1)[1] < cur[0]) out.add(new int[]{cur[0], cur[1]});
                else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);
            }
            return out.toArray(new int[0][]);
        }
    }

    // Approach 2: One linear pass in three phases (optimal)
    // Time O(n), Space O(n) output
    // Idea: Copy intervals that end before the new one starts; merge every interval that overlaps it into it; copy the rest.
    static class Approach2 {
        public int[][] insert(int[][] intervals, int[] newInterval) {
            List<int[]> out = new ArrayList<>();
            int i = 0, n = intervals.length;
            int s = newInterval[0], e = newInterval[1];
            while (i < n && intervals[i][1] < s) out.add(intervals[i++]);
            while (i < n && intervals[i][0] <= e) {
                s = Math.min(s, intervals[i][0]);
                e = Math.max(e, intervals[i][1]);
                i++;
            }
            out.add(new int[]{s, e});
            while (i < n) out.add(intervals[i++]);
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
        check("Approach 1", new Approach1().insert(new int[][]{{1,3},{6,9}}, new int[]{2,5}), "[[1, 5], [6, 9]]");
        check("Approach 1", new Approach1().insert(new int[][]{{1,2},{3,5},{6,7},{8,10},{12,16}}, new int[]{4,8}), "[[1, 2], [3, 10], [12, 16]]");
        check("Approach 1", new Approach1().insert(new int[][]{}, new int[]{5,7}), "[[5, 7]]");
        check("Approach 2", new Approach2().insert(new int[][]{{1,3},{6,9}}, new int[]{2,5}), "[[1, 5], [6, 9]]");
        check("Approach 2", new Approach2().insert(new int[][]{{1,2},{3,5},{6,7},{8,10},{12,16}}, new int[]{4,8}), "[[1, 2], [3, 10], [12, 16]]");
        check("Approach 2", new Approach2().insert(new int[][]{}, new int[]{5,7}), "[[5, 7]]");
        System.out.println("InsertInterval: all 2 approaches passed " + passed + " checks");
    }
}
