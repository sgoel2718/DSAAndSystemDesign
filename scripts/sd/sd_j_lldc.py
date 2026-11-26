"""Java practice programs: LLD & OOP concept tab."""
from sd_j_util import J

J("oop-pillars", r'''
import java.util.*;

public class OopPillarsDemo {
    // Abstraction: callers depend on what a Payment does, not how.
    interface Payment { String pay(long paise); }

    // Encapsulation: balance can't be changed from outside except through validated methods.
    static class Wallet {
        private long balancePaise;
        Wallet(long initial) { balancePaise = initial; }
        long balance() { return balancePaise; }
        void debit(long p) { if (p <= 0 || p > balancePaise) throw new IllegalArgumentException("invalid debit " + p); balancePaise -= p; }
    }

    // Inheritance: shared behaviour in a base class.
    static abstract class CardPayment implements Payment {
        protected final String last4;
        CardPayment(String last4) { this.last4 = last4; }
        protected String mask() { return "**** " + last4; }
    }
    static class CreditCard extends CardPayment { CreditCard(String l) { super(l); } public String pay(long p) { return "credit card " + mask() + " charged Rs " + p / 100; } }
    static class DebitCard extends CardPayment { DebitCard(String l) { super(l); } public String pay(long p) { return "debit card " + mask() + " charged Rs " + p / 100 + " (PIN verified)"; } }
    static class WalletPayment implements Payment {
        private final Wallet w; WalletPayment(Wallet w) { this.w = w; }
        public String pay(long p) { w.debit(p); return "wallet debited Rs " + p / 100 + ", left Rs " + w.balance() / 100; }
    }

    public static void main(String[] args) {
        Wallet w = new Wallet(1_00_000);
        List<Payment> methods = List.of(new CreditCard("4242"), new DebitCard("1881"), new WalletPayment(w));
        for (Payment p : methods) System.out.println(p.pay(49_900));                 // Polymorphism: one call, many behaviours
        try { new WalletPayment(w).pay(10_00_000); } catch (IllegalArgumentException e) { System.out.println("encapsulation guard: " + e.getMessage()); }
    }
}
''', ["Add a `UpiPayment` class without changing any existing class (that's the Open/Closed principle).",
      "Make `CardPayment` add a 2% fee for credit cards only, using an overridden `fee()` method.",
      "Replace inheritance with composition: a `Card` class that holds a `CardType` enum. Which feels simpler?"])

J("solid", r'''
import java.util.*;

public class SolidDemo {
    // S: each class has one reason to change. O: add new discount types without editing old code.
    // L: any Discount can replace another. I: small interfaces. D: high-level code depends on abstractions.
    interface Discount { long apply(long totalPaise); default String name() { return "custom rule"; } }
    record PercentOff(int pct) implements Discount { public long apply(long t) { return t - t * pct / 100; } public String name() { return pct + "% off"; } }
    record FlatOff(long paise) implements Discount { public long apply(long t) { return Math.max(0, t - paise); } public String name() { return "Rs " + paise / 100 + " off"; } }

    interface OrderRepository { void save(String order); }                 // D: abstraction the service depends on
    interface Notifier { void send(String msg); }                          // I: tiny interface, not a giant 'Utils'

    static class InMemoryRepo implements OrderRepository { final List<String> rows = new ArrayList<>(); public void save(String o) { rows.add(o); } }
    static class ConsoleNotifier implements Notifier { public void send(String m) { System.out.println("  notify: " + m); } }

    static class CheckoutService {                                          // S: only orchestrates checkout
        private final OrderRepository repo; private final Notifier notifier;
        CheckoutService(OrderRepository r, Notifier n) { repo = r; notifier = n; }
        long checkout(String user, long total, Discount d) {
            long finalPrice = d.apply(total);
            repo.save(user + ":" + finalPrice);
            notifier.send(user + " paid Rs " + finalPrice / 100 + " (" + d.name() + ")");
            return finalPrice;
        }
    }

    public static void main(String[] args) {
        InMemoryRepo repo = new InMemoryRepo();
        CheckoutService svc = new CheckoutService(repo, new ConsoleNotifier());   // dependencies injected
        svc.checkout("asha", 2_499_00, new PercentOff(10));
        svc.checkout("ravi", 2_499_00, new FlatOff(500_00));
        Discount buyMore = t -> t >= 2_000_00 ? t - 300_00 : t;                   // O: a new rule, zero edits elsewhere
        System.out.println("  lambda discount works too: Rs " + buyMore.apply(2_499_00) / 100);
        System.out.println("saved orders: " + repo.rows);
    }
}
''', ["Write a test-style `main` that injects a fake `Notifier` collecting messages in a list, and assert what was sent.",
      "Add a `MaxDiscountCap` decorator that wraps any `Discount` and limits it to Rs 1,000 (still Liskov-safe).",
      "Find a SOLID violation: put email sending inside `CheckoutService` and list what becomes hard to change or test."])

