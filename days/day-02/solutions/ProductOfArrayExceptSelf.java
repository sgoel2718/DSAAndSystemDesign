import java.util.*;
import java.util.stream.*;

/**
 * Product of Array Except Self (Medium) - Day 2
 * https://leetcode.com/problems/product-of-array-except-self/
 *
 * Approach 1: Brute force: multiply all others  |  Time O(n^2)  |  Space O(1) besides output
 * Approach 2: Prefix and suffix product arrays  |  Time O(n)  |  Space O(n)
 * Approach 3: Prefix in output, suffix in one variable (optimal)  |  Time O(n)  |  Space O(1) besides output  <- best
 *
 * Run: javac ProductOfArrayExceptSelf.java && java ProductOfArrayExceptSelf
 */
public class ProductOfArrayExceptSelf {

    // Approach 1: Brute force: multiply all others
    // Time O(n^2), Space O(1) besides output
    // Idea: For each index multiply every other element. (Division is not allowed by the problem and breaks on zeros.)
    static class Approach1 {
        public int[] productExceptSelf(int[] nums) {
            int n = nums.length;
            int[] out = new int[n];
            for (int i = 0; i < n; i++) {
                int p = 1;
                for (int j = 0; j < n; j++) if (j != i) p *= nums[j];
                out[i] = p;
            }
            return out;
        }
    }

    // Approach 2: Prefix and suffix product arrays
    // Time O(n), Space O(n)
    // Idea: answer[i] = (product of everything left of i) x (product of everything right of i).
    static class Approach2 {
        public int[] productExceptSelf(int[] nums) {
            int n = nums.length;
            int[] left = new int[n], right = new int[n], out = new int[n];
            left[0] = 1;
            for (int i = 1; i < n; i++) left[i] = left[i - 1] * nums[i - 1];
            right[n - 1] = 1;
            for (int i = n - 2; i >= 0; i--) right[i] = right[i + 1] * nums[i + 1];
            for (int i = 0; i < n; i++) out[i] = left[i] * right[i];
            return out;
        }
    }

    // Approach 3: Prefix in output, suffix in one variable (optimal)
    // Time O(n), Space O(1) besides output
    // Idea: Store left products directly in the output array, then sweep from the right multiplying by a running suffix product.
    static class Approach3 {
        public int[] productExceptSelf(int[] nums) {
            int n = nums.length;
            int[] out = new int[n];
            out[0] = 1;
            for (int i = 1; i < n; i++) out[i] = out[i - 1] * nums[i - 1];
            int suffix = 1;
            for (int i = n - 1; i >= 0; i--) {
                out[i] *= suffix;
                suffix *= nums[i];
            }
            return out;
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
        check("Approach 1", new Approach1().productExceptSelf(new int[]{1,2,3,4}), "[24, 12, 8, 6]");
        check("Approach 1", new Approach1().productExceptSelf(new int[]{-1,1,0,-3,3}), "[0, 0, 9, 0, 0]");
        check("Approach 2", new Approach2().productExceptSelf(new int[]{1,2,3,4}), "[24, 12, 8, 6]");
        check("Approach 2", new Approach2().productExceptSelf(new int[]{-1,1,0,-3,3}), "[0, 0, 9, 0, 0]");
        check("Approach 3", new Approach3().productExceptSelf(new int[]{1,2,3,4}), "[24, 12, 8, 6]");
        check("Approach 3", new Approach3().productExceptSelf(new int[]{-1,1,0,-3,3}), "[0, 0, 9, 0, 0]");
        System.out.println("ProductOfArrayExceptSelf: all 3 approaches passed " + passed + " checks");
    }
}
