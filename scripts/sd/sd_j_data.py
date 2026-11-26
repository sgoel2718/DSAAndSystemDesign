"""Java practice programs: Databases & Storage tab."""
from sd_j_util import J

J("sql-vs-nosql", r'''
import java.util.*;
import java.util.stream.*;

public class SqlVsNoSqlDemo {
    // Relational: normalised tables joined at read time. Document: one denormalised record per order.
    record Customer(int id, String name) {}
    record OrderRow(int id, int customerId, String status) {}
    record ItemRow(int orderId, String product, int qty, int price) {}

    public static void main(String[] args) {
        List<Customer> customers = List.of(new Customer(42, "Asha"), new Customer(7, "Ravi"));
        List<OrderRow> orders = List.of(new OrderRow(987, 42, "PAID"), new OrderRow(988, 7, "PENDING"));
        List<ItemRow> items = List.of(new ItemRow(987, "Shoes", 1, 2499), new ItemRow(987, "Socks", 3, 199), new ItemRow(988, "Cap", 1, 399));
        // SQL-style: SELECT ... FROM orders JOIN customers JOIN order_items WHERE orders.id = 987
        OrderRow o = orders.stream().filter(x -> x.id() == 987).findFirst().get();
        Customer c = customers.stream().filter(x -> x.id() == o.customerId()).findFirst().get();
        List<ItemRow> its = items.stream().filter(x -> x.orderId() == 987).toList();
        System.out.println("SQL join (3 tables): order " + o.id() + " by " + c.name() + " items " + its.stream().map(ItemRow::product).toList());
        // Document-style: everything the page needs in one record, fetched by key
        Map<Integer, Map<String, Object>> docs = new HashMap<>();
        for (OrderRow or : orders) {
            Customer cu = customers.stream().filter(x -> x.id() == or.customerId()).findFirst().get();
            docs.put(or.id(), Map.of("status", or.status(), "customer", Map.of("id", cu.id(), "name", cu.name()),
                "items", items.stream().filter(i -> i.orderId() == or.id()).map(i -> Map.of("product", i.product(), "qty", i.qty())).toList()));
        }
        System.out.println("Document get(987)  : " + docs.get(987));
        // The trade-off: Asha renames herself
        customers = List.of(new Customer(42, "Asha K"), new Customer(7, "Ravi"));
        System.out.println("\nAfter rename -> SQL reads the new name from one row: " + customers.get(0).name());
        System.out.println("Document still has the copied old name: " + ((Map<?, ?>) docs.get(987).get("customer")).get("name") + " (must update every copy)");
        int revenue = items.stream().mapToInt(i -> i.qty() * i.price()).sum();
        System.out.println("Ad-hoc report (SUM over all items) is easy in SQL: total revenue = " + revenue);
    }
}
''', ["Add a query 'all orders containing Socks' and compare how you'd do it in each model.",
      "Store the document as JSON text using a `StringBuilder` and measure its size vs the 3 rows.",
      "Write a function that fixes the stale customer name in every document (the denormalisation cost)."])

J("acid", r'''
import java.util.*;

public class AcidDemo {
    // A tiny database with a write-ahead log (WAL): transactions are atomic and survive a crash.
    static Map<String, Integer> data = new HashMap<>(Map.of("asha", 1000, "ravi", 200));
    static final List<String> wal = new ArrayList<>();                 // pretend this is fsync'd to disk

    static void transfer(String txId, String from, String to, int amt, boolean crashMidway) {
        Map<String, Integer> pending = new HashMap<>();
        if (data.get(from) - amt < 0) { System.out.println(txId + ": ROLLBACK, balance would go negative (Consistency)"); return; }
        pending.put(from, data.get(from) - amt);
        wal.add(txId + " SET " + from + "=" + pending.get(from));
        if (crashMidway) { System.out.println(txId + ": CRASH after debit was logged, before COMMIT"); return; }
        pending.put(to, data.get(to) + amt);
        wal.add(txId + " SET " + to + "=" + pending.get(to));
        wal.add(txId + " COMMIT");
        data.putAll(pending);                                           // apply only after COMMIT is durable
        System.out.println(txId + ": COMMIT " + from + " -> " + to + " " + amt + "  balances " + new TreeMap<>(data));
    }

    static Map<String, Integer> recoverFromWal(Map<String, Integer> snapshot) {
        Set<String> committed = new HashSet<>();
        for (String e : wal) if (e.endsWith("COMMIT")) committed.add(e.split(" ")[0]);
        Map<String, Integer> db = new HashMap<>(snapshot);
        for (String e : wal) {
            String[] p = e.split(" ");
            if (p[1].equals("SET") && committed.contains(p[0])) { String[] kv = p[2].split("="); db.put(kv[0], Integer.parseInt(kv[1])); }
        }
        return db;
    }

    public static void main(String[] args) {
        Map<String, Integer> snapshot = new HashMap<>(data);
        transfer("tx1", "asha", "ravi", 500, false);
        transfer("tx2", "ravi", "asha", 100, true);
        transfer("tx3", "ravi", "asha", 5000, false);
        System.out.println("\nWAL: " + wal);
        Map<String, Integer> recovered = recoverFromWal(snapshot);
        System.out.println("after restart, replay committed WAL entries -> " + new TreeMap<>(recovered));
        System.out.println("tx2's half-done debit was ignored (Atomicity); tx1 survived the crash (Durability).");
        System.out.println("total money before " + (1000 + 200) + ", after " + recovered.values().stream().mapToInt(i -> i).sum());
    }
}
''', ["Add Isolation: make `transfer` `synchronized` and run 100 random transfers from 4 threads; check the total stays 1,200.",
      "Add checkpointing: after recovery, save a new snapshot and truncate the WAL.",
      "Add a `CHECK balance >= 0` constraint table and enforce it generically before COMMIT."])

