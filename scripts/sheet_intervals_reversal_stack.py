"""Approaches for the Merge Intervals, In-place LinkedList Reversal and Stack questions
from the Padho with Pratyush practice sheet (Java only)."""

SOL = {

# ------------------------------------------------------------------ Merge intervals
"merge-intervals": [
 dict(name="Merge each interval into everything it overlaps",
      idea="Process intervals one by one; absorb every already-kept interval that overlaps the current one, then keep the merged result. Sort the output at the end.",
      time="O(n^2)", space="O(n)",
      code="""public int[][] merge(int[][] intervals) {
    List<int[]> kept = new ArrayList<>();
    for (int[] in : intervals) {
        int[] cur = {in[0], in[1]};
        Iterator<int[]> it = kept.iterator();
        while (it.hasNext()) {
            int[] k = it.next();
            if (k[0] <= cur[1] && cur[0] <= k[1]) {
                cur[0] = Math.min(cur[0], k[0]);
                cur[1] = Math.max(cur[1], k[1]);
                it.remove();
            }
        }
        kept.add(cur);
    }
    kept.sort((a, b) -> Integer.compare(a[0], b[0]));
    return kept.toArray(new int[0][]);
}"""),
 dict(name="Sort by start, then one merge pass (optimal)",
      idea="After sorting, an interval overlaps the last merged one exactly when its start <= that end; extend the end, otherwise start a new interval.",
      time="O(n log n)", space="O(n) output", best=True,
      code="""public int[][] merge(int[][] intervals) {
    Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
    List<int[]> out = new ArrayList<>();
    for (int[] cur : intervals) {
        if (out.isEmpty() || out.get(out.size() - 1)[1] < cur[0]) out.add(new int[]{cur[0], cur[1]});
        else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);
    }
    return out.toArray(new int[0][]);
}"""),
],

"insert-interval": [
 dict(name="Append, sort, merge",
      idea="Add the new interval and reuse the Merge Intervals solution. Ignores that the input is already sorted.",
      time="O(n log n)", space="O(n)",
      code="""public int[][] insert(int[][] intervals, int[] newInterval) {
    List<int[]> all = new ArrayList<>(Arrays.asList(intervals));
    all.add(newInterval);
    all.sort((a, b) -> Integer.compare(a[0], b[0]));
    List<int[]> out = new ArrayList<>();
    for (int[] cur : all) {
        if (out.isEmpty() || out.get(out.size() - 1)[1] < cur[0]) out.add(new int[]{cur[0], cur[1]});
        else out.get(out.size() - 1)[1] = Math.max(out.get(out.size() - 1)[1], cur[1]);
    }
    return out.toArray(new int[0][]);
}"""),
 dict(name="One linear pass in three phases (optimal)",
      idea="Copy intervals that end before the new one starts; merge every interval that overlaps it into it; copy the rest.",
      time="O(n)", space="O(n) output", best=True,
      code="""public int[][] insert(int[][] intervals, int[] newInterval) {
    List<int[]> out = new ArrayList<>();
    int i = 0, n = intervals.length;
    int s = newInterval[0], e = newInterval[1];
    while (i < n && intervals[i][1] < s) out.add(intervals[i++]);
    while (i < n && intervals[i][0] <= e) {
        s = Math.min(s, intervals[i][0]);
        e = Math.max(e, intervals[i][1]);
        i++;
    }
    out.add(new int[]{s, e});
    while (i < n) out.add(intervals[i++]);
    return out.toArray(new int[0][]);
}"""),
],

"interval-list-intersections": [
 dict(name="Check every pair",
      idea="Intersect every interval of the first list with every interval of the second. Both lists are sorted and disjoint, so the results come out in order.",
      time="O(m x n)", space="O(1) besides output",
      code="""public int[][] intervalIntersection(int[][] firstList, int[][] secondList) {
    List<int[]> out = new ArrayList<>();
    for (int[] a : firstList)
        for (int[] b : secondList) {
            int lo = Math.max(a[0], b[0]), hi = Math.min(a[1], b[1]);
            if (lo <= hi) out.add(new int[]{lo, hi});
        }
    return out.toArray(new int[0][]);
}"""),
 dict(name="Two pointers (optimal)",
      idea="The intersection of the current pair is [max start, min end] if non-empty. Then advance whichever interval ends first, because it cannot meet anything later.",
      time="O(m + n)", space="O(1) besides output", best=True,
      code="""public int[][] intervalIntersection(int[][] firstList, int[][] secondList) {
    List<int[]> out = new ArrayList<>();
    int i = 0, j = 0;
    while (i < firstList.length && j < secondList.length) {
        int lo = Math.max(firstList[i][0], secondList[j][0]);
        int hi = Math.min(firstList[i][1], secondList[j][1]);
        if (lo <= hi) out.add(new int[]{lo, hi});
        if (firstList[i][1] < secondList[j][1]) i++;
        else j++;
    }
    return out.toArray(new int[0][]);
}"""),
],

"gfg-check-if-any-two-intervals-overlap": [
 dict(name="Check every pair",
      idea="Two intervals overlap when each starts before the other ends.",
      time="O(n^2)", space="O(1)",
      code="""public boolean isOverlap(int[][] arr) {
    for (int i = 0; i < arr.length; i++)
        for (int j = i + 1; j < arr.length; j++)
            if (arr[i][0] < arr[j][1] && arr[j][0] < arr[i][1]) return true;
    return false;
}"""),
 dict(name="Sort by start, compare neighbours (optimal for any values)",
      idea="After sorting by start, if any two intervals overlap then some adjacent pair overlaps: check start[i] < end[i-1].",
      time="O(n log n)", space="O(log n) sort stack", best=True,
      code="""public boolean isOverlap(int[][] arr) {
    int[][] a = arr.clone();
    Arrays.sort(a, (x, y) -> Integer.compare(x[0], y[0]));
    for (int i = 1; i < a.length; i++) if (a[i][0] < a[i - 1][1]) return true;
    return false;
}"""),
 dict(name="Difference array over the time range",
      idea="When times are small non-negative integers, mark +1 at each start and -1 at each end; if the running count ever exceeds 1, two intervals overlap.",
      time="O(n + maxTime)", space="O(maxTime)",
      code="""public boolean isOverlap(int[][] arr) {
    int max = 0;
    for (int[] x : arr) max = Math.max(max, x[1]);
    int[] diff = new int[max + 2];
    for (int[] x : arr) { diff[x[0]]++; diff[x[1]]--; }
    int run = 0;
    for (int t = 0; t <= max; t++) {
        run += diff[t];
        if (run > 1) return true;
    }
    return false;
}"""),
],

"gfg-attend-all-meetings-ii": [
 dict(name="Count meetings running at each start time",
      idea="The rooms needed is the largest number of meetings in progress at any meeting's start time.",
      time="O(n^2)", space="O(1)",
      code="""public int minMeetingRooms(int[] start, int[] end) {
    int best = 0;
    for (int i = 0; i < start.length; i++) {
        int running = 0;
        for (int j = 0; j < start.length; j++)
            if (start[j] <= start[i] && start[i] < end[j]) running++;
        best = Math.max(best, running);
    }
    return best;
}"""),
 dict(name="Sort by start + min-heap of end times",
      idea="Process meetings by start time. The heap holds the end times of rooms in use; if the earliest one has ended, reuse that room.",
      time="O(n log n)", space="O(n)",
      code="""public int minMeetingRooms(int[] start, int[] end) {
    int n = start.length;
    Integer[] idx = new Integer[n];
    for (int i = 0; i < n; i++) idx[i] = i;
    Arrays.sort(idx, (a, b) -> Integer.compare(start[a], start[b]));
    PriorityQueue<Integer> ends = new PriorityQueue<>();
    for (int i : idx) {
        if (!ends.isEmpty() && ends.peek() <= start[i]) ends.poll();
        ends.offer(end[i]);
    }
    return ends.size();
}"""),
 dict(name="Sorted starts and sorted ends, two pointers (optimal)",
      idea="Walk the sorted start times; a room frees up whenever the next end time is <= the current start. Track the peak number of rooms in use.",
      time="O(n log n)", space="O(n)", best=True,
      code="""public int minMeetingRooms(int[] start, int[] end) {
    int[] s = start.clone(), e = end.clone();
    Arrays.sort(s);
    Arrays.sort(e);
    int rooms = 0, best = 0, j = 0;
    for (int i = 0; i < s.length; i++) {
        while (e[j] <= s[i]) { j++; rooms--; }
        rooms++;
        best = Math.max(best, rooms);
    }
    return best;
}"""),
],

"gfg-maximum-cpu-load": [
 dict(name="Sum the loads running at each job's start",
      idea="The peak load happens at some job's start time: add up the loads of all jobs running at that moment.",
      time="O(n^2)", space="O(1)",
      code="""public int maxCPULoad(int[][] jobs) {
    int best = 0;
    for (int[] a : jobs) {
        int load = 0;
        for (int[] b : jobs) if (b[0] <= a[0] && a[0] < b[1]) load += b[2];
        best = Math.max(best, load);
    }
    return best;
}"""),
 dict(name="Sort by start + min-heap by end time (optimal)",
      idea="Process jobs by start time; remove finished jobs (end <= current start) from a heap ordered by end, subtracting their load; add the current job and track the peak.",
      time="O(n log n)", space="O(n)", best=True,
      code="""public int maxCPULoad(int[][] jobs) {
    int[][] a = jobs.clone();
    Arrays.sort(a, (x, y) -> Integer.compare(x[0], y[0]));
    PriorityQueue<int[]> running = new PriorityQueue<>((x, y) -> Integer.compare(x[1], y[1]));
    int load = 0, best = 0;
    for (int[] job : a) {
        while (!running.isEmpty() && running.peek()[1] <= job[0]) load -= running.poll()[2];
        running.offer(job);
        load += job[2];
        best = Math.max(best, load);
    }
    return best;
}"""),
],

"codertrain-employee-free-time": [
 dict(name="Flatten, sort, merge, read the gaps",
      idea="Put every working interval of every employee in one list, sort by start, merge overlaps; the gaps between merged intervals are the common free time.",
      time="O(N log N) for N intervals", space="O(N)",
      code="""public int[][] employeeFreeTime(int[][][] schedule) {
    List<int[]> all = new ArrayList<>();
    for (int[][] emp : schedule) all.addAll(Arrays.asList(emp));
    all.sort((a, b) -> Integer.compare(a[0], b[0]));
    List<int[]> free = new ArrayList<>();
    int end = all.get(0)[1];
    for (int[] cur : all) {
        if (cur[0] > end) free.add(new int[]{end, cur[0]});
        end = Math.max(end, cur[1]);
    }
    return free.toArray(new int[0][]);
}"""),
 dict(name="K-way merge with a min-heap (optimal)",
      idea="Each employee's list is already sorted. A heap holding one interval per employee yields all intervals in start order without a full sort; track the latest end and record gaps.",
      time="O(N log k) for k employees", space="O(k)", best=True,
      code="""public int[][] employeeFreeTime(int[][][] schedule) {
    PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> Integer.compare(schedule[a[0]][a[1]][0], schedule[b[0]][b[1]][0]));
    for (int e = 0; e < schedule.length; e++) if (schedule[e].length > 0) pq.offer(new int[]{e, 0});
    List<int[]> free = new ArrayList<>();
    int end = -1;
    while (!pq.isEmpty()) {
        int[] top = pq.poll();
        int[] cur = schedule[top[0]][top[1]];
        if (end != -1 && cur[0] > end) free.add(new int[]{end, cur[0]});
        end = Math.max(end, cur[1]);
        if (top[1] + 1 < schedule[top[0]].length) pq.offer(new int[]{top[0], top[1] + 1});
    }
    return free.toArray(new int[0][]);
}"""),
],

# ------------------------------------------------------------------ In-place reversal
"reverse-linked-list": [
 dict(name="Stack of nodes",
      idea="Push every node, then pop them to relink in reverse order.",
      time="O(n)", space="O(n)",
      code="""public ListNode reverseList(ListNode head) {
    Deque<ListNode> st = new ArrayDeque<>();
    for (ListNode p = head; p != null; p = p.next) st.push(p);
    ListNode dummy = new ListNode(0), tail = dummy;
    while (!st.isEmpty()) { tail.next = st.pop(); tail = tail.next; }
    tail.next = null;
    return dummy.next;
}"""),
 dict(name="Recursion",
      idea="Reverse the rest of the list, then make the next node point back to head and cut head's old link.",
      time="O(n)", space="O(n) recursion stack",
      code="""public ListNode reverseList(ListNode head) {
    if (head == null || head.next == null) return head;
    ListNode newHead = reverseList(head.next);
    head.next.next = head;
    head.next = null;
    return newHead;
}"""),
 dict(name="Iterative pointer reversal (optimal)",
      idea="prev / cur / next: save next, point cur back to prev, move both forward.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode reverseList(ListNode head) {
    ListNode prev = null, cur = head;
    while (cur != null) {
        ListNode next = cur.next;
        cur.next = prev;
        prev = cur;
        cur = next;
    }
    return prev;
}"""),
],

"reverse-linked-list-ii": [
 dict(name="Copy values, reverse the range, write back",
      idea="Read values into an array, reverse positions left..right, write them back. Changes values instead of links.",
      time="O(n)", space="O(n)",
      code="""public ListNode reverseBetween(ListNode head, int left, int right) {
    List<Integer> v = new ArrayList<>();
    for (ListNode p = head; p != null; p = p.next) v.add(p.val);
    Collections.reverse(v.subList(left - 1, right));
    ListNode p = head;
    for (int x : v) { p.val = x; p = p.next; }
    return head;
}"""),
 dict(name="One pass: move each node to the front of the range (optimal)",
      idea="With a dummy head, walk to the node before position left. Then right - left times, take the node after the range start and insert it right after that node.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode reverseBetween(ListNode head, int left, int right) {
    ListNode dummy = new ListNode(0, head), before = dummy;
    for (int i = 1; i < left; i++) before = before.next;
    ListNode start = before.next;
    for (int i = 0; i < right - left; i++) {
        ListNode move = start.next;
        start.next = move.next;
        move.next = before.next;
        before.next = move;
    }
    return dummy.next;
}"""),
],