J("uml", r'''
import java.util.*;

public class UmlRelationshipsDemo {
    // Each relationship from a UML class diagram, as Java code.
    interface Payable { long amount(); }                                   // realisation (implements)  ..|>
    static abstract class Vehicle { abstract int wheels(); }               // generalisation (extends)  --|>
    static class Car extends Vehicle { int wheels() { return 4; } }

    static class Engine { final int cc; Engine(int cc) { this.cc = cc; } }
    static class Bus extends Vehicle {
        private final Engine engine = new Engine(5000);                    // composition *-- : created and owned, dies with Bus
        private final List<Passenger> passengers = new ArrayList<>();      // aggregation o-- : passengers exist on their own
        int wheels() { return 6; }
        void board(Passenger p) { passengers.add(p); }
        Ticket sell(Passenger p, PricingService pricing) { return new Ticket(p, pricing.price(p)); }   // dependency ..> : used, not stored
    }
    record Passenger(String name, int age) {}
    record Ticket(Passenger passenger, long amount) implements Payable {}   // association --> : Ticket knows its Passenger
    static class PricingService { long price(Passenger p) { return p.age() < 12 ? 50 : 100; } }

    public static void main(String[] args) {
        Bus bus = new Bus(); Passenger asha = new Passenger("Asha", 30), kid = new Passenger("Kiran", 8);
        bus.board(asha); bus.board(kid);
        PricingService pricing = new PricingService();
        List<Payable> bills = List.of(bus.sell(asha, pricing), bus.sell(kid, pricing));
        System.out.println("Bus is-a Vehicle with " + bus.wheels() + " wheels, has-a Engine " + bus.engine.cc + "cc (composition)");
        System.out.println("Bus aggregates passengers " + bus.passengers.stream().map(Passenger::name).toList());
        bills.forEach(b -> System.out.println("Ticket (Payable) " + b + " -> Rs " + b.amount()));
        bus = null;
        System.out.println("bus discarded: its Engine is gone too, but " + asha.name() + " still exists (aggregation)");
    }
}
''', ["Draw the UML class diagram for this code by hand, using the correct arrow for each relationship.",
      "Add a `Driver` with a 1-to-1 association to `Bus`, and a `Depot` that aggregates many buses.",
      "Write a sequence diagram (as println steps) for `bus.sell(asha, pricing)`."])

