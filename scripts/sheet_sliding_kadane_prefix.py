"""Approaches for the Sliding Window, Kadane and Prefix Sum questions from the Padho with Pratyush practice sheet (Java only)."""

SOL = {

# ------------------------------------------------------------------ Sliding window
"gfg-max-sum-subarray-of-size-k": [
 dict(name="Brute force: sum every window",
      idea="For each start, add the next k numbers.",
      time="O(n x k)", space="O(1)",
      code="""public long maximumSumSubarray(int[] arr, int k) {
    long best = Long.MIN_VALUE;
    for (int i = 0; i + k <= arr.length; i++) {
        long s = 0;
        for (int j = i; j < i + k; j++) s += arr[j];
        best = Math.max(best, s);
    }
    return best;
}"""),
 dict(name="Prefix sums",
      idea="Window sum = pre[i + k] - pre[i], each in O(1) after an O(n) build.",
      time="O(n)", space="O(n)",
      code="""public long maximumSumSubarray(int[] arr, int k) {
    long[] pre = new long[arr.length + 1];
    for (int i = 0; i < arr.length; i++) pre[i + 1] = pre[i] + arr[i];
    long best = Long.MIN_VALUE;
    for (int i = 0; i + k <= arr.length; i++) best = Math.max(best, pre[i + k] - pre[i]);
    return best;
}"""),
 dict(name="Fixed sliding window (optimal)",
      idea="Add the element entering on the right and subtract the one leaving on the left.",
      time="O(n)", space="O(1)", best=True,
      code="""public long maximumSumSubarray(int[] arr, int k) {
    long sum = 0, best;
    for (int i = 0; i < k; i++) sum += arr[i];
    best = sum;
    for (int r = k; r < arr.length; r++) {
        sum += arr[r] - arr[r - k];
        best = Math.max(best, sum);
    }
    return best;
}"""),
],

"minimum-size-subarray-sum": [
 dict(name="Brute force: grow from every start",
      idea="From each start, extend until the sum reaches the target; stop early because numbers are positive.",
      time="O(n^2)", space="O(1)",
      code="""public int minSubArrayLen(int target, int[] nums) {
    int best = Integer.MAX_VALUE;
    for (int i = 0; i < nums.length; i++) {
        int s = 0;
        for (int j = i; j < nums.length; j++) {
            s += nums[j];
            if (s >= target) { best = Math.min(best, j - i + 1); break; }
        }
    }
    return best == Integer.MAX_VALUE ? 0 : best;
}"""),
 dict(name="Prefix sums + binary search",
      idea="Prefix sums are increasing (positive numbers). For each start i, binary search the first end j with pre[j] >= pre[i] + target.",
      time="O(n log n)", space="O(n)",
      code="""public int minSubArrayLen(int target, int[] nums) {
    int n = nums.length, best = Integer.MAX_VALUE;
    long[] pre = new long[n + 1];
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
    for (int i = 0; i < n; i++) {
        long need = pre[i] + target;
        int lo = i + 1, hi = n + 1;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (pre[mid] >= need) hi = mid; else lo = mid + 1;
        }
        if (lo <= n) best = Math.min(best, lo - i);
    }
    return best == Integer.MAX_VALUE ? 0 : best;
}"""),
 dict(name="Variable sliding window (optimal)",
      idea="Grow right; while the sum is at least the target, record the length and shrink from the left.",
      time="O(n)", space="O(1)", best=True,
      code="""public int minSubArrayLen(int target, int[] nums) {
    int l = 0, sum = 0, best = Integer.MAX_VALUE;
    for (int r = 0; r < nums.length; r++) {
        sum += nums[r];
        while (sum >= target) {
            best = Math.min(best, r - l + 1);
            sum -= nums[l++];
        }
    }
    return best == Integer.MAX_VALUE ? 0 : best;
}"""),
],

"gfg-longest-k-unique-characters-substring": [
 dict(name="Brute force: grow from every start",
      idea="From each start count distinct characters; record the length whenever exactly k are distinct and stop once there are more than k. Return -1 if no substring has exactly k.",
      time="O(n^2)", space="O(1) (128-slot array)",
      code="""public int longestkSubstr(String s, int k) {
    int best = -1;
    for (int i = 0; i < s.length(); i++) {
        int[] c = new int[128];
        int distinct = 0;
        for (int j = i; j < s.length(); j++) {
            if (c[s.charAt(j)]++ == 0) distinct++;
            if (distinct == k) best = Math.max(best, j - i + 1);
            else if (distinct > k) break;
        }
    }
    return best;
}"""),
 dict(name="Variable sliding window with counts (optimal)",
      idea="Grow right, shrink left while there are more than k distinct characters; whenever exactly k are distinct, record the window.",
      time="O(n)", space="O(1) (128-slot array)", best=True,
      code="""public int longestkSubstr(String s, int k) {
    int[] c = new int[128];
    int l = 0, distinct = 0, best = -1;
    for (int r = 0; r < s.length(); r++) {
        if (c[s.charAt(r)]++ == 0) distinct++;
        while (distinct > k) {
            if (--c[s.charAt(l++)] == 0) distinct--;
        }
        if (distinct == k) best = Math.max(best, r - l + 1);
    }
    return best;
}"""),
],

"fruit-into-baskets": [
 dict(name="Brute force: grow from every start",
      idea="From each tree, extend while at most two fruit types are in the baskets.",
      time="O(n^2)", space="O(1)",
      code="""public int totalFruit(int[] fruits) {
    int best = 0;
    for (int i = 0; i < fruits.length; i++) {
        Set<Integer> types = new HashSet<>();
        int j = i;
        while (j < fruits.length) {
            types.add(fruits[j]);
            if (types.size() > 2) break;
            j++;
        }
        best = Math.max(best, j - i);
    }
    return best;
}"""),
 dict(name="Sliding window with a HashMap of counts",
      idea="This is 'longest subarray with at most 2 distinct values': shrink from the left while the map has more than two keys.",
      time="O(n)", space="O(1) (at most 3 keys)",
      code="""public int totalFruit(int[] fruits) {
    Map<Integer, Integer> count = new HashMap<>();
    int l = 0, best = 0;
    for (int r = 0; r < fruits.length; r++) {
        count.merge(fruits[r], 1, Integer::sum);
        while (count.size() > 2) {
            int f = fruits[l++];
            if (count.merge(f, -1, Integer::sum) == 0) count.remove(f);
        }
        best = Math.max(best, r - l + 1);
    }
    return best;
}"""),
 dict(name="Track the last two types and the last run (optimal, no map)",
      idea="Keep the last fruit type, the one before it, and how long the latest run of the last type is. A new third type resets the window to that run + 1.",
      time="O(n)", space="O(1)", best=True,
      code="""public int totalFruit(int[] fruits) {
    int last = -1, secondLast = -1, lastRun = 0, cur = 0, best = 0;
    for (int f : fruits) {
        cur = (f == last || f == secondLast) ? cur + 1 : lastRun + 1;
        if (f == last) lastRun++;
        else { lastRun = 1; secondLast = last; last = f; }
        best = Math.max(best, cur);
    }
    return best;
}"""),
],

"longest-repeating-character-replacement": [
 dict(name="Brute force: every substring with counts",
      idea="A substring is fixable if length - (count of its most common letter) <= k. Check all substrings, updating counts as the end grows.",
      time="O(n^2)", space="O(1)",
      code="""public int characterReplacement(String s, int k) {
    int best = 0;
    for (int i = 0; i < s.length(); i++) {
        int[] c = new int[26];
        int maxF = 0;
        for (int j = i; j < s.length(); j++) {
            maxF = Math.max(maxF, ++c[s.charAt(j) - 'A']);
            if (j - i + 1 - maxF <= k) best = Math.max(best, j - i + 1);
        }
    }
    return best;
}"""),
 dict(name="Sliding window, recompute the max count",
      idea="Grow right; while the window needs more than k replacements (length - max count), shrink left. Find the max count by scanning the 26 letters.",
      time="O(26 n)", space="O(1)",
      code="""public int characterReplacement(String s, int k) {
    int[] c = new int[26];
    int l = 0, best = 0;
    for (int r = 0; r < s.length(); r++) {
        c[s.charAt(r) - 'A']++;
        while (r - l + 1 - max(c) > k) c[s.charAt(l++) - 'A']--;
        best = Math.max(best, r - l + 1);
    }
    return best;
}
private int max(int[] c) { int m = 0; for (int x : c) m = Math.max(m, x); return m; }"""),
 dict(name="Sliding window, max count never decreases (optimal)",
      idea="Only a larger max count can give a longer answer, so keep the highest max count seen and never lower it. The window then slides instead of shrinking.",
      time="O(n)", space="O(1)", best=True,
      code="""public int characterReplacement(String s, int k) {
    int[] c = new int[26];
    int l = 0, maxF = 0, best = 0;
    for (int r = 0; r < s.length(); r++) {
        maxF = Math.max(maxF, ++c[s.charAt(r) - 'A']);
        if (r - l + 1 - maxF > k) c[s.charAt(l++) - 'A']--;
        best = Math.max(best, r - l + 1);
    }
    return best;
}"""),
],

"max-consecutive-ones-iii": [
 dict(name="Brute force: grow from every start",
      idea="From each start, extend while the number of zeros is at most k.",
      time="O(n^2)", space="O(1)",
      code="""public int longestOnes(int[] nums, int k) {
    int best = 0;
    for (int i = 0; i < nums.length; i++) {
        int zeros = 0;
        for (int j = i; j < nums.length; j++) {
            if (nums[j] == 0 && ++zeros > k) break;
            best = Math.max(best, j - i + 1);
        }
    }
    return best;
}"""),
 dict(name="Sliding window counting zeros (optimal)",
      idea="'Longest subarray with at most k zeros'. Grow right; while there are more than k zeros, shrink left.",
      time="O(n)", space="O(1)", best=True,
      code="""public int longestOnes(int[] nums, int k) {
    int l = 0, zeros = 0, best = 0;
    for (int r = 0; r < nums.length; r++) {
        if (nums[r] == 0) zeros++;
        while (zeros > k) if (nums[l++] == 0) zeros--;
        best = Math.max(best, r - l + 1);
    }
    return best;
}"""),
],

"permutation-in-string": [
 dict(name="Sort every window and compare",
      idea="Two strings are permutations of each other if their sorted forms match. Sort s1 once and every window of s2.",
      time="O(n x m log m)", space="O(m)",
      code="""public boolean checkInclusion(String s1, String s2) {
    char[] a = s1.toCharArray();
    Arrays.sort(a);
    String key = new String(a);
    for (int i = 0; i + s1.length() <= s2.length(); i++) {
        char[] w = s2.substring(i, i + s1.length()).toCharArray();
        Arrays.sort(w);
        if (key.equals(new String(w))) return true;
    }
    return false;
}"""),
 dict(name="Fixed window of letter counts",
      idea="Keep counts for the current window of length |s1|; compare the two 26-slot arrays at each step.",
      time="O(26 n)", space="O(1)",
      code="""public boolean checkInclusion(String s1, String s2) {
    int m = s1.length();
    if (m > s2.length()) return false;
    int[] need = new int[26], win = new int[26];
    for (char c : s1.toCharArray()) need[c - 'a']++;
    for (int r = 0; r < s2.length(); r++) {
        win[s2.charAt(r) - 'a']++;
        if (r >= m) win[s2.charAt(r - m) - 'a']--;
        if (r >= m - 1 && Arrays.equals(need, win)) return true;
    }
    return false;
}"""),
 dict(name="Fixed window with a 'matching letters' counter (optimal)",
      idea="Track how many of the 26 letters currently have equal counts. Each slide changes two letters, so the counter updates in O(1); all 26 matching means a permutation.",
      time="O(n)", space="O(1)", best=True,
      code="""public boolean checkInclusion(String s1, String s2) {
    int m = s1.length(), n = s2.length();
    if (m > n) return false;
    int[] a = new int[26], b = new int[26];
    for (int i = 0; i < m; i++) { a[s1.charAt(i) - 'a']++; b[s2.charAt(i) - 'a']++; }
    int matches = 0;
    for (int i = 0; i < 26; i++) if (a[i] == b[i]) matches++;
    for (int r = m; r < n; r++) {
        if (matches == 26) return true;
        int in = s2.charAt(r) - 'a';
        b[in]++;
        if (b[in] == a[in]) matches++; else if (b[in] == a[in] + 1) matches--;
        int out = s2.charAt(r - m) - 'a';
        b[out]--;
        if (b[out] == a[out]) matches++; else if (b[out] == a[out] - 1) matches--;
    }
    return matches == 26;
}"""),
],

"find-all-anagrams-in-a-string": [
 dict(name="Sort every window and compare",
      idea="Sort p once; sort each window of s of the same length and compare.",
      time="O(n x m log m)", space="O(m)",
      code="""public List<Integer> findAnagrams(String s, String p) {
    List<Integer> res = new ArrayList<>();
    char[] a = p.toCharArray();
    Arrays.sort(a);
    String key = new String(a);
    for (int i = 0; i + p.length() <= s.length(); i++) {
        char[] w = s.substring(i, i + p.length()).toCharArray();
        Arrays.sort(w);
        if (key.equals(new String(w))) res.add(i);
    }
    return res;
}"""),
 dict(name="Fixed window of letter counts",
      idea="Slide a window of length |p| over s keeping letter counts; record the start whenever the counts equal p's counts.",
      time="O(26 n)", space="O(1)",
      code="""public List<Integer> findAnagrams(String s, String p) {
    List<Integer> res = new ArrayList<>();
    int m = p.length();
    int[] need = new int[26], win = new int[26];
    for (char c : p.toCharArray()) need[c - 'a']++;
    for (int r = 0; r < s.length(); r++) {
        win[s.charAt(r) - 'a']++;
        if (r >= m) win[s.charAt(r - m) - 'a']--;
        if (r >= m - 1 && Arrays.equals(need, win)) res.add(r - m + 1);
    }
    return res;
}"""),
 dict(name="Fixed window with a 'still needed' counter (optimal)",
      idea="One count array of what p still needs and a counter of missing letters. The window is an anagram exactly when nothing is missing.",
      time="O(n)", space="O(1)", best=True,
      code="""public List<Integer> findAnagrams(String s, String p) {
    List<Integer> res = new ArrayList<>();
    int m = p.length();
    if (m > s.length()) return res;
    int[] need = new int[26];
    for (char c : p.toCharArray()) need[c - 'a']++;
    int missing = m;
    for (int r = 0; r < s.length(); r++) {
        if (need[s.charAt(r) - 'a']-- > 0) missing--;
        if (r >= m && ++need[s.charAt(r - m) - 'a'] > 0) missing++;
        if (missing == 0) res.add(r - m + 1);
    }
    return res;
}"""),
],

"substring-with-concatenation-of-all-words": [
 dict(name="Check every start index",
      idea="All words have the same length L. From each start, read w words of length L and check them against the word counts.",
      time="O(n x w x L)", space="O(w)",
      code="""public List<Integer> findSubstring(String s, String[] words) {
    List<Integer> res = new ArrayList<>();
    int L = words[0].length(), w = words.length, n = s.length();
    Map<String, Integer> need = new HashMap<>();
    for (String x : words) need.merge(x, 1, Integer::sum);
    for (int i = 0; i + w * L <= n; i++) {
        Map<String, Integer> seen = new HashMap<>();
        int j = 0;
        for (; j < w; j++) {
            String x = s.substring(i + j * L, i + (j + 1) * L);
            if (!need.containsKey(x) || seen.merge(x, 1, Integer::sum) > need.get(x)) break;
        }
        if (j == w) res.add(i);
    }
    return res;
}"""),
 dict(name="Sliding window per offset, one word at a time (optimal)",
      idea="Run L separate sliding windows (offsets 0..L-1) that step a whole word at a time. Shrink from the left when a word appears too often; reset when an unknown word appears.",
      time="O(n x L)", space="O(w)", best=True,
      code="""public List<Integer> findSubstring(String s, String[] words) {
    List<Integer> res = new ArrayList<>();
    int L = words[0].length(), w = words.length, n = s.length();
    Map<String, Integer> need = new HashMap<>();
    for (String x : words) need.merge(x, 1, Integer::sum);
    for (int off = 0; off < L; off++) {
        Map<String, Integer> have = new HashMap<>();
        int left = off, count = 0;
        for (int r = off; r + L <= n; r += L) {
            String word = s.substring(r, r + L);
            if (!need.containsKey(word)) { have.clear(); count = 0; left = r + L; continue; }
            have.merge(word, 1, Integer::sum);
            count++;
            while (have.get(word) > need.get(word)) {
                have.merge(s.substring(left, left + L), -1, Integer::sum);
                count--;
                left += L;
            }
            if (count == w) {
                res.add(left);
                have.merge(s.substring(left, left + L), -1, Integer::sum);
                count--;
                left += L;
            }
        }
    }
    Collections.sort(res);
    return res;
}"""),
],

# ------------------------------------------------------------------ Kadane
"gfg-smallest-sum-contiguous-subarray": [
 dict(name="Brute force: every subarray",
      idea="Running sum from each start; keep the smallest.",
      time="O(n^2)", space="O(1)",
      code="""public int smallestSumSubarray(int[] a) {
    int best = Integer.MAX_VALUE;
    for (int i = 0; i < a.length; i++) {
        int s = 0;
        for (int j = i; j < a.length; j++) { s += a[j]; best = Math.min(best, s); }
    }
    return best;
}"""),
 dict(name="Negate, then maximum-subarray Kadane",
      idea="The smallest sum of a is minus the largest sum of -a.",
      time="O(n)", space="O(1)",
      code="""public int smallestSumSubarray(int[] a) {
    int cur = -a[0], best = -a[0];
    for (int i = 1; i < a.length; i++) {
        cur = Math.max(-a[i], cur - a[i]);
        best = Math.max(best, cur);
    }
    return -best;
}"""),
 dict(name="Kadane for the minimum (optimal)",
      idea="Same rule with min: either extend the smallest subarray ending at the previous index or start fresh.",
      time="O(n)", space="O(1)", best=True,
      code="""public int smallestSumSubarray(int[] a) {
    int cur = a[0], best = a[0];
    for (int i = 1; i < a.length; i++) {
        cur = Math.min(a[i], cur + a[i]);
        best = Math.min(best, cur);
    }
    return best;
}"""),
],

"maximum-product-subarray": [
 dict(name="Brute force: every subarray",
      idea="Running product from each start; keep the largest.",
      time="O(n^2)", space="O(1)",
      code="""public int maxProduct(int[] nums) {
    int best = nums[0];
    for (int i = 0; i < nums.length; i++) {
        int p = 1;
        for (int j = i; j < nums.length; j++) { p *= nums[j]; best = Math.max(best, p); }
    }
    return best;
}"""),
 dict(name="Prefix and suffix products",
      idea="The best product starts at the array start, ends at the array end, or sits between zeros. Scan running products from both ends, restarting after a zero.",
      time="O(n)", space="O(1)",
      code="""public int maxProduct(int[] nums) {
    int n = nums.length, pre = 1, suf = 1, best = Integer.MIN_VALUE;
    for (int i = 0; i < n; i++) {
        pre = (pre == 0 ? 1 : pre) * nums[i];
        suf = (suf == 0 ? 1 : suf) * nums[n - 1 - i];
        best = Math.max(best, Math.max(pre, suf));
    }
    return best;
}"""),
 dict(name="Kadane tracking max and min (optimal)",
      idea="A negative number turns the smallest product into the largest, so keep both the max and the min product ending here.",
      time="O(n)", space="O(1)", best=True,
      code="""public int maxProduct(int[] nums) {
    int hi = nums[0], lo = nums[0], best = nums[0];
    for (int i = 1; i < nums.length; i++) {
        int x = nums[i], h = hi;
        hi = Math.max(x, Math.max(h * x, lo * x));
        lo = Math.min(x, Math.min(h * x, lo * x));
        best = Math.max(best, hi);
    }
    return best;
}"""),
],

"maximum-subarray-sum-with-one-deletion": [
 dict(name="Try every deletion, run Kadane each time",
      idea="For no deletion and for each index d, run Kadane on the array without d (the result must stay non-empty).",
      time="O(n^2)", space="O(1)",
      code="""public int maximumSum(int[] arr) {
    int best = kadane(arr, -1);
    if (arr.length > 1) for (int d = 0; d < arr.length; d++) best = Math.max(best, kadane(arr, d));
    return best;
}
private int kadane(int[] a, int skip) {
    int cur = 0, best = Integer.MIN_VALUE;
    boolean started = false;
    for (int i = 0; i < a.length; i++) {
        if (i == skip) continue;
        cur = started ? Math.max(a[i], cur + a[i]) : a[i];
        started = true;
        best = Math.max(best, cur);
    }
    return best;
}"""),
 dict(name="Best ending here + best starting here",
      idea="fw[i] = best sum ending at i, bw[i] = best sum starting at i. Deleting i joins fw[i-1] and bw[i+1].",
      time="O(n)", space="O(n)",
      code="""public int maximumSum(int[] arr) {
    int n = arr.length;
    int[] fw = new int[n], bw = new int[n];
    fw[0] = arr[0];
    int best = arr[0];
    for (int i = 1; i < n; i++) { fw[i] = Math.max(arr[i], fw[i - 1] + arr[i]); best = Math.max(best, fw[i]); }
    bw[n - 1] = arr[n - 1];
    for (int i = n - 2; i >= 0; i--) bw[i] = Math.max(arr[i], bw[i + 1] + arr[i]);
    for (int i = 1; i < n - 1; i++) best = Math.max(best, fw[i - 1] + bw[i + 1]);
    return best;
}"""),
 dict(name="Two-state Kadane (optimal)",
      idea="noDel = best sum ending here with no deletion; oneDel = best ending here with one deletion used (either delete this element, or extend an earlier deletion).",
      time="O(n)", space="O(1)", best=True,
      code="""public int maximumSum(int[] arr) {
    int noDel = arr[0], oneDel = Integer.MIN_VALUE / 2, best = arr[0];
    for (int i = 1; i < arr.length; i++) {
        oneDel = Math.max(oneDel + arr[i], noDel);   // extend a deletion, or delete arr[i]
        noDel = Math.max(noDel + arr[i], arr[i]);
        best = Math.max(best, Math.max(noDel, oneDel));
    }
    return best;
}"""),
],

"maximum-absolute-sum-of-any-subarray": [
 dict(name="Brute force: every subarray",
      idea="Running sum from each start; keep the largest absolute value.",
      time="O(n^2)", space="O(1)",
      code="""public int maxAbsoluteSum(int[] nums) {
    int best = 0;
    for (int i = 0; i < nums.length; i++) {
        int s = 0;
        for (int j = i; j < nums.length; j++) { s += nums[j]; best = Math.max(best, Math.abs(s)); }
    }
    return best;
}"""),
 dict(name="Prefix sums: largest prefix minus smallest prefix",
      idea="Any subarray sum is a difference of two prefix sums, so the largest absolute sum is max prefix - min prefix (including the empty prefix 0).",
      time="O(n)", space="O(1)",
      code="""public int maxAbsoluteSum(int[] nums) {
    int pre = 0, hi = 0, lo = 0;
    for (int x : nums) {
        pre += x;
        hi = Math.max(hi, pre);
        lo = Math.min(lo, pre);
    }
    return hi - lo;
}"""),
 dict(name="Kadane for the max and for the min (optimal)",
      idea="The answer is the larger of |best max subarray| and |best min subarray|; run both Kadanes in one pass.",
      time="O(n)", space="O(1)", best=True,
      code="""public int maxAbsoluteSum(int[] nums) {
    int curMax = 0, curMin = 0, best = 0;
    for (int x : nums) {
        curMax = Math.max(x, curMax + x);
        curMin = Math.min(x, curMin + x);
        best = Math.max(best, Math.max(curMax, -curMin));
    }
    return best;
}"""),
],

"maximum-sum-circular-subarray": [
 dict(name="Brute force: every start, every length",
      idea="From each start, walk up to n elements around the circle keeping a running sum.",
      time="O(n^2)", space="O(1)",
      code="""public int maxSubarraySumCircular(int[] nums) {
    int n = nums.length, best = Integer.MIN_VALUE;
    for (int i = 0; i < n; i++) {
        int s = 0;
        for (int len = 1; len <= n; len++) { s += nums[(i + len - 1) % n]; best = Math.max(best, s); }
    }
    return best;
}"""),
 dict(name="Kadane + best prefix joined with each suffix",
      idea="A wrapping subarray is a suffix plus a prefix. Precompute the best prefix sum up to each index, then try every suffix.",
      time="O(n)", space="O(n)",
      code="""public int maxSubarraySumCircular(int[] nums) {
    int n = nums.length, cur = nums[0], best = nums[0];
    for (int i = 1; i < n; i++) { cur = Math.max(nums[i], cur + nums[i]); best = Math.max(best, cur); }
    int[] leftMax = new int[n];
    int pre = nums[0];
    leftMax[0] = nums[0];
    for (int i = 1; i < n; i++) { pre += nums[i]; leftMax[i] = Math.max(leftMax[i - 1], pre); }
    int suf = 0;
    for (int i = n - 1; i >= 1; i--) { suf += nums[i]; best = Math.max(best, suf + leftMax[i - 1]); }
    return best;
}"""),
 dict(name="Total minus minimum subarray (optimal)",
      idea="A wrapping subarray = total - (a middle subarray left out); to maximise it, leave out the minimum subarray. If every number is negative, return the normal Kadane max.",
      time="O(n)", space="O(1)", best=True,
      code="""public int maxSubarraySumCircular(int[] nums) {
    int total = 0, curMax = 0, curMin = 0, maxS = Integer.MIN_VALUE, minS = Integer.MAX_VALUE;
    for (int x : nums) {
        curMax = Math.max(x, curMax + x);
        maxS = Math.max(maxS, curMax);
        curMin = Math.min(x, curMin + x);
        minS = Math.min(minS, curMin);
        total += x;
    }
    return maxS < 0 ? maxS : Math.max(maxS, total - minS);
}"""),
],

# ------------------------------------------------------------------ Prefix sum
"subarray-sum-equals-k": [
 dict(name="Brute force: every subarray with a running sum",
      idea="From each start keep a running sum; count every time it equals k.",
      time="O(n^2)", space="O(1)",
      code="""public int subarraySum(int[] nums, int k) {
    int count = 0;
    for (int i = 0; i < nums.length; i++) {
        int s = 0;
        for (int j = i; j < nums.length; j++) { s += nums[j]; if (s == k) count++; }
    }
    return count;
}"""),
 dict(name="Prefix sum + HashMap of counts (optimal)",
      idea="sum(i+1..j) = pre[j] - pre[i] = k, so at each j add how many earlier prefixes equal pre[j] - k. Seed the map with {0: 1}. Works with negative numbers, unlike a sliding window.",
      time="O(n)", space="O(n)", best=True,
      code="""public int subarraySum(int[] nums, int k) {
    Map<Integer, Integer> seen = new HashMap<>();
    seen.put(0, 1);
    int pre = 0, count = 0;
    for (int x : nums) {
        pre += x;
        count += seen.getOrDefault(pre - k, 0);
        seen.merge(pre, 1, Integer::sum);
    }
    return count;
}"""),
],

"find-pivot-index": [
 dict(name="Brute force: sum both sides for each index",
      idea="For every index, add up the left side and the right side.",
      time="O(n^2)", space="O(1)",
      code="""public int pivotIndex(int[] nums) {
    for (int i = 0; i < nums.length; i++) {
        int left = 0, right = 0;
        for (int j = 0; j < i; j++) left += nums[j];
        for (int j = i + 1; j < nums.length; j++) right += nums[j];
        if (left == right) return i;
    }
    return -1;
}"""),
 dict(name="Prefix sum array",
      idea="left = pre[i], right = total - pre[i + 1].",
      time="O(n)", space="O(n)",
      code="""public int pivotIndex(int[] nums) {
    int n = nums.length;
    int[] pre = new int[n + 1];
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
    for (int i = 0; i < n; i++) if (pre[i] == pre[n] - pre[i + 1]) return i;
    return -1;
}"""),
 dict(name="Total sum + running left sum (optimal)",
      idea="right = total - left - nums[i], so one running variable is enough.",
      time="O(n)", space="O(1)", best=True,
      code="""public int pivotIndex(int[] nums) {
    int total = 0, left = 0;
    for (int x : nums) total += x;
    for (int i = 0; i < nums.length; i++) {
        if (left == total - left - nums[i]) return i;
        left += nums[i];
    }
    return -1;
}"""),
],

"subarray-sums-divisible-by-k": [
 dict(name="Brute force: every subarray",
      idea="Running sum from each start; count sums divisible by k.",
      time="O(n^2)", space="O(1)",
      code="""public int subarraysDivByK(int[] nums, int k) {
    int count = 0;
    for (int i = 0; i < nums.length; i++) {
        int s = 0;
        for (int j = i; j < nums.length; j++) { s += nums[j]; if (s % k == 0) count++; }
    }
    return count;
}"""),
 dict(name="Prefix remainders + counts (optimal)",
      idea="sum(i+1..j) is divisible by k exactly when pre[i] and pre[j] have the same remainder. Count remainders; fix negatives with ((x % k) + k) % k.",
      time="O(n)", space="O(k)", best=True,
      code="""public int subarraysDivByK(int[] nums, int k) {
    int[] count = new int[k];
    count[0] = 1;
    int pre = 0, res = 0;
    for (int x : nums) {
        pre = ((pre + x) % k + k) % k;
        res += count[pre]++;
    }
    return res;
}"""),
],

"contiguous-array": [
 dict(name="Brute force: every subarray",
      idea="Count zeros and ones from each start; record lengths where they are equal.",
      time="O(n^2)", space="O(1)",
      code="""public int findMaxLength(int[] nums) {
    int best = 0;
    for (int i = 0; i < nums.length; i++) {
        int bal = 0;
        for (int j = i; j < nums.length; j++) {
            bal += nums[j] == 1 ? 1 : -1;
            if (bal == 0) best = Math.max(best, j - i + 1);
        }
    }
    return best;
}"""),
 dict(name="Prefix balance + first-seen HashMap (optimal)",
      idea="Treat 0 as -1. Equal zeros and ones means the balance returns to an earlier value; the longest such subarray uses the first index where that balance appeared.",
      time="O(n)", space="O(n)", best=True,
      code="""public int findMaxLength(int[] nums) {
    Map<Integer, Integer> first = new HashMap<>();
    first.put(0, -1);
    int bal = 0, best = 0;
    for (int i = 0; i < nums.length; i++) {
        bal += nums[i] == 1 ? 1 : -1;
        Integer j = first.putIfAbsent(bal, i);
        if (j != null) best = Math.max(best, i - j);
    }
    return best;
}"""),
 dict(name="Prefix balance + array instead of a map",
      idea="The balance is always in [-n, n], so an array of size 2n + 1 replaces the HashMap (faster in practice).",
      time="O(n)", space="O(n)",
      code="""public int findMaxLength(int[] nums) {
    int n = nums.length, bal = 0, best = 0;
    int[] first = new int[2 * n + 1];
    Arrays.fill(first, -2);
    first[n] = -1;
    for (int i = 0; i < n; i++) {
        bal += nums[i] == 1 ? 1 : -1;
        if (first[bal + n] == -2) first[bal + n] = i;
        else best = Math.max(best, i - first[bal + n]);
    }
    return best;
}"""),
],

"shortest-subarray-with-sum-at-least-k": [
 dict(name="Brute force: every subarray",
      idea="Running sum from each start; record the shortest subarray reaching k. Negative numbers mean we cannot stop early.",
      time="O(n^2)", space="O(1)",
      code="""public int shortestSubarray(int[] nums, int k) {
    int best = Integer.MAX_VALUE;
    for (int i = 0; i < nums.length; i++) {
        long s = 0;
        for (int j = i; j < nums.length && j - i + 1 < best; j++) {
            s += nums[j];
            if (s >= k) best = j - i + 1;
        }
    }
    return best == Integer.MAX_VALUE ? -1 : best;
}"""),
 dict(name="Prefix sums + monotonic deque (optimal)",
      idea="Keep prefix indices with increasing prefix sums in a deque. From the front, pop while pre[i] - pre[front] >= k (record lengths). From the back, pop larger prefixes: a smaller, later prefix is always a better start.",
      time="O(n)", space="O(n)", best=True,
      code="""public int shortestSubarray(int[] nums, int k) {
    int n = nums.length, best = n + 1;
    long[] pre = new long[n + 1];
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
    Deque<Integer> dq = new ArrayDeque<>();
    for (int i = 0; i <= n; i++) {
        while (!dq.isEmpty() && pre[i] - pre[dq.peekFirst()] >= k) best = Math.min(best, i - dq.pollFirst());
        while (!dq.isEmpty() && pre[i] <= pre[dq.peekLast()]) dq.pollLast();
        dq.addLast(i);
    }
    return best <= n ? best : -1;
}"""),
],

"count-of-range-sum": [
 dict(name="Brute force: every subarray with a running sum",
      idea="Count subarray sums inside [lower, upper]. Use long to avoid overflow.",
      time="O(n^2)", space="O(1)",
      code="""public int countRangeSum(int[] nums, int lower, int upper) {
    int count = 0;
    for (int i = 0; i < nums.length; i++) {
        long s = 0;
        for (int j = i; j < nums.length; j++) {
            s += nums[j];
            if (s >= lower && s <= upper) count++;
        }
    }
    return count;
}"""),
 dict(name="Merge sort on prefix sums (optimal)",
      idea="Count pairs i < j with lower <= pre[j] - pre[i] <= upper. During merge sort both halves are sorted, so for each i in the left half two moving pointers find the valid j range in the right half.",
      time="O(n log n)", space="O(n)", best=True,
      code="""public int countRangeSum(int[] nums, int lower, int upper) {
    long[] pre = new long[nums.length + 1];
    for (int i = 0; i < nums.length; i++) pre[i + 1] = pre[i] + nums[i];
    return sort(pre, 0, pre.length, lower, upper);
}
private int sort(long[] p, int lo, int hi, int lower, int upper) {
    if (hi - lo <= 1) return 0;
    int mid = (lo + hi) >>> 1;
    int count = sort(p, lo, mid, lower, upper) + sort(p, mid, hi, lower, upper);
    int a = mid, b = mid;
    for (int i = lo; i < mid; i++) {
        while (a < hi && p[a] - p[i] < lower) a++;
        while (b < hi && p[b] - p[i] <= upper) b++;
        count += b - a;
    }
    long[] t = new long[hi - lo];
    int x = lo, y = mid, k = 0;
    while (x < mid && y < hi) t[k++] = p[x] <= p[y] ? p[x++] : p[y++];
    while (x < mid) t[k++] = p[x++];
    while (y < hi) t[k++] = p[y++];
    System.arraycopy(t, 0, p, lo, t.length);
    return count;
}"""),
],
}