"swap-nodes-in-pairs": [
 dict(name="Swap the values",
      idea="Swap the values of each pair. Simple, but interviewers usually forbid changing values (only links), so mention it and move on.",
      time="O(n)", space="O(1)",
      code="""public ListNode swapPairs(ListNode head) {
    for (ListNode p = head; p != null && p.next != null; p = p.next.next) {
        int t = p.val; p.val = p.next.val; p.next.val = t;
    }
    return head;
}"""),
 dict(name="Recursion",
      idea="Swap the first two nodes, and attach the result of swapping the rest.",
      time="O(n)", space="O(n) recursion stack",
      code="""public ListNode swapPairs(ListNode head) {
    if (head == null || head.next == null) return head;
    ListNode second = head.next;
    head.next = swapPairs(second.next);
    second.next = head;
    return second;
}"""),
 dict(name="Iterative with a dummy head (optimal)",
      idea="prev points to the node before the pair; relink prev -> second -> first -> rest, then move prev to first.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode swapPairs(ListNode head) {
    ListNode dummy = new ListNode(0, head), prev = dummy;
    while (prev.next != null && prev.next.next != null) {
        ListNode a = prev.next, b = a.next;
        a.next = b.next;
        b.next = a;
        prev.next = b;
        prev = a;
    }
    return dummy.next;
}"""),
],

"reverse-nodes-in-k-group": [
 dict(name="Stack per group",
      idea="Push k nodes; if there are k, pop them to relink reversed; a final short group stays as it is.",
      time="O(n)", space="O(k)",
      code="""public ListNode reverseKGroup(ListNode head, int k) {
    ListNode dummy = new ListNode(0), tail = dummy, p = head;
    Deque<ListNode> st = new ArrayDeque<>();
    while (p != null) {
        ListNode q = p;
        int c = 0;
        while (q != null && c < k) { st.push(q); q = q.next; c++; }
        if (c < k) { tail.next = p; return dummy.next; }
        while (!st.isEmpty()) { tail.next = st.pop(); tail = tail.next; }
        tail.next = null;
        p = q;
    }
    return dummy.next;
}"""),
 dict(name="Recursion",
      idea="Check that k nodes exist; reverse them; their old head becomes the tail and links to the recursively processed rest.",
      time="O(n)", space="O(n / k) recursion stack",
      code="""public ListNode reverseKGroup(ListNode head, int k) {
    ListNode p = head;
    for (int i = 0; i < k; i++) { if (p == null) return head; p = p.next; }
    ListNode prev = reverseKGroup(p, k), cur = head;
    for (int i = 0; i < k; i++) {
        ListNode nx = cur.next;
        cur.next = prev;
        prev = cur;
        cur = nx;
    }
    return prev;
}"""),
 dict(name="Iterative, group by group (optimal)",
      idea="groupPrev sits before each group. Find the k-th node; if missing, stop. Reverse the group with its next node as the starting 'prev', then reconnect and move groupPrev to the group's new tail.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode reverseKGroup(ListNode head, int k) {
    ListNode dummy = new ListNode(0, head), groupPrev = dummy;
    while (true) {
        ListNode kth = groupPrev;
        for (int i = 0; i < k && kth != null; i++) kth = kth.next;
        if (kth == null) break;
        ListNode groupNext = kth.next, prev = groupNext, cur = groupPrev.next;
        while (cur != groupNext) {
            ListNode nx = cur.next;
            cur.next = prev;
            prev = cur;
            cur = nx;
        }
        ListNode newTail = groupPrev.next;
        groupPrev.next = kth;
        groupPrev = newTail;
    }
    return dummy.next;
}"""),
],

