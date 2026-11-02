import java.util.*;

/**
 * Day 2 - Live demo 2: prefix sums, the "subarray sum = k" trick, and the difference array.
 * Run:  javac PrefixSumDemo.java && java PrefixSumDemo
 */
public class PrefixSumDemo {

    public static void main(String[] args) {
        rangeQueries();
        subarraySumK(new int[]{1, 2, 1, -1, 2, 1}, 3);
        differenceArray();
    }

    // 1) Build once in O(n), answer any range sum in O(1)
    static void rangeQueries() {
        int[] a = {3, 1, 4, 1, 5, 9, 2};
        int[] pre = new int[a.length + 1];                     // pre[i] = sum of a[0..i-1]
        for (int i = 0; i < a.length; i++) pre[i + 1] = pre[i] + a[i];
        System.out.println("1) a   = " + Arrays.toString(a));
        System.out.println("   pre = " + Arrays.toString(pre) + "   (one extra 0 at the front)");
        int l = 2, r = 5;
        System.out.println("   sum(a[" + l + ".." + r + "]) = pre[" + (r + 1) + "] - pre[" + l + "] = " + pre[r + 1] + " - " + pre[l] + " = " + (pre[r + 1] - pre[l]) + "\n");
    }

    // 2) Count subarrays with sum k: works with negatives (sliding window does not)
    static void subarraySumK(int[] a, int k) {
        System.out.println("2) count subarrays of " + Arrays.toString(a) + " with sum " + k);
        Map<Integer, Integer> seen = new HashMap<>();
        seen.put(0, 1);                                        // empty prefix
        int prefix = 0, count = 0;
        for (int i = 0; i < a.length; i++) {
            prefix += a[i];
            int found = seen.getOrDefault(prefix - k, 0);
            count += found;
            System.out.printf("   i=%d x=%2d prefix=%d  look for prefix-k=%d -> found %d  count=%d  map=%s%n",
                    i, a[i], prefix, prefix - k, found, count, seen);
            seen.merge(prefix, 1, Integer::sum);
        }
        System.out.println("   Answer: " + count + " (each match means sum(j+1..i) = prefix_i - prefix_j = k)\n");
    }

    // 3) Many range updates, one read at the end: difference array makes each update O(1)
    static void differenceArray() {
        int n = 8;
        int[][] updates = {{1, 4, 10}, {3, 6, 5}, {0, 7, 1}};  // add val to every index in [l..r]
        int[] diff = new int[n + 1];
        for (int[] u : updates) {
            diff[u[0]] += u[2];
            diff[u[1] + 1] -= u[2];
        }
        int[] result = new int[n];
        int run = 0;
        for (int i = 0; i < n; i++) { run += diff[i]; result[i] = run; }
        System.out.println("3) updates [l, r, +val] = " + Arrays.deepToString(updates));
        System.out.println("   diff   = " + Arrays.toString(diff));
        System.out.println("   result = " + Arrays.toString(result) + "   (prefix sum of diff)");
        System.out.println("   Each update O(1) instead of O(r - l + 1).");
    }
}
