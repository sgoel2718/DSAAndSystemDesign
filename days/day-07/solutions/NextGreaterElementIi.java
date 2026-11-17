import java.util.*;
import java.util.stream.*;

/**
 * Next Greater Element II (Medium) - Day 7
 * https://leetcode.com/problems/next-greater-element-ii/
 *
 * Approach 1: Brute force: walk around the circle  |  Time O(n^2)  |  Space O(1) besides output
 * Approach 2: Monotonic stack over two passes (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac NextGreaterElementIi.java && java NextGreaterElementIi
 */
public class NextGreaterElementIi {

    // Approach 1: Brute force: walk around the circle
    // Time O(n^2), Space O(1) besides output
    // Idea: For each index, check the next n - 1 positions (mod n) for a greater value.
    static class Approach1 {
        public int[] nextGreaterElements(int[] nums) {
            int n = nums.length;
            int[] ans = new int[n];
            Arrays.fill(ans, -1);
            for (int i = 0; i < n; i++)
                for (int d = 1; d < n; d++)
                    if (nums[(i + d) % n] > nums[i]) { ans[i] = nums[(i + d) % n]; break; }
            return ans;
        }
    }

    // Approach 2: Monotonic stack over two passes (optimal)
    // Time O(n), Space O(n)
    // Idea: Loop i from 0 to 2n - 1 using i mod n, so elements near the end can see the start. Pop smaller waiting indices and give them the current value.
    static class Approach2 {
        public int[] nextGreaterElements(int[] nums) {
            int n = nums.length;
            int[] ans = new int[n];
            Arrays.fill(ans, -1);
            Deque<Integer> st = new ArrayDeque<>();
            for (int i = 0; i < 2 * n; i++) {
                int x = nums[i % n];
                while (!st.isEmpty() && nums[st.peek()] < x) ans[st.pop()] = x;
                if (i < n) st.push(i);
            }
            return ans;
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
        check("Approach 1", new Approach1().nextGreaterElements(new int[]{1,2,1}), "[2, -1, 2]");
        check("Approach 1", new Approach1().nextGreaterElements(new int[]{1,2,3,4,3}), "[2, 3, 4, -1, 4]");
        check("Approach 1", new Approach1().nextGreaterElements(new int[]{5,5,5}), "[-1, -1, -1]");
        check("Approach 2", new Approach2().nextGreaterElements(new int[]{1,2,1}), "[2, -1, 2]");
        check("Approach 2", new Approach2().nextGreaterElements(new int[]{1,2,3,4,3}), "[2, 3, 4, -1, 4]");
        check("Approach 2", new Approach2().nextGreaterElements(new int[]{5,5,5}), "[-1, -1, -1]");
        System.out.println("NextGreaterElementIi: all 2 approaches passed " + passed + " checks");
    }
}
