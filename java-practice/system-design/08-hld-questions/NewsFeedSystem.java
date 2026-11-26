import java.util.*;

public class NewsFeedSystem {
    // Hybrid fan-out + ranking: push for normal authors, pull for celebrities, then rank by affinity x recency x engagement.
    record Post(long id, String author, long ts, int likes) {}
    static final Map<String, Set<String>> followers = new HashMap<>(), following = new HashMap<>();
    static final Map<String, Deque<Long>> feedCache = new HashMap<>();
    static final Map<String, List<Post>> timelines = new HashMap<>();
    static final Map<Long, Post> posts = new HashMap<>();
    static final Map<String, Map<String, Double>> affinity = new HashMap<>();  // how much a user interacts with an author
    static long seq = 0; static final int CELEB = 3;

    static void follow(String u, String a, double aff) { followers.computeIfAbsent(a, k -> new HashSet<>()).add(u); following.computeIfAbsent(u, k -> new TreeSet<>()).add(a); affinity.computeIfAbsent(u, k -> new HashMap<>()).put(a, aff); }
    static void publish(String author, long ts, int likes) {
        Post p = new Post(++seq, author, ts, likes); posts.put(p.id(), p); timelines.computeIfAbsent(author, k -> new ArrayList<>()).add(p);
        if (followers.getOrDefault(author, Set.of()).size() < CELEB) for (String f : followers.getOrDefault(author, Set.of())) feedCache.computeIfAbsent(f, k -> new ArrayDeque<>()).addFirst(p.id());
    }
    static List<String> feed(String user, long now) {
        List<Post> cand = new ArrayList<>();
        for (long id : feedCache.getOrDefault(user, new ArrayDeque<>())) cand.add(posts.get(id));
        for (String a : following.getOrDefault(user, Set.of())) if (followers.get(a).size() >= CELEB) cand.addAll(timelines.getOrDefault(a, List.of()));
        return cand.stream().sorted(Comparator.comparingDouble((Post p) -> -score(user, p, now)))
            .map(p -> String.format("%s#%d(%.2f)", p.author(), p.id(), score(user, p, now))).toList();
    }
    static double score(String u, Post p, long now) {
        double aff = affinity.get(u).getOrDefault(p.author(), 0.1), recency = Math.exp(-(now - p.ts()) / 24.0), engagement = Math.log(2 + p.likes());
        return aff * recency * engagement;
    }

    public static void main(String[] args) {
        follow("asha", "ravi", 0.9); follow("asha", "zoya", 0.3); for (String u : List.of("asha", "kiran", "meera")) follow(u, "bollywood", 0.5);
        publish("ravi", 10, 5); publish("zoya", 20, 300); publish("bollywood", 22, 90_000); publish("ravi", 23, 2); publish("zoya", 2, 50);
        System.out.println("asha's ranked feed at hour 24: " + feed("asha", 24));
        System.out.println("pushed entries in asha's cache: " + feedCache.get("asha") + " (bollywood posts pulled at read time)");
    }
}