TESTS = {
 "gfg-max-sum-subarray-of-size-k": [("new int[]{100,200,300,400}, 2", "700"), ("new int[]{1,4,2,10,23,3,1,0,20}, 4", "39"), ("new int[]{-3,-1,-2}, 1", "-1")],
 "minimum-size-subarray-sum": [("7, new int[]{2,3,1,2,4,3}", "2"), ("4, new int[]{1,4,4}", "1"), ("11, new int[]{1,1,1,1,1,1,1,1}", "0")],
 "gfg-longest-k-unique-characters-substring": [('"aabacbebebe", 3', "7"), ('"aaaa", 2', "-1"), ('"aabaaab", 2', "7")],
 "fruit-into-baskets": [("new int[]{1,2,1}", "3"), ("new int[]{0,1,2,2}", "3"), ("new int[]{1,2,3,2,2}", "4"), ("new int[]{3,3,3,1,2,1,1,2,3,3,4}", "5")],
 "longest-repeating-character-replacement": [('"ABAB", 2', "4"), ('"AABABBA", 1', "4"), ('"A", 0', "1"), ('"ABBB", 0', "3")],
 "max-consecutive-ones-iii": [("new int[]{1,1,1,0,0,0,1,1,1,1,0}, 2", "6"), ("new int[]{0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1}, 3", "10"),
                              ("new int[]{0,0,0}, 0", "0")],
 "permutation-in-string": [('"ab", "eidbaooo"', "true"), ('"ab", "eidboaoo"', "false"), ('"adc", "dcda"', "true"), ('"abc", "ab"', "false")],
 "find-all-anagrams-in-a-string": [('"cbaebabacd", "abc"', "[0, 6]"), ('"abab", "ab"', "[0, 1, 2]"), ('"a", "ab"', "[]")],
 "substring-with-concatenation-of-all-words": [('"barfoothefoobarman", new String[]{"foo","bar"}', "[0, 9]"),
                                               ('"wordgoodgoodgoodbestword", new String[]{"word","good","best","word"}', "[]"),
                                               ('"barfoofoobarthefoobarman", new String[]{"bar","foo","the"}', "[6, 9, 12]"),
                                               ('"aaaaaa", new String[]{"aa","aa"}', "[0, 1, 2]")],
 "gfg-smallest-sum-contiguous-subarray": [("new int[]{3,-4,2,-3,-1,7,-5}", "-6"), ("new int[]{2,6,8,1,4}", "1")],
 "maximum-product-subarray": [("new int[]{2,3,-2,4}", "6"), ("new int[]{-2,0,-1}", "0"), ("new int[]{-2,3,-4}", "24"), ("new int[]{-2}", "-2")],
 "maximum-subarray-sum-with-one-deletion": [("new int[]{1,-2,0,3}", "4"), ("new int[]{1,-2,-2,3}", "3"), ("new int[]{-1,-1,-1,-1}", "-1"), ("new int[]{5}", "5")],
 "maximum-absolute-sum-of-any-subarray": [("new int[]{1,-3,2,3,-4}", "5"), ("new int[]{2,-5,1,-4,3,-2}", "8")],
 "maximum-sum-circular-subarray": [("new int[]{1,-2,3,-2}", "3"), ("new int[]{5,-3,5}", "10"), ("new int[]{-3,-2,-3}", "-2")],
 "subarray-sum-equals-k": [("new int[]{1,1,1}, 2", "2"), ("new int[]{1,2,3}, 3", "2"), ("new int[]{1,-1,0}, 0", "3")],
 "find-pivot-index": [("new int[]{1,7,3,6,5,6}", "3"), ("new int[]{1,2,3}", "-1"), ("new int[]{2,1,-1}", "0")],
 "subarray-sums-divisible-by-k": [("new int[]{4,5,0,-2,-3,1}, 5", "7"), ("new int[]{5}, 9", "0"), ("new int[]{-1,2,9}, 2", "2")],
 "contiguous-array": [("new int[]{0,1}", "2"), ("new int[]{0,1,0}", "2"), ("new int[]{0,1,1,1,1,1,0,0,0}", "6")],
 "shortest-subarray-with-sum-at-least-k": [("new int[]{1}, 1", "1"), ("new int[]{1,2}, 4", "-1"), ("new int[]{2,-1,2}, 3", "3"),
                                           ("new int[]{84,-37,32,40,95}, 167", "3")],
 "count-of-range-sum": [("new int[]{-2,5,-1}, -2, 2", "3"), ("new int[]{0}, 0, 0", "1"),
                        ("new int[]{-2147483647,0,-2147483647,2147483647}, -564, 3864", "3")],
}
