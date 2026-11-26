import java.util.*;
import java.util.function.*;

public class CdcDemo {
    // The database's own change log is tailed and turned into events for other systems (Debezium-style).
    record Change(long lsn, String op, String table, Map<String, Object> before, Map<String, Object> after) {}
    static final List<Change> wal = new ArrayList<>();
    static final Map<Integer, Map<String, Object>> orders = new TreeMap<>();

    static void insert(int id, String status) { Map<String, Object> row = Map.of("id", id, "status", status); orders.put(id, row); wal.add(new Change(wal.size() + 1, "c", "orders", null, row)); }
    static void update(int id, String status) { Map<String, Object> old = orders.get(id), row = Map.of("id", id, "status", status); orders.put(id, row); wal.add(new Change(wal.size() + 1, "u", "orders", old, row)); }
    static void delete(int id) { wal.add(new Change(wal.size() + 1, "d", "orders", orders.remove(id), null)); }

    public static void main(String[] args) {
        Map<Integer, String> searchIndex = new TreeMap<>(); Set<String> cache = new TreeSet<>(Set.of("order:987", "order:988"));
        List<Consumer<Change>> subscribers = List.of(
            c -> { if (c.after() != null) searchIndex.put((Integer) c.after().get("id"), (String) c.after().get("status")); else searchIndex.remove((Integer) c.before().get("id")); },
            c -> cache.remove("order:" + (c.after() != null ? c.after() : c.before()).get("id")));
        insert(987, "PENDING"); insert(988, "PENDING"); update(987, "PAID"); delete(988);
        long connectorOffset = 0;
        for (Change c : wal) {
            if (c.lsn() <= connectorOffset) continue;
            System.out.println("event lsn=" + c.lsn() + " op=" + c.op() + " before=" + c.before() + " after=" + c.after());
            subscribers.forEach(s -> s.accept(c));
            connectorOffset = c.lsn();                                        // checkpoint so a restart resumes here
        }
        System.out.println("search index now " + searchIndex + "; cache keys left " + cache);
        System.out.println("the app only wrote to the DB; search and cache stayed in sync from the log.");
    }
}
