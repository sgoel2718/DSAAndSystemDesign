"""Java practice programs: HLD questions 13-24."""
from sd_j_util import J

J("autocomplete-hld", r'''
import java.util.*;

public class AutocompleteSystem {
    // Offline: aggregate query logs -> build a trie with top-k per node -> publish snapshot. Online: prefix lookup + cache.
    static class Node { final Map<Character, Node> kids = new TreeMap<>(); List<Map.Entry<String, Long>> top = List.of(); }
    static Node build(Map<String, Long> counts, int k) {
        Node root = new Node();
        for (var e : counts.entrySet()) { Node n = root; for (char c : e.getKey().toCharArray()) n = n.kids.computeIfAbsent(c, x -> new Node()); }
        fill(root, "", counts, k); return root;
    }
    static List<Map.Entry<String, Long>> fill(Node n, String prefix, Map<String, Long> counts, int k) {
        List<Map.Entry<String, Long>> all = new ArrayList<>();
        if (counts.containsKey(prefix)) all.add(Map.entry(prefix, counts.get(prefix)));
        for (var e : n.kids.entrySet()) all.addAll(fill(e.getValue(), prefix + e.getKey(), counts, k));
        all.sort(Map.Entry.<String, Long>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey()));
        n.top = all.subList(0, Math.min(k, all.size())); return n.top;
    }
    static final Map<String, List<String>> prefixCache = new HashMap<>(); static int trieLookups = 0;
    static List<String> suggest(Node root, String prefix) {
        String p = prefix.toLowerCase().trim();
        if (prefixCache.containsKey(p)) return prefixCache.get(p);
        trieLookups++; Node n = root;
        for (char c : p.toCharArray()) { n = n.kids.get(c); if (n == null) return List.of(); }
        List<String> res = n.top.stream().map(Map.Entry::getKey).toList(); prefixCache.put(p, res); return res;
    }

    public static void main(String[] args) {
        String[] log = {"iphone 16", "iphone 16", "iphone 16 pro", "ipl score", "ipl score", "ipl score", "ipl schedule", "india vs australia", "iphone 16", "ikea", "ipl score"};
        Map<String, Long> counts = new TreeMap<>(); for (String q : log) counts.merge(q, 1L, Long::sum);
        System.out.println("weekly aggregation: " + counts);
        Node v1 = build(counts, 3);
        for (String p : List.of("i", "ip", "iph", "IPL ", "x")) System.out.println("'" + p + "' -> " + suggest(v1, p));
        suggest(v1, "ip"); System.out.println("trie lookups: " + trieLookups + " (repeats served from the prefix cache / CDN)");
        for (int i = 0; i < 6; i++) counts.merge("iphone 17 launch", 1L, Long::sum);           // hourly delta for a trending query
        Node v2 = build(counts, 3); prefixCache.clear();
        System.out.println("after the hourly rebuild, 'iph' -> " + suggest(v2, "iph"));
    }
}
''', ["Filter banned/offensive queries out at build time.",
      "Personalise: merge the global top-3 with the user's own last 3 searches that match the prefix.",
      "Shard the trie by the first character and route each lookup to the right shard map."])

J("youtube-hld", r'''
import java.util.*;
import java.util.concurrent.*;

public class VideoPlatformSystem {
    // Upload -> chunk -> parallel transcode DAG (renditions x chunks) -> manifest -> CDN; view counting buffered.
    record Segment(int index, String rendition) {}

    public static void main(String[] args) throws Exception {
        int durationSec = 60, chunkSec = 6; String[] renditions = {"240p", "480p", "720p", "1080p"};
        int chunks = durationSec / chunkSec;
        ExecutorService workers = Executors.newFixedThreadPool(4);
        List<Future<Segment>> jobs = new ArrayList<>();
        long t0 = System.nanoTime();
        for (int c = 0; c < chunks; c++) for (String r : renditions) { final int ci = c; final String rr = r;
            jobs.add(workers.submit(() -> { Thread.sleep(5); return new Segment(ci, rr); })); }      // each task = encode one chunk at one quality
        Map<String, List<Integer>> done = new TreeMap<>();
        for (Future<Segment> f : jobs) { Segment s = f.get(); done.computeIfAbsent(s.rendition(), k -> new ArrayList<>()).add(s.index()); }
        workers.shutdown();
        System.out.printf("transcoded %d chunks x %d renditions = %d tasks on 4 workers in ~%d ms (sequential would be ~%d ms)%n", chunks, renditions.length, jobs.size(), Math.round((System.nanoTime() - t0) / 1e7) * 10, jobs.size() * 5);
        StringBuilder manifest = new StringBuilder("#EXTM3U\n");
        int[] bw = {400_000, 1_400_000, 2_800_000, 5_000_000};
        for (int i = 0; i < renditions.length; i++) manifest.append("#EXT-X-STREAM-INF:BANDWIDTH=").append(bw[i]).append("\n").append(renditions[i]).append("/index.m3u8\n");
        System.out.print("master playlist (served from CDN):\n" + manifest);
        System.out.println("720p media playlist has " + done.get("720p").size() + " segments: " + done.get("720p").stream().map(i -> "seg" + i + ".ts").limit(3).toList() + " ...");
        Map<String, Long> viewBuffer = new HashMap<>(); long dbWrites = 0;
        for (int i = 0; i < 100_000; i++) { viewBuffer.merge("video:7", 1L, Long::sum); if (i % 20_000 == 19_999) { viewBuffer.clear(); dbWrites++; } }
        System.out.println("100,000 views -> " + dbWrites + " DB writes (buffered counts flushed every 20,000)");
    }
}
''', ["Add a dependency: generate the thumbnail only after the 480p rendition of chunk 0 is done (a DAG edge).",
      "Retry a failed transcode task up to 3 times (make 5% of tasks throw).",
      "Pick the CDN edge for a viewer by city from a `Map<String city, String edge>` and fall back to origin on a miss."])

