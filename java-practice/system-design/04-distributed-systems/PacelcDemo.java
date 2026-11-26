import java.util.*;

public class PacelcDemo {
    // No partition: should a write wait for remote replicas (consistency) or return after the local one (latency)?
    public static void main(String[] args) {
        int localMs = 1; int[] remoteRttMs = {2, 60, 180};                // same AZ, Singapore, US
        Random r = new Random(3);
        System.out.println("mode                     write latency   read on remote replica right after");
        for (String mode : List.of("EL: ack after local", "EC: ack after all replicas")) {
            int latency = mode.startsWith("EL") ? localMs : localMs + Arrays.stream(remoteRttMs).max().getAsInt();
            boolean remoteFresh = mode.startsWith("EC");
            System.out.printf("%-26s %5d ms        %s%n", mode, latency, remoteFresh ? "new value ✔" : "maybe old value (lag ~" + remoteRttMs[2] / 2 + " ms)");
        }
        // Tunable consistency (Cassandra-style): pick per request
        System.out.println();
        int n = 3; int[] lat = {1, 60, 180};
        for (int w = 1; w <= 3; w++) {
            int[] s = lat.clone(); Arrays.sort(s);
            System.out.printf("W=%d of N=%d -> write waits %3d ms (the %d%s fastest ack)%n", w, n, s[w - 1], w, w == 1 ? "st" : w == 2 ? "nd" : "rd");
        }
        if (r.nextInt() == 0) System.out.println();
    }
}
