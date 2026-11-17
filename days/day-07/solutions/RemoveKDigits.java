import java.util.*;
import java.util.stream.*;

/**
 * Remove K Digits (Medium) - Day 7
 * https://leetcode.com/problems/remove-k-digits/
 *
 * Approach 1: Greedy, remove one digit k times  |  Time O(n x k)  |  Space O(n)
 * Approach 2: Monotonic increasing stack (optimal)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac RemoveKDigits.java && java RemoveKDigits
 */
public class RemoveKDigits {

    // Approach 1: Greedy, remove one digit k times
    // Time O(n x k), Space O(n)
    // Idea: To shrink a number the most, delete the first digit that is bigger than the digit after it (or the last digit). Repeat k times.
    static class Approach1 {
        public String removeKdigits(String num, int k) {
            StringBuilder sb = new StringBuilder(num);
            for (int t = 0; t < k; t++) {
                int i = 0;
                while (i < sb.length() - 1 && sb.charAt(i) <= sb.charAt(i + 1)) i++;
                sb.deleteCharAt(i);
            }
            int z = 0;
            while (z < sb.length() - 1 && sb.charAt(z) == '0') z++;
            String res = sb.substring(z);
            return res.isEmpty() ? "0" : res;
        }
    }

    // Approach 2: Monotonic increasing stack (optimal)
    // Time O(n), Space O(n)
    // Idea: Same greedy rule in one pass: while k > 0 and the previous digit is bigger than the current one, pop it. Remove any remaining k from the end, then strip leading zeros.
    static class Approach2 {
        public String removeKdigits(String num, int k) {
            StringBuilder st = new StringBuilder();
            for (char c : num.toCharArray()) {
                while (k > 0 && st.length() > 0 && st.charAt(st.length() - 1) > c) {
                    st.deleteCharAt(st.length() - 1);
                    k--;
                }
                st.append(c);
            }
            st.setLength(st.length() - k);
            int z = 0;
            while (z < st.length() - 1 && st.charAt(z) == '0') z++;
            String res = st.substring(z);
            return res.isEmpty() ? "0" : res;
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
        check("Approach 1", new Approach1().removeKdigits("1432219", 3), "1219");
        check("Approach 1", new Approach1().removeKdigits("10200", 1), "200");
        check("Approach 1", new Approach1().removeKdigits("10", 2), "0");
        check("Approach 1", new Approach1().removeKdigits("112", 1), "11");
        check("Approach 1", new Approach1().removeKdigits("9", 1), "0");
        check("Approach 2", new Approach2().removeKdigits("1432219", 3), "1219");
        check("Approach 2", new Approach2().removeKdigits("10200", 1), "200");
        check("Approach 2", new Approach2().removeKdigits("10", 2), "0");
        check("Approach 2", new Approach2().removeKdigits("112", 1), "11");
        check("Approach 2", new Approach2().removeKdigits("9", 1), "0");
        System.out.println("RemoveKDigits: all 2 approaches passed " + passed + " checks");
    }
}
