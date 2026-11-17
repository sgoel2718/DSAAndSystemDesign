import java.util.*;
import java.util.stream.*;

/**
 * Maximum CPU Load (Hard) - Day 15
 * https://leetcode.com/problems/gfg-maximum-cpu-load/
 *
 * Approach 1: Sum the loads running at each job's start  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sort by start + min-heap by end time (optimal)  |  Time O(n log n)  |  Space O(n)  <- best
 *
 * Run: javac GfgMaximumCpuLoad.java && java GfgMaximumCpuLoad
 */
public class GfgMaximumCpuLoad {

    // Approach 1: Sum the loads running at each job's start
    // Time O(n^2), Space O(1)
    // Idea: The peak load happens at some job's start time: add up the loads of all jobs running at that moment.
    static class Approach1 {
        public int maxCPULoad(int[][] jobs) {
            int best = 0;
            for (int[] a : jobs) {
                int load = 0;
                for (int[] b : jobs) if (b[0] <= a[0] && a[0] < b[1]) load += b[2];
                best = Math.max(best, load);
            }
            return best;
        }
    }

    // Approach 2: Sort by start + min-heap by end time (optimal)
    // Time O(n log n), Space O(n)
    // Idea: Process jobs by start time; remove finished jobs (end <= current start) from a heap ordered by end, subtracting their load; add the current job and track the peak.
    static class Approach2 {
        public int maxCPULoad(int[][] jobs) {
            int[][] a = jobs.clone();
            Arrays.sort(a, (x, y) -> Integer.compare(x[0], y[0]));
            PriorityQueue<int[]> running = new PriorityQueue<>((x, y) -> Integer.compare(x[1], y[1]));
            int load = 0, best = 0;
            for (int[] job : a) {
                while (!running.isEmpty() && running.peek()[1] <= job[0]) load -= running.poll()[2];
                running.offer(job);
                load += job[2];
                best = Math.max(best, load);
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
        check("Approach 1", new Approach1().maxCPULoad(new int[][]{{1,4,3},{2,5,4},{7,9,6}}), "7");
        check("Approach 1", new Approach1().maxCPULoad(new int[][]{{6,7,10},{2,4,11},{8,12,15}}), "15");
        check("Approach 1", new Approach1().maxCPULoad(new int[][]{{1,4,2},{2,4,1},{3,6,5}}), "8");
        check("Approach 2", new Approach2().maxCPULoad(new int[][]{{1,4,3},{2,5,4},{7,9,6}}), "7");
        check("Approach 2", new Approach2().maxCPULoad(new int[][]{{6,7,10},{2,4,11},{8,12,15}}), "15");
        check("Approach 2", new Approach2().maxCPULoad(new int[][]{{1,4,2},{2,4,1},{3,6,5}}), "8");
        System.out.println("GfgMaximumCpuLoad: all 2 approaches passed " + passed + " checks");
    }
}
