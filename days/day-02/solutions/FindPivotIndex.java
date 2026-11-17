import java.util.*;
import java.util.stream.*;

/**
 * Find Pivot Index (Easy) - Day 2
 * https://leetcode.com/problems/find-pivot-index/
 *
 * Approach 1: Brute force: sum both sides for each index  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix sum array  |  Time O(n)  |  Space O(n)
 * Approach 3: Total sum + running left sum (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac FindPivotIndex.java && java FindPivotIndex
 */
public class FindPivotIndex {

    // Approach 1: Brute force: sum both sides for each index
    // Time O(n^2), Space O(1)
    // Idea: For every index, add up the left side and the right side.
    static class Approach1 {
        public int pivotIndex(int[] nums) {
            for (int i = 0; i < nums.length; i++) {
                int left = 0, right = 0;
                for (int j = 0; j < i; j++) left += nums[j];
                for (int j = i + 1; j < nums.length; j++) right += nums[j];
                if (left == right) return i;
            }
            return -1;
        }
    }

    // Approach 2: Prefix sum array
    // Time O(n), Space O(n)
    // Idea: left = pre[i], right = total - pre[i + 1].
    static class Approach2 {
        public int pivotIndex(int[] nums) {
            int n = nums.length;
            int[] pre = new int[n + 1];
            for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
            for (int i = 0; i < n; i++) if (pre[i] == pre[n] - pre[i + 1]) return i;
            return -1;
        }
    }

    // Approach 3: Total sum + running left sum (optimal)
    // Time O(n), Space O(1)
    // Idea: right = total - left - nums[i], so one running variable is enough.
    static class Approach3 {
        public int pivotIndex(int[] nums) {
            int total = 0, left = 0;
            for (int x : nums) total += x;
            for (int i = 0; i < nums.length; i++) {
                if (left == total - left - nums[i]) return i;
                left += nums[i];
            }
            return -1;
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
        check("Approach 1", new Approach1().pivotIndex(new int[]{1,7,3,6,5,6}), "3");
        check("Approach 1", new Approach1().pivotIndex(new int[]{1,2,3}), "-1");
        check("Approach 1", new Approach1().pivotIndex(new int[]{2,1,-1}), "0");
        check("Approach 2", new Approach2().pivotIndex(new int[]{1,7,3,6,5,6}), "3");
        check("Approach 2", new Approach2().pivotIndex(new int[]{1,2,3}), "-1");
        check("Approach 2", new Approach2().pivotIndex(new int[]{2,1,-1}), "0");
        check("Approach 3", new Approach3().pivotIndex(new int[]{1,7,3,6,5,6}), "3");
        check("Approach 3", new Approach3().pivotIndex(new int[]{1,2,3}), "-1");
        check("Approach 3", new Approach3().pivotIndex(new int[]{2,1,-1}), "0");
        System.out.println("FindPivotIndex: all 3 approaches passed " + passed + " checks");
    }
}