"rotate-list": [
 dict(name="Rotate one step at a time",
      idea="Move the last node to the front, k mod n times.",
      time="O(n x (k mod n))", space="O(1)",
      code="""public ListNode rotateRight(ListNode head, int k) {
    if (head == null || head.next == null) return head;
    int n = 0;
    for (ListNode p = head; p != null; p = p.next) n++;
    for (int step = 0; step < k % n; step++) {
        ListNode prev = null, last = head;
        while (last.next != null) { prev = last; last = last.next; }
        prev.next = null;
        last.next = head;
        head = last;
    }
    return head;
}"""),
 dict(name="Copy values into an array",
      idea="Value at new position (i + k) mod n comes from position i; write the rotated values back.",
      time="O(n)", space="O(n)",
      code="""public ListNode rotateRight(ListNode head, int k) {
    List<Integer> v = new ArrayList<>();
    for (ListNode p = head; p != null; p = p.next) v.add(p.val);
    int n = v.size();
    if (n == 0) return head;
    Collections.rotate(v, k % n);
    ListNode p = head;
    for (int x : v) { p.val = x; p = p.next; }
    return head;
}"""),
 dict(name="Close into a ring, cut at the right place (optimal)",
      idea="Find the length and tail, link tail to head, walk n - k mod n steps to the new tail, and break the ring there.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode rotateRight(ListNode head, int k) {
    if (head == null || head.next == null || k == 0) return head;
    int n = 1;
    ListNode tail = head;
    while (tail.next != null) { tail = tail.next; n++; }
    k %= n;
    if (k == 0) return head;
    tail.next = head;
    ListNode newTail = head;
    for (int i = 1; i < n - k; i++) newTail = newTail.next;
    ListNode newHead = newTail.next;
    newTail.next = null;
    return newHead;
}"""),
],

"reverse-nodes-in-even-length-groups": [
 dict(name="Copy values, reverse even-length groups, write back",
      idea="Groups have sizes 1, 2, 3, ... (the last may be shorter). Reverse the values of every group whose actual length is even.",
      time="O(n)", space="O(n)",
      code="""public ListNode reverseEvenLengthGroups(ListNode head) {
    List<Integer> v = new ArrayList<>();
    for (ListNode p = head; p != null; p = p.next) v.add(p.val);
    int start = 0, size = 1, n = v.size();
    while (start < n) {
        int len = Math.min(size, n - start);
        if (len % 2 == 0) Collections.reverse(v.subList(start, start + len));
        start += len;
        size++;
    }
    ListNode p = head;
    for (int x : v) { p.val = x; p = p.next; }
    return head;
}"""),
 dict(name="Walk group by group, reverse links in place (optimal)",
      idea="prev is the node before the group. Count the group's real length; if even, reverse exactly that many nodes and reconnect; otherwise just skip them.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode reverseEvenLengthGroups(ListNode head) {
    ListNode prev = head;
    int size = 2;
    while (prev.next != null) {
        int cnt = 0;
        ListNode after = prev.next;
        while (cnt < size && after != null) { cnt++; after = after.next; }
        if (cnt % 2 == 0) {
            ListNode cur = prev.next, groupTail = cur, pr = after;
            for (int i = 0; i < cnt; i++) {
                ListNode nx = cur.next;
                cur.next = pr;
                pr = cur;
                cur = nx;
            }
            prev.next = pr;
            prev = groupTail;
        } else {
            for (int i = 0; i < cnt; i++) prev = prev.next;
        }
        size++;
    }
    return head;
}"""),
],

