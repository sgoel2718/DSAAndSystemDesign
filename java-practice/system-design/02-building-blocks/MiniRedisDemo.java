import java.util.*;

public class MiniRedisDemo {
    // A tiny in-memory Redis: strings with TTL, INCR, lists, sorted sets. Single-threaded command loop = atomic commands.
    final Map<String, Object> data = new HashMap<>();
    final Map<String, Long> expiry = new HashMap<>();
    long now = 0;

    Object get(String k) { if (expiry.containsKey(k) && expiry.get(k) <= now) { data.remove(k); expiry.remove(k); } return data.get(k); }
    String set(String k, String v, Long exSeconds, boolean nx) {
        if (nx && get(k) != null) return "nil";
        data.put(k, v); if (exSeconds != null) expiry.put(k, now + exSeconds * 1000); else expiry.remove(k); return "OK";
    }
    long incr(String k) { long v = Long.parseLong((String) Optional.ofNullable(get(k)).orElse("0")) + 1; data.put(k, String.valueOf(v)); return v; }
    @SuppressWarnings("unchecked") long lpush(String k, String v) { Deque<String> d = (Deque<String>) data.computeIfAbsent(k, x -> new ArrayDeque<>()); d.addFirst(v); return d.size(); }
    @SuppressWarnings("unchecked") List<String> lrange(String k, int a, int b) { List<String> l = new ArrayList<>((Deque<String>) data.getOrDefault(k, new ArrayDeque<>())); return l.subList(a, Math.min(b + 1, l.size())); }
    @SuppressWarnings("unchecked") double zincrby(String k, double by, String m) { Map<String, Double> z = (Map<String, Double>) data.computeIfAbsent(k, x -> new HashMap<>()); return z.merge(m, by, Double::sum); }
    @SuppressWarnings("unchecked") List<String> zrevrange(String k, int n) {
        Map<String, Double> z = (Map<String, Double>) data.get(k);
        return z.entrySet().stream().sorted(Map.Entry.<String, Double>comparingByValue().reversed()).limit(n).map(e -> e.getKey() + "=" + e.getValue().intValue()).toList();
    }

    public static void main(String[] args) {
        MiniRedisDemo r = new MiniRedisDemo();
        System.out.println("SET session:abc asha EX 60 -> " + r.set("session:abc", "asha", 60L, false));
        System.out.println("INCR views:post:9 x3       -> " + r.incr("views:post:9") + "," + r.incr("views:post:9") + "," + r.incr("views:post:9"));
        System.out.println("SET lock:order NX EX 5     -> " + r.set("lock:order", "worker-1", 5L, true));
        System.out.println("SET lock:order NX EX 5     -> " + r.set("lock:order", "worker-2", 5L, true) + " (already locked)");
        for (String p : List.of("p1", "p2", "p3")) r.lpush("feed:42", p);
        System.out.println("LRANGE feed:42 0 1         -> " + r.lrange("feed:42", 0, 1));
        r.zincrby("lb", 50, "asha"); r.zincrby("lb", 80, "ravi"); r.zincrby("lb", 40, "asha");
        System.out.println("ZREVRANGE lb 0 1           -> " + r.zrevrange("lb", 2));
        r.now += 61_000;
        System.out.println("61 s later GET session:abc -> " + r.get("session:abc") + " (expired)");
        System.out.println("            GET lock:order -> " + r.get("lock:order") + " (lock auto-released)");
    }
}
