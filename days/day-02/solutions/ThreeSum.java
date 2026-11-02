import java.util.*;
import java.util.stream.*;

/**
 * 3Sum (Medium) - Day 2
 * https://leetcode.com/problems/3sum/
 *
 * Approach 1: Brute force: every triplet + set to remove duplicates  |  Time O(n^3)  |  Space O(k) for k answers
 * Approach 2: Fix one number + HashSet Two Sum  |  Time O(n^2)  |  Space O(n)
 * Approach 3: Sort + two pointers (optimal)  |  Time O(n^2)  |  Space O(log n) sort stack  <- best
 *
 * Run: javac ThreeSum.java && java ThreeSum
 */
public class ThreeSum {

    // Approach 1: Brute force: every triplet + set to remove duplicates
    // Time O(n^3), Space O(k) for k answers
    // Idea: Check all triplets; sort each found triplet and store it in a Set so duplicates collapse.
    static class Approach1 {
        public List<List<Integer>> threeSum(int[] nums) {
            Set<List<Integer>> found = new HashSet<>();
            int n = nums.length;
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++)
                    for (int k = j + 1; k < n; k++)
                        if (nums[i] + nums[j] + nums[k] == 0) {
                            List<Integer> t = Arrays.asList(nums[i], nums[j], nums[k]);
                            Collections.sort(t);
                            found.add(t);
                        }
            return new ArrayList<>(found);
        }
    }

    // Approach 2: Fix one number + HashSet Two Sum
    // Time O(n^2), Space O(n)
    // Idea: For each i, run Two Sum (target -nums[i]) on the rest with a HashSet. Sorting first lets us skip duplicate values of i.
    static class Approach2 {
        public List<List<Integer>> threeSum(int[] nums) {
            Arrays.sort(nums);
            Set<List<Integer>> found = new HashSet<>();
            for (int i = 0; i < nums.length - 2; i++) {
                if (i > 0 && nums[i] == nums[i - 1]) continue;
                Set<Integer> seen = new HashSet<>();
                for (int j = i + 1; j < nums.length; j++) {
                    int need = -nums[i] - nums[j];
                    if (seen.contains(need)) found.add(Arrays.asList(nums[i], need, nums[j]));
                    seen.add(nums[j]);
                }
            }
            return new ArrayList<>(found);
        }
    }

    // Approach 3: Sort + two pointers (optimal)
    // Time O(n^2), Space O(log n) sort stack
    // Idea: Sort. Fix nums[i], then two pointers on the right part look for a pair summing to -nums[i]. Skip equal values to avoid duplicate triplets without any Set.
    static class Approach3 {
        public List<List<Integer>> threeSum(int[] nums) {
            Arrays.sort(nums);
            List<List<Integer>> res = new ArrayList<>();
            for (int i = 0; i < nums.length - 2; i++) {
                if (nums[i] > 0) break;                          // smallest is positive: no more answers
                if (i > 0 && nums[i] == nums[i - 1]) continue;   // skip duplicate first numbers
                int l = i + 1, r = nums.length - 1;
                while (l < r) {
                    int sum = nums[i] + nums[l] + nums[r];
                    if (sum == 0) {
                        res.add(Arrays.asList(nums[i], nums[l], nums[r]));
                        while (l < r && nums[l] == nums[l + 1]) l++;
                        while (l < r && nums[r] == nums[r - 1]) r--;
                        l++;
                        r--;
                    } else if (sum < 0) l++;
                    else r--;
                }
            }
            return res;
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
        { Approach1 o = new Approach1(); Object r; r = norm(o.threeSum(new int[]{-1,0,1,2,-1,-4})); check("Approach 1", r, "[[-1, -1, 2], [-1, 0, 1]]"); }
        { Approach1 o = new Approach1(); Object r; r = norm(o.threeSum(new int[]{0,0,0,0})); check("Approach 1", r, "[[0, 0, 0]]"); }
        { Approach1 o = new Approach1(); Object r; r = norm(o.threeSum(new int[]{0,1,1})); check("Approach 1", r, "[]"); }
        { Approach2 o = new Approach2(); Object r; r = norm(o.threeSum(new int[]{-1,0,1,2,-1,-4})); check("Approach 2", r, "[[-1, -1, 2], [-1, 0, 1]]"); }
        { Approach2 o = new Approach2(); Object r; r = norm(o.threeSum(new int[]{0,0,0,0})); check("Approach 2", r, "[[0, 0, 0]]"); }
        { Approach2 o = new Approach2(); Object r; r = norm(o.threeSum(new int[]{0,1,1})); check("Approach 2", r, "[]"); }
        { Approach3 o = new Approach3(); Object r; r = norm(o.threeSum(new int[]{-1,0,1,2,-1,-4})); check("Approach 3", r, "[[-1, -1, 2], [-1, 0, 1]]"); }
        { Approach3 o = new Approach3(); Object r; r = norm(o.threeSum(new int[]{0,0,0,0})); check("Approach 3", r, "[[0, 0, 0]]"); }
        { Approach3 o = new Approach3(); Object r; r = norm(o.threeSum(new int[]{0,1,1})); check("Approach 3", r, "[]"); }
        System.out.println("ThreeSum: all 3 approaches passed " + passed + " checks");
    }
}
