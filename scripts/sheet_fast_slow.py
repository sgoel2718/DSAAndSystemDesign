"""Approaches for the Fast & Slow Pointers questions from the Padho with Pratyush practice sheet (Java only)."""

SOL = {

"linked-list-cycle": [
 dict(name="HashSet of visited nodes",
      idea="Walk the list; if a node is seen twice there is a cycle.",
      time="O(n)", space="O(n)",
      code="""public boolean hasCycle(ListNode head) {
    Set<ListNode> seen = new HashSet<>();
    for (ListNode p = head; p != null; p = p.next) {
        if (!seen.add(p)) return true;
    }
    return false;
}"""),
 dict(name="Floyd's fast & slow pointers (optimal)",
      idea="Slow moves 1 step, fast moves 2. In a cycle fast gains one node per step and must land on slow; without a cycle fast reaches null.",
      time="O(n)", space="O(1)", best=True,
      code="""public boolean hasCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) return true;
    }
    return false;
}"""),
],

"linked-list-cycle-ii": [
 dict(name="HashSet of visited nodes",
      idea="The first node seen twice is where the cycle starts.",
      time="O(n)", space="O(n)",
      code="""public ListNode detectCycle(ListNode head) {
    Set<ListNode> seen = new HashSet<>();
    for (ListNode p = head; p != null; p = p.next) {
        if (!seen.add(p)) return p;
    }
    return null;
}"""),
 dict(name="Floyd: meet, then restart one pointer from head (optimal)",
      idea="After slow and fast meet, the distance from head to the cycle start equals the distance from the meeting point to the start (mod cycle length). Move one pointer from head and one from the meeting point, one step each; they meet at the start.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode detectCycle(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) {
            ListNode p = head;
            while (p != slow) { p = p.next; slow = slow.next; }
            return p;
        }
    }
    return null;
}"""),
],

"middle-of-the-linked-list": [
 dict(name="Copy nodes into an array",
      idea="Store every node in a list and return the one at index size / 2.",
      time="O(n)", space="O(n)",
      code="""public ListNode middleNode(ListNode head) {
    List<ListNode> nodes = new ArrayList<>();
    for (ListNode p = head; p != null; p = p.next) nodes.add(p);
    return nodes.get(nodes.size() / 2);
}"""),
 dict(name="Count, then walk half way",
      idea="First pass counts n; second pass walks n / 2 steps.",
      time="O(n)", space="O(1)",
      code="""public ListNode middleNode(ListNode head) {
    int n = 0;
    for (ListNode p = head; p != null; p = p.next) n++;
    ListNode p = head;
    for (int i = 0; i < n / 2; i++) p = p.next;
    return p;
}"""),
 dict(name="Fast & slow pointers (optimal, one pass)",
      idea="When fast reaches the end, slow has moved half as far. For even length this returns the second middle, as the problem asks.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode middleNode(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    return slow;
}"""),
],

"happy-number": [
 dict(name="HashSet of seen numbers",
      idea="Keep replacing n by the sum of the squares of its digits. If we reach 1 it is happy; if a number repeats we are in a loop.",
      time="O(log n) per step, few steps", space="O(log n)",
      code="""public boolean isHappy(int n) {
    Set<Integer> seen = new HashSet<>();
    while (n != 1 && seen.add(n)) n = next(n);
    return n == 1;
}
private int next(int n) {
    int s = 0;
    while (n > 0) { int d = n % 10; s += d * d; n /= 10; }
    return s;
}"""),
 dict(name="Floyd's cycle detection (optimal)",
      idea="The sequence either reaches 1 or loops. Treat it as a linked list: slow takes one step, fast takes two; they meet inside the loop, and the number is happy only if they meet at 1.",
      time="O(log n) per step, few steps", space="O(1)", best=True,
      code="""public boolean isHappy(int n) {
    int slow = n, fast = next(n);
    while (fast != 1 && slow != fast) {
        slow = next(slow);
        fast = next(next(fast));
    }
    return fast == 1;
}
private int next(int n) {
    int s = 0;
    while (n > 0) { int d = n % 10; s += d * d; n /= 10; }
    return s;
}"""),
],

