"""Day 2 approaches (Java only). Merged into SOLUTIONS by solutions_data.py."""

D2 = {

"best-time-to-buy-and-sell-stock": [
 dict(name="Brute force: every buy/sell pair",
      idea="Try every buy day i and every later sell day j; keep the best profit.",
      time="O(n^2)", space="O(1)",
      code="""public int maxProfit(int[] prices) {
    int best = 0;
    for (int i = 0; i < prices.length; i++) {
        for (int j = i + 1; j < prices.length; j++) {
            best = Math.max(best, prices[j] - prices[i]);
        }
    }
    return best;
}"""),
 dict(name="Kadane on daily differences",
      idea="Profit of buying on i and selling on j equals the sum of daily changes between them, so it is a maximum-subarray problem on the differences.",
      time="O(n)", space="O(1)",
      code="""public int maxProfit(int[] prices) {
    int cur = 0, best = 0;
    for (int i = 1; i < prices.length; i++) {
        cur = Math.max(0, cur + prices[i] - prices[i - 1]);
        best = Math.max(best, cur);
    }
    return best;
}"""),
 dict(name="One pass: track the minimum so far (optimal)",
      idea="Sliding window of size 'best buy day so far': for each day, the best sale is today's price minus the cheapest price seen before it.",
      time="O(n)", space="O(1)", best=True,
      code="""public int maxProfit(int[] prices) {
    int minPrice = Integer.MAX_VALUE, best = 0;
    for (int p : prices) {
        minPrice = Math.min(minPrice, p);
        best = Math.max(best, p - minPrice);
    }
    return best;
}"""),
],

"container-with-most-water": [
 dict(name="Brute force: every pair of lines",
      idea="Area = width x the shorter line. Try all pairs.",
      time="O(n^2)", space="O(1)",
      code="""public int maxArea(int[] height) {
    int best = 0;
    for (int i = 0; i < height.length; i++) {
        for (int j = i + 1; j < height.length; j++) {
            best = Math.max(best, (j - i) * Math.min(height[i], height[j]));
        }
    }
    return best;
}"""),
 dict(name="Two pointers from both ends (optimal)",
      idea="Start with the widest container. The shorter line limits the area, so moving the taller one can never help; always move the shorter one inward.",
      time="O(n)", space="O(1)", best=True,
      code="""public int maxArea(int[] height) {
    int l = 0, r = height.length - 1, best = 0;
    while (l < r) {
        best = Math.max(best, (r - l) * Math.min(height[l], height[r]));
        if (height[l] < height[r]) l++;
        else r--;
    }
    return best;
}"""),
],

"3sum": [
 dict(name="Brute force: every triplet + set to remove duplicates",
      idea="Check all triplets; sort each found triplet and store it in a Set so duplicates collapse.",
      time="O(n^3)", space="O(k) for k answers",
      code="""public List<List<Integer>> threeSum(int[] nums) {
    Set<List<Integer>> found = new HashSet<>();
    int n = nums.length;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            for (int k = j + 1; k < n; k++)
                if (nums[i] + nums[j] + nums[k] == 0) {
                    List<Integer> t = Arrays.asList(nums[i], nums[j], nums[k]);
                    Collections.sort(t);
                    found.add(t);
                }
    return new ArrayList<>(found);
}"""),
 dict(name="Fix one number + HashSet Two Sum",
      idea="For each i, run Two Sum (target -nums[i]) on the rest with a HashSet. Sorting first lets us skip duplicate values of i.",
      time="O(n^2)", space="O(n)",
      code="""public List<List<Integer>> threeSum(int[] nums) {
    Arrays.sort(nums);
    Set<List<Integer>> found = new HashSet<>();
    for (int i = 0; i < nums.length - 2; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        Set<Integer> seen = new HashSet<>();
        for (int j = i + 1; j < nums.length; j++) {
            int need = -nums[i] - nums[j];
            if (seen.contains(need)) found.add(Arrays.asList(nums[i], need, nums[j]));
            seen.add(nums[j]);
        }
    }
    return new ArrayList<>(found);
}"""),
 dict(name="Sort + two pointers (optimal)",
      idea="Sort. Fix nums[i], then two pointers on the right part look for a pair summing to -nums[i]. Skip equal values to avoid duplicate triplets without any Set.",
      time="O(n^2)", space="O(log n) sort stack", best=True,
      code="""public List<List<Integer>> threeSum(int[] nums) {
    Arrays.sort(nums);
    List<List<Integer>> res = new ArrayList<>();
    for (int i = 0; i < nums.length - 2; i++) {
        if (nums[i] > 0) break;                          // smallest is positive: no more answers
        if (i > 0 && nums[i] == nums[i - 1]) continue;   // skip duplicate first numbers
        int l = i + 1, r = nums.length - 1;
        while (l < r) {
            int sum = nums[i] + nums[l] + nums[r];
            if (sum == 0) {
                res.add(Arrays.asList(nums[i], nums[l], nums[r]));
                while (l < r && nums[l] == nums[l + 1]) l++;
                while (l < r && nums[r] == nums[r - 1]) r--;
                l++;
                r--;
            } else if (sum < 0) l++;
            else r--;
        }
    }
    return res;
}"""),
],

"longest-substring-without-repeating-characters": [
 dict(name="Brute force: grow from every start",
      idea="From each start index, extend while characters stay unique (tracked in a Set).",
      time="O(n^2)", space="O(min(n, charset))",
      code="""public int lengthOfLongestSubstring(String s) {
    int best = 0;
    for (int i = 0; i < s.length(); i++) {
        Set<Character> seen = new HashSet<>();
        for (int j = i; j < s.length() && seen.add(s.charAt(j)); j++) {
            best = Math.max(best, j - i + 1);
        }
    }
    return best;
}"""),
 dict(name="Sliding window + HashSet",
      idea="Expand right; while the new char is already in the window, remove from the left.",
      time="O(n)", space="O(min(n, charset))",
      code="""public int lengthOfLongestSubstring(String s) {
    Set<Character> window = new HashSet<>();
    int l = 0, best = 0;
    for (int r = 0; r < s.length(); r++) {
        while (!window.add(s.charAt(r))) {
            window.remove(s.charAt(l++));
        }
        best = Math.max(best, r - l + 1);
    }
    return best;
}"""),
 dict(name="Sliding window + last-seen index (optimal)",
      idea="Remember where each char was last seen; on a repeat, jump the left edge straight past it instead of shrinking one step at a time.",
      time="O(n)", space="O(1) (128-slot array)", best=True,
      code="""public int lengthOfLongestSubstring(String s) {
    int[] last = new int[128];
    Arrays.fill(last, -1);
    int l = 0, best = 0;
    for (int r = 0; r < s.length(); r++) {
        char c = s.charAt(r);
        if (last[c] >= l) l = last[c] + 1;
        last[c] = r;
        best = Math.max(best, r - l + 1);
    }
    return best;
}"""),
],

"maximum-subarray": [
 dict(name="Brute force: every subarray with running sum",
      idea="For each start, extend the end and keep a running sum.",
      time="O(n^2)", space="O(1)",
      code="""public int maxSubArray(int[] nums) {
    int best = Integer.MIN_VALUE;
    for (int i = 0; i < nums.length; i++) {
        int sum = 0;
        for (int j = i; j < nums.length; j++) {
            sum += nums[j];
            best = Math.max(best, sum);
        }
    }
    return best;
}"""),
 dict(name="Divide and conquer",
      idea="Best subarray is entirely in the left half, entirely in the right half, or crosses the middle (best suffix of left + best prefix of right).",
      time="O(n log n)", space="O(log n) recursion",
      code="""public int maxSubArray(int[] nums) {
    return solve(nums, 0, nums.length - 1);
}
private int solve(int[] a, int lo, int hi) {
    if (lo == hi) return a[lo];
    int mid = lo + (hi - lo) / 2;
    int leftBest = Integer.MIN_VALUE, sum = 0;
    for (int i = mid; i >= lo; i--) { sum += a[i]; leftBest = Math.max(leftBest, sum); }
    int rightBest = Integer.MIN_VALUE; sum = 0;
    for (int i = mid + 1; i <= hi; i++) { sum += a[i]; rightBest = Math.max(rightBest, sum); }
    int cross = leftBest + rightBest;
    return Math.max(cross, Math.max(solve(a, lo, mid), solve(a, mid + 1, hi)));
}"""),
 dict(name="Prefix sums: subtract the smallest earlier prefix",
      idea="Sum(i..j) = prefix[j+1] - prefix[i]. For each end, subtract the minimum prefix seen so far.",
      time="O(n)", space="O(1)",
      code="""public int maxSubArray(int[] nums) {
    int prefix = 0, minPrefix = 0, best = Integer.MIN_VALUE;
    for (int x : nums) {
        prefix += x;
        best = Math.max(best, prefix - minPrefix);
        minPrefix = Math.min(minPrefix, prefix);
    }
    return best;
}"""),
 dict(name="Kadane's algorithm (optimal)",
      idea="At each element either extend the previous subarray or start fresh here: cur = max(x, cur + x).",
      time="O(n)", space="O(1)", best=True,
      code="""public int maxSubArray(int[] nums) {
    int cur = nums[0], best = nums[0];
    for (int i = 1; i < nums.length; i++) {
        cur = Math.max(nums[i], cur + nums[i]);
        best = Math.max(best, cur);
    }
    return best;
}"""),
],

"product-of-array-except-self": [
 dict(name="Brute force: multiply all others",
      idea="For each index multiply every other element. (Division is not allowed by the problem and breaks on zeros.)",
      time="O(n^2)", space="O(1) besides output",
      code="""public int[] productExceptSelf(int[] nums) {
    int n = nums.length;
    int[] out = new int[n];
    for (int i = 0; i < n; i++) {
        int p = 1;
        for (int j = 0; j < n; j++) if (j != i) p *= nums[j];
        out[i] = p;
    }
    return out;
}"""),
 dict(name="Prefix and suffix product arrays",
      idea="answer[i] = (product of everything left of i) x (product of everything right of i).",
      time="O(n)", space="O(n)",
      code="""public int[] productExceptSelf(int[] nums) {
    int n = nums.length;
    int[] left = new int[n], right = new int[n], out = new int[n];
    left[0] = 1;
    for (int i = 1; i < n; i++) left[i] = left[i - 1] * nums[i - 1];
    right[n - 1] = 1;
    for (int i = n - 2; i >= 0; i--) right[i] = right[i + 1] * nums[i + 1];
    for (int i = 0; i < n; i++) out[i] = left[i] * right[i];
    return out;
}"""),
 dict(name="Prefix in output, suffix in one variable (optimal)",
      idea="Store left products directly in the output array, then sweep from the right multiplying by a running suffix product.",
      time="O(n)", space="O(1) besides output", best=True,
      code="""public int[] productExceptSelf(int[] nums) {
    int n = nums.length;
    int[] out = new int[n];
    out[0] = 1;
    for (int i = 1; i < n; i++) out[i] = out[i - 1] * nums[i - 1];
    int suffix = 1;
    for (int i = n - 1; i >= 0; i--) {
        out[i] *= suffix;
        suffix *= nums[i];
    }
    return out;
}"""),
],

"minimum-window-substring": [
 dict(name="Brute force: grow from every start",
      idea="From each start, extend until the window covers t (count of still-missing chars hits 0); keep the shortest.",
      time="O(n^2)", space="O(1) (128-slot arrays)",
      code="""public String minWindow(String s, String t) {
    int[] need = new int[128];
    for (char c : t.toCharArray()) need[c]++;
    int bestLen = Integer.MAX_VALUE, bestStart = 0;
    for (int i = 0; i < s.length(); i++) {
        int[] have = new int[128];
        int missing = t.length();
        for (int j = i; j < s.length(); j++) {
            char c = s.charAt(j);
            if (have[c]++ < need[c]) missing--;
            if (missing == 0) {
                if (j - i + 1 < bestLen) { bestLen = j - i + 1; bestStart = i; }
                break;
            }
        }
    }
    return bestLen == Integer.MAX_VALUE ? "" : s.substring(bestStart, bestStart + bestLen);
}"""),
 dict(name="Sliding window with counts (optimal)",
      idea="Expand right until every needed char is covered, then shrink from the left while it stays covered, recording the smallest window.",
      time="O(|s| + |t|)", space="O(1) (128-slot array)", best=True,
      code="""public String minWindow(String s, String t) {
    int[] need = new int[128];
    for (char c : t.toCharArray()) need[c]++;
    int missing = t.length(), l = 0, bestLen = Integer.MAX_VALUE, bestStart = 0;
    for (int r = 0; r < s.length(); r++) {
        if (need[s.charAt(r)]-- > 0) missing--;          // this char was still needed
        while (missing == 0) {                           // window covers t: try to shrink
            if (r - l + 1 < bestLen) { bestLen = r - l + 1; bestStart = l; }
            if (++need[s.charAt(l++)] > 0) missing++;    // removed a needed char
        }
    }
    return bestLen == Integer.MAX_VALUE ? "" : s.substring(bestStart, bestStart + bestLen);
}"""),
],

"trapping-rain-water": [
 dict(name="Brute force: scan left and right for each bar",
      idea="Water above bar i = min(tallest on its left, tallest on its right) - height[i].",
      time="O(n^2)", space="O(1)",
      code="""public int trap(int[] height) {
    int water = 0;
    for (int i = 0; i < height.length; i++) {
        int leftMax = 0, rightMax = 0;
        for (int j = i; j >= 0; j--) leftMax = Math.max(leftMax, height[j]);
        for (int j = i; j < height.length; j++) rightMax = Math.max(rightMax, height[j]);
        water += Math.min(leftMax, rightMax) - height[i];
    }
    return water;
}"""),
 dict(name="Prefix max + suffix max arrays",
      idea="Precompute the tallest bar to the left and right of every index once.",
      time="O(n)", space="O(n)",
      code="""public int trap(int[] height) {
    int n = height.length;
    if (n == 0) return 0;
    int[] leftMax = new int[n], rightMax = new int[n];
    leftMax[0] = height[0];
    for (int i = 1; i < n; i++) leftMax[i] = Math.max(leftMax[i - 1], height[i]);
    rightMax[n - 1] = height[n - 1];
    for (int i = n - 2; i >= 0; i--) rightMax[i] = Math.max(rightMax[i + 1], height[i]);
    int water = 0;
    for (int i = 0; i < n; i++) water += Math.min(leftMax[i], rightMax[i]) - height[i];
    return water;
}"""),
 dict(name="Monotonic stack",
      idea="Keep a decreasing stack of indices. When a taller bar arrives, pop the bottom of a 'bowl' and add the water layer between the new bar and the bar below it on the stack.",
      time="O(n)", space="O(n)",
      code="""public int trap(int[] height) {
    Deque<Integer> st = new ArrayDeque<>();
    int water = 0;
    for (int i = 0; i < height.length; i++) {
        while (!st.isEmpty() && height[i] > height[st.peek()]) {
            int bottom = st.pop();
            if (st.isEmpty()) break;
            int left = st.peek();
            int width = i - left - 1;
            int h = Math.min(height[left], height[i]) - height[bottom];
            water += width * h;
        }
        st.push(i);
    }
    return water;
}"""),
 dict(name="Two pointers (optimal)",
      idea="Move the side with the smaller max inward: that side's water is fully decided by its own max, because the other side is at least as tall.",
      time="O(n)", space="O(1)", best=True,
      code="""public int trap(int[] height) {
    int l = 0, r = height.length - 1, leftMax = 0, rightMax = 0, water = 0;
    while (l < r) {
        if (height[l] < height[r]) {
            leftMax = Math.max(leftMax, height[l]);
            water += leftMax - height[l];
            l++;
        } else {
            rightMax = Math.max(rightMax, height[r]);
            water += rightMax - height[r];
            r--;
        }
    }
    return water;
}"""),
],

"spiral-matrix": [
 dict(name="Simulation with a visited matrix",
      idea="Walk right, down, left, up; turn whenever the next cell is outside or already visited.",
      time="O(m x n)", space="O(m x n)",
      code="""public List<Integer> spiralOrder(int[][] matrix) {
    int m = matrix.length, n = matrix[0].length;
    boolean[][] seen = new boolean[m][n];
    int[] dr = {0, 1, 0, -1}, dc = {1, 0, -1, 0};
    List<Integer> out = new ArrayList<>();
    int r = 0, c = 0, d = 0;
    for (int k = 0; k < m * n; k++) {
        out.add(matrix[r][c]);
        seen[r][c] = true;
        int nr = r + dr[d], nc = c + dc[d];
        if (nr < 0 || nr >= m || nc < 0 || nc >= n || seen[nr][nc]) {
            d = (d + 1) % 4;
            nr = r + dr[d];
            nc = c + dc[d];
        }
        r = nr;
        c = nc;
    }
    return out;
}"""),
 dict(name="Shrinking boundaries (optimal)",
      idea="Keep top, bottom, left, right walls. Walk one side, then move that wall inward. Check the walls again before the bottom row and left column so a single row/column is not repeated.",
      time="O(m x n)", space="O(1) besides output", best=True,
      code="""public List<Integer> spiralOrder(int[][] matrix) {
    List<Integer> out = new ArrayList<>();
    int top = 0, bottom = matrix.length - 1, left = 0, right = matrix[0].length - 1;
    while (top <= bottom && left <= right) {
        for (int c = left; c <= right; c++) out.add(matrix[top][c]);
        top++;
        for (int r = top; r <= bottom; r++) out.add(matrix[r][right]);
        right--;
        if (top <= bottom) {
            for (int c = right; c >= left; c--) out.add(matrix[bottom][c]);
            bottom--;
        }
        if (left <= right) {
            for (int r = bottom; r >= top; r--) out.add(matrix[r][left]);
            left++;
        }
    }
    return out;
}"""),
],

"rotate-image": [
 dict(name="Copy into a new matrix",
      idea="Cell (i, j) moves to (j, n-1-i). Fill a copy, then write it back. Simple, but the problem asks for in-place.",
      time="O(n^2)", space="O(n^2)",
      code="""public void rotate(int[][] matrix) {
    int n = matrix.length;
    int[][] copy = new int[n][n];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            copy[j][n - 1 - i] = matrix[i][j];
    for (int i = 0; i < n; i++) matrix[i] = copy[i];
}"""),
 dict(name="Rotate four cells at a time, layer by layer",
      idea="Each cell in the outer ring trades places with 3 others (top -> right -> bottom -> left). Do it ring by ring.",
      time="O(n^2)", space="O(1)",
      code="""public void rotate(int[][] matrix) {
    int n = matrix.length;
    for (int i = 0; i < n / 2; i++) {
        for (int j = i; j < n - 1 - i; j++) {
            int tmp = matrix[i][j];
            matrix[i][j] = matrix[n - 1 - j][i];
            matrix[n - 1 - j][i] = matrix[n - 1 - i][n - 1 - j];
            matrix[n - 1 - i][n - 1 - j] = matrix[j][n - 1 - i];
            matrix[j][n - 1 - i] = tmp;
        }
    }
}"""),
 dict(name="Transpose, then reverse each row (optimal, easiest to explain)",
      idea="Clockwise rotation = transpose (swap across the main diagonal) + mirror each row.",
      time="O(n^2)", space="O(1)", best=True,
      code="""public void rotate(int[][] matrix) {
    int n = matrix.length;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) {
            int t = matrix[i][j]; matrix[i][j] = matrix[j][i]; matrix[j][i] = t;
        }
    for (int[] row : matrix)
        for (int l = 0, r = n - 1; l < r; l++, r--) {
            int t = row[l]; row[l] = row[r]; row[r] = t;
        }
}"""),
],

"set-matrix-zeroes": [
 dict(name="Copy the matrix",
      idea="Read zeros from an untouched copy so newly written zeros do not spread.",
      time="O(m x n x (m + n))", space="O(m x n)",
      code="""public void setZeroes(int[][] matrix) {
    int m = matrix.length, n = matrix[0].length;
    int[][] orig = new int[m][];
    for (int i = 0; i < m; i++) orig[i] = matrix[i].clone();
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            if (orig[i][j] == 0) {
                for (int c = 0; c < n; c++) matrix[i][c] = 0;
                for (int r = 0; r < m; r++) matrix[r][j] = 0;
            }
}"""),
 dict(name="Row and column flag arrays",
      idea="First pass: mark which rows and columns contain a zero. Second pass: zero a cell if its row or column is marked.",
      time="O(m x n)", space="O(m + n)",
      code="""public void setZeroes(int[][] matrix) {
    int m = matrix.length, n = matrix[0].length;
    boolean[] row = new boolean[m], col = new boolean[n];
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            if (matrix[i][j] == 0) { row[i] = true; col[j] = true; }
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            if (row[i] || col[j]) matrix[i][j] = 0;
}"""),
 dict(name="Use the first row and column as the flags (optimal)",
      idea="Store the row/column marks inside the matrix itself. Two booleans remember whether the first row/column themselves need zeroing.",
      time="O(m x n)", space="O(1)", best=True,
      code="""public void setZeroes(int[][] matrix) {
    int m = matrix.length, n = matrix[0].length;
    boolean firstRow = false, firstCol = false;
    for (int j = 0; j < n; j++) if (matrix[0][j] == 0) firstRow = true;
    for (int i = 0; i < m; i++) if (matrix[i][0] == 0) firstCol = true;
    for (int i = 1; i < m; i++)
        for (int j = 1; j < n; j++)
            if (matrix[i][j] == 0) { matrix[i][0] = 0; matrix[0][j] = 0; }
    for (int i = 1; i < m; i++)
        for (int j = 1; j < n; j++)
            if (matrix[i][0] == 0 || matrix[0][j] == 0) matrix[i][j] = 0;
    if (firstRow) for (int j = 0; j < n; j++) matrix[0][j] = 0;
    if (firstCol) for (int i = 0; i < m; i++) matrix[i][0] = 0;
}"""),
],

"missing-number": [
 dict(name="Sort and find the gap",
      idea="After sorting, index i should hold i; the first mismatch is the answer.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public int missingNumber(int[] nums) {
    Arrays.sort(nums);
    for (int i = 0; i < nums.length; i++) if (nums[i] != i) return i;
    return nums.length;
}"""),
 dict(name="HashSet",
      idea="Put everything in a set and check 0..n.",
      time="O(n)", space="O(n)",
      code="""public int missingNumber(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    for (int x : nums) seen.add(x);
    for (int i = 0; i <= nums.length; i++) if (!seen.contains(i)) return i;
    return -1;
}"""),
 dict(name="Cyclic sort",
      idea="Swap each value v into index v (ignore v = n). The first index i with nums[i] != i is missing.",
      time="O(n)", space="O(1)",
      code="""public int missingNumber(int[] nums) {
    int n = nums.length, i = 0;
    while (i < n) {
        int v = nums[i];
        if (v < n && nums[v] != v) { nums[i] = nums[v]; nums[v] = v; }
        else i++;
    }
    for (i = 0; i < n; i++) if (nums[i] != i) return i;
    return n;
}"""),
 dict(name="Gauss sum formula",
      idea="Expected sum 0..n is n(n+1)/2; the difference with the actual sum is the missing number. Use long to be safe from overflow.",
      time="O(n)", space="O(1)",
      code="""public int missingNumber(int[] nums) {
    long n = nums.length, expected = n * (n + 1) / 2, actual = 0;
    for (int x : nums) actual += x;
    return (int) (expected - actual);
}"""),
 dict(name="XOR (optimal, no overflow risk)",
      idea="XOR all indices 0..n with all values; every present number cancels itself (a ^ a = 0), leaving the missing one.",
      time="O(n)", space="O(1)", best=True,
      code="""public int missingNumber(int[] nums) {
    int x = nums.length;
    for (int i = 0; i < nums.length; i++) x ^= i ^ nums[i];
    return x;
}"""),
],

"find-all-duplicates-in-an-array": [
 dict(name="Sort and compare neighbours",
      idea="Duplicates sit next to each other after sorting.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public List<Integer> findDuplicates(int[] nums) {
    Arrays.sort(nums);
    List<Integer> out = new ArrayList<>();
    for (int i = 1; i < nums.length; i++) if (nums[i] == nums[i - 1]) out.add(nums[i]);
    return out;
}"""),
 dict(name="HashSet",
      idea="add() returns false the second time a value appears.",
      time="O(n)", space="O(n)",
      code="""public List<Integer> findDuplicates(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    List<Integer> out = new ArrayList<>();
    for (int x : nums) if (!seen.add(x)) out.add(x);
    return out;
}"""),
 dict(name="Cyclic sort",
      idea="Swap each value v to index v-1. Afterwards, any index i not holding i+1 holds a duplicate.",
      time="O(n)", space="O(1) besides output",
      code="""public List<Integer> findDuplicates(int[] nums) {
    int i = 0;
    while (i < nums.length) {
        int home = nums[i] - 1;
        if (nums[i] != nums[home]) { int t = nums[i]; nums[i] = nums[home]; nums[home] = t; }
        else i++;
    }
    List<Integer> out = new ArrayList<>();
    for (i = 0; i < nums.length; i++) if (nums[i] != i + 1) out.add(nums[i]);
    return out;
}"""),
 dict(name="Mark visits by negating (optimal)",
      idea="Values are 1..n, so value v points at index v-1. Flip that cell negative on the first visit; if it is already negative, v is a duplicate.",
      time="O(n)", space="O(1) besides output", best=True,
      code="""public List<Integer> findDuplicates(int[] nums) {
    List<Integer> out = new ArrayList<>();
    for (int x : nums) {
        int idx = Math.abs(x) - 1;
        if (nums[idx] < 0) out.add(Math.abs(x));
        else nums[idx] = -nums[idx];
    }
    return out;
}"""),
],

