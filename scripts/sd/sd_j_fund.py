"""Java practice programs: Fundamentals tab."""
from sd_j_util import J

J("what-is-sd", r'''
import java.util.*;

public class SystemGrowthDemo {
    // A tiny model of how design choices change capacity as users grow.
    record Stage(String name, int appServers, boolean cache, int readReplicas) {
        double appCapacity() { return appServers * 1_000.0; }                          // each app server: ~1k req/s
        double dbCapacity() { return 5_000.0 * (1 + readReplicas) / (cache ? 0.1 : 1.0); } // 5k reads/s per DB node; cache absorbs 90%
        double capacity() { return Math.min(appCapacity(), dbCapacity()); }
        String bottleneck() { return appCapacity() <= dbCapacity() ? "app servers" : "database"; }
    }

    public static void main(String[] args) {
        List<Stage> stages = List.of(
            new Stage("1 server", 1, false, 0),
            new Stage("LB + 4 app servers", 4, false, 0),
            new Stage("LB + 12 app servers", 12, false, 0),
            new Stage("+ Redis cache", 12, true, 0),
            new Stage("+ 60 app servers, 2 replicas", 60, true, 2));
        int[] loads = {3_500, 8_000, 30_000};
        for (int load : loads) {
            System.out.printf("%nPeak load %,d req/s%n", load);
            for (Stage s : stages) {
                boolean ok = s.capacity() >= load;
                System.out.printf("  %-30s capacity %,9.0f  %s%n", s.name(), s.capacity(), ok ? "OK" : "overloaded, bottleneck: " + s.bottleneck());
            }
        }
    }
}
''', ["Change the cache hit ratio from 90% to 99% (`cache ? 0.01 : 1.0`) and see which stage's bottleneck moves.",
      "Add a stage with sharding: give the DB 4× the write/read capacity and test it at 120,000 req/s.",
      "Add a `costPerMonth()` method (e.g. $150 per app server, $1,200 per DB node) and print cost per 1,000 req/s for each stage."])

J("client-server", r'''
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
''', ["Move the session map inside `startServer` (one map per server) and see request 2 become `anonymous`: that's why stateful servers need sticky sessions.",
      "Add a `/login?user=ravi` endpoint that creates a random session id and returns it in a `Set-Cookie` header.",
      "Stop server-A after request 2 and make the client retry the next server on `ConnectException`."])

J("url-journey", r'''
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
''', ["Add HTTP keep-alive: on the second visit skip the TCP and TLS steps and see how much time it saves.",
      "Give DNS entries a TTL (e.g. 60 s of simulated time) and expire them.",
      "Add a 'browser cache' for static assets with `Cache-Control: max-age` so the render step drops to 100 ms on repeat visits."])

J("latency-throughput", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class LatencyThroughputDemo {
    // Each request "takes" 20 ms (sleep). Throughput depends on how many run in parallel: Little's law.
    static double runWithThreads(int threads, int requests) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(threads);
        long start = System.nanoTime();
        List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < requests; i++) fs.add(pool.submit(() -> { try { Thread.sleep(20); } catch (InterruptedException e) {} }));
        for (Future<?> f : fs) f.get();
        pool.shutdown();
        double seconds = (System.nanoTime() - start) / 1e9;
        return requests / seconds;
    }

    static long percentile(List<Long> sorted, double p) { return sorted.get((int) Math.ceil(p * sorted.size()) - 1); }

    public static void main(String[] args) throws Exception {
        for (int t : new int[]{1, 4, 16}) {
            double tput = runWithThreads(t, 160);
            System.out.printf("threads=%2d  latency=20 ms  throughput ~ %4.0f req/s  (Little's law predicts %d)%n", t, Math.floor(tput / 10) * 10, t * 50);
        }
        // Percentiles: a fixed, seeded latency sample with a slow tail
        Random r = new Random(7);
        List<Long> lat = new ArrayList<>();
        for (int i = 0; i < 1000; i++) lat.add((long) (r.nextInt(100) < 98 ? 30 + r.nextInt(40) : 300 + r.nextInt(900)));
        Collections.sort(lat);
        double avg = lat.stream().mapToLong(Long::longValue).average().orElse(0);
        System.out.printf("%naverage=%.0f ms  p50=%d  p90=%d  p99=%d  max=%d%n", avg, percentile(lat, .50), percentile(lat, .90), percentile(lat, .99), lat.get(999));
        System.out.println("The average hides the slow tail; alert on p99.");
    }
}
''', ["Change the sleep to 100 ms: how many threads do you need to keep 160 req/s?",
      "Make 2% of requests take 500 ms and re-run: watch throughput drop for a small pool (head-of-line blocking).",
      "Compute p99.9 and add a check that fails if p99 > 250 ms (an SLO test)."])

J("scalability", r'''
import java.util.*;

