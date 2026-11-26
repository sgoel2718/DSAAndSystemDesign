import java.util.*;

public class ReadWriteHeavyDemo {
    public static void main(String[] args) {
        // Read-heavy: a news article read 100,000 times, edited twice -> cache it
        int reads = 100_000, dbReads = 0; Map<String, String> cache = new HashMap<>();
        for (int i = 0; i < reads; i++) {
            if (i == 40_000 || i == 80_000) cache.remove("article:1");          // edit -> invalidate
            if (cache.get("article:1") == null) { dbReads++; cache.put("article:1", "<html>"); }
        }
        System.out.printf("read-heavy : %,d reads -> %d DB reads (cache absorbs %.3f%%)%n", reads, dbReads, 100.0 * (reads - dbReads) / reads);
        // Write-heavy: 1,000,000 sensor readings -> append to a log and write in batches instead of one row at a time
        int events = 1_000_000, batch = 5_000; List<int[]> log = new ArrayList<>(); int writeCalls = 0; List<int[]> buf = new ArrayList<>();
        Random r = new Random(1);
        for (int i = 0; i < events; i++) {
            buf.add(new int[]{i % 1000, r.nextInt(50)});
            if (buf.size() == batch) { log.addAll(buf); buf.clear(); writeCalls++; }
        }
        System.out.printf("write-heavy: %,d events -> %,d batched sequential appends instead of %,d single-row writes%n", events, writeCalls, events);
        // ...and aggregate asynchronously for reads (per-sensor average)
        double[] sum = new double[1000]; int[] cnt = new int[1000];
        for (int[] e : log) { sum[e[0]] += e[1]; cnt[e[0]]++; }
        System.out.printf("rollup for dashboards: sensor 7 avg %.1f over %d readings%n", sum[7] / cnt[7], cnt[7]);
    }
}
