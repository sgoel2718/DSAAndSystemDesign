"""Approaches for the Two Pointers questions from the Padho with Pratyush practice sheet (Java only)."""

SOL = {

"sort-colors": [
 dict(name="Library sort",
      idea="Just sort the array. Correct, but ignores that there are only three values.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public void sortColors(int[] nums) {
    Arrays.sort(nums);
}"""),
 dict(name="Counting sort (two passes)",
      idea="Count how many 0s, 1s and 2s there are, then overwrite the array in order.",
      time="O(n)", space="O(1)",
      code="""public void sortColors(int[] nums) {
    int[] count = new int[3];
    for (int x : nums) count[x]++;
    int i = 0;
    for (int c = 0; c < 3; c++)
        while (count[c]-- > 0) nums[i++] = c;
}"""),
 dict(name="Dutch National Flag, one pass (optimal)",
      idea="Three pointers: everything before low is 0, everything after high is 2, mid scans. Swap 0s to low and 2s to high; do not advance mid after swapping with high because the swapped-in value is unchecked.",
      time="O(n)", space="O(1)", best=True,
      code="""public void sortColors(int[] nums) {
    int low = 0, mid = 0, high = nums.length - 1;
    while (mid <= high) {
        if (nums[mid] == 0) {
            int t = nums[low]; nums[low] = nums[mid]; nums[mid] = t;
            low++; mid++;
        } else if (nums[mid] == 1) {
            mid++;
        } else {
            int t = nums[high]; nums[high] = nums[mid]; nums[mid] = t;
            high--;
        }
    }
}"""),
],

"remove-duplicates-from-sorted-array": [
 dict(name="LinkedHashSet, then copy back",
      idea="Collect unique values in order with a LinkedHashSet and write them back to the front.",
      time="O(n)", space="O(n)",
      code="""public int removeDuplicates(int[] nums) {
    Set<Integer> uniq = new LinkedHashSet<>();
    for (int x : nums) uniq.add(x);
    int k = 0;
    for (int x : uniq) nums[k++] = x;
    return k;
}"""),
 dict(name="Two pointers: read and write (optimal)",
      idea="The array is sorted, so a value is new exactly when it differs from the last value written. Copy only those to the write pointer.",
      time="O(n)", space="O(1)", best=True,
      code="""public int removeDuplicates(int[] nums) {
    if (nums.length == 0) return 0;
    int write = 1;
    for (int read = 1; read < nums.length; read++) {
        if (nums[read] != nums[write - 1]) nums[write++] = nums[read];
    }
    return write;
}"""),
],

"4sum": [
 dict(name="Brute force: every quadruplet + set",
      idea="Try all quadruplets; store each sorted quadruplet in a Set to drop duplicates. Use long for the sum.",
      time="O(n^4)", space="O(k) for k answers",
      code="""public List<List<Integer>> fourSum(int[] nums, int target) {
    Set<List<Integer>> found = new HashSet<>();
    int n = nums.length;
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++)
            for (int c = b + 1; c < n; c++)
                for (int d = c + 1; d < n; d++)
                    if ((long) nums[a] + nums[b] + nums[c] + nums[d] == target) {
                        List<Integer> q = Arrays.asList(nums[a], nums[b], nums[c], nums[d]);
                        Collections.sort(q);
                        found.add(q);
                    }
    return new ArrayList<>(found);
}"""),
 dict(name="Fix two numbers + HashSet for the third and fourth",
      idea="Sort, fix i and j, then do Two Sum with a HashSet on the rest. A Set of results removes duplicates.",
      time="O(n^3)", space="O(n)",
      code="""public List<List<Integer>> fourSum(int[] nums, int target) {
    Arrays.sort(nums);
    Set<List<Integer>> found = new HashSet<>();
    int n = nums.length;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            Set<Long> seen = new HashSet<>();
            for (int k = j + 1; k < n; k++) {
                long need = (long) target - nums[i] - nums[j] - nums[k];
                if (seen.contains(need)) found.add(Arrays.asList(nums[i], nums[j], (int) need, nums[k]));
                seen.add((long) nums[k]);
            }
        }
    return new ArrayList<>(found);
}"""),
 dict(name="Sort + fix two + two pointers (optimal)",
      idea="Same as 3Sum with one more loop: fix i and j, two pointers on the rest, skip equal values at every level. Use long to avoid overflow.",
      time="O(n^3)", space="O(log n) sort stack", best=True,
      code="""public List<List<Integer>> fourSum(int[] nums, int target) {
    Arrays.sort(nums);
    List<List<Integer>> res = new ArrayList<>();
    int n = nums.length;
    for (int i = 0; i < n - 3; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        for (int j = i + 1; j < n - 2; j++) {
            if (j > i + 1 && nums[j] == nums[j - 1]) continue;
            int l = j + 1, r = n - 1;
            while (l < r) {
                long sum = (long) nums[i] + nums[j] + nums[l] + nums[r];
                if (sum == target) {
                    res.add(Arrays.asList(nums[i], nums[j], nums[l], nums[r]));
                    while (l < r && nums[l] == nums[l + 1]) l++;
                    while (l < r && nums[r] == nums[r - 1]) r--;
                    l++;
                    r--;
                } else if (sum < target) l++;
                else r--;
            }
        }
    }
    return res;
}"""),
],

"gfg-segregate-0s-and-1s": [
 dict(name="Library sort",
      idea="Sorting puts all 0s before 1s.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public void segregate0and1(int[] arr) {
    Arrays.sort(arr);
}"""),
 dict(name="Count the zeros (two passes)",
      idea="Count the 0s, then write that many 0s followed by 1s.",
      time="O(n)", space="O(1)",
      code="""public void segregate0and1(int[] arr) {
    int zeros = 0;
    for (int x : arr) if (x == 0) zeros++;
    for (int i = 0; i < arr.length; i++) arr[i] = i < zeros ? 0 : 1;
}"""),
 dict(name="Two pointers from both ends (optimal, one pass)",
      idea="Move l right past 0s and r left past 1s; when l sees a 1 and r sees a 0, swap them.",
      time="O(n)", space="O(1)", best=True,
      code="""public void segregate0and1(int[] arr) {
    int l = 0, r = arr.length - 1;
    while (l < r) {
        if (arr[l] == 0) l++;
        else if (arr[r] == 1) r--;
        else { arr[l] = 0; arr[r] = 1; l++; r--; }
    }
}"""),
],