J("isolation-levels", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class IsolationDemo {
    // Lost update: two threads do read-modify-write on the same balance. Then three fixes.
    static int balance;
    static final Object lock = new Object();
    static final AtomicInteger atomicBalance = new AtomicInteger();
    static final AtomicLong versioned = new AtomicLong();                      // high 32 bits: version, low 32: value

    static int run(String mode) throws Exception {
        balance = 1000; atomicBalance.set(1000); versioned.set(1000);
        ExecutorService pool = Executors.newFixedThreadPool(8);
        CountDownLatch go = new CountDownLatch(1);
        List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < 100; i++) fs.add(pool.submit(() -> {
            go.await();
            switch (mode) {
                case "no isolation" -> { int read = balance; Thread.onSpinWait(); Thread.yield(); balance = read - 5; }
                case "pessimistic lock (SELECT FOR UPDATE)" -> { synchronized (lock) { int read = balance; balance = read - 5; } }
                case "atomic UPDATE balance = balance - 5" -> atomicBalance.addAndGet(-5);
                case "optimistic (WHERE version = v)" -> {
                    while (true) {
                        long cur = versioned.get(); int ver = (int) (cur >>> 32), val = (int) cur;
                        long next = ((long) (ver + 1) << 32) | (val - 5);
                        if (versioned.compareAndSet(cur, next)) break;          // 0 rows updated -> retry
                    }
                }
            }
            return null;
        }));
        go.countDown();
        for (Future<?> f : fs) f.get();
        pool.shutdown();
        return switch (mode) { case "atomic UPDATE balance = balance - 5" -> atomicBalance.get(); case "optimistic (WHERE version = v)" -> (int) versioned.get(); default -> balance; };
    }

    public static void main(String[] args) throws Exception {
        System.out.println("100 withdrawals of 5 from 1000 -> expected 500");
        for (String m : List.of("no isolation", "pessimistic lock (SELECT FOR UPDATE)", "atomic UPDATE balance = balance - 5", "optimistic (WHERE version = v)")) {
            int r = run(m);
            System.out.printf("%-38s -> %s%n", m, r == 500 ? "500 ✔" : "wrong (" + (r > 500 ? "lost updates" : "?") + ")");
        }
    }
}
''', ["Reproduce a non-repeatable read: thread A reads the balance twice with a sleep between, thread B updates it in between.",
      "Reproduce write skew: two 'doctors' each check that 2 are on call, then each goes off call. Fix it with one lock over the check.",
      "Count how many retries the optimistic version needed and compare under 2 vs 16 threads."])

J("indexes", r'''
import java.util.*;

public class IndexDemo {
    record User(int id, String email, String country, String city, int age) {}

