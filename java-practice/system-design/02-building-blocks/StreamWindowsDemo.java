import java.util.*;

public class StreamWindowsDemo {
    record Click(String page, long tsSec) {}

    public static void main(String[] args) {
        List<Click> clicks = List.of(new Click("home", 2), new Click("cart", 15), new Click("home", 59), new Click("home", 61),
            new Click("cart", 70), new Click("home", 125), new Click("home", 45));          // last one arrives late (event time 45)
        // Batch: one job over the complete data
        Map<String, Long> batch = new TreeMap<>();
        for (Click c : clicks) batch.merge(c.page(), 1L, Long::sum);
        System.out.println("batch (all data, run once)   : " + batch);
        // Stream: tumbling 60 s windows by event time, emitted when the watermark passes the window end
        Map<Long, Map<String, Long>> windows = new TreeMap<>();
        long watermark = 0, allowedLateness = 10;
        for (Click c : clicks) {
            long w = c.tsSec() / 60 * 60;
            if (w + 60 + allowedLateness <= watermark) { System.out.println("  late event dropped: " + c); continue; }
            windows.computeIfAbsent(w, k -> new TreeMap<>()).merge(c.page(), 1L, Long::sum);
            watermark = Math.max(watermark, c.tsSec());
            for (Iterator<Map.Entry<Long, Map<String, Long>>> it = windows.entrySet().iterator(); it.hasNext(); ) {
                var e = it.next();
                if (e.getKey() + 60 + allowedLateness <= watermark) { System.out.println("stream window [" + e.getKey() + "," + (e.getKey() + 60) + ") : " + e.getValue()); it.remove(); }
            }
        }
        windows.forEach((w, v) -> System.out.println("stream window [" + w + "," + (w + 60) + ") : " + v + " (flushed at end)"));
    }
}
