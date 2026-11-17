import java.util.*;
import java.util.stream.*;

/**
 * 4Sum (Medium) - Day 2
 * https://leetcode.com/problems/4sum/
 *
 * Approach 1: Brute force: every quadruplet + set  |  Time O(n^4)  |  Space O(k) for k answers
 * Approach 2: Fix two numbers + HashSet for the third and fourth  |  Time O(n^3)  |  Space O(n)
 * Approach 3: Sort + fix two + two pointers (optimal)  |  Time O(n^3)  |  Space O(log n) sort stack  <- best
 *
 * Run: javac FourSum.java && java FourSum
 */
public class FourSum {

    // Approach 1: Brute force: every quadruplet + set
    // Time O(n^4), Space O(k) for k answers
    // Idea: Try all quadruplets; store each sorted quadruplet in a Set to drop duplicates. Use long for the sum.
    static class Approach1 {
        public List<List<Integer>> fourSum(int[] nums, int target) {
            Set<List<Integer>> found = new HashSet<>();
            int n = nums.length;
            for (int a = 0; a < n; a++)
                for (int b = a + 1; b < n; b++)
                    for (int c = b + 1; c < n; c++)
                        for (int d = c + 1; d < n; d++)
                            if ((long) nums[a] + nums[b] + nums[c] + nums[d] == target) {
                                List<Integer> q = Arrays.asList(nums[a], nums[b], nums[c], nums[d]);
                                Collections.sort(q);
                                found.add(q);
                            }
            return new ArrayList<>(found);
        }
    }

    // Approach 2: Fix two numbers + HashSet for the third and fourth
    // Time O(n^3), Space O(n)
    // Idea: Sort, fix i and j, then do Two Sum with a HashSet on the rest. A Set of results removes duplicates.
    static class Approach2 {
        public List<List<Integer>> fourSum(int[] nums, int target) {
            Arrays.sort(nums);
            Set<List<Integer>> found = new HashSet<>();
            int n = nums.length;
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++) {
                    Set<Long> seen = new HashSet<>();
                    for (int k = j + 1; k < n; k++) {
                        long need = (long) target - nums[i] - nums[j] - nums[k];
                        if (seen.contains(need)) found.add(Arrays.asList(nums[i], nums[j], (int) need, nums[k]));
                        seen.add((long) nums[k]);
                    }
                }
            return new ArrayList<>(found);
        }
    }

    // Approach 3: Sort + fix two + two pointers (optimal)
    // Time O(n^3), Space O(log n) sort stack
    // Idea: Same as 3Sum with one more loop: fix i and j, two pointers on the rest, skip equal values at every level. Use long to avoid overflow.
    static class Approach3 {
        public List<List<Integer>> fourSum(int[] nums, int target) {
            Arrays.sort(nums);
            List<List<Integer>> res = new ArrayList<>();
            int n = nums.length;
            for (int i = 0; i < n - 3; i++) {
                if (i > 0 && nums[i] == nums[i - 1]) continue;
                for (int j = i + 1; j < n - 2; j++) {
                    if (j > i + 1 && nums[j] == nums[j - 1]) continue;
                    int l = j + 1, r = n - 1;
                    while (l < r) {
                        long sum = (long) nums[i] + nums[j] + nums[l] + nums[r];
                        if (sum == target) {
                            res.add(Arrays.asList(nums[i], nums[j], nums[l], nums[r]));
                            while (l < r && nums[l] == nums[l + 1]) l++;
                            while (l < r && nums[r] == nums[r - 1]) r--;
                            l++;
                            r--;
                        } else if (sum < target) l++;
                        else r--;
                    }
                }
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
        { Approach1 o = new Approach1(); Object r; r = norm(o.fourSum(new int[]{1,0,-1,0,-2,2}, 0)); check("Approach 1", r, "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"); }
        { Approach1 o = new Approach1(); Object r; r = norm(o.fourSum(new int[]{2,2,2,2,2}, 8)); check("Approach 1", r, "[[2, 2, 2, 2]]"); }
        { Approach1 o = new Approach1(); Object r; r = norm(o.fourSum(new int[]{1000000000,1000000000,1000000000,1000000000}, -294967296)); check("Approach 1", r, "[]"); }
        { Approach2 o = new Approach2(); Object r; r = norm(o.fourSum(new int[]{1,0,-1,0,-2,2}, 0)); check("Approach 2", r, "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"); }
        { Approach2 o = new Approach2(); Object r; r = norm(o.fourSum(new int[]{2,2,2,2,2}, 8)); check("Approach 2", r, "[[2, 2, 2, 2]]"); }
        { Approach2 o = new Approach2(); Object r; r = norm(o.fourSum(new int[]{1000000000,1000000000,1000000000,1000000000}, -294967296)); check("Approach 2", r, "[]"); }
        { Approach3 o = new Approach3(); Object r; r = norm(o.fourSum(new int[]{1,0,-1,0,-2,2}, 0)); check("Approach 3", r, "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"); }
        { Approach3 o = new Approach3(); Object r; r = norm(o.fourSum(new int[]{2,2,2,2,2}, 8)); check("Approach 3", r, "[[2, 2, 2, 2]]"); }
        { Approach3 o = new Approach3(); Object r; r = norm(o.fourSum(new int[]{1000000000,1000000000,1000000000,1000000000}, -294967296)); check("Approach 3", r, "[]"); }
        System.out.println("FourSum: all 3 approaches passed " + passed + " checks");
    }
}
