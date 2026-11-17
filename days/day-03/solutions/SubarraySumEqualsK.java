import java.util.*;
import java.util.stream.*;

/**
 * Subarray Sum Equals K (Medium) - Day 3
 * https://leetcode.com/problems/subarray-sum-equals-k/
 *
 * Approach 1: Brute force: every subarray with a running sum  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix sum + HashMap of counts (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac SubarraySumEqualsK.java && java SubarraySumEqualsK
 */
public class SubarraySumEqualsK {

    // Approach 1: Brute force: every subarray with a running sum
    // Time O(n^2), Space O(1)
    // Idea: From each start keep a running sum; count every time it equals k.
    static class Approach1 {
        public int subarraySum(int[] nums, int k) {
            int count = 0;
            for (int i = 0; i < nums.length; i++) {
                int s = 0;
                for (int j = i; j < nums.length; j++) { s += nums[j]; if (s == k) count++; }
            }
            return count;
        }
    }

    // Approach 2: Prefix sum + HashMap of counts (optimal)
    // Time O(n), Space O(n)
    // Idea: sum(i+1..j) = pre[j] - pre[i] = k, so at each j add how many earlier prefixes equal pre[j] - k. Seed the map with {0: 1}. Works with negative numbers, unlike a sliding window.
    static class Approach2 {
        public int subarraySum(int[] nums, int k) {
            Map<Integer, Integer> seen = new HashMap<>();
            seen.put(0, 1);
            int pre = 0, count = 0;
            for (int x : nums) {
                pre += x;
                count += seen.getOrDefault(pre - k, 0);
                seen.merge(pre, 1, Integer::sum);
            }
            return count;
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
        check("Approach 1", new Approach1().subarraySum(new int[]{1,1,1}, 2), "2");
        check("Approach 1", new Approach1().subarraySum(new int[]{1,2,3}, 3), "2");
        check("Approach 1", new Approach1().subarraySum(new int[]{1,-1,0}, 0), "3");
        check("Approach 2", new Approach2().subarraySum(new int[]{1,1,1}, 2), "2");
        check("Approach 2", new Approach2().subarraySum(new int[]{1,2,3}, 3), "2");
        check("Approach 2", new Approach2().subarraySum(new int[]{1,-1,0}, 0), "3");
        System.out.println("SubarraySumEqualsK: all 2 approaches passed " + passed + " checks");
    }
}
