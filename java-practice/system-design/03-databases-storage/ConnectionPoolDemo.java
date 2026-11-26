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
