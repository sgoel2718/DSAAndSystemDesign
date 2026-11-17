"""'Padho with Pratyush Practice Sheet' - mirrors Shubham's Google Sheet row by row (read 17 Nov 2026).
Each row: (text exactly as in the sheet, [links in sheet order]). Rows map to board slugs so ticks, bookmarks
and comments are shared with the rest of the board."""
import re

SHEET_URL = "https://docs.google.com/spreadsheets/d/1T5-nGsJ9WNwna44e9WWRD0jlZIT5KxVOGvylcvvVrY8/edit?gid=0#gid=0"
GFG = "https://www.geeksforgeeks.org/"
LC = "https://leetcode.com/problems/"

SECTIONS = [
 ("Two Pointers", "1. Pattern: Two Pointers", "Two pointers", [
   ("Pair with Target Sum (easy)", [LC + "two-sum-ii-input-array-is-sorted/description/"]),
   ("Rearrange 0 and 1", [GFG + "problems/segregate-0s-and-1s5106/1"]),
   ("Remove Duplicates (easy) · Sorted List", [LC + "remove-duplicates-from-sorted-list/"]),
   ("Remove Duplicates (easy) · Sorted Array", [LC + "remove-duplicates-from-sorted-array/description/"]),
   ("Remove Duplicates (easy) · Sorted Array II", [LC + "remove-duplicates-from-sorted-array-ii/"]),
   ("Squaring a Sorted Array (easy)", [LC + "squares-of-a-sorted-array/"]),
   ("Triplet Sum to Zero (medium)", [LC + "3sum/"]),
   ("Triplet Sum Close to Target (medium)", [LC + "3sum-closest/"]),
   ("Triplets with Smaller Sum (medium)", [GFG + "problems/count-triplets-with-sum-smaller-than-x5549/1"]),
   ("Subarrays with Product Less than a Target (medium)", [LC + "subarray-product-less-than-k/"]),
   ("Dutch National Flag Problem (medium)", [LC + "sort-colors/description/"]),
   ("Problem Challenge 1: Quadruple Sum to Target (medium)", [LC + "4sum/"]),
   ("Problem Challenge 2: Comparing Strings containing Backspaces (medium)", [LC + "backspace-string-compare/"]),
   ("Problem Challenge 3: Minimum Window Sort (medium)", [LC + "shortest-unsorted-continuous-subarray/",
      "https://www.ideserve.co.in/learn/minimum-length-subarray-sorting-which-results-in-sorted-array"]),
 ]),
 ("Fast & Slow Pointers", "2. Pattern: Fast & Slow pointers", "Fast & slow pointers", [
   ("LinkedList Cycle (easy)", [LC + "linked-list-cycle/"]),
   ("Start of LinkedList Cycle (medium)", [LC + "linked-list-cycle-ii/"]),
   ("Happy Number (medium)", [LC + "happy-number/"]),
   ("FIND DUPLICATE NUMBER", [LC + "find-the-duplicate-number/description/"]),
   ("Middle of the LinkedList (easy)", [LC + "middle-of-the-linked-list/"]),
   ("Problem Challenge 1: Palindrome LinkedList (medium)", [LC + "palindrome-linked-list/"]),
   ("Problem Challenge 2: Rearrange a LinkedList (medium)", [LC + "reorder-list/"]),
   ("Problem Challenge 3: Cycle in a Circular Array (hard)", [LC + "circular-array-loop/"]),
 ]),
 ("Sliding Window", "3. Pattern: Sliding Window", "Sliding window", [
   ("Maximum Sum Subarray of Size K (easy)", [GFG + "problems/max-sum-subarray-of-size-k5313/1"]),
   ("Smallest Subarray with a given sum (easy)", [LC + "minimum-size-subarray-sum/"]),
   ("Longest Substring with K Distinct Characters (medium)", [GFG + "problems/longest-k-unique-characters-substring0853/1"]),
   ("Fruits into Baskets (medium)", [LC + "fruit-into-baskets/"]),
   ("No-repeat Substring (hard)", [LC + "longest-substring-without-repeating-characters/"]),
   ("Longest Substring with Same Letters after Replacement (hard)", [LC + "longest-repeating-character-replacement/"]),
   ("Longest Subarray with Ones after Replacement (hard)", [LC + "max-consecutive-ones-iii/"]),
   ("Minimum size subarray SUM", [LC + "minimum-size-subarray-sum/"]),
   ("MInimum Size Substring (HARD)", [LC + "minimum-window-substring/description/"]),
   ("Problem Challenge 1: Permutation in a String (hard)", [LC + "permutation-in-string/"]),
   ("Problem Challenge 2: String Anagrams (hard)", [LC + "find-all-anagrams-in-a-string/"]),
   ("Problem Challenge 4: Words Concatenation (hard)", [LC + "substring-with-concatenation-of-all-words/"]),
 ]),
 ("Kadane", "Pattern: Kadane pattern", "Kadane's algorithm", [
   ("Maximum subarray sum", [LC + "maximum-subarray/"]),
   ("Minimum Subarray Sum", [GFG + "problems/smallest-sum-contiguous-subarray/1"]),
   ("Maximum product subarray", [LC + "maximum-product-subarray/"]),
   ("Maximum subarray sum with one deletion", [LC + "maximum-subarray-sum-with-one-deletion/description/"]),
   ("Maximum absolute sum of any subarray", [LC + "maximum-absolute-sum-of-any-subarray/"]),
   ("Maximum sum in circular array variant", [LC + "maximum-sum-circular-subarray/"]),
 ]),
 ("Prefix Sum", "PATTERN: PREFIX SUM", "Prefix sum + hash map", [
   ("Subarray Sum Equals K (EASY)", [LC + "subarray-sum-equals-k/description/"]),
   ("Find Pivot Index (EASY)", [LC + "find-pivot-index/description/"]),
   ("Subarray Sums Divisible By K (Med)", [LC + "subarray-sums-divisible-by-k/description/"]),
   ("Contiguous array (MED)", [LC + "contiguous-array/description/"]),
   ("Problem challenge: Shortest Subarray With Sum at Least K (HARD)", [LC + "shortest-subarray-with-sum-at-least-k/description/"]),
   ("Problem challenge: Count Range Sum (hard)", [LC + "count-of-range-sum/description/"]),
 ]),
 ("Merge Intervals", "4. Pattern: Merge Intervals", "Merge intervals", [
   ("Merge Intervals (medium)", [LC + "merge-intervals/description/"]),
   ("Insert Interval (medium)", [LC + "insert-interval/"]),
   ("Intervals Intersection (medium)", [LC + "interval-list-intersections/description/"]),
   ("Overlapping Intervals", [GFG + "check-if-any-two-intervals-overlap-among-a-given-set-of-intervals/"]),
   ("Problem Challenge 1: Minimum Meeting Rooms (hard)", [GFG + "problems/attend-all-meetings-ii/1"]),
   ("Problem Challenge 2: Maximum CPU Load (hard)", [GFG + "maximum-cpu-load-from-the-given-list-of-jobs/"]),
   ("Problem Challenge 3: Employee Free Time (hard)", ["https://www.codertrain.co/employee-free-time"]),
 ]),
 ("In-place Reversal of a LinkedList", "6. Pattern: In-place Reversal of a LinkedList", "In-place list reversal", [
   ("Reverse a LinkedList (easy)", [LC + "reverse-linked-list/"]),
   ("Reverse a Sub-list (medium)", [LC + "reverse-linked-list-ii/"]),
   ("Reverse List in Pairs (Medium)", [LC + "swap-nodes-in-pairs/description/"]),
   ("Reverse every K-element Sub-list (HARD)", [LC + "reverse-nodes-in-k-group/"]),
   ("Problem Challenge 1: Reverse nodes in EVEN Length Groups (HARD)", [LC + "reverse-nodes-in-even-length-groups/description/"]),
   ("Problem Challenge 2: Rotate a LinkedList (medium)", [LC + "rotate-list/"]),
 ]),
 ("Stack", "7. Pattern: Stack", "Stack & monotonic stack", [
   ("remove adjacent duplicates", [LC + "remove-all-adjacent-duplicates-in-string/description/"]),
   ("Balanced Parentheses", [LC + "valid-parentheses/description/"]),
   ("Reverse a String", []),                      # no link in the sheet; board suggests LeetCode Reverse String
   ("Next Greater Element (easy)", [LC + "next-greater-element-ii/description/"]),
   ("Daily Temperatures (easy)", [LC + "daily-temperatures/"]),
   ("Remove Nodes From Linked List (easy)", [LC + "remove-nodes-from-linked-list/"]),
   ("Remove All Adjacent Duplicates in String II (medium)", [LC + "remove-all-adjacent-duplicates-in-string-ii/"]),
   ("Simplify Path (Problem Challenge)", [LC + "simplify-path/"]),
   ("Remove K Digits (hard) Problem challenge", [LC + "remove-k-digits/"]),
 ]),
 ("Hash Maps", "9. Pattern: Hash Maps", "Hash maps", [
   ("First Non-repeating Character (easy)", [LC + "first-unique-character-in-a-string/"]),
   ("Maximum Number of Balloons (easy)", [LC + "maximum-number-of-balloons/"]),
   ("Longest Palindrome(easy)", [LC + "longest-palindrome/"]),
   ("Ransom Note (easy)", [LC + "ransom-note/"]),
 ]),
 ("Binary Search", "10. Pattern : Binary Search", "Modified binary search", [
   ("Binary search basic", [LC + "binary-search/"]),
   ("Upper Bound/ Ceiling", [GFG + "problems/ceil-in-a-sorted-array/1"]),
   ("First and Last position", [LC + "find-first-and-last-position-of-element-in-sorted-array/"]),
   ("Count number of occurences", [GFG + "problems/number-of-occurrence2259/1"]),
   ("Search in infinite Sorted array", [GFG + "find-position-element-sorted-array-infinite-numbers/"]),
   ("Peak index in Mountain", [LC + "peak-index-in-a-mountain-array/"]),
   ("Find peak in mountain range", [LC + "find-peak-element/"]),
   ("Find minimum in rotated sorted array", [LC + "find-minimum-in-rotated-sorted-array/"]),
   ("Find number of rotations to sorted array", [GFG + "problems/rotation4723/1"]),
   ("Search in rotated sorted array", [LC + "search-in-rotated-sorted-array/description/"]),
   ("KOKO eating BANANAS", [LC + "koko-eating-bananas/"]),
   ("Min num of days to make m bouquets", [LC + "minimum-number-of-days-to-make-m-bouquets/"]),
   ("Aggresive cows", [GFG + "problems/aggressive-cows/1"]),
   ("H index 2", [LC + "h-index-ii/description/"]),
   ("Max candies to k children", [LC + "maximum-candies-allocated-to-k-children/description/"]),
   ("Capacity to ship packages in d days", [LC + "capacity-to-ship-packages-within-d-days/description/"]),
   ("Book Allocation Problem", [GFG + "problems/allocate-minimum-number-of-pages0937/1"]),
   ("Split largest arrray", [LC + "split-array-largest-sum/description/"]),
 ]),
]

