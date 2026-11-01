import java.util.*;

/**
 * Day 1 - Demo 3: core Java facts that interviewers test and that cause silent DSA bugs.
 * Run:  javac CoreJavaGotchas.java && java CoreJavaGotchas
 */
public class CoreJavaGotchas {

    record Person(String name, int age) {}                   // Java 16+ record: immutable data class

    public static void main(String[] args) {
        integerCache();
        stringPool();
        passByValue();
        autoboxingCost();
        comparableVsComparator();
        recursionDepth();
    }

    // 1) Integer cache: == compares REFERENCES for objects
    static void integerCache() {
        Integer a = 127, b = 127, c = 128, d = 128;
        System.out.println("1) Integer cache");
        System.out.println("   127 == 127 -> " + (a == b) + "   (cached object, same reference)");
        System.out.println("   128 == 128 -> " + (c == d) + "  (two different objects!)");
        System.out.println("   128 equals -> " + c.equals(d) + "   <- always use equals() for wrappers\n");
    }

    // 2) String pool and immutability
    static void stringPool() {
        String s1 = "java", s2 = "java", s3 = new String("java");
        System.out.println("2) String pool");
        System.out.println("   literal == literal   -> " + (s1 == s2));
        System.out.println("   literal == new String -> " + (s1 == s3));
        System.out.println("   s1.equals(s3)         -> " + s1.equals(s3));
        long t = System.nanoTime();
        String slow = ""; for (int i = 0; i < 20_000; i++) slow += "x";          // O(n^2): copies every time
        long t2 = System.nanoTime();
        StringBuilder sb = new StringBuilder(); for (int i = 0; i < 20_000; i++) sb.append('x'); // amortised O(n)
        long t3 = System.nanoTime();
        System.out.printf("   20,000 appends: String += %.1f ms vs StringBuilder %.2f ms%n%n", (t2 - t) / 1e6, (t3 - t2) / 1e6);
        if (slow.length() != sb.length()) throw new AssertionError();
    }

    // 3) Java is ALWAYS pass-by-value (the value of a reference is copied)
    static void passByValue() {
        int[] arr = {1, 2, 3};
        mutate(arr);
        System.out.println("3) Pass by value");
        System.out.println("   after mutate(arr): " + Arrays.toString(arr) + "  <- contents changed (same object)");
        reassign(arr);
        System.out.println("   after reassign(arr): " + Arrays.toString(arr) + "  <- caller's reference unchanged\n");
    }
    static void mutate(int[] a) { a[0] = 99; }
    static void reassign(int[] a) { a = new int[]{7, 7, 7}; }

    // 4) Autoboxing cost: int[] vs List<Integer>
    static void autoboxingCost() {
        int n = 5_000_000;
        long t = System.nanoTime();
        int[] prim = new int[n]; long s1 = 0; for (int i = 0; i < n; i++) { prim[i] = i; s1 += prim[i]; }
        long t2 = System.nanoTime();
        List<Integer> boxed = new ArrayList<>(n); long s2 = 0; for (int i = 0; i < n; i++) { boxed.add(i); s2 += boxed.get(i); }
        long t3 = System.nanoTime();
        System.out.println("4) Autoboxing");
        System.out.printf("   5M ints: int[] %.1f ms vs List<Integer> %.1f ms (sums equal: %b)%n", (t2 - t) / 1e6, (t3 - t2) / 1e6, s1 == s2);
        System.out.println("   Each Integer is a ~16-byte object on the heap; an int is 4 bytes inline.\n");
    }

    // 5) Comparable (natural order, inside the class) vs Comparator (any order, outside)
    static void comparableVsComparator() {
        List<Person> people = new ArrayList<>(List.of(
                new Person("Ravi", 30), new Person("Anu", 25), new Person("Zoya", 25), new Person("Kiran", 35)));
        people.sort(Comparator.comparingInt(Person::age).thenComparing(Person::name));
        System.out.println("5) Comparator: by age, then name");
        System.out.println("   " + people);
        int[][] intervals = {{5, 6}, {1, 3}, {2, 4}};
        Arrays.sort(intervals, (x, y) -> Integer.compare(x[0], y[0]));   // never x[0] - y[0] (overflow)
        System.out.println("   intervals sorted by start: " + Arrays.deepToString(intervals) + "\n");
    }

    // 6) Recursion uses the call stack (stack memory), objects live on the heap
    static int depth = 0;
    static void recurse() { depth++; recurse(); }
    static void recursionDepth() {
        try { recurse(); } catch (StackOverflowError e) {
            System.out.println("6) Stack vs heap");
            System.out.println("   StackOverflowError after about " + depth + " nested calls (default stack size).");
            System.out.println("   For 10^5+ depth (long linked lists, skewed trees) prefer iteration.");
        }
    }
}
