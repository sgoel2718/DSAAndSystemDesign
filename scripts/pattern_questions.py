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
 "Modified binary search": ["binary-search", "find-first-and-last-position-of-element-in-sorted-array", "find-peak-element",
                            "find-minimum-in-rotated-sorted-array", "search-in-rotated-sorted-array", "koko-eating-bananas",
                            "capacity-to-ship-packages-within-d-days", "split-array-largest-sum"],
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
             "Merge intervals": 15}
SHEET_ORDER = ["Two pointers", "Fast & slow pointers", "Sliding window", "Kadane's algorithm", "Prefix sum + hash map",
               "Merge intervals", "In-place list reversal", "Stack & monotonic stack", "Hash maps", "Modified binary search"]


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
