import java.util.*;

public class QueueingDemo {
    // Single server queue simulated with seeded random arrivals: latency explodes as utilisation approaches 100%.
    static double avgLatency(double utilisation, long seed) {
        Random r = new Random(seed);
        double serviceMs = 10, arrivalRate = utilisation / serviceMs;      // requests per ms
        double t = 0, serverFreeAt = 0, total = 0; int n = 200_000;
        for (int i = 0; i < n; i++) {
            t += -Math.log(1 - r.nextDouble()) / arrivalRate;               // next arrival
            double start = Math.max(t, serverFreeAt);
            double service = -Math.log(1 - r.nextDouble()) * serviceMs;
            serverFreeAt = start + service;
            total += serverFreeAt - t;                                      // waiting + service
        }
        return total / n;
    }

    public static void main(String[] args) {
        System.out.println("utilisation  avg latency   (theory M/M/1: 10 ms / (1 - rho))");
        for (double u : new double[]{0.5, 0.7, 0.8, 0.9, 0.95}) {
            System.out.printf("   %3.0f%%       %6.1f ms    %6.1f ms%n", u * 100, avgLatency(u, 11), 10 / (1 - u));
        }
        System.out.println("\nFast for one user (10 ms) is a performance property;");
        System.out.println("staying fast as load grows needs headroom (scale out before ~70-80% busy).");
    }
}
