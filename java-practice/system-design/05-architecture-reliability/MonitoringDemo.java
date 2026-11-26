import java.util.*;

public class MonitoringDemo {
    // Metrics (RED), structured logs with a request id, and a trace of spans.
    record Span(String name, long startMs, long durMs, int depth) {}

    public static void main(String[] args) {
        Random r = new Random(6); List<Integer> latencies = new ArrayList<>(); int errors = 0, requests = 1200;
        for (int i = 0; i < requests; i++) { int l = 40 + r.nextInt(60) + (r.nextInt(50) == 0 ? 800 : 0); latencies.add(l); if (r.nextInt(200) == 0) errors++; }
        Collections.sort(latencies);
        System.out.printf("RED  rate=%d req/min  errors=%.2f%%  duration p50=%d ms p99=%d ms%n", requests, errors * 100.0 / requests, latencies.get(600), latencies.get((int) (requests * 0.99)));
        double slo = 0.995, errorRate = errors / (double) requests, burn = errorRate / (1 - slo);
        System.out.printf("SLO 99.5%% -> burn rate %.2f %s%n", burn, burn > 2 ? "(page someone!)" : "(ok)");
        String reqId = "req-7f3a";
        System.out.println("{\"ts\":\"10:02:03.120\",\"level\":\"INFO\",\"svc\":\"order\",\"req\":\"" + reqId + "\",\"msg\":\"checkout start\",\"user\":42}");
        System.out.println("{\"ts\":\"10:02:03.520\",\"level\":\"WARN\",\"svc\":\"payment\",\"req\":\"" + reqId + "\",\"msg\":\"psp slow\",\"ms\":280}");
        List<Span> trace = List.of(new Span("GET /checkout (gateway)", 0, 420, 0), new Span("order-svc", 10, 390, 1), new Span("inventory.reserve", 20, 60, 2),
            new Span("payment.charge", 85, 280, 2), new Span("db insert", 370, 25, 2));
        System.out.println("trace " + reqId + ":");
        for (Span s : trace) System.out.printf("  %-26s %s%s %d ms%n", "  ".repeat(s.depth()) + s.name(), " ".repeat((int) (s.startMs() / 20)), "█".repeat((int) Math.max(1, s.durMs() / 20)), s.durMs());
        Span slow = trace.stream().filter(s -> s.depth() == 2).max(Comparator.comparingLong(Span::durMs)).get();
        System.out.println("bottleneck: " + slow.name() + " (" + slow.durMs() + " ms)");
    }
}
