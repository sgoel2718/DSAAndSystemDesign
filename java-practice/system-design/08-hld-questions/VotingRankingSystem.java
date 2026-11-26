import java.util.*;

public class VotingRankingSystem {
    // One vote per user per post (upsert), score = ups - downs, and Reddit's 'hot' formula: log10(score) + age/45000 s.
    record Post(String id, String title, long createdSec) {}
    static final Map<String, Map<String, Integer>> votes = new HashMap<>();           // post -> user -> +1 / -1

    static void vote(String post, String user, int dir) { votes.computeIfAbsent(post, k -> new HashMap<>()).put(user, dir); }   // changing a vote just overwrites it
    static int score(String post) { return votes.getOrDefault(post, Map.of()).values().stream().mapToInt(i -> i).sum(); }
    static double hot(Post p) { int s = score(p.id()); double order = Math.log10(Math.max(Math.abs(s), 1)); int sign = Integer.signum(s); return sign * order + (p.createdSec() - 1_134_028_003L) / 45000.0; }

    public static void main(String[] args) {
        long now = 1_764_140_000L;
        List<Post> posts = List.of(new Post("p1", "Old viral meme", now - 30 * 3600), new Post("p2", "Fresh system design tip", now - 1 * 3600), new Post("p3", "Controversial take", now - 2 * 3600));
        for (int i = 0; i < 5000; i++) vote("p1", "u" + i, 1);
        for (int i = 0; i < 120; i++) vote("p2", "u" + i, 1);
        for (int i = 0; i < 300; i++) vote("p3", "u" + i, i % 2 == 0 ? 1 : -1);
        vote("p2", "u5", -1); vote("p2", "u5", 1); vote("p2", "u5", 1);                    // flip-flopping and double-voting count once
        for (Post p : posts) System.out.printf("%-24s score %5d  hot %.4f%n", p.title(), score(p.id()), hot(p));
        System.out.println("front page (hot): " + posts.stream().sorted(Comparator.comparingDouble(VotingRankingSystem::hot).reversed()).map(Post::title).toList());
        System.out.println("top (all time)  : " + posts.stream().sorted(Comparator.comparingInt((Post p) -> score(p.id())).reversed()).map(Post::title).toList());
        System.out.println("12.5 hours of age = 10x the votes: new posts get a chance; votes are buffered and the hot list is cached per subreddit");
    }
}
