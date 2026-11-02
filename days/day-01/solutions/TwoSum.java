import java.util.*;
import java.util.stream.*;

/**
 * Two Sum (Easy) - Day 1
 * https://leetcode.com/problems/two-sum/
 *
 * Approach 1: Brute force: every pair  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sort + two pointers (keep original indices)  |  Time O(n log n)  |  Space O(n)
 * Approach 3: Sort + two pointers (return values only)  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 4: HashMap, two passes  |  Time O(n)  |  Space O(n)
 * Approach 5: HashMap, one pass (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac TwoSum.java && java TwoSum
 */
public class TwoSum {

    // Approach 1: Brute force: every pair
    // Time O(n^2), Space O(1)
    // Idea: Try every pair (i, j) with i < j and return when they add up to target.
    static class Approach1 {
        public int[] twoSum(int[] nums, int target) {
            for (int i = 0; i < nums.length; i++) {
                for (int j = i + 1; j < nums.length; j++) {
                    if (nums[i] + nums[j] == target) return new int[]{i, j};
                }
            }
            return new int[0];
        }
    }

    // Approach 2: Sort + two pointers (keep original indices)
    // Time O(n log n), Space O(n)
    // Idea: Sort an array of indices by value, then move two pointers inward. Sorting moves elements, so the index array is needed to report original positions.
    static class Approach2 {
        public int[] twoSum(int[] nums, int target) {
            Integer[] idx = new Integer[nums.length];
            for (int i = 0; i < nums.length; i++) idx[i] = i;
            Arrays.sort(idx, (a, b) -> Integer.compare(nums[a], nums[b]));
            int l = 0, r = nums.length - 1;
            while (l < r) {
                int sum = nums[idx[l]] + nums[idx[r]];
                if (sum == target) return new int[]{Math.min(idx[l], idx[r]), Math.max(idx[l], idx[r])};
                if (sum < target) l++;
                else r--;
            }
            return new int[0];
        }
    }

    // Approach 3: Sort + two pointers (return values only)
    // Time O(n log n), Space O(log n) sort stack
    // Idea: If only the two values (or true/false) are needed, sort in place and use two pointers. No extra array, but the input order is destroyed.
    static class Approach3 {
        public int[] twoSumValues(int[] nums, int target) {
            Arrays.sort(nums);
            int l = 0, r = nums.length - 1;
            while (l < r) {
                int sum = nums[l] + nums[r];
                if (sum == target) return new int[]{nums[l], nums[r]};
                if (sum < target) l++;
                else r--;
            }
            return new int[0];
        }
    }

    // Approach 4: HashMap, two passes
    // Time O(n), Space O(n)
    // Idea: First pass stores value -> index. Second pass looks up target - x, skipping the same index.
    static class Approach4 {
        public int[] twoSum(int[] nums, int target) {
            Map<Integer, Integer> indexOf = new HashMap<>();
            for (int i = 0; i < nums.length; i++) indexOf.put(nums[i], i);
            for (int i = 0; i < nums.length; i++) {
                Integer j = indexOf.get(target - nums[i]);
                if (j != null && j != i) return new int[]{i, j};
            }
            return new int[0];
        }
    }

    // Approach 5: HashMap, one pass (optimal)
    // Time O(n), Space O(n)
    // Idea: For each x, check whether target - x was seen earlier; only then store x. Checking before storing stops x pairing with itself.
    static class Approach5 {
        public int[] twoSum(int[] nums, int target) {
            Map<Integer, Integer> indexOf = new HashMap<>();
            for (int i = 0; i < nums.length; i++) {
                int need = target - nums[i];
                if (indexOf.containsKey(need)) return new int[]{indexOf.get(need), i};
                indexOf.put(nums[i], i);
            }
            return new int[0];
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
        check("Approach 1", new Approach1().twoSum(new int[]{2,7,11,15}, 9), "[0, 1]");
        check("Approach 1", new Approach1().twoSum(new int[]{3,2,4}, 6), "[1, 2]");
        check("Approach 1", new Approach1().twoSum(new int[]{3,3}, 6), "[0, 1]");
        check("Approach 2", new Approach2().twoSum(new int[]{2,7,11,15}, 9), "[0, 1]");
        check("Approach 2", new Approach2().twoSum(new int[]{3,2,4}, 6), "[1, 2]");
        check("Approach 2", new Approach2().twoSum(new int[]{3,3}, 6), "[0, 1]");
        check("Approach 3", new Approach3().twoSumValues(new int[]{2,7,11,15}, 9), "[2, 7]");
        check("Approach 3", new Approach3().twoSumValues(new int[]{3,2,4}, 6), "[2, 4]");
        check("Approach 4", new Approach4().twoSum(new int[]{2,7,11,15}, 9), "[0, 1]");
        check("Approach 4", new Approach4().twoSum(new int[]{3,2,4}, 6), "[1, 2]");
        check("Approach 4", new Approach4().twoSum(new int[]{3,3}, 6), "[0, 1]");
        check("Approach 5", new Approach5().twoSum(new int[]{2,7,11,15}, 9), "[0, 1]");
        check("Approach 5", new Approach5().twoSum(new int[]{3,2,4}, 6), "[1, 2]");
        check("Approach 5", new Approach5().twoSum(new int[]{3,3}, 6), "[0, 1]");
        System.out.println("TwoSum: all 5 approaches passed " + passed + " checks");
    }
}
