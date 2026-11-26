import java.util.*;

public class DistributedTracingSystem {
    // Trace context (traceId, parent span) propagated through calls; spans reported to a collector; tree rebuilt; tail-based sampling.
    record Span(String traceId, String spanId, String parentId, String service, String op, long start, long end, boolean error) {}
    static final List<Span> collector = new ArrayList<>(); static int ids = 0;

    static long call(String traceId, String parent, String service, String op, long start, long selfMs, boolean error, List<Object[]> children) {
        String id = "s" + (++ids); long t = start + selfMs / 2; boolean childError = false;
        for (Object[] c : children) { long end = call(traceId, id, (String) c[0], (String) c[1], t, (Long) c[2], (Boolean) c[3], List.of()); t = end; childError |= (Boolean) c[3]; }
        long end = t + selfMs / 2;
        collector.add(new Span(traceId, id, parent, service, op, start, end, error || childError));
        return end;
    }
    static void print(List<Span> spans, String parent, int depth) {
        spans.stream().filter(s -> Objects.equals(s.parentId(), parent)).sorted(Comparator.comparingLong(Span::start)).forEach(s -> {
            System.out.printf("  %-34s %4d ms %s%n", "  ".repeat(depth) + s.service() + " " + s.op(), s.end() - s.start(), s.error() ? "ERROR" : "");
            print(spans, s.spanId(), depth + 1);
        });
    }

    public static void main(String[] args) {
        call("trace-A", null, "gateway", "GET /checkout", 0, 10, false, List.of(new Object[]{"order", "createOrder", 40L, false}, new Object[]{"payment", "charge", 320L, false}, new Object[]{"email", "send", 15L, false}));
        call("trace-B", null, "gateway", "GET /checkout", 1000, 10, false, List.of(new Object[]{"order", "createOrder", 35L, false}, new Object[]{"payment", "charge", 60L, true}));
        call("trace-C", null, "gateway", "GET /home", 2000, 30, false, List.of());
        Map<String, List<Span>> byTrace = new TreeMap<>(); for (Span s : collector) byTrace.computeIfAbsent(s.traceId(), k -> new ArrayList<>()).add(s);
        for (var e : byTrace.entrySet()) {
            Span root = e.getValue().stream().filter(s -> s.parentId() == null).findFirst().get();
            boolean keep = root.error() || root.end() - root.start() > 300;                     // tail sampling: keep slow or failed traces
            System.out.println(e.getKey() + " (" + (root.end() - root.start()) + " ms) -> " + (keep ? "KEPT" : "dropped (fast and healthy)"));
            if (keep) print(e.getValue(), null, 0);
        }
    }
}
