import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class OversellingDemo {
    static int stockUnsafe; static final AtomicInteger stockSafe = new AtomicInteger();

    static int flashSale(boolean safe, int stock, int buyers) throws Exception {
        stockUnsafe = stock; stockSafe.set(stock); AtomicInteger orders = new AtomicInteger();
        ExecutorService pool = Executors.newFixedThreadPool(16); CountDownLatch go = new CountDownLatch(1); List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < buyers; i++) fs.add(pool.submit(() -> {
            go.await();
            if (!safe) { if (stockUnsafe > 0) { Thread.yield(); stockUnsafe--; orders.incrementAndGet(); } }   // check-then-act race
            else {
                while (true) {                                            // UPDATE ... SET stock = stock - 1 WHERE stock >= 1
                    int s = stockSafe.get(); if (s < 1) break;
                    if (stockSafe.compareAndSet(s, s - 1)) { orders.incrementAndGet(); break; }
                }
            }
            return null;
        }));
        go.countDown(); for (Future<?> f : fs) f.get(); pool.shutdown();
        return orders.get();
    }

    public static void main(String[] args) throws Exception {
        int worst = 0; for (int run = 0; run < 20; run++) worst = Math.max(worst, flashSale(false, 10, 5000));
        System.out.println("check-then-act : 10 PS5s, 5,000 buyers -> up to " + (worst > 10 ? worst + " orders (OVERSOLD)" : worst + " orders (race didn't show this time; it will in production)"));
        System.out.println("conditional decrement: 10 PS5s, 5,000 buyers -> " + flashSale(true, 10, 5000) + " orders, never more");
        // Reservation with TTL: hold for 10 min; unpaid holds return to stock
        Map<String, Long> holds = new LinkedHashMap<>(Map.of("asha", 0L, "ravi", 2L, "zoya", 9L)); int available = 0; long now = 12;
        for (var it = holds.entrySet().iterator(); it.hasNext(); ) { var h = it.next(); if (now - h.getValue() >= 10) { it.remove(); available++; } }
        System.out.println("at minute 12, expired unpaid holds released -> " + available + " back in stock, still held: " + holds.keySet());
    }
}
