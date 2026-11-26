import java.util.*;
import java.util.regex.*;

public class LoggingSystem {
    // Apps emit structured logs -> agent batches -> Kafka-like buffer -> indexer builds an inverted index per day -> search + retention.
    record Log(long ts, String day, String service, String level, String traceId, String msg) {}
    static final List<Log> buffer = new ArrayList<>();
    static final Map<String, List<Log>> dailyIndices = new TreeMap<>();
    static final Map<String, Map<String, Set<Integer>>> inverted = new TreeMap<>();

    static void index(Log l) {
        List<Log> docs = dailyIndices.computeIfAbsent("logs-" + l.day(), k -> new ArrayList<>()); docs.add(l); int docId = docs.size() - 1;
        Map<String, Set<Integer>> inv = inverted.computeIfAbsent("logs-" + l.day(), k -> new HashMap<>());
        for (String tok : (l.service() + " " + l.level() + " " + l.traceId() + " " + l.msg()).toLowerCase().split("\\W+")) inv.computeIfAbsent(tok, k -> new TreeSet<>()).add(docId);
    }
    static List<Log> search(String day, String... terms) {
        Map<String, Set<Integer>> inv = inverted.getOrDefault("logs-" + day, Map.of()); Set<Integer> hits = null;
        for (String t : terms) { Set<Integer> p = inv.getOrDefault(t.toLowerCase(), Set.of()); hits = hits == null ? new TreeSet<>(p) : hits; hits.retainAll(p); }
        return hits == null ? List.of() : hits.stream().map(i -> dailyIndices.get("logs-" + day).get(i)).toList();
    }

    public static void main(String[] args) {
        String[][] raw = {{"11-24", "order", "INFO", "t1", "checkout started user=42"}, {"11-24", "payment", "ERROR", "t1", "psp timeout after 3000ms"},
            {"11-25", "order", "INFO", "t2", "checkout started user=7"}, {"11-25", "payment", "ERROR", "t2", "card declined"}, {"11-26", "payment", "ERROR", "t3", "psp timeout after 3000ms"},
            {"11-26", "order", "WARN", "t3", "retrying payment"}};
        long ts = 0;
        for (String[] r : raw) { buffer.add(new Log(ts++, r[0], r[1], r[2], r[3], r[4])); if (buffer.size() == 3) { buffer.forEach(LoggingSystem::index); System.out.println("agent flushed a batch of 3 -> indexed"); buffer.clear(); } }
        System.out.println("indices: " + dailyIndices.keySet());
        System.out.println("search 11-26 'payment error timeout': " + search("11-26", "payment", "error", "timeout").stream().map(Log::msg).toList());
        System.out.println("all logs for trace t3: " + search("11-26", "t3").stream().map(l -> l.service() + ":" + l.msg()).toList());
        String cutoff = "11-25"; dailyIndices.keySet().removeIf(k -> k.compareTo("logs-" + cutoff) < 0); inverted.keySet().removeIf(k -> k.compareTo("logs-" + cutoff) < 0);
        System.out.println("retention (keep 2 days): indices now " + dailyIndices.keySet() + " (dropping a whole day is instant)");
    }
}