J("dropbox-hld", r'''
import java.security.MessageDigest;
import java.util.*;

public class FileStorageSyncSystem {
    // Block server (chunk + dedup), metadata server (file -> block list, versions), notification of other devices, conflict copies.
    static final Map<String, byte[]> blocks = new HashMap<>();
    record Version(int no, List<String> blockHashes, String device) {}
    static final Map<String, List<Version>> files = new TreeMap<>();
    static final Map<String, List<String>> notifications = new TreeMap<>();
    static final List<String> devices = List.of("laptop", "phone", "tablet");
    static int uploadedBytes = 0;

    static String hash(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)).substring(0, 8); }
    static List<String> chunk(String content) throws Exception {
        List<String> hs = new ArrayList<>(); byte[] d = content.getBytes();
        for (int i = 0; i < d.length; i += 8) { byte[] c = Arrays.copyOfRange(d, i, Math.min(d.length, i + 8)); String h = hash(c); if (blocks.putIfAbsent(h, c) == null) uploadedBytes += c.length; hs.add(h); }
        return hs;
    }
    static String commit(String device, String path, String content, int baseVersion) throws Exception {
        List<Version> vs = files.computeIfAbsent(path, k -> new ArrayList<>());
        if (baseVersion != vs.size()) { path = path.replace(".", " (" + device + " conflict)."); vs = files.computeIfAbsent(path, k -> new ArrayList<>()); }
        vs.add(new Version(vs.size() + 1, chunk(content), device));
        for (String d : devices) if (!d.equals(device)) notifications.computeIfAbsent(d, k -> new ArrayList<>()).add(path + " v" + vs.size());
        return path + " v" + vs.size();
    }
    static String download(String path, int version) { StringBuilder sb = new StringBuilder(); for (String h : files.get(path).get(version - 1).blockHashes()) sb.append(new String(blocks.get(h))); return sb.toString(); }

    public static void main(String[] args) throws Exception {
        System.out.println("laptop commits " + commit("laptop", "plan.txt", "Day1: arrays. Day2: strings. Day3: graphs.", 0) + ", uploaded " + uploadedBytes + " bytes");
        int before = uploadedBytes;
        System.out.println("laptop commits " + commit("laptop", "plan.txt", "Day1: arrays. Day2: hashing. Day3: graphs.", 1) + ", uploaded " + (uploadedBytes - before) + " bytes (only changed chunks)");
        System.out.println("phone (offline, based on v1) commits " + commit("phone", "plan.txt", "Day1: arrays. Day2: strings. Day3: DP!!!", 1));
        System.out.println("pending notifications: " + notifications);
        System.out.println("tablet downloads plan.txt v2: '" + download("plan.txt", 2) + "'");
        System.out.println("restore plan.txt v1: '" + download("plan.txt", 1) + "'");
    }
}
''', ["Make the tablet download only blocks it doesn't already have from v1.",
      "Add sharing: a `Map<path, Set<user>>` ACL checked on download.",
      "Add a quota per user (e.g. 100 bytes) counting only unique blocks they own."])