# ------------------------------------------------------------------ Stack
"valid-parentheses": [
 dict(name="Repeatedly remove matched pairs",
      idea="Delete every '()', '[]' and '{}' until nothing changes; the string is valid if it becomes empty.",
      time="O(n^2)", space="O(n)",
      code="""public boolean isValid(String s) {
    String prev;
    do {
        prev = s;
        s = s.replace("()", "").replace("[]", "").replace("{}", "");
    } while (!s.equals(prev));
    return s.isEmpty();
}"""),
 dict(name="Stack of expected closers (optimal)",
      idea="For each opener push the closer it needs; for each closer, the top of the stack must be exactly that closer. Valid if the stack is empty at the end.",
      time="O(n)", space="O(n)", best=True,
      code="""public boolean isValid(String s) {
    Deque<Character> st = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        if (c == '(') st.push(')');
        else if (c == '[') st.push(']');
        else if (c == '{') st.push('}');
        else if (st.isEmpty() || st.pop() != c) return false;
    }
    return st.isEmpty();
}"""),
],

"daily-temperatures": [
 dict(name="Brute force: scan right for each day",
      idea="For every day look ahead for the first warmer day.",
      time="O(n^2)", space="O(1) besides output",
      code="""public int[] dailyTemperatures(int[] temperatures) {
    int n = temperatures.length;
    int[] ans = new int[n];
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            if (temperatures[j] > temperatures[i]) { ans[i] = j - i; break; }
    return ans;
}"""),
 dict(name="Monotonic decreasing stack (optimal)",
      idea="Keep indices of days still waiting for a warmer day, temperatures decreasing. A warmer day pops every cooler waiting day and fills in its answer.",
      time="O(n)", space="O(n)", best=True,
      code="""public int[] dailyTemperatures(int[] temperatures) {
    int n = temperatures.length;
    int[] ans = new int[n];
    Deque<Integer> st = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {
        while (!st.isEmpty() && temperatures[i] > temperatures[st.peek()]) {
            int j = st.pop();
            ans[j] = i - j;
        }
        st.push(i);
    }
    return ans;
}"""),
 dict(name="Right to left, jump using answers already found",
      idea="Going backwards, to find the next warmer day after i, start at i + 1 and jump by its known answer instead of stepping one day at a time.",
      time="O(n) amortised", space="O(1) besides output",
      code="""public int[] dailyTemperatures(int[] temperatures) {
    int n = temperatures.length;
    int[] ans = new int[n];
    for (int i = n - 2; i >= 0; i--) {
        int j = i + 1;
        while (j < n && temperatures[j] <= temperatures[i]) {
            if (ans[j] == 0) { j = n; break; }
            j += ans[j];
        }
        if (j < n) ans[i] = j - i;
    }
    return ans;
}"""),
],