J("creational-patterns", r'''
import java.util.*;

public class CreationalPatternsDemo {
    // Singleton (enum = thread-safe, serialisation-safe)
    enum Config { INSTANCE; final Map<String, String> values = new HashMap<>(Map.of("currency", "INR")); }

    // Factory method: callers ask for a type by name, never call 'new' on concrete classes
    interface Notification { String send(String to, String msg); }
    static class Email implements Notification { public String send(String to, String m) { return "email to " + to + ": " + m; } }
    static class Sms implements Notification { public String send(String to, String m) { return "sms to " + to + ": " + m; } }
    static Notification notificationFor(String channel) {
        return switch (channel) { case "email" -> new Email(); case "sms" -> new Sms(); default -> throw new IllegalArgumentException(channel); };
    }

    // Builder: many optional fields, readable construction, immutable result
    static final class Pizza {
        final String size; final List<String> toppings; final boolean extraCheese;
        private Pizza(Builder b) { size = b.size; toppings = List.copyOf(b.toppings); extraCheese = b.extraCheese; }
        static Builder builder(String size) { return new Builder(size); }
        static final class Builder {
            private final String size; private final List<String> toppings = new ArrayList<>(); private boolean extraCheese;
            Builder(String size) { this.size = size; }
            Builder topping(String t) { toppings.add(t); return this; }
            Builder extraCheese() { extraCheese = true; return this; }
            Pizza build() { if (toppings.size() > 5) throw new IllegalStateException("too many toppings"); return new Pizza(this); }
        }
        public String toString() { return size + " pizza " + toppings + (extraCheese ? " + extra cheese" : ""); }
    }

    // Prototype: copy a configured object instead of rebuilding it
    record Document(String template, Map<String, String> fields) { Document copyWith(String k, String v) { Map<String, String> f = new HashMap<>(fields); f.put(k, v); return new Document(template, f); } }

    public static void main(String[] args) {
        System.out.println("singleton same object? " + (Config.INSTANCE == Config.valueOf("INSTANCE")) + ", currency=" + Config.INSTANCE.values.get("currency"));
        for (String ch : List.of("email", "sms")) System.out.println("factory: " + notificationFor(ch).send("asha", "order shipped"));
        System.out.println("builder: " + Pizza.builder("large").topping("paneer").topping("onion").extraCheese().build());
        Document invoice = new Document("invoice-v2", Map.of("company", "ShopCo", "gst", "29ABCDE"));
        System.out.println("prototype: " + new TreeMap<>(invoice.copyWith("customer", "Ravi").fields()));
    }
}
''', ["Add an Abstract Factory that creates a matching `Button` and `Checkbox` for 'light' and 'dark' themes.",
      "Write a lazy, thread-safe singleton with double-checked locking and explain why `volatile` is needed.",
      "Add validation to the builder: 'small' pizzas allow at most 2 toppings."])