"palindrome-linked-list": [
 dict(name="Copy values into an array, two pointers",
      idea="Copy the values to an ArrayList and compare from both ends.",
      time="O(n)", space="O(n)",
      code="""public boolean isPalindrome(ListNode head) {
    List<Integer> v = new ArrayList<>();
    for (ListNode p = head; p != null; p = p.next) v.add(p.val);
    for (int l = 0, r = v.size() - 1; l < r; l++, r--) {
        if (!v.get(l).equals(v.get(r))) return false;
    }
    return true;
}"""),
 dict(name="Stack of the values",
      idea="Push all values; popping returns them in reverse order. Compare with a second walk from the head.",
      time="O(n)", space="O(n)",
      code="""public boolean isPalindrome(ListNode head) {
    Deque<Integer> st = new ArrayDeque<>();
    for (ListNode p = head; p != null; p = p.next) st.push(p.val);
    for (ListNode p = head; p != null; p = p.next) {
        if (p.val != st.pop()) return false;
    }
    return true;
}"""),
 dict(name="Find middle, reverse second half, compare (optimal)",
      idea="Fast/slow finds the middle; reverse the second half in place; compare it with the first half; reverse it back to restore the input.",
      time="O(n)", space="O(1)", best=True,
      code="""public boolean isPalindrome(ListNode head) {
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) { slow = slow.next; fast = fast.next.next; }
    ListNode second = reverse(slow), p = head, q = second;
    boolean ok = true;
    while (q != null) {
        if (p.val != q.val) { ok = false; break; }
        p = p.next;
        q = q.next;
    }
    reverse(second);                                   // restore the list
    return ok;
}
private ListNode reverse(ListNode head) {
    ListNode prev = null;
    while (head != null) { ListNode nx = head.next; head.next = prev; prev = head; head = nx; }
    return prev;
}"""),
],

"reorder-list": [
 dict(name="Copy nodes into an array, relink with two pointers",
      idea="Store nodes in a list, then link first, last, second, second-last, ... and terminate the end.",
      time="O(n)", space="O(n)",
      code="""public void reorderList(ListNode head) {
    List<ListNode> a = new ArrayList<>();
    for (ListNode p = head; p != null; p = p.next) a.add(p);
    int l = 0, r = a.size() - 1;
    while (l < r) {
        a.get(l).next = a.get(r);
        l++;
        if (l == r) break;
        a.get(r).next = a.get(l);
        r--;
    }
    if (!a.isEmpty()) a.get(l).next = null;
}"""),
 dict(name="Middle + reverse second half + merge (optimal)",
      idea="Three Day-6 tools in one: fast/slow to split, in-place reversal of the second half, then weave the two halves together.",
      time="O(n)", space="O(1)", best=True,
      code="""public void reorderList(ListNode head) {
    if (head == null || head.next == null) return;
    ListNode slow = head, fast = head;
    while (fast.next != null && fast.next.next != null) { slow = slow.next; fast = fast.next.next; }
    ListNode second = null, cur = slow.next;
    slow.next = null;
    while (cur != null) { ListNode nx = cur.next; cur.next = second; second = cur; cur = nx; }
    ListNode first = head;
    while (second != null) {
        ListNode n1 = first.next, n2 = second.next;
        first.next = second;
        second.next = n1;
        first = n1;
        second = n2;
    }
}"""),
],

"find-the-duplicate-number": [
 dict(name="Sort and compare neighbours",
      idea="After sorting, the duplicate sits next to itself. Modifies the input, which the problem forbids, but it is a fine first answer.",
      time="O(n log n)", space="O(log n) sort stack",
      code="""public int findDuplicate(int[] nums) {
    int[] a = nums.clone();
    Arrays.sort(a);
    for (int i = 1; i < a.length; i++) if (a[i] == a[i - 1]) return a[i];
    return -1;
}"""),
 dict(name="HashSet",
      idea="The first value that is already in the set is the duplicate.",
      time="O(n)", space="O(n)",
      code="""public int findDuplicate(int[] nums) {
    Set<Integer> seen = new HashSet<>();
    for (int x : nums) if (!seen.add(x)) return x;
    return -1;
}"""),
 dict(name="Binary search on the value (pigeonhole)",
      idea="For a guess mid, count values <= mid. If the count is greater than mid, the duplicate is in [1, mid]; otherwise it is above mid.",
      time="O(n log n)", space="O(1)",
      code="""public int findDuplicate(int[] nums) {
    int lo = 1, hi = nums.length - 1;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2, count = 0;
        for (int x : nums) if (x <= mid) count++;
        if (count > mid) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}"""),
 dict(name="Floyd's cycle detection on indices (optimal)",
      idea="Treat i -> nums[i] as a linked list. Two indices point to the duplicate value, so it is the entrance of a cycle: find it exactly like Linked List Cycle II.",
      time="O(n)", space="O(1)", best=True,
      code="""public int findDuplicate(int[] nums) {
    int slow = nums[0], fast = nums[0];
    do {
        slow = nums[slow];
        fast = nums[nums[fast]];
    } while (slow != fast);
    slow = nums[0];
    while (slow != fast) { slow = nums[slow]; fast = nums[fast]; }
    return slow;
}"""),
],

