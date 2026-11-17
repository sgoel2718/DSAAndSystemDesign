import java.util.*;
import java.util.stream.*;

/**
 * Attend All Meetings II (Minimum Meeting Rooms) (Medium) - Day 15
 * https://leetcode.com/problems/gfg-attend-all-meetings-ii/
 *
 * Approach 1: Count meetings running at each start time  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sort by start + min-heap of end times  |  Time O(n log n)  |  Space O(n)
 * Approach 3: Sorted starts and sorted ends, two pointers (optimal)  |  Time O(n log n)  |  Space O(n)  <- best
 *
 * Run: javac GfgAttendAllMeetingsIi.java && java GfgAttendAllMeetingsIi
 */
public class GfgAttendAllMeetingsIi {

    // Approach 1: Count meetings running at each start time
    // Time O(n^2), Space O(1)
    // Idea: The rooms needed is the largest number of meetings in progress at any meeting's start time.
    static class Approach1 {
        public int minMeetingRooms(int[] start, int[] end) {
            int best = 0;
            for (int i = 0; i < start.length; i++) {
                int running = 0;
                for (int j = 0; j < start.length; j++)
                    if (start[j] <= start[i] && start[i] < end[j]) running++;
                best = Math.max(best, running);
            }
            return best;
        }
    }

    // Approach 2: Sort by start + min-heap of end times
    // Time O(n log n), Space O(n)
    // Idea: Process meetings by start time. The heap holds the end times of rooms in use; if the earliest one has ended, reuse that room.
    static class Approach2 {
        public int minMeetingRooms(int[] start, int[] end) {
            int n = start.length;
            Integer[] idx = new Integer[n];
            for (int i = 0; i < n; i++) idx[i] = i;
            Arrays.sort(idx, (a, b) -> Integer.compare(start[a], start[b]));
            PriorityQueue<Integer> ends = new PriorityQueue<>();
            for (int i : idx) {
                if (!ends.isEmpty() && ends.peek() <= start[i]) ends.poll();
                ends.offer(end[i]);
            }
            return ends.size();
        }
    }

    // Approach 3: Sorted starts and sorted ends, two pointers (optimal)
    // Time O(n log n), Space O(n)
    // Idea: Walk the sorted start times; a room frees up whenever the next end time is <= the current start. Track the peak number of rooms in use.
    static class Approach3 {
        public int minMeetingRooms(int[] start, int[] end) {
            int[] s = start.clone(), e = end.clone();
            Arrays.sort(s);
            Arrays.sort(e);
            int rooms = 0, best = 0, j = 0;
            for (int i = 0; i < s.length; i++) {
                while (e[j] <= s[i]) { j++; rooms--; }
                rooms++;
                best = Math.max(best, rooms);
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
        check("Approach 1", new Approach1().minMeetingRooms(new int[]{1,10,7}, new int[]{4,15,10}), "1");
        check("Approach 1", new Approach1().minMeetingRooms(new int[]{2,9,6}, new int[]{4,12,10}), "2");
        check("Approach 1", new Approach1().minMeetingRooms(new int[]{0,5,15}, new int[]{30,10,20}), "2");
        check("Approach 2", new Approach2().minMeetingRooms(new int[]{1,10,7}, new int[]{4,15,10}), "1");
        check("Approach 2", new Approach2().minMeetingRooms(new int[]{2,9,6}, new int[]{4,12,10}), "2");
        check("Approach 2", new Approach2().minMeetingRooms(new int[]{0,5,15}, new int[]{30,10,20}), "2");
        check("Approach 3", new Approach3().minMeetingRooms(new int[]{1,10,7}, new int[]{4,15,10}), "1");
        check("Approach 3", new Approach3().minMeetingRooms(new int[]{2,9,6}, new int[]{4,12,10}), "2");
        check("Approach 3", new Approach3().minMeetingRooms(new int[]{0,5,15}, new int[]{30,10,20}), "2");
        System.out.println("GfgAttendAllMeetingsIi: all 3 approaches passed " + passed + " checks");
    }
}