    public static void main(String[] args) {
        int n = 1_000_000; Random r = new Random(4);
        String[] countries = {"IN", "US", "DE"}, cities = {"Pune", "Delhi", "Austin", "Berlin"};
        List<User> table = new ArrayList<>(n);
        for (int i = 0; i < n; i++) table.add(new User(i, String.format("user%07d@x.com", i), countries[r.nextInt(3)], cities[r.nextInt(4)], 18 + r.nextInt(50)));
        String target = "user0777777@x.com";
        // Full table scan
        int scanned = 0; User found = null;
        for (User u : table) { scanned++; if (u.email().equals(target)) { found = u; break; } }
        System.out.println("full scan     : found id " + found.id() + " after reading " + String.format("%,d", scanned) + " rows");
        // B-tree-like sorted index: TreeMap (red-black tree) email -> row id
        TreeMap<String, Integer> emailIdx = new TreeMap<>();
        for (User u : table) emailIdx.put(u.email(), u.id());
        int depth = (int) Math.ceil(Math.log(n) / Math.log(2));
        System.out.println("tree index    : found id " + emailIdx.get(target) + " in ~" + depth + " comparisons (a B+ tree with fan-out 500 needs ~3 page reads)");
        // Range scan uses the sorted order
        System.out.println("range scan    : emails from 'user0100000' to 'user0100100' -> " + emailIdx.subMap("user0100000", "user0100100").size() + " rows, read in order without scanning the table");
        // Composite index (country, city, age): works for leftmost prefixes
        TreeMap<String, List<Integer>> composite = new TreeMap<>();
        for (User u : table) composite.computeIfAbsent(u.country() + "|" + u.city() + "|" + String.format("%03d", u.age()), k -> new ArrayList<>()).add(u.id());
        int prefixRows = composite.subMap("IN|Pune|", "IN|Pune|~").values().stream().mapToInt(List::size).sum();
        int prefixAge = composite.subMap("IN|Pune|030", "IN|Pune|~").values().stream().mapToInt(List::size).sum();
        System.out.println("composite     : country=IN AND city=Pune -> " + prefixRows + " rows via prefix seek");
        System.out.println("composite     : ... AND age >= 30        -> " + prefixAge + " rows, still a range seek");
        System.out.println("composite     : city=Pune alone can't use it (not a leftmost prefix) -> full scan");
        System.out.println("write cost    : each insert now updates the table + " + 2 + " indexes");
    }
}
''', ["Build a hash index (`HashMap`) on email and explain why it can't answer the range query.",
      "Measure the time of 10,000 inserts with 0, 1 and 2 indexes maintained.",
      "Add a 'covering index' that stores (email -> age) so a query for age needs no table lookup."])

J("storage-engines", r'''
import java.util.*;

public class LsmTreeDemo {
    // A mini LSM tree: writes go to a WAL + sorted memtable; when full it flushes to an immutable SSTable;
    // reads check memtable, then SSTables newest-first (each with a tiny Bloom filter); compaction merges SSTables.
    static class SSTable {
        final TreeMap<String, String> data; final BitSet bloom = new BitSet(64);
        SSTable(TreeMap<String, String> d) { data = d; d.keySet().forEach(k -> { bloom.set(h1(k)); bloom.set(h2(k)); }); }
        boolean mightContain(String k) { return bloom.get(h1(k)) && bloom.get(h2(k)); }
        static int h1(String k) { return Math.floorMod(k.hashCode(), 64); }
        static int h2(String k) { return Math.floorMod(k.hashCode() * 31 + 7, 64); }
    }
    final List<String> wal = new ArrayList<>(); TreeMap<String, String> memtable = new TreeMap<>(); final LinkedList<SSTable> sstables = new LinkedList<>();
    int diskReads = 0;

    void put(String k, String v) {
        wal.add(k + "=" + v); memtable.put(k, v);
        if (memtable.size() >= 3) { sstables.addFirst(new SSTable(memtable)); System.out.println("  flush memtable -> SSTable " + memtable); memtable = new TreeMap<>(); wal.clear(); }
    }
    String get(String k) {
        if (memtable.containsKey(k)) return memtable.get(k);
        for (SSTable s : sstables) { if (!s.mightContain(k)) continue; diskReads++; if (s.data.containsKey(k)) return s.data.get(k); }
        return null;
    }
    void compact() {
        TreeMap<String, String> merged = new TreeMap<>();
        for (Iterator<SSTable> it = sstables.descendingIterator(); it.hasNext(); ) merged.putAll(it.next().data);   // newer overwrite older
        merged.values().removeIf(v -> v.equals("<tombstone>"));
        sstables.clear(); sstables.add(new SSTable(merged));
        System.out.println("  compaction -> 1 SSTable " + merged);
    }

    public static void main(String[] args) {
        LsmTreeDemo db = new LsmTreeDemo();
        String[][] writes = {{"apple", "1"}, {"kiwi", "2"}, {"mango", "3"}, {"apple", "10"}, {"banana", "4"}, {"kiwi", "<tombstone>"}, {"plum", "5"}};
        for (String[] w : writes) { System.out.println("put " + w[0] + "=" + w[1]); db.put(w[0], w[1]); }
        System.out.println("SSTables on disk: " + db.sstables.size() + ", memtable " + db.memtable);
        System.out.println("get apple -> " + db.get("apple") + " (newest version wins)");
        db.diskReads = 0; System.out.println("get grape -> " + db.get("grape") + ", disk reads " + db.diskReads + " (Bloom filters skipped files)");
        db.compact();
        System.out.println("get kiwi  -> " + db.get("kiwi") + " (deleted by tombstone)");
    }
}
''', ["Make flush size 5 and count how many SSTables exist after 50 random writes; then add automatic compaction when there are more than 4.",
      "Measure write amplification: count total bytes written by flush + compaction versus bytes the user wrote.",
      "Replace the TreeMap memtable with a `ConcurrentSkipListMap` and write from 4 threads."])

J("nosql-types", r'''
import java.util.*;

