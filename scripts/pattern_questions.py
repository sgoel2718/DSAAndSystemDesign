"""Questions solvable by each pattern. Slugs already in the 30-day plan are looked up there (name, difficulty, day);
EXTRA lists classic practice questions outside the plan as (name, slug, difficulty)."""

IN_PLAN = {
 "Two pointers": ["two-sum-ii-input-array-is-sorted", "container-with-most-water", "3sum", "trapping-rain-water", "sort-colors"],
 "Sliding window": ["best-time-to-buy-and-sell-stock", "longest-substring-without-repeating-characters", "minimum-window-substring", "sliding-window-maximum"],
 "Fast & slow pointers": ["linked-list-cycle", "remove-nth-node-from-end-of-list", "reorder-list"],
 "Prefix sum + hash map": ["two-sum", "subarray-sum-equals-k", "product-of-array-except-self", "range-sum-query-2d-immutable", "count-of-range-sum"],
 "Kadane's algorithm": ["best-time-to-buy-and-sell-stock", "maximum-subarray"],
 "Hash maps": ["two-sum", "contains-duplicate", "valid-anagram", "group-anagrams", "top-k-frequent-elements", "longest-consecutive-sequence", "design-hashmap"],
 "Cyclic sort": ["missing-number", "find-all-duplicates-in-an-array", "first-missing-positive"],
 "Merge intervals": ["merge-intervals", "insert-interval", "non-overlapping-intervals", "minimum-number-of-arrows-to-burst-balloons", "partition-labels", "my-calendar-i", "my-calendar-iii"],
 "In-place list reversal": ["reverse-linked-list", "reorder-list", "reverse-nodes-in-k-group"],
 "Stack & monotonic stack": ["daily-temperatures", "largest-rectangle-in-histogram", "sliding-window-maximum", "trapping-rain-water", "min-stack", "valid-parentheses", "evaluate-reverse-polish-notation"],
 "Tree DFS / BFS": ["maximum-depth-of-binary-tree", "invert-binary-tree", "diameter-of-binary-tree", "binary-tree-level-order-traversal", "binary-tree-right-side-view",
                    "lowest-common-ancestor-of-a-binary-tree", "binary-tree-maximum-path-sum", "serialize-and-deserialize-binary-tree", "validate-binary-search-tree",
                    "kth-smallest-element-in-a-bst", "lowest-common-ancestor-of-a-binary-search-tree", "delete-node-in-a-bst", "convert-sorted-array-to-binary-search-tree", "house-robber-iii"],
 "Graph BFS / DFS": ["number-of-islands", "clone-graph", "rotting-oranges", "pacific-atlantic-water-flow", "surrounded-regions", "open-the-lock", "word-ladder",
                     "is-graph-bipartite", "bus-routes", "shortest-path-visiting-all-nodes", "reconstruct-itinerary", "critical-connections-in-a-network"],
 "Topological sort": ["course-schedule", "course-schedule-ii", "verifying-an-alien-dictionary", "longest-increasing-path-in-a-matrix"],
 "Shortest paths & MST": ["network-delay-time", "cheapest-flights-within-k-stops", "path-with-minimum-effort", "swim-in-rising-water",
                          "min-cost-to-connect-all-points"],
 "Union-Find": ["number-of-provinces", "redundant-connection", "min-cost-to-connect-all-points", "number-of-islands", "swim-in-rising-water", "path-with-minimum-effort"],
 "Two heaps": ["find-median-from-data-stream"],
 "Top-K / K-way merge": ["kth-largest-element-in-an-array", "top-k-frequent-elements", "kth-largest-element-in-a-stream", "last-stone-weight", "k-closest-points-to-origin",
                         "task-scheduler", "merge-k-sorted-lists", "network-delay-time", "cheapest-flights-within-k-stops", "design-twitter"],
 "Modified binary search": ["binary-search", "search-in-rotated-sorted-array", "find-minimum-in-rotated-sorted-array", "koko-eating-bananas", "search-a-2d-matrix",
                            "median-of-two-sorted-arrays", "time-based-key-value-store", "snapshot-array", "random-pick-with-weight", "two-sum-ii-input-array-is-sorted"],
 "Backtracking": ["subsets", "permutations", "combination-sum", "generate-parentheses", "word-search", "n-queens", "word-search-ii"],
 "Dynamic programming": ["best-time-to-buy-and-sell-stock", "climbing-stairs", "house-robber", "house-robber-ii", "decode-ways", "coin-change", "partition-equal-subset-sum", "longest-increasing-subsequence",
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
 "Stack & monotonic stack": [("Next Greater Element I", "next-greater-element-i", "Easy"), ("Next Greater Element II", "next-greater-element-ii", "Medium"),
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


# ---------------------------------------------------------------------------
# Questions from Shubham's own sheet (added 17 Nov 2026). (name, slug, difficulty, url or None for LeetCode)
# Difficulty is the site's own rating. Questions already listed above are not repeated, only marked.
# ---------------------------------------------------------------------------
GFG = "https://www.geeksforgeeks.org/"
SHEET_NEW = {
 "Two pointers": [
   ("Segregate 0s and 1s", "gfg-segregate-0s-and-1s", "Easy", GFG + "problems/segregate-0s-and-1s5106/1"),
   ("Remove Duplicates from Sorted List", "remove-duplicates-from-sorted-list", "Easy", None),
   ("Remove Duplicates from Sorted Array II", "remove-duplicates-from-sorted-array-ii", "Medium", None),
   ("Squares of a Sorted Array", "squares-of-a-sorted-array", "Easy", None),
   ("3Sum Closest", "3sum-closest", "Medium", None),
   ("Count Triplets with Sum Smaller than X", "gfg-count-triplets-with-sum-smaller-than-x", "Medium", GFG + "problems/count-triplets-with-sum-smaller-than-x5549/1"),
   ("Subarray Product Less Than K", "subarray-product-less-than-k", "Medium", None),
   ("Backspace String Compare", "backspace-string-compare", "Easy", None),
   ("Shortest Unsorted Continuous Subarray", "shortest-unsorted-continuous-subarray", "Medium", None)],
 "Fast & slow pointers": [
   ("Circular Array Loop", "circular-array-loop", "Medium", None)],
 "Sliding window": [
   ("Max Sum Subarray of Size K", "gfg-max-sum-subarray-of-size-k", "Easy", GFG + "problems/max-sum-subarray-of-size-k5313/1"),
   ("Longest K Unique Characters Substring", "gfg-longest-k-unique-characters-substring", "Medium", GFG + "problems/longest-k-unique-characters-substring0853/1"),
   ("Fruit Into Baskets", "fruit-into-baskets", "Medium", None),
   ("Max Consecutive Ones III", "max-consecutive-ones-iii", "Medium", None),
   ("Substring with Concatenation of All Words", "substring-with-concatenation-of-all-words", "Hard", None)],
 "Kadane's algorithm": [
   ("Smallest Sum Contiguous Subarray", "gfg-smallest-sum-contiguous-subarray", "Medium", GFG + "problems/smallest-sum-contiguous-subarray/1"),
   ("Maximum Product Subarray", "maximum-product-subarray", "Medium", None),
   ("Maximum Subarray Sum with One Deletion", "maximum-subarray-sum-with-one-deletion", "Medium", None),
   ("Maximum Absolute Sum of Any Subarray", "maximum-absolute-sum-of-any-subarray", "Medium", None),
   ("Maximum Sum Circular Subarray", "maximum-sum-circular-subarray", "Medium", None)],
 "Prefix sum + hash map": [
   ("Find Pivot Index", "find-pivot-index", "Easy", None),
   ("Shortest Subarray with Sum at Least K", "shortest-subarray-with-sum-at-least-k", "Hard", None)],
 "Merge intervals": [
   ("Check if Any Two Intervals Overlap", "gfg-check-if-any-two-intervals-overlap", "Easy", GFG + "check-if-any-two-intervals-overlap-among-a-given-set-of-intervals/"),
   ("Attend All Meetings II (Minimum Meeting Rooms)", "gfg-attend-all-meetings-ii", "Medium", GFG + "problems/attend-all-meetings-ii/1"),
   ("Maximum CPU Load", "gfg-maximum-cpu-load", "Hard", GFG + "maximum-cpu-load-from-the-given-list-of-jobs/"),
   ("Employee Free Time", "codertrain-employee-free-time", "Hard", "https://www.codertrain.co/employee-free-time")],
 "In-place list reversal": [
   ("Reverse Nodes in Even Length Groups", "reverse-nodes-in-even-length-groups", "Medium", None)],
 "Stack & monotonic stack": [
   ("Remove All Adjacent Duplicates In String", "remove-all-adjacent-duplicates-in-string", "Easy", None),
   ("Reverse String", "reverse-string", "Easy", None),
   ("Remove Nodes From Linked List", "remove-nodes-from-linked-list", "Medium", None),
   ("Remove All Adjacent Duplicates in String II", "remove-all-adjacent-duplicates-in-string-ii", "Medium", None),
   ("Simplify Path", "simplify-path", "Medium", None)],
 "Hash maps": [
   ("First Unique Character in a String", "first-unique-character-in-a-string", "Easy", None),
   ("Maximum Number of Balloons", "maximum-number-of-balloons", "Easy", None),
   ("Longest Palindrome", "longest-palindrome", "Easy", None),
   ("Ransom Note", "ransom-note", "Easy", None)],
 "Modified binary search": [
   ("Ceil in a Sorted Array", "gfg-ceil-in-a-sorted-array", "Easy", GFG + "problems/ceil-in-a-sorted-array/1"),
   ("Number of Occurrence", "gfg-number-of-occurrence", "Easy", GFG + "problems/number-of-occurrence2259/1"),
   ("Search in an Infinite Sorted Array", "gfg-search-in-infinite-sorted-array", "Medium", GFG + "find-position-element-sorted-array-infinite-numbers/"),
   ("Peak Index in a Mountain Array", "peak-index-in-a-mountain-array", "Medium", None),
   ("Find Kth Rotation (rotation count)", "gfg-find-kth-rotation", "Easy", GFG + "problems/rotation4723/1"),
   ("Minimum Number of Days to Make m Bouquets", "minimum-number-of-days-to-make-m-bouquets", "Medium", None),
   ("Aggressive Cows", "gfg-aggressive-cows", "Medium", GFG + "problems/aggressive-cows/1"),
   ("H-Index II", "h-index-ii", "Medium", None),
   ("Maximum Candies Allocated to K Children", "maximum-candies-allocated-to-k-children", "Medium", None),
   ("Allocate Minimum Pages", "gfg-allocate-minimum-pages", "Medium", GFG + "problems/allocate-minimum-number-of-pages0937/1")],
}
# Second half of the sheet (rows 101-213), added 18 Nov 2026
SHEET_NEW["Modified binary search"] += [
   ("Search a 2D Matrix II", "search-a-2d-matrix-ii", "Medium", None),
   ("Kth Smallest Element in a Sorted Matrix", "kth-smallest-element-in-a-sorted-matrix", "Medium", None),
   ("Kth Smallest Number in Multiplication Table", "kth-smallest-number-in-multiplication-table", "Hard", None)]
SHEET_NEW["Top-K / K-way merge"] = [
   ("Kth Smallest Element", "gfg-kth-smallest-element", "Medium", GFG + "problems/kth-smallest-element5635/1"),
   ("Find K Closest Elements", "find-k-closest-elements", "Medium", None),
   ("The K Weakest Rows in a Matrix", "the-k-weakest-rows-in-a-matrix", "Easy", None),
   ("Merge K Sorted Arrays", "gfg-merge-k-sorted-arrays", "Medium", GFG + "problems/merge-k-sorted-arrays/1"),
   ("Minimum Number of Refueling Stops", "minimum-number-of-refueling-stops", "Hard", None),
   ("IPO", "ipo", "Hard", None),
   ("Course Schedule III", "course-schedule-iii", "Hard", None)]
SHEET_NEW["Backtracking"] = [
   ("Fibonacci Number", "fibonacci-number", "Easy", None),
   ("Palindrome String", "gfg-palindrome-string", "Easy", GFG + "problems/palindrome-string0817/1"),
   ("Check if an Array is Sorted", "gfg-check-if-an-array-is-sorted", "Easy", GFG + "problems/check-if-an-array-is-sorted0701/1"),
   ("Sum of Digits", "gfg-sum-of-digits", "Easy", GFG + "problems/sum-of-digits1742/1"),
   ("Remove All Occurrences of a Character in a String", "gfg-remove-all-occurrences-of-a-character", "Easy",
    GFG + "problems/remove-all-occurrences-of-a-character-in-a-string/1")]
SHEET_NEW["Tree DFS / BFS"] = [
   ("Binary Tree Inorder Traversal", "binary-tree-inorder-traversal", "Easy", None),
   ("Binary Tree Preorder Traversal", "binary-tree-preorder-traversal", "Easy", None),
   ("Binary Tree Postorder Traversal", "binary-tree-postorder-traversal", "Easy", None),
   ("Binary Tree Level Order Traversal II", "binary-tree-level-order-traversal-ii", "Medium", None),
   ("Symmetric Tree", "symmetric-tree", "Easy", None),
   ("Flip Equivalent Binary Trees", "flip-equivalent-binary-trees", "Medium", None),
   ("Search in a Binary Search Tree", "search-in-a-binary-search-tree", "Easy", None),
   ("Lowest Common Ancestor of Deepest Leaves", "lowest-common-ancestor-of-deepest-leaves", "Medium", None),
   ("Two Sum IV - Input is a BST", "two-sum-iv-input-is-a-bst", "Easy", None),
   ("Minimum Depth of Binary Tree", "minimum-depth-of-binary-tree", "Easy", None),
   ("Check Completeness of a Binary Tree", "check-completeness-of-a-binary-tree", "Medium", None),
   ("Recover Binary Search Tree", "recover-binary-search-tree", "Medium", None),
   ("Path Sum", "path-sum", "Easy", None),
   ("Sum Root to Leaf Numbers", "sum-root-to-leaf-numbers", "Medium", None),
   ("Construct Binary Tree from Inorder and Postorder Traversal", "construct-binary-tree-from-inorder-and-postorder-traversal", "Medium", None)]
SHEET_NEW["Graph BFS / DFS"] = [
   ("Print Adjacency List", "gfg-print-adjacency-list", "Easy", GFG + "problems/print-adjacency-list-1587115620/1"),
   ("DFS of Graph", "gfg-dfs-of-graph", "Easy", GFG + "problems/depth-first-traversal-for-a-graph/1"),
   ("BFS of Graph", "gfg-bfs-of-graph", "Easy", GFG + "problems/bfs-traversal-of-graph/1"),
   ("Detect Cycle in an Undirected Graph", "gfg-detect-cycle-in-an-undirected-graph", "Medium", GFG + "problems/detect-cycle-in-an-undirected-graph/1"),
   ("Shortest Path in Undirected Graph (unit distance)", "gfg-shortest-path-unit-distance", "Medium",
    GFG + "problems/shortest-path-in-undirected-graph-having-unit-distance/1")]
SHEET_NEW["Topological sort"] = [
   ("Detect Cycle in a Directed Graph", "gfg-detect-cycle-in-a-directed-graph", "Medium", GFG + "problems/detect-cycle-in-a-directed-graph/1"),
   ("Topological Sort", "gfg-topological-sort", "Medium", GFG + "problems/topological-sort/1")]
SHEET_NEW["Shortest paths & MST"] = [
   ("Dijkstra's Algorithm", "gfg-dijkstra", "Medium", GFG + "problems/implementing-dijkstra-set-1-adjacency-matrix/1"),
   ("Bellman-Ford (Distance from the Source)", "gfg-bellman-ford", "Medium", GFG + "problems/distance-from-the-source-bellman-ford-algorithm/1"),
   ("Minimum Spanning Tree (Prim)", "gfg-prim-mst", "Medium", GFG + "problems/minimum-spanning-tree/1")]
SHEET_NEW["Dynamic programming"] = [
   ("Fibonacci Number", "fibonacci-number", "Easy", None),
   ("0 - 1 Knapsack Problem", "gfg-0-1-knapsack", "Medium", GFG + "problems/0-1-knapsack-problem0945/1"),
   ("Subset Sum Problem", "gfg-subset-sum", "Medium", GFG + "problems/subset-sum-problem-1611555638/1"),
   ("Target Sum", "gfg-target-sum", "Medium", GFG + "problems/target-sum-1626326450/1"),
   ("Best Time to Buy and Sell Stock II", "best-time-to-buy-and-sell-stock-ii", "Medium", None),
   ("Best Time to Buy and Sell Stock III", "best-time-to-buy-and-sell-stock-iii", "Hard", None),
   ("Best Time to Buy and Sell Stock IV", "best-time-to-buy-and-sell-stock-iv", "Hard", None),
   ("Minimum Cost to Cut a Stick", "minimum-cost-to-cut-a-stick", "Hard", None)]
SHEET_NEW["Greedy"] = [
   ("Lemonade Change", "lemonade-change", "Easy", None),
   ("Fractional Knapsack", "gfg-fractional-knapsack", "Medium", GFG + "problems/fractional-knapsack-1587115620/1")]

# Questions from the sheet that were already listed under that pattern (marked "your list")
SHEET_EXISTING = {
 "Two pointers": ["two-sum-ii-input-array-is-sorted", "remove-duplicates-from-sorted-array", "3sum", "sort-colors", "4sum"],
 "Fast & slow pointers": ["linked-list-cycle", "linked-list-cycle-ii", "happy-number", "find-the-duplicate-number", "middle-of-the-linked-list",
                          "palindrome-linked-list", "reorder-list"],
 "Sliding window": ["minimum-size-subarray-sum", "longest-substring-without-repeating-characters", "longest-repeating-character-replacement",
                    "minimum-window-substring", "permutation-in-string", "find-all-anagrams-in-a-string"],
 "Kadane's algorithm": ["maximum-subarray"],
 "Prefix sum + hash map": ["subarray-sum-equals-k", "subarray-sums-divisible-by-k", "contiguous-array", "count-of-range-sum"],
 "Merge intervals": ["merge-intervals", "insert-interval", "interval-list-intersections"],
 "In-place list reversal": ["reverse-linked-list", "reverse-linked-list-ii", "swap-nodes-in-pairs", "reverse-nodes-in-k-group", "rotate-list"],
 "Stack & monotonic stack": ["valid-parentheses", "next-greater-element-ii", "daily-temperatures", "remove-k-digits"],
 "Modified binary search": ["search-a-2d-matrix", "median-of-two-sorted-arrays",
                            "binary-search", "find-first-and-last-position-of-element-in-sorted-array", "find-peak-element",
                            "find-minimum-in-rotated-sorted-array", "search-in-rotated-sorted-array", "koko-eating-bananas",
                            "capacity-to-ship-packages-within-d-days", "split-array-largest-sum"],
 "Top-K / K-way merge": ["kth-largest-element-in-an-array", "top-k-frequent-elements", "top-k-frequent-words", "k-closest-points-to-origin",
                         "kth-smallest-element-in-a-sorted-matrix", "last-stone-weight", "task-scheduler", "reorganize-string"],
 "Two heaps": ["find-median-from-data-stream", "sliding-window-median"],
 "Backtracking": ["generate-parentheses", "letter-combinations-of-a-phone-number", "permutations", "combination-sum", "palindrome-partitioning"],
 "Tree DFS / BFS": ["binary-tree-level-order-traversal", "binary-tree-zigzag-level-order-traversal", "invert-binary-tree", "same-tree",
                    "subtree-of-another-tree", "lowest-common-ancestor-of-a-binary-tree", "lowest-common-ancestor-of-a-binary-search-tree",
                    "kth-smallest-element-in-a-bst", "maximum-depth-of-binary-tree", "balanced-binary-tree", "diameter-of-binary-tree",
                    "validate-binary-search-tree", "path-sum-ii", "binary-tree-maximum-path-sum",
                    "construct-binary-tree-from-preorder-and-inorder-traversal", "convert-sorted-array-to-binary-search-tree"],
 "Graph BFS / DFS": ["number-of-islands", "rotting-oranges", "is-graph-bipartite", "surrounded-regions", "word-ladder"],
 "Union-Find": ["number-of-provinces"],
 "Shortest paths & MST": ["network-delay-time", "path-with-minimum-effort", "swim-in-rising-water", "cheapest-flights-within-k-stops"],
 "Dynamic programming": ["climbing-stairs", "house-robber", "longest-increasing-subsequence", "longest-common-subsequence", "unique-paths",
                         "best-time-to-buy-and-sell-stock"],
 "Greedy": ["jump-game", "assign-cookies"],
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
        have = {r["slug"] for r in rows}
        for name, s, diff in EXTRA.get(pat, []):
            if s not in have:
                rows.append(dict(name=name, slug=s, diff=diff, day=None)); have.add(s)
        for name, s, diff, url in SHEET_NEW.get(pat, []):
            assert s not in have, f"{pat}: {s} already listed"
            rows.append(dict(name=name, slug=s, diff=diff, day=None, url=url)); have.add(s)
        mine = set(SHEET_EXISTING.get(pat, [])) | {t[1] for t in SHEET_NEW.get(pat, [])}
        assert mine <= have, f"{pat}: sheet slugs missing {mine - have}"
        for r in rows:
            r["url"] = r.get("url") or f"https://leetcode.com/problems/{r['slug']}/"
            r["mine"] = r["slug"] in mine
        out[pat] = rows
    return out


# Which plan day teaches each pattern from Shubham's sheet (so the Questions tab can show them day-wise)
SHEET_DAY = {"Two pointers": 2, "Sliding window": 2, "Kadane's algorithm": 2, "Prefix sum + hash map": 2, "Hash maps": 3,
             "Modified binary search": 5, "Fast & slow pointers": 6, "In-place list reversal": 6, "Stack & monotonic stack": 7,
             "Merge intervals": 15, "Backtracking": 4, "Top-K / K-way merge": 10, "Two heaps": 10, "Tree DFS / BFS": 8,
             "Graph BFS / DFS": 12, "Topological sort": 12, "Union-Find": 13, "Shortest paths & MST": 13,
             "Dynamic programming": 16, "Greedy": 15}
SHEET_ORDER = ["Two pointers", "Fast & slow pointers", "Sliding window", "Kadane's algorithm", "Prefix sum + hash map",
               "Merge intervals", "In-place list reversal", "Stack & monotonic stack", "Hash maps", "Modified binary search",
               "Top-K / K-way merge", "Two heaps", "Backtracking", "Tree DFS / BFS", "Graph BFS / DFS", "Topological sort",
               "Union-Find", "Shortest paths & MST", "Dynamic programming", "Greedy"]


def mine_by_day(days, pattern_q):
    """Sheet questions that are not already plan questions, grouped under the day that teaches their pattern."""
    in_plan = {slug for d in days for _, slug, _ in d["problems"]}
    assert set(SHEET_ORDER) == set(SHEET_DAY) == set(SHEET_NEW) | set(SHEET_EXISTING)
    out, seen = {}, set()
    for pat in SHEET_ORDER:
        for r in pattern_q[pat]:
            if r["mine"] and r["slug"] not in in_plan and r["slug"] not in seen:
                seen.add(r["slug"])
                out.setdefault(SHEET_DAY[pat], []).append(dict(name=r["name"], slug=r["slug"], diff=r["diff"], url=r["url"], pattern=pat))
    return out
