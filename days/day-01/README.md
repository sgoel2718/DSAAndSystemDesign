# Day 1 - Java for DSA + Complexity Analysis

**Goal:** be able to look at any code and state its time and space complexity, pick the right Java collection for a job, and avoid the core-Java traps that cause silent bugs in interviews.

| File | What it shows | Run |
|---|---|---|
| `GrowthRates.java` | Step counts for each Big-O class, then O(n^2) vs O(n) timed on real code | `javac GrowthRates.java && java GrowthRates` |
| `CollectionsBenchmark.java` | ArrayList vs LinkedList vs ArrayDeque on the same operations | `javac CollectionsBenchmark.java && java CollectionsBenchmark` |
| `CoreJavaGotchas.java` | Integer cache, String pool, pass-by-value, autoboxing, comparators, stack depth | `javac CoreJavaGotchas.java && java CoreJavaGotchas` |
| `Problems.java` | Two Sum, Contains Duplicate, Fizz Buzz, Richest Customer Wealth with tests | `javac Problems.java && java Problems` |

---

## 1. What Big-O actually measures

Big-O describes **how the work grows when the input grows**, ignoring constants and small terms.

- `O(3n + 20)` -> `O(n)`; `O(n^2 + n)` -> `O(n^2)`; `O(500)` -> `O(1)`.
- Different inputs get different letters: looping over `a` then `b` is `O(a + b)`, nested is `O(a * b)`. Don't call both `n`.

| Notation | Meaning | Interview use |
|---|---|---|
| Big-O | upper bound (worst case growth) | what you quote by default |
| Big-Omega | lower bound | "any comparison sort needs Omega(n log n)" |
| Big-Theta | tight bound (both) | precise statements |

**Best / average / worst case** are about *which input*: quicksort is O(n log n) average but O(n^2) worst (already-sorted input with a bad pivot). HashMap get is O(1) average, O(n) worst (all keys collide; O(log n) since Java 8 when a bucket becomes a red-black tree).

### The growth ladder (from `GrowthRates` output)

| n | log n | n | n log n | n^2 |
|---|---|---|---|---|
| 10^3 | 10 | 10^3 | 10^4 | 10^6 |
| 10^5 | 17 | 10^5 | 1.7 x 10^6 | **10^10** |
| 10^6 | 20 | 10^6 | 2 x 10^7 | 10^12 |

**About 10^8 simple operations take ~1 second.** Use the constraint to guess the intended complexity:

| Constraint on n | Expected complexity | Typical technique |
|---|---|---|
| n <= 12 | O(n!) | permutations |
| n <= 20-25 | O(2^n) | subsets, bitmask DP |
| n <= 500 | O(n^3) | interval DP, Floyd-Warshall |
| n <= 5,000 | O(n^2) | 2D DP, nested loops |
| n <= 10^5 - 10^6 | O(n log n) or O(n) | sorting, heaps, two pointers, hashing |
| n >= 10^9 | O(log n) or O(1) | binary search, math |

Measured on Day 1 (no duplicates, worst case):

| n | O(n^2) nested loops | O(n) HashSet |
|---|---|---|
| 10,000 | 13 ms | 1.2 ms |
| 100,000 | 742 ms | 17 ms |

## 2. How to compute complexity

1. **Sequential blocks add:** loop of n, then loop of m -> O(n + m).
2. **Nested loops multiply:** but check the inner bound. `for i..n for j = i..n` is still O(n^2) (n^2 / 2).
3. **Halving gives log:** `while (n > 1) n /= 2;` -> O(log n).
4. **Recursion:** cost = (number of calls) x (work per call). Draw the recursion tree.
   - `fib(n) = fib(n-1) + fib(n-2)` -> about 2^n calls -> O(2^n).
   - Merge sort: log n levels, O(n) work per level -> O(n log n).
5. **Master theorem** for `T(n) = a T(n/b) + O(n^d)`:
   - d > log_b a -> O(n^d); d = log_b a -> O(n^d log n); d < log_b a -> O(n^(log_b a)).
   - Binary search: a=1, b=2, d=0 -> O(log n). Merge sort: a=2, b=2, d=1 -> O(n log n).
6. **Space** counts extra memory you allocate **plus the recursion stack** (a recursive DFS on a tree of height h uses O(h) space).

