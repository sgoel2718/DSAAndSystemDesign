import com.sun.net.httpserver.HttpServer;
import java.net.*;
import java.net.http.*;
import java.util.*;

public class HttpDemo {
    public static void main(String[] args) throws Exception {
        Map<String, String> items = new TreeMap<>(Map.of("1", "pen"));
        HttpServer s = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        s.createContext("/items", ex -> {
            String id = ex.getRequestURI().getPath().replace("/items", "").replace("/", "");
            String m = ex.getRequestMethod(); int code; String body = "";
            String etag = "\"v" + items.hashCode() + "\"";
            if (m.equals("GET") && id.isEmpty()) {
                if (etag.equals(ex.getRequestHeaders().getFirst("If-None-Match"))) code = 304;
                else { code = 200; body = items.toString(); ex.getResponseHeaders().add("ETag", etag); }
            } else if (m.equals("GET")) { code = items.containsKey(id) ? 200 : 404; body = items.getOrDefault(id, "not found"); }
            else if (m.equals("PUT")) { code = items.containsKey(id) ? 200 : 201; items.put(id, new String(ex.getRequestBody().readAllBytes())); }
            else if (m.equals("DELETE")) { code = items.remove(id) != null ? 204 : 404; }
            else { code = 405; body = "method not allowed"; }
            byte[] b = body.getBytes();
            ex.sendResponseHeaders(code, code == 204 || code == 304 ? -1 : b.length);
            if (b.length > 0 && code != 304) ex.getResponseBody().write(b);
            ex.close();
        });
        s.start();
        String base = "http://127.0.0.1:" + s.getAddress().getPort() + "/items";
        HttpClient c = HttpClient.newHttpClient();
        HttpResponse<String> r = c.send(HttpRequest.newBuilder(URI.create(base)).build(), HttpResponse.BodyHandlers.ofString());
        String etag = r.headers().firstValue("ETag").orElse("");
        System.out.println("GET /items          -> " + r.statusCode() + " " + r.body() + " ETag=" + etag);
        r = c.send(HttpRequest.newBuilder(URI.create(base)).header("If-None-Match", etag).build(), HttpResponse.BodyHandlers.ofString());
        System.out.println("GET /items (cached) -> " + r.statusCode() + " Not Modified, no body sent");
        for (int i = 0; i < 2; i++) {
            r = c.send(HttpRequest.newBuilder(URI.create(base + "/2")).PUT(HttpRequest.BodyPublishers.ofString("book")).build(), HttpResponse.BodyHandlers.ofString());
            System.out.println("PUT /items/2 book   -> " + r.statusCode() + (i == 0 ? " Created" : " OK (PUT is idempotent: same result)"));
        }
        r = c.send(HttpRequest.newBuilder(URI.create(base + "/9")).build(), HttpResponse.BodyHandlers.ofString());
        System.out.println("GET /items/9        -> " + r.statusCode());
        r = c.send(HttpRequest.newBuilder(URI.create(base + "/1")).DELETE().build(), HttpResponse.BodyHandlers.ofString());
        System.out.println("DELETE /items/1     -> " + r.statusCode() + " No Content");
        r = c.send(HttpRequest.newBuilder(URI.create(base + "/1")).method("PATCH", HttpRequest.BodyPublishers.noBody()).build(), HttpResponse.BodyHandlers.ofString());
        System.out.println("PATCH /items/1      -> " + r.statusCode());
        s.stop(0);
    }
}
