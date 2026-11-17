"""Approaches for the Hash Maps and Binary Search questions from the Padho with Pratyush practice sheet (Java only)."""

SOL = {

# ------------------------------------------------------------------ Hash maps
"first-unique-character-in-a-string": [
 dict(name="Brute force: compare with every other character",
      idea="For each index, scan the whole string for another copy of the same character.",
      time="O(n^2)", space="O(1)",
      code="""public int firstUniqChar(String s) {
    for (int i = 0; i < s.length(); i++) {
        boolean unique = true;
        for (int j = 0; j < s.length() && unique; j++)
            if (i != j && s.charAt(i) == s.charAt(j)) unique = false;
        if (unique) return i;
    }
    return -1;
}"""),
 dict(name="HashMap of counts, two passes",
      idea="Count every character, then return the first index whose count is 1.",
      time="O(n)", space="O(k) distinct characters",
      code="""public int firstUniqChar(String s) {
    Map<Character, Integer> count = new HashMap<>();
    for (char c : s.toCharArray()) count.merge(c, 1, Integer::sum);
    for (int i = 0; i < s.length(); i++) if (count.get(s.charAt(i)) == 1) return i;
    return -1;
}"""),
 dict(name="int[26] counts, two passes (optimal)",
      idea="Same idea with an array indexed by c - 'a', which is faster than a map for lowercase letters.",
      time="O(n)", space="O(1)", best=True,
      code="""public int firstUniqChar(String s) {
    int[] count = new int[26];
    for (char c : s.toCharArray()) count[c - 'a']++;
    for (int i = 0; i < s.length(); i++) if (count[s.charAt(i) - 'a'] == 1) return i;
    return -1;
}"""),
],

"maximum-number-of-balloons": [
 dict(name="Simulate: build balloons one at a time",
      idea="Count the letters, then keep spending b, a, l, l, o, o, n until one runs out.",
      time="O(n + answer)", space="O(1)",
      code="""public int maxNumberOfBalloons(String text) {
    int[] c = new int[26];
    for (char ch : text.toCharArray()) c[ch - 'a']++;
    int made = 0;
    while (true) {
        for (char ch : "balloon".toCharArray()) {
            if (c[ch - 'a'] == 0) return made;
            c[ch - 'a']--;
        }
        made++;
    }
}"""),
 dict(name="HashMap of counts",
      idea="Each balloon needs b, a, n once and l, o twice: the answer is the smallest of count / need over those letters.",
      time="O(n)", space="O(1)",
      code="""public int maxNumberOfBalloons(String text) {
    Map<Character, Integer> have = new HashMap<>(), need = new HashMap<>();
    for (char ch : text.toCharArray()) have.merge(ch, 1, Integer::sum);
    for (char ch : "balloon".toCharArray()) need.merge(ch, 1, Integer::sum);
    int best = Integer.MAX_VALUE;
    for (Map.Entry<Character, Integer> e : need.entrySet())
        best = Math.min(best, have.getOrDefault(e.getKey(), 0) / e.getValue());
    return best;
}"""),
 dict(name="int[26] counts (optimal)",
      idea="Same formula with an array: min(b, a, l / 2, o / 2, n).",
      time="O(n)", space="O(1)", best=True,
      code="""public int maxNumberOfBalloons(String text) {
    int[] c = new int[26];
    for (char ch : text.toCharArray()) c[ch - 'a']++;
    return Math.min(Math.min(c['b' - 'a'], c['a' - 'a']),
           Math.min(Math.min(c['l' - 'a'] / 2, c['o' - 'a'] / 2), c['n' - 'a']));
}"""),
],

"longest-palindrome": [
 dict(name="HashSet pairing",
      idea="Add a character to a set; when it appears again, remove it and count a pair. If any unpaired character is left, one can sit in the middle.",
      time="O(n)", space="O(k) distinct characters",
      code="""public int longestPalindrome(String s) {
    Set<Character> odd = new HashSet<>();
    int pairs = 0;
    for (char c : s.toCharArray()) {
        if (!odd.add(c)) { odd.remove(c); pairs++; }
    }
    return pairs * 2 + (odd.isEmpty() ? 0 : 1);
}"""),
 dict(name="HashMap of counts",
      idea="Use count / 2 * 2 of every character; add 1 if any count is odd (for the middle).",
      time="O(n)", space="O(k)",
      code="""public int longestPalindrome(String s) {
    Map<Character, Integer> count = new HashMap<>();
    for (char c : s.toCharArray()) count.merge(c, 1, Integer::sum);
    int len = 0;
    boolean odd = false;
    for (int v : count.values()) { len += v / 2 * 2; if (v % 2 == 1) odd = true; }
    return len + (odd ? 1 : 0);
}"""),
 dict(name="int[128] counts (optimal)",
      idea="Same rule with an array that covers upper and lower case letters.",
      time="O(n)", space="O(1)", best=True,
      code="""public int longestPalindrome(String s) {
    int[] count = new int[128];
    for (char c : s.toCharArray()) count[c]++;
    int len = 0;
    for (int v : count) len += v / 2 * 2;
    return len < s.length() ? len + 1 : len;
}"""),
],

"ransom-note": [
 dict(name="Remove each used letter from the magazine",
      idea="For every note letter, find and delete one copy in a StringBuilder of the magazine.",
      time="O(m x n)", space="O(n)",
      code="""public boolean canConstruct(String ransomNote, String magazine) {
    StringBuilder mag = new StringBuilder(magazine);
    for (char c : ransomNote.toCharArray()) {
        int i = mag.indexOf(String.valueOf(c));
        if (i < 0) return false;
        mag.deleteCharAt(i);
    }
    return true;
}"""),
 dict(name="HashMap of counts",
      idea="Count the magazine's letters, then spend one for each note letter; fail if a count goes below zero.",
      time="O(m + n)", space="O(k)",
      code="""public boolean canConstruct(String ransomNote, String magazine) {
    Map<Character, Integer> have = new HashMap<>();
    for (char c : magazine.toCharArray()) have.merge(c, 1, Integer::sum);
    for (char c : ransomNote.toCharArray()) {
        if (have.merge(c, -1, Integer::sum) < 0) return false;
    }
    return true;
}"""),
 dict(name="int[26] counts (optimal)",
      idea="Same with an array of 26 counts.",
      time="O(m + n)", space="O(1)", best=True,
      code="""public boolean canConstruct(String ransomNote, String magazine) {
    if (ransomNote.length() > magazine.length()) return false;
    int[] have = new int[26];
    for (char c : magazine.toCharArray()) have[c - 'a']++;
    for (char c : ransomNote.toCharArray()) if (--have[c - 'a'] < 0) return false;
    return true;
}"""),
],

# ------------------------------------------------------------------ Binary search
"binary-search": [
 dict(name="Linear scan",
      idea="Check every element. Ignores that the array is sorted.",
      time="O(n)", space="O(1)",
      code="""public int search(int[] nums, int target) {
    for (int i = 0; i < nums.length; i++) if (nums[i] == target) return i;
    return -1;
}"""),
 dict(name="Recursive binary search",
      idea="Compare with the middle element and recurse into the half that can still contain the target.",
      time="O(log n)", space="O(log n) recursion stack",
      code="""public int search(int[] nums, int target) {
    return go(nums, target, 0, nums.length - 1);
}
private int go(int[] a, int t, int lo, int hi) {
    if (lo > hi) return -1;
    int mid = lo + (hi - lo) / 2;
    if (a[mid] == t) return mid;
    return a[mid] < t ? go(a, t, mid + 1, hi) : go(a, t, lo, mid - 1);
}"""),
 dict(name="Iterative binary search (optimal)",
      idea="Keep [lo, hi] as the range that may contain the target; halve it each step. mid = lo + (hi - lo) / 2 avoids overflow.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int search(int[] nums, int target) {
    int lo = 0, hi = nums.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}"""),
],

"gfg-ceil-in-a-sorted-array": [
 dict(name="Linear scan",
      idea="The first element >= x is the ceiling.",
      time="O(n)", space="O(1)",
      code="""public int findCeil(int[] arr, int x) {
    for (int i = 0; i < arr.length; i++) if (arr[i] >= x) return i;
    return -1;
}"""),
 dict(name="Lower-bound binary search (optimal)",
      idea="Find the first index whose value is >= x; if the search runs off the end there is no ceiling.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int findCeil(int[] arr, int x) {
    int lo = 0, hi = arr.length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] >= x) hi = mid;
        else lo = mid + 1;
    }
    return lo < arr.length ? lo : -1;
}"""),
],

