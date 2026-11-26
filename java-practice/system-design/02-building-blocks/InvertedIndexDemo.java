import java.util.*;

public class InvertedIndexDemo {
    static final Map<String, Map<Integer, Integer>> index = new TreeMap<>();      // term -> (doc -> term frequency)
    static final Map<Integer, String> docs = new TreeMap<>();
    static final Map<Integer, Integer> docLen = new HashMap<>();

    static List<String> analyze(String text) {
        List<String> out = new ArrayList<>();
        for (String w : text.toLowerCase().split("\\W+")) {
            if (w.isBlank() || Set.of("the", "a", "and").contains(w)) continue;
            out.add(w.replaceAll("(ning|ing|s)$", ""));                         // toy stemmer: running -> run, shoes -> shoe
        }
        return out;
    }

    static void add(int id, String text) {
        docs.put(id, text); List<String> terms = analyze(text); docLen.put(id, terms.size());
        for (String t : terms) index.computeIfAbsent(t, k -> new TreeMap<>()).merge(id, 1, Integer::sum);
    }

    static List<String> search(String q) {                                   // BM25 ranking, OR semantics
        double avgLen = docLen.values().stream().mapToInt(i -> i).average().orElse(1), k1 = 1.2, b = 0.75; int n = docs.size();
        Map<Integer, Double> score = new HashMap<>();
        for (String t : analyze(q)) {
            Map<Integer, Integer> postings = index.getOrDefault(t, Map.of());
            double idf = Math.log(1 + (n - postings.size() + 0.5) / (postings.size() + 0.5));
            postings.forEach((doc, tf) -> score.merge(doc, idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * docLen.get(doc) / avgLen)), Double::sum));
        }
        return score.entrySet().stream().sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
            .map(e -> String.format("doc%d(%.2f) %s", e.getKey(), e.getValue(), docs.get(e.getKey()))).toList();
    }

    public static void main(String[] args) {
        add(1, "Red running shoes"); add(2, "Blue running jacket"); add(3, "Red jacket"); add(4, "Shoes and socks bundle");
        System.out.println("inverted index:"); index.forEach((t, p) -> System.out.println("  " + t + " -> " + p.keySet()));
        System.out.println("search 'red shoes':"); search("red shoes").forEach(r -> System.out.println("  " + r));
        System.out.println("search 'jackets':"); search("jackets").forEach(r -> System.out.println("  " + r));
    }
}
