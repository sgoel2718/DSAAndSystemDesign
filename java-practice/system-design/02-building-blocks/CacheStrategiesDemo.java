import java.util.*;

public class CacheStrategiesDemo {
    static final Map<String, Integer> db = new HashMap<>(Map.of("stock:ps5", 10));
    static final Map<String, Integer> cache = new HashMap<>();
    static final List<String> log = new ArrayList<>();

    // Cache-aside: app reads cache, loads from DB on miss; on write, update DB then DELETE the key
    static int readAside(String k) {
        Integer v = cache.get(k);
        if (v != null) { log.add("aside read " + k + " HIT " + v); return v; }
        v = db.get(k); cache.put(k, v); log.add("aside read " + k + " MISS -> DB " + v); return v;
    }
    static void writeAside(String k, int v) { db.put(k, v); cache.remove(k); log.add("aside write " + k + "=" + v + " -> DB, delete cache key"); }

    // Write-through: write cache and DB together
    static void writeThrough(String k, int v) { cache.put(k, v); db.put(k, v); log.add("write-through " + k + "=" + v + " -> cache + DB"); }

    // Write-behind: write cache now, flush to DB later in a batch
    static final Map<String, Integer> dirty = new LinkedHashMap<>();
    static void writeBehind(String k, int v) { cache.put(k, v); dirty.put(k, v); log.add("write-behind " + k + "=" + v + " -> cache only (DB=" + db.get(k) + ")"); }
    static void flush() { db.putAll(dirty); log.add("flush " + dirty.size() + " dirty keys -> DB=" + db); dirty.clear(); }

    public static void main(String[] args) {
        readAside("stock:ps5"); readAside("stock:ps5");
        writeAside("stock:ps5", 9); readAside("stock:ps5");
        writeThrough("stock:ps5", 8); readAside("stock:ps5");
        writeBehind("stock:ps5", 7); writeBehind("stock:ps5", 6); writeBehind("stock:xbox", 4);
        flush();
        log.forEach(System.out::println);
    }
}
