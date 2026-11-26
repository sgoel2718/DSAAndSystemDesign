import java.util.*;

public class DbScalingPathDemo {
    // A capacity model of a database tier; each step is applied only when the load needs it.
    record Tier(String step, double readCap, double writeCap) {}

    public static void main(String[] args) {
        double reads = 30_000, writes = 3_000;                           // target load per second
        List<Tier> path = new ArrayList<>();
        double readCap = 2_000, writeCap = 1_000;                         // one unoptimised DB
        path.add(new Tier("start: 1 DB, missing indexes", readCap, writeCap));
        readCap *= 2.5; writeCap *= 1.5; path.add(new Tier("1 add indexes, fix N+1 queries", readCap, writeCap));
        readCap *= 2; writeCap *= 2; path.add(new Tier("2 bigger machine (2x)", readCap, writeCap));
        readCap /= 0.2; path.add(new Tier("3 Redis cache, 80% hit ratio", readCap, writeCap));
        readCap += 3 * 10_000; path.add(new Tier("4 + 3 read replicas", readCap, writeCap));
        writeCap *= 4; path.add(new Tier("5 shard writes across 4 primaries", readCap, writeCap));
        System.out.printf("target: %,.0f reads/s, %,.0f writes/s%n", reads, writes);
        for (Tier t : path) {
            boolean ok = t.readCap() >= reads && t.writeCap() >= writes;
            System.out.printf("%-34s reads %,8.0f  writes %,6.0f  %s%n", t.step(), t.readCap(), t.writeCap(),
                ok ? "✔ enough" : "✘ short on " + (t.readCap() < reads ? "reads" : "") + (t.readCap() < reads && t.writeCap() < writes ? " + " : "") + (t.writeCap() < writes ? "writes" : ""));
        }
        System.out.println("Do the cheap steps first; sharding is last because it costs joins, transactions and operations.");
    }
}