J("structural-patterns", r'''
import java.util.*;

public class StructuralPatternsDemo {
    interface PaymentGateway { boolean charge(String user, long paise); }

    // Adapter: a third-party SDK with a different interface, wrapped to fit ours
    static class LegacyPayU { int makePayment(double rupees, String customerId) { return rupees < 100_000 ? 200 : 402; } }
    static class PayUAdapter implements PaymentGateway {
        private final LegacyPayU sdk = new LegacyPayU();
        public boolean charge(String u, long p) { return sdk.makePayment(p / 100.0, u) == 200; }
    }

    // Decorator: add logging and retries without changing the gateway
    static class LoggingGateway implements PaymentGateway {
        private final PaymentGateway inner; LoggingGateway(PaymentGateway i) { inner = i; }
        public boolean charge(String u, long p) { boolean ok = inner.charge(u, p); System.out.println("  [log] charge " + u + " Rs " + p / 100 + " -> " + ok); return ok; }
    }

    // Proxy: controls access (here a cache in front of a slow service)
    interface ExchangeRates { double usdToInr(); }
    static class SlowRatesApi implements ExchangeRates { int calls; public double usdToInr() { calls++; return 83.2; } }
    static class CachingRatesProxy implements ExchangeRates {
        private final SlowRatesApi real; private Double cached; CachingRatesProxy(SlowRatesApi r) { real = r; }
        public double usdToInr() { if (cached == null) cached = real.usdToInr(); return cached; }
    }

    // Facade: one simple method over many subsystems
    static class CheckoutFacade {
        private final PaymentGateway pay = new LoggingGateway(new PayUAdapter());
        String placeOrder(String user, long paise) {
            boolean reserved = true;                                             // inventory subsystem
            boolean paid = reserved && pay.charge(user, paise);                  // payment subsystem
            return paid ? "order confirmed, invoice emailed" : "payment failed, stock released";
        }
    }

    // Composite: treat a single item and a bundle the same way
    interface CartItem { long price(); }
    record Product(String name, long price) implements CartItem {}
    record Bundle(String name, List<CartItem> items, int discountPct) implements CartItem {
        public long price() { return items.stream().mapToLong(CartItem::price).sum() * (100 - discountPct) / 100; }
    }

    public static void main(String[] args) {
        CheckoutFacade shop = new CheckoutFacade();
        System.out.println("facade: " + shop.placeOrder("asha", 2_499_00));
        System.out.println("facade: " + shop.placeOrder("ravi", 2_00_000_00));
        SlowRatesApi api = new SlowRatesApi(); ExchangeRates rates = new CachingRatesProxy(api);
        for (int i = 0; i < 3; i++) rates.usdToInr();
        System.out.println("proxy: 3 lookups, real API called " + api.calls + " time");
        CartItem combo = new Bundle("cricket kit", List.of(new Product("bat", 3000), new Product("ball", 500), new Bundle("pads+gloves", List.of(new Product("pads", 1500), new Product("gloves", 800)), 10)), 5);
        System.out.println("composite: bundle price Rs " + combo.price());
    }
}
''', ["Add a `RetryingGateway` decorator and stack it: `new LoggingGateway(new RetryingGateway(new PayUAdapter()))`.",
      "Add a TTL to the caching proxy so the rate refreshes every 60 'seconds'.",
      "Add a Bridge: `Shape` × `Renderer` (SVG, ASCII) without creating a class per combination."])

J("behavioral-patterns", r'''
import java.util.*;
import java.util.function.*;

public class BehavioralPatternsDemo {
    // Strategy: swap the algorithm at runtime
    interface FareStrategy { double fare(double km); }
    static final Map<String, FareStrategy> fares = Map.of("normal", km -> 30 + 12 * km, "surge", km -> (30 + 12 * km) * 1.8, "pool", km -> 20 + 8 * km);

    // Observer: subscribers are notified of changes
    static class OrderStatus {
        private final List<Consumer<String>> observers = new ArrayList<>(); private String status = "CREATED";
        void subscribe(Consumer<String> o) { observers.add(o); }
        void set(String s) { status = s; observers.forEach(o -> o.accept(s)); }
    }

    // State: behaviour depends on the current state object
    interface DoorState { DoorState press(StringBuilder log); }
    static final DoorState OPEN = new DoorState() { public DoorState press(StringBuilder l) { l.append("closing -> "); return CLOSED(); } };
    static DoorState CLOSED() { return log -> { log.append("opening -> "); return OPEN; }; }

    // Command: actions as objects, so they can be queued and undone
    interface Command { void run(); void undo(); }
    static final StringBuilder doc = new StringBuilder();
    static Command type(String s) { return new Command() { public void run() { doc.append(s); } public void undo() { doc.setLength(doc.length() - s.length()); } }; }

    // Chain of responsibility: each handler passes the request on or stops it
    static Function<Map<String, Object>, String> chain = req -> {
        List<Function<Map<String, Object>, String>> handlers = List.of(
            r -> r.get("token") == null ? "401 by auth handler" : null,
            r -> (int) r.get("calls") > 100 ? "429 by rate-limit handler" : null,
            r -> "200 handled by controller");
        for (var h : handlers) { String res = h.apply(req); if (res != null) return res; }
        return "unreachable";
    };

    public static void main(String[] args) {
        new TreeMap<>(fares).forEach((k, s) -> System.out.printf("strategy %-6s 10 km -> Rs %.0f%n", k, s.fare(10)));
        OrderStatus o = new OrderStatus();
        o.subscribe(s -> System.out.println("observer email: order is " + s)); o.subscribe(s -> System.out.println("observer app push: " + s));
        o.set("SHIPPED");
        StringBuilder log = new StringBuilder(); DoorState d = CLOSED(); for (int i = 0; i < 3; i++) d = d.press(log);
        System.out.println("state: " + log + "done");
        Deque<Command> history = new ArrayDeque<>();
        for (String w : List.of("Hello", " world", "!!")) { Command c = type(w); c.run(); history.push(c); }
        System.out.println("command: '" + doc + "'"); history.pop().undo(); System.out.println("after undo: '" + doc + "'");
        System.out.println("chain: " + chain.apply(Map.of("calls", 5)) + " | " + chain.apply(Map.of("token", "t", "calls", 500)) + " | " + chain.apply(Map.of("token", "t", "calls", 5)));
    }
}
''', ["Add a Template Method: an abstract `DataExporter` with fixed steps (read, transform, write) and CSV/JSON subclasses.",
      "Add redo to the Command example with a second stack.",
      "Implement an Iterator over a binary tree (in-order) using an explicit stack."])

