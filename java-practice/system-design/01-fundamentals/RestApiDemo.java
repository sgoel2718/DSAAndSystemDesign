import com.sun.net.httpserver.*;
import java.net.*;
import java.net.http.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class RestApiDemo {
    record Order(long id, String item, String status, int version) {}
    static final Map<Long, Order> db = new ConcurrentSkipListMap<>();
    static final Map<String, Long> idempotency = new ConcurrentHashMap<>();
    static final AtomicLong seq = new AtomicLong(100);

    static void send(HttpExchange ex, int code, String body) throws java.io.IOException {
        byte[] b = body.getBytes(); ex.sendResponseHeaders(code, b.length); ex.getResponseBody().write(b); ex.close();
    }

    public static void main(String[] args) throws Exception {
        HttpServer s = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        s.createContext("/v1/orders", ex -> {
            String path = ex.getRequestURI().getPath(), q = Optional.ofNullable(ex.getRequestURI().getQuery()).orElse("");
            switch (ex.getRequestMethod()) {
                case "POST" -> {
                    String key = ex.getRequestHeaders().getFirst("Idempotency-Key");
                    long id = idempotency.computeIfAbsent(key, k -> { long n = seq.incrementAndGet(); db.put(n, new Order(n, new String(readAll(ex)), "PENDING", 1)); return n; });
                    ex.getResponseHeaders().add("Location", "/v1/orders/" + id);
                    send(ex, 201, db.get(id).toString());
                }
                case "GET" -> {
                    if (path.equals("/v1/orders")) {                                  // cursor pagination: ?after=ID&limit=N
                        long after = q.contains("after=") ? Long.parseLong(q.replaceAll(".*after=(\\d+).*", "$1")) : 0;
                        List<Long> page = db.keySet().stream().filter(k -> k > after).limit(2).toList();
                        String next = page.size() == 2 ? String.valueOf(page.get(1)) : "null";
                        send(ex, 200, "{items:" + page + ", next_cursor:" + next + "}");
                    } else { Order o = db.get(Long.parseLong(path.substring(11))); send(ex, o == null ? 404 : 200, String.valueOf(o)); }
                }
                case "PATCH" -> {
                    long id = Long.parseLong(path.substring(11)); Order o = db.get(id);
                    String ifMatch = ex.getRequestHeaders().getFirst("If-Match");
                    if (!String.valueOf(o.version()).equals(ifMatch)) { send(ex, 412, "version changed, re-read first"); return; }
                    Order n = new Order(id, o.item(), new String(readAll(ex)), o.version() + 1); db.put(id, n); send(ex, 200, n.toString());
                }
                default -> send(ex, 405, "");
            }
        });
        s.start();
        HttpClient c = HttpClient.newHttpClient(); String base = "http://127.0.0.1:" + s.getAddress().getPort() + "/v1/orders";
        for (String[] o : new String[][]{{"k1", "shoes"}, {"k1", "shoes"}, {"k2", "socks"}, {"k3", "cap"}}) {
            var r = c.send(HttpRequest.newBuilder(URI.create(base)).header("Idempotency-Key", o[0]).POST(HttpRequest.BodyPublishers.ofString(o[1])).build(), HttpResponse.BodyHandlers.ofString());
            System.out.println("POST " + o[1] + " key=" + o[0] + " -> " + r.statusCode() + " " + r.headers().firstValue("Location").orElse("") + " " + r.body());
        }
        System.out.println("GET page 1 -> " + get(c, base));
        System.out.println("GET page 2 -> " + get(c, base + "?after=102"));
        System.out.println("PATCH v1   -> " + patch(c, base + "/101", "1", "PAID"));
        System.out.println("PATCH v1   -> " + patch(c, base + "/101", "1", "CANCELLED") + "  (stale version)");
        s.stop(0);
    }

    static byte[] readAll(HttpExchange ex) { try { return ex.getRequestBody().readAllBytes(); } catch (Exception e) { return new byte[0]; } }
    static String get(HttpClient c, String u) throws Exception { var r = c.send(HttpRequest.newBuilder(URI.create(u)).build(), HttpResponse.BodyHandlers.ofString()); return r.statusCode() + " " + r.body(); }
    static String patch(HttpClient c, String u, String v, String body) throws Exception {
        var r = c.send(HttpRequest.newBuilder(URI.create(u)).header("If-Match", v).method("PATCH", HttpRequest.BodyPublishers.ofString(body)).build(), HttpResponse.BodyHandlers.ofString());
        return r.statusCode() + " " + r.body();
    }
}