public class ScalabilityDemo {
    interface Server { String name(); int capacity(); }
    record Machine(String name, int cores) implements Server { public int capacity() { return cores * 250; } }

    static int handle(List<? extends Server> servers, int load) {
        int capacity = servers.stream().mapToInt(Server::capacity).sum();
        return Math.min(load, capacity);
    }

    public static void main(String[] args) {
        int load = 20_000;
        // Vertical: keep buying a bigger single machine
        for (int cores : new int[]{8, 32, 96}) {
            List<Machine> one = List.of(new Machine("big-" + cores, cores));
            System.out.printf("vertical   1 x %2d cores -> serves %,6d of %,d req/s%n", cores, handle(one, load), load);
        }
        System.out.println("           (no 300-core machine to buy; and if it dies, everything is down)");
        // Horizontal: add identical 8-core machines behind a load balancer
        for (int n : new int[]{2, 5, 10}) {
            List<Machine> fleet = new ArrayList<>();
            for (int i = 0; i < n; i++) fleet.add(new Machine("app-" + i, 8));
            System.out.printf("horizontal %2d x 8 cores -> serves %,6d of %,d req/s%n", n, handle(fleet, load), load);
        }
        List<Machine> fleet = new ArrayList<>();
        for (int i = 0; i < 10; i++) fleet.add(new Machine("app-" + i, 8));
        fleet.remove(3);
        System.out.printf("one of 10 servers fails -> still serves %,d req/s%n", handle(fleet, load));
    }
}
''', ["Add a database with fixed capacity 12,000 req/s that every request needs: at what fleet size does adding app servers stop helping?",
      "Add a `pricePerHour` to `Machine` where cost grows faster than cores for big machines (e.g. cores^1.3) and compare cost per req/s.",
      "Simulate an availability zone failure: put servers in 3 zones and remove one zone."])

J("availability", r'''
public class AvailabilityDemo {
    static double series(double... parts) { double a = 1; for (double p : parts) a *= p; return a; }
    static double parallel(double each, int copies) { return 1 - Math.pow(1 - each, copies); }
    static String downtime(double a) {
        double minutes = (1 - a) * 365 * 24 * 60;
        return minutes > 120 ? String.format("%.1f hours/year", minutes / 60) : String.format("%.1f minutes/year", minutes);
    }

    public static void main(String[] args) {
        for (double a : new double[]{0.99, 0.999, 0.9999, 0.99999})
            System.out.printf("%.3f%% -> %s%n", a * 100, downtime(a));
        double chain = series(0.9999, 0.999, 0.9995);                     // LB -> app -> DB
        System.out.printf("%nseries LB(99.99) x app(99.9) x DB(99.95) = %.3f%% -> %s%n", chain * 100, downtime(chain));
        double app2 = parallel(0.999, 2), db2 = parallel(0.9995, 2);
        double redundant = series(0.9999, app2, db2);
        System.out.printf("with 2 app servers and a DB standby          = %.4f%% -> %s%n", redundant * 100, downtime(redundant));
        // error budget for an SLO of 99.9% over 30 days
        double budgetMin = 0.001 * 30 * 24 * 60;
        System.out.printf("%nSLO 99.9%% over 30 days -> error budget %.1f minutes; a 25-minute outage uses %.0f%% of it%n", budgetMin, 25 / budgetMin * 100);
    }
}
''', ["Add a fourth dependency (an external payment API at 99.5%) in series: how bad does it get, and what does a fallback do?",
      "Find how many 99% servers in parallel you need to reach 99.999%.",
      "Write `remainingBudget(List<Integer> outageMinutes)` that returns what's left of the monthly error budget."])

J("reliability-terms", r'''
import java.util.*;

public class ReliabilityDemo {
    // Simulates a year of a service: failures arrive every ~MTBF hours, each takes MTTR hours to fix.
    static double simulate(double mtbfHours, double mttrHours, long seed) {
        Random r = new Random(seed);
        double t = 0, down = 0, year = 365 * 24;
        while (t < year) {
            double up = -Math.log(1 - r.nextDouble()) * mtbfHours;   // exponential time to next failure
            t += up;
            if (t >= year) break;
            double repair = Math.min(mttrHours, year - t);
            down += repair; t += repair;
        }
        return 1 - down / year;
    }