"find-first-and-last-position-of-element-in-sorted-array": [
 dict(name="Linear scan",
      idea="Record the first and last index where the value equals the target.",
      time="O(n)", space="O(1)",
      code="""public int[] searchRange(int[] nums, int target) {
    int first = -1, last = -1;
    for (int i = 0; i < nums.length; i++)
        if (nums[i] == target) { if (first == -1) first = i; last = i; }
    return new int[]{first, last};
}"""),
 dict(name="Binary search once, then expand",
      idea="Find any occurrence with binary search, then walk left and right. Degrades to O(n) when the target repeats many times.",
      time="O(log n + k)", space="O(1)",
      code="""public int[] searchRange(int[] nums, int target) {
    int lo = 0, hi = nums.length - 1, at = -1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) { at = mid; break; }
        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    if (at == -1) return new int[]{-1, -1};
    int l = at, r = at;
    while (l > 0 && nums[l - 1] == target) l--;
    while (r < nums.length - 1 && nums[r + 1] == target) r++;
    return new int[]{l, r};
}"""),
 dict(name="Two lower-bound searches (optimal)",
      idea="first = lowerBound(target); last = lowerBound(target + 1) - 1. If first is out of range or not the target, it is absent.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int[] searchRange(int[] nums, int target) {
    int first = lowerBound(nums, target);
    if (first == nums.length || nums[first] != target) return new int[]{-1, -1};
    return new int[]{first, lowerBound(nums, target + 1) - 1};
}
private int lowerBound(int[] a, int x) {
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] >= x) hi = mid; else lo = mid + 1;
    }
    return lo;
}"""),
],

"gfg-number-of-occurrence": [
 dict(name="Linear count",
      idea="Count matching elements.",
      time="O(n)", space="O(1)",
      code="""public int countFreq(int[] arr, int target) {
    int c = 0;
    for (int x : arr) if (x == target) c++;
    return c;
}"""),
 dict(name="Two binary searches (optimal)",
      idea="count = lowerBound(target + 1) - lowerBound(target): the size of the block of equal values.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int countFreq(int[] arr, int target) {
    return lowerBound(arr, target + 1) - lowerBound(arr, target);
}
private int lowerBound(int[] a, int x) {
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] >= x) hi = mid; else lo = mid + 1;
    }
    return lo;
}"""),
],