"next-greater-element-ii": [
 dict(name="Brute force: walk around the circle",
      idea="For each index, check the next n - 1 positions (mod n) for a greater value.",
      time="O(n^2)", space="O(1) besides output",
      code="""public int[] nextGreaterElements(int[] nums) {
    int n = nums.length;
    int[] ans = new int[n];
    Arrays.fill(ans, -1);
    for (int i = 0; i < n; i++)
        for (int d = 1; d < n; d++)
            if (nums[(i + d) % n] > nums[i]) { ans[i] = nums[(i + d) % n]; break; }
    return ans;
}"""),
 dict(name="Monotonic stack over two passes (optimal)",
      idea="Loop i from 0 to 2n - 1 using i mod n, so elements near the end can see the start. Pop smaller waiting indices and give them the current value.",
      time="O(n)", space="O(n)", best=True,
      code="""public int[] nextGreaterElements(int[] nums) {
    int n = nums.length;
    int[] ans = new int[n];
    Arrays.fill(ans, -1);
    Deque<Integer> st = new ArrayDeque<>();
    for (int i = 0; i < 2 * n; i++) {
        int x = nums[i % n];
        while (!st.isEmpty() && nums[st.peek()] < x) ans[st.pop()] = x;
        if (i < n) st.push(i);
    }
    return ans;
}"""),
],

