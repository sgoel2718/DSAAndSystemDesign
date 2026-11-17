import java.util.*;
import java.util.stream.*;

/**
 * Circular Array Loop (Medium) - Day 6
 * https://leetcode.com/problems/circular-array-loop/
 *
 * Approach 1: Simulate from every start with a visited set  |  Time O(n^2)  |  Space O(n)
 * Approach 2: Fast & slow pointers + mark dead ends (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac CircularArrayLoop.java && java CircularArrayLoop
 */
public class CircularArrayLoop {

    // Approach 1: Simulate from every start with a visited set
    // Time O(n^2), Space O(n)
    // Idea: From each index, follow the jumps while the direction stays the same. If an index repeats, there is a loop; it counts only if it is longer than one element.
    static class Approach1 {
        public boolean circularArrayLoop(int[] nums) {
            int n = nums.length;
            for (int i = 0; i < n; i++) {
                Set<Integer> seen = new HashSet<>();
                boolean forward = nums[i] > 0;
                int j = i;
                while ((nums[j] > 0) == forward) {
                    if (!seen.add(j)) {
                        if (next(nums, j) != j) return true;
                        break;
                    }
                    j = next(nums, j);
                }
            }
            return false;
        }
        private int next(int[] a, int i) {
            int n = a.length;
            return ((i + a[i]) % n + n) % n;
        }
    }

    // Approach 2: Fast & slow pointers + mark dead ends (optimal)
    // Time O(n), Space O(1)
    // Idea: From each start run Floyd while every step keeps the same direction. A meeting means a loop unless it is a one-element self loop. Afterwards set every index on the failed path to 0 so it is never explored again.
    static class Approach2 {
        public boolean circularArrayLoop(int[] nums) {
            int n = nums.length;
            for (int i = 0; i < n; i++) {
                if (nums[i] == 0) continue;
                int slow = i, fast = next(nums, i);
                while (nums[fast] * nums[i] > 0 && nums[next(nums, fast)] * nums[i] > 0) {
                    if (slow == fast) {
                        if (slow == next(nums, slow)) break;      // one-element loop does not count
                        return true;
                    }
                    slow = next(nums, slow);
                    fast = next(nums, next(nums, fast));
                }
                int j = i, sign = nums[i];
                while (nums[j] != 0 && nums[j] * sign > 0) {       // mark this path as explored
                    int nx = next(nums, j);
                    nums[j] = 0;
                    j = nx;
                }
            }
            return false;
        }
        private int next(int[] a, int i) {
            int n = a.length;
            return ((i + a[i]) % n + n) % n;
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
        check("Approach 1", new Approach1().circularArrayLoop(new int[]{2,-1,1,2,2}), "true");
        check("Approach 1", new Approach1().circularArrayLoop(new int[]{-1,-2,-3,-4,-5,6}), "false");
        check("Approach 1", new Approach1().circularArrayLoop(new int[]{1,-1,5,1,4}), "true");
        check("Approach 1", new Approach1().circularArrayLoop(new int[]{-1,2}), "false");
        check("Approach 1", new Approach1().circularArrayLoop(new int[]{1,1}), "true");
        check("Approach 2", new Approach2().circularArrayLoop(new int[]{2,-1,1,2,2}), "true");
        check("Approach 2", new Approach2().circularArrayLoop(new int[]{-1,-2,-3,-4,-5,6}), "false");
        check("Approach 2", new Approach2().circularArrayLoop(new int[]{1,-1,5,1,4}), "true");
        check("Approach 2", new Approach2().circularArrayLoop(new int[]{-1,2}), "false");
        check("Approach 2", new Approach2().circularArrayLoop(new int[]{1,1}), "true");
        System.out.println("CircularArrayLoop: all 2 approaches passed " + passed + " checks");
    }
}