J("proximity-hld", r'''
import java.util.*;

public class ProximityServiceSystem {
    // Businesses indexed by geohash prefix (read-heavy, rarely updated); search = rider cell + 8 neighbours, then exact distance + rating sort.
    record Business(String name, double lat, double lon, double rating) {}
    static final String B32 = "0123456789bcdefghjkmnpqrstuvwxyz";
    static String geohash(double lat, double lon, int len) {
        double[] la = {-90, 90}, lo = {-180, 180}; StringBuilder sb = new StringBuilder(); boolean even = true; int bits = 0, ch = 0;
        while (sb.length() < len) { double[] r = even ? lo : la; double v = even ? lon : lat, mid = (r[0] + r[1]) / 2; if (v >= mid) { ch = ch * 2 + 1; r[0] = mid; } else { ch *= 2; r[1] = mid; } even = !even; if (++bits == 5) { sb.append(B32.charAt(ch)); bits = 0; ch = 0; } }
        return sb.toString();
    }
    static double km(double a, double b, double c, double d) { double x = Math.toRadians(d - b) * Math.cos(Math.toRadians((a + c) / 2)), y = Math.toRadians(c - a); return Math.sqrt(x * x + y * y) * 6371; }
    static List<String> neighbours(double lat, double lon, int len) {
        double dLat = 180 / Math.pow(2, Math.floor(len * 5 / 2.0)), dLon = 360 / Math.pow(2, Math.ceil(len * 5 / 2.0));
        Set<String> out = new TreeSet<>(); for (int i = -1; i <= 1; i++) for (int j = -1; j <= 1; j++) out.add(geohash(lat + i * dLat, lon + j * dLon, len));
        return new ArrayList<>(out);
    }

    public static void main(String[] args) {
        List<Business> all = List.of(new Business("Vaishali", 18.5204, 73.8418, 4.5), new Business("Goodluck Cafe", 18.5178, 73.8414, 4.3),
            new Business("Cafe Paashh", 18.5367, 73.8930, 4.6), new Business("Le Plaisir", 18.5196, 73.8364, 4.7), new Business("Mumbai Bistro", 19.0760, 72.8777, 4.2));
        Map<String, List<Business>> index = new TreeMap<>(); for (Business b : all) index.computeIfAbsent(geohash(b.lat(), b.lon(), 5), k -> new ArrayList<>()).add(b);
        double lat = 18.5190, lon = 73.8400, radiusKm = 2;
        List<String> cells = neighbours(lat, lon, 5);
        System.out.println("user cell " + geohash(lat, lon, 5) + ", searching 9 cells " + cells);
        List<Business> cand = new ArrayList<>(); for (String c : cells) cand.addAll(index.getOrDefault(c, List.of()));
        System.out.println("candidates from index: " + cand.size() + " of " + all.size() + " businesses");
        cand.stream().filter(b -> km(lat, lon, b.lat(), b.lon()) <= radiusKm)
            .sorted(Comparator.comparingDouble(Business::rating).reversed())
            .forEach(b -> System.out.printf("  %-14s %.2f km  rating %.1f%n", b.name(), km(lat, lon, b.lat(), b.lon()), b.rating()));
    }
}
''', ["Grow the search: if fewer than 3 results are found, retry with geohash length 4 (bigger cells).",
      "Load 100,000 random businesses around Pune and time the indexed search vs scanning all.",
      "Add an 'open now' filter using opening hours stored per business."])