"remove-k-digits": [
 dict(name="Greedy, remove one digit k times",
      idea="To shrink a number the most, delete the first digit that is bigger than the digit after it (or the last digit). Repeat k times.",
      time="O(n x k)", space="O(n)",
      code="""public String removeKdigits(String num, int k) {
    StringBuilder sb = new StringBuilder(num);
    for (int t = 0; t < k; t++) {
        int i = 0;
        while (i < sb.length() - 1 && sb.charAt(i) <= sb.charAt(i + 1)) i++;
        sb.deleteCharAt(i);
    }
    int z = 0;
    while (z < sb.length() - 1 && sb.charAt(z) == '0') z++;
    String res = sb.substring(z);
    return res.isEmpty() ? "0" : res;
}"""),
 dict(name="Monotonic increasing stack (optimal)",
      idea="Same greedy rule in one pass: while k > 0 and the previous digit is bigger than the current one, pop it. Remove any remaining k from the end, then strip leading zeros.",
      time="O(n)", space="O(n)", best=True,
      code="""public String removeKdigits(String num, int k) {
    StringBuilder st = new StringBuilder();
    for (char c : num.toCharArray()) {
        while (k > 0 && st.length() > 0 && st.charAt(st.length() - 1) > c) {
            st.deleteCharAt(st.length() - 1);
            k--;
        }
        st.append(c);
    }
    st.setLength(st.length() - k);
    int z = 0;
    while (z < st.length() - 1 && st.charAt(z) == '0') z++;
    String res = st.substring(z);
    return res.isEmpty() ? "0" : res;
}"""),
],

"remove-all-adjacent-duplicates-in-string": [
 dict(name="Repeatedly remove a pair",
      idea="Scan for two equal neighbours, remove them, and start again until there are none.",
      time="O(n^2)", space="O(n)",
      code="""public String removeDuplicates(String s) {
    StringBuilder sb = new StringBuilder(s);
    boolean changed = true;
    while (changed) {
        changed = false;
        for (int i = 0; i + 1 < sb.length(); i++) {
            if (sb.charAt(i) == sb.charAt(i + 1)) { sb.delete(i, i + 2); changed = true; break; }
        }
    }
    return sb.toString();
}"""),
 dict(name="Stack (a StringBuilder used as one) (optimal)",
      idea="Push each character; if it equals the top, pop instead. What is left is the answer.",
      time="O(n)", space="O(n)", best=True,
      code="""public String removeDuplicates(String s) {
    StringBuilder st = new StringBuilder();
    for (char c : s.toCharArray()) {
        int n = st.length();
        if (n > 0 && st.charAt(n - 1) == c) st.deleteCharAt(n - 1);
        else st.append(c);
    }
    return st.toString();
}"""),
],

"remove-all-adjacent-duplicates-in-string-ii": [
 dict(name="Repeatedly remove a run of k",
      idea="Find any run of k equal characters, delete it, and repeat until no run of k remains.",
      time="O(n^2 / k)", space="O(n)",
      code="""public String removeDuplicates(String s, int k) {
    StringBuilder sb = new StringBuilder(s);
    boolean changed = true;
    while (changed) {
        changed = false;
        int run = 1;
        for (int i = 1; i < sb.length(); i++) {
            run = sb.charAt(i) == sb.charAt(i - 1) ? run + 1 : 1;
            if (run == k) { sb.delete(i - k + 1, i + 1); changed = true; break; }
        }
    }
    return sb.toString();
}"""),
 dict(name="Stack of (character, count) (optimal)",
      idea="Keep the current run length on a count stack alongside the characters. When a run reaches k, delete those k characters at once.",
      time="O(n)", space="O(n)", best=True,
      code="""public String removeDuplicates(String s, int k) {
    StringBuilder sb = new StringBuilder();
    int[] count = new int[s.length()];
    for (char c : s.toCharArray()) {
        int n = sb.length();
        sb.append(c);
        count[n] = (n > 0 && sb.charAt(n - 1) == c) ? count[n - 1] + 1 : 1;
        if (count[n] == k) sb.setLength(n + 1 - k);
    }
    return sb.toString();
}"""),
],

"reverse-string": [
 dict(name="Copy into a new array",
      idea="Write characters into a new array in reverse order, then copy back. Uses extra memory, which the problem forbids.",
      time="O(n)", space="O(n)",
      code="""public void reverseString(char[] s) {
    char[] copy = new char[s.length];
    for (int i = 0; i < s.length; i++) copy[i] = s[s.length - 1 - i];
    System.arraycopy(copy, 0, s, 0, s.length);
}"""),
 dict(name="Stack",
      idea="Push every character, then pop them back in reverse order.",
      time="O(n)", space="O(n)",
      code="""public void reverseString(char[] s) {
    Deque<Character> st = new ArrayDeque<>();
    for (char c : s) st.push(c);
    for (int i = 0; i < s.length; i++) s[i] = st.pop();
}"""),
 dict(name="Two pointers, swap in place (optimal)",
      idea="Swap the two ends and move inward.",
      time="O(n)", space="O(1)", best=True,
      code="""public void reverseString(char[] s) {
    for (int l = 0, r = s.length - 1; l < r; l++, r--) {
        char t = s[l]; s[l] = s[r]; s[r] = t;
    }
}"""),
],