"first-missing-positive": [
 dict(name="Sort and scan",
      idea="Sort, then walk positives looking for the first gap starting at 1.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public int firstMissingPositive(int[] nums) {
    Arrays.sort(nums);
    int expect = 1;
    for (int x : nums) {
        if (x == expect) expect++;
        else if (x > expect) break;
    }
    return expect;
}"""),
 dict(name="HashSet",
      idea="The answer is in 1..n+1, so check those numbers against a set.",
      time="O(n)", space="O(n)",
      code="""public int firstMissingPositive(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    for (int x : nums) seen.add(x);
    for (int k = 1; k <= nums.length + 1; k++) if (!seen.contains(k)) return k;
    return -1;
}"""),
 dict(name="Index marking with negation",
      idea="Replace values outside 1..n with n+1, then mark value v by making index v-1 negative. The first non-negative index i gives i+1.",
      time="O(n)", space="O(1)",
      code="""public int firstMissingPositive(int[] nums) {
    int n = nums.length;
    for (int i = 0; i < n; i++) if (nums[i] <= 0 || nums[i] > n) nums[i] = n + 1;
    for (int i = 0; i < n; i++) {
        int v = Math.abs(nums[i]);
        if (v <= n && nums[v - 1] > 0) nums[v - 1] = -nums[v - 1];
    }
    for (int i = 0; i < n; i++) if (nums[i] > 0) return i + 1;
    return n + 1;
}"""),
 dict(name="Cyclic sort (optimal)",
      idea="Put every value v in 1..n at index v-1 by swapping. The first index i that does not hold i+1 is the answer.",
      time="O(n)", space="O(1)", best=True,
      code="""public int firstMissingPositive(int[] nums) {
    int n = nums.length, i = 0;
    while (i < n) {
        int v = nums[i];
        if (v >= 1 && v <= n && nums[v - 1] != v) { nums[i] = nums[v - 1]; nums[v - 1] = v; }
        else i++;
    }
    for (i = 0; i < n; i++) if (nums[i] != i + 1) return i + 1;
    return n + 1;
}"""),
],
}