"remove-duplicates-from-sorted-list": [
 dict(name="Rebuild from a LinkedHashSet",
      idea="Collect unique values in order, then build a fresh list.",
      time="O(n)", space="O(n)",
      code="""public ListNode deleteDuplicates(ListNode head) {
    Set<Integer> uniq = new LinkedHashSet<>();
    for (ListNode p = head; p != null; p = p.next) uniq.add(p.val);
    ListNode dummy = new ListNode(0), tail = dummy;
    for (int v : uniq) { tail.next = new ListNode(v); tail = tail.next; }
    return dummy.next;
}"""),
 dict(name="Recursion",
      idea="Clean the rest of the list first, then skip the head's next node if it has the same value.",
      time="O(n)", space="O(n) recursion stack",
      code="""public ListNode deleteDuplicates(ListNode head) {
    if (head == null || head.next == null) return head;
    head.next = deleteDuplicates(head.next);
    return head.val == head.next.val ? head.next : head;
}"""),
 dict(name="One pass, skip equal neighbours (optimal)",
      idea="The list is sorted, so duplicates are adjacent: while the next node has the same value, unlink it.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode deleteDuplicates(ListNode head) {
    ListNode cur = head;
    while (cur != null && cur.next != null) {
        if (cur.next.val == cur.val) cur.next = cur.next.next;
        else cur = cur.next;
    }
    return head;
}"""),
],

"remove-duplicates-from-sorted-array-ii": [
 dict(name="Count occurrences, write at most two",
      idea="Count each value with a TreeMap (keeps sorted order), then write each value min(count, 2) times.",
      time="O(n log n)", space="O(n)",
      code="""public int removeDuplicates(int[] nums) {
    Map<Integer, Integer> count = new TreeMap<>();
    for (int x : nums) count.merge(x, 1, Integer::sum);
    int k = 0;
    for (Map.Entry<Integer, Integer> e : count.entrySet())
        for (int c = 0; c < Math.min(2, e.getValue()); c++) nums[k++] = e.getKey();
    return k;
}"""),
 dict(name="Two pointers: compare with the element two places back (optimal)",
      idea="A value may be written if it differs from the value written two slots earlier; that allows at most two copies. Generalises to 'at most k'.",
      time="O(n)", space="O(1)", best=True,
      code="""public int removeDuplicates(int[] nums) {
    int write = 0;
    for (int x : nums) {
        if (write < 2 || x != nums[write - 2]) nums[write++] = x;
    }
    return write;
}"""),
],

"squares-of-a-sorted-array": [
 dict(name="Square everything, then sort",
      idea="Squares of negatives can be large, so the squared array is unsorted; sort it.",
      time="O(n log n)", space="O(n) output",
      code="""public int[] sortedSquares(int[] nums) {
    int[] out = new int[nums.length];
    for (int i = 0; i < nums.length; i++) out[i] = nums[i] * nums[i];
    Arrays.sort(out);
    return out;
}"""),
 dict(name="Two pointers, fill from the back (optimal)",
      idea="The largest square is at one of the two ends. Compare the ends and place the larger square at the back of the output.",
      time="O(n)", space="O(n) output", best=True,
      code="""public int[] sortedSquares(int[] nums) {
    int n = nums.length, l = 0, r = n - 1;
    int[] out = new int[n];
    for (int k = n - 1; k >= 0; k--) {
        if (Math.abs(nums[l]) > Math.abs(nums[r])) { out[k] = nums[l] * nums[l]; l++; }
        else { out[k] = nums[r] * nums[r]; r--; }
    }
    return out;
}"""),
],

"3sum-closest": [
 dict(name="Brute force: every triplet",
      idea="Try all triplets and keep the sum closest to the target.",
      time="O(n^3)", space="O(1)",
      code="""public int threeSumClosest(int[] nums, int target) {
    int best = nums[0] + nums[1] + nums[2];
    for (int i = 0; i < nums.length; i++)
        for (int j = i + 1; j < nums.length; j++)
            for (int k = j + 1; k < nums.length; k++) {
                int s = nums[i] + nums[j] + nums[k];
                if (Math.abs(s - target) < Math.abs(best - target)) best = s;
            }
    return best;
}"""),
 dict(name="Sort + two pointers (optimal)",
      idea="Sort, fix i, move two pointers: sum too small -> l++, too big -> r--, equal -> return immediately. Track the closest sum.",
      time="O(n^2)", space="O(log n) sort stack", best=True,
      code="""public int threeSumClosest(int[] nums, int target) {
    Arrays.sort(nums);
    int best = nums[0] + nums[1] + nums[2];
    for (int i = 0; i < nums.length - 2; i++) {
        int l = i + 1, r = nums.length - 1;
        while (l < r) {
            int s = nums[i] + nums[l] + nums[r];
            if (Math.abs(s - target) < Math.abs(best - target)) best = s;
            if (s == target) return s;
            if (s < target) l++;
            else r--;
        }
    }
    return best;
}"""),
],

"gfg-count-triplets-with-sum-smaller-than-x": [
 dict(name="Brute force: every triplet",
      idea="Count every triplet whose sum is below the target.",
      time="O(n^3)", space="O(1)",
      code="""public long countTriplets(int[] arr, int sum) {
    long count = 0;
    int n = arr.length;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            for (int k = j + 1; k < n; k++)
                if (arr[i] + arr[j] + arr[k] < sum) count++;
    return count;
}"""),
 dict(name="Sort + two pointers, count a whole block at once (optimal)",
      idea="Sort, fix i. If arr[i] + arr[l] + arr[r] < sum, then every r' in (l, r] also works with l, so add r - l and move l. Otherwise move r.",
      time="O(n^2)", space="O(log n) sort stack", best=True,
      code="""public long countTriplets(int[] arr, int sum) {
    Arrays.sort(arr);
    long count = 0;
    for (int i = 0; i < arr.length - 2; i++) {
        int l = i + 1, r = arr.length - 1;
        while (l < r) {
            if (arr[i] + arr[l] + arr[r] < sum) {
                count += r - l;
                l++;
            } else r--;
        }
    }
    return count;
}"""),
],

"subarray-product-less-than-k": [
 dict(name="Brute force with early stop",
      idea="From each start, multiply forward while the product stays below k (all numbers are positive, so it only grows).",
      time="O(n^2)", space="O(1)",
      code="""public int numSubarrayProductLessThanK(int[] nums, int k) {
    int count = 0;
    for (int i = 0; i < nums.length; i++) {
        long p = 1;
        for (int j = i; j < nums.length; j++) {
            p *= nums[j];
            if (p >= k) break;
            count++;
        }
    }
    return count;
}"""),
 dict(name="Sliding window (optimal)",
      idea="Grow the window to the right; while the product is >= k, divide out the left element. Every window ending at r contributes r - l + 1 subarrays.",
      time="O(n)", space="O(1)", best=True,
      code="""public int numSubarrayProductLessThanK(int[] nums, int k) {
    if (k <= 1) return 0;
    long prod = 1;
    int l = 0, count = 0;
    for (int r = 0; r < nums.length; r++) {
        prod *= nums[r];
        while (prod >= k) prod /= nums[l++];
        count += r - l + 1;
    }
    return count;
}"""),
],

"backspace-string-compare": [
 dict(name="Build both strings with a stack",
      idea="Process each string: a letter is pushed, '#' pops. Compare the results.",
      time="O(n + m)", space="O(n + m)",
      code="""public boolean backspaceCompare(String s, String t) {
    return build(s).equals(build(t));
}
private String build(String s) {
    StringBuilder sb = new StringBuilder();
    for (char c : s.toCharArray()) {
        if (c != '#') sb.append(c);
        else if (sb.length() > 0) sb.deleteCharAt(sb.length() - 1);
    }
    return sb.toString();
}"""),
 dict(name="Two pointers from the end (optimal)",
      idea="Walk both strings backwards, skipping characters that a later '#' deletes. Compare the next surviving character of each.",
      time="O(n + m)", space="O(1)", best=True,
      code="""public boolean backspaceCompare(String s, String t) {
    int i = s.length() - 1, j = t.length() - 1;
    while (i >= 0 || j >= 0) {
        i = nextValid(s, i);
        j = nextValid(t, j);
        if (i < 0 || j < 0) return i < 0 && j < 0;
        if (s.charAt(i) != t.charAt(j)) return false;
        i--;
        j--;
    }
    return true;
}
private int nextValid(String s, int i) {
    int skip = 0;
    while (i >= 0) {
        if (s.charAt(i) == '#') { skip++; i--; }
        else if (skip > 0) { skip--; i--; }
        else break;
    }
    return i;
}"""),
],

"shortest-unsorted-continuous-subarray": [
 dict(name="Sort a copy and compare",
      idea="The answer is the span between the first and last positions where the array differs from its sorted copy.",
      time="O(n log n)", space="O(n)",
      code="""public int findUnsortedSubarray(int[] nums) {
    int[] sorted = nums.clone();
    Arrays.sort(sorted);
    int l = 0, r = nums.length - 1;
    while (l <= r && nums[l] == sorted[l]) l++;
    while (r >= l && nums[r] == sorted[r]) r--;
    return r - l + 1;
}"""),
 dict(name="Monotonic stacks",
      idea="Left boundary: smallest index popped by an increasing stack scanning left to right. Right boundary: largest index popped by a decreasing stack scanning right to left.",
      time="O(n)", space="O(n)",
      code="""public int findUnsortedSubarray(int[] nums) {
    int n = nums.length, l = n, r = 0;
    Deque<Integer> st = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {
        while (!st.isEmpty() && nums[st.peek()] > nums[i]) l = Math.min(l, st.pop());
        st.push(i);
    }
    st.clear();
    for (int i = n - 1; i >= 0; i--) {
        while (!st.isEmpty() && nums[st.peek()] < nums[i]) r = Math.max(r, st.pop());
        st.push(i);
    }
    return r > l ? r - l + 1 : 0;
}"""),
 dict(name="Two scans with running max and min (optimal)",
      idea="Scanning left to right, any element smaller than the running max is out of place: the last such index is the right end. Scanning right to left with a running min gives the left end.",
      time="O(n)", space="O(1)", best=True,
      code="""public int findUnsortedSubarray(int[] nums) {
    int n = nums.length, max = Integer.MIN_VALUE, min = Integer.MAX_VALUE, end = -1, start = 0;
    for (int i = 0; i < n; i++) {
        max = Math.max(max, nums[i]);
        if (nums[i] < max) end = i;
    }
    for (int i = n - 1; i >= 0; i--) {
        min = Math.min(min, nums[i]);
        if (nums[i] > min) start = i;
    }
    return end == -1 ? 0 : end - start + 1;
}"""),
],
}

ARR = lambda k: f'!int[] a = {k}; int n = o.{{m}}(a); r = Arrays.toString(Arrays.copyOf(a, n));'
TESTS = {
 "sort-colors": [("!int[] a = {2,0,2,1,1,0}; o.{m}(a); r = a;", "[0, 0, 1, 1, 2, 2]"), ("!int[] a = {2,0,1}; o.{m}(a); r = a;", "[0, 1, 2]"),
                 ("!int[] a = {1}; o.{m}(a); r = a;", "[1]")],
 "remove-duplicates-from-sorted-array": [(ARR("{1,1,2}"), "[1, 2]"), (ARR("{0,0,1,1,1,2,2,3,3,4}"), "[0, 1, 2, 3, 4]"), (ARR("{7}"), "[7]")],
 "4sum": [("!r = norm(o.{m}(new int[]{1,0,-1,0,-2,2}, 0));", "[[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]"),
          ("!r = norm(o.{m}(new int[]{2,2,2,2,2}, 8));", "[[2, 2, 2, 2]]"),
          ("!r = norm(o.{m}(new int[]{1000000000,1000000000,1000000000,1000000000}, -294967296));", "[]")],
 "gfg-segregate-0s-and-1s": [("!int[] a = {0,0,1,1,0}; o.{m}(a); r = a;", "[0, 0, 0, 1, 1]"),
                             ("!int[] a = {1,1,1,1}; o.{m}(a); r = a;", "[1, 1, 1, 1]"), ("!int[] a = {1,0,1,0,1,0}; o.{m}(a); r = a;", "[0, 0, 0, 1, 1, 1]")],
 "remove-duplicates-from-sorted-list": [("!r = toList(o.{m}(list(1,1,2)));", "[1, 2]"), ("!r = toList(o.{m}(list(1,1,2,3,3)));", "[1, 2, 3]"),
                                        ("!r = toList(o.{m}(list()));", "[]")],
 "remove-duplicates-from-sorted-array-ii": [(ARR("{1,1,1,2,2,3}"), "[1, 1, 2, 2, 3]"), (ARR("{0,0,1,1,1,1,2,3,3}"), "[0, 0, 1, 1, 2, 3, 3]")],
 "squares-of-a-sorted-array": [("new int[]{-4,-1,0,3,10}", "[0, 1, 9, 16, 100]"), ("new int[]{-7,-3,2,3,11}", "[4, 9, 9, 49, 121]")],
 "3sum-closest": [("new int[]{-1,2,1,-4}, 1", "2"), ("new int[]{0,0,0}, 1", "0"), ("new int[]{4,0,5,-5,3,3,0,-4,-5}, -2", "-2")],
 "gfg-count-triplets-with-sum-smaller-than-x": [("new int[]{-2,0,1,3}, 2", "2"), ("new int[]{5,1,3,4,7}, 12", "4")],
 "subarray-product-less-than-k": [("new int[]{10,5,2,6}, 100", "8"), ("new int[]{1,2,3}, 0", "0"), ("new int[]{1,1,1}, 2", "6")],
 "backspace-string-compare": [('"ab#c", "ad#c"', "true"), ('"ab##", "c#d#"', "true"), ('"a#c", "b"', "false"), ('"bxj##tw", "bxo#j##tw"', "true")],
 "shortest-unsorted-continuous-subarray": [("new int[]{2,6,4,8,10,9,15}", "5"), ("new int[]{1,2,3,4}", "0"), ("new int[]{1}", "0"),
                                           ("new int[]{1,3,2,2,2}", "4")],
}