"remove-nodes-from-linked-list": [
 dict(name="Brute force: check everything to the right",
      idea="Keep a node only if no node after it has a larger value.",
      time="O(n^2)", space="O(1)",
      code="""public ListNode removeNodes(ListNode head) {
    ListNode dummy = new ListNode(0), tail = dummy;
    for (ListNode p = head; p != null; p = p.next) {
        boolean keep = true;
        for (ListNode q = p.next; q != null; q = q.next) if (q.val > p.val) { keep = false; break; }
        if (keep) { tail.next = p; tail = p; }
    }
    tail.next = null;
    return dummy.next;
}"""),
 dict(name="Monotonic stack",
      idea="Push nodes; before pushing, pop every node smaller than the new one (it has a greater node to its right). The stack, bottom to top, is the answer.",
      time="O(n)", space="O(n)",
      code="""public ListNode removeNodes(ListNode head) {
    Deque<ListNode> st = new ArrayDeque<>();
    for (ListNode p = head; p != null; p = p.next) {
        while (!st.isEmpty() && st.peek().val < p.val) st.pop();
        st.push(p);
    }
    ListNode next = null;
    while (!st.isEmpty()) { ListNode cur = st.pop(); cur.next = next; next = cur; }
    return next;
}"""),
 dict(name="Recursion",
      idea="Process the rest first; then keep head only if it is not smaller than the first kept node after it.",
      time="O(n)", space="O(n) recursion stack",
      code="""public ListNode removeNodes(ListNode head) {
    if (head == null) return null;
    head.next = removeNodes(head.next);
    return (head.next != null && head.next.val > head.val) ? head.next : head;
}"""),
 dict(name="Reverse, keep a running maximum, reverse back (optimal)",
      idea="From the right, a node survives if it is at least the maximum seen so far. Reverse the list to walk it right-to-left, drop smaller nodes, and reverse again.",
      time="O(n)", space="O(1)", best=True,
      code="""public ListNode removeNodes(ListNode head) {
    head = reverse(head);
    int max = head.val;
    ListNode cur = head;
    while (cur.next != null) {
        if (cur.next.val < max) cur.next = cur.next.next;
        else { cur = cur.next; max = cur.val; }
    }
    return reverse(head);
}
private ListNode reverse(ListNode h) {
    ListNode prev = null;
    while (h != null) { ListNode nx = h.next; h.next = prev; prev = h; h = nx; }
    return prev;
}"""),
],

"simplify-path": [
 dict(name="Parse character by character",
      idea="Read one name between slashes at a time without split(); '..' removes the last kept name, '.' and empty names are ignored.",
      time="O(n)", space="O(n)",
      code="""public String simplifyPath(String path) {
    List<String> parts = new ArrayList<>();
    int i = 0, n = path.length();
    while (i < n) {
        while (i < n && path.charAt(i) == '/') i++;
        int j = i;
        while (j < n && path.charAt(j) != '/') j++;
        String name = path.substring(i, j);
        if (name.equals("..")) { if (!parts.isEmpty()) parts.remove(parts.size() - 1); }
        else if (!name.isEmpty() && !name.equals(".")) parts.add(name);
        i = j;
    }
    return "/" + String.join("/", parts);
}"""),
 dict(name="Split on '/' + stack (optimal, clearest)",
      idea="Split by '/', push real names on a stack, pop on '..', skip '.' and empty parts; join what remains.",
      time="O(n)", space="O(n)", best=True,
      code="""public String simplifyPath(String path) {
    Deque<String> st = new ArrayDeque<>();
    for (String part : path.split("/")) {
        if (part.equals("..")) { if (!st.isEmpty()) st.pollLast(); }
        else if (!part.isEmpty() && !part.equals(".")) st.offerLast(part);
    }
    return "/" + String.join("/", st);
}"""),
],
}