J("uber-hld", r'''
import java.util.*;

public class RideHailingSystem {
    // Drivers send location every few seconds -> in-memory geo index; matching offers the ride to the nearest available
    // driver with a timeout; trip state machine; surge from demand/supply per cell.
    enum TripState { REQUESTED, ACCEPTED, ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED }
    record Driver(String id, double lat, double lon, boolean available) {}
    static final Map<String, Driver> drivers = new TreeMap<>();
    static double dist(double a, double b, double c, double d) { return Math.hypot(a - c, (b - d) * Math.cos(Math.toRadians(a))) * 111; }
    static String cell(double lat, double lon) { return String.format("%.2f,%.2f", Math.floor(lat * 50) / 50, Math.floor(lon * 50) / 50); }

    static void heartbeat(String id, double lat, double lon, boolean avail) { drivers.put(id, new Driver(id, lat, lon, avail)); }

    public static void main(String[] args) {
        heartbeat("d1", 18.520, 73.856, true); heartbeat("d2", 18.522, 73.860, true); heartbeat("d3", 18.540, 73.880, true); heartbeat("d4", 18.521, 73.857, false);
        double rLat = 18.5205, rLon = 73.8565;
        Set<String> declined = Set.of("d1");                                           // d1 ignores the offer (timeout)
        List<Driver> nearby = drivers.values().stream().filter(Driver::available).sorted(Comparator.comparingDouble(d -> dist(rLat, rLon, d.lat(), d.lon()))).toList();
        System.out.println("nearby available drivers: " + nearby.stream().map(d -> String.format("%s(%.2f km)", d.id(), dist(rLat, rLon, d.lat(), d.lon()))).toList());
        String assigned = null;
        for (Driver d : nearby) {
            System.out.print("offer to " + d.id() + " (15 s timeout) -> ");
            if (declined.contains(d.id())) { System.out.println("no response"); continue; }
            System.out.println("accepted"); assigned = d.id(); break;
        }
        heartbeat(assigned, drivers.get(assigned).lat(), drivers.get(assigned).lon(), false);   // lock driver: no double assignment
        TripState s = TripState.REQUESTED; StringBuilder path = new StringBuilder(s.name());
        for (TripState next : List.of(TripState.ACCEPTED, TripState.ARRIVED, TripState.IN_PROGRESS, TripState.COMPLETED)) { s = next; path.append(" -> ").append(s); }
        System.out.println("trip " + path);
        Map<String, int[]> demandSupply = new TreeMap<>();
        for (Driver d : drivers.values()) if (d.available()) demandSupply.computeIfAbsent(cell(d.lat(), d.lon()), k -> new int[2])[1]++;
        for (int i = 0; i < 9; i++) demandSupply.computeIfAbsent(cell(rLat, rLon), k -> new int[2])[0]++;
        demandSupply.forEach((c, ds) -> System.out.printf("cell %s: %d requests / %d drivers -> surge x%.1f%n", c, ds[0], ds[1], Math.min(3.0, Math.max(1.0, ds[0] / Math.max(1.0, ds[1]) / 2))));
    }
}
''', ["Add ETA: assume 25 km/h and print the pickup ETA for the assigned driver.",
      "Store driver locations in a geohash-keyed map and query only the rider's cell + neighbours.",
      "Reject illegal trip transitions (e.g. COMPLETED -> IN_PROGRESS) with an `EnumMap` of allowed next states."])

J("ticketmaster-hld", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class SeatBookingSystem {
    // Seat holds with TTL (atomic compare-and-set per seat), payment confirms, expired holds released, virtual waiting room.
    enum SeatState { FREE, HELD, BOOKED }
    record Seat(SeatState state, String user, long holdUntil) {}
    static final ConcurrentHashMap<String, Seat> seats = new ConcurrentHashMap<>();

    static boolean hold(String seat, String user, long now) {
        Seat[] result = new Seat[1];
        seats.compute(seat, (k, s) -> {
            boolean free = s.state() == SeatState.FREE || (s.state() == SeatState.HELD && s.holdUntil() <= now);
            result[0] = free ? new Seat(SeatState.HELD, user, now + 600) : s; return result[0];
        });
        return user.equals(result[0].user()) && result[0].state() == SeatState.HELD;
    }
    static boolean confirm(String seat, String user, long now) {
        Seat s = seats.get(seat);
        if (s.state() != SeatState.HELD || !s.user().equals(user) || s.holdUntil() <= now) return false;
        return seats.replace(seat, s, new Seat(SeatState.BOOKED, user, 0));
    }

    public static void main(String[] args) throws Exception {
        for (String s : List.of("A1", "A2", "A3")) seats.put(s, new Seat(SeatState.FREE, null, 0));
        ExecutorService pool = Executors.newFixedThreadPool(8); AtomicInteger winners = new AtomicInteger(); List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < 1000; i++) { String u = "user" + i; fs.add(pool.submit(() -> { if (hold("A1", u, 0)) winners.incrementAndGet(); })); }
        for (Future<?> f : fs) f.get(); pool.shutdown();
        String holder = seats.get("A1").user();
        System.out.println("1,000 users try to hold A1 at once -> holds granted: " + winners.get() + " (to " + holder + ")");
        System.out.println(holder + " pays at t=300 -> confirmed: " + confirm("A1", holder, 300));
        System.out.println("asha holds A2 at t=0 -> " + hold("A2", "asha", 0) + "; ravi tries A2 at t=100 -> " + hold("A2", "ravi", 100));
        System.out.println("asha never pays; ravi tries A2 at t=700 (hold expired) -> " + hold("A2", "ravi", 700));
        System.out.println("asha tries to pay at t=710 -> " + confirm("A2", "asha", 710) + " (hold lost)");
        Deque<String> waitingRoom = new ArrayDeque<>(); for (int i = 0; i < 6; i++) waitingRoom.add("fan" + i);
        List<String> admitted = new ArrayList<>(); while (admitted.size() < 2) admitted.add(waitingRoom.poll());
        System.out.println("waiting room admits " + admitted + " to the seat map; " + waitingRoom.size() + " still queued");
        System.out.println("seats: " + new TreeMap<>(seats));
    }
}
''', ["Let a user hold up to 4 seats atomically: all or none (roll back partial holds).",
      "Run a cleanup task that sets expired HELD seats back to FREE so the seat map shows them as available.",
      "Admit users from the waiting room at a fixed rate (e.g. 2 every 10 seconds) based on how many seats are left."])

J("ecommerce-hld", r'''
import java.util.*;

