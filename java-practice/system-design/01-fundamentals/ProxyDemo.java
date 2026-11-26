import java.util.*;

public class ProxyDemo {
    interface Origin { String get(String path); }

    // Reverse proxy in front of servers: hides them, balances load, caches responses
    static class ReverseProxy implements Origin {
        private final List<Origin> backends; private final Map<String, String> cache = new HashMap<>(); private int rr = 0;
        ReverseProxy(List<Origin> backends) { this.backends = backends; }
        public String get(String path) {
            if (cache.containsKey(path)) return cache.get(path) + " [proxy cache]";
            String res = backends.get(rr++ % backends.size()).get(path);
            if (path.startsWith("/static")) cache.put(path, res);
            return res;
        }
    }

    // Forward proxy in front of clients: hides them, enforces an allow/deny policy
    static class ForwardProxy {
        private final Set<String> blocked = Set.of("games.example");
        String fetch(String clientIp, String host, Map<String, Origin> internet, String path) {
            if (blocked.contains(host)) return "403 blocked by company policy";
            return internet.get(host).get(path) + " (site saw proxy IP, not " + clientIp + ")";
        }
    }

    public static void main(String[] args) {
        Origin s1 = p -> "server-1 " + p, s2 = p -> "server-2 " + p;
        ReverseProxy nginx = new ReverseProxy(List.of(s1, s2));
        for (String p : new String[]{"/api/cart", "/api/cart", "/static/logo.png", "/static/logo.png"}) System.out.println("reverse: " + nginx.get(p));
        ForwardProxy corp = new ForwardProxy();
        Map<String, Origin> internet = Map.of("news.example", p -> "news page " + p, "games.example", p -> "game");
        System.out.println("forward: " + corp.fetch("10.0.0.5", "news.example", internet, "/today"));
        System.out.println("forward: " + corp.fetch("10.0.0.5", "games.example", internet, "/play"));
    }
}
