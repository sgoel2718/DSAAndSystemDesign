import java.util.*;

public class NewsAggregatorSystem {
    // Fetch articles from sources -> normalise -> cluster near-duplicate stories by word-shingle Jaccard similarity -> rank clusters.
    record Article(String source, String title, int ageHours) {}

    static Set<String> shingles(String t) { String[] w = t.toLowerCase().replaceAll("[^a-z0-9 ]", "").split(" "); Set<String> s = new HashSet<>(); for (int i = 0; i + 1 < w.length; i++) s.add(w[i] + " " + w[i + 1]); return s; }
    static double jaccard(Set<String> a, Set<String> b) { Set<String> i = new HashSet<>(a); i.retainAll(b); Set<String> u = new HashSet<>(a); u.addAll(b); return u.isEmpty() ? 0 : i.size() / (double) u.size(); }

    public static void main(String[] args) {
        List<Article> feed = List.of(new Article("NDTV", "India beat Australia by 6 wickets in Perth Test", 2), new Article("TOI", "India beat Australia by 6 wickets in the Perth Test match", 1),
            new Article("ESPN", "Perth Test: India beat Australia by 6 wickets", 3), new Article("Reuters", "RBI keeps repo rate unchanged at 6.5 percent", 4),
            new Article("Mint", "RBI keeps repo rate unchanged at 6.5 percent for tenth time", 5), new Article("Verge", "New phone launched with bigger battery", 1));
        List<List<Article>> clusters = new ArrayList<>(); List<Set<String>> reps = new ArrayList<>();
        for (Article a : feed) {
            Set<String> sh = shingles(a.title()); int best = -1; double bestSim = 0.3;
            for (int i = 0; i < reps.size(); i++) { double s = jaccard(sh, reps.get(i)); if (s >= bestSim) { bestSim = s; best = i; } }
            if (best < 0) { clusters.add(new ArrayList<>(List.of(a))); reps.add(sh); } else clusters.get(best).add(a);
        }
        clusters.sort(Comparator.comparingDouble((List<Article> c) -> -(c.size() * 10 - c.stream().mapToInt(Article::ageHours).min().getAsInt())));
        for (List<Article> c : clusters) System.out.printf("story (%d sources, freshest %dh): %s%n   covered by %s%n", c.size(), c.stream().mapToInt(Article::ageHours).min().getAsInt(), c.get(0).title(), c.stream().map(Article::source).toList());
    }
}