"gfg-search-in-infinite-sorted-array": [
 dict(name="Linear scan until the values pass the target",
      idea="We cannot ask for the length, so walk forward until we find the target or pass it. get(i) returns Integer.MAX_VALUE beyond the data, like an infinite array.",
      time="O(p) for answer position p", space="O(1)",
      code="""public int search(int[] arr, int target) {
    for (int i = 0; ; i++) {
        int v = get(arr, i);
        if (v == target) return i;
        if (v > target) return -1;
    }
}
private int get(int[] a, int i) { return i < a.length ? a[i] : Integer.MAX_VALUE; }"""),
 dict(name="Double the window, then binary search (optimal)",
      idea="Grow hi = 1, 2, 4, 8, ... until get(hi) >= target; the target must lie in [hi / 2, hi]. Then run normal binary search there.",
      time="O(log p)", space="O(1)", best=True,
      code="""public int search(int[] arr, int target) {
    int lo = 0, hi = 1;
    while (get(arr, hi) < target) { lo = hi; hi *= 2; }
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2, v = get(arr, mid);
        if (v == target) return mid;
        if (v < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}
private int get(int[] a, int i) { return i < a.length ? a[i] : Integer.MAX_VALUE; }"""),
],

"peak-index-in-a-mountain-array": [
 dict(name="Linear scan",
      idea="The peak is the first index whose next value is smaller.",
      time="O(n)", space="O(1)",
      code="""public int peakIndexInMountainArray(int[] arr) {
    int i = 0;
    while (arr[i] < arr[i + 1]) i++;
    return i;
}"""),
 dict(name="Binary search on the slope (optimal)",
      idea="If arr[mid] < arr[mid + 1] we are on the rising side, so the peak is to the right; otherwise it is at mid or to the left.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int peakIndexInMountainArray(int[] arr) {
    int lo = 0, hi = arr.length - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] < arr[mid + 1]) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}"""),
],

"find-peak-element": [
 dict(name="Linear scan",
      idea="Return the first index that is bigger than the next one (or the last index).",
      time="O(n)", space="O(1)",
      code="""public int findPeakElement(int[] nums) {
    for (int i = 0; i < nums.length - 1; i++) if (nums[i] > nums[i + 1]) return i;
    return nums.length - 1;
}"""),
 dict(name="Binary search on the slope (optimal)",
      idea="Walking uphill must reach a peak (the ends count as -infinity). If nums[mid] < nums[mid + 1], a peak exists to the right; otherwise at mid or to the left.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int findPeakElement(int[] nums) {
    int lo = 0, hi = nums.length - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] < nums[mid + 1]) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}"""),
],