    public static void main(String[] args) {
        double[][] cases = {{1000, 1}, {1000, 0.1}, {5000, 1}};
        for (double[] c : cases) {
            double formula = c[0] / (c[0] + c[1]);
            double sim = simulate(c[0], c[1], 42);
            System.out.printf("MTBF %5.0f h, MTTR %4.1f h -> formula %.4f%%, simulated year %.4f%%%n", c[0], c[1], formula * 100, sim * 100);
        }
        System.out.println("\nCutting repair time 10x helps as much as making failures 10x rarer.");
        // Durability: chance to lose an object stored on 3 independent disks with 1% annual failure, no repair
        double loss3 = Math.pow(0.01, 3);
        System.out.printf("P(lose all 3 copies in a year, no re-replication) = %.0e%n", loss3);
    }
}
''', ["Add a 'fault tolerance' mode: two replicas, the service is down only when both are failed at the same time.",
      "Model re-replication: after one disk fails, a new copy is made within 6 hours. How does durability change?",
      "Print the number of incidents per year next to the availability for each case."])

J("estimation", r'''
public class EstimationDemo {
    static String human(double v, String unit) {
        String[] counts = {"", " thousand", " million", " billion", " trillion"}, bytes = {" B", " KB", " MB", " GB", " TB", " PB", " EB"};
        String[] u = unit.equals("B") ? bytes : counts; int i = 0;
        while (Math.abs(v) >= 1000 && i < u.length - 1) { v /= 1000; i++; }
        return String.format("%.1f%s", v, u[i]) + (unit.equals("B") || unit.isEmpty() ? "" : " " + unit);
    }

    public static void main(String[] args) {
        double dau = 100e6, uploadShare = 0.10, photoBytes = 2e6, viewsPerUser = 10, peak = 3;
        double uploadsPerDay = dau * uploadShare;
        double writeQps = uploadsPerDay / 86_400;
        double readQps = dau * viewsPerUser / 86_400;
        double storagePerDay = uploadsPerDay * photoBytes;
        System.out.println("Photo app estimate");
        System.out.println("  uploads/day      = " + human(uploadsPerDay, ""));
        System.out.println("  write QPS        = " + human(writeQps, "/s") + ", peak " + human(writeQps * peak, "/s"));
        System.out.println("  read QPS         = " + human(readQps, "/s") + ", peak " + human(readQps * peak, "/s"));
        System.out.println("  read:write ratio = " + Math.round(readQps / writeQps) + " : 1  -> read-heavy, cache + CDN");
        System.out.println("  storage/day      = " + human(storagePerDay, "B"));
        System.out.println("  storage 5 years  = " + human(storagePerDay * 365 * 5, "B") + " -> object storage");
        double egress = readQps * 200e3;                                  // 200 KB thumbnails
        System.out.println("  egress bandwidth = " + human(egress, "B") + "/s -> CDN essential");
    }
}
''', ["Redo it for a chat app: 500 M DAU, 40 messages/user/day, 100 bytes each, keep 5 years.",
      "Add 3x replication to the storage numbers.",
      "Estimate how many app servers you need at peak if one server handles 2,000 req/s."])

J("latency-numbers", r'''
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class LatencyNumbersDemo {
    // Measures a few of the 'latency numbers' on this machine. Your numbers will differ; the ratios are the lesson.
    public static void main(String[] args) throws Exception {
        int n = 4_000_000;
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = i;
        long t = System.nanoTime(); long sum = 0;
        for (int i = 0; i < n; i++) sum += arr[i];                          // sequential: cache-friendly
        double seqNs = (System.nanoTime() - t) / (double) n;
        int[] idx = new int[n]; Random r = new Random(1);
        for (int i = 0; i < n; i++) idx[i] = r.nextInt(n);
        t = System.nanoTime();
        for (int i = 0; i < n; i++) sum += arr[idx[i]];                     // random: cache misses
        double rndNs = (System.nanoTime() - t) / (double) n;
        Path f = Files.createTempFile("lat", ".bin");
        byte[] mb = new byte[1 << 20];
        t = System.nanoTime();
        try (OutputStream o = new FileOutputStream(f.toFile())) { for (int i = 0; i < 16; i++) o.write(mb); }
        double writeMs = (System.nanoTime() - t) / 1e6 / 16;
        t = System.nanoTime();
        try (InputStream in = new FileInputStream(f.toFile())) { while (in.read(mb) > 0) {} }
        double readMs = (System.nanoTime() - t) / 1e6 / 16;
        Files.delete(f);
        System.out.printf("sequential array read : %.2f ns per element%n", seqNs);
        System.out.printf("random array read     : %.2f ns per element (%.0fx slower: cache misses)%n", rndNs, rndNs / seqNs);
        System.out.printf("write 1 MB to file    : %.3f ms (OS page cache)%n", writeMs);
        System.out.printf("read 1 MB from file   : %.3f ms%n", readMs);
        System.out.println("reference: same-datacenter round trip ~0.5 ms, India<->US ~200 ms");
        if (sum == 42) System.out.println();
    }
}
''', ["Add a measurement of `Thread.sleep(1)` and see how far from 1 ms it is.",
      "Measure a `HashMap.get` on 1 million keys vs a `TreeMap.get` and explain the difference.",
      "Add an in-memory cache in front of the file read and compare repeated reads."])

J("perf-vs-scale", r'''
import java.util.*;