public class NoSqlTypesDemo {
    public static void main(String[] args) {
        // Key-value: opaque value, get by key only
        Map<String, String> kv = new HashMap<>();
        kv.put("session:abc", "{user:42, cart:[sku1]}");
        System.out.println("key-value   GET session:abc -> " + kv.get("session:abc"));
        // Document: nested fields you can query/index
        List<Map<String, Object>> products = List.of(
            Map.of("_id", 1, "name", "Shoes", "tags", List.of("sport", "running"), "price", 2499),
            Map.of("_id", 2, "name", "Kettle", "tags", List.of("home"), "price", 999));
        System.out.println("document    find tags contains 'sport' -> " + products.stream().filter(p -> ((List<?>) p.get("tags")).contains("sport")).map(p -> p.get("name")).toList());
        // Wide-column: partition key -> rows sorted by clustering key (like Cassandra)
        Map<String, TreeMap<Long, String>> messages = new HashMap<>();
        long[] ts = {1005, 1001, 1003, 1010};
        for (long t : ts) messages.computeIfAbsent("chat:42", k -> new TreeMap<>(Comparator.reverseOrder())).put(t, "msg@" + t);
        System.out.println("wide-column chat:42 latest 3 -> " + messages.get("chat:42").values().stream().limit(3).toList() + " (one partition, already sorted)");
        // Graph: adjacency lists + traversal (friends of friends)
        Map<String, List<String>> follows = Map.of("asha", List.of("ravi", "zoya"), "ravi", List.of("meera", "zoya"), "zoya", List.of("kiran"), "meera", List.of(), "kiran", List.of());
        Set<String> fof = new TreeSet<>();
        for (String f : follows.get("asha")) fof.addAll(follows.get(f));
        fof.removeAll(follows.get("asha")); fof.remove("asha");
        System.out.println("graph       people asha may know (2 hops) -> " + fof);
    }
}
''', ["Model 'orders by customer, newest first' in the wide-column style and fetch the latest 2 orders for a customer.",
      "Add a secondary index to the document store (`Map<String tag, List<id>>`) and use it for the tag query.",
      "Find the shortest follow-path between two users with BFS in the graph store."])

J("normalization", r'''
import java.util.*;

public class NormalizationDemo {
    record FlatOrder(int orderId, String customer, String city, String product, int price) {}

    public static void main(String[] args) {
        List<FlatOrder> flat = new ArrayList<>(List.of(new FlatOrder(1, "Asha", "Pune", "Shoes", 2499),
            new FlatOrder(2, "Asha", "Pune", "Socks", 199), new FlatOrder(3, "Ravi", "Delhi", "Shoes", 2499)));
        // Update anomaly: Asha moves; we forget one row
        flat.set(0, new FlatOrder(1, "Asha", "Mumbai", "Shoes", 2499));
        Set<String> ashaCities = new TreeSet<>(); for (FlatOrder f : flat) if (f.customer().equals("Asha")) ashaCities.add(f.city());
        System.out.println("unnormalised: Asha now lives in " + ashaCities + "  <- update anomaly");
        // Delete anomaly: removing order 3 loses the fact that Ravi lives in Delhi
        flat.removeIf(f -> f.orderId() == 3);
        System.out.println("unnormalised: after deleting order 3, do we know Ravi's city? " + flat.stream().anyMatch(f -> f.customer().equals("Ravi")));
        // Normalised (3NF): each fact stored once
        Map<Integer, String[]> customers = new TreeMap<>(Map.of(1, new String[]{"Asha", "Pune"}, 2, new String[]{"Ravi", "Delhi"}));
        Map<Integer, Object[]> products = new TreeMap<>(Map.of(10, new Object[]{"Shoes", 2499}, 11, new Object[]{"Socks", 199}));
        List<int[]> orders = new ArrayList<>(List.of(new int[]{1, 1, 10}, new int[]{2, 1, 11}, new int[]{3, 2, 10}));
        customers.get(1)[1] = "Mumbai";                                    // one update, everywhere consistent
        orders.removeIf(o -> o[0] == 3);
        System.out.println("normalised  : Asha's city " + customers.get(1)[1] + "; Ravi still known: " + customers.get(2)[0] + " in " + customers.get(2)[1]);
        for (int[] o : orders) System.out.println("  join -> order " + o[0] + ": " + customers.get(o[1])[0] + " (" + customers.get(o[1])[1] + ") bought " + products.get(o[2])[0]);
    }
}
''', ["Add an order_items table so one order can have many products (1:N) and print order totals with a join.",
      "Build a denormalised 'order summary' read view from the normalised tables and refresh it after updates.",
      "Find a transitive dependency in a table of (employee, dept, dept_head) and normalise it."])

J("replication", r'''
import java.util.*;

public class ReplicationDemo {
    static class Node { final String name; final Map<String, String> data = new HashMap<>(); long appliedLsn; Node(String n) { name = n; } }
    record LogEntry(long lsn, String key, String value) {}

    static final Node leader = new Node("leader");
    static final List<Node> followers = List.of(new Node("f1"), new Node("f2"));
    static final List<LogEntry> wal = new ArrayList<>();

