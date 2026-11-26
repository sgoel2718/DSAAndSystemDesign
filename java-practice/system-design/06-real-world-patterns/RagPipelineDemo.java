import java.util.*;

public class RagPipelineDemo {
    // Toy RAG: embed docs as word-count vectors, retrieve top-k by cosine, build a prompt, and estimate token cost.
    static Map<String, Integer> embed(String text) { Map<String, Integer> v = new HashMap<>(); for (String w : text.toLowerCase().split("\\W+")) if (w.length() > 2) v.merge(w, 1, Integer::sum); return v; }
    static double cos(Map<String, Integer> a, Map<String, Integer> b) {
        double d = 0; for (var e : a.entrySet()) d += e.getValue() * b.getOrDefault(e.getKey(), 0);
        return d / Math.sqrt(a.values().stream().mapToDouble(x -> x * x).sum() * b.values().stream().mapToDouble(x -> x * x).sum());
    }

    public static void main(String[] args) {
        List<String> chunks = List.of(
            "Refunds are processed within 5 business days to the original payment method.",
            "Shipping is free on orders above Rs 499 across India.",
            "You can cancel an order before it is shipped from the My Orders page.",
            "Gift cards cannot be refunded or exchanged for cash.");
        Map<String, Map<String, Integer>> index = new LinkedHashMap<>(); for (String c : chunks) index.put(c, embed(c));
        String question = "How many days do refunds take?";
        Map<String, Integer> q = embed(question);
        List<Map.Entry<String, Double>> top = index.entrySet().stream().map(e -> Map.entry(e.getKey(), cos(q, e.getValue())))
            .sorted(Map.Entry.<String, Double>comparingByValue().reversed()).limit(2).toList();
        System.out.println("retrieved:"); top.forEach(e -> System.out.printf("  %.2f  %s%n", e.getValue(), e.getKey()));
        String prompt = "Answer using only the context. Cite the line you used.\nContext:\n- " + top.get(0).getKey() + "\n- " + top.get(1).getKey() + "\nQuestion: " + question;
        int promptTokens = prompt.split("\\s+").length * 4 / 3, outputTokens = 40;
        System.out.println("prompt ~" + promptTokens + " tokens, answer ~" + outputTokens + " tokens");
        Map<String, String> cache = new HashMap<>();
        for (int i = 0; i < 2; i++) {
            String key = question.toLowerCase().trim();
            System.out.println(cache.containsKey(key) ? "ask again -> served from answer cache (0 GPU time)" : "ask -> LLM call, stream tokens back over SSE");
            cache.putIfAbsent(key, "Refunds take up to 5 business days [1]");
        }
        double reqPerSec = 200, tokPerReq = promptTokens + outputTokens, gpuTokPerSec = 2000;
        System.out.printf("capacity: %.0f req/s x %.0f tokens = %.0f tokens/s -> ~%.0f GPUs at %.0f tokens/s each%n", reqPerSec, tokPerReq, reqPerSec * tokPerReq, Math.ceil(reqPerSec * tokPerReq / gpuTokPerSec), gpuTokPerSec);
    }
}
