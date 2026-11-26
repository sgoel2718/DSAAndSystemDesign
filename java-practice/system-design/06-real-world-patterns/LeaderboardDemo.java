import java.util.*;

public class LeaderboardDemo {
    // Sorted set: member -> score map + a TreeSet ordered by (score desc, time asc, name) for O(log n) updates and top-k.
    record Entry(String member, long score, long achievedAt) {}
    static final Map<String, Entry> byMember = new HashMap<>();
    static final TreeSet<Entry> ranked = new TreeSet<>(Comparator.comparingLong((Entry e) -> -e.score()).thenComparingLong(Entry::achievedAt).thenComparing(Entry::member));

    static void zincrby(String m, long by, long now) {
        Entry old = byMember.get(m); if (old != null) ranked.remove(old);
        Entry e = new Entry(m, (old == null ? 0 : old.score()) + by, now); byMember.put(m, e); ranked.add(e);
    }
    static List<String> top(int k) { return ranked.stream().limit(k).map(e -> e.member() + "=" + e.score()).toList(); }
    static int rank(String m) { return ranked.headSet(byMember.get(m)).size() + 1; }       // O(n) here; a skip list with spans makes it O(log n)

    public static void main(String[] args) {
        zincrby("asha", 50, 1); zincrby("ravi", 80, 2); zincrby("zoya", 70, 3); zincrby("asha", 40, 4); zincrby("kiran", 90, 5);
        System.out.println("top 3: " + top(3));
        System.out.println("rank of zoya: " + rank("zoya"));
        zincrby("zoya", 20, 6);
        System.out.println("zoya +20 -> top 3: " + top(3) + " (ties: asha reached 90 first, ahead of zoya)");
        Random r = new Random(1); for (int i = 0; i < 100_000; i++) zincrby("p" + i, r.nextInt(100), 10 + i);
        System.out.println("100,003 players, top 3: " + top(3) + ", asha's rank: " + rank("asha"));
    }
}
