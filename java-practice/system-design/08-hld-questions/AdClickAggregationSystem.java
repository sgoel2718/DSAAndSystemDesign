import java.util.*;

public class AdClickAggregationSystem {
    // Click events -> dedupe by click id -> tumbling 1-minute windows by EVENT time with watermark -> per-ad counts -> reconcile with batch.
    record Click(String clickId, String adId, long eventSec, long arrivalSec) {}

    public static void main(String[] args) {
        List<Click> stream = List.of(new Click("c1", "ad7", 5, 6), new Click("c2", "ad7", 20, 21), new Click("c2", "ad7", 20, 22),      // c2 retried by the client
            new Click("c3", "ad9", 50, 51), new Click("c4", "ad7", 65, 66), new Click("c5", "ad9", 58, 75),                              // c5 arrives 17 s late
            new Click("c6", "ad9", 130, 131), new Click("c7", "ad7", 40, 200));                                                         // c7 is very late
        Set<String> seen = new HashSet<>(); Map<Long, Map<String, Integer>> open = new TreeMap<>(), emitted = new TreeMap<>();
        long watermark = 0, allowedLateness = 30; List<Click> lateForBatch = new ArrayList<>();
        for (Click c : stream) {
            if (!seen.add(c.clickId())) { System.out.println("dedupe: dropped duplicate " + c.clickId()); continue; }
            long window = c.eventSec() / 60 * 60;
            if (window + 60 + allowedLateness <= watermark) { lateForBatch.add(c); System.out.println("too late for streaming: " + c.clickId() + " (left for the batch job)"); continue; }
            open.computeIfAbsent(window, k -> new TreeMap<>()).merge(c.adId(), 1, Integer::sum);
            watermark = Math.max(watermark, c.arrivalSec() - 5);                   // watermark trails arrival time a little
            for (Iterator<Map.Entry<Long, Map<String, Integer>>> it = open.entrySet().iterator(); it.hasNext(); ) {
                var e = it.next();
                if (e.getKey() + 60 + allowedLateness <= watermark) { emitted.put(e.getKey(), e.getValue()); System.out.println("emit window [" + e.getKey() + "," + (e.getKey() + 60) + ") -> " + e.getValue()); it.remove(); }
            }
        }
        open.forEach((w, v) -> { emitted.put(w, v); System.out.println("emit window [" + w + "," + (w + 60) + ") at shutdown -> " + v); });
        Map<Long, Map<String, Integer>> batch = new TreeMap<>(); Set<String> s2 = new HashSet<>();
        for (Click c : stream) if (s2.add(c.clickId())) batch.computeIfAbsent(c.eventSec() / 60 * 60, k -> new TreeMap<>()).merge(c.adId(), 1, Integer::sum);
        System.out.println("nightly batch (exact) : " + batch);
        System.out.println("streaming (real-time) : " + emitted + " -> batch result replaces it for billing (lambda-style reconciliation)");
    }
}
