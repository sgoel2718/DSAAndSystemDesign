import java.util.*;

/**
 * Day 2 - Live demo 3: two pointers and in-place matrix tricks, step by step.
 * Run:  javac TwoPointersDemo.java && java TwoPointersDemo
 */
public class TwoPointersDemo {

    public static void main(String[] args) {
        containerTrace(new int[]{1, 8, 6, 2, 5, 4, 8, 3, 7});
        kadaneTrace(new int[]{-2, 1, -3, 4, -1, 2, 1, -5, 4});
        rotateTrace();
    }

    // Opposite-ends two pointers: always move the shorter line
    static void containerTrace(int[] h) {
        System.out.println("1) Container With Most Water " + Arrays.toString(h));
        int l = 0, r = h.length - 1, best = 0;
        while (l < r) {
            int area = (r - l) * Math.min(h[l], h[r]);
            best = Math.max(best, area);
            String move = h[l] < h[r] ? "move l (shorter)" : "move r (shorter or equal)";
            System.out.printf("   l=%d(h=%d) r=%d(h=%d) width=%d area=%d best=%d -> %s%n", l, h[l], r, h[r], r - l, area, best, move);
            if (h[l] < h[r]) l++; else r--;
        }
        System.out.println("   Answer: " + best + "  (" + (h.length - 1) + " steps instead of " + h.length * (h.length - 1) / 2 + " pairs)\n");
    }

    // Kadane: extend or restart
    static void kadaneTrace(int[] a) {
        System.out.println("2) Kadane on " + Arrays.toString(a));
        int cur = a[0], best = a[0];
        System.out.printf("   x=%2d cur=%2d best=%2d%n", a[0], cur, best);
        for (int i = 1; i < a.length; i++) {
            boolean restart = a[i] > cur + a[i];
            cur = Math.max(a[i], cur + a[i]);
            best = Math.max(best, cur);
            System.out.printf("   x=%2d cur=%2d best=%2d  %s%n", a[i], cur, best, restart ? "<- restart here" : "");
        }
        System.out.println("   Answer: " + best + "\n");
    }

    // Rotate 90 degrees clockwise = transpose + reverse each row
    static void rotateTrace() {
        int[][] m = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
        System.out.println("3) Rotate image in place");
        show("   start", m);
        for (int i = 0; i < 3; i++) for (int j = i + 1; j < 3; j++) { int t = m[i][j]; m[i][j] = m[j][i]; m[j][i] = t; }
        show("   transposed", m);
        for (int[] row : m) for (int l = 0, r = 2; l < r; l++, r--) { int t = row[l]; row[l] = row[r]; row[r] = t; }
        show("   rows reversed (= rotated)", m);
    }

    static void show(String label, int[][] m) {
        System.out.println(label + ": " + Arrays.deepToString(m));
    }
}
