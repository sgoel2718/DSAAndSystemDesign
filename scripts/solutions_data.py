"""All approaches for every problem taught so far, in Java only.
Key = LeetCode slug. Each approach: name, idea, time, space, code (a Java method, compiled by check_solutions.py)."""

SOLUTIONS = {

"two-sum": [
 dict(name="Brute force: every pair",
      idea="Try every pair (i, j) with i < j and return when they add up to target.",
      time="O(n^2)", space="O(1)",
      code="""public int[] twoSum(int[] nums, int target) {
    for (int i = 0; i < nums.length; i++) {
        for (int j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] == target) return new int[]{i, j};
        }
    }
    return new int[0];
}"""),
 dict(name="Sort + two pointers (keep original indices)",
      idea="Sort an array of indices by value, then move two pointers inward. Sorting moves elements, so the index array is needed to report original positions.",
      time="O(n log n)", space="O(n)",
      code="""public int[] twoSum(int[] nums, int target) {
    Integer[] idx = new Integer[nums.length];
    for (int i = 0; i < nums.length; i++) idx[i] = i;
    Arrays.sort(idx, (a, b) -> Integer.compare(nums[a], nums[b]));
    int l = 0, r = nums.length - 1;
    while (l < r) {
        int sum = nums[idx[l]] + nums[idx[r]];
        if (sum == target) return new int[]{Math.min(idx[l], idx[r]), Math.max(idx[l], idx[r])};
        if (sum < target) l++;
        else r--;
    }
    return new int[0];
}"""),
 dict(name="Sort + two pointers (return values only)",
      idea="If only the two values (or true/false) are needed, sort in place and use two pointers. No extra array, but the input order is destroyed.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public int[] twoSumValues(int[] nums, int target) {
    Arrays.sort(nums);
    int l = 0, r = nums.length - 1;
    while (l < r) {
        int sum = nums[l] + nums[r];
        if (sum == target) return new int[]{nums[l], nums[r]};
        if (sum < target) l++;
        else r--;
    }
    return new int[0];
}"""),
 dict(name="HashMap, two passes",
      idea="First pass stores value -> index. Second pass looks up target - x, skipping the same index.",
      time="O(n)", space="O(n)",
      code="""public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> indexOf = new HashMap<>();
    for (int i = 0; i < nums.length; i++) indexOf.put(nums[i], i);
    for (int i = 0; i < nums.length; i++) {
        Integer j = indexOf.get(target - nums[i]);
        if (j != null && j != i) return new int[]{i, j};
    }
    return new int[0];
}"""),
 dict(name="HashMap, one pass (optimal)",
      idea="For each x, check whether target - x was seen earlier; only then store x. Checking before storing stops x pairing with itself.",
      time="O(n)", space="O(n)", best=True,
      code="""public int[] twoSum(int[] nums, int target) {
    Map<Integer, Integer> indexOf = new HashMap<>();
    for (int i = 0; i < nums.length; i++) {
        int need = target - nums[i];
        if (indexOf.containsKey(need)) return new int[]{indexOf.get(need), i};
        indexOf.put(nums[i], i);
    }
    return new int[0];
}"""),
],

"two-sum-ii-input-array-is-sorted": [
 dict(name="Brute force: every pair",
      idea="Ignore the sorted order and check all pairs.",
      time="O(n^2)", space="O(1)",
      code="""public int[] twoSum(int[] numbers, int target) {
    for (int i = 0; i < numbers.length; i++) {
        for (int j = i + 1; j < numbers.length; j++) {
            if (numbers[i] + numbers[j] == target) return new int[]{i + 1, j + 1};
        }
    }
    return new int[0];
}"""),
 dict(name="Binary search for the complement",
      idea="For each i, binary search target - numbers[i] in the part to its right.",
      time="O(n log n)", space="O(1)",
      code="""public int[] twoSum(int[] numbers, int target) {
    for (int i = 0; i < numbers.length; i++) {
        int need = target - numbers[i];
        int lo = i + 1, hi = numbers.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            if (numbers[mid] == need) return new int[]{i + 1, mid + 1};
            if (numbers[mid] < need) lo = mid + 1;
            else hi = mid - 1;
        }
    }
    return new int[0];
}"""),
 dict(name="HashMap",
      idea="Same as Two Sum I. Works, but wastes the sorted order and uses extra memory.",
      time="O(n)", space="O(n)",
      code="""public int[] twoSum(int[] numbers, int target) {
    Map<Integer, Integer> indexOf = new HashMap<>();
    for (int i = 0; i < numbers.length; i++) {
        Integer j = indexOf.get(target - numbers[i]);
        if (j != null) return new int[]{j + 1, i + 1};
        indexOf.put(numbers[i], i);
    }
    return new int[0];
}"""),
 dict(name="Two pointers (optimal)",
      idea="Start at both ends. Sum too small -> move left right; too big -> move right left. Each step discards one element for good.",
      time="O(n)", space="O(1)", best=True,
      code="""public int[] twoSum(int[] numbers, int target) {
    int l = 0, r = numbers.length - 1;
    while (l < r) {
        int sum = numbers[l] + numbers[r];
        if (sum == target) return new int[]{l + 1, r + 1};
        if (sum < target) l++;
        else r--;
    }
    return new int[0];
}"""),
],

"contains-duplicate": [
 dict(name="Brute force: every pair",
      idea="Compare every pair of elements.",
      time="O(n^2)", space="O(1)",
      code="""public boolean containsDuplicate(int[] nums) {
    for (int i = 0; i < nums.length; i++) {
        for (int j = i + 1; j < nums.length; j++) {
            if (nums[i] == nums[j]) return true;
        }
    }
    return false;
}"""),
 dict(name="Sort, then compare neighbours",
      idea="After sorting, equal values sit next to each other. Mutates the input.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public boolean containsDuplicate(int[] nums) {
    Arrays.sort(nums);
    for (int i = 1; i < nums.length; i++) {
        if (nums[i] == nums[i - 1]) return true;
    }
    return false;
}"""),
 dict(name="HashSet (optimal time)",
      idea="Set.add returns false when the value is already present.",
      time="O(n)", space="O(n)", best=True,
      code="""public boolean containsDuplicate(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    for (int x : nums) {
        if (!seen.add(x)) return true;
    }
    return false;
}"""),
 dict(name="Stream distinct count",
      idea="Short one-liner: compare the distinct count with the length. Fine to mention, but it always scans everything and boxes each int.",
      time="O(n)", space="O(n)",
      code="""public boolean containsDuplicate(int[] nums) {
    return Arrays.stream(nums).distinct().count() < nums.length;
}"""),
],

