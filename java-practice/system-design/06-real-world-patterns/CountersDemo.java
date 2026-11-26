import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class CountersDemo {
    public static void main(String[] args) throws Exception {
        int threads = 8, likesEach = 100_000;
        // 1. One contended counter vs LongAdder (striped/sharded counter inside the JVM)
        AtomicLong single = new AtomicLong(); LongAdder sharded = new LongAdder();
        long t1 = time(threads, () -> { for (int i = 0; i < likesEach; i++) single.incrementAndGet(); });
        long t2 = time(threads, () -> { for (int i = 0; i < likesEach; i++) sharded.increment(); });
        System.out.printf("single AtomicLong : %,d likes (all threads fight over one memory location)%n", single.get());
        System.out.printf("sharded LongAdder : %,d likes (threads write different cells; read = sum of cells)%n", sharded.sum());
        // 2. Buffer-and-flush to a 'database'
        ConcurrentHashMap<String, LongAdder> buffer = new ConcurrentHashMap<>(); Map<String, Long> db = new TreeMap<>(); int[] dbWrites = {0};
        ScheduledExecutorService flusher = Executors.newSingleThreadScheduledExecutor();
        flusher.scheduleAtFixedRate(() -> {
            for (String k : buffer.keySet()) { long d = buffer.get(k).sumThenReset(); if (d > 0) { synchronized (db) { db.merge(k, d, Long::sum); dbWrites[0]++; } } }
        }, 20, 20, TimeUnit.MILLISECONDS);
        time(threads, () -> { for (int i = 0; i < 50_000; i++) buffer.computeIfAbsent("post:" + (i % 3), k -> new LongAdder()).increment(); });
        Thread.sleep(60); flusher.shutdown(); flusher.awaitTermination(1, TimeUnit.SECONDS);
        for (String k : buffer.keySet()) { long d = buffer.get(k).sumThenReset(); if (d > 0) { db.merge(k, d, Long::sum); dbWrites[0]++; } }
        System.out.printf("buffered counting : db=%s from %,d likes with only %s DB writes%n", db, threads * 50_000, dbWrites[0] < 100 ? "a few dozen" : String.valueOf(dbWrites[0]));
    }

    static long time(int threads, Runnable r) throws Exception {
        ExecutorService p = Executors.newFixedThreadPool(threads); long t = System.nanoTime();
        List<Future<?>> fs = new ArrayList<>(); for (int i = 0; i < threads; i++) fs.add(p.submit(r));
        for (Future<?> f : fs) f.get(); p.shutdown(); return System.nanoTime() - t;
    }
}
