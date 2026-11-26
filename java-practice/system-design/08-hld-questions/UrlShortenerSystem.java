import java.util.*;
import java.util.concurrent.atomic.*;

public class UrlShortenerSystem {
    // Key generation (counter ranges + base62), storage, cache-aside reads, 301/302 redirects, expiry and click counting.
    static final String B62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    static String base62(long n) { StringBuilder sb = new StringBuilder(); do { sb.append(B62.charAt((int) (n % 62))); n /= 62; } while (n > 0); return sb.reverse().toString(); }

    static class RangeAllocator {                                              // like ZooKeeper handing out id blocks to each app server
        private final AtomicLong next = new AtomicLong(1_000_000_000L);
        long[] lease(int size) { long s = next.getAndAdd(size); return new long[]{s, s + size}; }
    }
    static class AppServer {
        final String name; final RangeAllocator alloc; long cur, end;
        AppServer(String name, RangeAllocator a) { this.name = name; alloc = a; }
        long nextId() { if (cur == end) { long[] r = alloc.lease(1000); cur = r[0]; end = r[1]; } return cur++; }
    }
    record Link(String code, String longUrl, long expiresAt, String owner) {}

    static final Map<String, Link> db = new HashMap<>();
    static final Map<String, String> cache = new LinkedHashMap<>(16, .75f, true) { protected boolean removeEldestEntry(Map.Entry<String, String> e) { return size() > 2; } };
    static final Map<String, Long> clicks = new TreeMap<>();
    static int dbReads = 0;

    static String shorten(AppServer s, String url, String custom, long ttl, long now) {
        String code = custom != null ? custom : base62(s.nextId());
        if (db.containsKey(code)) return "409 alias taken";
        db.put(code, new Link(code, url, ttl > 0 ? now + ttl : Long.MAX_VALUE, "user-42"));
        return "https://sho.rt/" + code;
    }

    static String redirect(String code, long now) {
        String url = cache.get(code);
        if (url == null) {
            dbReads++; Link l = db.get(code);
            if (l == null) return "404";
            if (l.expiresAt() <= now) return "410 Gone (expired)";
            url = l.longUrl(); cache.put(code, url);
        }
        clicks.merge(code, 1L, Long::sum);                                     // in production: async event to Kafka
        return "302 Location: " + url;
    }

    public static void main(String[] args) {
        RangeAllocator zk = new RangeAllocator(); AppServer a = new AppServer("app-1", zk), b = new AppServer("app-2", zk);
        String s1 = shorten(a, "https://en.wikipedia.org/wiki/System_design", null, 0, 0);
        String s2 = shorten(b, "https://leetcode.com/problems/lru-cache/", null, 0, 0);
        String s3 = shorten(a, "https://sale.example.com/diwali", "diwali", 100, 0);
        System.out.println("app-1 -> " + s1 + "\napp-2 -> " + s2 + "  (different id ranges: no coordination per request)\ncustom -> " + s3);
        System.out.println("custom again -> " + shorten(b, "https://x.com", "diwali", 0, 0));
        String c1 = s1.substring(15);
        for (int i = 0; i < 5; i++) redirect(c1, 10);
        System.out.println("redirect " + c1 + " -> " + redirect(c1, 10) + " | db reads so far " + dbReads + " (rest from cache)");
        System.out.println("redirect diwali at t=50  -> " + redirect("diwali", 50));
        cache.clear();
        System.out.println("redirect diwali at t=150 -> " + redirect("diwali", 150));
        System.out.println("redirect nope            -> " + redirect("nope", 150));
        System.out.println("click counts: " + clicks);
        System.out.printf("7-char base62 codes give %,.0f possible links%n", Math.pow(62, 7));
    }
}