"fizz-buzz": [
 dict(name="Modulo checks (standard)",
      idea="Check 15 first, then 3, then 5.",
      time="O(n)", space="O(1) besides output", best=True,
      code="""public List<String> fizzBuzz(int n) {
    List<String> out = new ArrayList<>(n);
    for (int i = 1; i <= n; i++) {
        if (i % 15 == 0) out.add("FizzBuzz");
        else if (i % 3 == 0) out.add("Fizz");
        else if (i % 5 == 0) out.add("Buzz");
        else out.add(String.valueOf(i));
    }
    return out;
}"""),
 dict(name="String building (easy to extend)",
      idea="Append Fizz and Buzz independently; if nothing was appended use the number. Adding a new rule (e.g. 7 -> Bazz) is one line.",
      time="O(n)", space="O(1) besides output",
      code="""public List<String> fizzBuzz(int n) {
    List<String> out = new ArrayList<>(n);
    for (int i = 1; i <= n; i++) {
        StringBuilder sb = new StringBuilder();
        if (i % 3 == 0) sb.append("Fizz");
        if (i % 5 == 0) sb.append("Buzz");
        out.add(sb.length() == 0 ? String.valueOf(i) : sb.toString());
    }
    return out;
}"""),
 dict(name="Counters, no modulo",
      idea="Keep counters that reset at 3 and 5. Useful follow-up when the interviewer says modulo is expensive.",
      time="O(n)", space="O(1) besides output",
      code="""public List<String> fizzBuzz(int n) {
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
}"""),
],

"richest-customer-wealth": [
 dict(name="Nested loops (optimal)",
      idea="Sum each customer's row and keep the maximum. Every cell must be read once, so this is optimal.",
      time="O(m x n)", space="O(1)", best=True,
      code="""public int maximumWealth(int[][] accounts) {
    int best = 0;
    for (int[] customer : accounts) {
        int sum = 0;
        for (int money : customer) sum += money;
        best = Math.max(best, sum);
    }
    return best;
}"""),
 dict(name="Streams",
      idea="Map each row to its sum and take the max. Readable; slightly slower than plain loops.",
      time="O(m x n)", space="O(1)",
      code="""public int maximumWealth(int[][] accounts) {
    return Arrays.stream(accounts)
                 .mapToInt(row -> Arrays.stream(row).sum())
                 .max()
                 .orElse(0);
}"""),
],
}

from solutions_day02 import D2
SOLUTIONS.update(D2)
