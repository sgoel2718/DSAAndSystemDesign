import java.util.*;
import java.util.stream.*;

/**
 * Squares of a Sorted Array (Easy) - Day 2
 * https://leetcode.com/problems/squares-of-a-sorted-array/
 *
 * Approach 1: Square everything, then sort  |  Time O(n log n)  |  Space O(n) output
 * Approach 2: Two pointers, fill from the back (optimal)  |  Time O(n)  |  Space O(n) output  <- best
 *
 * Run: javac SquaresOfASortedArray.java && java SquaresOfASortedArray
 */
public class SquaresOfASortedArray {

    // Approach 1: Square everything, then sort
    // Time O(n log n), Space O(n) output
    // Idea: Squares of negatives can be large, so the squared array is unsorted; sort it.
    static class Approach1 {
        public int[] sortedSquares(int[] nums) {
            int[] out = new int[nums.length];
            for (int i = 0; i < nums.length; i++) out[i] = nums[i] * nums[i];
            Arrays.sort(out);
            return out;
        }
    }

    // Approach 2: Two pointers, fill from the back (optimal)
    // Time O(n), Space O(n) output
    // Idea: The largest square is at one of the two ends. Compare the ends and place the larger square at the back of the output.
    static class Approach2 {
        public int[] sortedSquares(int[] nums) {
            int n = nums.length, l = 0, r = n - 1;
            int[] out = new int[n];
            for (int k = n - 1; k >= 0; k--) {
                if (Math.abs(nums[l]) > Math.abs(nums[r])) { out[k] = nums[l] * nums[l]; l++; }
                else { out[k] = nums[r] * nums[r]; r--; }
            }
            return out;
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
        check("Approach 1", new Approach1().sortedSquares(new int[]{-4,-1,0,3,10}), "[0, 1, 9, 16, 100]");
        check("Approach 1", new Approach1().sortedSquares(new int[]{-7,-3,2,3,11}), "[4, 9, 9, 49, 121]");
        check("Approach 2", new Approach2().sortedSquares(new int[]{-4,-1,0,3,10}), "[0, 1, 9, 16, 100]");
        check("Approach 2", new Approach2().sortedSquares(new int[]{-7,-3,2,3,11}), "[4, 9, 9, 49, 121]");
        System.out.println("SquaresOfASortedArray: all 2 approaches passed " + passed + " checks");
    }
}