public class QueueingDemo {
    // Single server queue simulated with seeded random arrivals: latency explodes as utilisation approaches 100%.
    static double avgLatency(double utilisation, long seed) {
        Random r = new Random(seed);
        double serviceMs = 10, arrivalRate = utilisation / serviceMs;      // requests per ms
        double t = 0, serverFreeAt = 0, total = 0; int n = 200_000;
        for (int i = 0; i < n; i++) {
            t += -Math.log(1 - r.nextDouble()) / arrivalRate;               // next arrival
            double start = Math.max(t, serverFreeAt);
            double service = -Math.log(1 - r.nextDouble()) * serviceMs;
            serverFreeAt = start + service;
            total += serverFreeAt - t;                                      // waiting + service
        }
        return total / n;
    }

    public static void main(String[] args) {
        System.out.println("utilisation  avg latency   (theory M/M/1: 10 ms / (1 - rho))");
        for (double u : new double[]{0.5, 0.7, 0.8, 0.9, 0.95}) {
            System.out.printf("   %3.0f%%       %6.1f ms    %6.1f ms%n", u * 100, avgLatency(u, 11), 10 / (1 - u));
        }
        System.out.println("\nFast for one user (10 ms) is a performance property;");
        System.out.println("staying fast as load grows needs headroom (scale out before ~70-80% busy).");
    }
}
''', ["Add a second server (two queues, send each request to the shorter one) and compare at 90% load.",
      "Add a timeout: drop requests that would wait more than 200 ms and count them.",
      "Simulate a retry storm: dropped requests are retried once, which adds load. What happens at 90%?"])

J("cap-intro", r'''
import java.util.*;

public class CapDemo {
    static class Replica {
        final String name; int balance = 800; boolean partitioned;
        Replica(String name) { this.name = name; }
    }

    static Replica mumbai = new Replica("Mumbai"), chennai = new Replica("Chennai");

    static void write(Replica at, int value) {
        at.balance = value;
        if (!at.partitioned) { mumbai.balance = value; chennai.balance = value; }   // replicate when the link works
    }

    static String read(Replica at, boolean preferConsistency) {
        if (at.partitioned && preferConsistency) return "ERROR: can't confirm latest value (CP)";
        return at.balance + (at.partitioned ? " (may be stale, AP)" : "");
    }

    public static void main(String[] args) {
        write(mumbai, 500);
        System.out.println("link OK      : Chennai reads " + read(chennai, true));
        mumbai.partitioned = chennai.partitioned = true;                 // cut the network
        write(mumbai, 200);
        System.out.println("partitioned  : Mumbai wrote 200");
        System.out.println("  CP choice  : Chennai reads " + read(chennai, true));
        System.out.println("  AP choice  : Chennai reads " + read(chennai, false));
        mumbai.partitioned = chennai.partitioned = false;                // heal and resync
        chennai.balance = mumbai.balance;
        System.out.println("healed       : Chennai reads " + read(chennai, true));
    }
}
''', ["Let both sides accept writes during the partition (Mumbai 200, Chennai 300) and implement last-write-wins with timestamps when healing.",
      "Add a third replica and implement 'accept writes only if a majority (2 of 3) is reachable'.",
      "Make shopping-cart reads AP and balance reads CP in the same program."])

J("osi-tcpip", r'''
public class EncapsulationDemo {
    // Shows how each layer wraps the one above it, then unwraps on the receiver.
    static String http(String path) { return "GET " + path + " HTTP/1.1|Host: shop.com"; }
    static String tcp(String payload, int srcPort, int dstPort) { return "[TCP src=" + srcPort + " dst=" + dstPort + " seq=1]" + payload; }
    static String ip(String segment, String src, String dst) { return "[IP " + src + "->" + dst + " ttl=64]" + segment; }
    static String ethernet(String packet, String srcMac, String dstMac) { return "[ETH " + srcMac + "->" + dstMac + "]" + packet + "[CRC]"; }

