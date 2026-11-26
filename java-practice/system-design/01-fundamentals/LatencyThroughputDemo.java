import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class LatencyThroughputDemo {
    // Each request "takes" 20 ms (sleep). Throughput depends on how many run in parallel: Little's law.
    static double runWithThreads(int threads, int requests) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(threads);
        long start = System.nanoTime();
        List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < requests; i++) fs.add(pool.submit(() -> { try { Thread.sleep(20); } catch (InterruptedException e) {} }));
        for (Future<?> f : fs) f.get();
        pool.shutdown();
        double seconds = (System.nanoTime() - start) / 1e9;
        return requests / seconds;
    }

    static long percentile(List<Long> sorted, double p) { return sorted.get((int) Math.ceil(p * sorted.size()) - 1); }

    public static void main(String[] args) throws Exception {
        for (int t : new int[]{1, 4, 16}) {
            double tput = runWithThreads(t, 160);
            System.out.printf("threads=%2d  latency=20 ms  throughput ~ %4.0f req/s  (Little's law predicts %d)%n", t, Math.floor(tput / 10) * 10, t * 50);
        }
        // Percentiles: a fixed, seeded latency sample with a slow tail
        Random r = new Random(7);
        List<Long> lat = new ArrayList<>();
        for (int i = 0; i < 1000; i++) lat.add((long) (r.nextInt(100) < 98 ? 30 + r.nextInt(40) : 300 + r.nextInt(900)));
        Collections.sort(lat);
        double avg = lat.stream().mapToLong(Long::longValue).average().orElse(0);
        System.out.printf("%naverage=%.0f ms  p50=%d  p90=%d  p99=%d  max=%d%n", avg, percentile(lat, .50), percentile(lat, .90), percentile(lat, .99), lat.get(999));
        System.out.println("The average hides the slow tail; alert on p99.");
    }
}
