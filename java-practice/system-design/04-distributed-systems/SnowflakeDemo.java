import java.util.*;
import java.util.concurrent.*;

public class SnowflakeDemo {
    static class Snowflake {
        static final long EPOCH = 1_700_000_000_000L; final long machine; long lastMs = -1, seq = 0;
        Snowflake(long machine) { if (machine < 0 || machine > 1023) throw new IllegalArgumentException(); this.machine = machine; }
        synchronized long next(long nowMs) {
            if (nowMs < lastMs) throw new IllegalStateException("clock moved backwards");
            if (nowMs == lastMs) {
                seq = (seq + 1) & 4095;
                if (seq == 0) { while (nowMs <= lastMs) nowMs = Math.max(nowMs, System.currentTimeMillis()); }   // 4096 ids used this ms: wait for the next ms
            }
            else seq = 0;
            lastMs = nowMs;
            return ((nowMs - EPOCH) << 22) | (machine << 12) | seq;
        }
        synchronized long next() { return next(System.currentTimeMillis()); }     // read the clock inside the lock
        static String explain(long id) { return String.format("ts=+%dms machine=%d seq=%d", id >>> 22, (id >> 12) & 1023, id & 4095); }
    }

    public static void main(String[] args) throws Exception {
        Snowflake m7 = new Snowflake(7), m8 = new Snowflake(8);
        long now = 1_764_140_000_000L;
        long a = m7.next(now), b = m7.next(now), c = m8.next(now), d = m7.next(now + 1);
        for (long id : new long[]{a, b, c, d}) System.out.println(id + "  " + Snowflake.explain(id));
        System.out.println("sorted by id == sorted by time: " + (a < b && b < d));
        Set<Long> ids = ConcurrentHashMap.newKeySet();
        Snowflake shared = new Snowflake(1); ExecutorService pool = Executors.newFixedThreadPool(8);
        List<Future<?>> fs = new ArrayList<>();
        for (int t = 0; t < 8; t++) fs.add(pool.submit(() -> { for (int i = 0; i < 50_000; i++) ids.add(shared.next()); }));
        try { for (Future<?> f : fs) f.get(); } finally { pool.shutdown(); }
        System.out.println("8 threads x 50,000 ids -> " + ids.size() + " unique");
        try { m7.next(now - 5); } catch (IllegalStateException e) { System.out.println("clock went back 5 ms -> " + e.getMessage() + " (wait or refuse)"); }
        System.out.println("UUIDv4 for comparison: " + UUID.randomUUID().toString().length() + " chars, random order");
    }
}