    static String strip(String frame, String layer) {
        int end = frame.indexOf(']') + 1;
        String rest = frame.substring(end);
        if (layer.equals("ETH")) rest = rest.substring(0, rest.length() - "[CRC]".length());
        return rest;
    }

    public static void main(String[] args) {
        String app = http("/cart");
        String seg = tcp(app, 51544, 443);
        String pkt = ip(seg, "10.0.0.7", "142.250.1.1");
        String frame = ethernet(pkt, "aa:bb", "cc:dd");
        System.out.println("L7 application: " + app);
        System.out.println("L4 transport  : " + seg);
        System.out.println("L3 network    : " + pkt);
        System.out.println("L2 link       : " + frame);
        String up = strip(strip(strip(frame, "ETH"), "IP"), "TCP");
        System.out.println("\nreceiver unwraps -> " + up);
        System.out.println("an L4 load balancer reads only up to [TCP ...]; an L7 one reads 'GET /cart' and can route by path");
    }
}
''', ["Write an `l4Route(frame)` that picks a backend by destination port and an `l7Route(frame)` that picks by URL path.",
      "Add TTL decrement at each router hop and drop the packet at 0.",
      "Split the HTTP payload into 2 TCP segments with seq numbers and reassemble them in order."])

J("ip-dns", r'''
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
''', ["Cache NS records too, so the second lookup of a new name in example.com skips root and TLD.",
      "Add GeoDNS: return a different A record depending on the client's country.",
      "Add weighted round-robin A records (two IPs, 80/20) for a simple DNS load balancer."])

J("tcp-udp", r'''
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;

public class TcpUdpDemo {
    public static void main(String[] args) throws Exception {
        // TCP: connection, ordered reliable byte stream
        try (ServerSocket server = new ServerSocket(0, 50, InetAddress.getLoopbackAddress())) {
            Thread t = new Thread(() -> {
                try (Socket s = server.accept();
                     BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream()));
                     PrintWriter out = new PrintWriter(s.getOutputStream(), true)) {
                    String line;
                    while ((line = in.readLine()) != null) out.println("echo:" + line);
                } catch (IOException ignored) {}
            });
            t.start();
            try (Socket c = new Socket(InetAddress.getLoopbackAddress(), server.getLocalPort());
                 PrintWriter out = new PrintWriter(c.getOutputStream(), true);
                 BufferedReader in = new BufferedReader(new InputStreamReader(c.getInputStream()))) {
                for (String m : new String[]{"one", "two", "three"}) { out.println(m); System.out.println("TCP  sent " + m + " <- " + in.readLine()); }
            }
            t.join();
        }
        // UDP: no connection, each datagram stands alone; may be lost or reordered on real networks
        try (DatagramSocket server = new DatagramSocket(0, InetAddress.getLoopbackAddress());
             DatagramSocket client = new DatagramSocket()) {
            for (String m : new String[]{"frame-1", "frame-2", "frame-3"}) {
                byte[] b = m.getBytes(StandardCharsets.UTF_8);
                client.send(new DatagramPacket(b, b.length, InetAddress.getLoopbackAddress(), server.getLocalPort()));
            }
            server.setSoTimeout(500);
            byte[] buf = new byte[100];
            for (int i = 0; i < 3; i++) {
                DatagramPacket p = new DatagramPacket(buf, buf.length);
                server.receive(p);
                System.out.println("UDP  got  " + new String(p.getData(), 0, p.getLength(), StandardCharsets.UTF_8) + " (no handshake, no ack)");
            }
        }
    }
}
''', ["Simulate packet loss on UDP: randomly skip 1 of every 3 sends and make the receiver report gaps using sequence numbers in the payload.",
      "Add a simple ACK + resend to your UDP protocol (that's what QUIC/TCP do).",
      "Measure the time to open 100 TCP connections vs sending 100 UDP datagrams."])

J("http", r'''
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
''', ["Add POST /items that creates an item with a server-generated id and returns 201 plus a `Location` header.",
      "Return 429 with `Retry-After: 1` when a client sends more than 5 requests per second.",
      "Add `Cache-Control: max-age=60` and make the client skip the request entirely while its copy is fresh."])

J("tls", r'''
import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.security.spec.*;
import java.util.*;

