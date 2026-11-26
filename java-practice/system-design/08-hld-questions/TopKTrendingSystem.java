import java.util.*;

public class TopKTrendingSystem {
    // Count-Min Sketch for approximate counts in bounded memory + a min-heap of the top K, per time window; exact recount offline.
    static class CountMinSketch {
        final int w, d; final int[][] t; final int[] seeds;
        CountMinSketch(int w, int d) { this.w = w; this.d = d; t = new int[d][w]; seeds = new int[d]; Random r = new Random(3); for (int i = 0; i < d; i++) seeds[i] = r.nextInt() | 1; }
        int idx(String k, int i) { int h = k.hashCode() * seeds[i]; h ^= h >>> 15; return Math.floorMod(h, w); }
        void add(String k) { for (int i = 0; i < d; i++) t[i][idx(k, i)]++; }
        int estimate(String k) { int m = Integer.MAX_VALUE; for (int i = 0; i < d; i++) m = Math.min(m, t[i][idx(k, i)]); return m; }
    }

    public static void main(String[] args) {
        CountMinSketch cms = new CountMinSketch(1000, 4); Map<String, Integer> exact = new HashMap<>();
        PriorityQueue<Map.Entry<String, Integer>> heap = new PriorityQueue<>(Map.Entry.comparingByValue()); Map<String, Map.Entry<String, Integer>> inHeap = new HashMap<>();
        Random r = new Random(9); int K = 3;
        for (int i = 0; i < 200_000; i++) {
            String video = "v" + (int) Math.floor(Math.pow(r.nextDouble(), 4) * 50_000);              // skewed popularity
            cms.add(video); exact.merge(video, 1, Integer::sum);
            int est = cms.estimate(video);
            if (inHeap.containsKey(video)) { heap.remove(inHeap.get(video)); }
            else if (heap.size() == K && est <= heap.peek().getValue()) continue;
            else if (heap.size() == K) inHeap.remove(heap.poll().getKey());
            Map.Entry<String, Integer> e = Map.entry(video, est); heap.add(e); inHeap.put(video, e);
        }
        List<Map.Entry<String, Integer>> top = new ArrayList<>(heap); top.sort(Map.Entry.<String, Integer>comparingByValue().reversed());
        System.out.println("approx top-" + K + " (Count-Min + heap): " + top);
        System.out.println("exact top-" + K + "                  : " + exact.entrySet().stream().sorted(Map.Entry.<String, Integer>comparingByValue().reversed()).limit(K).toList());
        System.out.printf("memory: sketch %,d counters vs exact map %,d keys%n", 1000 * 4, exact.size());
        String rare = exact.entrySet().stream().filter(e -> e.getValue() == 1).findFirst().get().getKey();
        System.out.println("a rare video " + rare + ": exact 1, sketch estimate " + cms.estimate(rare) + " (only over-estimates, never under)");
    }
}