J("concurrency-java", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.concurrent.locks.*;

public class ConcurrencyDemo {
    static int unsafeCounter = 0;

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        // 1. Race condition vs AtomicInteger
        AtomicInteger safe = new AtomicInteger(); List<Future<?>> fs = new ArrayList<>();
        for (int t = 0; t < 4; t++) fs.add(pool.submit(() -> { for (int i = 0; i < 100_000; i++) { unsafeCounter++; safe.incrementAndGet(); } }));
        for (Future<?> f : fs) f.get();
        System.out.println("1. 4 threads x 100,000 increments: int++ = " + (unsafeCounter == 400_000 ? "400000 (got lucky)" : unsafeCounter + " (lost updates)") + ", AtomicInteger = " + safe.get());
        // 2. ReentrantLock protecting a check-then-act on a seat map
        Map<String, String> seats = new HashMap<>(); ReentrantLock lock = new ReentrantLock(); AtomicInteger booked = new AtomicInteger();
        fs.clear();
        for (int t = 0; t < 8; t++) { final String user = "u" + t; fs.add(pool.submit(() -> { lock.lock(); try { if (!seats.containsKey("A1")) { seats.put("A1", user); booked.incrementAndGet(); } } finally { lock.unlock(); } })); }
        for (Future<?> f : fs) f.get();
        System.out.println("2. 8 users race for seat A1 -> bookings made: " + booked.get());
        // 3. Producer-consumer with a BlockingQueue
        BlockingQueue<Integer> q = new ArrayBlockingQueue<>(5); AtomicInteger sum = new AtomicInteger();
        Future<?> consumer = pool.submit(() -> { for (int i = 0; i < 20; i++) sum.addAndGet(q.take()); return null; });
        for (int i = 1; i <= 20; i++) q.put(i);
        consumer.get();
        System.out.println("3. producer -> bounded queue(5) -> consumer: sum 1..20 = " + sum.get());
        // 4. CompletableFuture: run two calls in parallel and combine
        CompletableFuture<String> price = CompletableFuture.supplyAsync(() -> { sleep(50); return "Rs 2499"; }, pool);
        CompletableFuture<String> stock = CompletableFuture.supplyAsync(() -> { sleep(50); return "in stock"; }, pool);
        long t0 = System.nanoTime(); String page = price.thenCombine(stock, (p, s) -> p + ", " + s).get();
        System.out.println("4. CompletableFuture combine: '" + page + "' in ~" + Math.round((System.nanoTime() - t0) / 1e7) * 10 + " ms (parallel, not 100)");
        // 5. CountDownLatch: wait for all workers
        CountDownLatch done = new CountDownLatch(3);
        for (int i = 0; i < 3; i++) pool.submit(() -> { sleep(10); done.countDown(); });
        System.out.println("5. latch: all 3 workers finished = " + done.await(1, TimeUnit.SECONDS));
        // 6. ConcurrentHashMap.merge for safe aggregation
        ConcurrentHashMap<String, Integer> wordCount = new ConcurrentHashMap<>(); fs.clear();
        for (int t = 0; t < 4; t++) fs.add(pool.submit(() -> { for (String w : "to be or not to be".split(" ")) wordCount.merge(w, 1, Integer::sum); }));
        for (Future<?> f : fs) f.get();
        System.out.println("6. ConcurrentHashMap word count from 4 threads: " + new TreeMap<>(wordCount));
        pool.shutdown();
    }
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } }
}
''', ["Create a deadlock with two locks acquired in opposite orders, then fix it by always locking in the same order.",
      "Replace the `ReentrantLock` with a `ReadWriteLock` for a cache that is read 100× more than written.",
      "Use virtual threads (`Executors.newVirtualThreadPerTaskExecutor()`) to run 10,000 sleeping tasks and time it."])

J("lld-approach", r'''
import java.util.*;

