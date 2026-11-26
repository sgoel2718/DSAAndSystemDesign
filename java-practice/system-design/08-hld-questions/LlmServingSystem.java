import java.util.*;

public class LlmServingSystem {
    // Continuous batching on a GPU: each step generates one token for every active request; finished requests leave,
    // waiting ones join immediately. Compare with static batching (wait for the whole batch to finish).
    record Req(String id, int arrivalStep, int outputTokens) {}

    static Map<String, Integer> simulate(List<Req> reqs, int maxBatch, boolean continuous) {
        Map<String, Integer> done = new TreeMap<>(); Map<String, Integer> remaining = new HashMap<>(); Deque<Req> waiting = new ArrayDeque<>(reqs);
        List<Req> active = new ArrayList<>(); int step = 0;
        while (done.size() < reqs.size()) {
            boolean canJoin = continuous || active.isEmpty();
            while (canJoin && active.size() < maxBatch && !waiting.isEmpty() && waiting.peek().arrivalStep() <= step) { Req r = waiting.poll(); active.add(r); remaining.put(r.id(), r.outputTokens()); }
            for (Req r : active) remaining.merge(r.id(), -1, Integer::sum);           // one forward pass = one token for each active request
            step++;
            for (Iterator<Req> it = active.iterator(); it.hasNext(); ) { Req r = it.next(); if (remaining.get(r.id()) == 0) { done.put(r.id(), step - r.arrivalStep()); it.remove(); } }
        }
        return done;
    }

    public static void main(String[] args) {
        List<Req> reqs = List.of(new Req("long-essay", 0, 400), new Req("hi", 0, 5), new Req("code", 0, 120), new Req("joke", 2, 30), new Req("sum", 3, 60), new Req("q6", 5, 10));
        Map<String, Integer> stat = simulate(reqs, 4, false), cont = simulate(reqs, 4, true);
        System.out.println("request      tokens  static-batch latency  continuous-batch latency (steps)");
        for (Req r : reqs) System.out.printf("%-12s %5d   %8d              %8d%n", r.id(), r.outputTokens(), stat.get(r.id()), cont.get(r.id()));
        System.out.printf("average: static %.0f vs continuous %.0f steps; short requests no longer wait for the long essay%n",
            stat.values().stream().mapToInt(i -> i).average().orElse(0), cont.values().stream().mapToInt(i -> i).average().orElse(0));
        int kvBytesPerToken = 2 * 32 * 4096 * 2;                                          // K and V, 32 layers, 4096 hidden, fp16
        System.out.printf("KV cache: %,d KB per token -> a 4,000-token conversation holds %.1f GB of GPU memory%n", kvBytesPerToken / 1024, kvBytesPerToken * 4000 / 1e9);
    }
}
