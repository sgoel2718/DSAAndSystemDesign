import java.util.*;
import java.util.stream.*;

/**
 * Container With Most Water (Medium) - Day 2
 * https://leetcode.com/problems/container-with-most-water/
 *
 * Approach 1: Brute force: every pair of lines  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Two pointers from both ends (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac ContainerWithMostWater.java && java ContainerWithMostWater
 */
public class ContainerWithMostWater {

    // Approach 1: Brute force: every pair of lines
    // Time O(n^2), Space O(1)
    // Idea: Area = width x the shorter line. Try all pairs.
    static class Approach1 {
        public int maxArea(int[] height) {
            int best = 0;
            for (int i = 0; i < height.length; i++) {
                for (int j = i + 1; j < height.length; j++) {
                    best = Math.max(best, (j - i) * Math.min(height[i], height[j]));
                }
            }
            return best;
        }
    }

    // Approach 2: Two pointers from both ends (optimal)
    // Time O(n), Space O(1)
    // Idea: Start with the widest container. The shorter line limits the area, so moving the taller one can never help; always move the shorter one inward.
    static class Approach2 {
        public int maxArea(int[] height) {
            int l = 0, r = height.length - 1, best = 0;
            while (l < r) {
                best = Math.max(best, (r - l) * Math.min(height[l], height[r]));
                if (height[l] < height[r]) l++;
                else r--;
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
        check("Approach 1", new Approach1().maxArea(new int[]{1,8,6,2,5,4,8,3,7}), "49");
        check("Approach 1", new Approach1().maxArea(new int[]{1,1}), "1");
        check("Approach 2", new Approach2().maxArea(new int[]{1,8,6,2,5,4,8,3,7}), "49");
        check("Approach 2", new Approach2().maxArea(new int[]{1,1}), "1");
        System.out.println("ContainerWithMostWater: all 2 approaches passed " + passed + " checks");
    }
}
