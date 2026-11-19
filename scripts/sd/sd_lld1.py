"""Low-level design questions with complete, runnable Java code (part 1). Each code block is one file:
public class <Name> with nested types and a main() demo. Compiled and run by sd/check_lld.py."""
from sd_util2 import L

LLD1 = [
L("parkinglot-lld", "Design a parking lot", "Basic",
  ["Amazon", "Microsoft", "Google", "Flipkart", "Uber"],
  ["Multiple floors, each with spots of types BIKE, CAR, TRUCK", "Park a vehicle in the nearest free spot of its type and issue a ticket", "Unpark with a ticket and compute the fee (hourly)", "Show free spots per floor; thread-safe parking"],
  ["ParkingLot", "Floor", "Spot", "Vehicle / VehicleType", "Ticket", "FeeStrategy", "SpotAllocationStrategy"],
  ["Strategy (fees, allocation)", "Singleton-free design with dependency injection", "Enums for types"],
  r"""
import java.time.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

public class ParkingLotDemo {
    enum VehicleType { BIKE, CAR, TRUCK }
    record Vehicle(String number, VehicleType type) {}

    static final class Spot {
        final int floor, id; final VehicleType type; Vehicle parked;
        Spot(int floor, int id, VehicleType type) { this.floor = floor; this.id = id; this.type = type; }
        boolean isFree() { return parked == null; }
    }
    record Ticket(long id, Vehicle vehicle, Spot spot, Instant entry) {}

    interface FeeStrategy { long fee(VehicleType type, Duration parked); }
    static final class HourlyFee implements FeeStrategy {               // first hour charged in full
        private final Map<VehicleType, Long> perHour = Map.of(VehicleType.BIKE, 20L, VehicleType.CAR, 40L, VehicleType.TRUCK, 100L);
        public long fee(VehicleType t, Duration d) { long hours = Math.max(1, (d.toMinutes() + 59) / 60); return hours * perHour.get(t); }
    }
    interface AllocationStrategy { Optional<Spot> pick(List<Spot> spots, VehicleType type); }
    static final class NearestFirst implements AllocationStrategy {     // spots are kept ordered floor 0 → n
        public Optional<Spot> pick(List<Spot> spots, VehicleType type) {
            return spots.stream().filter(s -> s.type == type && s.isFree()).findFirst();
        }
    }

    static final class ParkingLot {
        private final List<Spot> spots = new ArrayList<>();
        private final Map<Long, Ticket> active = new HashMap<>();
        private final AtomicLong ids = new AtomicLong(1);
        private final FeeStrategy fees; private final AllocationStrategy allocation; private final Clock clock;

        ParkingLot(int floors, Map<VehicleType, Integer> spotsPerFloor, FeeStrategy fees, AllocationStrategy allocation, Clock clock) {
            this.fees = fees; this.allocation = allocation; this.clock = clock;
            for (int f = 0; f < floors; f++) {
                int id = 0;
                for (VehicleType t : VehicleType.values())
                    for (int i = 0; i < spotsPerFloor.getOrDefault(t, 0); i++) spots.add(new Spot(f, id++, t));
            }
        }
        synchronized Ticket park(Vehicle v) {                      // one lock keeps allocation race-free
            Spot s = allocation.pick(spots, v.type()).orElseThrow(() -> new IllegalStateException("Lot full for " + v.type()));
            s.parked = v;
            Ticket t = new Ticket(ids.getAndIncrement(), v, s, clock.instant());
            active.put(t.id(), t);
            return t;
        }
        synchronized long unpark(long ticketId) {
            Ticket t = active.remove(ticketId);
            if (t == null) throw new IllegalArgumentException("Invalid ticket " + ticketId);
            t.spot().parked = null;
            return fees.fee(t.vehicle().type(), Duration.between(t.entry(), clock.instant()));
        }
        synchronized Map<Integer, Long> freeSpots(VehicleType type) {
            Map<Integer, Long> m = new TreeMap<>();
            for (Spot s : spots) if (s.type == type && s.isFree()) m.merge(s.floor, 1L, Long::sum);
            return m;
        }
    }

    static final class MutableClock extends Clock {               // lets the demo move time forward
        Instant now = Instant.parse("2026-11-20T10:00:00Z");
        public ZoneId getZone() { return ZoneOffset.UTC; }
        public Clock withZone(ZoneId z) { return this; }
        public Instant instant() { return now; }
    }

    public static void main(String[] args) {
        MutableClock clock = new MutableClock();
        ParkingLot lot = new ParkingLot(2, Map.of(VehicleType.CAR, 2, VehicleType.BIKE, 1), new HourlyFee(), new NearestFirst(), clock);
        Ticket t1 = lot.park(new Vehicle("TN01AB1234", VehicleType.CAR));
        Ticket t2 = lot.park(new Vehicle("TN02CD5678", VehicleType.CAR));
        Ticket t3 = lot.park(new Vehicle("TN03EF9999", VehicleType.CAR));
        System.out.println("t1 floor " + t1.spot().floor + ", t3 floor " + t3.spot().floor);
        System.out.println("free car spots " + lot.freeSpots(VehicleType.CAR));
        clock.now = clock.now.plus(Duration.ofMinutes(130));
        System.out.println("fee t1 = Rs " + lot.unpark(t1.id()));      // 3 hours x 40
        System.out.println("free car spots " + lot.freeSpots(VehicleType.CAR));
    }
}
""",
  ["Multiple entry/exit gates (gates call the same ParkingLot service)", "Per-floor locks instead of one global lock for higher concurrency", "Reservations, EV charging spots, display boards (Observer)", "Persist tickets in a DB; payments via a PaymentGateway interface"]),

L("lru-lld", "Design an LRU cache (LeetCode 146)", "Basic",
  ["Amazon", "Google", "Microsoft", "Meta", "Uber"],
  ["`get(key)` returns value or -1, marks key most recently used", "`put(key, value)` inserts/updates; evicts least recently used when over capacity", "Both O(1)", "Thread-safe variant"],
  ["Node (key, value, prev, next)", "HashMap<key, Node>", "Doubly linked list with sentinel head/tail"],
  ["HashMap + doubly linked list", "Generic types", "ReentrantLock for thread safety"],
  r"""
import java.util.*;
import java.util.concurrent.locks.ReentrantLock;

public class LruCacheDemo {
    static final class LRUCache<K, V> {
        private final class Node { K key; V val; Node prev, next; Node(K k, V v) { key = k; val = v; } }
        private final int capacity;
        private final Map<K, Node> map = new HashMap<>();
        private final Node head = new Node(null, null), tail = new Node(null, null);   // sentinels
        private final ReentrantLock lock = new ReentrantLock();

        LRUCache(int capacity) { this.capacity = capacity; head.next = tail; tail.prev = head; }

        Optional<V> get(K key) {
            lock.lock();
            try {
                Node n = map.get(key);
                if (n == null) return Optional.empty();
                moveToFront(n);
                return Optional.of(n.val);
            } finally { lock.unlock(); }
        }
        void put(K key, V val) {
            lock.lock();
            try {
                Node n = map.get(key);
                if (n != null) { n.val = val; moveToFront(n); return; }
                if (map.size() == capacity) { Node lru = tail.prev; unlink(lru); map.remove(lru.key); }
                n = new Node(key, val); map.put(key, n); addFront(n);
            } finally { lock.unlock(); }
        }
        private void unlink(Node n) { n.prev.next = n.next; n.next.prev = n.prev; }
        private void addFront(Node n) { n.next = head.next; n.prev = head; head.next.prev = n; head.next = n; }
        private void moveToFront(Node n) { unlink(n); addFront(n); }
    }

    public static void main(String[] args) {
        LRUCache<Integer, String> c = new LRUCache<>(2);
        c.put(1, "one"); c.put(2, "two");
        System.out.println(c.get(1));        // Optional[one]  -> 1 becomes most recent
        c.put(3, "three");                   // evicts 2
        System.out.println(c.get(2));        // Optional.empty
        System.out.println(c.get(3));        // Optional[three]
    }
}
""",
  ["LFU cache (LeetCode 460) with frequency buckets", "TTL per entry", "Sharded locks / ConcurrentHashMap + approximate LRU for high concurrency", "Java shortcut: LinkedHashMap(accessOrder=true) + removeEldestEntry"]),

L("elevator-lld", "Design an elevator system", "Intermediate",
  ["Amazon", "Microsoft", "Google", "Uber"],
  ["N elevators, M floors", "Hall calls (up/down at a floor) and car calls (button inside)", "Dispatcher assigns the best elevator", "Elevators serve requests in the current direction first (SCAN / LOOK)"],
  ["Elevator (state, direction, stop sets)", "Direction enum", "Request", "Dispatcher with DispatchStrategy", "ElevatorSystem (simulation step)"],
  ["Strategy (dispatch)", "State via enum", "TreeSet for ordered stops (LOOK algorithm)"],
  r"""
import java.util.*;

public class ElevatorDemo {
    enum Direction { UP, DOWN, IDLE }

    static final class Elevator {
        final int id; int floor = 0; Direction dir = Direction.IDLE;
        final TreeSet<Integer> upStops = new TreeSet<>(), downStops = new TreeSet<>();
        Elevator(int id) { this.id = id; }
        void addStop(int f) { if (f > floor) upStops.add(f); else if (f < floor) downStops.add(f); }
        boolean idle() { return upStops.isEmpty() && downStops.isEmpty(); }

        void step() {                                    // move one floor per tick (LOOK algorithm)
            if (dir == Direction.IDLE) dir = !upStops.isEmpty() ? Direction.UP : !downStops.isEmpty() ? Direction.DOWN : Direction.IDLE;
            if (dir == Direction.UP) {
                floor++;
                if (upStops.remove(floor)) System.out.println("  E" + id + " stops at " + floor);
                if (upStops.isEmpty()) dir = downStops.isEmpty() ? Direction.IDLE : Direction.DOWN;
            } else if (dir == Direction.DOWN) {
                floor--;
                if (downStops.remove(floor)) System.out.println("  E" + id + " stops at " + floor);
                if (downStops.isEmpty()) dir = upStops.isEmpty() ? Direction.IDLE : Direction.UP;
            }
        }
    }

    interface DispatchStrategy { Elevator choose(List<Elevator> all, int floor, Direction want); }
    static final class NearestSuitable implements DispatchStrategy {
        public Elevator choose(List<Elevator> all, int floor, Direction want) {
            return all.stream().min(Comparator.comparingInt(e -> cost(e, floor, want))).orElseThrow();
        }
        private int cost(Elevator e, int floor, Direction want) {
            int d = Math.abs(e.floor - floor);
            boolean onTheWay = (e.dir == Direction.UP && want == Direction.UP && floor >= e.floor)
                            || (e.dir == Direction.DOWN && want == Direction.DOWN && floor <= e.floor);
            return e.idle() || onTheWay ? d : d + 100;     // penalise elevators moving away
        }
    }

    static final class ElevatorSystem {
        final List<Elevator> elevators = new ArrayList<>(); final DispatchStrategy strategy;
        ElevatorSystem(int n, DispatchStrategy s) { for (int i = 0; i < n; i++) elevators.add(new Elevator(i)); strategy = s; }
        void hallCall(int floor, Direction want) {
            Elevator e = strategy.choose(elevators, floor, want);
            System.out.println("hall call " + floor + " " + want + " -> E" + e.id);
            e.addStop(floor);
        }
        void carCall(int elevatorId, int floor) { elevators.get(elevatorId).addStop(floor); }
        void tick() { elevators.forEach(Elevator::step); }
    }

    public static void main(String[] args) {
        ElevatorSystem sys = new ElevatorSystem(2, new NearestSuitable());
        sys.hallCall(5, Direction.UP);
        sys.hallCall(2, Direction.UP);
        for (int t = 0; t < 3; t++) sys.tick();
        sys.carCall(1, 7);
        for (int t = 0; t < 8; t++) sys.tick();
        sys.elevators.forEach(e -> System.out.println("E" + e.id + " at floor " + e.floor + " " + e.dir));
    }
}
""",
  ["Door states and safety (State pattern)", "Capacity/weight limits", "Peak-hour zoning (elevators dedicated to floor ranges)", "Concurrency: dispatcher thread + elevator threads with a BlockingQueue of requests"]),

L("vending-lld", "Design a vending machine", "Intermediate",
  ["Amazon", "Microsoft", "Google", "Walmart"],
  ["Select a product, insert coins/notes, dispense product and change", "Cancel returns inserted money", "Out-of-stock and insufficient-funds handling"],
  ["VendingMachine (context)", "State interface: Idle, HasSelection, Dispensing", "Inventory", "Coin enum", "Change maker"],
  ["State pattern", "Greedy change making"],
  r"""
import java.util.*;

public class VendingMachineDemo {
    enum Coin { ONE(1), TWO(2), FIVE(5), TEN(10), TWENTY(20); final int v; Coin(int v) { this.v = v; } }
    record Product(String code, String name, int price) {}

    interface State {
        default void select(VendingMachine m, String code) { throw new IllegalStateException("Cannot select now"); }
        default void insert(VendingMachine m, Coin c) { throw new IllegalStateException("Select a product first"); }
        default List<Coin> cancel(VendingMachine m) { return List.of(); }
    }
    static final class Idle implements State {
        public void select(VendingMachine m, String code) {
            Product p = m.catalog.get(code);
            if (p == null || m.stock.getOrDefault(code, 0) == 0) throw new IllegalStateException("Out of stock: " + code);
            m.selected = p; m.state = new HasSelection();
            System.out.println("Selected " + p.name() + " (Rs " + p.price() + ")");
        }
    }
    static final class HasSelection implements State {
        public void insert(VendingMachine m, Coin c) {
            m.inserted.add(c); m.balance += c.v;
            if (m.balance >= m.selected.price()) { m.state = new Dispensing(); m.dispense(); }
        }
        public List<Coin> cancel(VendingMachine m) { List<Coin> back = new ArrayList<>(m.inserted); m.reset(); return back; }
    }
    static final class Dispensing implements State {}

    static final class VendingMachine {
        final Map<String, Product> catalog = new HashMap<>();
        final Map<String, Integer> stock = new HashMap<>();
        final EnumMap<Coin, Integer> till = new EnumMap<>(Coin.class);
        State state = new Idle(); Product selected; int balance; final List<Coin> inserted = new ArrayList<>();

        void load(Product p, int qty) { catalog.put(p.code(), p); stock.merge(p.code(), qty, Integer::sum); }
        void loadTill(Coin c, int n) { till.merge(c, n, Integer::sum); }
        void select(String code) { state.select(this, code); }
        void insert(Coin c) { state.insert(this, c); }
        List<Coin> cancel() { return state.cancel(this); }

        void dispense() {
            inserted.forEach(c -> till.merge(c, 1, Integer::sum));
            List<Coin> change = makeChange(balance - selected.price());
            if (change == null) {                                // can't give exact change: refund
                inserted.forEach(c -> till.merge(c, -1, Integer::sum));
                System.out.println("No exact change, refunded " + inserted); reset(); return;
            }
            stock.merge(selected.code(), -1, Integer::sum);
            System.out.println("Dispensed " + selected.name() + ", change " + change);
            reset();
        }
        private List<Coin> makeChange(int amount) {            // greedy works for these denominations
            List<Coin> out = new ArrayList<>(); EnumMap<Coin, Integer> t = new EnumMap<>(till);
            Coin[] cs = Coin.values();
            for (int i = cs.length - 1; i >= 0 && amount > 0; i--)
                while (amount >= cs[i].v && t.getOrDefault(cs[i], 0) > 0) { amount -= cs[i].v; t.merge(cs[i], -1, Integer::sum); out.add(cs[i]); }
            if (amount != 0) return null;
            till.clear(); till.putAll(t); return out;
        }
        void reset() { selected = null; balance = 0; inserted.clear(); state = new Idle(); }
    }

    public static void main(String[] args) {
        VendingMachine m = new VendingMachine();
        m.load(new Product("A1", "Chips", 15), 2); m.load(new Product("B2", "Juice", 25), 1);
        m.loadTill(Coin.FIVE, 5); m.loadTill(Coin.TWO, 5); m.loadTill(Coin.ONE, 5);
        m.select("A1"); m.insert(Coin.TEN); m.insert(Coin.TEN);           // change 5
        m.select("B2"); m.insert(Coin.TEN);
        System.out.println("Cancelled, returned " + m.cancel());
        try { m.insert(Coin.TEN); } catch (IllegalStateException e) { System.out.println("Error: " + e.getMessage()); }
    }
}
""",
  ["Card/UPI payments via a PaymentStrategy", "Admin mode for restocking (another State)", "Thread safety if several UIs share the machine"]),

L("splitwise-lld", "Design Splitwise (expense sharing)", "Intermediate",
  ["Amazon", "Flipkart", "Microsoft", "Goldman Sachs"],
  ["Users add expenses split EQUAL, EXACT or PERCENT", "Show balances (who owes whom)", "Simplify debts to the minimum number of transactions"],
  ["User", "Expense", "SplitStrategy (Equal/Exact/Percent)", "BalanceSheet (net balance per user)", "DebtSimplifier"],
  ["Strategy (split types)", "Greedy debt simplification with heaps", "Money in paise (long), never double"],
  r"""
import java.util.*;

public class SplitwiseDemo {
    record User(String id, String name) {}

    interface SplitStrategy { Map<String, Long> split(long amountPaise, List<String> users, List<Long> params); }
    static final class EqualSplit implements SplitStrategy {
        public Map<String, Long> split(long amt, List<String> users, List<Long> p) {
            Map<String, Long> m = new LinkedHashMap<>(); long each = amt / users.size(), rem = amt % users.size();
            for (int i = 0; i < users.size(); i++) m.put(users.get(i), each + (i < rem ? 1 : 0));   // spread leftover paise
            return m;
        }
    }
    static final class ExactSplit implements SplitStrategy {
        public Map<String, Long> split(long amt, List<String> users, List<Long> p) {
            if (p.stream().mapToLong(Long::longValue).sum() != amt) throw new IllegalArgumentException("Exact amounts must add up");
            Map<String, Long> m = new LinkedHashMap<>(); for (int i = 0; i < users.size(); i++) m.put(users.get(i), p.get(i)); return m;
        }
    }
    static final class PercentSplit implements SplitStrategy {
        public Map<String, Long> split(long amt, List<String> users, List<Long> pct) {
            if (pct.stream().mapToLong(Long::longValue).sum() != 100) throw new IllegalArgumentException("Percents must add to 100");
            Map<String, Long> m = new LinkedHashMap<>(); long given = 0;
            for (int i = 0; i < users.size(); i++) {
                long share = i == users.size() - 1 ? amt - given : amt * pct.get(i) / 100;
                m.put(users.get(i), share); given += share;
            }
            return m;
        }
    }

    static final class ExpenseService {
        final Map<String, Long> net = new TreeMap<>();     // +ve = should receive, -ve = owes
        void addExpense(String paidBy, long amountPaise, List<String> users, SplitStrategy s, List<Long> params) {
            Map<String, Long> shares = s.split(amountPaise, users, params);
            net.merge(paidBy, amountPaise, Long::sum);
            shares.forEach((u, share) -> net.merge(u, -share, Long::sum));
        }
        List<String> simplify() {                           // greedy: largest debtor pays largest creditor
            PriorityQueue<long[]> cred = new PriorityQueue<>((a, b) -> Long.compare(b[1], a[1]));
            PriorityQueue<long[]> debt = new PriorityQueue<>((a, b) -> Long.compare(b[1], a[1]));
            List<String> names = new ArrayList<>(net.keySet());
            for (int i = 0; i < names.size(); i++) {
                long v = net.get(names.get(i));
                if (v > 0) cred.add(new long[]{i, v}); else if (v < 0) debt.add(new long[]{i, -v});
            }
            List<String> tx = new ArrayList<>();
            while (!cred.isEmpty() && !debt.isEmpty()) {
                long[] c = cred.poll(), d = debt.poll(); long x = Math.min(c[1], d[1]);
                tx.add(names.get((int) d[0]) + " pays " + names.get((int) c[0]) + " Rs " + x / 100.0);
                if (c[1] > x) cred.add(new long[]{c[0], c[1] - x});
                if (d[1] > x) debt.add(new long[]{d[0], d[1] - x});
            }
            return tx;
        }
    }

    public static void main(String[] args) {
        ExpenseService s = new ExpenseService();
        List<String> all = List.of("amit", "bina", "chen", "dev");
        s.addExpense("amit", 100000, all, new EqualSplit(), List.of());                          // Rs 1000 dinner
        s.addExpense("bina", 50000, List.of("bina", "chen"), new ExactSplit(), List.of(20000L, 30000L));
        s.addExpense("dev", 30000, List.of("amit", "dev"), new PercentSplit(), List.of(40L, 60L));
        System.out.println("net balances (paise): " + s.net);
        s.simplify().forEach(System.out::println);
    }
}
""",
  ["Groups and per-group balances", "Persist expenses (event log) and recompute balances", "Optimal minimisation is NP-hard; greedy gives at most n−1 transactions", "Multiple currencies with conversion"]),

L("bookmyshow-lld", "Design a movie ticket booking system (BookMyShow)", "Advanced",
  ["Amazon", "Microsoft", "Flipkart", "BookMyShow", "Google"],
  ["Cities → theatres → screens → shows", "View seats for a show", "Hold seats for 5 minutes, then confirm with payment", "No double booking under concurrency"],
  ["Movie, Theatre, Screen, Show, Seat (type, price)", "SeatLock (holdId, expiry)", "Booking, BookingService", "PaymentService interface"],
  ["Fine-grained locking per show", "Holds with expiry", "Strategy for pricing"],
  r"""
import java.time.*;
import java.util.*;
import java.util.concurrent.*;

public class BookMyShowDemo {
    enum SeatType { REGULAR, PREMIUM }
    record Seat(String id, SeatType type) {}
    record Show(String id, String movie, Instant start, List<Seat> seats) {}
    record Hold(String id, String showId, Set<String> seats, String user, Instant expires) {}
    record Booking(String id, String showId, Set<String> seats, String user, long amount) {}

    interface PricingStrategy { long price(Seat s, Show show); }
    static final class SimplePricing implements PricingStrategy {
        public long price(Seat s, Show show) { return s.type() == SeatType.PREMIUM ? 350 : 200; }
    }

    static final class BookingService {
        private final Map<String, Show> shows = new ConcurrentHashMap<>();
        private final Map<String, Map<String, String>> taken = new ConcurrentHashMap<>();  // show -> seat -> holdId/BOOKED
        private final Map<String, Hold> holds = new ConcurrentHashMap<>();
        private final PricingStrategy pricing; private final Clock clock;
        BookingService(PricingStrategy p, Clock c) { pricing = p; clock = c; }

        void addShow(Show s) { shows.put(s.id(), s); taken.put(s.id(), new HashMap<>()); }

        Hold hold(String showId, Set<String> seatIds, String user) {
            Map<String, String> t = taken.get(showId);
            synchronized (t) {                                     // lock per show, not global
                releaseExpired(showId, t);
                for (String s : seatIds) if (t.containsKey(s)) throw new IllegalStateException("Seat " + s + " not available");
                Hold h = new Hold(UUID.randomUUID().toString(), showId, seatIds, user, clock.instant().plus(Duration.ofMinutes(5)));
                seatIds.forEach(s -> t.put(s, h.id()));
                holds.put(h.id(), h);
                return h;
            }
        }
        Booking confirm(String holdId, boolean paymentOk) {
            Hold h = holds.remove(holdId);
            if (h == null) throw new IllegalStateException("Hold not found");
            Map<String, String> t = taken.get(h.showId());
            synchronized (t) {
                boolean valid = clock.instant().isBefore(h.expires()) && h.seats().stream().allMatch(s -> holdId.equals(t.get(s)));
                if (!valid || !paymentOk) { h.seats().forEach(s -> t.remove(s, holdId)); throw new IllegalStateException("Hold expired or payment failed"); }
                h.seats().forEach(s -> t.put(s, "BOOKED"));
            }
            Show show = shows.get(h.showId());
            long amount = show.seats().stream().filter(s -> h.seats().contains(s.id())).mapToLong(s -> pricing.price(s, show)).sum();
            return new Booking(UUID.randomUUID().toString(), h.showId(), h.seats(), h.user(), amount);
        }
        private void releaseExpired(String showId, Map<String, String> t) {
            Instant now = clock.instant();
            holds.values().removeIf(h -> {
                if (h.showId().equals(showId) && !now.isBefore(h.expires())) { h.seats().forEach(s -> t.remove(s, h.id())); return true; }
                return false;
            });
        }
    }

    public static void main(String[] args) throws Exception {
        Clock clock = Clock.systemUTC();
        BookingService svc = new BookingService(new SimplePricing(), clock);
        List<Seat> seats = new ArrayList<>();
        for (int i = 1; i <= 10; i++) seats.add(new Seat("A" + i, i > 8 ? SeatType.PREMIUM : SeatType.REGULAR));
        svc.addShow(new Show("S1", "Interstellar", Instant.now(), seats));

        ExecutorService pool = Executors.newFixedThreadPool(8);          // 8 users race for seat A9
        List<Future<String>> results = new ArrayList<>();
        for (int u = 0; u < 8; u++) {
            String user = "user" + u;
            results.add(pool.submit(() -> {
                try { Hold h = svc.hold("S1", Set.of("A9", "A10"), user); return user + " booked " + svc.confirm(h.id(), true).amount(); }
                catch (IllegalStateException e) { return user + " failed"; }
            }));
        }
        long wins = 0; for (Future<String> f : results) if (f.get().contains("booked")) { wins++; System.out.println(f.get()); }
        pool.shutdown();
        System.out.println("successful bookings for A9+A10: " + wins);
    }
}
""",
  ["Distributed version: DB conditional updates or Redis `SET NX EX` holds", "Payment saga and refunds", "Search for movies/shows by city (catalogue service + cache)", "Seat-map UI updates via WebSocket"]),

L("library-lld", "Design a library management system", "Basic",
  ["Microsoft", "Amazon", "Adobe"],
  ["Add books (multiple copies)", "Members borrow (max 3) and return; due in 14 days", "Fines for late returns", "Reserve a book that's all checked out; notify when available"],
  ["Book, BookCopy", "Member", "Loan", "Library service", "FinePolicy", "Notifier (Observer)"],
  ["Strategy (fines)", "Observer (reservation notifications)", "Repository-style maps"],
  r"""
import java.time.*;
import java.util.*;

public class LibraryDemo {
    record Book(String isbn, String title) {}
    record Copy(String id, Book book) {}
    record Member(String id, String name) {}
    record Loan(Copy copy, Member member, LocalDate due) {}

    interface FinePolicy { long fine(LocalDate due, LocalDate returned); }
    static final class PerDayFine implements FinePolicy {
        public long fine(LocalDate due, LocalDate ret) { long late = Duration.between(due.atStartOfDay(), ret.atStartOfDay()).toDays(); return Math.max(0, late) * 10; }
    }
    interface Notifier { void notify(Member m, String msg); }

    static final class Library {
        private final Map<String, List<Copy>> available = new HashMap<>();
        private final Map<String, Loan> loans = new HashMap<>();                    // copyId -> loan
        private final Map<String, Deque<Member>> reservations = new HashMap<>();   // isbn -> queue
        private final FinePolicy fines; private final Notifier notifier;
        Library(FinePolicy f, Notifier n) { fines = f; notifier = n; }

        void addCopies(Book b, int n) { for (int i = 0; i < n; i++) available.computeIfAbsent(b.isbn(), k -> new ArrayList<>()).add(new Copy(b.isbn() + "-" + i, b)); }

        Loan borrow(Member m, String isbn, LocalDate today) {
            long current = loans.values().stream().filter(l -> l.member().equals(m)).count();
            if (current >= 3) throw new IllegalStateException(m.name() + " already has 3 books");
            Deque<Member> q = reservations.getOrDefault(isbn, new ArrayDeque<>());
            if (!q.isEmpty() && !q.peek().equals(m)) throw new IllegalStateException("Reserved for " + q.peek().name());
            List<Copy> free = available.getOrDefault(isbn, List.of());
            if (free.isEmpty()) throw new IllegalStateException("No copy available");
            if (!q.isEmpty()) q.poll();
            Copy c = free.remove(free.size() - 1);
            Loan l = new Loan(c, m, today.plusDays(14)); loans.put(c.id(), l); return l;
        }
        long giveBack(String copyId, LocalDate today) {
            Loan l = loans.remove(copyId); if (l == null) throw new IllegalArgumentException("Not on loan");
            available.get(l.copy().book().isbn()).add(l.copy());
            Deque<Member> q = reservations.get(l.copy().book().isbn());
            if (q != null && !q.isEmpty()) notifier.notify(q.peek(), "'" + l.copy().book().title() + "' is available for you");
            return fines.fine(l.due(), today);
        }
        void reserve(Member m, String isbn) { reservations.computeIfAbsent(isbn, k -> new ArrayDeque<>()).add(m); }
    }

    public static void main(String[] args) {
        Library lib = new Library(new PerDayFine(), (m, msg) -> System.out.println("notify " + m.name() + ": " + msg));
        Book ddia = new Book("978-1449373320", "Designing Data-Intensive Applications");
        lib.addCopies(ddia, 1);
        Member asha = new Member("m1", "Asha"), ravi = new Member("m2", "Ravi");
        LocalDate d = LocalDate.of(2026, 11, 1);
        Loan l = lib.borrow(asha, ddia.isbn(), d);
        try { lib.borrow(ravi, ddia.isbn(), d); } catch (IllegalStateException e) { System.out.println(e.getMessage()); lib.reserve(ravi, ddia.isbn()); }
        System.out.println("fine = Rs " + lib.giveBack(l.copy().id(), d.plusDays(17)));    // 3 days late
        System.out.println(lib.borrow(ravi, ddia.isbn(), d.plusDays(18)).member().name() + " borrowed it");
    }
}
""",
  ["Search by title/author (index or search service)", "Persist with repositories; concurrency for multiple librarians", "Different member tiers with different limits (Strategy)"]),

L("snakeladder-lld", "Design Snake and Ladder", "Basic",
  ["Flipkart", "Microsoft", "Amazon"],
  ["Board of 100 cells with snakes and ladders", "2+ players take turns rolling a die", "Exact roll needed to reach 100; first to 100 wins"],
  ["Board (jumps map)", "Player", "Dice (interface for testability)", "Game (turn queue)"],
  ["Dependency injection for the dice (deterministic tests)", "Queue for turns"],
  r"""
import java.util.*;

public class SnakeLadderDemo {
    interface Dice { int roll(); }
    record Player(String name) {}

    static final class Board {
        final int size; final Map<Integer, Integer> jumps = new HashMap<>();   // snake head->tail, ladder bottom->top
        Board(int size) { this.size = size; }
        Board snake(int head, int tail) { if (tail >= head) throw new IllegalArgumentException(); jumps.put(head, tail); return this; }
        Board ladder(int bottom, int top) { if (top <= bottom) throw new IllegalArgumentException(); jumps.put(bottom, top); return this; }
        int land(int pos) { return jumps.getOrDefault(pos, pos); }
    }

    static final class Game {
        final Board board; final Dice dice; final Deque<Player> turns; final Map<Player, Integer> pos = new HashMap<>();
        Game(Board b, Dice d, List<Player> players) { board = b; dice = d; turns = new ArrayDeque<>(players); players.forEach(p -> pos.put(p, 0)); }
        Player play() {
            while (true) {
                Player p = turns.poll();
                int r = dice.roll(), from = pos.get(p), to = from + r;
                if (to <= board.size) {
                    int landed = board.land(to);
                    System.out.println(p.name() + " rolls " + r + ": " + from + " -> " + to + (landed != to ? " -> " + landed : ""));
                    pos.put(p, landed);
                    if (landed == board.size) return p;
                } else System.out.println(p.name() + " rolls " + r + ": needs exact roll, stays at " + from);
                turns.add(p);
            }
        }
    }

    public static void main(String[] args) {
        Board b = new Board(30).ladder(3, 22).ladder(5, 8).snake(27, 1).snake(21, 9).ladder(20, 29);
        Random rnd = new Random(42);
        Player w = new Game(b, () -> rnd.nextInt(6) + 1, List.of(new Player("Asha"), new Player("Ravi"))).play();
        System.out.println("Winner: " + w.name());
    }
}
""",
  ["Multiple dice, special rules (six gives another turn)", "Validation: no cycles, no jump on the last cell", "Undo moves (Command pattern)"]),

L("tictactoe-lld", "Design Tic-Tac-Toe (N×N)", "Basic",
  ["Microsoft", "Amazon", "Google"],
  ["N×N board, two players X and O", "Detect a win in O(1) per move", "Detect a draw; reject invalid moves"],
  ["Board", "Player", "Game", "Move validation"],
  ["Row/column/diagonal counters for O(1) win check (LeetCode 348)"],
  r"""
public class TicTacToeDemo {
    static final class Game {
        private final int n; private final char[][] g; private final int[] rows, cols; private int diag, anti, moves;
        private char turn = 'X'; private char winner = 0;
        Game(int n) { this.n = n; g = new char[n][n]; rows = new int[n]; cols = new int[n]; }

        char move(int r, int c) {                      // returns winner ('X'/'O'), 'D' for draw, 0 to continue
            if (winner != 0) throw new IllegalStateException("Game over");
            if (r < 0 || c < 0 || r >= n || c >= n || g[r][c] != 0) throw new IllegalArgumentException("Invalid move");
            g[r][c] = turn; moves++;
            int add = turn == 'X' ? 1 : -1;
            rows[r] += add; cols[c] += add;
            if (r == c) diag += add;
            if (r + c == n - 1) anti += add;
            if (Math.abs(rows[r]) == n || Math.abs(cols[c]) == n || Math.abs(diag) == n || Math.abs(anti) == n) winner = turn;
            else if (moves == n * n) winner = 'D';
            turn = turn == 'X' ? 'O' : 'X';
            return winner;
        }
        void print() { for (char[] row : g) { StringBuilder sb = new StringBuilder(); for (char ch : row) sb.append(ch == 0 ? '.' : ch); System.out.println(sb); } }
    }

    public static void main(String[] args) {
        Game game = new Game(3);
        int[][] moves = {{0, 0}, {1, 1}, {0, 1}, {2, 2}, {0, 2}};
        char result = 0;
        for (int[] m : moves) result = game.move(m[0], m[1]);
        game.print();
        System.out.println("Result: " + result);
    }
}
""",
  ["Players as an interface (Human/AI with minimax)", "K-in-a-row on larger boards", "Undo (Command pattern)"]),
]