public class TlsHandshakeDemo {
    // The heart of TLS 1.3: ephemeral key exchange (ECDH) -> shared secret -> symmetric AES-GCM, server signs to prove identity.
    public static void main(String[] args) throws Exception {
        KeyPairGenerator ec = KeyPairGenerator.getInstance("EC"); ec.initialize(new ECGenParameterSpec("secp256r1"));
        KeyPair serverIdentity = ec.generateKeyPair();                  // long-term key (its public key is in the certificate)
        KeyPair clientEph = ec.generateKeyPair(), serverEph = ec.generateKeyPair();
        // ServerHello: server signs its ephemeral public key with its identity key
        Signature signer = Signature.getInstance("SHA256withECDSA"); signer.initSign(serverIdentity.getPrivate());
        signer.update(serverEph.getPublic().getEncoded()); byte[] sig = signer.sign();
        Signature verifier = Signature.getInstance("SHA256withECDSA"); verifier.initVerify(serverIdentity.getPublic());
        verifier.update(serverEph.getPublic().getEncoded());
        System.out.println("1. client verifies server signature (certificate key): " + verifier.verify(sig));
        byte[] clientSecret = agree(clientEph.getPrivate(), serverEph.getPublic());
        byte[] serverSecret = agree(serverEph.getPrivate(), clientEph.getPublic());
        System.out.println("2. both sides derived the same secret without sending it: " + Arrays.equals(clientSecret, serverSecret));
        SecretKey key = new SecretKeySpec(MessageDigest.getInstance("SHA-256").digest(clientSecret), 0, 16, "AES");
        byte[] iv = new byte[12]; new SecureRandom().nextBytes(iv);
        Cipher enc = Cipher.getInstance("AES/GCM/NoPadding"); enc.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
        byte[] ct = enc.doFinal("GET /account HTTP/1.1".getBytes());
        System.out.println("3. on the wire: " + ct.length + " encrypted bytes (unreadable)");
        Cipher dec = Cipher.getInstance("AES/GCM/NoPadding"); dec.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(128, iv));
        System.out.println("4. server decrypts: " + new String(dec.doFinal(ct)));
        ct[3] ^= 1;                                                       // attacker flips a bit
        try { dec.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(128, iv)); dec.doFinal(ct); }
        catch (AEADBadTagException e) { System.out.println("5. tampered message rejected: integrity check failed"); }
    }

    static byte[] agree(PrivateKey mine, PublicKey theirs) throws Exception {
        KeyAgreement ka = KeyAgreement.getInstance("ECDH"); ka.init(mine); ka.doPhase(theirs, true); return ka.generateSecret();
    }
}
''', ["Simulate a man-in-the-middle: replace `serverEph` with an attacker's key and show the signature check fails.",
      "Use separate keys for client->server and server->client by hashing the secret with different labels.",
      "Encrypt 3 messages with the same key but a counter-based IV, and explain why reusing an IV is dangerous."])

J("rest", r'''
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
''', ["Add `DELETE /v1/orders/{id}` returning 204, and 404 when it doesn't exist.",
      "Return errors as JSON `{code, message}` consistently and add 400 for a missing `Idempotency-Key`.",
      "Add filtering `?status=PAID` that works together with cursor pagination."])

J("rpc-grpc", r'''
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

public class RpcDemo {
    // A tiny RPC framework: the client calls an interface; a proxy serialises the call into bytes ("the wire"),
    // the server decodes it and invokes the real implementation. gRPC does the same with protobuf + HTTP/2.
    interface OrderService { String getOrder(String id); int total(int[] prices); }

    static class OrderServiceImpl implements OrderService {
        public String getOrder(String id) { return "Order{id=" + id + ", status=PAID}"; }
        public int total(int[] prices) { return Arrays.stream(prices).sum(); }
    }

    record Call(String method, Object[] args) implements Serializable {}

    static byte[] serverHandle(byte[] request, Object impl) throws Exception {
        Call call = (Call) new ObjectInputStream(new ByteArrayInputStream(request)).readObject();
        Method m = Arrays.stream(impl.getClass().getMethods()).filter(x -> x.getName().equals(call.method())).findFirst().orElseThrow();
        Object result = m.invoke(impl, call.args());
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        new ObjectOutputStream(bos).writeObject(result);
        return bos.toByteArray();
    }

