import java.util.*;
import java.util.stream.*;

/**
 * Find the Duplicate Number (Medium) - Day 6
 * https://leetcode.com/problems/find-the-duplicate-number/
 *
 * Approach 1: Sort and compare neighbours  |  Time O(n log n)  |  Space O(log n) sort stack
 * Approach 2: HashSet  |  Time O(n)  |  Space O(n)
 * Approach 3: Binary search on the value (pigeonhole)  |  Time O(n log n)  |  Space O(1)
 * Approach 4: Floyd's cycle detection on indices (optimal)  |  Time O(n)  |  Space O(1)  <- best
 *
 * Run: javac FindTheDuplicateNumber.java && java FindTheDuplicateNumber
 */
public class FindTheDuplicateNumber {

    // Approach 1: Sort and compare neighbours
    // Time O(n log n), Space O(log n) sort stack
    // Idea: After sorting, the duplicate sits next to itself. Modifies the input, which the problem forbids, but it is a fine first answer.
    static class Approach1 {
        public int findDuplicate(int[] nums) {
            int[] a = nums.clone();
            Arrays.sort(a);
            for (int i = 1; i < a.length; i++) if (a[i] == a[i - 1]) return a[i];
            return -1;
        }
    }

    // Approach 2: HashSet
    // Time O(n), Space O(n)
    // Idea: The first value that is already in the set is the duplicate.
    static class Approach2 {
        public int findDuplicate(int[] nums) {
            Set<Integer> seen = new HashSet<>();
            for (int x : nums) if (!seen.add(x)) return x;
            return -1;
        }
    }

    // Approach 3: Binary search on the value (pigeonhole)
    // Time O(n log n), Space O(1)
    // Idea: For a guess mid, count values <= mid. If the count is greater than mid, the duplicate is in [1, mid]; otherwise it is above mid.
    static class Approach3 {
        public int findDuplicate(int[] nums) {
            int lo = 1, hi = nums.length - 1;
            while (lo < hi) {
                int mid = lo + (hi - lo) / 2, count = 0;
                for (int x : nums) if (x <= mid) count++;
                if (count > mid) hi = mid;
                else lo = mid + 1;
            }
            return lo;
        }
    }

    // Approach 4: Floyd's cycle detection on indices (optimal)
    // Time O(n), Space O(1)
    // Idea: Treat i -> nums[i] as a linked list. Two indices point to the duplicate value, so it is the entrance of a cycle: find it exactly like Linked List Cycle II.
    static class Approach4 {
        public int findDuplicate(int[] nums) {
            int slow = nums[0], fast = nums[0];
            do {
                slow = nums[slow];
                fast = nums[nums[fast]];
            } while (slow != fast);
            slow = nums[0];
            while (slow != fast) { slow = nums[slow]; fast = nums[fast]; }
            return slow;
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
        check("Approach 1", new Approach1().findDuplicate(new int[]{1,3,4,2,2}), "2");
        check("Approach 1", new Approach1().findDuplicate(new int[]{3,1,3,4,2}), "3");
        check("Approach 1", new Approach1().findDuplicate(new int[]{3,3,3,3,3}), "3");
        check("Approach 2", new Approach2().findDuplicate(new int[]{1,3,4,2,2}), "2");
        check("Approach 2", new Approach2().findDuplicate(new int[]{3,1,3,4,2}), "3");
        check("Approach 2", new Approach2().findDuplicate(new int[]{3,3,3,3,3}), "3");
        check("Approach 3", new Approach3().findDuplicate(new int[]{1,3,4,2,2}), "2");
        check("Approach 3", new Approach3().findDuplicate(new int[]{3,1,3,4,2}), "3");
        check("Approach 3", new Approach3().findDuplicate(new int[]{3,3,3,3,3}), "3");
        check("Approach 4", new Approach4().findDuplicate(new int[]{1,3,4,2,2}), "2");
        check("Approach 4", new Approach4().findDuplicate(new int[]{3,1,3,4,2}), "3");
        check("Approach 4", new Approach4().findDuplicate(new int[]{3,3,3,3,3}), "3");
        System.out.println("FindTheDuplicateNumber: all 4 approaches passed " + passed + " checks");
    }
}
