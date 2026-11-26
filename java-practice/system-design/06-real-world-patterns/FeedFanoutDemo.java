import java.util.*;

public class FeedFanoutDemo {
    static final Map<String, Set<String>> followers = new HashMap<>();      // author -> followers
    static final Map<String, Set<String>> following = new HashMap<>();      // user -> authors
    static final Map<String, Deque<String>> feedCache = new HashMap<>();    // precomputed feeds (push)
    static final Map<String, List<String>> authorTimeline = new HashMap<>();
    static final int CELEB_THRESHOLD = 3; static int cacheWrites = 0;

    static void follow(String u, String a) { followers.computeIfAbsent(a, k -> new TreeSet<>()).add(u); following.computeIfAbsent(u, k -> new TreeSet<>()).add(a); }

    static void post(String author, String postId) {
        authorTimeline.computeIfAbsent(author, k -> new ArrayList<>()).add(0, postId);
        Set<String> fs = followers.getOrDefault(author, Set.of());
        if (fs.size() >= CELEB_THRESHOLD) { System.out.println(author + " posts " + postId + " -> celebrity: stored once, pulled at read time"); return; }
        for (String f : fs) { feedCache.computeIfAbsent(f, k -> new ArrayDeque<>()).addFirst(postId); cacheWrites++; }
        System.out.println(author + " posts " + postId + " -> pushed into " + fs.size() + " follower feeds");
    }

    static List<String> readFeed(String user) {
        List<String> feed = new ArrayList<>(feedCache.getOrDefault(user, new ArrayDeque<>()));
        for (String a : following.getOrDefault(user, Set.of()))
            if (followers.get(a).size() >= CELEB_THRESHOLD) feed.addAll(authorTimeline.getOrDefault(a, List.of()));   // merge celebrity posts
        feed.sort(Comparator.comparing((String p) -> Integer.parseInt(p.substring(1))).reversed());               // newest first (ids are time-ordered)
        return feed;
    }

    public static void main(String[] args) {
        follow("asha", "ravi"); follow("zoya", "ravi");
        for (String u : List.of("asha", "zoya", "meera", "kiran")) follow(u, "celeb");
        post("ravi", "p1"); post("celeb", "p2"); post("ravi", "p3"); post("celeb", "p4");
        System.out.println("asha's feed: " + readFeed("asha"));
        System.out.println("meera's feed: " + readFeed("meera"));
        System.out.println("cache writes: " + cacheWrites + " (with pure push the celebrity would cost " + followers.get("celeb").size() + " writes per post; with 100M followers, 100M)");
    }
}