TESTS = {
 "merge-intervals": [("new int[][]{{1,3},{2,6},{8,10},{15,18}}", "[[1, 6], [8, 10], [15, 18]]"), ("new int[][]{{1,4},{4,5}}", "[[1, 5]]"),
                     ("new int[][]{{1,4},{0,4}}", "[[0, 4]]"), ("new int[][]{{2,3},{4,5},{6,7},{8,9},{1,10}}", "[[1, 10]]")],
 "insert-interval": [("new int[][]{{1,3},{6,9}}, new int[]{2,5}", "[[1, 5], [6, 9]]"),
                     ("new int[][]{{1,2},{3,5},{6,7},{8,10},{12,16}}, new int[]{4,8}", "[[1, 2], [3, 10], [12, 16]]"),
                     ("new int[][]{}, new int[]{5,7}", "[[5, 7]]")],
 "interval-list-intersections": [("new int[][]{{0,2},{5,10},{13,23},{24,25}}, new int[][]{{1,5},{8,12},{15,24},{25,26}}",
                                  "[[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]"),
                                 ("new int[][]{{1,3},{5,9}}, new int[][]{}", "[]")],
 "gfg-check-if-any-two-intervals-overlap": [("new int[][]{{1,3},{5,7},{2,4},{6,8}}", "true"), ("new int[][]{{1,3},{7,9},{4,6},{10,13}}", "false"),
                                            ("new int[][]{{1,3},{3,5}}", "false")],
 "gfg-attend-all-meetings-ii": [("new int[]{1,10,7}, new int[]{4,15,10}", "1"), ("new int[]{2,9,6}, new int[]{4,12,10}", "2"),
                                ("new int[]{0,5,15}, new int[]{30,10,20}", "2")],
 "gfg-maximum-cpu-load": [("new int[][]{{1,4,3},{2,5,4},{7,9,6}}", "7"), ("new int[][]{{6,7,10},{2,4,11},{8,12,15}}", "15"),
                          ("new int[][]{{1,4,2},{2,4,1},{3,6,5}}", "8")],
 "codertrain-employee-free-time": [("new int[][][]{{{1,2},{5,6}},{{1,3}},{{4,10}}}", "[[3, 4]]"),
                                   ("new int[][][]{{{1,3},{6,7}},{{2,4}},{{2,5},{9,12}}}", "[[5, 6], [7, 9]]")],
 "reverse-linked-list": [("!r = toList(o.{m}(list(1,2,3,4,5)));", "[5, 4, 3, 2, 1]"), ("!r = toList(o.{m}(list(1,2)));", "[2, 1]"),
                         ("!r = toList(o.{m}(list()));", "[]")],
 "reverse-linked-list-ii": [("!r = toList(o.{m}(list(1,2,3,4,5), 2, 4));", "[1, 4, 3, 2, 5]"), ("!r = toList(o.{m}(list(5), 1, 1));", "[5]"),
                            ("!r = toList(o.{m}(list(3,5), 1, 2));", "[5, 3]")],
 "swap-nodes-in-pairs": [("!r = toList(o.{m}(list(1,2,3,4)));", "[2, 1, 4, 3]"), ("!r = toList(o.{m}(list()));", "[]"),
                         ("!r = toList(o.{m}(list(1)));", "[1]"), ("!r = toList(o.{m}(list(1,2,3)));", "[2, 1, 3]")],
 "reverse-nodes-in-k-group": [("!r = toList(o.{m}(list(1,2,3,4,5), 2));", "[2, 1, 4, 3, 5]"), ("!r = toList(o.{m}(list(1,2,3,4,5), 3));", "[3, 2, 1, 4, 5]"),
                              ("!r = toList(o.{m}(list(1,2,3), 1));", "[1, 2, 3]"), ("!r = toList(o.{m}(list(1,2,3,4), 4));", "[4, 3, 2, 1]")],
 "rotate-list": [("!r = toList(o.{m}(list(1,2,3,4,5), 2));", "[4, 5, 1, 2, 3]"), ("!r = toList(o.{m}(list(0,1,2), 4));", "[2, 0, 1]"),
                 ("!r = toList(o.{m}(list(), 0));", "[]"), ("!r = toList(o.{m}(list(1,2), 2));", "[1, 2]")],
 "reverse-nodes-in-even-length-groups": [("!r = toList(o.{m}(list(5,2,6,3,9,1,7,3,8,4)));", "[5, 6, 2, 3, 9, 1, 4, 8, 3, 7]"),
                                         ("!r = toList(o.{m}(list(1,1,0,6)));", "[1, 0, 1, 6]"), ("!r = toList(o.{m}(list(1,1,0,6,5)));", "[1, 0, 1, 5, 6]"),
                                         ("!r = toList(o.{m}(list(2)));", "[2]")],
 "valid-parentheses": [('"()"', "true"), ('"()[]{}"', "true"), ('"(]"', "false"), ('"([)]"', "false"), ('"{[]}"', "true"), ('"("', "false"), ('"]"', "false")],
 "daily-temperatures": [("new int[]{73,74,75,71,69,72,76,73}", "[1, 1, 4, 2, 1, 1, 0, 0]"), ("new int[]{30,40,50,60}", "[1, 1, 1, 0]"),
                        ("new int[]{30,60,90}", "[1, 1, 0]"), ("new int[]{90,80,70}", "[0, 0, 0]")],
 "next-greater-element-ii": [("new int[]{1,2,1}", "[2, -1, 2]"), ("new int[]{1,2,3,4,3}", "[2, 3, 4, -1, 4]"), ("new int[]{5,5,5}", "[-1, -1, -1]")],
 "remove-k-digits": [('"1432219", 3', "1219"), ('"10200", 1', "200"), ('"10", 2', "0"), ('"112", 1', "11"), ('"9", 1', "0")],
 "remove-all-adjacent-duplicates-in-string": [('"abbaca"', "ca"), ('"azxxzy"', "ay"), ('"aa"', "")],
 "remove-all-adjacent-duplicates-in-string-ii": [('"abcd", 2', "abcd"), ('"deeedbbcccbdaa", 3', "aa"), ('"pbbcggttciiippooaais", 2', "ps")],
 "reverse-string": [('!char[] a = "hello".toCharArray(); o.{m}(a); r = new String(a);', "olleh"),
                    ('!char[] a = "Hannah".toCharArray(); o.{m}(a); r = new String(a);', "hannaH")],
 "remove-nodes-from-linked-list": [("!r = toList(o.{m}(list(5,2,13,3,8)));", "[13, 8]"), ("!r = toList(o.{m}(list(1,1,1,1)));", "[1, 1, 1, 1]"),
                                   ("!r = toList(o.{m}(list(3,2,1)));", "[3, 2, 1]")],
 "simplify-path": [('"/home/"', "/home"), ('"/../"', "/"), ('"/home//foo/"', "/home/foo"), ('"/a/./b/../../c/"', "/c"),
                   ('"/.../a/../b/c/../d/./"', "/.../b/d")],
}