    @SuppressWarnings("unchecked")
    static <T> T stub(Class<T> api, Object remoteImpl) {
        return (T) Proxy.newProxyInstance(api.getClassLoader(), new Class<?>[]{api}, (proxy, method, args) -> {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            new ObjectOutputStream(bos).writeObject(new Call(method.getName(), args));
            byte[] wire = bos.toByteArray();
            System.out.println("  [wire] " + method.getName() + " request " + wire.length + " bytes");
            byte[] reply = serverHandle(wire, remoteImpl);               // in real life: an HTTP/2 network call
            return new ObjectInputStream(new ByteArrayInputStream(reply)).readObject();
        });
    }

    public static void main(String[] args) {
        OrderService client = stub(OrderService.class, new OrderServiceImpl());
        System.out.println("getOrder -> " + client.getOrder("987"));
        System.out.println("total    -> " + client.total(new int[]{2499, 199, 199}));
        System.out.println("The caller wrote client.getOrder(...) like a local call; the stub hid the network.");
    }
}
''', ["Add a deadline: if `serverHandle` takes longer than 100 ms (add a sleep), throw a timeout in the stub.",
      "Replace Java serialisation with a compact hand-written format (method name + length-prefixed args) and compare byte sizes.",
      "Add a 'server streaming' method that returns a list of order events one at a time via a callback."])

J("graphql", r'''
import java.util.*;
import java.util.function.*;

public class GraphQlDemo {
    // A mini GraphQL-style executor: the client lists the fields it wants; resolvers fetch only those.
    record User(String id, String name, String city) {}
    record Post(String id, String authorId, String title, int likes) {}
    static final Map<String, User> users = Map.of("42", new User("42", "Asha", "Pune"), "7", new User("7", "Ravi", "Delhi"));
    static final List<Post> posts = List.of(new Post("p1", "42", "Hello", 10), new Post("p2", "42", "System design", 99), new Post("p3", "7", "Java", 5));
    static int dbCalls = 0;

    static Map<String, Object> user(String id, List<String> fields, Map<String, List<String>> nested) {
        dbCalls++; User u = users.get(id);
        Map<String, Object> out = new LinkedHashMap<>();
        for (String f : fields) switch (f) {
            case "name" -> out.put("name", u.name());
            case "city" -> out.put("city", u.city());
            case "posts" -> { dbCalls++; out.put("posts", posts.stream().filter(p -> p.authorId().equals(id)).map(p -> pick(p, nested.get("posts"))).toList()); }
        }
        return out;
    }

    static Map<String, Object> pick(Post p, List<String> fields) {
        Map<String, Object> m = new LinkedHashMap<>();
        for (String f : fields) m.put(f, f.equals("title") ? p.title() : f.equals("likes") ? p.likes() : p.id());
        return m;
    }

    public static void main(String[] args) {
        System.out.println("query { user(id:42) { name } }");
        System.out.println("  -> " + user("42", List.of("name"), Map.of()) + "   db calls: " + dbCalls);
        dbCalls = 0;
        System.out.println("query { user(id:42) { name city posts { title likes } } }");
        System.out.println("  -> " + user("42", List.of("name", "city", "posts"), Map.of("posts", List.of("title", "likes"))) + "   db calls: " + dbCalls);
        System.out.println("One request, exactly the fields asked for: no over-fetching, no second round trip.");
    }
}
''', ["Add a `posts { author { name } }` field and count DB calls: you'll hit the N+1 problem.",
      "Fix N+1 with a DataLoader: collect all author ids first, load them in one batch call.",
      "Reject queries nested deeper than 3 levels (query depth limiting)."])

J("realtime-comm", r'''
import java.util.*;
import java.util.concurrent.*;

public class RealtimeDemo {
    // Compares short polling, long polling and push (WebSocket/SSE style) for the same 3 messages.
    static final BlockingQueue<String> inbox = new LinkedBlockingQueue<>();
    static final List<Long> arrivalMs = List.of(120L, 450L, 460L);

    public static void main(String[] args) throws Exception {
        // Short polling every 200 ms: requests are made even when nothing is new
        int requests = 0; List<String> log = new ArrayList<>();
        for (long t = 0; t <= 600; t += 200) {
            requests++;
            for (long a : arrivalMs) if (a > t - 200 && a <= t) log.add("msg@" + a + " seen@" + t + " (late " + (t - a) + " ms)");
        }
        System.out.println("short polling: " + requests + " requests -> " + log);
        // Long polling: server holds the request until a message arrives (real threads + queue)
        ExecutorService server = Executors.newSingleThreadExecutor();
        long start = System.currentTimeMillis();
        server.submit(() -> { for (long a : arrivalMs) { sleepUntil(start + a); inbox.add("msg@" + a); } });
        List<String> got = new ArrayList<>(); int longPolls = 0;
        while (got.size() < 3) {
            longPolls++;
            String m = inbox.poll(2, TimeUnit.SECONDS);                  // held open until data or timeout
            if (m != null) { got.add(m); inbox.drainTo(got); }
        }
        server.shutdown();
        System.out.println("long polling : " + longPolls + " requests -> " + got + " (each delivered as soon as it arrived)");
        // Push: one open connection, server calls the client callback
        List<String> pushed = new ArrayList<>();
        java.util.function.Consumer<String> socket = pushed::add;
        for (long a : arrivalMs) socket.accept("msg@" + a);
        System.out.println("push (WS/SSE): 1 connection -> " + pushed);
    }