public class EcommerceCheckoutSystem {
    // Cart -> price & tax -> reserve inventory -> payment (idempotent) -> order -> outbox events, with compensation on failure.
    record Line(String sku, int qty) {}
    static final Map<String, Integer> priceRs = Map.of("shoes", 2499, "socks", 199, "watch", 15999);
    static final Map<String, Integer> stock = new TreeMap<>(Map.of("shoes", 5, "socks", 1, "watch", 2));
    static final List<String> outbox = new ArrayList<>(); static final Map<String, String> paymentsByKey = new HashMap<>();
    static int orderSeq = 0;

    static String checkout(String user, List<Line> cart, String idemKey, boolean cardDeclines) {
        int subtotal = cart.stream().mapToInt(l -> priceRs.get(l.sku()) * l.qty()).sum(), gst = subtotal * 18 / 100, total = subtotal + gst;
        List<Line> reserved = new ArrayList<>();
        for (Line l : cart) {                                                      // reserve atomically per SKU (UPDATE ... WHERE stock >= qty)
            if (stock.get(l.sku()) < l.qty()) { reserved.forEach(r -> stock.merge(r.sku(), r.qty(), Integer::sum)); return "FAILED: " + l.sku() + " out of stock (released " + reserved.size() + " reservation(s))"; }
            stock.merge(l.sku(), -l.qty(), Integer::sum); reserved.add(l);
        }
        String payment = paymentsByKey.computeIfAbsent(idemKey, k -> cardDeclines ? "DECLINED" : "pay_" + k);
        if (payment.equals("DECLINED")) { reserved.forEach(r -> stock.merge(r.sku(), r.qty(), Integer::sum)); paymentsByKey.remove(idemKey); return "FAILED: card declined, inventory released"; }
        String orderId = "OD" + (++orderSeq);
        outbox.add("OrderPlaced{" + orderId + ", user=" + user + ", total=" + total + "}");   // same transaction as the order row
        return String.format("OK %s subtotal %d + GST %d = Rs %d, payment %s", orderId, subtotal, gst, total, payment);
    }

    public static void main(String[] args) {
        System.out.println(checkout("asha", List.of(new Line("shoes", 1), new Line("socks", 1)), "k1", false));
        System.out.println(checkout("ravi", List.of(new Line("shoes", 1), new Line("socks", 1)), "k2", false));
        System.out.println(checkout("zoya", List.of(new Line("watch", 1)), "k3", true));
        System.out.println(checkout("zoya", List.of(new Line("watch", 1)), "k4", false));
        System.out.println("stock now " + stock);
        System.out.println("outbox events for email/warehouse/analytics: " + outbox);
    }
}
''', ["Add coupons: `FLAT200` and `10PCT` (max Rs 500) applied before GST.",
      "Retry the same checkout with key k1 and make it return the original order instead of creating a second one.",
      "Split inventory across 2 warehouses and reserve from the one nearest to the user's pincode."])

J("payment-hld", r'''
import java.util.*;

public class PaymentSystem {
    // Payment intent state machine, idempotent API, PSP call with timeout + status polling, double-entry ledger, reconciliation.
    enum State { CREATED, PROCESSING, SUCCEEDED, FAILED }
    record Intent(String id, long amountPaise, State state, String pspRef) {}
    static final Map<String, Intent> intents = new TreeMap<>(); static final Map<String, String> idem = new HashMap<>();
    static final List<String> ledger = new ArrayList<>(); static final Map<String, String> pspSide = new HashMap<>();
    static int seq = 0;

