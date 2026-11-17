import java.util.*;
import java.util.stream.*;

/**
 * Daily Temperatures (Medium) - Day 7
 * https://leetcode.com/problems/daily-temperatures/
 *
 * Approach 1: Brute force: scan right for each day  |  Time O(n^2)  |  Space O(1) besides output
 * Approach 2: Monotonic decreasing stack (optimal)  |  Time O(n)  |  Space O(n)  <- best
 * Approach 3: Right to left, jump using answers already found  |  Time O(n) amortised  |  Space O(1) besides output
 *
 * Run: javac DailyTemperatures.java && java DailyTemperatures
 */
public class DailyTemperatures {

    // Approach 1: Brute force: scan right for each day
    // Time O(n^2), Space O(1) besides output
    // Idea: For every day look ahead for the first warmer day.
    static class Approach1 {
        public int[] dailyTemperatures(int[] temperatures) {
            int n = temperatures.length;
            int[] ans = new int[n];
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++)
                    if (temperatures[j] > temperatures[i]) { ans[i] = j - i; break; }
            return ans;
        }
    }

    // Approach 2: Monotonic decreasing stack (optimal)
    // Time O(n), Space O(n)
    // Idea: Keep indices of days still waiting for a warmer day, temperatures decreasing. A warmer day pops every cooler waiting day and fills in its answer.
    static class Approach2 {
        public int[] dailyTemperatures(int[] temperatures) {
            int n = temperatures.length;
            int[] ans = new int[n];
            Deque<Integer> st = new ArrayDeque<>();
            for (int i = 0; i < n; i++) {
                while (!st.isEmpty() && temperatures[i] > temperatures[st.peek()]) {
                    int j = st.pop();
                    ans[j] = i - j;
                }
                st.push(i);
            }
            return ans;
        }
    }

    // Approach 3: Right to left, jump using answers already found
    // Time O(n) amortised, Space O(1) besides output
    // Idea: Going backwards, to find the next warmer day after i, start at i + 1 and jump by its known answer instead of stepping one day at a time.
    static class Approach3 {
        public int[] dailyTemperatures(int[] temperatures) {
            int n = temperatures.length;
            int[] ans = new int[n];
            for (int i = n - 2; i >= 0; i--) {
                int j = i + 1;
                while (j < n && temperatures[j] <= temperatures[i]) {
                    if (ans[j] == 0) { j = n; break; }
                    j += ans[j];
                }
                if (j < n) ans[i] = j - i;
            }
            return ans;
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
        check("Approach 1", new Approach1().dailyTemperatures(new int[]{73,74,75,71,69,72,76,73}), "[1, 1, 4, 2, 1, 1, 0, 0]");
        check("Approach 1", new Approach1().dailyTemperatures(new int[]{30,40,50,60}), "[1, 1, 1, 0]");
        check("Approach 1", new Approach1().dailyTemperatures(new int[]{30,60,90}), "[1, 1, 0]");
        check("Approach 1", new Approach1().dailyTemperatures(new int[]{90,80,70}), "[0, 0, 0]");
        check("Approach 2", new Approach2().dailyTemperatures(new int[]{73,74,75,71,69,72,76,73}), "[1, 1, 4, 2, 1, 1, 0, 0]");
        check("Approach 2", new Approach2().dailyTemperatures(new int[]{30,40,50,60}), "[1, 1, 1, 0]");
        check("Approach 2", new Approach2().dailyTemperatures(new int[]{30,60,90}), "[1, 1, 0]");
        check("Approach 2", new Approach2().dailyTemperatures(new int[]{90,80,70}), "[0, 0, 0]");
        check("Approach 3", new Approach3().dailyTemperatures(new int[]{73,74,75,71,69,72,76,73}), "[1, 1, 4, 2, 1, 1, 0, 0]");
        check("Approach 3", new Approach3().dailyTemperatures(new int[]{30,40,50,60}), "[1, 1, 1, 0]");
        check("Approach 3", new Approach3().dailyTemperatures(new int[]{30,60,90}), "[1, 1, 0]");
        check("Approach 3", new Approach3().dailyTemperatures(new int[]{90,80,70}), "[0, 0, 0]");
        System.out.println("DailyTemperatures: all 3 approaches passed " + passed + " checks");
    }
}
