"""Questions solvable by each pattern. Slugs already in the 30-day plan are looked up there (name, difficulty, day);
EXTRA lists classic practice questions outside the plan as (name, slug, difficulty)."""

IN_PLAN = {
 "Two pointers": ["two-sum-ii-input-array-is-sorted", "container-with-most-water", "3sum", "trapping-rain-water", "sort-colors"],
 "Sliding window": ["best-time-to-buy-and-sell-stock", "longest-substring-without-repeating-characters", "minimum-window-substring", "sliding-window-maximum"],
 "Fast & slow pointers": ["linked-list-cycle", "remove-nth-node-from-end-of-list", "reorder-list"],
 "Prefix sum + hash map": ["two-sum", "subarray-sum-equals-k", "product-of-array-except-self", "range-sum-query-2d-immutable", "count-of-range-sum"],
 "Cyclic sort": ["missing-number", "find-all-duplicates-in-an-array", "first-missing-positive"],
 "Merge intervals": ["merge-intervals", "insert-interval", "non-overlapping-intervals", "minimum-number-of-arrows-to-burst-balloons", "partition-labels", "my-calendar-i", "my-calendar-iii"],
 "In-place list reversal": ["reverse-linked-list", "reorder-list", "reverse-nodes-in-k-group"],
 "Monotonic stack/deque": ["daily-temperatures", "largest-rectangle-in-histogram", "sliding-window-maximum", "trapping-rain-water", "min-stack", "valid-parentheses", "evaluate-reverse-polish-notation"],
 "Tree DFS / BFS": ["maximum-depth-of-binary-tree", "invert-binary-tree", "diameter-of-binary-tree", "binary-tree-level-order-traversal", "binary-tree-right-side-view",
                    "lowest-common-ancestor-of-a-binary-tree", "binary-tree-maximum-path-sum", "serialize-and-deserialize-binary-tree", "validate-binary-search-tree",
                    "kth-smallest-element-in-a-bst", "lowest-common-ancestor-of-a-binary-search-tree", "delete-node-in-a-bst", "convert-sorted-array-to-binary-search-tree", "house-robber-iii"],
 "Graph BFS / DFS": ["number-of-islands", "clone-graph", "rotting-oranges", "pacific-atlantic-water-flow", "surrounded-regions", "open-the-lock", "word-ladder",
                     "is-graph-bipartite", "bus-routes", "shortest-path-visiting-all-nodes", "reconstruct-itinerary", "critical-connections-in-a-network"],
 "Topological sort": ["course-schedule", "course-schedule-ii", "verifying-an-alien-dictionary", "longest-increasing-path-in-a-matrix"],
 "Union-Find": ["number-of-provinces", "redundant-connection", "min-cost-to-connect-all-points", "number-of-islands", "swim-in-rising-water", "path-with-minimum-effort"],
 "Two heaps": ["find-median-from-data-stream"],
 "Top-K / K-way merge": ["kth-largest-element-in-an-array", "top-k-frequent-elements", "kth-largest-element-in-a-stream", "last-stone-weight", "k-closest-points-to-origin",
                         "task-scheduler", "merge-k-sorted-lists", "network-delay-time", "cheapest-flights-within-k-stops", "design-twitter"],
 "Modified binary search": ["binary-search", "search-in-rotated-sorted-array", "find-minimum-in-rotated-sorted-array", "koko-eating-bananas", "search-a-2d-matrix",
                            "median-of-two-sorted-arrays", "time-based-key-value-store", "snapshot-array", "random-pick-with-weight", "two-sum-ii-input-array-is-sorted"],
 "Backtracking": ["subsets", "permutations", "combination-sum", "generate-parentheses", "word-search", "n-queens", "word-search-ii"],
 "Dynamic programming": ["climbing-stairs", "house-robber", "house-robber-ii", "decode-ways", "coin-change", "partition-equal-subset-sum", "longest-increasing-subsequence",
                         "word-break", "maximum-subarray", "unique-paths", "minimum-path-sum", "longest-common-subsequence", "edit-distance", "palindromic-substrings",
                         "longest-palindromic-substring", "best-time-to-buy-and-sell-stock-with-cooldown", "distinct-subsequences", "regular-expression-matching",
                         "house-robber-iii", "target-sum", "burst-balloons", "counting-bits"],
 "Greedy": ["jump-game", "gas-station", "partition-labels", "non-overlapping-intervals", "minimum-number-of-arrows-to-burst-balloons", "task-scheduler",
            "best-time-to-buy-and-sell-stock", "maximum-subarray"],
 "Trie": ["implement-trie-prefix-tree", "design-add-and-search-words-data-structure", "word-search-ii", "search-suggestions-system"],
 "Bit manipulation": ["single-number", "counting-bits", "number-of-1-bits", "missing-number", "subsets", "shortest-path-visiting-all-nodes"],
}