"find-minimum-in-rotated-sorted-array": [
 dict(name="Linear scan for the minimum",
      idea="Look at every element.",
      time="O(n)", space="O(1)",
      code="""public int findMin(int[] nums) {
    int min = nums[0];
    for (int x : nums) min = Math.min(min, x);
    return min;
}"""),
 dict(name="Binary search against the right end (optimal)",
      idea="If nums[mid] > nums[hi], the drop (minimum) is to the right of mid; otherwise the minimum is at mid or to its left.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int findMin(int[] nums) {
    int lo = 0, hi = nums.length - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1;
        else hi = mid;
    }
    return nums[lo];
}"""),
],

"gfg-find-kth-rotation": [
 dict(name="Linear scan for the minimum's index",
      idea="The number of rotations equals the index of the smallest element.",
      time="O(n)", space="O(1)",
      code="""public int findKRotation(int[] arr) {
    int idx = 0;
    for (int i = 1; i < arr.length; i++) if (arr[i] < arr[idx]) idx = i;
    return idx;
}"""),
 dict(name="Binary search for the minimum's index (optimal)",
      idea="Same search as Find Minimum in Rotated Sorted Array, but return the index.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int findKRotation(int[] arr) {
    int lo = 0, hi = arr.length - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (arr[mid] > arr[hi]) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}"""),
],

