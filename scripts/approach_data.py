"""How to approach questions: per pattern (playbook with Java template) and per day/topic."""

# name -> dict(steps, template, pitfalls, complexity)
PLAYBOOK = {
"Two pointers": dict(
  steps=["Check the input is sorted (or can be sorted without losing what you need).",
         "Place pointers: both ends for pair sums; same side (slow/fast) for in-place removal.",
         "Compare the current pair with the target and move the pointer that brings you closer.",
         "For triplets, fix one element in a loop and run two pointers on the rest; skip duplicates."],
  template="""int l = 0, r = a.length - 1;
while (l < r) {
    int sum = a[l] + a[r];
    if (sum == target) return new int[]{l, r};
    if (sum < target) l++; else r--;
}""",
  pitfalls="Forgetting to skip duplicates in 3Sum; using two pointers on an unsorted array.",
  complexity="O(n) after an O(n log n) sort; O(1) extra space."),
"Sliding window": dict(
  steps=["Confirm the answer is a contiguous subarray/substring.",
         "Expand the right edge one step at a time and add the new element to the window state (sum or count map).",
         "While the window breaks the rule, shrink from the left and remove that element from the state.",
         "Update the answer at the point where the window is valid (longest: after shrinking; shortest: while shrinking)."],
  template="""Map<Character, Integer> cnt = new HashMap<>();
int l = 0, best = 0;
for (int r = 0; r < s.length(); r++) {
    cnt.merge(s.charAt(r), 1, Integer::sum);
    while (/* window invalid */ cnt.get(s.charAt(r)) > 1) {
        cnt.merge(s.charAt(l), -1, Integer::sum);
        l++;
    }
    best = Math.max(best, r - l + 1);
}""",
  pitfalls="Using sliding window with negative numbers (use prefix sums instead); updating the answer before the window is valid.",
  complexity="O(n): each index enters and leaves the window once."),
"Fast & slow pointers": dict(
  steps=["Use when a linked list or a 'next value' function may contain a cycle, or you need the middle.",
         "Move slow by 1 and fast by 2.",
         "If they meet there is a cycle; reset one pointer to head and move both by 1 to find the cycle start.",
         "For the middle, stop when fast reaches the end; slow is the middle."],
  template="""ListNode slow = head, fast = head;
while (fast != null && fast.next != null) {
    slow = slow.next;
    fast = fast.next.next;
    if (slow == fast) {               // cycle found
        slow = head;
        while (slow != fast) { slow = slow.next; fast = fast.next; }
        return slow;                  // cycle start
    }
}
return null;""",
  pitfalls="Not checking fast.next before fast.next.next (NullPointerException).",
  complexity="O(n) time, O(1) space."),
"Prefix sum + hash map": dict(
  steps=["Look for 'number of subarrays with sum/xor/count = k' (works with negative numbers).",
         "Keep a running prefix and a map from prefix value to how many times you have seen it.",
         "At each index add map[prefix - k] to the answer, then record the current prefix.",
         "Seed the map with prefix 0 seen once (the empty prefix)."],
  template="""Map<Integer, Integer> seen = new HashMap<>();
seen.put(0, 1);
int prefix = 0, count = 0;
for (int x : nums) {
    prefix += x;
    count += seen.getOrDefault(prefix - k, 0);
    seen.merge(prefix, 1, Integer::sum);
}""",
  pitfalls="Forgetting seen.put(0, 1); recording the prefix before reading the map.",
  complexity="O(n) time and space."),
"Cyclic sort": dict(
  steps=["Signal: values are in the range 1..n (or 0..n) and you need missing or duplicate numbers.",
         "Swap each value into its home index (value v belongs at index v - 1) until the current slot is correct or the swap would repeat.",
         "Scan once more: any index i that does not hold i + 1 reveals a missing/duplicate number."],
  template="""int i = 0;
while (i < n) {
    int home = a[i] - 1;
    if (a[i] > 0 && a[i] <= n && a[i] != a[home]) {
        int t = a[i]; a[i] = a[home]; a[home] = t;
    } else i++;
}
for (i = 0; i < n; i++) if (a[i] != i + 1) return i + 1;
return n + 1;""",
  pitfalls="Infinite loop when swapping duplicates (check a[i] != a[home], not i != home).",
  complexity="O(n) time, O(1) space."),
"Merge intervals": dict(
  steps=["Sort intervals by start time.",
         "Walk through them keeping the last merged interval.",
         "If the next one overlaps (start <= last end), extend last end = max(last end, end); otherwise start a new one.",
         "For 'maximum non-overlapping' sort by END instead and greedily keep the earliest-ending."],
  template="""Arrays.sort(iv, (x, y) -> Integer.compare(x[0], y[0]));
List<int[]> out = new ArrayList<>();
for (int[] cur : iv) {
    if (out.isEmpty() || out.get(out.size() - 1)[1] < cur[0]) out.add(cur);
    else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);
}
return out.toArray(new int[0][]);""",
  pitfalls="Using a - b in comparators (overflow); deciding whether touching intervals count as overlapping.",
  complexity="O(n log n) for the sort."),
"In-place list reversal": dict(
  steps=["Use a dummy node if the head can change.",
         "Walk to the node before the part to reverse.",
         "Reverse with prev/cur/next pointers, then reconnect both ends."],
  template="""ListNode prev = null, cur = head;
while (cur != null) {
    ListNode next = cur.next;
    cur.next = prev;
    prev = cur;
    cur = next;
}
return prev;""",
  pitfalls="Losing the rest of the list (save next before re-pointing); forgetting to reconnect the reversed part.",
  complexity="O(n) time, O(1) space."),
"Monotonic stack/deque": dict(
  steps=["Signal: 'next greater/smaller element', spans, or the max/min of every window.",
         "Keep indices on a stack whose values are increasing or decreasing.",
         "When the new element breaks the order, pop: each popped index has found its answer (the new element).",
         "For window max, use a deque and also drop indices that slide out of the window from the front."],
  template="""int[] ans = new int[n];
Deque<Integer> st = new ArrayDeque<>();   // indices, decreasing temps
for (int i = 0; i < n; i++) {
    while (!st.isEmpty() && t[i] > t[st.peek()]) {
        int j = st.pop();
        ans[j] = i - j;
    }
    st.push(i);
}""",
  pitfalls="Storing values instead of indices (you lose distances); choosing the wrong comparison for duplicates.",
  complexity="O(n): each index is pushed and popped once."),
"Tree DFS / BFS": dict(
  steps=["Decide what one call returns for a subtree (height, sum, is-valid, etc.).",
         "Write the base case for null.",
         "Combine left and right results; update a global answer if the best path can bend through the node.",
         "Use BFS with queue.size() per level when the question says 'level', 'depth by depth' or 'right side view'."],
  template="""int best = 0;
int depth(TreeNode node) {
    if (node == null) return 0;
    int l = depth(node.left), r = depth(node.right);
    best = Math.max(best, l + r);      // diameter through this node
    return 1 + Math.max(l, r);
}""",
  pitfalls="Mixing up what you return vs what you record globally; deep recursion on skewed trees (stack overflow).",
  complexity="O(n) time; O(h) stack space."),
"Graph BFS / DFS": dict(
  steps=["Build the graph: adjacency list from edges, or treat each grid cell as a node.",
         "Pick BFS for shortest path in steps; DFS for reachability, components or cycle checks.",
         "Mark nodes visited when you push/enqueue them.",
         "For several starting points (multi-source), enqueue all of them first."],
  template="""Deque<int[]> q = new ArrayDeque<>();
q.offer(new int[]{sr, sc}); seen[sr][sc] = true;
int steps = 0;
int[][] dirs = {{1,0},{-1,0},{0,1},{0,-1}};
while (!q.isEmpty()) {
    for (int size = q.size(); size > 0; size--) {
        int[] c = q.poll();
        if (c[0] == tr && c[1] == tc) return steps;
        for (int[] d : dirs) {
            int r = c[0] + d[0], col = c[1] + d[1];
            if (r < 0 || col < 0 || r >= R || col >= C || seen[r][col] || grid[r][col] == '#') continue;
            seen[r][col] = true; q.offer(new int[]{r, col});
        }
    }
    steps++;
}
return -1;""",
  pitfalls="Marking visited on dequeue (nodes get added many times); forgetting disconnected components.",
  complexity="O(V + E)."),
"Topological sort": dict(
  steps=["Signal: tasks with prerequisites, ordering, or 'detect a cycle in a directed graph'.",
         "Build adjacency list and in-degree counts.",
         "Queue every node with in-degree 0; pop, add to order, decrement neighbours' in-degree, enqueue those that hit 0.",
         "If the order has fewer than n nodes, there is a cycle."],
  template="""int[] indeg = new int[n];
List<List<Integer>> g = new ArrayList<>();
for (int i = 0; i < n; i++) g.add(new ArrayList<>());
for (int[] e : pre) { g.get(e[1]).add(e[0]); indeg[e[0]]++; }
Deque<Integer> q = new ArrayDeque<>();
for (int i = 0; i < n; i++) if (indeg[i] == 0) q.offer(i);
List<Integer> order = new ArrayList<>();
while (!q.isEmpty()) {
    int u = q.poll(); order.add(u);
    for (int v : g.get(u)) if (--indeg[v] == 0) q.offer(v);
}
return order.size() == n;   // false => cycle""",
  pitfalls="Reversing the edge direction for prerequisites [a, b] (b comes before a).",
  complexity="O(V + E)."),
"Union-Find": dict(
  steps=["Signal: groups that merge over time, 'are these connected?', counting components, redundant edge.",
         "Start with each node as its own parent.",
         "union(a, b) joins the roots; find(x) follows parents with path compression.",
         "If union finds both already in the same set, that edge creates a cycle."],
  template="""int[] parent, rank;
int find(int x) { return parent[x] == x ? x : (parent[x] = find(parent[x])); }
boolean union(int a, int b) {
    int ra = find(a), rb = find(b);
    if (ra == rb) return false;
    if (rank[ra] < rank[rb]) { int t = ra; ra = rb; rb = t; }
    parent[rb] = ra;
    if (rank[ra] == rank[rb]) rank[ra]++;
    return true;
}""",
  pitfalls="Comparing parent[a] == parent[b] instead of find(a) == find(b).",
  complexity="Almost O(1) per operation (inverse Ackermann)."),
"Two heaps": dict(
  steps=["Signal: median of a stream, or balancing a lower half and an upper half.",
         "Max-heap holds the lower half, min-heap the upper half.",
         "Add to the lower heap, move its top to the upper heap, then rebalance so lower has equal or one more element.",
         "Median is lower.peek() (odd count) or the average of both tops."],
  template="""PriorityQueue<Integer> lo = new PriorityQueue<>(Collections.reverseOrder());
PriorityQueue<Integer> hi = new PriorityQueue<>();
void add(int x) {
    lo.offer(x);
    hi.offer(lo.poll());
    if (hi.size() > lo.size()) lo.offer(hi.poll());
}
double median() {
    return lo.size() > hi.size() ? lo.peek() : (lo.peek() + (long) hi.peek()) / 2.0;
}""",
  pitfalls="Integer overflow when adding the two tops; forgetting to rebalance.",
  complexity="O(log n) add, O(1) median."),
"Top-K / K-way merge": dict(
  steps=["For 'K largest', keep a MIN-heap of size K; pop when it exceeds K.",
         "For 'K smallest/closest', keep a MAX-heap of size K.",
         "For merging K sorted lists, push the head of each list; pop the smallest and push its successor."],
  template="""PriorityQueue<ListNode> pq = new PriorityQueue<>((a, b) -> Integer.compare(a.val, b.val));
for (ListNode h : lists) if (h != null) pq.offer(h);
ListNode dummy = new ListNode(0), tail = dummy;
while (!pq.isEmpty()) {
    ListNode n = pq.poll();
    tail.next = n; tail = n;
    if (n.next != null) pq.offer(n.next);
}
return dummy.next;""",
  pitfalls="Using the wrong heap direction; sorting everything (O(n log n)) when O(n log K) is expected.",
  complexity="O(n log K)."),
"Modified binary search": dict(
  steps=["Signal: sorted/rotated data, or 'minimum X such that condition holds' where the condition is monotonic.",
         "Define the search range [lo, hi] of possible answers.",
         "Write a check(mid) that is false...false, true...true across the range.",
         "Use the lower-bound template so the loop ends exactly at the first true."],
  template="""int lo = 1, hi = maxPile;           // answer range
while (lo < hi) {
    int mid = lo + (hi - lo) / 2;
    if (canFinish(mid)) hi = mid;      // mid works, try smaller
    else lo = mid + 1;
}
return lo;""",
  pitfalls="Infinite loops from mixing lo <= hi with hi = mid; overflow in (lo + hi) / 2.",
  complexity="O(log range x cost of check)."),
"Backtracking": dict(
  steps=["Draw the decision tree: what choice is made at each level?",
         "Recurse with the partial path; when it is complete, copy it into the result.",
         "Undo the last choice after returning (backtrack).",
         "Prune branches that can no longer lead to a valid answer."],
  template="""void dfs(int start, List<Integer> path) {
    res.add(new ArrayList<>(path));            // subsets: record every node
    for (int i = start; i < nums.length; i++) {
        if (i > start && nums[i] == nums[i - 1]) continue;   // skip dupes (sorted)
        path.add(nums[i]);
        dfs(i + 1, path);
        path.remove(path.size() - 1);          // undo
    }
}""",
  pitfalls="Adding the path itself instead of a copy; forgetting to undo the choice.",
  complexity="Exponential: O(2^n) subsets, O(n!) permutations."),
"Dynamic programming": dict(
  steps=["Write a brute-force recursion that tries every choice.",
         "Identify the state: the minimum arguments that describe a subproblem (index, remaining capacity, ...).",
         "Write the transition (how a state uses smaller states) and the base cases.",
         "Add memoisation; then convert to a bottom-up table if needed and shrink space."],
  template="""// Coin change: fewest coins to make amount
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1);
dp[0] = 0;
for (int a = 1; a <= amount; a++)
    for (int c : coins)
        if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
return dp[amount] > amount ? -1 : dp[amount];""",
  pitfalls="Wrong iteration order (0/1 knapsack must loop capacity backwards); using Integer.MAX_VALUE then adding 1 (overflow).",
  complexity="Number of states x cost per transition."),
"Greedy": dict(
  steps=["Find a natural order (sort by end time, by ratio, by deadline).",
         "Make the locally best choice and never undo it.",
         "Convince yourself with an exchange argument; if a counter-example exists, switch to DP."],
  template="""Arrays.sort(iv, (x, y) -> Integer.compare(x[1], y[1]));   // by end
int kept = 0, end = Integer.MIN_VALUE;
for (int[] cur : iv) {
    if (cur[0] >= end) { kept++; end = cur[1]; }
}
return iv.length - kept;   // removals for non-overlapping""",
  pitfalls="Assuming greedy works without checking a counter-example (e.g. coins {1, 3, 4} for 6).",
  complexity="Usually O(n log n) for the sort."),
"Trie": dict(
  steps=["Signal: many words share prefixes; prefix search; autocomplete; searching many words in a grid.",
         "Each node has children[26] and an end-of-word flag (or the word itself).",
         "Insert and search walk one character per level.",
         "For grid word search, DFS on the board while walking the trie; prune finished branches."],
  template="""class Node { Node[] next = new Node[26]; boolean end; }
Node root = new Node();
void insert(String w) {
    Node cur = root;
    for (char ch : w.toCharArray()) {
        int i = ch - 'a';
        if (cur.next[i] == null) cur.next[i] = new Node();
        cur = cur.next[i];
    }
    cur.end = true;
}""",
  pitfalls="Returning true for a prefix when a full word was asked (check the end flag).",
  complexity="O(length of word) per operation."),
"Bit manipulation": dict(
  steps=["Signal: 'appears once while others appear twice', subsets with n <= 20, powers of two, flags.",
         "Remember the core tricks: a ^ a = 0, x & (x - 1) clears the lowest set bit, x & -x isolates it.",
         "Use a mask from 0 to (1 << n) - 1 to enumerate every subset."],
  template="""for (int mask = 0; mask < (1 << n); mask++) {
    List<Integer> subset = new ArrayList<>();
    for (int i = 0; i < n; i++)
        if ((mask & (1 << i)) != 0) subset.add(nums[i]);
}
int single = 0; for (int x : nums) single ^= x;""",
  pitfalls="Operator precedence: always bracket (mask & (1 << i)) != 0; >> vs >>> for negative numbers.",
  complexity="O(2^n x n) for subset enumeration."),
}

