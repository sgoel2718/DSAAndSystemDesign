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