    static long write(String k, String v) { long lsn = wal.size() + 1; wal.add(new LogEntry(lsn, k, v)); leader.data.put(k, v); leader.appliedLsn = lsn; return lsn; }
    static void replicate(Node f, int maxEntries) {                                  // async shipping of the log
        for (LogEntry e : wal) if (e.lsn() > f.appliedLsn && maxEntries-- > 0) { f.data.put(e.key(), e.value()); f.appliedLsn = e.lsn(); }
    }
    static String read(Node n, String k) { return n.name + "(lsn " + n.appliedLsn + ") " + k + "=" + n.data.get(k); }

    public static void main(String[] args) {
        write("bio", "hello");
        followers.forEach(f -> replicate(f, 10));
        long myWrite = write("bio", "system design fan");
        replicate(followers.get(0), 10);                                            // f2 is lagging
        System.out.println("read after write from f1: " + read(followers.get(0), "bio"));
        System.out.println("read after write from f2: " + read(followers.get(1), "bio") + "  <- replication lag, stale");
        // Read-your-writes: only read from a replica that has applied my write's LSN
        Node chosen = followers.stream().filter(f -> f.appliedLsn >= myWrite).findFirst().orElse(leader);
        System.out.println("read-your-writes routing picks " + chosen.name + ": " + read(chosen, "bio"));
        // Leader dies before f2 caught up; promote the most up-to-date follower
        write("bio", "unreplicated write");
        Node promoted = followers.stream().max(Comparator.comparingLong(f -> f.appliedLsn)).get();
        System.out.println("leader crashed; promote " + promoted.name + " (lsn " + promoted.appliedLsn + "); lost write at lsn " + wal.size() + " because replication was async");
    }
}
''', ["Make replication semi-synchronous: `write` returns only after at least one follower has applied the entry.",
      "Add a monotonic-reads rule: remember the highest LSN each user has seen and never read from a replica behind it.",
      "Simulate multi-leader: two leaders accept writes to the same key, then resolve with last-write-wins timestamps."])

J("sharding", r'''
import java.util.*;

public class ShardingDemo {
    interface Router { int shardFor(long userId); }

    public static void main(String[] args) {
        int shards = 4;
        Router range = id -> (int) Math.min(shards - 1, id / 250_000);              // 0-249,999 -> shard 0 ...
        Router hash = id -> Math.floorMod(Long.hashCode(id * 0x9E3779B97F4A7C15L), shards);
        long[] newestUsers = new long[10_000];
        for (int i = 0; i < newestUsers.length; i++) newestUsers[i] = 990_000 + i;    // new signups have the highest ids
        for (var e : Map.of("range", range, "hash ", hash).entrySet()) {
            int[] load = new int[shards];
            for (long id : newestUsers) load[e.getValue().shardFor(id)]++;
            System.out.println(e.getKey() + " sharding, writes from 10,000 new users per shard: " + Arrays.toString(load));
        }
        System.out.println("range sharding puts all new users on the last shard (hotspot); hashing spreads them.");
        // Co-location: shard orders by user_id so a user's orders live with the user -> single-shard query
        Map<Integer, List<String>> shardData = new TreeMap<>();
        long[][] orders = {{42, 9001}, {42, 9002}, {7, 9003}, {500_123, 9004}};
        for (long[] o : orders) shardData.computeIfAbsent(hash.shardFor(o[0]), k -> new ArrayList<>()).add("user" + o[0] + "/order" + o[1]);
        System.out.println("orders keyed by user_id: " + shardData);
        System.out.println("'all orders of user 42' -> query only shard " + hash.shardFor(42));
        System.out.println("'all orders over Rs 1000' -> scatter to all " + shards + " shards and merge (expensive)");
        // Resharding pain with modulo
        int moved = 0;
        for (long id = 0; id < 100_000; id++) if (Math.floorMod(Long.hashCode(id * 0x9E3779B97F4A7C15L), 4) != Math.floorMod(Long.hashCode(id * 0x9E3779B97F4A7C15L), 5)) moved++;
        System.out.printf("going from 4 to 5 shards with hash %% N moves %.0f%% of rows (see consistent hashing)%n", moved / 1000.0);
    }
}
''', ["Add a directory-based router (`Map<userId, shard>`) and move one celebrity user to a dedicated shard.",
      "Implement a scatter-gather query 'top 5 most expensive orders' across all shards.",
      "Use 64 logical shards mapped onto 4 machines and show moving 16 logical shards to a 5th machine."])

J("consistent-hashing", r'''
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public class ConsistentHashingDemo {
    static final TreeMap<Long, String> ring = new TreeMap<>();
    static final int VNODES = 100;

    static long hash(String s) {
        try { byte[] d = MessageDigest.getInstance("MD5").digest(s.getBytes(StandardCharsets.UTF_8)); long h = 0; for (int i = 0; i < 8; i++) h = (h << 8) | (d[i] & 0xff); return h; }
        catch (Exception e) { throw new RuntimeException(e); }
    }
    static void addServer(String s) { for (int v = 0; v < VNODES; v++) ring.put(hash(s + "#" + v), s); }
    static void removeServer(String s) { ring.values().removeIf(x -> x.equals(s)); }
    static String serverFor(String key) {
        Map.Entry<Long, String> e = ring.ceilingEntry(hash(key));             // next position clockwise
        return (e != null ? e : ring.firstEntry()).getValue();                // wrap around
    }

    static Map<String, String> assign(List<String> keys) { Map<String, String> m = new HashMap<>(); for (String k : keys) m.put(k, serverFor(k)); return m; }

    public static void main(String[] args) {
        List<String> keys = new ArrayList<>(); for (int i = 0; i < 100_000; i++) keys.add("user:" + i);
        for (String s : List.of("A", "B", "C", "D")) addServer(s);
        Map<String, String> before = assign(keys);
        Map<String, Integer> load = new TreeMap<>(); before.values().forEach(s -> load.merge(s, 1, Integer::sum));
        System.out.println("4 servers, 100 vnodes each, load: " + load);
        addServer("E");
        Map<String, String> after = assign(keys);
        long moved = keys.stream().filter(k -> !before.get(k).equals(after.get(k))).count();
        long wrong = keys.stream().filter(k -> !before.get(k).equals(after.get(k)) && !after.get(k).equals("E")).count();
        System.out.printf("add server E: %.1f%% of keys moved (ideal 20%%), all of them to E? %s%n", moved / 1000.0, wrong == 0);
        removeServer("B");
        Map<String, String> afterRemove = assign(keys);
        Map<String, Integer> gained = new TreeMap<>();
        for (String k : keys) if (after.get(k).equals("B")) gained.merge(afterRemove.get(k), 1, Integer::sum);
        System.out.println("remove server B: its keys spread over the survivors " + gained);
        long modMoved = 0; for (int i = 0; i < 100_000; i++) if (Math.floorMod(("user:" + i).hashCode(), 4) != Math.floorMod(("user:" + i).hashCode(), 5)) modMoved++;
        System.out.printf("compare: hash %% N from 4 to 5 servers moves %.1f%% of keys%n", modMoved / 1000.0);
    }
}
''', ["Set VNODES to 1 and then 1000: print the max/min load ratio for each and explain the trade-off.",
      "Add weights: give server E 2× the virtual nodes because it has twice the RAM.",
      "Add replication: store each key on the next 3 distinct servers clockwise."])

J("db-scaling-path", r'''
import java.util.*;

