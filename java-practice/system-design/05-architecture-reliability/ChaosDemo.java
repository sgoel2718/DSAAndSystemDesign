import java.util.*;

public class ChaosDemo {
    // Steady-state hypothesis: checkout success >= 99%. Inject faults; abort the experiment if the hypothesis breaks.
    static boolean hasTimeout = false, hasFallback = false;

    static boolean checkout(Random r, String fault) {
        boolean recsUp = !fault.equals("kill recommendations");
        boolean slowPayments = fault.equals("payment +2s latency") && r.nextInt(10) < 3;
        if (!recsUp && !hasFallback) return false;                      // page crashes without recommendations
        if (slowPayments && !hasTimeout) return false;                  // threads pile up, requests fail
        return r.nextInt(1000) != 0;
    }

    static void experiment(String fault) {
        Random r = new Random(13); int ok = 0, n = 2000;
        for (int i = 0; i < n; i++) if (checkout(r, fault)) ok++;
        double rate = ok * 100.0 / n;
        System.out.printf("  %-24s success %.1f%% -> %s%n", fault, rate, rate >= 99 ? "hypothesis holds" : "BROKEN: abort, fix it");
    }

    public static void main(String[] args) {
        System.out.println("round 1 (no resilience):");
        for (String f : List.of("none", "kill recommendations", "payment +2s latency")) experiment(f);
        hasFallback = true; hasTimeout = true;
        System.out.println("round 2 (added fallback for recs + timeout/retry for payments):");
        for (String f : List.of("none", "kill recommendations", "payment +2s latency")) experiment(f);
    }
}
