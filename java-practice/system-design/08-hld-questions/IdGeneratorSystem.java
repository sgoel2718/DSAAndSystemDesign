import java.util.*;
import java.util.concurrent.*;

public class IdGeneratorSystem {
    // Three designs side by side: Snowflake (time+machine+seq), ticket server ranges, and UUIDv7-style.
    static class Snowflake {
        final long machine; long last = -1, seq;
        Snowflake(long m) { machine = m; }
        synchronized long next(long ms) { if (ms == last) { seq = (seq + 1) & 4095; } else { seq = 0; last = ms; } return (ms - 1_700_000_000_000L) << 22 | machine << 12 | seq; }
    }
    static class TicketServer { long next = 1; synchronized long[] range(int n) { long s = next; next += n; return new long[]{s, s + n - 1}; } }
    static String uuidV7(long ms, Random r) { return String.format("%012x-7%03x-%016x", ms, r.nextInt(4096), r.nextLong() & 0x3fffffffffffffffL | 0x8000000000000000L); }

    public static void main(String[] args) throws Exception {
        Map<Long, Snowflake> fleet = new TreeMap<>(); for (long m = 1; m <= 3; m++) fleet.put(m, new Snowflake(m));
        long now = 1_764_140_000_000L;
        System.out.println("Snowflake ids from 3 machines in the same millisecond:");
        for (Snowflake s : fleet.values()) System.out.println("  machine " + s.machine + " -> " + s.next(now) + ", " + s.next(now));
        Set<Long> ids = ConcurrentHashMap.newKeySet(); ExecutorService pool = Executors.newFixedThreadPool(3); List<Future<?>> fs = new ArrayList<>();
        for (Snowflake s : fleet.values()) fs.add(pool.submit(() -> { for (int ms = 0; ms < 100; ms++) for (int i = 0; i < 1000; i++) ids.add(s.next(now + 10 + ms)); }));
        for (Future<?> f : fs) f.get(); pool.shutdown();
        System.out.println("  300,000 ids generated in parallel -> unique: " + ids.size());
        TicketServer ts = new TicketServer();
        System.out.println("Ticket server ranges: app-1 " + Arrays.toString(ts.range(1000)) + ", app-2 " + Arrays.toString(ts.range(1000)) + " (one DB call per 1,000 ids)");
        Random r = new Random(1);
        String u1 = uuidV7(now, r), u2 = uuidV7(now + 5, r);
        System.out.println("UUIDv7-style: " + u1 + " < " + u2 + " ? " + (u1.compareTo(u2) < 0) + " (time-sortable, no coordination, 128 bits)");
    }
}