public class DbScalingPathDemo {
    // A capacity model of a database tier; each step is applied only when the load needs it.
    record Tier(String step, double readCap, double writeCap) {}

    public static void main(String[] args) {
        double reads = 30_000, writes = 3_000;                           // target load per second
        List<Tier> path = new ArrayList<>();
        double readCap = 2_000, writeCap = 1_000;                         // one unoptimised DB
        path.add(new Tier("start: 1 DB, missing indexes", readCap, writeCap));
        readCap *= 2.5; writeCap *= 1.5; path.add(new Tier("1 add indexes, fix N+1 queries", readCap, writeCap));
        readCap *= 2; writeCap *= 2; path.add(new Tier("2 bigger machine (2x)", readCap, writeCap));
        readCap /= 0.2; path.add(new Tier("3 Redis cache, 80% hit ratio", readCap, writeCap));
        readCap += 3 * 10_000; path.add(new Tier("4 + 3 read replicas", readCap, writeCap));
        writeCap *= 4; path.add(new Tier("5 shard writes across 4 primaries", readCap, writeCap));
        System.out.printf("target: %,.0f reads/s, %,.0f writes/s%n", reads, writes);
        for (Tier t : path) {
            boolean ok = t.readCap() >= reads && t.writeCap() >= writes;
            System.out.printf("%-34s reads %,8.0f  writes %,6.0f  %s%n", t.step(), t.readCap(), t.writeCap(),
                ok ? "✔ enough" : "✘ short on " + (t.readCap() < reads ? "reads" : "") + (t.readCap() < reads && t.writeCap() < writes ? " + " : "") + (t.writeCap() < writes ? "writes" : ""));
        }
        System.out.println("Do the cheap steps first; sharding is last because it costs joins, transactions and operations.");
    }
}
''', ["Change the load to 5,000 reads and 500 writes: which is the first step that is enough?",
      "Add a 'split by feature' step (move the orders tables to their own DB, halving load on each).",
      "Add the monthly cost of each step and print cost per 1,000 writes/s."])

J("connection-pooling", r'''
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class ConnectionPoolDemo {
    static final AtomicInteger opened = new AtomicInteger();
    static class Conn { final int id = opened.incrementAndGet(); Conn() { sleep(30); } String query(String sql) { sleep(5); return "ok"; } }   // opening = TCP + TLS + auth ~30 ms
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException ignored) {} }

    static class Pool {
        final BlockingQueue<Conn> idle; final int max; final AtomicInteger created = new AtomicInteger();
        Pool(int max) { this.max = max; idle = new ArrayBlockingQueue<>(max); }
        Conn borrow(long timeoutMs) throws Exception {
            Conn c = idle.poll();
            if (c != null) return c;
            if (created.incrementAndGet() <= max) return new Conn();
            created.decrementAndGet();
            c = idle.poll(timeoutMs, TimeUnit.MILLISECONDS);             // wait for someone to return one
            if (c == null) throw new TimeoutException("pool exhausted");
            return c;
        }
        void giveBack(Conn c) { idle.offer(c); }
    }

    static long run(boolean pooled, int requests) throws Exception {
        opened.set(0); Pool pool = new Pool(4);
        ExecutorService web = Executors.newFixedThreadPool(16);
        long t = System.nanoTime();
        List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < requests; i++) fs.add(web.submit(() -> {
            if (!pooled) { new Conn().query("SELECT 1"); return null; }
            Conn c = pool.borrow(2000);
            try { c.query("SELECT 1"); } finally { pool.giveBack(c); }
            return null;
        }));
        for (Future<?> f : fs) f.get();
        web.shutdown();
        return (System.nanoTime() - t) / 1_000_000;
    }

    public static void main(String[] args) throws Exception {
        long a = run(false, 200); int openedNoPool = opened.get();
        long b = run(true, 200); int openedPool = opened.get();
        System.out.println("200 queries, 16 web threads");
        System.out.println("  new connection per query : " + openedNoPool + " connections opened, " + (a > b ? "slower" : "faster"));
        System.out.println("  pool of 4                : " + openedPool + " connections opened and reused, " + (b < a ? "faster" : "slower"));
        System.out.println("  " + (a / Math.max(1, b) >= 2 ? "pool was at least 2x faster" : "pool was faster") + " and the database saw 4 connections instead of " + openedNoPool);
    }
}
''', ["Make the pool size 1 and then 16: when does a bigger pool stop helping?",
      "Make one query leak its connection (never returned) and watch the pool exhaust with `TimeoutException`.",
      "Add a validation check on borrow (`isValid`) and a max lifetime after which connections are replaced."])

J("distributed-transactions", r'''
import java.util.*;