"search-in-rotated-sorted-array": [
 dict(name="Linear scan",
      idea="Check every element.",
      time="O(n)", space="O(1)",
      code="""public int search(int[] nums, int target) {
    for (int i = 0; i < nums.length; i++) if (nums[i] == target) return i;
    return -1;
}"""),
 dict(name="Find the rotation point, then binary search one side",
      idea="Binary search the index of the minimum; the array is two sorted pieces around it. Search the piece that can contain the target.",
      time="O(log n)", space="O(1)",
      code="""public int search(int[] nums, int target) {
    int n = nums.length, lo = 0, hi = n - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid;
    }
    int pivot = lo;
    if (target >= nums[pivot] && target <= nums[n - 1]) { lo = pivot; hi = n - 1; }
    else { lo = 0; hi = pivot - 1; }
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
}"""),
 dict(name="One binary search, pick the sorted half (optimal)",
      idea="At every step one half of [lo, hi] is sorted. If the target lies inside that sorted half, go there; otherwise go to the other half.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int search(int[] nums, int target) {
    int lo = 0, hi = nums.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (nums[mid] == target) return mid;
        if (nums[lo] <= nums[mid]) {                       // left half sorted
            if (target >= nums[lo] && target < nums[mid]) hi = mid - 1;
            else lo = mid + 1;
        } else {                                           // right half sorted
            if (target > nums[mid] && target <= nums[hi]) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return -1;
}"""),
],

"koko-eating-bananas": [
 dict(name="Try every speed from 1 upward",
      idea="The first speed that finishes within h hours is the answer.",
      time="O(max pile x n)", space="O(1)",
      code="""public int minEatingSpeed(int[] piles, int h) {
    for (int k = 1; ; k++) {
        long hours = 0;
        for (int p : piles) hours += (p + k - 1) / k;
        if (hours <= h) return k;
    }
}"""),
 dict(name="Binary search on the speed (optimal)",
      idea="Hours needed only goes down as speed goes up, so binary search the smallest speed in [1, max pile] that finishes in time.",
      time="O(n log max)", space="O(1)", best=True,
      code="""public int minEatingSpeed(int[] piles, int h) {
    int lo = 1, hi = 0;
    for (int p : piles) hi = Math.max(hi, p);
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        long hours = 0;
        for (int p : piles) hours += (p + mid - 1) / mid;
        if (hours <= h) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}"""),
],

"minimum-number-of-days-to-make-m-bouquets": [
 dict(name="Try every distinct bloom day in order",
      idea="The answer is one of the bloom days. Sort the distinct days and return the first on which m bouquets of k adjacent flowers can be made.",
      time="O(n^2)", space="O(n)",
      code="""public int minDays(int[] bloomDay, int m, int k) {
    if ((long) m * k > bloomDay.length) return -1;
    int[] days = Arrays.stream(bloomDay).distinct().sorted().toArray();
    for (int d : days) if (canMake(bloomDay, d, m, k)) return d;
    return -1;
}
private boolean canMake(int[] b, int day, int m, int k) {
    int made = 0, run = 0;
    for (int x : b) {
        run = x <= day ? run + 1 : 0;
        if (run == k) { made++; run = 0; }
    }
    return made >= m;
}"""),
 dict(name="Binary search on the day (optimal)",
      idea="If it is possible by day d, it is possible on any later day. Binary search the smallest such day between min and max bloom day.",
      time="O(n log(max day))", space="O(1)", best=True,
      code="""public int minDays(int[] bloomDay, int m, int k) {
    if ((long) m * k > bloomDay.length) return -1;
    int lo = Integer.MAX_VALUE, hi = 0;
    for (int x : bloomDay) { lo = Math.min(lo, x); hi = Math.max(hi, x); }
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (canMake(bloomDay, mid, m, k)) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}
private boolean canMake(int[] b, int day, int m, int k) {
    int made = 0, run = 0;
    for (int x : b) {
        run = x <= day ? run + 1 : 0;
        if (run == k) { made++; run = 0; }
    }
    return made >= m;
}"""),
],

"gfg-aggressive-cows": [
 dict(name="Try every distance from 1 upward",
      idea="Sort the stalls. Place cows greedily (first stall, then the next stall at least d away). The answer is the largest d that still fits all k cows.",
      time="O(n x range)", space="O(1)",
      code="""public int aggressiveCows(int[] stalls, int k) {
    int[] s = stalls.clone();
    Arrays.sort(s);
    int best = 0;
    for (int d = 1; d <= s[s.length - 1] - s[0]; d++) {
        if (canPlace(s, d, k)) best = d;
        else break;
    }
    return best;
}
private boolean canPlace(int[] s, int d, int k) {
    int cows = 1, last = s[0];
    for (int i = 1; i < s.length; i++) {
        if (s[i] - last >= d) { cows++; last = s[i]; }
    }
    return cows >= k;
}"""),
 dict(name="Binary search on the answer (optimal)",
      idea="If k cows fit with gap d, they fit with any smaller gap. Binary search the largest d in [1, max - min] for which greedy placement works.",
      time="O(n log n + n log range)", space="O(1)", best=True,
      code="""public int aggressiveCows(int[] stalls, int k) {
    int[] s = stalls.clone();
    Arrays.sort(s);
    int lo = 1, hi = s[s.length - 1] - s[0], best = 0;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (canPlace(s, mid, k)) { best = mid; lo = mid + 1; }
        else hi = mid - 1;
    }
    return best;
}
private boolean canPlace(int[] s, int d, int k) {
    int cows = 1, last = s[0];
    for (int i = 1; i < s.length; i++) {
        if (s[i] - last >= d) { cows++; last = s[i]; }
    }
    return cows >= k;
}"""),
],

"h-index-ii": [
 dict(name="Linear scan",
      idea="Citations are sorted ascending. The first index i with citations[i] >= n - i gives h = n - i.",
      time="O(n)", space="O(1)",
      code="""public int hIndex(int[] citations) {
    int n = citations.length;
    for (int i = 0; i < n; i++) if (citations[i] >= n - i) return n - i;
    return 0;
}"""),
 dict(name="Binary search (optimal)",
      idea="Binary search the first index i where citations[i] >= n - i; the answer is n - i.",
      time="O(log n)", space="O(1)", best=True,
      code="""public int hIndex(int[] citations) {
    int n = citations.length, lo = 0, hi = n;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (citations[mid] >= n - mid) hi = mid;
        else lo = mid + 1;
    }
    return n - lo;
}"""),
],

"maximum-candies-allocated-to-k-children": [
 dict(name="Try every pile size from the largest down",
      idea="For a size c, piles can be split into sum(p / c) portions. Return the largest c giving at least k portions.",
      time="O(max pile x n)", space="O(1)",
      code="""public int maximumCandies(int[] candies, long k) {
    int max = 0;
    for (int c : candies) max = Math.max(max, c);
    for (int size = max; size >= 1; size--) {
        long parts = 0;
        for (int c : candies) parts += c / size;
        if (parts >= k) return size;
    }
    return 0;
}"""),
 dict(name="Binary search on the size (optimal)",
      idea="Portions only go down as the size grows, so binary search the largest size whose portion count is at least k.",
      time="O(n log max)", space="O(1)", best=True,
      code="""public int maximumCandies(int[] candies, long k) {
    int lo = 1, hi = 0, best = 0;
    for (int c : candies) hi = Math.max(hi, c);
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        long parts = 0;
        for (int c : candies) parts += c / mid;
        if (parts >= k) { best = mid; lo = mid + 1; }
        else hi = mid - 1;
    }
    return best;
}"""),
],

"capacity-to-ship-packages-within-d-days": [
 dict(name="Try every capacity from the heaviest package upward",
      idea="The capacity must be at least the heaviest package. Simulate loading for each capacity and return the first that needs <= days.",
      time="O(n x (sum - max))", space="O(1)",
      code="""public int shipWithinDays(int[] weights, int days) {
    int max = 0, sum = 0;
    for (int w : weights) { max = Math.max(max, w); sum += w; }
    for (int cap = max; cap <= sum; cap++) if (daysNeeded(weights, cap) <= days) return cap;
    return sum;
}
private int daysNeeded(int[] w, int cap) {
    int d = 1, load = 0;
    for (int x : w) {
        if (load + x > cap) { d++; load = 0; }
        load += x;
    }
    return d;
}"""),
 dict(name="Binary search on the capacity (optimal)",
      idea="Days needed only goes down as capacity grows; binary search the smallest capacity in [max, sum] that fits.",
      time="O(n log sum)", space="O(1)", best=True,
      code="""public int shipWithinDays(int[] weights, int days) {
    int lo = 0, hi = 0;
    for (int w : weights) { lo = Math.max(lo, w); hi += w; }
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (daysNeeded(weights, mid) <= days) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}
private int daysNeeded(int[] w, int cap) {
    int d = 1, load = 0;
    for (int x : w) {
        if (load + x > cap) { d++; load = 0; }
        load += x;
    }
    return d;
}"""),
],

"gfg-allocate-minimum-pages": [
 dict(name="Dynamic programming over split points",
      idea="dp[j][i] = smallest possible maximum when the first i books go to j students. Try every position for the last student's first book.",
      time="O(k x n^2)", space="O(k x n)",
      code="""public int findPages(int[] arr, int k) {
    int n = arr.length;
    if (k > n) return -1;
    long[] pre = new long[n + 1];
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + arr[i];
    long[][] dp = new long[k + 1][n + 1];
    for (long[] row : dp) Arrays.fill(row, Long.MAX_VALUE);
    dp[0][0] = 0;
    for (int j = 1; j <= k; j++)
        for (int i = j; i <= n; i++)
            for (int p = j - 1; p < i; p++)
                if (dp[j - 1][p] != Long.MAX_VALUE)
                    dp[j][i] = Math.min(dp[j][i], Math.max(dp[j - 1][p], pre[i] - pre[p]));
    return (int) dp[k][n];
}"""),
 dict(name="Binary search on the answer (optimal)",
      idea="For a page limit L, give books to a student until the next book would exceed L. If that needs <= k students, L works. Binary search L in [max book, total].",
      time="O(n log total)", space="O(1)", best=True,
      code="""public int findPages(int[] arr, int k) {
    if (k > arr.length) return -1;
    long lo = 0, hi = 0;
    for (int x : arr) { lo = Math.max(lo, x); hi += x; }
    while (lo < hi) {
        long mid = lo + (hi - lo) / 2;
        if (studentsNeeded(arr, mid) <= k) hi = mid;
        else lo = mid + 1;
    }
    return (int) lo;
}
private int studentsNeeded(int[] a, long limit) {
    int s = 1;
    long pages = 0;
    for (int x : a) {
        if (pages + x > limit) { s++; pages = 0; }
        pages += x;
    }
    return s;
}"""),
],

"split-array-largest-sum": [
 dict(name="Dynamic programming over split points",
      idea="dp[j][i] = minimal largest sum when the first i numbers form j subarrays; the last subarray starts at some p.",
      time="O(k x n^2)", space="O(k x n)",
      code="""public int splitArray(int[] nums, int k) {
    int n = nums.length;
    long[] pre = new long[n + 1];
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + nums[i];
    long[][] dp = new long[k + 1][n + 1];
    for (long[] row : dp) Arrays.fill(row, Long.MAX_VALUE);
    dp[0][0] = 0;
    for (int j = 1; j <= k; j++)
        for (int i = j; i <= n; i++)
            for (int p = j - 1; p < i; p++)
                if (dp[j - 1][p] != Long.MAX_VALUE)
                    dp[j][i] = Math.min(dp[j][i], Math.max(dp[j - 1][p], pre[i] - pre[p]));
    return (int) dp[k][n];
}"""),
 dict(name="Binary search on the answer (optimal)",
      idea="Same structure as Allocate Minimum Pages: for a limit L, count greedy subarrays; binary search the smallest L needing <= k pieces.",
      time="O(n log sum)", space="O(1)", best=True,
      code="""public int splitArray(int[] nums, int k) {
    long lo = 0, hi = 0;
    for (int x : nums) { lo = Math.max(lo, x); hi += x; }
    while (lo < hi) {
        long mid = lo + (hi - lo) / 2;
        int pieces = 1;
        long sum = 0;
        for (int x : nums) {
            if (sum + x > mid) { pieces++; sum = 0; }
            sum += x;
        }
        if (pieces <= k) hi = mid;
        else lo = mid + 1;
    }
    return (int) lo;
}"""),
],
}

TESTS = {
 "first-unique-character-in-a-string": [('"leetcode"', "0"), ('"loveleetcode"', "2"), ('"aabb"', "-1")],
 "maximum-number-of-balloons": [('"nlaebolko"', "1"), ('"loonbalxballpoon"', "2"), ('"leetcode"', "0")],
 "longest-palindrome": [('"abccccdd"', "7"), ('"a"', "1"), ('"Aa"', "1"), ('"aaabbb"', "5")],
 "ransom-note": [('"a", "b"', "false"), ('"aa", "ab"', "false"), ('"aa", "aab"', "true")],
 "binary-search": [("new int[]{-1,0,3,5,9,12}, 9", "4"), ("new int[]{-1,0,3,5,9,12}, 2", "-1"), ("new int[]{5}, 5", "0")],
 "gfg-ceil-in-a-sorted-array": [("new int[]{1,2,8,10,11,12,19}, 5", "2"), ("new int[]{1,2,8}, 20", "-1"), ("new int[]{1,1,2,8,10}, 0", "0"),
                                ("new int[]{1,2,2,2,5}, 2", "1")],
 "find-first-and-last-position-of-element-in-sorted-array": [("new int[]{5,7,7,8,8,10}, 8", "[3, 4]"), ("new int[]{5,7,7,8,8,10}, 6", "[-1, -1]"),
                                                              ("new int[]{}, 0", "[-1, -1]"), ("new int[]{2,2}, 2", "[0, 1]")],
 "gfg-number-of-occurrence": [("new int[]{1,1,2,2,2,2,3}, 2", "4"), ("new int[]{1,1,2,2,2,2,3}, 4", "0"), ("new int[]{8,9,10,12,12,12}, 12", "3")],
 "gfg-search-in-infinite-sorted-array": [("new int[]{3,5,7,9,10,90,100,130,140,160,170}, 10", "4"),
                                         ("new int[]{3,5,7,9,10,90,100,130,140,160,170}, 170", "10"),
                                         ("new int[]{3,5,7,9,10,90,100,130,140,160,170}, 6", "-1")],
 "peak-index-in-a-mountain-array": [("new int[]{0,1,0}", "1"), ("new int[]{0,2,1,0}", "1"), ("new int[]{0,10,5,2}", "1"), ("new int[]{0,1,2,5,3}", "3")],
 "find-peak-element": [("new int[]{1,2,3,1}", "2"), ("!int[] a = {1,2,1,3,5,6,4}; int p = o.{m}(a); r = (p == 1 || p == 5);", "true"),
                       ("new int[]{1}", "0"), ("new int[]{2,1}", "0")],
 "find-minimum-in-rotated-sorted-array": [("new int[]{3,4,5,1,2}", "1"), ("new int[]{4,5,6,7,0,1,2}", "0"), ("new int[]{11,13,15,17}", "11"), ("new int[]{2,1}", "1")],
 "gfg-find-kth-rotation": [("new int[]{5,1,2,3,4}", "1"), ("new int[]{1,2,3,4,5}", "0"), ("new int[]{15,18,2,3,6,12}", "2")],
 "search-in-rotated-sorted-array": [("new int[]{4,5,6,7,0,1,2}, 0", "4"), ("new int[]{4,5,6,7,0,1,2}, 3", "-1"), ("new int[]{1}, 0", "-1"),
                                    ("new int[]{3,1}, 1", "1"), ("new int[]{5,1,3}, 5", "0")],
 "koko-eating-bananas": [("new int[]{3,6,7,11}, 8", "4"), ("new int[]{30,11,23,4,20}, 5", "30"), ("new int[]{30,11,23,4,20}, 6", "23")],
 "minimum-number-of-days-to-make-m-bouquets": [("new int[]{1,10,3,10,2}, 3, 1", "3"), ("new int[]{1,10,3,10,2}, 3, 2", "-1"),
                                               ("new int[]{7,7,7,7,12,7,7}, 2, 3", "12")],
 "gfg-aggressive-cows": [("new int[]{1,2,4,8,9}, 3", "3"), ("new int[]{10,1,2,7,5}, 3", "4"), ("new int[]{2,12,11,3,26,7}, 5", "1")],
 "h-index-ii": [("new int[]{0,1,3,5,6}", "3"), ("new int[]{1,2,100}", "2"), ("new int[]{0}", "0"), ("new int[]{100}", "1")],
 "maximum-candies-allocated-to-k-children": [("new int[]{5,8,6}, 3L", "5"), ("new int[]{2,5}, 11L", "0"), ("new int[]{4,7,5}, 4L", "3")],
 "capacity-to-ship-packages-within-d-days": [("new int[]{1,2,3,4,5,6,7,8,9,10}, 5", "15"), ("new int[]{3,2,2,4,1,4}, 3", "6"), ("new int[]{1,2,3,1,1}, 4", "3")],
 "gfg-allocate-minimum-pages": [("new int[]{12,34,67,90}, 2", "113"), ("new int[]{15,17,20}, 5", "-1"), ("new int[]{22,23,67}, 1", "112")],
 "split-array-largest-sum": [("new int[]{7,2,5,10,8}, 2", "18"), ("new int[]{1,2,3,4,5}, 2", "9"), ("new int[]{1,4,4}, 3", "4")],
}
