import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.concurrent.locks.*;

public class ConcurrencyDemo {
    static int unsafeCounter = 0;

    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        // 1. Race condition vs AtomicInteger
        AtomicInteger safe = new AtomicInteger(); List<Future<?>> fs = new ArrayList<>();
        for (int t = 0; t < 4; t++) fs.add(pool.submit(() -> { for (int i = 0; i < 100_000; i++) { unsafeCounter++; safe.incrementAndGet(); } }));
        for (Future<?> f : fs) f.get();
        System.out.println("1. 4 threads x 100,000 increments: int++ = " + (unsafeCounter == 400_000 ? "400000 (got lucky)" : unsafeCounter + " (lost updates)") + ", AtomicInteger = " + safe.get());
        // 2. ReentrantLock protecting a check-then-act on a seat map
        Map<String, String> seats = new HashMap<>(); ReentrantLock lock = new ReentrantLock(); AtomicInteger booked = new AtomicInteger();
        fs.clear();
        for (int t = 0; t < 8; t++) { final String user = "u" + t; fs.add(pool.submit(() -> { lock.lock(); try { if (!seats.containsKey("A1")) { seats.put("A1", user); booked.incrementAndGet(); } } finally { lock.unlock(); } })); }
        for (Future<?> f : fs) f.get();
        System.out.println("2. 8 users race for seat A1 -> bookings made: " + booked.get());
        // 3. Producer-consumer with a BlockingQueue
        BlockingQueue<Integer> q = new ArrayBlockingQueue<>(5); AtomicInteger sum = new AtomicInteger();
        Future<?> consumer = pool.submit(() -> { for (int i = 0; i < 20; i++) sum.addAndGet(q.take()); return null; });
        for (int i = 1; i <= 20; i++) q.put(i);
        consumer.get();
        System.out.println("3. producer -> bounded queue(5) -> consumer: sum 1..20 = " + sum.get());
        // 4. CompletableFuture: run two calls in parallel and combine
        CompletableFuture<String> price = CompletableFuture.supplyAsync(() -> { sleep(50); return "Rs 2499"; }, pool);
        CompletableFuture<String> stock = CompletableFuture.supplyAsync(() -> { sleep(50); return "in stock"; }, pool);
        long t0 = System.nanoTime(); String page = price.thenCombine(stock, (p, s) -> p + ", " + s).get();
        System.out.println("4. CompletableFuture combine: '" + page + "' in ~" + Math.round((System.nanoTime() - t0) / 1e7) * 10 + " ms (parallel, not 100)");
        // 5. CountDownLatch: wait for all workers
        CountDownLatch done = new CountDownLatch(3);
        for (int i = 0; i < 3; i++) pool.submit(() -> { sleep(10); done.countDown(); });
        System.out.println("5. latch: all 3 workers finished = " + done.await(1, TimeUnit.SECONDS));
        // 6. ConcurrentHashMap.merge for safe aggregation
        ConcurrentHashMap<String, Integer> wordCount = new ConcurrentHashMap<>(); fs.clear();
        for (int t = 0; t < 4; t++) fs.add(pool.submit(() -> { for (String w : "to be or not to be".split(" ")) wordCount.merge(w, 1, Integer::sum); }));
        for (Future<?> f : fs) f.get();
        System.out.println("6. ConcurrentHashMap word count from 4 threads: " + new TreeMap<>(wordCount));
        pool.shutdown();
    }
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } }
}