    static Intent create(String key, long amount) { String id = idem.computeIfAbsent(key, k -> "pi_" + (++seq)); intents.putIfAbsent(id, new Intent(id, amount, State.CREATED, null)); return intents.get(id); }
    static Intent pay(String id, boolean pspTimesOut) {
        Intent i = intents.get(id); if (i.state() != State.CREATED) return i;           // idempotent: no second charge
        intents.put(id, new Intent(id, i.amountPaise(), State.PROCESSING, null));
        String ref = "psp_" + id; pspSide.put(ref, "CAPTURED");                         // PSP actually charged the card
        if (pspTimesOut) return intents.get(id);                                         // ...but our call timed out: stay PROCESSING
        return succeed(id, ref);
    }
    static Intent succeed(String id, String ref) {
        Intent i = intents.get(id); intents.put(id, new Intent(id, i.amountPaise(), State.SUCCEEDED, ref));
        ledger.add(id + " DEBIT customer " + i.amountPaise()); ledger.add(id + " CREDIT merchant " + i.amountPaise());
        return intents.get(id);
    }
    static void pollStuck() { intents.values().stream().filter(i -> i.state() == State.PROCESSING).toList().forEach(i -> { String ref = "psp_" + i.id(); if ("CAPTURED".equals(pspSide.get(ref))) { System.out.println("  poller: PSP says " + ref + " captured -> mark SUCCEEDED"); succeed(i.id(), ref); } }); }

    public static void main(String[] args) {
        Intent a = create("order-987", 2_499_00); System.out.println("create  -> " + a);
        System.out.println("create again (same key) -> " + create("order-987", 2_499_00).id() + " (same intent)");
        System.out.println("pay     -> " + pay(a.id(), false));
        System.out.println("pay again -> " + pay(a.id(), false).state() + " (no second charge)");
        Intent b = create("order-988", 999_00);
        System.out.println("pay with PSP timeout -> " + pay(b.id(), true).state() + " (unknown outcome: do NOT retry blindly)");
        pollStuck();
        System.out.println("ledger: " + ledger);
        long ourTotal = intents.values().stream().filter(i -> i.state() == State.SUCCEEDED).mapToLong(Intent::amountPaise).sum();
        System.out.println("reconciliation: our captured total " + ourTotal + " vs PSP captured count " + pspSide.size() + " -> " + (pspSide.size() == intents.values().stream().filter(i -> i.state() == State.SUCCEEDED).count() ? "match" : "MISMATCH"));
    }
}
''', ["Add refunds: a REFUNDED state, a reversing ledger entry, and refusing to refund more than was captured.",
      "Add webhooks: the PSP calls you back; make the handler idempotent because webhooks can arrive twice.",
      "Add a FAILED path where the poller finds the PSP never captured, and release the order."])

J("hotel-hld", r'''
import java.util.*;

public class HotelReservationSystem {
    // Inventory per (room type, night) with optimistic versions; a booking reserves every night or none; overbooking allowance.
    record Key(String roomType, int night) {}
    static final class Inv { int total, reserved, version; Inv(int t) { total = t; } }
    static final Map<Key, Inv> inventory = new TreeMap<>(Comparator.comparing(Key::roomType).thenComparingInt(Key::night));
    static final double OVERBOOK = 1.10;

    static String book(String guest, String type, int checkIn, int checkOut, int rooms) {
        Map<Key, Integer> seen = new HashMap<>();
        for (int n = checkIn; n < checkOut; n++) {                                         // read phase: check every night
            Inv inv = inventory.get(new Key(type, n));
            if (inv.reserved + rooms > Math.floor(inv.total * OVERBOOK)) return guest + ": SOLD OUT on night " + n;
            seen.put(new Key(type, n), inv.version);
        }
        for (var e : seen.entrySet()) if (inventory.get(e.getKey()).version != e.getValue()) return guest + ": conflict, retry";   // optimistic check
        for (Key k : seen.keySet()) { Inv inv = inventory.get(k); inv.reserved += rooms; inv.version++; }                     // write phase (one transaction)
        return guest + ": BOOKED " + rooms + " x " + type + " nights " + checkIn + "-" + (checkOut - 1);
    }

    public static void main(String[] args) {
        for (int night = 1; night <= 5; night++) { inventory.put(new Key("deluxe", night), new Inv(10)); inventory.put(new Key("suite", night), new Inv(2)); }
        System.out.println(book("asha", "suite", 1, 4, 1));
        System.out.println(book("ravi", "suite", 2, 3, 1));
        System.out.println(book("zoya", "suite", 3, 5, 1) + " (2 rooms x 1.10 overbooking = 2)");
        System.out.println(book("kiran", "deluxe", 1, 3, 11) + " (10 x 1.10 = 11 allowed)");
        System.out.println(book("meera", "deluxe", 2, 3, 1));
        inventory.forEach((k, v) -> { if (k.roomType().equals("suite")) System.out.println("  suite night " + k.night() + ": reserved " + v.reserved + "/" + v.total); });
    }
}
''', ["Add cancellation that decrements every night of the booking.",
      "Run 50 concurrent bookings for the last suite with threads and make the optimistic check actually retry.",
      "Add dynamic pricing: price per night = base × (1 + reserved/total)."])

J("metrics-hld", r'''
import java.util.*;

