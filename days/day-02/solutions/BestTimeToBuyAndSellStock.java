import java.util.*;
import java.util.stream.*;

/**
 * Best Time to Buy and Sell Stock (Easy) - Day 2
 * https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
 *
 * Approach 1: Brute force: every buy/sell pair  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Kadane on daily differences  |  Time O(n)  |  Space O(1)
 * Approach 3: One pass: track the minimum so far (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac BestTimeToBuyAndSellStock.java && java BestTimeToBuyAndSellStock
 */
public class BestTimeToBuyAndSellStock {

    // Approach 1: Brute force: every buy/sell pair
    // Time O(n^2), Space O(1)
    // Idea: Try every buy day i and every later sell day j; keep the best profit.
    static class Approach1 {
        public int maxProfit(int[] prices) {
            int best = 0;
            for (int i = 0; i < prices.length; i++) {
                for (int j = i + 1; j < prices.length; j++) {
                    best = Math.max(best, prices[j] - prices[i]);
                }
            }
            return best;
        }
    }

    // Approach 2: Kadane on daily differences
    // Time O(n), Space O(1)
    // Idea: Profit of buying on i and selling on j equals the sum of daily changes between them, so it is a maximum-subarray problem on the differences.
    static class Approach2 {
        public int maxProfit(int[] prices) {
            int cur = 0, best = 0;
            for (int i = 1; i < prices.length; i++) {
                cur = Math.max(0, cur + prices[i] - prices[i - 1]);
                best = Math.max(best, cur);
            }
            return best;
        }
    }

    // Approach 3: One pass: track the minimum so far (optimal)
    // Time O(n), Space O(1)
    // Idea: Sliding window of size 'best buy day so far': for each day, the best sale is today's price minus the cheapest price seen before it.
    static class Approach3 {
        public int maxProfit(int[] prices) {
            int minPrice = Integer.MAX_VALUE, best = 0;
            for (int p : prices) {
                minPrice = Math.min(minPrice, p);
                best = Math.max(best, p - minPrice);
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
        check("Approach 1", new Approach1().maxProfit(new int[]{7,1,5,3,6,4}), "5");
        check("Approach 1", new Approach1().maxProfit(new int[]{7,6,4,3,1}), "0");
        check("Approach 1", new Approach1().maxProfit(new int[]{2,4,1}), "2");
        check("Approach 2", new Approach2().maxProfit(new int[]{7,1,5,3,6,4}), "5");
        check("Approach 2", new Approach2().maxProfit(new int[]{7,6,4,3,1}), "0");
        check("Approach 2", new Approach2().maxProfit(new int[]{2,4,1}), "2");
        check("Approach 3", new Approach3().maxProfit(new int[]{7,1,5,3,6,4}), "5");
        check("Approach 3", new Approach3().maxProfit(new int[]{7,6,4,3,1}), "0");
        check("Approach 3", new Approach3().maxProfit(new int[]{2,4,1}), "2");
        System.out.println("BestTimeToBuyAndSellStock: all 3 approaches passed " + passed + " checks");
    }
}
