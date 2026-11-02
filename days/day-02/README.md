# Day 2 - Arrays & Strings: Two Pointers, Sliding Window, Prefix Sums, Matrices, Cyclic Sort

**Goal:** turn O(n^2) "check every subarray / every pair" solutions into O(n) by recognising five patterns: two pointers, sliding window, prefix sums, Kadane, and cyclic sort, plus in-place matrix tricks.

| File | What it shows |
|---|---|
| `SlidingWindowDemo.java` | Fixed window (max sum of k) and variable window (longest unique substring), printed step by step |
| `PrefixSumDemo.java` | Range sums in O(1), "count subarrays with sum k" traced with its HashMap, difference array |
| `TwoPointersDemo.java` | Container With Most Water pointer moves, Kadane trace, rotate-image in place |
| `solutions/*.java` | Every approach for all 14 problems, each file runs its own tests (`javac X.java && java X`) |

---

## 1. Arrays and Strings in Java

| Fact | Why it matters |
|---|---|
| `int[]` is a contiguous block: `a[i]` is O(1) | Index arithmetic is free; inserting in the middle is O(n) |
| `String` is immutable; `charAt(i)` is O(1) | Build results with `StringBuilder`; `s.substring()` copies (O(k)) |
| `int[2][3]` is an array of 3-element arrays | Rows can be swapped by reference; `matrix[i] = copy[i]` |
| Characters are numbers: `c - 'a'` is 0..25 | `int[26]` or `int[128]` counts are faster than `HashMap<Character,Integer>` |

---

## 2. Two pointers

**Signal:** sorted array, pairs/triplets with a target sum, or "in place" rearranging.

| Variant | Setup | Moves | Example |
|---|---|---|---|
| Opposite ends | `l = 0, r = n-1` | move the side that cannot be part of a better answer | Two Sum II, Container With Most Water, 3Sum |
| Same direction (read/write) | `write = 0`, scan with `read` | copy good elements to `write++` | Move Zeroes, Remove Duplicates |
| Three-way partition | `low, mid, high` | swap 0s left, 2s right | Sort Colors (Day 5) |

**Why it is correct (Container With Most Water):** area = width x shorter line. If `h[l] < h[r]`, every container using `l` with any `r' < r` is narrower and still capped by `h[l]`, so `l` can never do better: discard it. Demo output: 8 pointer moves instead of 36 pairs.

**3Sum recipe:** sort, fix `i`, two pointers on `i+1..n-1` for target `-nums[i]`, skip equal values for `i`, `l` and `r` to avoid duplicate triplets. O(n^2), no Set needed.

---

## 3. Sliding window

**Signal:** the answer is a **contiguous** subarray/substring ("longest", "shortest", "at most k", "contains all of").

```
for r in 0..n-1:
    add a[r] to the window state
    while window is invalid:
        remove a[l] from the state; l++
    update answer (window [l..r] is valid)
```

| Type | When | Example |
|---|---|---|
| Fixed size k | "every k consecutive" | max sum of k (demo), Sliding Window Maximum (Day 7) |
| Variable, longest valid | grow, shrink when it breaks | Longest Substring Without Repeating Characters |
| Variable, shortest valid | shrink while it is still valid | Minimum Window Substring |

**Why O(n):** `l` and `r` only move forward, so each index is added once and removed once.

**Faster shrinking:** for "no repeats", store each character's last index and jump `l = last[c] + 1` directly (demo Part B).

**When it fails:** with **negative numbers**, adding an element can make a sum smaller, so "shrink when too big" is wrong. Use prefix sums instead.

**Minimum Window Substring trick:** one `need[128]` array and a `missing` counter. `need[c]-- > 0` means a needed char just arrived (`missing--`); when shrinking, `++need[c] > 0` means you just lost a needed char (`missing++`).

---

## 4. Prefix sums

`pre[i+1] = pre[i] + a[i]` (keep an extra 0 at the front). Then `sum(a[l..r]) = pre[r+1] - pre[l]` in O(1).

| Use | Trick |
|---|---|
| Many range-sum queries | build once O(n), each query O(1) |
| Count subarrays with sum k (negatives allowed) | HashMap of prefix counts, seeded with `{0: 1}`; at each step add `count[prefix - k]` |
| Product of Array Except Self | prefix **product** from the left x suffix product from the right |
| Many range **updates** | difference array: `diff[l] += v; diff[r+1] -= v;` then prefix-sum it once |

In the demo, `[1, 2, 1, -1, 2, 1]` with k = 3 has **5** subarrays, found in one pass even though there is a negative number.

---

## 5. Kadane's algorithm (maximum subarray)

At every element, either **extend** the previous best subarray ending here, or **restart** at this element:

```java
cur = Math.max(x, cur + x);
best = Math.max(best, cur);
```

Initialise with `nums[0]` (not 0) so an all-negative array returns its largest element. Best Time to Buy and Sell Stock is Kadane on daily price differences, or simply "today's price minus the minimum so far".

---

## 6. Matrix techniques

