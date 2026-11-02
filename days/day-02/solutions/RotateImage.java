import java.util.*;
import java.util.stream.*;

/**
 * Rotate Image (Medium) - Day 2
 * https://leetcode.com/problems/rotate-image/
 *
 * Approach 1: Copy into a new matrix  |  Time O(n^2)  |  Space O(n^2)
 * Approach 2: Rotate four cells at a time, layer by layer  |  Time O(n^2)  |  Space O(1)
 * Approach 3: Transpose, then reverse each row (optimal, easiest to explain)  |  Time O(n^2)  |  Space O(1)  <- best
 *
 * Run: javac RotateImage.java && java RotateImage
 */
public class RotateImage {

    // Approach 1: Copy into a new matrix
    // Time O(n^2), Space O(n^2)
    // Idea: Cell (i, j) moves to (j, n-1-i). Fill a copy, then write it back. Simple, but the problem asks for in-place.
    static class Approach1 {
        public void rotate(int[][] matrix) {
            int n = matrix.length;
            int[][] copy = new int[n][n];
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    copy[j][n - 1 - i] = matrix[i][j];
            for (int i = 0; i < n; i++) matrix[i] = copy[i];
        }
    }

    // Approach 2: Rotate four cells at a time, layer by layer
    // Time O(n^2), Space O(1)
    // Idea: Each cell in the outer ring trades places with 3 others (top -> right -> bottom -> left). Do it ring by ring.
    static class Approach2 {
        public void rotate(int[][] matrix) {
            int n = matrix.length;
            for (int i = 0; i < n / 2; i++) {
                for (int j = i; j < n - 1 - i; j++) {
                    int tmp = matrix[i][j];
                    matrix[i][j] = matrix[n - 1 - j][i];
                    matrix[n - 1 - j][i] = matrix[n - 1 - i][n - 1 - j];
                    matrix[n - 1 - i][n - 1 - j] = matrix[j][n - 1 - i];
                    matrix[j][n - 1 - i] = tmp;
                }
            }
        }
    }

    // Approach 3: Transpose, then reverse each row (optimal, easiest to explain)
    // Time O(n^2), Space O(1)
    // Idea: Clockwise rotation = transpose (swap across the main diagonal) + mirror each row.
    static class Approach3 {
        public void rotate(int[][] matrix) {
            int n = matrix.length;
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++) {
                    int t = matrix[i][j]; matrix[i][j] = matrix[j][i]; matrix[j][i] = t;
                }
            for (int[] row : matrix)
                for (int l = 0, r = n - 1; l < r; l++, r--) {
                    int t = row[l]; row[l] = row[r]; row[r] = t;
                }
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
        { Approach1 o = new Approach1(); Object r; int[][] a = {{1,2,3},{4,5,6},{7,8,9}}; o.rotate(a); r = a; check("Approach 1", r, "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]"); }
        { Approach1 o = new Approach1(); Object r; int[][] a = {{5,1,9,11},{2,4,8,10},{13,3,6,7},{15,14,12,16}}; o.rotate(a); r = a; check("Approach 1", r, "[[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]"); }
        { Approach1 o = new Approach1(); Object r; int[][] a = {{1}}; o.rotate(a); r = a; check("Approach 1", r, "[[1]]"); }
        { Approach2 o = new Approach2(); Object r; int[][] a = {{1,2,3},{4,5,6},{7,8,9}}; o.rotate(a); r = a; check("Approach 2", r, "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]"); }
        { Approach2 o = new Approach2(); Object r; int[][] a = {{5,1,9,11},{2,4,8,10},{13,3,6,7},{15,14,12,16}}; o.rotate(a); r = a; check("Approach 2", r, "[[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]"); }
        { Approach2 o = new Approach2(); Object r; int[][] a = {{1}}; o.rotate(a); r = a; check("Approach 2", r, "[[1]]"); }
        { Approach3 o = new Approach3(); Object r; int[][] a = {{1,2,3},{4,5,6},{7,8,9}}; o.rotate(a); r = a; check("Approach 3", r, "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]"); }
        { Approach3 o = new Approach3(); Object r; int[][] a = {{5,1,9,11},{2,4,8,10},{13,3,6,7},{15,14,12,16}}; o.rotate(a); r = a; check("Approach 3", r, "[[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]]"); }
        { Approach3 o = new Approach3(); Object r; int[][] a = {{1}}; o.rotate(a); r = a; check("Approach 3", r, "[[1]]"); }
        System.out.println("RotateImage: all 3 approaches passed " + passed + " checks");
    }
}
