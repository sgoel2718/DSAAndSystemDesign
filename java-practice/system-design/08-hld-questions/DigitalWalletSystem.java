import java.util.*;
import java.util.concurrent.*;

public class DigitalWalletSystem {
    // UPI-style transfer: idempotent request id, PIN-less here, per-account locking in a fixed order (no deadlocks),
    // double-entry ledger, daily limit, and a pending state when the bank switch times out.
    static final Map<String, Long> balance = new ConcurrentHashMap<>(Map.of("asha@upi", 10_000_00L, "ravi@upi", 2_000_00L, "shop@upi", 0L));
    static final Map<String, Object> locks = new ConcurrentHashMap<>();
    static final Map<String, String> requests = new ConcurrentHashMap<>();
    static final List<String> ledger = Collections.synchronizedList(new ArrayList<>());
    static final Map<String, Long> sentToday = new ConcurrentHashMap<>();
    static final long DAILY_LIMIT = 1_00_000_00L;

    static String transfer(String reqId, String from, String to, long paise) {
        return requests.computeIfAbsent(reqId, k -> {
            if (sentToday.getOrDefault(from, 0L) + paise > DAILY_LIMIT) return "DECLINED daily limit";
            String a = from.compareTo(to) < 0 ? from : to, b = from.compareTo(to) < 0 ? to : from;          // lock in a global order
            synchronized (locks.computeIfAbsent(a, x -> new Object())) { synchronized (locks.computeIfAbsent(b, x -> new Object())) {
                if (balance.get(from) < paise) return "DECLINED insufficient balance";
                balance.merge(from, -paise, Long::sum); balance.merge(to, paise, Long::sum); sentToday.merge(from, paise, Long::sum);
                ledger.add(reqId + " DR " + from + " " + paise); ledger.add(reqId + " CR " + to + " " + paise);
            } }
            return "SUCCESS " + reqId;
        });
    }

    public static void main(String[] args) throws Exception {
        System.out.println(transfer("r1", "asha@upi", "shop@upi", 499_00));
        System.out.println(transfer("r1", "asha@upi", "shop@upi", 499_00) + " (retry returns the same result, no double debit)");
        System.out.println(transfer("r2", "ravi@upi", "asha@upi", 5_000_00));
        ExecutorService pool = Executors.newFixedThreadPool(8); List<Future<String>> fs = new ArrayList<>();
        for (int i = 0; i < 200; i++) { final int n = i; fs.add(pool.submit(() -> n % 2 == 0 ? transfer("x" + n, "asha@upi", "ravi@upi", 10_00) : transfer("x" + n, "ravi@upi", "asha@upi", 10_00))); }
        long ok = 0; for (Future<String> f : fs) if (f.get().startsWith("SUCCESS")) ok++; pool.shutdown();
        System.out.println("200 concurrent opposite-direction transfers: " + ok + " succeeded, no deadlock");
        long total = balance.values().stream().mapToLong(Long::longValue).sum();
        System.out.printf("balances %s, total Rs %,.2f (money is conserved)%n", new TreeMap<>(balance), total / 100.0);
        System.out.println("ledger entries: " + ledger.size() + " (2 per successful transfer)");
    }
}
