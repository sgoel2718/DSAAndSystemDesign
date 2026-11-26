import java.util.*;

public class SystemGrowthDemo {
    // A tiny model of how design choices change capacity as users grow.
    record Stage(String name, int appServers, boolean cache, int readReplicas) {
        double appCapacity() { return appServers * 1_000.0; }                          // each app server: ~1k req/s
        double dbCapacity() { return 5_000.0 * (1 + readReplicas) / (cache ? 0.1 : 1.0); } // 5k reads/s per DB node; cache absorbs 90%
        double capacity() { return Math.min(appCapacity(), dbCapacity()); }
        String bottleneck() { return appCapacity() <= dbCapacity() ? "app servers" : "database"; }
    }

    public static void main(String[] args) {
        List<Stage> stages = List.of(
            new Stage("1 server", 1, false, 0),
            new Stage("LB + 4 app servers", 4, false, 0),
            new Stage("LB + 12 app servers", 12, false, 0),
            new Stage("+ Redis cache", 12, true, 0),
            new Stage("+ 60 app servers, 2 replicas", 60, true, 2));
        int[] loads = {3_500, 8_000, 30_000};
        for (int load : loads) {
            System.out.printf("%nPeak load %,d req/s%n", load);
            for (Stage s : stages) {
                boolean ok = s.capacity() >= load;
                System.out.printf("  %-30s capacity %,9.0f  %s%n", s.name(), s.capacity(), ok ? "OK" : "overloaded, bottleneck: " + s.bottleneck());
            }
        }
    }
}