public class MetricsMonitoringSystem {
    // Agents push samples -> time-series store (series = name+labels) -> rollups -> rule evaluation with 'for' duration -> alerts.
    record Sample(String metric, Map<String, String> labels, long ts, double value) {}
    static final Map<String, TreeMap<Long, Double>> tsdb = new TreeMap<>();

    static String seriesKey(String m, Map<String, String> l) { return m + new TreeMap<>(l); }
    static void ingest(Sample s) { tsdb.computeIfAbsent(seriesKey(s.metric(), s.labels()), k -> new TreeMap<>()).put(s.ts(), s.value()); }
    static double avgOver(String key, long from, long to) { return tsdb.get(key).subMap(from, true, to, true).values().stream().mapToDouble(d -> d).average().orElse(Double.NaN); }

    public static void main(String[] args) {
        Random r = new Random(5);
        for (long t = 0; t < 600; t += 10) {
            for (String host : List.of("web-1", "web-2")) {
                double cpu = host.equals("web-2") && t >= 300 ? 92 + r.nextInt(6) : 40 + r.nextInt(20);
                ingest(new Sample("cpu_percent", Map.of("host", host, "env", "prod"), t, cpu));
            }
        }
        System.out.println("series stored: " + tsdb.keySet());
        String w2 = seriesKey("cpu_percent", Map.of("host", "web-2", "env", "prod"));
        for (long m = 0; m < 600; m += 60) System.out.printf("  1-min rollup web-2 minute %d: %.1f%%%n", m / 60, avgOver(w2, m, m + 59));
        // Rule: avg(cpu over 1 min) > 90 for 2 consecutive evaluations -> FIRING
        String state = "OK"; int pendingFor = 0;
        for (long now = 60; now <= 600; now += 60) {
            boolean breach = avgOver(w2, now - 60, now) > 90;
            pendingFor = breach ? pendingFor + 1 : 0;
            String next = pendingFor == 0 ? "OK" : pendingFor < 2 ? "PENDING" : "FIRING";
            if (!next.equals(state)) System.out.println("t=" + now + " alert HighCPU web-2: " + state + " -> " + next + (next.equals("FIRING") ? "  (page on-call)" : ""));
            state = next;
        }
        System.out.printf("cardinality: %d series; adding a per-request label like user_id would create millions%n", tsdb.size());
    }
}
''', ["Add a p95 query over the raw samples of web-1 for the last 5 minutes.",
      "Downsample: keep raw 10-second points for 2 minutes and only 1-minute rollups for older data; compare memory.",
      "Add alert deduplication and a resolve notification when the alert goes back to OK."])

J("logging-hld", r'''
import java.util.*;
import java.util.regex.*;

public class LoggingSystem {
    // Apps emit structured logs -> agent batches -> Kafka-like buffer -> indexer builds an inverted index per day -> search + retention.
    record Log(long ts, String day, String service, String level, String traceId, String msg) {}
    static final List<Log> buffer = new ArrayList<>();
    static final Map<String, List<Log>> dailyIndices = new TreeMap<>();
    static final Map<String, Map<String, Set<Integer>>> inverted = new TreeMap<>();

    static void index(Log l) {
        List<Log> docs = dailyIndices.computeIfAbsent("logs-" + l.day(), k -> new ArrayList<>()); docs.add(l); int docId = docs.size() - 1;
        Map<String, Set<Integer>> inv = inverted.computeIfAbsent("logs-" + l.day(), k -> new HashMap<>());
        for (String tok : (l.service() + " " + l.level() + " " + l.traceId() + " " + l.msg()).toLowerCase().split("\\W+")) inv.computeIfAbsent(tok, k -> new TreeSet<>()).add(docId);
    }
    static List<Log> search(String day, String... terms) {
        Map<String, Set<Integer>> inv = inverted.getOrDefault("logs-" + day, Map.of()); Set<Integer> hits = null;
        for (String t : terms) { Set<Integer> p = inv.getOrDefault(t.toLowerCase(), Set.of()); hits = hits == null ? new TreeSet<>(p) : hits; hits.retainAll(p); }
        return hits == null ? List.of() : hits.stream().map(i -> dailyIndices.get("logs-" + day).get(i)).toList();
    }

