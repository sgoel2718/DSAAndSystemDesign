import java.util.*;

public class CdnDemo {
    record Cached(String body, long expiresAt) {}

    static class Origin { int hits; String get(String path) { hits++; return "content of " + path; } }

    static class Edge {
        final String city; final int rttMs; final Origin origin; final Map<String, Cached> cache = new HashMap<>();
        Edge(String city, int rttMs, Origin origin) { this.city = city; this.rttMs = rttMs; this.origin = origin; }
        String get(String path, long now, int maxAge) {
            Cached c = cache.get(path);
            if (c != null && c.expiresAt() > now) return String.format("%-8s HIT  %-22s %3d ms", city, path, rttMs);
            String body = origin.get(path);
            cache.put(path, new Cached(body, now + maxAge));
            return String.format("%-8s MISS %-22s %3d ms (went to origin in Virginia)", city, path, rttMs + 200);
        }
    }

    public static void main(String[] args) {
        Origin origin = new Origin();
        Edge mumbai = new Edge("Mumbai", 8, origin), london = new Edge("London", 10, origin);
        System.out.println(mumbai.get("/img/cat.jpg", 0, 86_400));
        System.out.println(mumbai.get("/img/cat.jpg", 5, 86_400));
        System.out.println(london.get("/img/cat.jpg", 6, 86_400));
        System.out.println(mumbai.get("/app.3f9c.js", 7, 31_536_000));
        System.out.println("-- deploy: new bundle gets a new versioned name, no purge needed --");
        System.out.println(mumbai.get("/app.8d21.js", 100, 31_536_000));
        System.out.println(mumbai.get("/api/price", 101, 0) + "  <- dynamic, max-age 0");
        System.out.println(mumbai.get("/img/cat.jpg", 90_000, 86_400) + "  <- next day, expired");
        System.out.println("origin served " + origin.hits + " of 8 requests");
    }
}