public class SagaDemo {
    // Orchestrated saga: each step is a local transaction with a compensating action.
    interface Step { String name(); boolean run(Map<String, Object> ctx); void compensate(Map<String, Object> ctx); }

    static Step step(String name, java.util.function.Predicate<Map<String, Object>> run, java.util.function.Consumer<Map<String, Object>> comp) {
        return new Step() { public String name() { return name; } public boolean run(Map<String, Object> c) { return run.test(c); } public void compensate(Map<String, Object> c) { comp.accept(c); } };
    }

    static int wallet = 5000, stock = 0; static String orderStatus = "NONE";
    static final List<String> outbox = new ArrayList<>();

    static void runSaga(List<Step> steps) {
        Map<String, Object> ctx = new HashMap<>(); Deque<Step> done = new ArrayDeque<>();
        for (Step s : steps) {
            if (s.run(ctx)) { done.push(s); System.out.println("  ✔ " + s.name()); continue; }
            System.out.println("  ✘ " + s.name() + " failed -> compensating in reverse order");
            while (!done.isEmpty()) { Step d = done.pop(); d.compensate(ctx); System.out.println("    ↺ undo " + d.name()); }
            return;
        }
    }

    public static void main(String[] args) {
        List<Step> placeOrder = List.of(
            step("create order (PENDING)", c -> { orderStatus = "PENDING"; outbox.add("OrderCreated"); return true; }, c -> { orderStatus = "CANCELLED"; outbox.add("OrderCancelled"); }),
            step("charge Rs 2499", c -> { if (wallet < 2499) return false; wallet -= 2499; return true; }, c -> { wallet += 2499; outbox.add("PaymentRefunded"); }),
            step("reserve 1 item", c -> { if (stock < 1) return false; stock--; return true; }, c -> stock++),
            step("confirm order", c -> { orderStatus = "CONFIRMED"; return true; }, c -> {}));
        System.out.println("Saga 1: stock = 0");
        runSaga(placeOrder);
        System.out.println("  result: order=" + orderStatus + " wallet=" + wallet + " stock=" + stock + " events=" + outbox);
        stock = 3; outbox.clear();
        System.out.println("Saga 2: stock = 3");
        runSaga(placeOrder);
        System.out.println("  result: order=" + orderStatus + " wallet=" + wallet + " stock=" + stock + " events=" + outbox);
    }
}
''', ["Implement two-phase commit for the same flow: a coordinator asks each participant to `prepare()` and commits only if all vote yes.",
      "Make a compensation fail once and add retries with a limit, then a 'needs manual review' state.",
      "Persist the saga's progress (current step) so it can resume after the orchestrator crashes."])

J("cdc", r'''
import java.util.*;
import java.util.function.*;

