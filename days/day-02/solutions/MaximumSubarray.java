import java.util.*;
import java.util.stream.*;

/**
 * Maximum Subarray (Medium) - Day 2
 * https://leetcode.com/problems/maximum-subarray/
 *
 * Approach 1: Brute force: every subarray with running sum  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Divide and conquer  |  Time O(n log n)  |  Space O(log n) recursion
 * Approach 3: Prefix sums: subtract the smallest earlier prefix  |  Time O(n)  |  Space O(1)
 * Approach 4: Kadane's algorithm (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MaximumSubarray.java && java MaximumSubarray
 */
public class MaximumSubarray {

    // Approach 1: Brute force: every subarray with running sum
    // Time O(n^2), Space O(1)
    // Idea: For each start, extend the end and keep a running sum.
    static class Approach1 {
        public int maxSubArray(int[] nums) {
            int best = Integer.MIN_VALUE;
            for (int i = 0; i < nums.length; i++) {
                int sum = 0;
                for (int j = i; j < nums.length; j++) {
                    sum += nums[j];
                    best = Math.max(best, sum);
                }
            }
            return best;
        }
    }

    // Approach 2: Divide and conquer
    // Time O(n log n), Space O(log n) recursion
    // Idea: Best subarray is entirely in the left half, entirely in the right half, or crosses the middle (best suffix of left + best prefix of right).
    static class Approach2 {
        public int maxSubArray(int[] nums) {
            return solve(nums, 0, nums.length - 1);
        }
        private int solve(int[] a, int lo, int hi) {
            if (lo == hi) return a[lo];
            int mid = lo + (hi - lo) / 2;
            int leftBest = Integer.MIN_VALUE, sum = 0;
            for (int i = mid; i >= lo; i--) { sum += a[i]; leftBest = Math.max(leftBest, sum); }
            int rightBest = Integer.MIN_VALUE; sum = 0;
            for (int i = mid + 1; i <= hi; i++) { sum += a[i]; rightBest = Math.max(rightBest, sum); }
            int cross = leftBest + rightBest;
            return Math.max(cross, Math.max(solve(a, lo, mid), solve(a, mid + 1, hi)));
        }
    }

    // Approach 3: Prefix sums: subtract the smallest earlier prefix
    // Time O(n), Space O(1)
    // Idea: Sum(i..j) = prefix[j+1] - prefix[i]. For each end, subtract the minimum prefix seen so far.
    static class Approach3 {
        public int maxSubArray(int[] nums) {
            int prefix = 0, minPrefix = 0, best = Integer.MIN_VALUE;
            for (int x : nums) {
                prefix += x;
                best = Math.max(best, prefix - minPrefix);
                minPrefix = Math.min(minPrefix, prefix);
            }
            return best;
        }
    }

    // Approach 4: Kadane's algorithm (optimal)
    // Time O(n), Space O(1)
    // Idea: At each element either extend the previous subarray or start fresh here: cur = max(x, cur + x).
    static class Approach4 {
        public int maxSubArray(int[] nums) {
            int cur = nums[0], best = nums[0];
            for (int i = 1; i < nums.length; i++) {
                cur = Math.max(nums[i], cur + nums[i]);
                best = Math.max(best, cur);
            }
            return best;
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
        check("Approach 1", new Approach1().maxSubArray(new int[]{-2,1,-3,4,-1,2,1,-5,4}), "6");
        check("Approach 1", new Approach1().maxSubArray(new int[]{5,4,-1,7,8}), "23");
        check("Approach 1", new Approach1().maxSubArray(new int[]{-3,-1,-2}), "-1");
        check("Approach 2", new Approach2().maxSubArray(new int[]{-2,1,-3,4,-1,2,1,-5,4}), "6");
        check("Approach 2", new Approach2().maxSubArray(new int[]{5,4,-1,7,8}), "23");
        check("Approach 2", new Approach2().maxSubArray(new int[]{-3,-1,-2}), "-1");
        check("Approach 3", new Approach3().maxSubArray(new int[]{-2,1,-3,4,-1,2,1,-5,4}), "6");
        check("Approach 3", new Approach3().maxSubArray(new int[]{5,4,-1,7,8}), "23");
        check("Approach 3", new Approach3().maxSubArray(new int[]{-3,-1,-2}), "-1");
        check("Approach 4", new Approach4().maxSubArray(new int[]{-2,1,-3,4,-1,2,1,-5,4}), "6");
        check("Approach 4", new Approach4().maxSubArray(new int[]{5,4,-1,7,8}), "23");
        check("Approach 4", new Approach4().maxSubArray(new int[]{-3,-1,-2}), "-1");
        System.out.println("MaximumSubarray: all 4 approaches passed " + passed + " checks");
    }
}
