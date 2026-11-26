import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class AuctionSystem {
    // Bids accepted only if higher than current by a minimum increment (atomic compare-and-set), anti-sniping extension, proxy bidding.
    record State(long price, String leader, long endsAt) {}
    static final AtomicReference<State> auction = new AtomicReference<>(new State(1000, null, 600));
    static final Map<String, Long> proxyMax = new ConcurrentHashMap<>();
    static final long INCREMENT = 50;

    static String bid(String user, long amount, long now) {
        while (true) {
            State s = auction.get();
            if (now >= s.endsAt()) return user + " " + amount + " rejected: auction ended";
            if (amount < s.price() + INCREMENT) return user + " " + amount + " rejected: must be >= " + (s.price() + INCREMENT);
            long newEnd = s.endsAt() - now < 60 ? now + 60 : s.endsAt();          // a bid in the last minute extends the auction
            if (auction.compareAndSet(s, new State(amount, user, newEnd))) {
                String r = user + " leads at " + amount + (newEnd != s.endsAt() ? " (extended to t=" + newEnd + ")" : "");
                String rival = s.leader();
                if (rival != null && proxyMax.getOrDefault(rival, 0L) >= amount + INCREMENT) { r += "\n  proxy for " + rival + " -> " + bid(rival, amount + INCREMENT, now); }
                return r;
            }
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println(bid("asha", 1100, 10));
        proxyMax.put("asha", 1500L);                                                     // asha: 'bid for me up to 1500'
        System.out.println(bid("ravi", 1200, 100));
        System.out.println(bid("ravi", 1520, 200));
        System.out.println(bid("zoya", 1550, 300));
        ExecutorService pool = Executors.newFixedThreadPool(8); List<Future<String>> fs = new ArrayList<>();
        for (int i = 0; i < 100; i++) { final long amt = 1600 + i * 10; fs.add(pool.submit(() -> bid("bot" + amt, amt, 400))); }
        int accepted = 0; for (Future<String> f : fs) if (f.get().contains("leads")) accepted++; pool.shutdown();
        System.out.println("100 concurrent bot bids: " + accepted + " accepted in order; leader " + auction.get().leader() + " at " + auction.get().price() + " (never a lower price over a higher one)");
        System.out.println(bid("kiran", 2700, 570));
        System.out.println(bid("asha", 3000, 610) + " | ends at t=" + auction.get().endsAt());
        System.out.println(bid("ravi", 3100, 700));
    }
}
