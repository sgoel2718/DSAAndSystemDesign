import java.util.*;
import java.util.stream.*;

/**
 * Set Matrix Zeroes (Medium) - Day 2
 * https://leetcode.com/problems/set-matrix-zeroes/
 *
 * Approach 1: Copy the matrix  |  Time O(m x n x (m + n))  |  Space O(m x n)
 * Approach 2: Row and column flag arrays  |  Time O(m x n)  |  Space O(m + n)
 * Approach 3: Use the first row and column as the flags (optimal)  |  Time O(m x n)  |  Space O(1)  <- best
 *
 * Run: javac SetMatrixZeroes.java && java SetMatrixZeroes
 */
public class SetMatrixZeroes {

    // Approach 1: Copy the matrix
    // Time O(m x n x (m + n)), Space O(m x n)
    // Idea: Read zeros from an untouched copy so newly written zeros do not spread.
    static class Approach1 {
        public void setZeroes(int[][] matrix) {
            int m = matrix.length, n = matrix[0].length;
            int[][] orig = new int[m][];
            for (int i = 0; i < m; i++) orig[i] = matrix[i].clone();
            for (int i = 0; i < m; i++)
                for (int j = 0; j < n; j++)
                    if (orig[i][j] == 0) {
                        for (int c = 0; c < n; c++) matrix[i][c] = 0;
                        for (int r = 0; r < m; r++) matrix[r][j] = 0;
                    }
        }
    }

    // Approach 2: Row and column flag arrays
    // Time O(m x n), Space O(m + n)
    // Idea: First pass: mark which rows and columns contain a zero. Second pass: zero a cell if its row or column is marked.
    static class Approach2 {
        public void setZeroes(int[][] matrix) {
            int m = matrix.length, n = matrix[0].length;
            boolean[] row = new boolean[m], col = new boolean[n];
            for (int i = 0; i < m; i++)
                for (int j = 0; j < n; j++)
                    if (matrix[i][j] == 0) { row[i] = true; col[j] = true; }
            for (int i = 0; i < m; i++)
                for (int j = 0; j < n; j++)
                    if (row[i] || col[j]) matrix[i][j] = 0;
        }
    }

    // Approach 3: Use the first row and column as the flags (optimal)
    // Time O(m x n), Space O(1)
    // Idea: Store the row/column marks inside the matrix itself. Two booleans remember whether the first row/column themselves need zeroing.
    static class Approach3 {
        public void setZeroes(int[][] matrix) {
            int m = matrix.length, n = matrix[0].length;
            boolean firstRow = false, firstCol = false;
            for (int j = 0; j < n; j++) if (matrix[0][j] == 0) firstRow = true;
            for (int i = 0; i < m; i++) if (matrix[i][0] == 0) firstCol = true;
            for (int i = 1; i < m; i++)
                for (int j = 1; j < n; j++)
                    if (matrix[i][j] == 0) { matrix[i][0] = 0; matrix[0][j] = 0; }
            for (int i = 1; i < m; i++)
                for (int j = 1; j < n; j++)
                    if (matrix[i][0] == 0 || matrix[0][j] == 0) matrix[i][j] = 0;
            if (firstRow) for (int j = 0; j < n; j++) matrix[0][j] = 0;
            if (firstCol) for (int i = 0; i < m; i++) matrix[i][0] = 0;
        }
    }

    static String show(Object r) {
        if (r instanceof int[] a) return Arrays.toString(a);
        if (r instanceof int[][] a) return Arrays.deepToString(a);
        if (r instanceof ListNode l) return toList(l);
        return String.valueOf(r);
    }
    static String norm(List<List<Integer>> x) {                 // order-independent view of a list of lists
        List<List<Integer>> c = new ArrayList<>();
        for (List<Integer> t : x) { List<Integer> s = new ArrayList<>(t); Collections.sort(s); c.add(s); }
        c.sort((p, q) -> { for (int i = 0; i < Math.min(p.size(), q.size()); i++) { int d = Integer.compare(p.get(i), q.get(i)); if (d != 0) return d; } return p.size() - q.size(); });
        return c.toString();
    }
    static String sorted(List<Integer> x) { List<Integer> c = new ArrayList<>(x); Collections.sort(c); return c.toString(); }
    static class ListNode {
        int val; ListNode next;
        ListNode() {}
        ListNode(int val) { this.val = val; }
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
    }
    static ListNode list(int... v) { ListNode d = new ListNode(0), t = d; for (int x : v) { t.next = new ListNode(x); t = t.next; } return d.next; }
    static ListNode cyclic(int[] v, int pos) {                   // list whose tail links back to index pos (-1 = no cycle)
        ListNode h = list(v), t = h, at = null;
        for (int i = 0; t != null; i++, t = t.next) { if (i == pos) at = t; if (t.next == null) { t.next = at; break; } }
        return h;
    }
    static String toList(ListNode h) { List<Integer> o = new ArrayList<>(); for (int i = 0; h != null && i < 1000; i++, h = h.next) o.add(h.val); return o.toString(); }
    static int passed = 0;
    static void check(String what, Object r, String want) {
        String got = show(r);
        if (!got.equals(want)) throw new AssertionError(what + ": got " + got + ", want " + want);
        passed++;
    }

    public static void main(String[] args) {
        { Approach1 o = new Approach1(); Object r; int[][] a = {{1,1,1},{1,0,1},{1,1,1}}; o.setZeroes(a); r = a; check("Approach 1", r, "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]"); }
        { Approach1 o = new Approach1(); Object r; int[][] a = {{0,1,2,0},{3,4,5,2},{1,3,1,5}}; o.setZeroes(a); r = a; check("Approach 1", r, "[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]"); }
        { Approach2 o = new Approach2(); Object r; int[][] a = {{1,1,1},{1,0,1},{1,1,1}}; o.setZeroes(a); r = a; check("Approach 2", r, "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]"); }
        { Approach2 o = new Approach2(); Object r; int[][] a = {{0,1,2,0},{3,4,5,2},{1,3,1,5}}; o.setZeroes(a); r = a; check("Approach 2", r, "[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]"); }
        { Approach3 o = new Approach3(); Object r; int[][] a = {{1,1,1},{1,0,1},{1,1,1}}; o.setZeroes(a); r = a; check("Approach 3", r, "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]"); }
        { Approach3 o = new Approach3(); Object r; int[][] a = {{0,1,2,0},{3,4,5,2},{1,3,1,5}}; o.setZeroes(a); r = a; check("Approach 3", r, "[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]"); }
        System.out.println("SetMatrixZeroes: all 3 approaches passed " + passed + " checks");
    }
}
