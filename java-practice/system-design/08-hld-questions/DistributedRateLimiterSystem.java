import java.util.*;
import java.util.concurrent.*;

public class DistributedRateLimiterSystem {
    // Gateways share counters in one "Redis" (here a synchronized store). Sliding-window-counter algorithm per (user, rule).
    static class RedisLike {
        private final Map<String, Long> kv = new HashMap<>();
        synchronized long[] incrAndGetWindows(String key, long windowStart, long prevStart) {   // atomic like a Lua script
            long cur = kv.merge(key + ":" + windowStart, 1L, Long::sum);
            long prev = kv.getOrDefault(key + ":" + prevStart, 0L);
            return new long[]{cur, prev};
        }
    }
    record Rule(String name, int limit, long windowMs) {}
    static final Map<String, Rule> rules = Map.of("free", new Rule("free", 5, 1000), "pro", new Rule("pro", 20, 1000));

    static class Gateway {
        final String name; final RedisLike redis; boolean redisDown = false;
        Gateway(String n, RedisLike r) { name = n; redis = r; }
        String handle(String user, String plan, long now) {
            Rule r = rules.get(plan);
            if (redisDown) return "200 (fail-open: limiter unavailable)";
            long win = now / r.windowMs() * r.windowMs();
            long[] c = redis.incrAndGetWindows("rl:" + user, win, win - r.windowMs());
            double weight = 1 - (now - win) / (double) r.windowMs();               // how much of the previous window still overlaps
            double estimate = c[1] * weight + c[0];
            if (estimate > r.limit()) return String.format("429 (est %.1f > %d) Retry-After: %d ms", estimate, r.limit(), win + r.windowMs() - now);
            return String.format("200 (est %.1f of %d)", estimate, r.limit());
        }
    }

    public static void main(String[] args) {
        RedisLike redis = new RedisLike(); Gateway g1 = new Gateway("gw-1", redis), g2 = new Gateway("gw-2", redis);
        long[] times = {100, 200, 300, 400, 500, 600, 1100, 1500};
        for (int i = 0; i < times.length; i++) {
            Gateway g = i % 2 == 0 ? g1 : g2;                                          // requests spread over two gateways
            System.out.printf("t=%4d %s asha(free) -> %s%n", times[i], g.name, g.handle("asha", "free", times[i]));
        }
        System.out.println("pro user ravi, 8 quick requests -> " + (int) java.util.stream.IntStream.range(0, 8).filter(i -> g1.handle("ravi", "pro", 2000 + i).startsWith("200")).count() + " allowed");
        g2.redisDown = true;
        System.out.println("redis outage, gw-2 -> " + g2.handle("asha", "free", 2100));
    }
}
