import java.util.*;

public class QuorumDemo {
    record Versioned(long version, String value) {}
    static final Versioned[] replicas = new Versioned[3];
    static final boolean[] down = new boolean[3];

    static boolean write(int w, long version, String value, int... skip) {
        int acks = 0; Set<Integer> s = new HashSet<>(); for (int x : skip) s.add(x);
        for (int i = 0; i < 3; i++) if (!down[i] && !s.contains(i)) { replicas[i] = new Versioned(version, value); acks++; }
        return acks >= w;
    }

    static String read(int r, int[] askOrder) {
        List<Integer> asked = new ArrayList<>(); Versioned best = null;
        for (int i : askOrder) {
            if (asked.size() == r) break;
            if (down[i]) continue;
            asked.add(i);
            if (replicas[i] != null && (best == null || replicas[i].version() > best.version())) best = replicas[i];
        }
        if (asked.size() < r) return "FAILED (only " + asked.size() + " replicas reachable)";
        for (int i : asked) if (best != null && (replicas[i] == null || replicas[i].version() < best.version())) replicas[i] = best;   // read repair
        return best.value() + " (v" + best.version() + ") from replicas " + asked;
    }

    public static void main(String[] args) {
        write(3, 1, "x=5");
        boolean ok = write(2, 2, "x=7", 2);                                    // replica 2 misses the write
        System.out.println("write x=7 with W=2 (replica 2 missed it): " + (ok ? "OK" : "FAIL"));
        System.out.println("R=1 asking replica 2 only     : " + read(1, new int[]{2, 0, 1}) + "  <- stale (R+W = 3, not > 3)");
        System.out.println("R=2 asking replicas 2 then 1  : " + read(2, new int[]{2, 1, 0}) + "  <- overlap guarantees latest");
        System.out.println("replica 2 after read repair   : " + replicas[2]);
        down[0] = true;
        System.out.println("replica 0 down, W=2 write x=9 : " + (write(2, 3, "x=9") ? "OK (2 acks)" : "FAIL"));
        down[1] = true;
        System.out.println("replicas 0,1 down, W=2 write  : " + (write(2, 4, "x=11") ? "OK" : "FAIL (only 1 ack): not available"));
        System.out.println("replicas 0,1 down, R=2 read   : " + read(2, new int[]{0, 1, 2}));
    }
}
