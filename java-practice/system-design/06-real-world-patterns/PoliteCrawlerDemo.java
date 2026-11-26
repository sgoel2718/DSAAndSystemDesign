import java.util.*;

public class PoliteCrawlerDemo {
    record Url(String host, String path, int priority) {}
    static final Map<String, Deque<Url>> perHost = new TreeMap<>();               // back queues: one per host
    static final PriorityQueue<Object[]> nextAllowed = new PriorityQueue<>(Comparator.comparingLong(a -> (Long) a[1]));   // {host, time}
    static final Set<String> seen = new HashSet<>();
    static final Map<String, Set<String>> robotsDisallow = Map.of("shop.com", Set.of("/cart"));
    static final Map<String, Long> crawlDelayMs = Map.of("shop.com", 1000L, "news.com", 500L, "blog.com", 500L);

    static void add(Url u) {
        if (!seen.add(u.host() + u.path())) return;                               // dedup (a Bloom filter at scale)
        if (robotsDisallow.getOrDefault(u.host(), Set.of()).stream().anyMatch(u.path()::startsWith)) { System.out.println("  robots.txt disallows " + u.host() + u.path()); return; }
        boolean newHost = !perHost.containsKey(u.host());
        perHost.computeIfAbsent(u.host(), k -> new ArrayDeque<>()).add(u);
        if (newHost) nextAllowed.add(new Object[]{u.host(), 0L});
    }

    public static void main(String[] args) {
        for (String p : List.of("/", "/a", "/b", "/cart", "/a")) add(new Url("shop.com", p, 1));
        for (String p : List.of("/", "/today")) add(new Url("news.com", p, 1));
        add(new Url("blog.com", "/", 2));
        long clock = 0; int fetched = 0;
        while (!nextAllowed.isEmpty() && fetched < 10) {
            Object[] slot = nextAllowed.poll(); String host = (String) slot[0]; clock = Math.max(clock, (Long) slot[1]);
            Url u = perHost.get(host).poll(); fetched++;
            System.out.printf("t=%4d ms fetch %s%s%n", clock, u.host(), u.path());
            if (!perHost.get(host).isEmpty()) nextAllowed.add(new Object[]{host, clock + crawlDelayMs.get(host)});    // politeness delay per host
        }
        System.out.println("each host is hit at most once per crawl-delay, while different hosts are fetched in parallel");
    }
}
