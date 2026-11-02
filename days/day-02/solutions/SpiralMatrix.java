import java.util.*;
import java.util.stream.*;

/**
 * Spiral Matrix (Medium) - Day 2
 * https://leetcode.com/problems/spiral-matrix/
 *
 * Approach 1: Simulation with a visited matrix  |  Time O(m x n)  |  Space O(m x n)
 * Approach 2: Shrinking boundaries (optimal)  |  Time O(m x n)  |  Space O(1) besides output  <- best
 *
 * Run: javac SpiralMatrix.java && java SpiralMatrix
 */
public class SpiralMatrix {

    // Approach 1: Simulation with a visited matrix
    // Time O(m x n), Space O(m x n)
    // Idea: Walk right, down, left, up; turn whenever the next cell is outside or already visited.
    static class Approach1 {
        public List<Integer> spiralOrder(int[][] matrix) {
            int m = matrix.length, n = matrix[0].length;
            boolean[][] seen = new boolean[m][n];
            int[] dr = {0, 1, 0, -1}, dc = {1, 0, -1, 0};
            List<Integer> out = new ArrayList<>();
            int r = 0, c = 0, d = 0;
            for (int k = 0; k < m * n; k++) {
                out.add(matrix[r][c]);
                seen[r][c] = true;
                int nr = r + dr[d], nc = c + dc[d];
                if (nr < 0 || nr >= m || nc < 0 || nc >= n || seen[nr][nc]) {
                    d = (d + 1) % 4;
                    nr = r + dr[d];
                    nc = c + dc[d];
                }
                r = nr;
                c = nc;
            }
            return out;
        }
    }

    // Approach 2: Shrinking boundaries (optimal)
    // Time O(m x n), Space O(1) besides output
    // Idea: Keep top, bottom, left, right walls. Walk one side, then move that wall inward. Check the walls again before the bottom row and left column so a single row/column is not repeated.
    static class Approach2 {
        public List<Integer> spiralOrder(int[][] matrix) {
            List<Integer> out = new ArrayList<>();
            int top = 0, bottom = matrix.length - 1, left = 0, right = matrix[0].length - 1;
            while (top <= bottom && left <= right) {
                for (int c = left; c <= right; c++) out.add(matrix[top][c]);
                top++;
                for (int r = top; r <= bottom; r++) out.add(matrix[r][right]);
                right--;
                if (top <= bottom) {
                    for (int c = right; c >= left; c--) out.add(matrix[bottom][c]);
                    bottom--;
                }
                if (left <= right) {
                    for (int r = bottom; r >= top; r--) out.add(matrix[r][left]);
                    left++;
                }
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
        check("Approach 1", new Approach1().spiralOrder(new int[][]{{1,2,3},{4,5,6},{7,8,9}}), "[1, 2, 3, 6, 9, 8, 7, 4, 5]");
        check("Approach 1", new Approach1().spiralOrder(new int[][]{{1,2,3,4},{5,6,7,8},{9,10,11,12}}), "[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]");
        check("Approach 1", new Approach1().spiralOrder(new int[][]{{1},{2},{3}}), "[1, 2, 3]");
        check("Approach 2", new Approach2().spiralOrder(new int[][]{{1,2,3},{4,5,6},{7,8,9}}), "[1, 2, 3, 6, 9, 8, 7, 4, 5]");
        check("Approach 2", new Approach2().spiralOrder(new int[][]{{1,2,3,4},{5,6,7,8},{9,10,11,12}}), "[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]");
        check("Approach 2", new Approach2().spiralOrder(new int[][]{{1},{2},{3}}), "[1, 2, 3]");
        System.out.println("SpiralMatrix: all 2 approaches passed " + passed + " checks");
    }
}
