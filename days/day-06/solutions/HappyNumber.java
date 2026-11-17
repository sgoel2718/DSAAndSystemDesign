import java.util.*;
import java.util.stream.*;

/**
 * Happy Number (Easy) - Day 6
 * https://leetcode.com/problems/happy-number/
 *
 * Approach 1: HashSet of seen numbers  |  Time O(log n) per step, few steps  |  Space O(log n)
 * Approach 2: Floyd's cycle detection (optimal)  |  Time O(log n) per step, few steps  |  Space O(1)  <- best
 *
 * Run: javac HappyNumber.java && java HappyNumber
 */
public class HappyNumber {

    // Approach 1: HashSet of seen numbers
    // Time O(log n) per step, few steps, Space O(log n)
    // Idea: Keep replacing n by the sum of the squares of its digits. If we reach 1 it is happy; if a number repeats we are in a loop.
    static class Approach1 {
        public boolean isHappy(int n) {
            Set<Integer> seen = new HashSet<>();
            while (n != 1 && seen.add(n)) n = next(n);
            return n == 1;
        }
        private int next(int n) {
            int s = 0;
            while (n > 0) { int d = n % 10; s += d * d; n /= 10; }
            return s;
        }
    }

    // Approach 2: Floyd's cycle detection (optimal)
    // Time O(log n) per step, few steps, Space O(1)
    // Idea: The sequence either reaches 1 or loops. Treat it as a linked list: slow takes one step, fast takes two; they meet inside the loop, and the number is happy only if they meet at 1.
    static class Approach2 {
        public boolean isHappy(int n) {
            int slow = n, fast = next(n);
            while (fast != 1 && slow != fast) {
                slow = next(slow);
                fast = next(next(fast));
            }
            return fast == 1;
        }
        private int next(int n) {
            int s = 0;
            while (n > 0) { int d = n % 10; s += d * d; n /= 10; }
            return s;
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
        check("Approach 1", new Approach1().isHappy(19), "true");
        check("Approach 1", new Approach1().isHappy(2), "false");
        check("Approach 1", new Approach1().isHappy(1), "true");
        check("Approach 1", new Approach1().isHappy(7), "true");
        check("Approach 2", new Approach2().isHappy(19), "true");
        check("Approach 2", new Approach2().isHappy(2), "false");
        check("Approach 2", new Approach2().isHappy(1), "true");
        check("Approach 2", new Approach2().isHappy(7), "true");
        System.out.println("HappyNumber: all 2 approaches passed " + passed + " checks");
    }
}