public class CdcDemo {
    // The database's own change log is tailed and turned into events for other systems (Debezium-style).
    record Change(long lsn, String op, String table, Map<String, Object> before, Map<String, Object> after) {}
    static final List<Change> wal = new ArrayList<>();
    static final Map<Integer, Map<String, Object>> orders = new TreeMap<>();

    static void insert(int id, String status) { Map<String, Object> row = Map.of("id", id, "status", status); orders.put(id, row); wal.add(new Change(wal.size() + 1, "c", "orders", null, row)); }
    static void update(int id, String status) { Map<String, Object> old = orders.get(id), row = Map.of("id", id, "status", status); orders.put(id, row); wal.add(new Change(wal.size() + 1, "u", "orders", old, row)); }
    static void delete(int id) { wal.add(new Change(wal.size() + 1, "d", "orders", orders.remove(id), null)); }

    public static void main(String[] args) {
        Map<Integer, String> searchIndex = new TreeMap<>(); Set<String> cache = new TreeSet<>(Set.of("order:987", "order:988"));
        List<Consumer<Change>> subscribers = List.of(
            c -> { if (c.after() != null) searchIndex.put((Integer) c.after().get("id"), (String) c.after().get("status")); else searchIndex.remove((Integer) c.before().get("id")); },
            c -> cache.remove("order:" + (c.after() != null ? c.after() : c.before()).get("id")));
        insert(987, "PENDING"); insert(988, "PENDING"); update(987, "PAID"); delete(988);
        long connectorOffset = 0;
        for (Change c : wal) {
            if (c.lsn() <= connectorOffset) continue;
            System.out.println("event lsn=" + c.lsn() + " op=" + c.op() + " before=" + c.before() + " after=" + c.after());
            subscribers.forEach(s -> s.accept(c));
            connectorOffset = c.lsn();                                        // checkpoint so a restart resumes here
        }
        System.out.println("search index now " + searchIndex + "; cache keys left " + cache);
        System.out.println("the app only wrote to the DB; search and cache stayed in sync from the log.");
    }
}
''', ["Add an 'analytics' subscriber that counts orders per status from the events.",
      "Simulate a connector crash after lsn 2 and resume from the checkpoint without reprocessing.",
      "Implement the transactional outbox instead: write an `outbox` row in the same 'transaction' and publish from it."])

J("blob-metadata", r'''
import java.security.MessageDigest;
import java.util.*;

public class BlobMetadataDemo {
    record Photo(long id, long owner, String objectKey, int sizeBytes, String sha256, String status) {}
    static final Map<String, byte[]> objectStore = new HashMap<>();          // S3 stand-in: big bytes, cheap
    static final Map<Long, Photo> metadataDb = new TreeMap<>();              // SQL stand-in: small rows, queryable
    static long seq = 0;

    static String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)).substring(0, 12); }

    static Photo upload(long owner, byte[] bytes) throws Exception {
        String h = sha(bytes);
        Optional<Photo> dup = metadataDb.values().stream().filter(p -> p.sha256().equals(h)).findFirst();
        long id = ++seq;
        String key = dup.map(Photo::objectKey).orElse("photos/" + h);
        metadataDb.put(id, new Photo(id, owner, key, bytes.length, h, "PENDING"));        // 1. row first, PENDING
        if (dup.isEmpty()) objectStore.put(key, bytes);                                     // 2. client PUTs bytes (pre-signed URL)
        Photo ready = new Photo(id, owner, key, bytes.length, h, "READY");                  // 3. storage event flips to READY
        metadataDb.put(id, ready);
        return ready;
    }

    public static void main(String[] args) throws Exception {
        byte[] cat = new byte[2_000_000]; Arrays.fill(cat, (byte) 7);
        byte[] dog = new byte[3_000_000]; Arrays.fill(dog, (byte) 9);
        System.out.println(upload(42, cat));
        System.out.println(upload(42, dog));
        System.out.println(upload(7, cat) + "  <- same bytes, deduplicated");
        long stored = objectStore.values().stream().mapToLong(b -> b.length).sum();
        System.out.printf("object store holds %d blobs, %.1f MB; metadata DB holds %d small rows%n", objectStore.size(), stored / 1e6, metadataDb.size());
        System.out.println("query 'photos of user 42' hits only the DB: " + metadataDb.values().stream().filter(p -> p.owner() == 42).map(Photo::id).toList());
    }
}
''', ["Add reference counting so deleting photo 3 doesn't delete the shared blob still used by photo 1.",
      "Add an orphan-cleanup job: find PENDING rows older than 1 day and blobs with no metadata row.",
      "Store thumbnails as separate objects (`photos/<sha>/thumb`) and add their keys to the row."])
