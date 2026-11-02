import java.util.*;
import java.util.stream.*;

/**
 * Trapping Rain Water (Hard) - Day 2
 * https://leetcode.com/problems/trapping-rain-water/
 *
 * Approach 1: Brute force: scan left and right for each bar  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Prefix max + suffix max arrays  |  Time O(n)  |  Space O(n)
 * Approach 3: Monotonic stack  |  Time O(n)  |  Space O(n)
 * Approach 4: Two pointers (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac TrappingRainWater.java && java TrappingRainWater
 */
public class TrappingRainWater {

    // Approach 1: Brute force: scan left and right for each bar
    // Time O(n^2), Space O(1)
    // Idea: Water above bar i = min(tallest on its left, tallest on its right) - height[i].
    static class Approach1 {
        public int trap(int[] height) {
            int water = 0;
            for (int i = 0; i < height.length; i++) {
                int leftMax = 0, rightMax = 0;
                for (int j = i; j >= 0; j--) leftMax = Math.max(leftMax, height[j]);
                for (int j = i; j < height.length; j++) rightMax = Math.max(rightMax, height[j]);
                water += Math.min(leftMax, rightMax) - height[i];
            }
            return water;
        }
    }

    // Approach 2: Prefix max + suffix max arrays
    // Time O(n), Space O(n)
    // Idea: Precompute the tallest bar to the left and right of every index once.
    static class Approach2 {
        public int trap(int[] height) {
            int n = height.length;
            if (n == 0) return 0;
            int[] leftMax = new int[n], rightMax = new int[n];
            leftMax[0] = height[0];
            for (int i = 1; i < n; i++) leftMax[i] = Math.max(leftMax[i - 1], height[i]);
            rightMax[n - 1] = height[n - 1];
            for (int i = n - 2; i >= 0; i--) rightMax[i] = Math.max(rightMax[i + 1], height[i]);
            int water = 0;
            for (int i = 0; i < n; i++) water += Math.min(leftMax[i], rightMax[i]) - height[i];
            return water;
        }
    }

    // Approach 3: Monotonic stack
    // Time O(n), Space O(n)
    // Idea: Keep a decreasing stack of indices. When a taller bar arrives, pop the bottom of a 'bowl' and add the water layer between the new bar and the bar below it on the stack.
    static class Approach3 {
        public int trap(int[] height) {
            Deque<Integer> st = new ArrayDeque<>();
            int water = 0;
            for (int i = 0; i < height.length; i++) {
                while (!st.isEmpty() && height[i] > height[st.peek()]) {
                    int bottom = st.pop();
                    if (st.isEmpty()) break;
                    int left = st.peek();
                    int width = i - left - 1;
                    int h = Math.min(height[left], height[i]) - height[bottom];
                    water += width * h;
                }
                st.push(i);
            }
            return water;
        }
    }

    // Approach 4: Two pointers (optimal)
    // Time O(n), Space O(1)
    // Idea: Move the side with the smaller max inward: that side's water is fully decided by its own max, because the other side is at least as tall.
    static class Approach4 {
        public int trap(int[] height) {
            int l = 0, r = height.length - 1, leftMax = 0, rightMax = 0, water = 0;
            while (l < r) {
                if (height[l] < height[r]) {
                    leftMax = Math.max(leftMax, height[l]);
                    water += leftMax - height[l];
                    l++;
                } else {
                    rightMax = Math.max(rightMax, height[r]);
                    water += rightMax - height[r];
                    r--;
                }
            }
            return water;
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
        check("Approach 1", new Approach1().trap(new int[]{0,1,0,2,1,0,1,3,2,1,2,1}), "6");
        check("Approach 1", new Approach1().trap(new int[]{4,2,0,3,2,5}), "9");
        check("Approach 1", new Approach1().trap(new int[]{}), "0");
        check("Approach 2", new Approach2().trap(new int[]{0,1,0,2,1,0,1,3,2,1,2,1}), "6");
        check("Approach 2", new Approach2().trap(new int[]{4,2,0,3,2,5}), "9");
        check("Approach 2", new Approach2().trap(new int[]{}), "0");
        check("Approach 3", new Approach3().trap(new int[]{0,1,0,2,1,0,1,3,2,1,2,1}), "6");
        check("Approach 3", new Approach3().trap(new int[]{4,2,0,3,2,5}), "9");
        check("Approach 3", new Approach3().trap(new int[]{}), "0");
        check("Approach 4", new Approach4().trap(new int[]{0,1,0,2,1,0,1,3,2,1,2,1}), "6");
        check("Approach 4", new Approach4().trap(new int[]{4,2,0,3,2,5}), "9");
        check("Approach 4", new Approach4().trap(new int[]{}), "0");
        System.out.println("TrappingRainWater: all 4 approaches passed " + passed + " checks");
    }
}
