import java.util.*;
import java.util.stream.*;

/**
 * Contains Duplicate (Easy) - Day 1
 * https://leetcode.com/problems/contains-duplicate/
 *
 * Approach 1: Brute force: every pair  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sort, then compare neighbours  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 3: HashSet (optimal time)  |  Time O(n)  |  Space O(n)  <- best
 * Approach 4: Stream distinct count  |  Time O(n)  |  Space O(n)
 *
 * Run: javac ContainsDuplicate.java && java ContainsDuplicate
 */
public class ContainsDuplicate {

    // Approach 1: Brute force: every pair
    // Time O(n^2), Space O(1)
    // Idea: Compare every pair of elements.
    static class Approach1 {
        public boolean containsDuplicate(int[] nums) {
            for (int i = 0; i < nums.length; i++) {
                for (int j = i + 1; j < nums.length; j++) {
                    if (nums[i] == nums[j]) return true;
                }
            }
            return false;
        }
    }

    // Approach 2: Sort, then compare neighbours
    // Time O(n log n), Space O(log n) sort stack
    // Idea: After sorting, equal values sit next to each other. Mutates the input.
    static class Approach2 {
        public boolean containsDuplicate(int[] nums) {
            Arrays.sort(nums);
            for (int i = 1; i < nums.length; i++) {
                if (nums[i] == nums[i - 1]) return true;
            }
            return false;
        }
    }

    // Approach 3: HashSet (optimal time)
    // Time O(n), Space O(n)
    // Idea: Set.add returns false when the value is already present.
    static class Approach3 {
        public boolean containsDuplicate(int[] nums) {
            Set<Integer> seen = new HashSet<>();
            for (int x : nums) {
                if (!seen.add(x)) return true;
            }
            return false;
        }
    }

    // Approach 4: Stream distinct count
    // Time O(n), Space O(n)
    // Idea: Short one-liner: compare the distinct count with the length. Fine to mention, but it always scans everything and boxes each int.
    static class Approach4 {
        public boolean containsDuplicate(int[] nums) {
            return Arrays.stream(nums).distinct().count() < nums.length;
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
        check("Approach 1", new Approach1().containsDuplicate(new int[]{1,2,3,1}), "true");
        check("Approach 1", new Approach1().containsDuplicate(new int[]{1,2,3,4}), "false");
        check("Approach 1", new Approach1().containsDuplicate(new int[]{}), "false");
        check("Approach 2", new Approach2().containsDuplicate(new int[]{1,2,3,1}), "true");
        check("Approach 2", new Approach2().containsDuplicate(new int[]{1,2,3,4}), "false");
        check("Approach 2", new Approach2().containsDuplicate(new int[]{}), "false");
        check("Approach 3", new Approach3().containsDuplicate(new int[]{1,2,3,1}), "true");
        check("Approach 3", new Approach3().containsDuplicate(new int[]{1,2,3,4}), "false");
        check("Approach 3", new Approach3().containsDuplicate(new int[]{}), "false");
        check("Approach 4", new Approach4().containsDuplicate(new int[]{1,2,3,1}), "true");
        check("Approach 4", new Approach4().containsDuplicate(new int[]{1,2,3,4}), "false");
        check("Approach 4", new Approach4().containsDuplicate(new int[]{}), "false");
        System.out.println("ContainsDuplicate: all 4 approaches passed " + passed + " checks");
    }
}