    static void sleepUntil(long t) { try { Thread.sleep(Math.max(0, t - System.currentTimeMillis())); } catch (InterruptedException ignored) {} }
}
''', ["Change the short-poll interval to 50 ms and 1 s: plot requests vs average lateness.",
      "Add a heartbeat to the push channel and detect a dead connection after 3 missed heartbeats.",
      "Build a tiny SSE endpoint with `com.sun.net.httpserver` that writes `data: ...\\n\\n` lines and read it with `HttpClient`."])

J("api-gateway", r'''
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
''', ["Add a response cache in the gateway for `GET /users/*` with a 30 s TTL.",
      "Add a timeout + fallback: if the order service throws, return 503 with a friendly message.",
      "Add request aggregation: `/home` calls both services and merges the results (a mini BFF)."])

J("proxies", r'''
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
''', ["Add health checks to the reverse proxy: skip a backend that throws, and retry on the next.",
      "Add gzip compression in the reverse proxy using `GZIPOutputStream` and print the size saving.",
      "Add an access log to the forward proxy (who visited which host, when)."])

J("rate-limiting", r'''
import java.util.*;

public class RateLimiterAlgorithmsDemo {
    interface Limiter { boolean allow(long nowMs); }

    static class TokenBucket implements Limiter {
        final double capacity, refillPerMs; double tokens; long last;
        TokenBucket(int capacity, int perSecond) { this.capacity = capacity; this.refillPerMs = perSecond / 1000.0; this.tokens = capacity; }
        public boolean allow(long now) {
            tokens = Math.min(capacity, tokens + (now - last) * refillPerMs); last = now;
            if (tokens >= 1) { tokens -= 1; return true; } return false;
        }
    }

    static class FixedWindow implements Limiter {
        final int limit; final long window; long windowStart = -1; int count;
        FixedWindow(int limit, long windowMs) { this.limit = limit; this.window = windowMs; }
        public boolean allow(long now) {
            long w = now / window * window;
            if (w != windowStart) { windowStart = w; count = 0; }
            return ++count <= limit;
        }
    }

    static class SlidingLog implements Limiter {
        final int limit; final long window; final Deque<Long> log = new ArrayDeque<>();
        SlidingLog(int limit, long windowMs) { this.limit = limit; this.window = windowMs; }
        public boolean allow(long now) {
            while (!log.isEmpty() && log.peekFirst() <= now - window) log.pollFirst();
            if (log.size() < limit) { log.addLast(now); return true; } return false;
        }
    }

    public static void main(String[] args) {
        // Burst at the edge of two windows: 5 requests at t=900..940 ms and 5 at t=1000..1040 ms; limit 5 per second
        long[] times = {900, 910, 920, 930, 940, 1000, 1010, 1020, 1030, 1040};
        Map<String, Limiter> ls = new LinkedHashMap<>();
        ls.put("fixed window ", new FixedWindow(5, 1000));
        ls.put("sliding log  ", new SlidingLog(5, 1000));
        ls.put("token bucket ", new TokenBucket(5, 5));
        for (var e : ls.entrySet()) {
            StringBuilder sb = new StringBuilder(); int ok = 0;
            for (long t : times) { boolean a = e.getValue().allow(t); sb.append(a ? '✔' : '✘'); if (a) ok++; }
            System.out.println(e.getKey() + sb + "  allowed " + ok + " of 10 within 140 ms");
        }
        System.out.println("Fixed window lets 10 through around the boundary; sliding log and token bucket hold the limit.");
    }
}
''', ["Implement the sliding-window counter (previous window count × overlap + current count) and add it to the comparison.",
      "Make the token bucket per user: `Map<String, TokenBucket>` and give premium users capacity 20.",
      "Make `TokenBucket.allow` thread-safe and hammer it from 8 threads to check it never allows more than capacity."])
