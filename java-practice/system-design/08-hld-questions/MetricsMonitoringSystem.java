import java.util.*;

public class MetricsMonitoringSystem {
    // Agents push samples -> time-series store (series = name+labels) -> rollups -> rule evaluation with 'for' duration -> alerts.
    record Sample(String metric, Map<String, String> labels, long ts, double value) {}
    static final Map<String, TreeMap<Long, Double>> tsdb = new TreeMap<>();

    static String seriesKey(String m, Map<String, String> l) { return m + new TreeMap<>(l); }
    static void ingest(Sample s) { tsdb.computeIfAbsent(seriesKey(s.metric(), s.labels()), k -> new TreeMap<>()).put(s.ts(), s.value()); }
    static double avgOver(String key, long from, long to) { return tsdb.get(key).subMap(from, true, to, true).values().stream().mapToDouble(d -> d).average().orElse(Double.NaN); }

    public static void main(String[] args) {
        Random r = new Random(5);
        for (long t = 0; t < 600; t += 10) {
            for (String host : List.of("web-1", "web-2")) {
                double cpu = host.equals("web-2") && t >= 300 ? 92 + r.nextInt(6) : 40 + r.nextInt(20);
                ingest(new Sample("cpu_percent", Map.of("host", host, "env", "prod"), t, cpu));
            }
        }
        System.out.println("series stored: " + tsdb.keySet());
        String w2 = seriesKey("cpu_percent", Map.of("host", "web-2", "env", "prod"));
        for (long m = 0; m < 600; m += 60) System.out.printf("  1-min rollup web-2 minute %d: %.1f%%%n", m / 60, avgOver(w2, m, m + 59));
        // Rule: avg(cpu over 1 min) > 90 for 2 consecutive evaluations -> FIRING
        String state = "OK"; int pendingFor = 0;
        for (long now = 60; now <= 600; now += 60) {
            boolean breach = avgOver(w2, now - 60, now) > 90;
            pendingFor = breach ? pendingFor + 1 : 0;
            String next = pendingFor == 0 ? "OK" : pendingFor < 2 ? "PENDING" : "FIRING";
            if (!next.equals(state)) System.out.println("t=" + now + " alert HighCPU web-2: " + state + " -> " + next + (next.equals("FIRING") ? "  (page on-call)" : ""));
            state = next;
        }
        System.out.printf("cardinality: %d series; adding a per-request label like user_id would create millions%n", tsdb.size());
    }
}
