import java.util.*;
import java.util.stream.*;

/**
 * Employee Free Time (Hard) - Day 15
 * https://leetcode.com/problems/codertrain-employee-free-time/
 *
 * Approach 1: Flatten, sort, merge, read the gaps  |  Time O(N log N) for N intervals  |  Space O(N)
 * Approach 2: K-way merge with a min-heap (optimal)  |  Time O(N log k) for k employees  |  Space O(k)  <- best
 *
 * Run: javac CodertrainEmployeeFreeTime.java && java CodertrainEmployeeFreeTime
 */
public class CodertrainEmployeeFreeTime {

    // Approach 1: Flatten, sort, merge, read the gaps
    // Time O(N log N) for N intervals, Space O(N)
    // Idea: Put every working interval of every employee in one list, sort by start, merge overlaps; the gaps between merged intervals are the common free time.
    static class Approach1 {
        public int[][] employeeFreeTime(int[][][] schedule) {
            List<int[]> all = new ArrayList<>();
            for (int[][] emp : schedule) all.addAll(Arrays.asList(emp));
            all.sort((a, b) -> Integer.compare(a[0], b[0]));
            List<int[]> free = new ArrayList<>();
            int end = all.get(0)[1];
            for (int[] cur : all) {
                if (cur[0] > end) free.add(new int[]{end, cur[0]});
                end = Math.max(end, cur[1]);
            }
            return free.toArray(new int[0][]);
        }
    }

    // Approach 2: K-way merge with a min-heap (optimal)
    // Time O(N log k) for k employees, Space O(k)
    // Idea: Each employee's list is already sorted. A heap holding one interval per employee yields all intervals in start order without a full sort; track the latest end and record gaps.
    static class Approach2 {
        public int[][] employeeFreeTime(int[][][] schedule) {
            PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> Integer.compare(schedule[a[0]][a[1]][0], schedule[b[0]][b[1]][0]));
            for (int e = 0; e < schedule.length; e++) if (schedule[e].length > 0) pq.offer(new int[]{e, 0});
            List<int[]> free = new ArrayList<>();
            int end = -1;
            while (!pq.isEmpty()) {
                int[] top = pq.poll();
                int[] cur = schedule[top[0]][top[1]];
                if (end != -1 && cur[0] > end) free.add(new int[]{end, cur[0]});
                end = Math.max(end, cur[1]);
                if (top[1] + 1 < schedule[top[0]].length) pq.offer(new int[]{top[0], top[1] + 1});
            }
            return free.toArray(new int[0][]);
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
        check("Approach 1", new Approach1().employeeFreeTime(new int[][][]{{{1,2},{5,6}},{{1,3}},{{4,10}}}), "[[3, 4]]");
        check("Approach 1", new Approach1().employeeFreeTime(new int[][][]{{{1,3},{6,7}},{{2,4}},{{2,5},{9,12}}}), "[[5, 6], [7, 9]]");
        check("Approach 2", new Approach2().employeeFreeTime(new int[][][]{{{1,2},{5,6}},{{1,3}},{{4,10}}}), "[[3, 4]]");
        check("Approach 2", new Approach2().employeeFreeTime(new int[][][]{{{1,3},{6,7}},{{2,4}},{{2,5},{9,12}}}), "[[5, 6], [7, 9]]");
        System.out.println("CodertrainEmployeeFreeTime: all 2 approaches passed " + passed + " checks");
    }
}