| Problem | Key idea |
|---|---|
| Spiral Matrix | four walls `top, bottom, left, right`; walk a side, move that wall in; re-check walls before the bottom row and left column |
| Rotate Image (clockwise) | transpose (`swap m[i][j], m[j][i]` for `j > i`) then reverse each row. Counter-clockwise: transpose then reverse each column |
| Set Matrix Zeroes in O(1) space | use row 0 and column 0 as flag storage; two booleans remember whether row 0 / column 0 themselves had a zero |
| Grid neighbours (Day 12) | `int[][] dirs = {{0,1},{1,0},{0,-1},{-1,0}}` |

---

## 7. Cyclic sort and index marking

**Signal:** values lie in `1..n` (or `0..n`) and you want what is **missing** or **duplicated**, in O(1) extra space.

- **Cyclic sort:** swap value `v` to index `v-1` until each slot holds its own number or a duplicate. Then any index `i` not holding `i+1` reveals the answer. Each swap places one number for good, so it is O(n).
- **Index marking:** treat value `v` as a pointer to index `v-1` and mark it by making it negative. Seeing it already negative means a duplicate.
- **Math:** Missing Number = `n(n+1)/2 - sum` (use `long`) or XOR of all indices and values.

First Missing Positive: the answer is always in `1..n+1`, so values outside that range can be ignored, which is what makes O(n) time and O(1) space possible.

---

## 8. Problems and every approach

All approaches are in `solutions/` and on the website (Questions tab).

| Problem | Approaches (time / space) | Best |
|---|---|---|
| [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | brute O(n^2)/O(1) · Kadane on differences O(n)/O(1) · min so far O(n)/O(1) | min so far |
| [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | brute O(n^2)/O(1) · two pointers O(n)/O(1) | two pointers |
| [3Sum](https://leetcode.com/problems/3sum/) | brute + set O(n^3) · fix one + HashSet O(n^2)/O(n) · sort + two pointers O(n^2)/O(log n) | sort + two pointers |
| [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | brute O(n^2) · window + set O(n) · window + last index O(n)/O(1) | last index |
| [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | brute O(n^2) · divide & conquer O(n log n) · prefix min O(n) · Kadane O(n)/O(1) | Kadane |
| [Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) | brute O(n^2) · prefix + suffix arrays O(n)/O(n) · in output O(n)/O(1) | in output |
| [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | brute O(n^2) · sliding window O(n + m)/O(1) | sliding window |
| [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | brute O(n^2) · max arrays O(n)/O(n) · monotonic stack O(n)/O(n) · two pointers O(n)/O(1) | two pointers |
| [Spiral Matrix](https://leetcode.com/problems/spiral-matrix/) | visited matrix O(mn)/O(mn) · boundaries O(mn)/O(1) | boundaries |
| [Rotate Image](https://leetcode.com/problems/rotate-image/) | copy O(n^2)/O(n^2) · four-way swap O(1) · transpose + reverse O(1) | transpose + reverse |
| [Set Matrix Zeroes](https://leetcode.com/problems/set-matrix-zeroes/) | copy O(mn)/O(mn) · flag arrays O(m + n) · first row/col O(1) | first row/col |
| [Missing Number](https://leetcode.com/problems/missing-number/) | sort · HashSet · cyclic sort · Gauss sum · XOR (O(n)/O(1)) | XOR |
| [Find All Duplicates in an Array](https://leetcode.com/problems/find-all-duplicates-in-an-array/) | sort · HashSet · cyclic sort · negation marking O(n)/O(1) | negation |
| [First Missing Positive](https://leetcode.com/problems/first-missing-positive/) | sort · HashSet · negation marking · cyclic sort O(n)/O(1) | cyclic sort |

### Trapping Rain Water: why two pointers works
Water above bar i is `min(maxLeft, maxRight) - h[i]`. If `h[l] < h[r]`, then the right side already has a bar at least as tall as `h[l]`, so `maxRight >= leftMax` is guaranteed for position l: its water is exactly `leftMax - h[l]`. Settle it and move `l`. Symmetric for the right.

---

## 9. How to approach questions today

1. **Contiguous?** -> sliding window (all non-negative) or prefix sums (negatives allowed).
2. **Sorted, or pairs/triplets?** -> two pointers (sort first if indices are not needed).
3. **Max/min subarray sum?** -> Kadane.
4. **Values in 1..n, missing or duplicate?** -> cyclic sort or index marking.
5. **Matrix in place?** -> boundaries, transpose + reverse, or use row 0 / col 0 as storage.
6. Say the O(n^2) brute force first, then remove the inner loop with one of the above.

## Sticky notes

- Sorted array + pair/triplet target = two pointers
- 'Longest/shortest substring with condition' = variable sliding window
- Subarray sum = k (negatives allowed): prefix sum + HashMap<sum, count>, seed {0: 1}
- Kadane: cur = max(x, cur + x); best = max(best, cur); start from nums[0]
- Numbers in 1..n => cyclic sort: put x at index x-1, then scan
- Rotate clockwise = transpose + reverse each row

## Practice

- **2-hour track:** Best Time to Buy and Sell Stock, Container With Most Water, 3Sum, Longest Substring Without Repeating Characters, Maximum Subarray.
- **5-hour track:** all 14. Re-solve Trapping Rain Water and Minimum Window Substring tomorrow without notes.
- Extra (from the Patterns tab): Move Zeroes, Permutation in String, Longest Repeating Character Replacement, Find All Anagrams in a String.