### Amortised analysis
`ArrayList.add` is usually O(1) but occasionally copies the whole array when full (capacity grows by 1.5x in Java). The copies add up to a constant multiple of n over n adds, so the **amortised** cost per add is O(1). Same idea for `HashMap` resizing and `StringBuilder.append`.

## 3. JVM memory in 60 seconds

| Stack | Heap |
|---|---|
| One per thread; holds method frames, local primitives and **references** | Shared; holds all **objects** and arrays |
| Freed automatically when the method returns | Freed by the garbage collector |
| Too deep -> `StackOverflowError` (~16,000 frames in the demo) | Too full -> `OutOfMemoryError` |

- **Primitives** (`int`, `long`, `char`, `boolean`) store the value directly. **Wrappers** (`Integer`, `Long`) are objects on the heap (~16 bytes each).
- Collections only hold objects, so `List<Integer>` **autoboxes** every int. In the demo, 5M ints: `int[]` 15 ms vs `List<Integer>` 63 ms. Use `int[]` when size is known.
- **Integer cache:** values -128..127 are reused objects, so `==` "works" for 127 and fails for 128. Always compare wrappers with `equals()` (or unbox to int first). This bug appears in real interviews with `map.get(a) == map.get(b)`.
- **Java is always pass-by-value.** For objects, the *reference* is copied: a method can change the array's contents, but reassigning the parameter does not affect the caller.
- **GC basics:** the heap is split into young and old generations; most objects die young and are collected cheaply. G1 is the default collector; ZGC targets very low pause times.

## 4. Strings

- `String` is **immutable**. `s += x` in a loop creates a new string each time -> O(n^2) total. Demo: 20,000 appends took 44 ms with `+=` and 0.6 ms with `StringBuilder`.
- String literals live in the **String pool**, so `"java" == "java"` is true but `"java" == new String("java")` is false. Use `equals()`.
- `StringBuilder` is not thread-safe and fast; `StringBuffer` is synchronised and slower (rarely needed).
- Useful in DSA: `s.toCharArray()`, `s.charAt(i)`, `int[] count = new int[26]; count[c - 'a']++;`.

## 5. The Collections Framework map

```
Collection
 ├── List      ArrayList (default), LinkedList
 ├── Set       HashSet (O(1)), LinkedHashSet (insertion order), TreeSet (sorted, O(log n))
 └── Queue/Deque  ArrayDeque (stack + queue), PriorityQueue (heap)
Map            HashMap (O(1)), LinkedHashMap (order / LRU), TreeMap (sorted, O(log n))
```

| Need | Use | Key operations and cost |
|---|---|---|
| Index access, append | `ArrayList` | get O(1), add O(1) amortised, add(0, x) O(n) |
| Stack | `ArrayDeque` | push / pop / peek O(1) (not `Stack`, which is legacy and synchronised) |
| Queue / BFS | `ArrayDeque` | offer / poll O(1) |
| "Seen before?" | `HashSet` | add / contains O(1) average |
| Counting, lookup by key | `HashMap` | get / put / merge O(1) average |
| Sorted keys, floor / ceiling | `TreeMap` / `TreeSet` | O(log n) |
| Smallest / largest repeatedly | `PriorityQueue` | offer / poll O(log n), peek O(1) |

Measured with n = 100,000 (`CollectionsBenchmark`):

| Operation | ArrayList | LinkedList | ArrayDeque |
|---|---|---|---|
| add at end | 1.1 ms | 16 ms | 4 ms |
| add at front | **322 ms** | 1.1 ms | 17 ms |
| get(i) x 10,000 | 0.3 ms | **1,472 ms** | n/a |

LinkedList wins only at the front, and ArrayDeque does that too without the slow `get`. In interviews: `ArrayList` for lists, `ArrayDeque` for stacks and queues.

## 6. Interview-ready Java habits

- **Fast input** for coding rounds that read stdin (HackerRank / Codility style online assessments):
  ```java
  BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
  StringTokenizer st = new StringTokenizer(br.readLine());
  int n = Integer.parseInt(st.nextToken());
  StringBuilder out = new StringBuilder();   // print once at the end
  ```
