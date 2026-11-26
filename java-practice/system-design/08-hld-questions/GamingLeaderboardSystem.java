import java.util.*;
import java.util.concurrent.*;

public class GamingLeaderboardSystem {
    // Score events -> per-season sorted set (ConcurrentSkipListSet) -> top-N, my rank, and friends leaderboard.
    record Entry(long score, long achievedAt, String player) implements Comparable<Entry> {
        public int compareTo(Entry o) { int c = Long.compare(o.score, score); if (c != 0) return c; c = Long.compare(achievedAt, o.achievedAt); return c != 0 ? c : player.compareTo(o.player); }
    }
    static final ConcurrentSkipListSet<Entry> board = new ConcurrentSkipListSet<>();
    static final ConcurrentHashMap<String, Entry> current = new ConcurrentHashMap<>();

    static void addScore(String p, long points, long ts) {
        current.compute(p, (k, old) -> { if (old != null) board.remove(old); Entry e = new Entry((old == null ? 0 : old.score()) + points, ts, p); board.add(e); return e; });
    }
    static int rank(String p) { return board.headSet(current.get(p)).size() + 1; }

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4); Random r = new Random(7); List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < 4; i++) { final int part = i; fs.add(pool.submit(() -> { for (int g = 0; g < 25_000; g++) { int p = part * 25_000 + g; synchronized (GamingLeaderboardSystem.class) { addScore("p" + (p % 50_000), (p * 7919L) % 1000, p); } } })); }
        for (Future<?> f : fs) f.get(); pool.shutdown();
        addScore("asha", 1500, 200_000); addScore("ravi", 900, 200_001); addScore("zoya", 1500, 200_002);
        System.out.println("players: " + current.size());
        System.out.println("top 5: " + board.stream().limit(5).map(e -> e.player() + "=" + e.score()).toList());
        System.out.println("asha rank " + rank("asha") + ", zoya rank " + rank("zoya") + " (same score, asha got there first)");
        List<String> friends = List.of("asha", "ravi", "zoya", "p42");
        System.out.println("friends board: " + friends.stream().map(current::get).sorted().map(e -> e.player() + "=" + e.score()).toList());
        if (r.nextInt() == 42) System.out.println();
    }
}
