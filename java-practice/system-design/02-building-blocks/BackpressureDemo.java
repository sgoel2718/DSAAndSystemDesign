import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class BackpressureDemo {
    // Fast producer (1 item/ms) vs slow consumer (1 item / 3 ms) for 300 ms.
    static void run(String name, BlockingQueue<Integer> q, boolean dropWhenFull) throws Exception {
        AtomicInteger produced = new AtomicInteger(), dropped = new AtomicInteger(), consumed = new AtomicInteger(), maxQueue = new AtomicInteger();
        AtomicBoolean done = new AtomicBoolean();
        Thread consumer = new Thread(() -> {
            while (!done.get() || !q.isEmpty()) {
                try { if (q.poll(10, TimeUnit.MILLISECONDS) != null) { consumed.incrementAndGet(); Thread.sleep(3); } } catch (InterruptedException e) { return; }
            }
        });
        consumer.start();
        long end = System.currentTimeMillis() + 300;
        while (System.currentTimeMillis() < end) {
            int item = produced.incrementAndGet();
            if (dropWhenFull) { if (!q.offer(item)) dropped.incrementAndGet(); }
            else q.put(item);                                              // blocks when full: producer slows down
            maxQueue.accumulateAndGet(q.size(), Math::max);
            Thread.sleep(1);
        }
        done.set(true); consumer.join();
        System.out.printf("%-26s produced %4s  dropped %4s  max queue %5s%n", name, bucket(produced.get()), bucket(dropped.get()), bucket(maxQueue.get()));
    }
    static String bucket(int n) { return n < 20 ? String.valueOf(n) : "~" + (n / 10 * 10); }

    public static void main(String[] args) throws Exception {
        run("unbounded queue", new LinkedBlockingQueue<>(), false);
        run("bounded(20), block", new ArrayBlockingQueue<>(20), false);
        run("bounded(20), drop/shed", new ArrayBlockingQueue<>(20), true);
        System.out.println("Unbounded: the backlog (and memory, and latency) keeps growing.");
        System.out.println("Blocking: the producer is slowed to the consumer's pace. Dropping: the queue stays small, extra work is shed.");
    }
}
