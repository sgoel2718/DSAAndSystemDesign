import java.util.*;

public class CanaryDeployDemo {
    // Gradually shift traffic to v2 while comparing error rates; roll back automatically if v2 is worse.
    static double run(String name, double v2ErrorRate) {
        Random r = new Random(17);
        int[] steps = {1, 5, 25, 50, 100};
        for (int pct : steps) {
            int v1Req = 0, v1Err = 0, v2Req = 0, v2Err = 0;
            for (int i = 0; i < 20_000; i++) {
                boolean toV2 = r.nextInt(100) < pct;
                boolean err = r.nextDouble() < (toV2 ? v2ErrorRate : 0.001);
                if (toV2) { v2Req++; if (err) v2Err++; } else { v1Req++; if (err) v1Err++; }
            }
            double e1 = v1Req == 0 ? 0 : v1Err / (double) v1Req, e2 = v2Err / (double) Math.max(1, v2Req);
            System.out.printf("  %-8s %3d%% on v2: v1 errors %.2f%%, v2 errors %.2f%%", name, pct, e1 * 100, e2 * 100);
            if (v2Req >= 100 && e2 > Math.max(0.002, e1 * 2)) { System.out.println("  -> ROLLBACK to v1"); return pct; }
            System.out.println("  -> healthy, continue");
        }
        return 100;
    }

    public static void main(String[] args) {
        System.out.println("good release:"); run("v2-good", 0.001);
        System.out.println("bad release:"); double stopped = run("v2-bad", 0.03);
        System.out.printf("the bad release reached only %.0f%% of users before rollback%n", stopped);
        // Blue-green: two full environments, the router flips in one step
        String live = "blue"; System.out.println("blue-green: live=" + live);
        live = "green"; System.out.println("blue-green: deploy to green, smoke test, flip router -> live=" + live);
        live = "blue"; System.out.println("blue-green: problem found -> flip back instantly -> live=" + live);
    }
}
