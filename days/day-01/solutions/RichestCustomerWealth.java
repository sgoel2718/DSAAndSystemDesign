import java.util.*;
import java.util.stream.*;

/**
 * Richest Customer Wealth (Easy) - Day 1
 * https://leetcode.com/problems/richest-customer-wealth/
 *
 * Approach 1: Nested loops (optimal)  |  Time O(m x n)  |  Space O(1)  <- best
 * Approach 2: Streams  |  Time O(m x n)  |  Space O(1)
 *
 * Run: javac RichestCustomerWealth.java && java RichestCustomerWealth
 */
public class RichestCustomerWealth {

    // Approach 1: Nested loops (optimal)
    // Time O(m x n), Space O(1)
    // Idea: Sum each customer's row and keep the maximum. Every cell must be read once, so this is optimal.
    static class Approach1 {
        public int maximumWealth(int[][] accounts) {
            int best = 0;
            for (int[] customer : accounts) {
                int sum = 0;
                for (int money : customer) sum += money;
                best = Math.max(best, sum);
            }
            return best;
        }
    }

    // Approach 2: Streams
    // Time O(m x n), Space O(1)
    // Idea: Map each row to its sum and take the max. Readable; slightly slower than plain loops.
    static class Approach2 {
        public int maximumWealth(int[][] accounts) {
            return Arrays.stream(accounts)
                         .mapToInt(row -> Arrays.stream(row).sum())
                         .max()
                         .orElse(0);
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
        check("Approach 1", new Approach1().maximumWealth(new int[][]{{1,5},{7,3},{3,5}}), "10");
        check("Approach 1", new Approach1().maximumWealth(new int[][]{{2,8,7},{7,1,3},{1,9,5}}), "17");
        check("Approach 2", new Approach2().maximumWealth(new int[][]{{1,5},{7,3},{3,5}}), "10");
        check("Approach 2", new Approach2().maximumWealth(new int[][]{{2,8,7},{7,1,3},{1,9,5}}), "17");
        System.out.println("RichestCustomerWealth: all 2 approaches passed " + passed + " checks");
    }
}