public class LldApproachDemo {
    // The interview approach in code, for a small "library checkout":
    // 1 requirements -> 2 entities -> 3 relationships -> 4 interfaces/patterns -> 5 core flow -> 6 edge cases
    enum CopyStatus { AVAILABLE, BORROWED }
    record Book(String isbn, String title) {}
    static final class Copy { final String id; final Book book; CopyStatus status = CopyStatus.AVAILABLE; Copy(String id, Book b) { this.id = id; book = b; } }
    record Member(String id, String name, int maxLoans) {}
    record Loan(Copy copy, Member member, int dueDay) {}
    interface FinePolicy { int fine(int daysLate); }                       // strategy: rules can change

    static final class Library {
        private final Map<String, List<Copy>> copiesByIsbn = new HashMap<>(); private final List<Loan> loans = new ArrayList<>(); private final FinePolicy fines;
        Library(FinePolicy f) { fines = f; }
        void addCopy(Copy c) { copiesByIsbn.computeIfAbsent(c.book.isbn(), k -> new ArrayList<>()).add(c); }
        Loan borrow(Member m, String isbn, int today) {
            if (loans.stream().filter(l -> l.member().equals(m)).count() >= m.maxLoans()) throw new IllegalStateException(m.name() + " has reached the loan limit");
            Copy c = copiesByIsbn.getOrDefault(isbn, List.of()).stream().filter(x -> x.status == CopyStatus.AVAILABLE).findFirst()
                .orElseThrow(() -> new IllegalStateException("no copy of " + isbn + " available"));
            c.status = CopyStatus.BORROWED; Loan l = new Loan(c, m, today + 14); loans.add(l); return l;
        }
        int giveBack(Loan l, int today) { loans.remove(l); l.copy().status = CopyStatus.AVAILABLE; return fines.fine(Math.max(0, today - l.dueDay())); }
    }

    public static void main(String[] args) {
        Book ddia = new Book("978-1449373320", "Designing Data-Intensive Applications");
        Library lib = new Library(days -> days * 5);
        lib.addCopy(new Copy("c1", ddia)); lib.addCopy(new Copy("c2", ddia));
        Member asha = new Member("m1", "Asha", 1), ravi = new Member("m2", "Ravi", 3), zoya = new Member("m3", "Zoya", 2);
        Loan a = lib.borrow(asha, ddia.isbn(), 1); System.out.println("Asha borrowed " + a.copy().id + ", due day " + a.dueDay());
        Loan r = lib.borrow(ravi, ddia.isbn(), 2); System.out.println("Ravi borrowed " + r.copy().id);
        for (Runnable edge : List.<Runnable>of(() -> lib.borrow(zoya, ddia.isbn(), 3), () -> lib.borrow(asha, ddia.isbn(), 3)))
            try { edge.run(); } catch (IllegalStateException e) { System.out.println("edge case handled: " + e.getMessage()); }
        System.out.println("Asha returns on day 20 -> fine Rs " + lib.giveBack(a, 20));
        System.out.println("Zoya now borrows " + lib.borrow(zoya, ddia.isbn(), 21).copy().id);
    }
}
''', ["Add reservations: when no copy is free, queue the member and assign the next returned copy to them.",
      "Make `borrow` thread-safe and run 10 members borrowing 2 copies concurrently.",
      "Before coding, write the 6 steps (requirements, entities, ...) for a 'Parking lot' in comments, then compare with the LLD tab's solution."])

J("api-contract-lld", r'''
import java.util.*;

