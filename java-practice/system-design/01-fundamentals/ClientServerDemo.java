import com.sun.net.httpserver.HttpServer;
import java.net.*;
import java.net.http.*;
import java.util.*;
import java.util.concurrent.*;

public class ClientServerDemo {
    // Session data lives in a shared store, NOT in a server's memory, so any server can answer.
    static final Map<String, String> sharedSessionStore = new ConcurrentHashMap<>();

    static HttpServer startServer(String name) throws Exception {
        HttpServer s = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        s.createContext("/profile", ex -> {
            String cookie = Optional.ofNullable(ex.getRequestHeaders().getFirst("Cookie")).orElse("");
            String sid = cookie.replace("session=", "");
            String user = sharedSessionStore.getOrDefault(sid, "anonymous");
            byte[] body = ("served by " + name + " for user=" + user).getBytes();
            ex.sendResponseHeaders(200, body.length);
            ex.getResponseBody().write(body);
            ex.close();
        });
        s.start();
        return s;
    }

    public static void main(String[] args) throws Exception {
        HttpServer a = startServer("server-A"), b = startServer("server-B");
        sharedSessionStore.put("abc123", "asha");                        // login happened earlier
        HttpClient client = HttpClient.newHttpClient();
        List<HttpServer> pool = List.of(a, b);
        for (int i = 0; i < 4; i++) {                                     // round-robin across servers
            HttpServer target = pool.get(i % 2);
            URI uri = URI.create("http://127.0.0.1:" + target.getAddress().getPort() + "/profile");
            HttpRequest req = HttpRequest.newBuilder(uri).header("Cookie", "session=abc123").build();
            HttpResponse<String> res = client.send(req, HttpResponse.BodyHandlers.ofString());
            System.out.println("request " + (i + 1) + " -> " + res.statusCode() + " " + res.body());
        }
        a.stop(0); b.stop(0);
        System.out.println("Both servers knew the user because the session is in the shared store (stateless servers).");
    }
}
