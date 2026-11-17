import java.util.*;
import java.util.stream.*;

/**
 * Simplify Path (Medium) - Day 7
 * https://leetcode.com/problems/simplify-path/
 *
 * Approach 1: Parse character by character  |  Time O(n)  |  Space O(n)
 * Approach 2: Split on '/' + stack (optimal, clearest)  |  Time O(n)  |  Space O(n)  <- best
 *
 * Run: javac SimplifyPath.java && java SimplifyPath
 */
public class SimplifyPath {

    // Approach 1: Parse character by character
    // Time O(n), Space O(n)
    // Idea: Read one name between slashes at a time without split(); '..' removes the last kept name, '.' and empty names are ignored.
    static class Approach1 {
        public String simplifyPath(String path) {
            List<String> parts = new ArrayList<>();
            int i = 0, n = path.length();
            while (i < n) {
                while (i < n && path.charAt(i) == '/') i++;
                int j = i;
                while (j < n && path.charAt(j) != '/') j++;
                String name = path.substring(i, j);
                if (name.equals("..")) { if (!parts.isEmpty()) parts.remove(parts.size() - 1); }
                else if (!name.isEmpty() && !name.equals(".")) parts.add(name);
                i = j;
            }
            return "/" + String.join("/", parts);
        }
    }

    // Approach 2: Split on '/' + stack (optimal, clearest)
    // Time O(n), Space O(n)
    // Idea: Split by '/', push real names on a stack, pop on '..', skip '.' and empty parts; join what remains.
    static class Approach2 {
        public String simplifyPath(String path) {
            Deque<String> st = new ArrayDeque<>();
            for (String part : path.split("/")) {
                if (part.equals("..")) { if (!st.isEmpty()) st.pollLast(); }
                else if (!part.isEmpty() && !part.equals(".")) st.offerLast(part);
            }
            return "/" + String.join("/", st);
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
        check("Approach 1", new Approach1().simplifyPath("/home/"), "/home");
        check("Approach 1", new Approach1().simplifyPath("/../"), "/");
        check("Approach 1", new Approach1().simplifyPath("/home//foo/"), "/home/foo");
        check("Approach 1", new Approach1().simplifyPath("/a/./b/../../c/"), "/c");
        check("Approach 1", new Approach1().simplifyPath("/.../a/../b/c/../d/./"), "/.../b/d");
        check("Approach 2", new Approach2().simplifyPath("/home/"), "/home");
        check("Approach 2", new Approach2().simplifyPath("/../"), "/");
        check("Approach 2", new Approach2().simplifyPath("/home//foo/"), "/home/foo");
        check("Approach 2", new Approach2().simplifyPath("/a/./b/../../c/"), "/c");
        check("Approach 2", new Approach2().simplifyPath("/.../a/../b/c/../d/./"), "/.../b/d");
        System.out.println("SimplifyPath: all 2 approaches passed " + passed + " checks");
    }
}
