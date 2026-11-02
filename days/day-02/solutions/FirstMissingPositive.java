import java.util.*;
import java.util.stream.*;

/**
 * First Missing Positive (Hard) - Day 2
 * https://leetcode.com/problems/first-missing-positive/
 *
 * Approach 1: Sort and scan  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 2: HashSet  |  Time O(n)  |  Space O(n)
 * Approach 3: Index marking with negation  |  Time O(n)  |  Space O(1)
 * Approach 4: Cyclic sort (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac FirstMissingPositive.java && java FirstMissingPositive
 */
public class FirstMissingPositive {

    // Approach 1: Sort and scan
    // Time O(n log n), Space O(log n) sort stack
    // Idea: Sort, then walk positives looking for the first gap starting at 1.
    static class Approach1 {
        public int firstMissingPositive(int[] nums) {
            Arrays.sort(nums);
            int expect = 1;
            for (int x : nums) {
                if (x == expect) expect++;
                else if (x > expect) break;
            }
            return expect;
        }
    }

    // Approach 2: HashSet
    // Time O(n), Space O(n)
    // Idea: The answer is in 1..n+1, so check those numbers against a set.
    static class Approach2 {
        public int firstMissingPositive(int[] nums) {
            Set<Integer> seen = new HashSet<>();
            for (int x : nums) seen.add(x);
            for (int k = 1; k <= nums.length + 1; k++) if (!seen.contains(k)) return k;
            return -1;
        }
    }

    // Approach 3: Index marking with negation
    // Time O(n), Space O(1)
    // Idea: Replace values outside 1..n with n+1, then mark value v by making index v-1 negative. The first non-negative index i gives i+1.
    static class Approach3 {
        public int firstMissingPositive(int[] nums) {
            int n = nums.length;
            for (int i = 0; i < n; i++) if (nums[i] <= 0 || nums[i] > n) nums[i] = n + 1;
            for (int i = 0; i < n; i++) {
                int v = Math.abs(nums[i]);
                if (v <= n && nums[v - 1] > 0) nums[v - 1] = -nums[v - 1];
            }
            for (int i = 0; i < n; i++) if (nums[i] > 0) return i + 1;
            return n + 1;
        }
    }

    // Approach 4: Cyclic sort (optimal)
    // Time O(n), Space O(1)
    // Idea: Put every value v in 1..n at index v-1 by swapping. The first index i that does not hold i+1 is the answer.
    static class Approach4 {
        public int firstMissingPositive(int[] nums) {
            int n = nums.length, i = 0;
            while (i < n) {
                int v = nums[i];
                if (v >= 1 && v <= n && nums[v - 1] != v) { nums[i] = nums[v - 1]; nums[v - 1] = v; }
                else i++;
            }
            for (i = 0; i < n; i++) if (nums[i] != i + 1) return i + 1;
            return n + 1;
        }
    }

    static String show(Object r) {
        if (r instanceof int[] a) return Arrays.toString(a);
        if (r instanceof int[][] a) return Arrays.deepToString(a);
        return String.valueOf(r);
    }
    static String norm(List<List<Integer>> x) {                 // order-independent view of a list of lists
        List<List<Integer>> c = new ArrayList<>();
        for (List<Integer> t : x) { List<Integer> s = new ArrayList<>(t); Collections.sort(s); c.add(s); }
        c.sort((p, q) -> { for (int i = 0; i < Math.min(p.size(), q.size()); i++) { int d = Integer.compare(p.get(i), q.get(i)); if (d != 0) return d; } return p.size() - q.size(); });
        return c.toString();
    }
    static String sorted(List<Integer> x) { List<Integer> c = new ArrayList<>(x); Collections.sort(c); return c.toString(); }
    static int passed = 0;
    static void check(String what, Object r, String want) {
        String got = show(r);
        if (!got.equals(want)) throw new AssertionError(what + ": got " + got + ", want " + want);
        passed++;
    }

    public static void main(String[] args) {
        check("Approach 1", new Approach1().firstMissingPositive(new int[]{1,2,0}), "3");
        check("Approach 1", new Approach1().firstMissingPositive(new int[]{3,4,-1,1}), "2");
        check("Approach 1", new Approach1().firstMissingPositive(new int[]{7,8,9,11,12}), "1");
        check("Approach 1", new Approach1().firstMissingPositive(new int[]{1,1}), "2");
        check("Approach 2", new Approach2().firstMissingPositive(new int[]{1,2,0}), "3");
        check("Approach 2", new Approach2().firstMissingPositive(new int[]{3,4,-1,1}), "2");
        check("Approach 2", new Approach2().firstMissingPositive(new int[]{7,8,9,11,12}), "1");
        check("Approach 2", new Approach2().firstMissingPositive(new int[]{1,1}), "2");
        check("Approach 3", new Approach3().firstMissingPositive(new int[]{1,2,0}), "3");
        check("Approach 3", new Approach3().firstMissingPositive(new int[]{3,4,-1,1}), "2");
        check("Approach 3", new Approach3().firstMissingPositive(new int[]{7,8,9,11,12}), "1");
        check("Approach 3", new Approach3().firstMissingPositive(new int[]{1,1}), "2");
        check("Approach 4", new Approach4().firstMissingPositive(new int[]{1,2,0}), "3");
        check("Approach 4", new Approach4().firstMissingPositive(new int[]{3,4,-1,1}), "2");
        check("Approach 4", new Approach4().firstMissingPositive(new int[]{7,8,9,11,12}), "1");
        check("Approach 4", new Approach4().firstMissingPositive(new int[]{1,1}), "2");
        System.out.println("FirstMissingPositive: all 4 approaches passed " + passed + " checks");
    }
}