- **Comparable vs Comparator:** `Comparable` defines the natural order inside the class (`compareTo`); `Comparator` defines any order from outside. Prefer `Comparator.comparingInt(Person::age).thenComparing(Person::name)`.
- **Never compare with subtraction:** `(a, b) -> a - b` overflows for large/negative values. Use `Integer.compare(a, b)`.
- **Generics:** write `Map<Integer, List<String>>` with `var` only where the type is obvious.
- **Java 8-21 features to mention:** lambdas and streams (for readable code, but use loops in performance-critical interview code), `Optional`, records (`record Person(String name, int age)`), switch expressions, `var`, text blocks, sealed classes.
- **Exceptions:** checked (`IOException`, must declare or catch) vs unchecked (`RuntimeException`, e.g. `NullPointerException`, `ArrayIndexOutOfBoundsException`). `final` (cannot reassign/extend), `finally` (always runs), `finalize` (deprecated).

## 7. Problems

| # | Problem | Brute force | Optimal | Pattern |
|---|---|---|---|---|
| 1 | [Two Sum](https://leetcode.com/problems/two-sum/) | O(n^2) every pair | **O(n)** HashMap of value -> index, check `target - x` before inserting `x` | hashing / complement lookup |
| 217 | [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | O(n^2) | **O(n)** HashSet (`add` returns false on repeat); or O(n log n) sort with O(1) extra space | hashing |
| 412 | [Fizz Buzz](https://leetcode.com/problems/fizz-buzz/) | - | O(n), check 15 first | clean code |
| 1672 | [Richest Customer Wealth](https://leetcode.com/problems/richest-customer-wealth/) | - | O(m x n) 2D traversal | arrays |

**Two Sum walkthrough** for `nums = [2, 7, 11, 15], target = 9`:

| i | nums[i] | need = 9 - nums[i] | map before | found? |
|---|---|---|---|---|
| 0 | 2 | 7 | {} | no -> put 2:0 |
| 1 | 7 | 2 | {2:0} | **yes -> [0, 1]** |

Checking before inserting is what makes `[3, 3], target 6` work without pairing an element with itself.

### Can we avoid the O(n) space? (sort + two pointers)

It depends on what the question asks you to return.

| Version | Time | Extra space | Notes |
|---|---|---|---|
| Brute force | O(n^2) | O(1) | every pair |
| HashMap | **O(n)** | O(n) | best for LeetCode 1 |
| Sort + two pointers, return **values** / true-false | O(n log n) | O(log n) (sort stack) | sorts the caller's array in place |
| Sort + two pointers, return **indices** | O(n log n) | **O(n)** | sorting loses positions, so you need an index array |
| [Two Sum II](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/): input **already sorted** | **O(n)** | **O(1)** | two pointers only, no sort |

- LeetCode 1 asks for **indices**. Once you sort, every element moves, so you must store each element's original position: that is O(n) space again, and the time is worse (O(n log n) vs O(n)). The HashMap wins.
- If the interviewer asks for the **values**, or only "does a pair exist?", sort + two pointers really does cut space to O(log n). Mention that it **mutates the input**; if that is not allowed, you need a copy and the space is O(n) again.
- If the input is **already sorted**, two pointers gives O(n) time and O(1) space: the best of both.
- `Arrays.sort(int[])` is dual-pivot quicksort, which uses O(log n) stack space. Most interviewers accept calling that "O(1) extra space", but saying O(log n) shows you know.

**Say this in the interview:** "HashMap gives O(n) time and O(n) space. If memory is tight and I only need the values, I can sort and use two pointers for O(n log n) time and O(log n) space, but that changes the input order and loses the original indices."

## 8. How to approach questions today

1. Read the constraints and state the target complexity (n <= 10^5 -> O(n log n) or better).
2. Say the brute force and its complexity out loud first.
3. Ask "what am I repeating?" - usually a search you can replace with a HashMap/HashSet lookup.
4. Code, then test: normal case, duplicates, negatives, empty input.
5. Finish with time and space complexity.

## Sticky notes

- Drop constants and lower terms: O(2n + 5) = O(n)
- Amortised O(1): ArrayList grows by copying, but n adds still cost O(n) total
- Integer caching only covers -128..127: compare wrappers with equals(), never ==
- StackOverflowError = recursion too deep; go iterative for 10^5+ depth
- Interviewers expect you to state time AND space before coding

## Homework (if you have the 5-hour day)

- Solve the 4 problems on LeetCode yourself **without looking at `Problems.java`**, then compare.
- Write the complexity of every method in `GrowthRates.java` and `CollectionsBenchmark.java` as comments.
- NexusKV: open `/nexuskv`, run `mvn test`, and read the `KeyValueStore` interface you will implement against for the next 4 weeks.