# Per-day "how to approach questions in this topic"
DAY_APPROACH = {
 1: ["Before coding, state input size n and the target complexity: n <= 10^5 needs O(n log n) or better.",
     "Pick the collection by operation: lookup -> HashMap/HashSet, ordered -> TreeMap, FIFO -> ArrayDeque.",
     "Finish every answer by stating time and space complexity."],
 2: ["Ask: contiguous? -> sliding window or prefix sums. Sorted / pairs? -> two pointers.",
     "Try the O(n^2) brute force out loud, then remove the inner loop with a pointer, window or map.",
     "Matrices: walk with boundaries (top, bottom, left, right) and shrink them; for in-place, use the first row/column as markers.",
     "Numbers in 1..n -> cyclic sort or index marking."],
 3: ["Whenever you need 'have I seen this?' or 'how many times?', reach for a HashMap/HashSet.",
     "For grouping, design a canonical key (sorted string, count signature).",
     "If you need order as well, consider LinkedHashMap or TreeMap."],
 4: ["Draw the recursion tree for a tiny input first.",
     "Define what one call is responsible for, then the base case.",
     "Use the choose / explore / un-choose template and prune invalid branches early."],
 5: ["Sorted input or a monotonic yes/no condition -> binary search.",
     "Write the check function first, then the lower-bound loop.",
     "Kth largest/smallest -> heap (O(n log k)) or quickselect (average O(n))."],
 6: ["Add a dummy node whenever the head may change.",
     "Middle / cycle / kth from end -> fast and slow pointers.",
     "Draw 3-4 boxes with arrows on paper before re-pointing anything."],
 7: ["Matching brackets or 'undo' behaviour -> stack.",
     "'Next greater/smaller' or 'span' -> monotonic stack of indices.",
     "Window maximum -> monotonic deque. Level-by-level -> queue."],
 8: ["Decide what each call returns for its subtree and whether you also need a global answer.",
     "Level-based wording -> BFS with queue size per level.",
     "Path problems: compute best downward path, update global with left + right through the node."],
 9: ["Use the BST property to discard half the tree at each step.",
     "Inorder traversal gives sorted order: kth smallest, validate, convert.",
     "In Java, floor/ceiling queries -> TreeMap/TreeSet instead of writing a BST."],
 10: ["K largest -> min-heap of size K; K smallest/closest -> max-heap of size K.",
      "Merging sorted sources -> heap of the current head of each source.",
      "Median or two halves -> two heaps; scheduling -> heap of next available time."],
 11: ["Many words + prefix queries -> trie.",
      "Find a pattern in text -> KMP or Rabin-Karp; for interviews indexOf is fine unless asked to implement.",
      "Palindromes -> expand around each centre (2n - 1 centres)."],
 12: ["First identify nodes and edges; grids are graphs with 4 neighbours.",
      "Fewest steps -> BFS. Reachability / components -> DFS or BFS. Ordering with prerequisites -> topological sort.",
      "Mark visited when you enqueue."],
 13: ["Weighted shortest path, non-negative -> Dijkstra. Negative edges or 'at most k stops' -> Bellman-Ford.",
      "Connecting all nodes at minimum cost -> MST (Kruskal with DSU).",
      "Dynamic connectivity or cycle in undirected graph -> Union-Find."],
 14: ["For design-a-data-structure questions, list each operation and its required complexity first.",
      "Combine structures: HashMap for lookup + list/heap/tree for order.",
      "Write the API signatures, then implement one method at a time with tests."],
 15: ["Intervals: sort by start to merge, by end to maximise non-overlapping.",
      "Try a counter-example before trusting greedy.",
      "Reachability like Jump Game: track the farthest index you can reach."],
 16: ["Signals for DP: 'number of ways', 'min/max cost', 'can you reach', with overlapping choices.",
      "Write recursion -> memo -> table -> space-optimised.",
      "Knapsack-type: for each item decide take / skip; mind the loop direction."],
 17: ["Two strings -> dp[i][j] over prefixes; one grid -> dp[r][c] from top/left.",
      "Fill a tiny table by hand to find the transition.",
      "State machine for stock problems: states = holding / not holding / cooldown."],
 18: ["Interval DP: dp[l][r] over lengths from small to large; try every split point.",
      "n <= 20 and 'visit all' -> bitmask DP over subsets.",
      "Math: use long and % MOD after every multiply; gcd via Euclid; primes via sieve.",
      "Random: reservoir sampling for streams, prefix sums + binary search for weighted picks."],
 19: ["Static array, many range queries -> prefix sums or sparse table.",
      "Updates + range queries -> Fenwick tree (sums) or segment tree (min/max/sum).",
      "Counting smaller elements -> Fenwick over compressed values, or merge sort."],
 20: ["Critical edges/nodes -> Tarjan low-link values.",
      "Two-colouring -> BFS with colours; odd cycle means not bipartite.",
      "Use every edge exactly once -> Eulerian path (Hierholzer)."],
 21: ["Contest order: read all, solve the easiest first, cap each problem at 20 minutes before moving on.",
      "For every miss, write the pattern you failed to spot in your mistake log."],
 22: ["LLD round: clarify requirements and actors, list entities, define relationships.",
      "Draw the class diagram, then code the core classes and one key flow.",
      "Point out where patterns give extensibility (Strategy for pricing, Observer for notifications)."],
 23: ["Identify shared mutable state first; protect it or make it immutable.",
      "Prefer high-level tools (ConcurrentHashMap, ExecutorService, BlockingQueue) over raw locks.",
      "Talk about deadlock, starvation and how you would test concurrency."],
 24: ["Always open with requirements and back-of-envelope numbers.",
      "Draw client -> load balancer -> stateless services -> cache -> database.",
      "For each component say why it is there and its trade-off."],
 25: ["Choose storage from access patterns, not habit.",
      "State the sharding key and how you handle hot keys and rebalancing.",
      "Explain replication mode and what happens when the leader fails."],
 26: ["Use a queue whenever work can be async or traffic is spiky.",
      "Every cross-service write: discuss idempotency, retries and the outbox pattern.",
      "Name your consistency choice and the failure you are guarding against."],
 27: ["Run the 7-step framework; spend most time on the 1-2 hardest deep dives.",
      "Use numbers to justify every scaling decision.",
      "Close with bottlenecks and what changes at 10x scale."],
 28: ["Measure before optimising: write the benchmark first.",
      "Explain your project in the same 7-step framework you use in interviews."],
 29: ["STAR: short situation, clear 'I' actions, measurable result.",
      "Map each story to 2-3 Amazon Leadership Principles."],
 30: ["Clarify -> examples -> brute force -> optimise -> code -> dry run -> complexity.",
      "Think aloud the whole time; silence is the most common reason for a weak signal."],
}