NO_LINK_SLUG = {"Reverse a String": "reverse-string"}


def build(days, pattern_q, sheet_day):
    """Resolve every sheet row to a board question (slug, difficulty, day key) and return JSON-ready sections."""
    plan_day = {}
    for d in days:
        for _, slug, _ in d["problems"]:
            plan_day.setdefault(slug, d["day"])
    by_url, by_slug = {}, {}
    for pat, rows in pattern_q.items():
        for r in rows:
            by_url[(pat, r["url"].split("?")[0].rstrip("/"))] = r
            by_slug[(pat, r["slug"])] = r
    out, n = [], 0
    for title, sheet_title, pattern, rows in SECTIONS:
        items = []
        for text, links in rows:
            if links:
                u = links[0].split("?")[0].rstrip("/")
                if u.startswith(LC):
                    slug = re.match(re.escape(LC) + r"([^/]+)", u).group(1)
                else:
                    slug = by_url[(pattern, u)]["slug"]
            else:
                slug = NO_LINK_SLUG[text]
            r = by_slug[(pattern, slug)]
            assert r["mine"] or slug in plan_day, f"{text}: {slug} not marked as your list"
            day = plan_day.get(slug, sheet_day[pattern])
            shown = links or [r["url"]]
            n += 1
            items.append(dict(n=n, text=text, slug=slug, name=r["name"], diff=r["diff"], day=day,
                              links=shown, suggested=not links))
        out.append(dict(title=title, sheet_title=sheet_title, pattern=pattern, day=sheet_day[pattern], items=items))
    return out
