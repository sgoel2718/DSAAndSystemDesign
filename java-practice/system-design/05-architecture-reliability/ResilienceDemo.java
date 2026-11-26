import java.util.*;

public class ResilienceDemo {
    static class CircuitBreaker {
        enum State { CLOSED, OPEN, HALF_OPEN }
        State state = State.CLOSED; int failures = 0; long openedAt; final int threshold = 3; final long cooldown = 30;
        String call(long now, java.util.function.Supplier<String> remote, String fallback) {
            if (state == State.OPEN) { if (now - openedAt >= cooldown) state = State.HALF_OPEN; else return fallback + " [breaker OPEN, no call made]"; }
            try {
                String r = remote.get();
                if (state == State.HALF_OPEN) System.out.println("    trial call succeeded -> CLOSED");
                state = State.CLOSED; failures = 0; return r;
            } catch (RuntimeException e) {
                failures++;
                if (state == State.HALF_OPEN || failures >= threshold) {
                    System.out.println(state == State.HALF_OPEN ? "    trial call (HALF-OPEN) failed -> OPEN again at t=" + now : "    3 failures in a row -> breaker OPEN at t=" + now);
                    state = State.OPEN; openedAt = now;
                }
                return fallback + " [" + e.getMessage() + "]";
            }
        }
    }

    static long backoffMs(int attempt, Random r) { long cap = Math.min(5000, 100L << (attempt - 1)); return r.nextLong(cap + 1); }  // full jitter

    public static void main(String[] args) {
        CircuitBreaker cb = new CircuitBreaker();
        boolean[] recsHealthy = new boolean[100]; Arrays.fill(recsHealthy, true);
        for (int t = 10; t < 60; t++) recsHealthy[t] = false;                 // recommendation service down from t=10 to t=60
        for (long t : new long[]{0, 10, 12, 14, 16, 20, 46, 62, 80, 82}) {
            final long tt = t;
            String r = cb.call(t, () -> { if (!recsHealthy[(int) tt]) throw new RuntimeException("timeout"); return "fresh recommendations"; }, "cached top sellers");
            System.out.printf("t=%2d %-9s %s%n", t, cb.state, r);
        }
        Random r = new Random(4);
        StringBuilder sb = new StringBuilder("retry waits with exponential backoff + jitter: ");
        for (int a = 1; a <= 5; a++) sb.append(backoffMs(a, r)).append(" ms  ");
        System.out.println(sb);
    }
}
