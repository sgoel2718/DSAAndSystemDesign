import java.util.*;
import java.util.stream.*;

/**
 * Two Sum II - Input Array Is Sorted (Medium) - Day 1
 * https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/
 *
 * Approach 1: Brute force: every pair  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Binary search for the complement  |  Time O(n log n)  |  Space O(1)
 * Approach 3: HashMap  |  Time O(n)  |  Space O(n)
 * Approach 4: Two pointers (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac TwoSumII.java && java TwoSumII
 */
public class TwoSumII {

    // Approach 1: Brute force: every pair
    // Time O(n^2), Space O(1)
    // Idea: Ignore the sorted order and check all pairs.
    static class Approach1 {
        public int[] twoSum(int[] numbers, int target) {
            for (int i = 0; i < numbers.length; i++) {
                for (int j = i + 1; j < numbers.length; j++) {
                    if (numbers[i] + numbers[j] == target) return new int[]{i + 1, j + 1};
                }
            }
            return new int[0];
        }
    }

    // Approach 2: Binary search for the complement
    // Time O(n log n), Space O(1)
    // Idea: For each i, binary search target - numbers[i] in the part to its right.
    static class Approach2 {
        public int[] twoSum(int[] numbers, int target) {
            for (int i = 0; i < numbers.length; i++) {
                int need = target - numbers[i];
                int lo = i + 1, hi = numbers.length - 1;
                while (lo <= hi) {
                    int mid = lo + (hi - lo) / 2;
                    if (numbers[mid] == need) return new int[]{i + 1, mid + 1};
                    if (numbers[mid] < need) lo = mid + 1;
                    else hi = mid - 1;
                }
            }
            return new int[0];
        }
    }

    // Approach 3: HashMap
    // Time O(n), Space O(n)
    // Idea: Same as Two Sum I. Works, but wastes the sorted order and uses extra memory.
    static class Approach3 {
        public int[] twoSum(int[] numbers, int target) {
            Map<Integer, Integer> indexOf = new HashMap<>();
            for (int i = 0; i < numbers.length; i++) {
                Integer j = indexOf.get(target - numbers[i]);
                if (j != null) return new int[]{j + 1, i + 1};
                indexOf.put(numbers[i], i);
            }
            return new int[0];
        }
    }

    // Approach 4: Two pointers (optimal)
    // Time O(n), Space O(1)
    // Idea: Start at both ends. Sum too small -> move left right; too big -> move right left. Each step discards one element for good.
    static class Approach4 {
        public int[] twoSum(int[] numbers, int target) {
            int l = 0, r = numbers.length - 1;
            while (l < r) {
                int sum = numbers[l] + numbers[r];
                if (sum == target) return new int[]{l + 1, r + 1};
                if (sum < target) l++;
                else r--;
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
        check("Approach 1", new Approach1().twoSum(new int[]{2,7,11,15}, 9), "[1, 2]");
        check("Approach 1", new Approach1().twoSum(new int[]{2,3,4}, 6), "[1, 3]");
        check("Approach 1", new Approach1().twoSum(new int[]{-1,0}, -1), "[1, 2]");
        check("Approach 2", new Approach2().twoSum(new int[]{2,7,11,15}, 9), "[1, 2]");
        check("Approach 2", new Approach2().twoSum(new int[]{2,3,4}, 6), "[1, 3]");
        check("Approach 2", new Approach2().twoSum(new int[]{-1,0}, -1), "[1, 2]");
        check("Approach 3", new Approach3().twoSum(new int[]{2,7,11,15}, 9), "[1, 2]");
        check("Approach 3", new Approach3().twoSum(new int[]{2,3,4}, 6), "[1, 3]");
        check("Approach 3", new Approach3().twoSum(new int[]{-1,0}, -1), "[1, 2]");
        check("Approach 4", new Approach4().twoSum(new int[]{2,7,11,15}, 9), "[1, 2]");
        check("Approach 4", new Approach4().twoSum(new int[]{2,3,4}, 6), "[1, 3]");
        check("Approach 4", new Approach4().twoSum(new int[]{-1,0}, -1), "[1, 2]");
        System.out.println("TwoSumII: all 4 approaches passed " + passed + " checks");
    }
}