EXTRA = {
 "Two pointers": [("Valid Palindrome", "valid-palindrome", "Easy"), ("Move Zeroes", "move-zeroes", "Easy"),
                  ("Remove Duplicates from Sorted Array", "remove-duplicates-from-sorted-array", "Easy"), ("4Sum", "4sum", "Medium")],
 "Sliding window": [("Maximum Average Subarray I", "maximum-average-subarray-i", "Easy"), ("Permutation in String", "permutation-in-string", "Medium"),
                    ("Longest Repeating Character Replacement", "longest-repeating-character-replacement", "Medium"),
                    ("Find All Anagrams in a String", "find-all-anagrams-in-a-string", "Medium"), ("Minimum Size Subarray Sum", "minimum-size-subarray-sum", "Medium")],
 "Fast & slow pointers": [("Middle of the Linked List", "middle-of-the-linked-list", "Easy"), ("Happy Number", "happy-number", "Easy"),
                          ("Palindrome Linked List", "palindrome-linked-list", "Easy"), ("Linked List Cycle II", "linked-list-cycle-ii", "Medium"),
                          ("Find the Duplicate Number", "find-the-duplicate-number", "Medium")],
 "Prefix sum + hash map": [("Range Sum Query - Immutable", "range-sum-query-immutable", "Easy"), ("Contiguous Array", "contiguous-array", "Medium"),
                           ("Continuous Subarray Sum", "continuous-subarray-sum", "Medium"), ("Subarray Sums Divisible by K", "subarray-sums-divisible-by-k", "Medium")],
 "Cyclic sort": [("Find All Numbers Disappeared in an Array", "find-all-numbers-disappeared-in-an-array", "Easy"), ("Set Mismatch", "set-mismatch", "Easy"),
                 ("Find the Duplicate Number", "find-the-duplicate-number", "Medium")],
 "Merge intervals": [("Interval List Intersections", "interval-list-intersections", "Medium"), ("Car Pooling", "car-pooling", "Medium")],
 "In-place list reversal": [("Palindrome Linked List", "palindrome-linked-list", "Easy"), ("Reverse Linked List II", "reverse-linked-list-ii", "Medium"),
                            ("Swap Nodes in Pairs", "swap-nodes-in-pairs", "Medium"), ("Rotate List", "rotate-list", "Medium")],
 "Monotonic stack/deque": [("Next Greater Element I", "next-greater-element-i", "Easy"), ("Next Greater Element II", "next-greater-element-ii", "Medium"),
                           ("Online Stock Span", "online-stock-span", "Medium"), ("Car Fleet", "car-fleet", "Medium"), ("Remove K Digits", "remove-k-digits", "Medium"),
                           ("Sum of Subarray Minimums", "sum-of-subarray-minimums", "Medium"), ("Maximal Rectangle", "maximal-rectangle", "Hard")],
 "Tree DFS / BFS": [("Same Tree", "same-tree", "Easy"), ("Balanced Binary Tree", "balanced-binary-tree", "Easy"), ("Subtree of Another Tree", "subtree-of-another-tree", "Easy"),
                    ("Path Sum II", "path-sum-ii", "Medium"), ("Binary Tree Zigzag Level Order Traversal", "binary-tree-zigzag-level-order-traversal", "Medium"),
                    ("Construct Binary Tree from Preorder and Inorder Traversal", "construct-binary-tree-from-preorder-and-inorder-traversal", "Medium")],
 "Graph BFS / DFS": [("Flood Fill", "flood-fill", "Easy"), ("Max Area of Island", "max-area-of-island", "Medium"), ("01 Matrix", "01-matrix", "Medium"),
                     ("Keys and Rooms", "keys-and-rooms", "Medium"), ("Shortest Path in Binary Matrix", "shortest-path-in-binary-matrix", "Medium")],
 "Topological sort": [("Find Eventual Safe States", "find-eventual-safe-states", "Medium"), ("Minimum Height Trees", "minimum-height-trees", "Medium"),
                      ("Course Schedule IV", "course-schedule-iv", "Medium"), ("Sort Items by Groups Respecting Dependencies", "sort-items-by-groups-respecting-dependencies", "Hard")],
 "Union-Find": [("Number of Operations to Make Network Connected", "number-of-operations-to-make-network-connected", "Medium"),
                ("Satisfiability of Equality Equations", "satisfiability-of-equality-equations", "Medium"), ("Accounts Merge", "accounts-merge", "Medium"),
                ("Most Stones Removed with Same Row or Column", "most-stones-removed-with-same-row-or-column", "Medium")],
 "Two heaps": [("Sliding Window Median", "sliding-window-median", "Hard"), ("IPO", "ipo", "Hard")],
 "Top-K / K-way merge": [("Top K Frequent Words", "top-k-frequent-words", "Medium"), ("Reorganize String", "reorganize-string", "Medium"),
                         ("Kth Smallest Element in a Sorted Matrix", "kth-smallest-element-in-a-sorted-matrix", "Medium"),
                         ("Find K Pairs with Smallest Sums", "find-k-pairs-with-smallest-sums", "Medium"),
                         ("Smallest Range Covering Elements from K Lists", "smallest-range-covering-elements-from-k-lists", "Hard")],
 "Modified binary search": [("Search Insert Position", "search-insert-position", "Easy"),
                            ("Find First and Last Position of Element in Sorted Array", "find-first-and-last-position-of-element-in-sorted-array", "Medium"),
                            ("Find Peak Element", "find-peak-element", "Medium"), ("Capacity To Ship Packages Within D Days", "capacity-to-ship-packages-within-d-days", "Medium"),
                            ("Split Array Largest Sum", "split-array-largest-sum", "Hard")],
 "Backtracking": [("Letter Combinations of a Phone Number", "letter-combinations-of-a-phone-number", "Medium"), ("Subsets II", "subsets-ii", "Medium"),
                  ("Permutations II", "permutations-ii", "Medium"), ("Combination Sum II", "combination-sum-ii", "Medium"),
                  ("Palindrome Partitioning", "palindrome-partitioning", "Medium"), ("Sudoku Solver", "sudoku-solver", "Hard")],
 "Dynamic programming": [("Min Cost Climbing Stairs", "min-cost-climbing-stairs", "Easy"), ("Coin Change II", "coin-change-ii", "Medium"),
                         ("Maximal Square", "maximal-square", "Medium"), ("Longest Palindromic Subsequence", "longest-palindromic-subsequence", "Medium"),
                         ("Interleaving String", "interleaving-string", "Medium")],
 "Greedy": [("Assign Cookies", "assign-cookies", "Easy"), ("Jump Game II", "jump-game-ii", "Medium"), ("Boats to Save People", "boats-to-save-people", "Medium"),
            ("Hand of Straights", "hand-of-straights", "Medium"), ("Valid Parenthesis String", "valid-parenthesis-string", "Medium"), ("Candy", "candy", "Hard")],
 "Trie": [("Replace Words", "replace-words", "Medium"), ("Longest Word in Dictionary", "longest-word-in-dictionary", "Medium"), ("Map Sum Pairs", "map-sum-pairs", "Medium"),
          ("Maximum XOR of Two Numbers in an Array", "maximum-xor-of-two-numbers-in-an-array", "Medium")],
 "Bit manipulation": [("Power of Two", "power-of-two", "Easy"), ("Reverse Bits", "reverse-bits", "Easy"), ("Single Number II", "single-number-ii", "Medium"),
                      ("Sum of Two Integers", "sum-of-two-integers", "Medium"), ("Bitwise AND of Numbers Range", "bitwise-and-of-numbers-range", "Medium")],
}


def build(days):
    where = {}
    for d in days:
        for name, slug, diff in d["problems"]:
            where.setdefault(slug, (name, diff, d["day"]))
    out = {}
    for pat, slugs in IN_PLAN.items():
        rows = []
        for s in slugs:
            assert s in where, f"{pat}: {s} not in plan"
            name, diff, day = where[s]
            rows.append(dict(name=name, slug=s, diff=diff, day=day))
        rows.sort(key=lambda r: (r["day"], ["Easy", "Medium", "Hard"].index(r["diff"])))
        for name, s, diff in EXTRA.get(pat, []):
            rows.append(dict(name=name, slug=s, diff=diff, day=None))
        out[pat] = rows
    return out
