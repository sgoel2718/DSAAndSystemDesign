import java.util.*;

public class RateLimiterAlgorithmsDemo {
    interface Limiter { boolean allow(long nowMs); }

    static class TokenBucket implements Limiter {
        final double capacity, refillPerMs; double tokens; long last;
        TokenBucket(int capacity, int perSecond) { this.capacity = capacity; this.refillPerMs = perSecond / 1000.0; this.tokens = capacity; }
        public boolean allow(long now) {
            tokens = Math.min(capacity, tokens + (now - last) * refillPerMs); last = now;
            if (tokens >= 1) { tokens -= 1; return true; } return false;
        }
    }

    static class FixedWindow implements Limiter {
        final int limit; final long window; long windowStart = -1; int count;
        FixedWindow(int limit, long windowMs) { this.limit = limit; this.window = windowMs; }
        public boolean allow(long now) {
            long w = now / window * window;
            if (w != windowStart) { windowStart = w; count = 0; }
            return ++count <= limit;
        }
    }

    static class SlidingLog implements Limiter {
        final int limit; final long window; final Deque<Long> log = new ArrayDeque<>();
        SlidingLog(int limit, long windowMs) { this.limit = limit; this.window = windowMs; }
        public boolean allow(long now) {
            while (!log.isEmpty() && log.peekFirst() <= now - window) log.pollFirst();
            if (log.size() < limit) { log.addLast(now); return true; } return false;
        }
    }

    public static void main(String[] args) {
        // Burst at the edge of two windows: 5 requests at t=900..940 ms and 5 at t=1000..1040 ms; limit 5 per second
        long[] times = {900, 910, 920, 930, 940, 1000, 1010, 1020, 1030, 1040};
        Map<String, Limiter> ls = new LinkedHashMap<>();
        ls.put("fixed window ", new FixedWindow(5, 1000));
        ls.put("sliding log  ", new SlidingLog(5, 1000));
        ls.put("token bucket ", new TokenBucket(5, 5));
        for (var e : ls.entrySet()) {
            StringBuilder sb = new StringBuilder(); int ok = 0;
            for (long t : times) { boolean a = e.getValue().allow(t); sb.append(a ? '✔' : '✘'); if (a) ok++; }
            System.out.println(e.getKey() + sb + "  allowed " + ok + " of 10 within 140 ms");
        }
        System.out.println("Fixed window lets 10 through around the boundary; sliding log and token bucket hold the limit.");
    }
}
