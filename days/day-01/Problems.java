import java.util.*;

/**
 * Day 1 problems, each with the brute force first and then the optimal version,
 * exactly the order you should present them in an interview.
 *
 * Run:  javac Problems.java && java Problems
 */
public class Problems {

    // ------------------------------------------------------------------
    // 1. Two Sum (LeetCode 1) - return indices of two numbers adding to target
    // ------------------------------------------------------------------
    // Brute force: try every pair.            Time O(n^2), Space O(1)
    static int[] twoSumBrute(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++)
            for (int j = i + 1; j < nums.length; j++)
                if (nums[i] + nums[j] == target) return new int[]{i, j};
        return new int[0];
    }

    // Optimal: for each x, ask "have I already seen target - x?"  Time O(n), Space O(n)
    static int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> indexOf = new HashMap<>();      // value -> index
        for (int i = 0; i < nums.length; i++) {
            int need = target - nums[i];
            if (indexOf.containsKey(need)) return new int[]{indexOf.get(need), i};
            indexOf.put(nums[i], i);                           // store AFTER checking, so we never pair x with itself
        }
        return new int[0];
    }

    // Sort + two pointers, VALUES version (or "does a pair exist?").
    // Time O(n log n), extra space O(log n) for the sort's recursion stack (no extra arrays).
    // Trade-off: it sorts the caller's array in place, so the original order is lost.
    static int[] twoSumValuesSorted(int[] nums, int target) {
        Arrays.sort(nums);                                    // dual-pivot quicksort for int[]
        int l = 0, r = nums.length - 1;
        while (l < r) {
            int sum = nums[l] + nums[r];
            if (sum == target) return new int[]{nums[l], nums[r]};
            if (sum < target) l++;                            // need a bigger sum
            else r--;                                         // need a smaller sum
        }
        return new int[0];
    }

    // Sort + two pointers, INDICES version (what LeetCode 1 actually asks).
    // Sorting moves elements, so we must remember where each came from: an index array.
    // Time O(n log n), Space O(n) -> no better than the HashMap, and slower.
    static int[] twoSumIndicesSorted(int[] nums, int target) {
        Integer[] idx = new Integer[nums.length];             // O(n) extra space
        for (int i = 0; i < nums.length; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> Integer.compare(nums[a], nums[b]));
        int l = 0, r = nums.length - 1;
        while (l < r) {
            int sum = nums[idx[l]] + nums[idx[r]];
            if (sum == target) return new int[]{Math.min(idx[l], idx[r]), Math.max(idx[l], idx[r])};
            if (sum < target) l++; else r--;
        }
        return new int[0];
    }

    // Two Sum II (LeetCode 167): input is ALREADY sorted, answer is 1-based indices.
    // Time O(n), Space O(1) -> the best of both worlds, because no sort is needed.
    static int[] twoSumII(int[] numbers, int target) {
        int l = 0, r = numbers.length - 1;
        while (l < r) {
            int sum = numbers[l] + numbers[r];
            if (sum == target) return new int[]{l + 1, r + 1};
            if (sum < target) l++; else r--;
        }
        return new int[0];
    }

    // ------------------------------------------------------------------
    // 2. Contains Duplicate (LeetCode 217)
    // ------------------------------------------------------------------
    // Option A: sort, then compare neighbours.  Time O(n log n), Space O(1) extra (but mutates input)
    static boolean containsDuplicateSort(int[] nums) {
        int[] a = nums.clone();
        Arrays.sort(a);
        for (int i = 1; i < a.length; i++) if (a[i] == a[i - 1]) return true;
        return false;
    }

    // Option B: HashSet.  Time O(n), Space O(n)
    static boolean containsDuplicate(int[] nums) {
        Set<Integer> seen = new HashSet<>();
        for (int x : nums) if (!seen.add(x)) return true;
        return false;
    }

    // ------------------------------------------------------------------
    // 3. Fizz Buzz (LeetCode 412) - tests clean code, not algorithms
    // ------------------------------------------------------------------
    // Time O(n), Space O(1) besides the output
    static List<String> fizzBuzz(int n) {
        List<String> out = new ArrayList<>(n);
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) out.add("FizzBuzz");             // check 15 first
            else if (i % 3 == 0) out.add("Fizz");
            else if (i % 5 == 0) out.add("Buzz");
            else out.add(String.valueOf(i));
        }
        return out;
    }

    // ------------------------------------------------------------------
    // 4. Richest Customer Wealth (LeetCode 1672) - 2D array traversal
    // ------------------------------------------------------------------
    // Time O(m * n), Space O(1)
    static int maximumWealth(int[][] accounts) {
        int best = 0;
        for (int[] customer : accounts) {
            int sum = 0;
            for (int money : customer) sum += money;
            best = Math.max(best, sum);
        }
        return best;
    }

    // ------------------------------------------------------------------
    // Tests: run them like an interviewer would - normal case, edge cases
    // ------------------------------------------------------------------
    public static void main(String[] args) {
        check("twoSum basic", Arrays.toString(twoSum(new int[]{2, 7, 11, 15}, 9)), "[0, 1]");
        check("twoSum same value twice", Arrays.toString(twoSum(new int[]{3, 3}, 6)), "[0, 1]");
        check("twoSum negatives", Arrays.toString(twoSum(new int[]{-3, 4, 3, 90}, 0)), "[0, 2]");
        check("twoSum brute == optimal", Arrays.toString(twoSumBrute(new int[]{3, 2, 4}, 6)), Arrays.toString(twoSum(new int[]{3, 2, 4}, 6)));

        check("twoSum values (sorted)", Arrays.toString(twoSumValuesSorted(new int[]{11, 7, 2, 15}, 9)), "[2, 7]");
        check("twoSum indices (sorted)", Arrays.toString(twoSumIndicesSorted(new int[]{11, 7, 2, 15}, 9)), "[1, 2]");
        check("twoSum indices (sorted) dupes", Arrays.toString(twoSumIndicesSorted(new int[]{3, 3}, 6)), "[0, 1]");
        check("twoSum indices sorted == hashmap", Arrays.toString(twoSumIndicesSorted(new int[]{3, 2, 4}, 6)), Arrays.toString(twoSum(new int[]{3, 2, 4}, 6)));
        int[] original = {11, 7, 2, 15};
        twoSumValuesSorted(original, 9);
        check("values version mutates input", Arrays.toString(original), "[2, 7, 11, 15]");
        check("twoSum II (already sorted)", Arrays.toString(twoSumII(new int[]{2, 7, 11, 15}, 9)), "[1, 2]");
        check("twoSum II negatives", Arrays.toString(twoSumII(new int[]{-1, 0}, -1)), "[1, 2]");

        check("dup yes", containsDuplicate(new int[]{1, 2, 3, 1}), true);
        check("dup no", containsDuplicate(new int[]{1, 2, 3, 4}), false);
        check("dup empty", containsDuplicate(new int[]{}), false);
        check("dup sort version", containsDuplicateSort(new int[]{1, 1, 1, 3, 3, 4, 3, 2, 4, 2}), true);

        check("fizzBuzz 15", fizzBuzz(15).get(14), "FizzBuzz");
        check("fizzBuzz 1..5", fizzBuzz(5).toString(), "[1, 2, Fizz, 4, Buzz]");

        check("wealth", maximumWealth(new int[][]{{1, 5}, {7, 3}, {3, 5}}), 10);
        check("wealth single", maximumWealth(new int[][]{{2, 8, 7}, {7, 1, 3}, {1, 9, 5}}), 17);

        System.out.println("\nAll Day 1 tests passed.");
    }

    static void check(String name, Object got, Object want) {
        if (!Objects.equals(got, want)) throw new AssertionError(name + ": got " + got + ", want " + want);
        System.out.println("PASS  " + name + "  -> " + got);
    }
}
