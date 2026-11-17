import java.util.*;
import java.util.stream.*;

/**
 * 3Sum Closest (Medium) - Day 2
 * https://leetcode.com/problems/3sum-closest/
 *
 * Approach 1: Brute force: every triplet  |  Time O(n^3)  |  Space O(1)
 * Approach 2: Sort + two pointers (optimal)  |  Time O(n^2)  |  Space O(log n) sort stack  <- best
 *
 * Run: javac Problem3sumClosest.java && java Problem3sumClosest
 */
public class Problem3sumClosest {

    // Approach 1: Brute force: every triplet
    // Time O(n^3), Space O(1)
    // Idea: Try all triplets and keep the sum closest to the target.
    static class Approach1 {
        public int threeSumClosest(int[] nums, int target) {
            int best = nums[0] + nums[1] + nums[2];
            for (int i = 0; i < nums.length; i++)
                for (int j = i + 1; j < nums.length; j++)
                    for (int k = j + 1; k < nums.length; k++) {
                        int s = nums[i] + nums[j] + nums[k];
                        if (Math.abs(s - target) < Math.abs(best - target)) best = s;
                    }
            return best;
        }
    }

    // Approach 2: Sort + two pointers (optimal)
    // Time O(n^2), Space O(log n) sort stack
    // Idea: Sort, fix i, move two pointers: sum too small -> l++, too big -> r--, equal -> return immediately. Track the closest sum.
    static class Approach2 {
        public int threeSumClosest(int[] nums, int target) {
            Arrays.sort(nums);
            int best = nums[0] + nums[1] + nums[2];
            for (int i = 0; i < nums.length - 2; i++) {
                int l = i + 1, r = nums.length - 1;
                while (l < r) {
                    int s = nums[i] + nums[l] + nums[r];
                    if (Math.abs(s - target) < Math.abs(best - target)) best = s;
                    if (s == target) return s;
                    if (s < target) l++;
                    else r--;
                }
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
        check("Approach 1", new Approach1().threeSumClosest(new int[]{-1,2,1,-4}, 1), "2");
        check("Approach 1", new Approach1().threeSumClosest(new int[]{0,0,0}, 1), "0");
        check("Approach 1", new Approach1().threeSumClosest(new int[]{4,0,5,-5,3,3,0,-4,-5}, -2), "-2");
        check("Approach 2", new Approach2().threeSumClosest(new int[]{-1,2,1,-4}, 1), "2");
        check("Approach 2", new Approach2().threeSumClosest(new int[]{0,0,0}, 1), "0");
        check("Approach 2", new Approach2().threeSumClosest(new int[]{4,0,5,-5,3,3,0,-4,-5}, -2), "-2");
        System.out.println("Problem3sumClosest: all 2 approaches passed " + passed + " checks");
    }
}
