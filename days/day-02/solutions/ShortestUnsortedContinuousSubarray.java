import java.util.*;
import java.util.stream.*;

/**
 * Shortest Unsorted Continuous Subarray (Medium) - Day 2
 * https://leetcode.com/problems/shortest-unsorted-continuous-subarray/
 *
 * Approach 1: Sort a copy and compare  |  Time O(n log n)  |  Space O(n)
 * Approach 2: Monotonic stacks  |  Time O(n)  |  Space O(n)
 * Approach 3: Two scans with running max and min (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac ShortestUnsortedContinuousSubarray.java && java ShortestUnsortedContinuousSubarray
 */
public class ShortestUnsortedContinuousSubarray {

    // Approach 1: Sort a copy and compare
    // Time O(n log n), Space O(n)
    // Idea: The answer is the span between the first and last positions where the array differs from its sorted copy.
    static class Approach1 {
        public int findUnsortedSubarray(int[] nums) {
            int[] sorted = nums.clone();
            Arrays.sort(sorted);
            int l = 0, r = nums.length - 1;
            while (l <= r && nums[l] == sorted[l]) l++;
            while (r >= l && nums[r] == sorted[r]) r--;
            return r - l + 1;
        }
    }

    // Approach 2: Monotonic stacks
    // Time O(n), Space O(n)
    // Idea: Left boundary: smallest index popped by an increasing stack scanning left to right. Right boundary: largest index popped by a decreasing stack scanning right to left.
    static class Approach2 {
        public int findUnsortedSubarray(int[] nums) {
            int n = nums.length, l = n, r = 0;
            Deque<Integer> st = new ArrayDeque<>();
            for (int i = 0; i < n; i++) {
                while (!st.isEmpty() && nums[st.peek()] > nums[i]) l = Math.min(l, st.pop());
                st.push(i);
            }
            st.clear();
            for (int i = n - 1; i >= 0; i--) {
                while (!st.isEmpty() && nums[st.peek()] < nums[i]) r = Math.max(r, st.pop());
                st.push(i);
            }
            return r > l ? r - l + 1 : 0;
        }
    }

    // Approach 3: Two scans with running max and min (optimal)
    // Time O(n), Space O(1)
    // Idea: Scanning left to right, any element smaller than the running max is out of place: the last such index is the right end. Scanning right to left with a running min gives the left end.
    static class Approach3 {
        public int findUnsortedSubarray(int[] nums) {
            int n = nums.length, max = Integer.MIN_VALUE, min = Integer.MAX_VALUE, end = -1, start = 0;
            for (int i = 0; i < n; i++) {
                max = Math.max(max, nums[i]);
                if (nums[i] < max) end = i;
            }
            for (int i = n - 1; i >= 0; i--) {
                min = Math.min(min, nums[i]);
                if (nums[i] > min) start = i;
            }
            return end == -1 ? 0 : end - start + 1;
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
        check("Approach 1", new Approach1().findUnsortedSubarray(new int[]{2,6,4,8,10,9,15}), "5");
        check("Approach 1", new Approach1().findUnsortedSubarray(new int[]{1,2,3,4}), "0");
        check("Approach 1", new Approach1().findUnsortedSubarray(new int[]{1}), "0");
        check("Approach 1", new Approach1().findUnsortedSubarray(new int[]{1,3,2,2,2}), "4");
        check("Approach 2", new Approach2().findUnsortedSubarray(new int[]{2,6,4,8,10,9,15}), "5");
        check("Approach 2", new Approach2().findUnsortedSubarray(new int[]{1,2,3,4}), "0");
        check("Approach 2", new Approach2().findUnsortedSubarray(new int[]{1}), "0");
        check("Approach 2", new Approach2().findUnsortedSubarray(new int[]{1,3,2,2,2}), "4");
        check("Approach 3", new Approach3().findUnsortedSubarray(new int[]{2,6,4,8,10,9,15}), "5");
        check("Approach 3", new Approach3().findUnsortedSubarray(new int[]{1,2,3,4}), "0");
        check("Approach 3", new Approach3().findUnsortedSubarray(new int[]{1}), "0");
        check("Approach 3", new Approach3().findUnsortedSubarray(new int[]{1,3,2,2,2}), "4");
        System.out.println("ShortestUnsortedContinuousSubarray: all 3 approaches passed " + passed + " checks");
    }
}
