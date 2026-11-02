import java.util.*;
import java.util.stream.*;

/**
 * Missing Number (Easy) - Day 2
 * https://leetcode.com/problems/missing-number/
 *
 * Approach 1: Sort and find the gap  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 2: HashSet  |  Time O(n)  |  Space O(n)
 * Approach 3: Cyclic sort  |  Time O(n)  |  Space O(1)
 * Approach 4: Gauss sum formula  |  Time O(n)  |  Space O(1)
 * Approach 5: XOR (optimal, no overflow risk)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac MissingNumber.java && java MissingNumber
 */
public class MissingNumber {

    // Approach 1: Sort and find the gap
    // Time O(n log n), Space O(log n) sort stack
    // Idea: After sorting, index i should hold i; the first mismatch is the answer.
    static class Approach1 {
        public int missingNumber(int[] nums) {
            Arrays.sort(nums);
            for (int i = 0; i < nums.length; i++) if (nums[i] != i) return i;
            return nums.length;
        }
    }

    // Approach 2: HashSet
    // Time O(n), Space O(n)
    // Idea: Put everything in a set and check 0..n.
    static class Approach2 {
        public int missingNumber(int[] nums) {
            Set<Integer> seen = new HashSet<>();
            for (int x : nums) seen.add(x);
            for (int i = 0; i <= nums.length; i++) if (!seen.contains(i)) return i;
            return -1;
        }
    }

    // Approach 3: Cyclic sort
    // Time O(n), Space O(1)
    // Idea: Swap each value v into index v (ignore v = n). The first index i with nums[i] != i is missing.
    static class Approach3 {
        public int missingNumber(int[] nums) {
            int n = nums.length, i = 0;
            while (i < n) {
                int v = nums[i];
                if (v < n && nums[v] != v) { nums[i] = nums[v]; nums[v] = v; }
                else i++;
            }
            for (i = 0; i < n; i++) if (nums[i] != i) return i;
            return n;
        }
    }

    // Approach 4: Gauss sum formula
    // Time O(n), Space O(1)
    // Idea: Expected sum 0..n is n(n+1)/2; the difference with the actual sum is the missing number. Use long to be safe from overflow.
    static class Approach4 {
        public int missingNumber(int[] nums) {
            long n = nums.length, expected = n * (n + 1) / 2, actual = 0;
            for (int x : nums) actual += x;
            return (int) (expected - actual);
        }
    }

    // Approach 5: XOR (optimal, no overflow risk)
    // Time O(n), Space O(1)
    // Idea: XOR all indices 0..n with all values; every present number cancels itself (a ^ a = 0), leaving the missing one.
    static class Approach5 {
        public int missingNumber(int[] nums) {
            int x = nums.length;
            for (int i = 0; i < nums.length; i++) x ^= i ^ nums[i];
            return x;
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
        check("Approach 1", new Approach1().missingNumber(new int[]{3,0,1}), "2");
        check("Approach 1", new Approach1().missingNumber(new int[]{0,1}), "2");
        check("Approach 1", new Approach1().missingNumber(new int[]{9,6,4,2,3,5,7,0,1}), "8");
        check("Approach 2", new Approach2().missingNumber(new int[]{3,0,1}), "2");
        check("Approach 2", new Approach2().missingNumber(new int[]{0,1}), "2");
        check("Approach 2", new Approach2().missingNumber(new int[]{9,6,4,2,3,5,7,0,1}), "8");
        check("Approach 3", new Approach3().missingNumber(new int[]{3,0,1}), "2");
        check("Approach 3", new Approach3().missingNumber(new int[]{0,1}), "2");
        check("Approach 3", new Approach3().missingNumber(new int[]{9,6,4,2,3,5,7,0,1}), "8");
        check("Approach 4", new Approach4().missingNumber(new int[]{3,0,1}), "2");
        check("Approach 4", new Approach4().missingNumber(new int[]{0,1}), "2");
        check("Approach 4", new Approach4().missingNumber(new int[]{9,6,4,2,3,5,7,0,1}), "8");
        check("Approach 5", new Approach5().missingNumber(new int[]{3,0,1}), "2");
        check("Approach 5", new Approach5().missingNumber(new int[]{0,1}), "2");
        check("Approach 5", new Approach5().missingNumber(new int[]{9,6,4,2,3,5,7,0,1}), "8");
        System.out.println("MissingNumber: all 5 approaches passed " + passed + " checks");
    }
}
