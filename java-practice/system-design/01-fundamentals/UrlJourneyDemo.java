import java.util.*;

public class UrlJourneyDemo {
    // Simulates the steps a browser takes for https://www.example.com and adds up the time.
    static final Map<String, String> browserDnsCache = new HashMap<>();
    static final Map<String, String> cdnCache = new HashMap<>();
    static int clockMs = 0;

    static void step(String what, int ms) { clockMs += ms; System.out.printf("  +%3d ms  %-48s t=%d ms%n", ms, what, clockMs); }

    static String resolve(String host) {
        if (browserDnsCache.containsKey(host)) { step("DNS: browser cache hit", 0); return browserDnsCache.get(host); }
        step("DNS: ask resolver -> root -> .com -> example.com NS", 30);
        browserDnsCache.put(host, "93.184.216.34");
        return "93.184.216.34";
    }

    static String fetch(String path) {
        if (cdnCache.containsKey(path)) { step("CDN edge: cache HIT " + path, 5); return cdnCache.get(path); }
        step("CDN edge: MISS -> origin server " + path, 120);
        cdnCache.put(path, "<html>...</html>");
        return cdnCache.get(path);
    }

    static void visit(String url) {
        clockMs = 0;
        System.out.println("Visit " + url);
        String host = URI_host(url);
        String ip = resolve(host);
        step("TCP handshake with " + ip + " (1 RTT)", 40);
        step("TLS 1.3 handshake (1 RTT)", 40);
        fetch("/");
        step("parse HTML, fetch CSS/JS/images, render", 300);
        System.out.println("  page ready in " + clockMs + " ms\n");
    }

    static String URI_host(String url) { return java.net.URI.create(url).getHost(); }

    public static void main(String[] args) {
        visit("https://www.example.com/");
        visit("https://www.example.com/");   // second visit: DNS cached, CDN warm
    }
}
