import java.util.*;
import java.util.stream.*;

/**
 * Fizz Buzz (Easy) - Day 1
 * https://leetcode.com/problems/fizz-buzz/
 *
 * Approach 1: Modulo checks (standard)  |  Time O(n)  |  Space O(1) besides output  <- best
 * Approach 2: String building (easy to extend)  |  Time O(n)  |  Space O(1) besides output
 * Approach 3: Counters, no modulo  |  Time O(n)  |  Space O(1) besides output
 *
 * Run: javac FizzBuzz.java && java FizzBuzz
 */
public class FizzBuzz {

    // Approach 1: Modulo checks (standard)
    // Time O(n), Space O(1) besides output
    // Idea: Check 15 first, then 3, then 5.
    static class Approach1 {
        public List<String> fizzBuzz(int n) {
            List<String> out = new ArrayList<>(n);
            for (int i = 1; i <= n; i++) {
                if (i % 15 == 0) out.add("FizzBuzz");
                else if (i % 3 == 0) out.add("Fizz");
                else if (i % 5 == 0) out.add("Buzz");
                else out.add(String.valueOf(i));
            }
            return out;
        }
    }

    // Approach 2: String building (easy to extend)
    // Time O(n), Space O(1) besides output
    // Idea: Append Fizz and Buzz independently; if nothing was appended use the number. Adding a new rule (e.g. 7 -> Bazz) is one line.
    static class Approach2 {
        public List<String> fizzBuzz(int n) {
            List<String> out = new ArrayList<>(n);
            for (int i = 1; i <= n; i++) {
                StringBuilder sb = new StringBuilder();
                if (i % 3 == 0) sb.append("Fizz");
                if (i % 5 == 0) sb.append("Buzz");
                out.add(sb.length() == 0 ? String.valueOf(i) : sb.toString());
            }
            return out;
        }
    }

    // Approach 3: Counters, no modulo
    // Time O(n), Space O(1) besides output
    // Idea: Keep counters that reset at 3 and 5. Useful follow-up when the interviewer says modulo is expensive.
    static class Approach3 {
        public List<String> fizzBuzz(int n) {
            List<String> out = new ArrayList<>(n);
            int three = 0, five = 0;
            for (int i = 1; i <= n; i++) {
                three++;
                five++;
                if (three == 3 && five == 5) { out.add("FizzBuzz"); three = 0; five = 0; }
                else if (three == 3) { out.add("Fizz"); three = 0; }
                else if (five == 5) { out.add("Buzz"); five = 0; }
                else out.add(String.valueOf(i));
            }
            return out;
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
        check("Approach 1", new Approach1().fizzBuzz(3), "[1, 2, Fizz]");
        check("Approach 1", new Approach1().fizzBuzz(15), "[1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz]");
        check("Approach 2", new Approach2().fizzBuzz(3), "[1, 2, Fizz]");
        check("Approach 2", new Approach2().fizzBuzz(15), "[1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz]");
        check("Approach 3", new Approach3().fizzBuzz(3), "[1, 2, Fizz]");
        check("Approach 3", new Approach3().fizzBuzz(15), "[1, 2, Fizz, 4, Buzz, Fizz, 7, 8, Fizz, Buzz, 11, Fizz, 13, 14, FizzBuzz]");
        System.out.println("FizzBuzz: all 3 approaches passed " + passed + " checks");
    }
}
