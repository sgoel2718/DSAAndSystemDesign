import java.util.*;
import java.util.stream.*;

/**
 * Contiguous Array (Medium) - Day 2
 * https://leetcode.com/problems/contiguous-array/
 *
 * Approach 1: Brute force: every subarray  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix balance + first-seen HashMap (optimal)  |  Time O(n)  |  Space O(n)  <- best
 * Approach 3: Prefix balance + array instead of a map  |  Time O(n)  |  Space O(n)
 *
 * Run: javac ContiguousArray.java && java ContiguousArray
 */
public class ContiguousArray {

    // Approach 1: Brute force: every subarray
    // Time O(n^2), Space O(1)
    // Idea: Count zeros and ones from each start; record lengths where they are equal.
    static class Approach1 {
        public int findMaxLength(int[] nums) {
            int best = 0;
            for (int i = 0; i < nums.length; i++) {
                int bal = 0;
                for (int j = i; j < nums.length; j++) {
                    bal += nums[j] == 1 ? 1 : -1;
                    if (bal == 0) best = Math.max(best, j - i + 1);
                }
            }
            return best;
        }
    }

    // Approach 2: Prefix balance + first-seen HashMap (optimal)
    // Time O(n), Space O(n)
    // Idea: Treat 0 as -1. Equal zeros and ones means the balance returns to an earlier value; the longest such subarray uses the first index where that balance appeared.
    static class Approach2 {
        public int findMaxLength(int[] nums) {
            Map<Integer, Integer> first = new HashMap<>();
            first.put(0, -1);
            int bal = 0, best = 0;
            for (int i = 0; i < nums.length; i++) {
                bal += nums[i] == 1 ? 1 : -1;
                Integer j = first.putIfAbsent(bal, i);
                if (j != null) best = Math.max(best, i - j);
            }
            return best;
        }
    }

    // Approach 3: Prefix balance + array instead of a map
    // Time O(n), Space O(n)
    // Idea: The balance is always in [-n, n], so an array of size 2n + 1 replaces the HashMap (faster in practice).
    static class Approach3 {
        public int findMaxLength(int[] nums) {
            int n = nums.length, bal = 0, best = 0;
            int[] first = new int[2 * n + 1];
            Arrays.fill(first, -2);
            first[n] = -1;
            for (int i = 0; i < n; i++) {
                bal += nums[i] == 1 ? 1 : -1;
                if (first[bal + n] == -2) first[bal + n] = i;
                else best = Math.max(best, i - first[bal + n]);
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
        check("Approach 1", new Approach1().findMaxLength(new int[]{0,1}), "2");
        check("Approach 1", new Approach1().findMaxLength(new int[]{0,1,0}), "2");
        check("Approach 1", new Approach1().findMaxLength(new int[]{0,1,1,1,1,1,0,0,0}), "6");
        check("Approach 2", new Approach2().findMaxLength(new int[]{0,1}), "2");
        check("Approach 2", new Approach2().findMaxLength(new int[]{0,1,0}), "2");
        check("Approach 2", new Approach2().findMaxLength(new int[]{0,1,1,1,1,1,0,0,0}), "6");
        check("Approach 3", new Approach3().findMaxLength(new int[]{0,1}), "2");
        check("Approach 3", new Approach3().findMaxLength(new int[]{0,1,0}), "2");
        check("Approach 3", new Approach3().findMaxLength(new int[]{0,1,1,1,1,1,0,0,0}), "6");
        System.out.println("ContiguousArray: all 3 approaches passed " + passed + " checks");
    }
}
