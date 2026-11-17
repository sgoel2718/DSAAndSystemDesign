import java.util.*;
import java.util.stream.*;

/**
 * Max Consecutive Ones III (Medium) - Day 2
 * https://leetcode.com/problems/max-consecutive-ones-iii/
 *
 * Approach 1: Brute force: grow from every start  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sliding window counting zeros (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MaxConsecutiveOnesIii.java && java MaxConsecutiveOnesIii
 */
public class MaxConsecutiveOnesIii {

    // Approach 1: Brute force: grow from every start
    // Time O(n^2), Space O(1)
    // Idea: From each start, extend while the number of zeros is at most k.
    static class Approach1 {
        public int longestOnes(int[] nums, int k) {
            int best = 0;
            for (int i = 0; i < nums.length; i++) {
                int zeros = 0;
                for (int j = i; j < nums.length; j++) {
                    if (nums[j] == 0 && ++zeros > k) break;
                    best = Math.max(best, j - i + 1);
                }
            }
            return best;
        }
    }

    // Approach 2: Sliding window counting zeros (optimal)
    // Time O(n), Space O(1)
    // Idea: 'Longest subarray with at most k zeros'. Grow right; while there are more than k zeros, shrink left.
    static class Approach2 {
        public int longestOnes(int[] nums, int k) {
            int l = 0, zeros = 0, best = 0;
            for (int r = 0; r < nums.length; r++) {
                if (nums[r] == 0) zeros++;
                while (zeros > k) if (nums[l++] == 0) zeros--;
                best = Math.max(best, r - l + 1);
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
        check("Approach 1", new Approach1().longestOnes(new int[]{1,1,1,0,0,0,1,1,1,1,0}, 2), "6");
        check("Approach 1", new Approach1().longestOnes(new int[]{0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1}, 3), "10");
        check("Approach 1", new Approach1().longestOnes(new int[]{0,0,0}, 0), "0");
        check("Approach 2", new Approach2().longestOnes(new int[]{1,1,1,0,0,0,1,1,1,1,0}, 2), "6");
        check("Approach 2", new Approach2().longestOnes(new int[]{0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1}, 3), "10");
        check("Approach 2", new Approach2().longestOnes(new int[]{0,0,0}, 0), "0");
        System.out.println("MaxConsecutiveOnesIii: all 2 approaches passed " + passed + " checks");
    }
}
