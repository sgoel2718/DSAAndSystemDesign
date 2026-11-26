import java.util.*;
import java.util.function.*;

public class ApiGatewayDemo {
    record Request(String path, String token, String ip) {}
    record Response(int status, String body) {}

    static final Map<String, Function<Request, Response>> routes = new LinkedHashMap<>();
    static final Map<String, String> validTokens = Map.of("tok-asha", "user-42");
    static final Map<String, Integer> callsPerIp = new HashMap<>();
    static int reqId = 0;

    static Response gateway(Request r) {
        String id = "req-" + (++reqId);
        String user = validTokens.get(r.token());
        if (user == null) return log(id, r, new Response(401, "invalid token"));                 // authentication
        int n = callsPerIp.merge(r.ip(), 1, Integer::sum);
        if (n > 3) return log(id, r, new Response(429, "rate limited"));                         // rate limiting
        for (var e : routes.entrySet())
            if (r.path().startsWith(e.getKey())) return log(id, r, e.getValue().apply(new Request(r.path(), user, r.ip())));   // routing; pass identity
        return log(id, r, new Response(404, "no route"));
    }

    static Response log(String id, Request r, Response res) {
        System.out.printf("%-6s %-14s ip=%-8s -> %d %s%n", id, r.path(), r.ip(), res.status(), res.body());
        return res;
    }

    public static void main(String[] args) {
        routes.put("/users", r -> new Response(200, "user-service: profile of " + r.token()));
        routes.put("/orders", r -> new Response(200, "order-service: orders of " + r.token()));
        gateway(new Request("/users/me", "tok-asha", "1.2.3.4"));
        gateway(new Request("/orders", "tok-asha", "1.2.3.4"));
        gateway(new Request("/orders", "bad", "5.6.7.8"));
        gateway(new Request("/search", "tok-asha", "1.2.3.4"));
        gateway(new Request("/orders", "tok-asha", "1.2.3.4"));
    }
}