public class ApiContractDemo {
    // A clean service contract: typed requests/responses, explicit errors, validation, and idempotency.
    record CreateBookingRequest(String userId, String showId, List<String> seats, String idempotencyKey) {}
    record Booking(String id, String userId, String showId, List<String> seats, long amountPaise, String status) {}
    sealed interface Result<T> permits Ok, Err {}
    record Ok<T>(T value) implements Result<T> {}
    record Err<T>(String code, String message) implements Result<T> {}

    interface BookingService {
        Result<Booking> create(CreateBookingRequest req);
        Result<Booking> get(String bookingId);
    }

    static final class InMemoryBookingService implements BookingService {
        private final Map<String, Booking> byId = new HashMap<>(); private final Map<String, String> byKey = new HashMap<>(); private final Set<String> taken = new HashSet<>(); private int seq;
        public Result<Booking> create(CreateBookingRequest r) {
            if (r.seats() == null || r.seats().isEmpty() || r.seats().size() > 6) return new Err<>("INVALID_ARGUMENT", "1 to 6 seats required");
            if (byKey.containsKey(r.idempotencyKey())) return new Ok<>(byId.get(byKey.get(r.idempotencyKey())));
            for (String s : r.seats()) if (taken.contains(r.showId() + ":" + s)) return new Err<>("SEAT_UNAVAILABLE", "seat " + s + " already booked");
            r.seats().forEach(s -> taken.add(r.showId() + ":" + s));
            Booking b = new Booking("bk-" + (++seq), r.userId(), r.showId(), List.copyOf(r.seats()), r.seats().size() * 250_00L, "CONFIRMED");
            byId.put(b.id(), b); byKey.put(r.idempotencyKey(), b.id()); return new Ok<>(b);
        }
        public Result<Booking> get(String id) { Booking b = byId.get(id); return b == null ? new Err<>("NOT_FOUND", "no booking " + id) : new Ok<>(b); }
    }

    static String show(Result<?> r) { return switch (r) { case Ok<?> ok -> "OK  " + ok.value(); case Err<?> e -> "ERR " + e.code() + ": " + e.message(); }; }

    public static void main(String[] args) {
        BookingService api = new InMemoryBookingService();
        System.out.println(show(api.create(new CreateBookingRequest("asha", "show-7", List.of("A1", "A2"), "k1"))));
        System.out.println(show(api.create(new CreateBookingRequest("asha", "show-7", List.of("A1", "A2"), "k1"))) + "  <- retry, same booking");
        System.out.println(show(api.create(new CreateBookingRequest("ravi", "show-7", List.of("A2", "A3"), "k2"))));
        System.out.println(show(api.create(new CreateBookingRequest("ravi", "show-7", List.of(), "k3"))));
        System.out.println(show(api.get("bk-1")));
        System.out.println(show(api.get("bk-9")));
    }
}
''', ["Add `cancel(bookingId, userId)` that only the owner can call and that frees the seats.",
      "Add pagination: `list(userId, pageSize, cursor)` returning a page and a next cursor.",
      "Map each error code to an HTTP status (INVALID_ARGUMENT→400, NOT_FOUND→404, SEAT_UNAVAILABLE→409) in a tiny REST layer."])
