/*
 * Maximum Absolute Sum of Any Subarray: prefix-sum method.  Time O(n), Space O(1).
 *
 * Idea: every subarray sum is a difference of two prefix sums.
 *   P[0] = 0, P[k] = nums[0] + ... + nums[k-1]
 *   sum(i..j) = P[j+1] - P[i]
 *
 * We want |sum|, and |P[b] - P[a]| = |P[a] - P[b]|, so the order of the two
 * prefixes does not matter. Any two prefixes form a valid subarray:
 *   - a positive subarray climbs from a low prefix to a high one,
 *   - a negative subarray falls from a high prefix to a low one.
 * So the answer is simply the widest gap: max(P) - min(P).
 *
 * Example: nums = [2, -5, 1, -4, 3, -2]
 *   P = 0, 2, -3, -2, -6, -3, -5   ->  hi = 2, lo = -6  ->  answer 8
 *   (the subarray between those prefixes is [-5, 1, -4], sum -8, |-8| = 8)
 *
 * hi and lo start at 0 because the empty prefix P[0] = 0 must be included;
 * without it a subarray starting at index 0 is missed (e.g. [5] would give 0).
 *
 * Note: this shortcut works only because of the absolute value. For plain
 * "maximum subarray sum" the low prefix must come BEFORE the high one.
 */
public int maxAbsoluteSum(int[] nums) {
        int sum = 0, hi = 0, lo = 0;
        for (int x : nums) 
        {
             sum += x;               // sum = next prefix P[k]
             hi = Math.max(hi, sum); // highest prefix seen
             lo = Math.min(lo, sum); // lowest prefix seen
        }
        return hi - lo;
    }
