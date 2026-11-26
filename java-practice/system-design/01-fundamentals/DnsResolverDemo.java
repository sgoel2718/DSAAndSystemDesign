import java.util.*;

public class DnsResolverDemo {
    record Rec(String value, int ttl) {}
    static final Map<String, Map<String, Rec>> servers = new HashMap<>();      // server -> (name -> record)
    static final Map<String, long[]> cacheExpiry = new HashMap<>();
    static final Map<String, String> cache = new HashMap<>();
    static int queries = 0;

    static {
        servers.put("root", Map.of("com.", new Rec("NS tld-com", 172800)));
        servers.put("tld-com", Map.of("example.com.", new Rec("NS ns1.example", 172800)));
        servers.put("ns1.example", Map.of("www.example.com.", new Rec("A 93.184.216.34", 300), "shop.example.com.", new Rec("CNAME www.example.com.", 300)));
    }

    static String resolve(String name, long now) {
        if (cache.containsKey(name) && cacheExpiry.get(name)[0] > now) return cache.get(name) + "  (cache)";
        String server = "root", zone;
        String[] labels = name.split("\\.");
        String[] path = {"com.", labels[labels.length - 2] + ".com.", name};
        Rec r = null;
        for (String q : path) {
            queries++;
            r = servers.get(server).get(q);
            if (r == null) return "NXDOMAIN";
            if (r.value().startsWith("NS ")) server = r.value().substring(3); else break;
        }
        if (r.value().startsWith("CNAME ")) return resolve(r.value().substring(6), now);
        cache.put(name, r.value()); cacheExpiry.put(name, new long[]{now + r.ttl()});
        return r.value();
    }

    public static void main(String[] args) {
        System.out.println("t=0    www.example.com  -> " + resolve("www.example.com.", 0) + "  [queries so far " + queries + "]");
        System.out.println("t=10   www.example.com  -> " + resolve("www.example.com.", 10) + "  [queries so far " + queries + "]");
        System.out.println("t=20   shop.example.com -> " + resolve("shop.example.com.", 20) + "  [queries so far " + queries + "]");
        System.out.println("t=400  www.example.com  -> " + resolve("www.example.com.", 400) + "  [TTL 300 expired, queries " + queries + "]");
        System.out.println("t=401  nope.example.com -> " + resolve("nope.example.com.", 401));
    }
}
