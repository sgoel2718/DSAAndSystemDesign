import java.util.*;

public class SearchEngineSystem {
    // Crawl graph -> PageRank (power iteration) -> inverted index -> query = BM25-ish text score x PageRank.
    public static void main(String[] args) {
        Map<String, List<String>> links = new TreeMap<>(Map.of("wiki", List.of("blog", "docs"), "blog", List.of("wiki"), "docs", List.of("wiki", "blog"), "spam", List.of("spam2"), "spam2", List.of("spam")));
        Map<String, String> text = Map.of("wiki", "java concurrency guide threads locks", "blog", "my java journey and threads", "docs", "official java docs streams",
            "spam", "java java java java cheap pills", "spam2", "buy pills");
        Map<String, Double> pr = new TreeMap<>(); links.keySet().forEach(p -> pr.put(p, 1.0 / links.size()));
        for (int it = 0; it < 30; it++) {
            Map<String, Double> next = new TreeMap<>(); links.keySet().forEach(p -> next.put(p, 0.15 / links.size()));
            links.forEach((p, outs) -> outs.forEach(o -> next.merge(o, 0.85 * pr.get(p) / outs.size(), Double::sum)));
            pr.putAll(next);
        }
        System.out.println("PageRank: " + pr.entrySet().stream().map(e -> String.format("%s=%.3f", e.getKey(), e.getValue())).toList());
        Map<String, Map<String, Integer>> index = new TreeMap<>();
        text.forEach((doc, t) -> { for (String w : t.split(" ")) index.computeIfAbsent(w, k -> new TreeMap<>()).merge(doc, 1, Integer::sum); });
        String q = "java threads";
        Map<String, Double> score = new HashMap<>();
        for (String term : q.split(" ")) {
            Map<String, Integer> post = index.getOrDefault(term, Map.of()); double idf = Math.log(1 + text.size() / (double) post.size());
            post.forEach((doc, tf) -> score.merge(doc, idf * (tf / (tf + 1.2)), Double::sum));               // saturating tf: repeating a word 4x helps little
        }
        System.out.println("query '" + q + "':");
        score.entrySet().stream().sorted(Comparator.comparingDouble((Map.Entry<String, Double> e) -> -(e.getValue() * pr.get(e.getKey()))))
            .forEach(e -> System.out.printf("  %-5s text %.2f x pagerank %.3f = %.3f%n", e.getKey(), e.getValue(), pr.get(e.getKey()), e.getValue() * pr.get(e.getKey())));
    }
}
