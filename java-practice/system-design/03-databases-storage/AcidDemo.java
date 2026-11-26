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
