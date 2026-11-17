import java.util.*;
import java.util.stream.*;

/**
 * Fruit Into Baskets (Medium) - Day 2
 * https://leetcode.com/problems/fruit-into-baskets/
 *
 * Approach 1: Brute force: grow from every start  |  Time O(n^2)  |  Space O(1)
 * Approach 2: Sliding window with a HashMap of counts  |  Time O(n)  |  Space O(1) (at most 3 keys)
 * Approach 3: Track the last two types and the last run (optimal, no map)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac FruitIntoBaskets.java && java FruitIntoBaskets
 */
public class FruitIntoBaskets {

    // Approach 1: Brute force: grow from every start
    // Time O(n^2), Space O(1)
    // Idea: From each tree, extend while at most two fruit types are in the baskets.
    static class Approach1 {
        public int totalFruit(int[] fruits) {
            int best = 0;
            for (int i = 0; i < fruits.length; i++) {
                Set<Integer> types = new HashSet<>();
                int j = i;
                while (j < fruits.length) {
                    types.add(fruits[j]);
                    if (types.size() > 2) break;
                    j++;
                }
                best = Math.max(best, j - i);
            }
            return best;
        }
    }

    // Approach 2: Sliding window with a HashMap of counts
    // Time O(n), Space O(1) (at most 3 keys)
    // Idea: This is 'longest subarray with at most 2 distinct values': shrink from the left while the map has more than two keys.
    static class Approach2 {
        public int totalFruit(int[] fruits) {
            Map<Integer, Integer> count = new HashMap<>();
            int l = 0, best = 0;
            for (int r = 0; r < fruits.length; r++) {
                count.merge(fruits[r], 1, Integer::sum);
                while (count.size() > 2) {
                    int f = fruits[l++];
                    if (count.merge(f, -1, Integer::sum) == 0) count.remove(f);
                }
                best = Math.max(best, r - l + 1);
            }
            return best;
        }
    }

    // Approach 3: Track the last two types and the last run (optimal, no map)
    // Time O(n), Space O(1)
    // Idea: Keep the last fruit type, the one before it, and how long the latest run of the last type is. A new third type resets the window to that run + 1.
    static class Approach3 {
        public int totalFruit(int[] fruits) {
            int last = -1, secondLast = -1, lastRun = 0, cur = 0, best = 0;
            for (int f : fruits) {
                cur = (f == last || f == secondLast) ? cur + 1 : lastRun + 1;
                if (f == last) lastRun++;
                else { lastRun = 1; secondLast = last; last = f; }
                best = Math.max(best, cur);
            }
            return best;
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
        check("Approach 1", new Approach1().totalFruit(new int[]{1,2,1}), "3");
        check("Approach 1", new Approach1().totalFruit(new int[]{0,1,2,2}), "3");
        check("Approach 1", new Approach1().totalFruit(new int[]{1,2,3,2,2}), "4");
        check("Approach 1", new Approach1().totalFruit(new int[]{3,3,3,1,2,1,1,2,3,3,4}), "5");
        check("Approach 2", new Approach2().totalFruit(new int[]{1,2,1}), "3");
        check("Approach 2", new Approach2().totalFruit(new int[]{0,1,2,2}), "3");
        check("Approach 2", new Approach2().totalFruit(new int[]{1,2,3,2,2}), "4");
        check("Approach 2", new Approach2().totalFruit(new int[]{3,3,3,1,2,1,1,2,3,3,4}), "5");
        check("Approach 3", new Approach3().totalFruit(new int[]{1,2,1}), "3");
        check("Approach 3", new Approach3().totalFruit(new int[]{0,1,2,2}), "3");
        check("Approach 3", new Approach3().totalFruit(new int[]{1,2,3,2,2}), "4");
        check("Approach 3", new Approach3().totalFruit(new int[]{3,3,3,1,2,1,1,2,3,3,4}), "5");
        System.out.println("FruitIntoBaskets: all 3 approaches passed " + passed + " checks");
    }
}