"circular-array-loop": [
 dict(name="Simulate from every start with a visited set",
      idea="From each index, follow the jumps while the direction stays the same. If an index repeats, there is a loop; it counts only if it is longer than one element.",
      time="O(n^2)", space="O(n)",
      code="""public boolean circularArrayLoop(int[] nums) {
    int n = nums.length;
    for (int i = 0; i < n; i++) {
        Set<Integer> seen = new HashSet<>();
        boolean forward = nums[i] > 0;
        int j = i;
        while ((nums[j] > 0) == forward) {
            if (!seen.add(j)) {
                if (next(nums, j) != j) return true;
                break;
            }
            j = next(nums, j);
        }
    }
    return false;
}
private int next(int[] a, int i) {
    int n = a.length;
    return ((i + a[i]) % n + n) % n;
}"""),
 dict(name="Fast & slow pointers + mark dead ends (optimal)",
      idea="From each start run Floyd while every step keeps the same direction. A meeting means a loop unless it is a one-element self loop. Afterwards set every index on the failed path to 0 so it is never explored again.",
      time="O(n)", space="O(1)", best=True,
      code="""public boolean circularArrayLoop(int[] nums) {
    int n = nums.length;
    for (int i = 0; i < n; i++) {
        if (nums[i] == 0) continue;
        int slow = i, fast = next(nums, i);
        while (nums[fast] * nums[i] > 0 && nums[next(nums, fast)] * nums[i] > 0) {
            if (slow == fast) {
                if (slow == next(nums, slow)) break;      // one-element loop does not count
                return true;
            }
            slow = next(nums, slow);
            fast = next(nums, next(nums, fast));
        }
        int j = i, sign = nums[i];
        while (nums[j] != 0 && nums[j] * sign > 0) {       // mark this path as explored
            int nx = next(nums, j);
            nums[j] = 0;
            j = nx;
        }
    }
    return false;
}
private int next(int[] a, int i) {
    int n = a.length;
    return ((i + a[i]) % n + n) % n;
}"""),
],
}

TESTS = {
 "linked-list-cycle": [("!r = o.{m}(cyclic(new int[]{3,2,0,-4}, 1));", "true"), ("!r = o.{m}(cyclic(new int[]{1,2}, 0));", "true"),
                       ("!r = o.{m}(cyclic(new int[]{1}, -1));", "false"), ("!r = o.{m}(list());", "false")],
 "linked-list-cycle-ii": [("!ListNode x = o.{m}(cyclic(new int[]{3,2,0,-4}, 1)); r = x == null ? null : x.val;", "2"),
                          ("!ListNode x = o.{m}(cyclic(new int[]{1,2}, 0)); r = x == null ? null : x.val;", "1"),
                          ("!ListNode x = o.{m}(cyclic(new int[]{1}, -1)); r = x == null ? null : x.val;", "null")],
 "middle-of-the-linked-list": [("!r = toList(o.{m}(list(1,2,3,4,5)));", "[3, 4, 5]"), ("!r = toList(o.{m}(list(1,2,3,4,5,6)));", "[4, 5, 6]"),
                               ("!r = toList(o.{m}(list(1)));", "[1]")],
 "happy-number": [("19", "true"), ("2", "false"), ("1", "true"), ("7", "true")],
 "palindrome-linked-list": [("!ListNode h = list(1,2,2,1); r = o.{m}(h) + toList(h);", "true[1, 2, 2, 1]"),
                            ("!r = o.{m}(list(1,2));", "false"), ("!r = o.{m}(list(1,2,3,2,1));", "true"), ("!r = o.{m}(list(1));", "true")],
 "reorder-list": [("!ListNode h = list(1,2,3,4); o.{m}(h); r = toList(h);", "[1, 4, 2, 3]"),
                  ("!ListNode h = list(1,2,3,4,5); o.{m}(h); r = toList(h);", "[1, 5, 2, 4, 3]"),
                  ("!ListNode h = list(1); o.{m}(h); r = toList(h);", "[1]")],
 "find-the-duplicate-number": [("new int[]{1,3,4,2,2}", "2"), ("new int[]{3,1,3,4,2}", "3"), ("new int[]{3,3,3,3,3}", "3")],
 "circular-array-loop": [("new int[]{2,-1,1,2,2}", "true"), ("new int[]{-1,-2,-3,-4,-5,6}", "false"), ("new int[]{1,-1,5,1,4}", "true"),
                         ("new int[]{-1,2}", "false"), ("new int[]{1,1}", "true")],
}
