"""Low-level design questions with complete, runnable Java code (part 2)."""
from sd_util2 import L

LLD2 = [
L("ratelimiter-lld", "Design a rate limiter (thread-safe, in-process)", "Intermediate",
  ["Google", "Amazon", "Microsoft", "Stripe", "Uber"],
  ["`allow(clientId)` returns true/false", "Configurable algorithm: token bucket or sliding window log", "Thread-safe for many concurrent callers"],
  ["RateLimiter interface", "TokenBucket (per client)", "SlidingWindowLog (per client)", "RateLimiterRegistry (ConcurrentHashMap)"],
  ["Strategy (algorithm)", "Factory (create limiter per client)", "Per-key locking"],
  r"""
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

public class RateLimiterDemo {
    interface RateLimiter { boolean tryAcquire(long nowNanos); }

    static final class TokenBucket implements RateLimiter {
        private final long capacity; private final double refillPerNano; private double tokens; private long last;
        TokenBucket(long capacity, double perSecond, long now) { this.capacity = capacity; this.refillPerNano = perSecond / 1e9; this.tokens = capacity; this.last = now; }
        public synchronized boolean tryAcquire(long now) {
            tokens = Math.min(capacity, tokens + (now - last) * refillPerNano); last = now;
            if (tokens >= 1) { tokens -= 1; return true; }
            return false;
        }
    }
    static final class SlidingWindowLog implements RateLimiter {
        private final int limit; private final long windowNanos; private final Deque<Long> log = new ArrayDeque<>();
        SlidingWindowLog(int limit, long windowNanos) { this.limit = limit; this.windowNanos = windowNanos; }
        public synchronized boolean tryAcquire(long now) {
            while (!log.isEmpty() && now - log.peekFirst() >= windowNanos) log.pollFirst();
            if (log.size() < limit) { log.addLast(now); return true; }
            return false;
        }
    }

    static final class Registry {
        private final ConcurrentHashMap<String, RateLimiter> limiters = new ConcurrentHashMap<>();
        private final Function<Long, RateLimiter> factory; private final LongSupplier clock;
        Registry(Function<Long, RateLimiter> factory, LongSupplier clock) { this.factory = factory; this.clock = clock; }
        boolean allow(String clientId) {
            long now = clock.getAsLong();
            return limiters.computeIfAbsent(clientId, k -> factory.apply(now)).tryAcquire(now);
        }
    }

    public static void main(String[] args) throws Exception {
        long[] fake = {0};                                      // controllable clock (nanoseconds)
        Registry tb = new Registry(now -> new TokenBucket(5, 2, now), () -> fake[0]);   // burst 5, 2/s
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 7; i++) sb.append(tb.allow("u1") ? 'Y' : 'n');
        fake[0] += 1_000_000_000L;                              // 1 s later: 2 new tokens
        sb.append(' ');
        for (int i = 0; i < 3; i++) sb.append(tb.allow("u1") ? 'Y' : 'n');
        System.out.println("token bucket: " + sb);              // YYYYYnn YYn

        Registry sw = new Registry(now -> new SlidingWindowLog(100, 1_000_000_000L), System::nanoTime);
        ExecutorService pool = Executors.newFixedThreadPool(8);
        List<Future<Boolean>> fs = new ArrayList<>();
        for (int i = 0; i < 1000; i++) fs.add(pool.submit(() -> sw.allow("api-key-9")));
        int ok = 0; for (Future<Boolean> f : fs) if (f.get()) ok++;
        pool.shutdown();
        System.out.println("sliding window allowed " + ok + " of 1000 concurrent calls");   // 100
    }
}
""",
  ["Distributed: store buckets in Redis with a Lua script", "Evict idle client limiters (Caffeine cache with expiry)", "Sliding window counter to save memory"]),

L("atm-lld", "Design an ATM (cash dispensing)", "Intermediate",
  ["Amazon", "Microsoft", "Goldman Sachs", "Paytm"],
  ["Insert card, enter PIN, check balance, withdraw", "Dispense using the fewest notes from available denominations", "Reject if the ATM can't make the amount or balance is insufficient"],
  ["ATM", "Card, Account (bank interface)", "CashDispenser chain: ₹2000 → ₹500 → ₹200 → ₹100", "ATMState"],
  ["Chain of Responsibility (note dispensing)", "State (idle → card inserted → authenticated)", "Interface for the bank"],
  r"""
import java.util.*;

public class AtmDemo {
    interface Bank { boolean verify(String card, String pin); long balance(String card); void debit(String card, long amount); }
    static final class InMemoryBank implements Bank {
        private final Map<String, String> pins = new HashMap<>(Map.of("4111", "1234")); private final Map<String, Long> bal = new HashMap<>(Map.of("4111", 25_000L));
        public boolean verify(String c, String p) { return p.equals(pins.get(c)); }
        public long balance(String c) { return bal.get(c); }
        public void debit(String c, long a) { if (bal.get(c) < a) throw new IllegalStateException("Insufficient balance"); bal.merge(c, -a, Long::sum); }
    }

    static abstract class NoteHandler {                        // chain of responsibility
        final int note; int count; NoteHandler next;
        NoteHandler(int note, int count) { this.note = note; this.count = count; }
        NoteHandler then(NoteHandler n) { next = n; return n; }
        boolean plan(long amount, Map<Integer, Integer> out) {
            int use = (int) Math.min(amount / note, count);
            for (int k = use; k >= 0; k--) {                   // back off if the rest can't be made
                long rest = amount - (long) k * note;
                Map<Integer, Integer> trial = new LinkedHashMap<>(out);
                if (k > 0) trial.put(note, k);
                if (rest == 0 || (next != null && next.plan(rest, trial))) { out.clear(); out.putAll(trial); return true; }
            }
            return false;
        }
        void take(Map<Integer, Integer> plan) { count -= plan.getOrDefault(note, 0); if (next != null) next.take(plan); }
    }
    static final class Notes extends NoteHandler { Notes(int n, int c) { super(n, c); } }

    enum State { IDLE, CARD_INSERTED, AUTHENTICATED }

    static final class Atm {
        private final Bank bank; private final NoteHandler chain; private State state = State.IDLE; private String card; private int pinTries;
        Atm(Bank bank, NoteHandler chain) { this.bank = bank; this.chain = chain; }
        void insertCard(String c) { require(State.IDLE); card = c; pinTries = 0; state = State.CARD_INSERTED; }
        void enterPin(String pin) {
            require(State.CARD_INSERTED);
            if (bank.verify(card, pin)) state = State.AUTHENTICATED;
            else if (++pinTries >= 3) { eject(); throw new IllegalStateException("Card blocked after 3 wrong PINs"); }
            else throw new IllegalArgumentException("Wrong PIN");
        }
        Map<Integer, Integer> withdraw(long amount) {
            require(State.AUTHENTICATED);
            if (amount <= 0 || amount % 100 != 0) throw new IllegalArgumentException("Amount must be a multiple of 100");
            if (bank.balance(card) < amount) throw new IllegalStateException("Insufficient balance");
            Map<Integer, Integer> plan = new LinkedHashMap<>();
            if (!chain.plan(amount, plan)) throw new IllegalStateException("ATM cannot dispense this amount");
            bank.debit(card, amount); chain.take(plan);           // debit first, then dispense
            return plan;
        }
        void eject() { card = null; state = State.IDLE; }
        private void require(State s) { if (state != s) throw new IllegalStateException("Invalid in state " + state); }
    }

    public static void main(String[] args) {
        NoteHandler head = new Notes(2000, 2);
        head.then(new Notes(500, 5)).then(new Notes(200, 3)).then(new Notes(100, 10));
        Atm atm = new Atm(new InMemoryBank(), head);
        atm.insertCard("4111");
        try { atm.enterPin("0000"); } catch (IllegalArgumentException e) { System.out.println(e.getMessage()); }
        atm.enterPin("1234");
        System.out.println("6600 -> " + atm.withdraw(6600));
        System.out.println("800  -> " + atm.withdraw(800));
        atm.eject();
    }
}
""",
  ["Persist transactions; reconcile cash with the bank", "Deposit flow, mini statement", "Concurrency: one session per ATM; bank side handles concurrent debits atomically"]),

L("logger-lld", "Design a logging framework", "Intermediate",
  ["Microsoft", "Amazon", "Google"],
  ["Log levels DEBUG < INFO < WARN < ERROR", "Multiple appenders (console, file, remote) with their own minimum level", "Pluggable formats", "Asynchronous logging so callers don't block"],
  ["Logger", "Level enum", "Appender interface", "Formatter interface", "AsyncAppender (BlockingQueue + worker)"],
  ["Singleton (LogManager)", "Strategy (formatters)", "Observer-like fan-out to appenders", "Decorator (async wrapper)"],
  r"""
import java.time.*;
import java.util.*;
import java.util.concurrent.*;

public class LoggerDemo {
    enum Level { DEBUG, INFO, WARN, ERROR }
    record LogEvent(Instant time, Level level, String logger, String msg, String thread) {}

    interface Formatter { String format(LogEvent e); }
    static final class TextFormatter implements Formatter {
        public String format(LogEvent e) { return e.level() + " [" + e.logger() + "] " + e.msg(); }
    }
    static final class JsonFormatter implements Formatter {
        public String format(LogEvent e) { return "{\"level\":\"" + e.level() + "\",\"logger\":\"" + e.logger() + "\",\"msg\":\"" + e.msg().replace("\"", "\\\"") + "\"}"; }
    }

    interface Appender { void append(LogEvent e); default void close() {} }
    static final class ConsoleAppender implements Appender {
        private final Level min; private final Formatter f;
        ConsoleAppender(Level min, Formatter f) { this.min = min; this.f = f; }
        public void append(LogEvent e) { if (e.level().compareTo(min) >= 0) System.out.println(f.format(e)); }
    }
    static final class AsyncAppender implements Appender {            // decorator: same interface, adds a queue
        private final BlockingQueue<LogEvent> q = new LinkedBlockingQueue<>(10_000);
        private final Thread worker;
        AsyncAppender(Appender target) {
            worker = new Thread(() -> {
                try { while (true) { LogEvent e = q.take(); if (e.msg() == null) break; target.append(e); } }
                catch (InterruptedException ignored) { Thread.currentThread().interrupt(); }
            }, "log-writer");
            worker.start();
        }
        public void append(LogEvent e) { if (!q.offer(e)) System.err.println("log queue full, dropping"); }   // never block callers
        public void close() { q.offer(new LogEvent(null, Level.ERROR, "", null, "")); try { worker.join(); } catch (InterruptedException ignored) {} }
    }

    static final class LogManager {
        private static final LogManager INSTANCE = new LogManager();
        static LogManager get() { return INSTANCE; }
        private final List<Appender> appenders = new CopyOnWriteArrayList<>();
        private volatile Level rootLevel = Level.INFO;
        void addAppender(Appender a) { appenders.add(a); }
        void setLevel(Level l) { rootLevel = l; }
        Logger logger(String name) { return new Logger(name); }
        void shutdown() { appenders.forEach(Appender::close); }

        final class Logger {
            private final String name; Logger(String n) { name = n; }
            void log(Level l, String msg) {
                if (l.compareTo(rootLevel) < 0) return;
                LogEvent e = new LogEvent(Instant.now(), l, name, msg, Thread.currentThread().getName());
                appenders.forEach(a -> a.append(e));
            }
            void debug(String m) { log(Level.DEBUG, m); } void info(String m) { log(Level.INFO, m); }
            void warn(String m) { log(Level.WARN, m); } void error(String m) { log(Level.ERROR, m); }
        }
    }

    public static void main(String[] args) {
        LogManager lm = LogManager.get();
        lm.addAppender(new ConsoleAppender(Level.WARN, new TextFormatter()));
        lm.addAppender(new AsyncAppender(new ConsoleAppender(Level.INFO, new JsonFormatter())));
        LogManager.Logger log = lm.logger("OrderService");
        log.debug("not shown (root level INFO)");
        log.info("order 42 placed");
        log.error("payment \"declined\" for order 42");
        lm.shutdown();
    }
}
""",
  ["File appender with size/time-based rotation", "MDC (request ID per thread) for tracing", "Batching and backpressure policy (drop vs block)"]),

L("pubsub-lld", "Design an in-memory pub/sub message broker", "Intermediate",
  ["Amazon", "Microsoft", "Uber", "Flipkart"],
  ["Create topics; publishers publish messages", "Multiple subscribers per topic, each consuming at its own pace (own offset)", "Subscribers can reset offset to replay"],
  ["Topic (append-only message list)", "Message", "Subscriber interface", "SubscriberWorker (offset + thread)", "Broker"],
  ["Observer / pub-sub", "Log with per-consumer offsets (like Kafka)", "wait/notify for consumers"],
  r"""
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class PubSubDemo {
    record Message(long offset, String payload) {}
    interface Subscriber { String id(); void consume(Message m) throws Exception; }

    static final class Topic {
        final String name; private final List<Message> log = new ArrayList<>();
        Topic(String name) { this.name = name; }
        synchronized void publish(String payload) { log.add(new Message(log.size(), payload)); notifyAll(); }
        synchronized Message await(long offset) throws InterruptedException { while (offset >= log.size()) wait(); return log.get((int) offset); }
    }

    static final class SubscriberWorker implements Runnable {
        final Topic topic; final Subscriber sub; final AtomicLong offset = new AtomicLong(0); volatile boolean running = true;
        SubscriberWorker(Topic t, Subscriber s) { topic = t; sub = s; }
        public void run() {
            while (running) {
                try {
                    Message m = topic.await(offset.get());
                    sub.consume(m);                       // at-least-once: advance only after success
                    offset.incrementAndGet();
                } catch (InterruptedException e) { return; }
                catch (Exception e) { System.out.println(sub.id() + " failed, will retry offset " + offset.get()); }
            }
        }
    }

    static final class Broker {
        private final Map<String, Topic> topics = new ConcurrentHashMap<>();
        private final Map<String, SubscriberWorker> workers = new ConcurrentHashMap<>();
        private final ExecutorService pool = Executors.newCachedThreadPool();
        Topic createTopic(String name) { return topics.computeIfAbsent(name, Topic::new); }
        void publish(String topic, String payload) { topics.get(topic).publish(payload); }
        void subscribe(String topic, Subscriber s) { SubscriberWorker w = new SubscriberWorker(topics.get(topic), s); workers.put(topic + "/" + s.id(), w); pool.submit(w); }
        void resetOffset(String topic, String subId, long off) { workers.get(topic + "/" + subId).offset.set(off); }
        void shutdown() { workers.values().forEach(w -> w.running = false); pool.shutdownNow(); }
    }

    public static void main(String[] args) throws Exception {
        Broker b = new Broker(); b.createTopic("orders");
        CountDownLatch done = new CountDownLatch(6);
        List<String> seen = Collections.synchronizedList(new ArrayList<>());
        for (String id : List.of("email", "analytics")) {
            b.subscribe("orders", new Subscriber() {
                public String id() { return id; }
                public void consume(Message m) { seen.add(id + ":" + m.payload()); done.countDown(); }
            });
        }
        for (int i = 1; i <= 3; i++) b.publish("orders", "order-" + i);
        done.await(2, TimeUnit.SECONDS);
        Collections.sort(seen);
        System.out.println(seen);
        b.shutdown();
    }
}
""",
  ["Partitions + consumer groups for parallelism", "Retention and offset persistence", "Dead-letter topic after N failures", "Backpressure with bounded buffers"]),

L("taskscheduler-lld", "Design a task scheduler (delayed and recurring jobs)", "Advanced",
  ["Amazon", "Google", "Microsoft", "Uber", "Atlassian"],
  ["Schedule a task to run once after a delay, or at a fixed rate", "Worker pool executes tasks; cancel a scheduled task", "Tasks run as close as possible to their time"],
  ["ScheduledTask (runAt, period, Runnable)", "DelayQueue / PriorityQueue ordered by runAt", "Dispatcher thread", "Worker pool"],
  ["Priority queue by time (min-heap)", "Producer–consumer", "Command pattern (tasks as objects)"],
  r"""
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class TaskSchedulerDemo {
    static final class Scheduler {
        private static final AtomicLong SEQ = new AtomicLong();
        final class Task implements Delayed {
            final long id = SEQ.incrementAndGet(); final Runnable job; final long periodMs; volatile long runAtMs; volatile boolean cancelled;
            Task(Runnable job, long runAtMs, long periodMs) { this.job = job; this.runAtMs = runAtMs; this.periodMs = periodMs; }
            public long getDelay(TimeUnit u) { return u.convert(runAtMs - System.currentTimeMillis(), TimeUnit.MILLISECONDS); }
            public int compareTo(Delayed o) { Task t = (Task) o; int c = Long.compare(runAtMs, t.runAtMs); return c != 0 ? c : Long.compare(id, t.id); }
            void cancel() { cancelled = true; }
        }
        private final DelayQueue<Task> queue = new DelayQueue<>();
        private final ExecutorService workers;
        private final Thread dispatcher;
        private volatile boolean running = true;

        Scheduler(int threads) {
            workers = Executors.newFixedThreadPool(threads);
            dispatcher = new Thread(() -> {
                while (running) {
                    try {
                        Task t = queue.take();                     // blocks until the earliest task is due
                        if (t.cancelled) continue;
                        workers.submit(() -> { try { t.job.run(); } catch (Exception e) { System.out.println("task " + t.id + " failed: " + e); } });
                        if (t.periodMs > 0) { t.runAtMs += t.periodMs; queue.put(t); }   // fixed-rate reschedule
                    } catch (InterruptedException e) { return; }
                }
            }, "dispatcher");
            dispatcher.start();
        }
        Task schedule(Runnable r, long delayMs) { Task t = new Task(r, System.currentTimeMillis() + delayMs, 0); queue.put(t); return t; }
        Task scheduleAtFixedRate(Runnable r, long initialMs, long periodMs) { Task t = new Task(r, System.currentTimeMillis() + initialMs, periodMs); queue.put(t); return t; }
        void shutdown() { running = false; dispatcher.interrupt(); workers.shutdown(); }
    }

    public static void main(String[] args) throws Exception {
        Scheduler s = new Scheduler(2);
        List<String> log = Collections.synchronizedList(new ArrayList<>());
        s.schedule(() -> log.add("B (200ms)"), 200);
        s.schedule(() -> log.add("A (100ms)"), 100);
        Scheduler.Task cancelled = s.schedule(() -> log.add("never"), 150);
        cancelled.cancel();
        AtomicInteger ticks = new AtomicInteger();
        Scheduler.Task heartbeat = s.scheduleAtFixedRate(() -> ticks.incrementAndGet(), 0, 60);
        Thread.sleep(400);
        heartbeat.cancel();
        s.shutdown();
        System.out.println(log + ", heartbeat ran " + (ticks.get() >= 5 ? ">= 5" : ticks.get()) + " times");
    }
}
""",
  ["Persistence so tasks survive restarts (DB + leases)", "Distributed version with sharded time buckets and leader election", "Retries with backoff, priorities, cron expressions"]),

L("kvstore-lld", "Design an in-memory key–value store with TTL and transactions", "Advanced",
  ["Google", "Amazon", "Microsoft", "Rubrik", "Uber"],
  ["`set/get/delete` with optional TTL", "Nested transactions: BEGIN, ROLLBACK, COMMIT", "Thread-safe; expired keys never returned"],
  ["Store (ConcurrentHashMap of entries)", "Entry (value, expiresAt)", "Transaction stack of undo logs", "Expiry: lazy on read + periodic sweeper"],
  ["Undo log per transaction (Memento-like)", "Lazy + active expiry like Redis"],
  r"""
import java.util.*;
import java.util.concurrent.*;

public class KvStoreDemo {
    static final class KvStore {
        private record Entry(String value, long expiresAt) { boolean expired(long now) { return expiresAt > 0 && now >= expiresAt; } }
        private final Map<String, Entry> data = new HashMap<>();
        private final Deque<Map<String, Optional<Entry>>> txUndo = new ArrayDeque<>();   // per tx: key -> previous entry
        private final java.util.function.LongSupplier clock;
        KvStore(java.util.function.LongSupplier clock) { this.clock = clock; }

        synchronized void set(String k, String v, long ttlMs) { remember(k); data.put(k, new Entry(v, ttlMs > 0 ? clock.getAsLong() + ttlMs : 0)); }
        synchronized Optional<String> get(String k) {
            Entry e = data.get(k);
            if (e == null) return Optional.empty();
            if (e.expired(clock.getAsLong())) { data.remove(k); return Optional.empty(); }   // lazy expiry
            return Optional.of(e.value());
        }
        synchronized boolean delete(String k) { remember(k); return data.remove(k) != null; }

        synchronized void begin() { txUndo.push(new HashMap<>()); }
        synchronized void rollback() {
            if (txUndo.isEmpty()) throw new IllegalStateException("NO TRANSACTION");
            txUndo.pop().forEach((k, prev) -> { if (prev.isPresent()) data.put(k, prev.get()); else data.remove(k); });
        }
        synchronized void commit() {
            if (txUndo.isEmpty()) throw new IllegalStateException("NO TRANSACTION");
            Map<String, Optional<Entry>> top = txUndo.pop();
            if (!txUndo.isEmpty()) top.forEach(txUndo.peek()::putIfAbsent);     // merge into parent so its rollback still works
        }
        synchronized int sweep() {                                              // active expiry, run periodically
            long now = clock.getAsLong(); int before = data.size();
            data.values().removeIf(e -> e.expired(now));
            return before - data.size();
        }
        private void remember(String k) { if (!txUndo.isEmpty()) txUndo.peek().putIfAbsent(k, Optional.ofNullable(data.get(k))); }
    }

    public static void main(String[] args) {
        long[] now = {0};
        KvStore kv = new KvStore(() -> now[0]);
        kv.set("a", "10", 0);
        kv.begin(); kv.set("a", "20", 0);
        kv.begin(); kv.set("a", "30", 0); kv.delete("a");
        System.out.println("inner: " + kv.get("a"));      // empty
        kv.rollback();
        System.out.println("after inner rollback: " + kv.get("a"));   // 20
        kv.commit();
        System.out.println("after commit: " + kv.get("a"));           // 20
        kv.set("session", "xyz", 1000);
        now[0] = 1500;
        System.out.println("expired session: " + kv.get("session") + ", swept " + kv.sweep());
    }
}
""",
  ["Per-key striped locks or ConcurrentHashMap for higher concurrency", "Persistence (append-only file / snapshot)", "Eviction when memory is full (LRU)", "Replication to a follower"]),

L("shoppingcart-lld", "Design a shopping cart with discounts and coupons", "Intermediate",
  ["Amazon", "Flipkart", "Walmart", "Myntra"],
  ["Add/remove items with quantities", "Apply discounts: percentage off category, buy-X-get-Y, flat coupon with minimum order", "Compute final price with a breakdown"],
  ["Product, CartItem, Cart", "Discount interface + implementations", "PricingEngine (applies discounts in order)"],
  ["Strategy (each discount rule)", "Chain/pipeline of rules", "Money in paise"],
  r"""
import java.util.*;

public class ShoppingCartDemo {
    enum Category { ELECTRONICS, FASHION, GROCERY }
    record Product(String sku, String name, long pricePaise, Category category) {}
    record Line(Product product, int qty) { long total() { return product.pricePaise() * qty; } }

    static final class Cart {
        private final Map<String, Line> lines = new LinkedHashMap<>();
        void add(Product p, int qty) { lines.merge(p.sku(), new Line(p, qty), (a, b) -> new Line(p, a.qty() + b.qty())); }
        void remove(String sku) { lines.remove(sku); }
        Collection<Line> lines() { return lines.values(); }
        long subtotal() { return lines.values().stream().mapToLong(Line::total).sum(); }
    }

    record Applied(String name, long amountPaise) {}
    interface Discount { Optional<Applied> apply(Cart cart, long runningTotal); }

    static final class CategoryPercent implements Discount {
        final Category cat; final int pct; CategoryPercent(Category c, int p) { cat = c; pct = p; }
        public Optional<Applied> apply(Cart c, long total) {
            long base = c.lines().stream().filter(l -> l.product().category() == cat).mapToLong(Line::total).sum();
            return base == 0 ? Optional.empty() : Optional.of(new Applied(pct + "% off " + cat, base * pct / 100));
        }
    }
    static final class BuyXGetY implements Discount {
        final String sku; final int x, y; BuyXGetY(String sku, int x, int y) { this.sku = sku; this.x = x; this.y = y; }
        public Optional<Applied> apply(Cart c, long total) {
            return c.lines().stream().filter(l -> l.product().sku().equals(sku)).findFirst().flatMap(l -> {
                int free = (l.qty() / (x + y)) * y;
                return free == 0 ? Optional.empty() : Optional.of(new Applied("Buy " + x + " get " + y + " " + l.product().name(), free * l.product().pricePaise()));
            });
        }
    }
    static final class FlatCoupon implements Discount {
        final String code; final long off, minOrder; FlatCoupon(String code, long off, long min) { this.code = code; this.off = off; minOrder = min; }
        public Optional<Applied> apply(Cart c, long total) { return total >= minOrder ? Optional.of(new Applied("Coupon " + code, Math.min(off, total))) : Optional.empty(); }
    }

    static final class PricingEngine {
        private final List<Discount> rules;                 // order matters: item-level first, then cart-level coupons
        PricingEngine(List<Discount> rules) { this.rules = rules; }
        long price(Cart cart, List<Applied> breakdown) {
            long total = cart.subtotal();
            for (Discount d : rules) {
                Optional<Applied> a = d.apply(cart, total);
                if (a.isPresent()) { breakdown.add(a.get()); total -= a.get().amountPaise(); }
            }
            return Math.max(0, total);
        }
    }

    public static void main(String[] args) {
        Cart cart = new Cart();
        cart.add(new Product("P1", "Headphones", 299900, Category.ELECTRONICS), 1);
        cart.add(new Product("P2", "T-shirt", 49900, Category.FASHION), 3);
        cart.add(new Product("P3", "Milk", 3000, Category.GROCERY), 4);
        PricingEngine engine = new PricingEngine(List.of(new CategoryPercent(Category.ELECTRONICS, 10), new BuyXGetY("P2", 2, 1), new FlatCoupon("SAVE200", 20000, 300000)));
        List<Applied> br = new ArrayList<>();
        long finalPrice = engine.price(cart, br);
        System.out.println("subtotal Rs " + cart.subtotal() / 100.0);
        br.forEach(a -> System.out.println("  - " + a.name() + ": Rs " + a.amountPaise() / 100.0));
        System.out.println("pay Rs " + finalPrice / 100.0);
    }
}
""",
  ["Rule conflicts and 'best discount wins' selection", "Coupon usage limits per user (needs persistence + atomic counters)", "Inventory check on checkout; price snapshot at order time"]),

L("filesystem-lld", "Design an in-memory file system", "Intermediate",
  ["Google", "Microsoft", "Amazon", "Dropbox"],
  ["mkdir -p, create file with content, read file", "ls (sorted names), size of a directory (recursive)", "Paths like /a/b/c.txt"],
  ["Node (abstract)", "Directory (children map)", "File (content)", "FileSystem (path resolution)"],
  ["Composite (files and folders share an interface)", "TreeMap for sorted listing"],
  r"""
import java.util.*;

public class FileSystemDemo {
    static abstract class Node { final String name; Node(String n) { name = n; } abstract long size(); }
    static final class FileNode extends Node {
        private final StringBuilder content = new StringBuilder();
        FileNode(String n) { super(n); }
        long size() { return content.length(); }
    }
    static final class Dir extends Node {
        final TreeMap<String, Node> children = new TreeMap<>();
        Dir(String n) { super(n); }
        long size() { return children.values().stream().mapToLong(Node::size).sum(); }   // composite: recurse
    }

    static final class FileSystem {
        private final Dir root = new Dir("");
        private List<String> parts(String path) { List<String> p = new ArrayList<>(); for (String s : path.split("/")) if (!s.isEmpty()) p.add(s); return p; }
        private Dir dir(List<String> parts, boolean create) {
            Dir cur = root;
            for (String p : parts) {
                Node n = cur.children.get(p);
                if (n == null) { if (!create) throw new NoSuchElementException(p); n = new Dir(p); cur.children.put(p, n); }
                if (!(n instanceof Dir d)) throw new IllegalArgumentException(p + " is a file");
                cur = d;
            }
            return cur;
        }
        void mkdir(String path) { dir(parts(path), true); }
        void writeFile(String path, String text, boolean append) {
            List<String> p = parts(path); Dir parent = dir(p.subList(0, p.size() - 1), true); String name = p.get(p.size() - 1);
            Node n = parent.children.computeIfAbsent(name, FileNode::new);
            if (!(n instanceof FileNode f)) throw new IllegalArgumentException(name + " is a directory");
            if (!append) f.content.setLength(0);
            f.content.append(text);
        }
        String read(String path) {
            List<String> p = parts(path); Node n = dir(p.subList(0, p.size() - 1), false).children.get(p.get(p.size() - 1));
            if (!(n instanceof FileNode f)) throw new NoSuchElementException(path);
            return f.content.toString();
        }
        List<String> ls(String path) {
            List<String> p = parts(path);
            if (!p.isEmpty()) {
                Node n = dir(p.subList(0, p.size() - 1), false).children.get(p.get(p.size() - 1));
                if (n instanceof FileNode) return List.of(n.name);
            }
            return new ArrayList<>(dir(p, false).children.keySet());
        }
        long du(String path) { return path.equals("/") ? root.size() : dir(parts(path), false).size(); }
    }

    public static void main(String[] args) {
        FileSystem fs = new FileSystem();
        fs.mkdir("/home/shubham/projects");
        fs.writeFile("/home/shubham/projects/notes.md", "# DSA\n", false);
        fs.writeFile("/home/shubham/projects/notes.md", "Day 3: hashing\n", true);
        fs.writeFile("/home/shubham/todo.txt", "practice LLD", false);
        System.out.println(fs.ls("/home/shubham"));
        System.out.print(fs.read("/home/shubham/projects/notes.md"));
        System.out.println("du /home = " + fs.du("/home") + " chars");
    }
}
""",
  ["Permissions and owners", "Move/rename, symbolic links", "Persistence and journaling", "Concurrency with read/write locks per directory"]),

L("ridesharing-lld", "Design a ride-sharing service core (Uber LLD)", "Advanced",
  ["Uber", "Ola", "Amazon", "Microsoft"],
  ["Riders request rides; nearest available driver is matched", "Fare depends on distance, vehicle type and surge", "Trip states: REQUESTED → ACCEPTED → IN_PROGRESS → COMPLETED / CANCELLED", "No driver gets two trips at once"],
  ["Rider, Driver (location, status)", "Trip (state machine)", "MatchingStrategy", "PricingStrategy", "RideService"],
  ["Strategy (matching, pricing)", "State machine with allowed transitions", "Atomic driver assignment"],
  r"""
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class RideSharingDemo {
    record Location(double x, double y) { double dist(Location o) { return Math.hypot(x - o.x, y - o.y); } }
    enum VehicleType { AUTO, MINI, SEDAN }
    enum TripState { REQUESTED, ACCEPTED, IN_PROGRESS, COMPLETED, CANCELLED }

    static final class Driver {
        final String id; final VehicleType type; volatile Location loc; final AtomicBoolean available = new AtomicBoolean(true);
        Driver(String id, VehicleType t, Location l) { this.id = id; type = t; loc = l; }
    }
    static final class Trip {
        private static final Map<TripState, Set<TripState>> NEXT = Map.of(
            TripState.REQUESTED, EnumSet.of(TripState.ACCEPTED, TripState.CANCELLED),
            TripState.ACCEPTED, EnumSet.of(TripState.IN_PROGRESS, TripState.CANCELLED),
            TripState.IN_PROGRESS, EnumSet.of(TripState.COMPLETED),
            TripState.COMPLETED, EnumSet.noneOf(TripState.class), TripState.CANCELLED, EnumSet.noneOf(TripState.class));
        final String id, rider; final Location from, to; final VehicleType type; Driver driver; TripState state = TripState.REQUESTED; long fare;
        Trip(String id, String rider, Location f, Location t, VehicleType type) { this.id = id; this.rider = rider; from = f; to = t; this.type = type; }
        synchronized void moveTo(TripState s) { if (!NEXT.get(state).contains(s)) throw new IllegalStateException(state + " -> " + s + " not allowed"); state = s; }
    }

    interface MatchingStrategy { Optional<Driver> match(Collection<Driver> drivers, Trip t); }
    static final class NearestAvailable implements MatchingStrategy {
        public Optional<Driver> match(Collection<Driver> ds, Trip t) {
            List<Driver> c = ds.stream().filter(d -> d.type == t.type && d.available.get())
                               .sorted(Comparator.comparingDouble(d -> d.loc.dist(t.from))).toList();
            for (Driver d : c) if (d.available.compareAndSet(true, false)) return Optional.of(d);   // atomic claim
            return Optional.empty();
        }
    }
    interface PricingStrategy { long fare(Trip t, double surge); }
    static final class DistancePricing implements PricingStrategy {
        private final Map<VehicleType, long[]> rates = Map.of(VehicleType.AUTO, new long[]{30, 12}, VehicleType.MINI, new long[]{50, 15}, VehicleType.SEDAN, new long[]{80, 20});
        public long fare(Trip t, double surge) { long[] r = rates.get(t.type); return Math.round((r[0] + r[1] * t.from.dist(t.to)) * surge); }
    }

    static final class RideService {
        final Map<String, Driver> drivers = new ConcurrentHashMap<>(); final Map<String, Trip> trips = new ConcurrentHashMap<>();
        final MatchingStrategy matching; final PricingStrategy pricing; final AtomicInteger ids = new AtomicInteger();
        RideService(MatchingStrategy m, PricingStrategy p) { matching = m; pricing = p; }
        void addDriver(Driver d) { drivers.put(d.id, d); }
        Trip request(String rider, Location from, Location to, VehicleType type) {
            Trip t = new Trip("T" + ids.incrementAndGet(), rider, from, to, type); trips.put(t.id, t);
            matching.match(drivers.values(), t).ifPresentOrElse(d -> { t.driver = d; t.moveTo(TripState.ACCEPTED); }, () -> t.moveTo(TripState.CANCELLED));
            return t;
        }
        void start(String tripId) { trips.get(tripId).moveTo(TripState.IN_PROGRESS); }
        long complete(String tripId, double surge) {
            Trip t = trips.get(tripId); t.moveTo(TripState.COMPLETED); t.fare = pricing.fare(t, surge);
            t.driver.loc = t.to; t.driver.available.set(true); return t.fare;
        }
    }

    public static void main(String[] args) throws Exception {
        RideService svc = new RideService(new NearestAvailable(), new DistancePricing());
        svc.addDriver(new Driver("D1", VehicleType.MINI, new Location(0, 0)));
        svc.addDriver(new Driver("D2", VehicleType.MINI, new Location(5, 5)));
        ExecutorService pool = Executors.newFixedThreadPool(3);           // 3 riders, 2 drivers, simultaneous
        List<Future<Trip>> fs = new ArrayList<>();
        for (int i = 0; i < 3; i++) { String r = "R" + i; fs.add(pool.submit(() -> svc.request(r, new Location(1, 1), new Location(4, 5), VehicleType.MINI))); }
        Set<String> assigned = new TreeSet<>(); int cancelled = 0; Trip any = null;
        for (Future<Trip> f : fs) { Trip t = f.get(); if (t.state == TripState.ACCEPTED) { assigned.add(t.driver.id); any = t; } else cancelled++; }
        pool.shutdown();
        System.out.println("drivers assigned " + assigned + ", riders without a driver: " + cancelled);
        svc.start(any.id);
        System.out.println("fare Rs " + svc.complete(any.id, 1.5));
        try { svc.start(any.id); } catch (IllegalStateException e) { System.out.println("rejected: " + e.getMessage()); }
    }
}
""",
  ["Geo index (quadtree/geohash) instead of scanning all drivers", "Driver acceptance with timeout; offer to next driver", "Ratings, payments, cancellations fees", "Ride pooling"]),

L("notification-lld", "Design a notification service (LLD)", "Intermediate",
  ["Amazon", "Swiggy", "Microsoft", "PhonePe"],
  ["Send notifications through Email, SMS, Push", "Respect user channel preferences", "Templates with placeholders", "Retry failed sends; pluggable providers"],
  ["Notification, Template", "Channel interface (EmailChannel, SmsChannel, PushChannel)", "PreferenceStore", "NotificationService (with retry policy)"],
  ["Strategy (channels)", "Factory/registry of channels", "Template method for rendering", "Retry with backoff"],
  r"""
import java.util.*;
import java.util.regex.*;

public class NotificationServiceDemo {
    enum ChannelType { EMAIL, SMS, PUSH }
    record User(String id, String email, String phone, String deviceToken) {}
    record Template(String id, String subject, String body) {
        String render(Map<String, String> params) {
            Matcher m = Pattern.compile("\\{\\{(\\w+)}}").matcher(body); StringBuilder sb = new StringBuilder();
            while (m.find()) m.appendReplacement(sb, Matcher.quoteReplacement(params.getOrDefault(m.group(1), "")));
            return m.appendTail(sb).toString();
        }
    }

    interface Channel { ChannelType type(); void send(User u, String subject, String text) throws Exception; }
    static final class EmailChannel implements Channel {
        public ChannelType type() { return ChannelType.EMAIL; }
        public void send(User u, String s, String t) { System.out.println("EMAIL to " + u.email() + ": [" + s + "] " + t); }
    }
    static final class FlakySmsChannel implements Channel {          // fails the first time to show retries
        private int calls; public ChannelType type() { return ChannelType.SMS; }
        public void send(User u, String s, String t) throws Exception { if (calls++ == 0) throw new Exception("gateway timeout"); System.out.println("SMS to " + u.phone() + ": " + t); }
    }
    static final class PushChannel implements Channel {
        public ChannelType type() { return ChannelType.PUSH; }
        public void send(User u, String s, String t) { System.out.println("PUSH to " + u.deviceToken() + ": " + s); }
    }

    static final class NotificationService {
        private final Map<ChannelType, Channel> channels = new EnumMap<>(ChannelType.class);
        private final Map<String, Set<ChannelType>> prefs = new HashMap<>();
        private final Map<String, Template> templates = new HashMap<>();
        private final Set<String> sentKeys = new HashSet<>();          // idempotency
        private final int maxAttempts;
        NotificationService(List<Channel> cs, int maxAttempts) { cs.forEach(c -> channels.put(c.type(), c)); this.maxAttempts = maxAttempts; }
        void setPreferences(String userId, Set<ChannelType> s) { prefs.put(userId, s); }
        void addTemplate(Template t) { templates.put(t.id(), t); }

        void notify(String idempotencyKey, User u, String templateId, Map<String, String> params) {
            if (!sentKeys.add(idempotencyKey)) { System.out.println("duplicate " + idempotencyKey + " ignored"); return; }
            Template t = templates.get(templateId); String text = t.render(params);
            for (ChannelType ct : prefs.getOrDefault(u.id(), EnumSet.of(ChannelType.EMAIL))) {
                Channel c = channels.get(ct);
                for (int attempt = 1; ; attempt++) {
                    try { c.send(u, t.subject(), text); break; }
                    catch (Exception e) {
                        if (attempt == maxAttempts) { System.out.println(ct + " failed permanently -> DLQ"); break; }
                        long backoff = (long) (50 * Math.pow(2, attempt - 1));
                        System.out.println(ct + " attempt " + attempt + " failed (" + e.getMessage() + "), retry in " + backoff + "ms");
                        try { Thread.sleep(backoff); } catch (InterruptedException ie) { Thread.currentThread().interrupt(); return; }
                    }
                }
            }
        }
    }

    public static void main(String[] args) {
        NotificationService svc = new NotificationService(List.of(new EmailChannel(), new FlakySmsChannel(), new PushChannel()), 3);
        svc.addTemplate(new Template("ORDER_SHIPPED", "Your order shipped", "Hi {{name}}, order {{orderId}} is on the way!"));
        User u = new User("u1", "asha@example.com", "+91-90000-00000", "device-abc");
        svc.setPreferences("u1", EnumSet.of(ChannelType.SMS, ChannelType.PUSH));
        svc.notify("ship-42", u, "ORDER_SHIPPED", Map.of("name", "Asha", "orderId", "42"));
        svc.notify("ship-42", u, "ORDER_SHIPPED", Map.of("name", "Asha", "orderId", "42"));
    }
}
""",
  ["Async sending through queues per channel", "Rate limits per user and quiet hours", "Priority (OTP vs marketing)", "Delivery tracking and provider failover"]),
]