    public static void main(String[] args) {
        String[][] raw = {{"11-24", "order", "INFO", "t1", "checkout started user=42"}, {"11-24", "payment", "ERROR", "t1", "psp timeout after 3000ms"},
            {"11-25", "order", "INFO", "t2", "checkout started user=7"}, {"11-25", "payment", "ERROR", "t2", "card declined"}, {"11-26", "payment", "ERROR", "t3", "psp timeout after 3000ms"},
            {"11-26", "order", "WARN", "t3", "retrying payment"}};
        long ts = 0;
        for (String[] r : raw) { buffer.add(new Log(ts++, r[0], r[1], r[2], r[3], r[4])); if (buffer.size() == 3) { buffer.forEach(LoggingSystem::index); System.out.println("agent flushed a batch of 3 -> indexed"); buffer.clear(); } }
        System.out.println("indices: " + dailyIndices.keySet());
        System.out.println("search 11-26 'payment error timeout': " + search("11-26", "payment", "error", "timeout").stream().map(Log::msg).toList());
        System.out.println("all logs for trace t3: " + search("11-26", "t3").stream().map(l -> l.service() + ":" + l.msg()).toList());
        String cutoff = "11-25"; dailyIndices.keySet().removeIf(k -> k.compareTo("logs-" + cutoff) < 0); inverted.keySet().removeIf(k -> k.compareTo("logs-" + cutoff) < 0);
        System.out.println("retention (keep 2 days): indices now " + dailyIndices.keySet() + " (dropping a whole day is instant)");
    }
}
''', ["Add sampling: keep 100% of ERROR logs but only 10% of INFO logs.",
      "Add a time-range filter and an aggregation 'errors per service per day'.",
      "Mask PII before indexing: replace anything like `user=\\d+` with `user=***`."])

J("topk-hld", r'''
import java.util.*;

public class TopKTrendingSystem {
    // Count-Min Sketch for approximate counts in bounded memory + a min-heap of the top K, per time window; exact recount offline.
    static class CountMinSketch {
        final int w, d; final int[][] t; final int[] seeds;
        CountMinSketch(int w, int d) { this.w = w; this.d = d; t = new int[d][w]; seeds = new int[d]; Random r = new Random(3); for (int i = 0; i < d; i++) seeds[i] = r.nextInt() | 1; }
        int idx(String k, int i) { int h = k.hashCode() * seeds[i]; h ^= h >>> 15; return Math.floorMod(h, w); }
        void add(String k) { for (int i = 0; i < d; i++) t[i][idx(k, i)]++; }
        int estimate(String k) { int m = Integer.MAX_VALUE; for (int i = 0; i < d; i++) m = Math.min(m, t[i][idx(k, i)]); return m; }
    }

    public static void main(String[] args) {
        CountMinSketch cms = new CountMinSketch(1000, 4); Map<String, Integer> exact = new HashMap<>();
        PriorityQueue<Map.Entry<String, Integer>> heap = new PriorityQueue<>(Map.Entry.comparingByValue()); Map<String, Map.Entry<String, Integer>> inHeap = new HashMap<>();
        Random r = new Random(9); int K = 3;
        for (int i = 0; i < 200_000; i++) {
            String video = "v" + (int) Math.floor(Math.pow(r.nextDouble(), 4) * 50_000);              // skewed popularity
            cms.add(video); exact.merge(video, 1, Integer::sum);
            int est = cms.estimate(video);
            if (inHeap.containsKey(video)) { heap.remove(inHeap.get(video)); }
            else if (heap.size() == K && est <= heap.peek().getValue()) continue;
            else if (heap.size() == K) inHeap.remove(heap.poll().getKey());
            Map.Entry<String, Integer> e = Map.entry(video, est); heap.add(e); inHeap.put(video, e);
        }
        List<Map.Entry<String, Integer>> top = new ArrayList<>(heap); top.sort(Map.Entry.<String, Integer>comparingByValue().reversed());
        System.out.println("approx top-" + K + " (Count-Min + heap): " + top);
        System.out.println("exact top-" + K + "                  : " + exact.entrySet().stream().sorted(Map.Entry.<String, Integer>comparingByValue().reversed()).limit(K).toList());
        System.out.printf("memory: sketch %,d counters vs exact map %,d keys%n", 1000 * 4, exact.size());
        String rare = exact.entrySet().stream().filter(e -> e.getValue() == 1).findFirst().get().getKey();
        System.out.println("a rare video " + rare + ": exact 1, sketch estimate " + cms.estimate(rare) + " (only over-estimates, never under)");
    }
}
''', ["Keep one sketch per minute and merge the last 5 for a sliding 5-minute trending list.",
      "Partition by video id across 3 'counter' nodes and merge their top-k lists into a global top-k.",
      "Change the sketch width to 100 and 10,000 and print how the rare-video error changes."])
