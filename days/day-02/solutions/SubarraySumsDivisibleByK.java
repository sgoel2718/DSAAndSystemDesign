import java.util.*;
import java.util.stream.*;

/**
 * Subarray Sums Divisible by K (Medium) - Day 2
 * https://leetcode.com/problems/subarray-sums-divisible-by-k/
 *
 * Approach 1: Brute force: every subarray  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix remainders + counts (optimal)  |  Time O(n)  |  Space O(k)  <- best
 *
 * Run: javac SubarraySumsDivisibleByK.java && java SubarraySumsDivisibleByK
 */
public class SubarraySumsDivisibleByK {

    // Approach 1: Brute force: every subarray
    // Time O(n^2), Space O(1)
    // Idea: Running sum from each start; count sums divisible by k.
    static class Approach1 {
        public int subarraysDivByK(int[] nums, int k) {
            int count = 0;
            for (int i = 0; i < nums.length; i++) {
                int s = 0;
                for (int j = i; j < nums.length; j++) { s += nums[j]; if (s % k == 0) count++; }
            }
            return count;
        }
    }

    // Approach 2: Prefix remainders + counts (optimal)
    // Time O(n), Space O(k)
    // Idea: sum(i+1..j) is divisible by k exactly when pre[i] and pre[j] have the same remainder. Count remainders; fix negatives with ((x % k) + k) % k.
    static class Approach2 {
        public int subarraysDivByK(int[] nums, int k) {
            int[] count = new int[k];
            count[0] = 1;
            int pre = 0, res = 0;
            for (int x : nums) {
                pre = ((pre + x) % k + k) % k;
                res += count[pre]++;
            }
            return res;
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
        check("Approach 1", new Approach1().subarraysDivByK(new int[]{4,5,0,-2,-3,1}, 5), "7");
        check("Approach 1", new Approach1().subarraysDivByK(new int[]{5}, 9), "0");
        check("Approach 1", new Approach1().subarraysDivByK(new int[]{-1,2,9}, 2), "2");
        check("Approach 2", new Approach2().subarraysDivByK(new int[]{4,5,0,-2,-3,1}, 5), "7");
        check("Approach 2", new Approach2().subarraysDivByK(new int[]{5}, 9), "0");
        check("Approach 2", new Approach2().subarraysDivByK(new int[]{-1,2,9}, 2), "2");
        System.out.println("SubarraySumsDivisibleByK: all 2 approaches passed " + passed + " checks");
    }
}
