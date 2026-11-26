import java.util.*;

public class DisasterRecoveryDemo {
    record Strategy(String name, int rpoMin, int rtoMin, int costPerMonth) {}

    public static void main(String[] args) {
        List<Strategy> s = List.of(new Strategy("backup & restore (daily)", 24 * 60, 8 * 60, 200), new Strategy("pilot light", 15, 45, 1_500),
            new Strategy("warm standby", 1, 10, 6_000), new Strategy("multi-site active-active", 0, 1, 20_000));
        int maxRpo = 30, maxRto = 60;                                     // business requirement
        System.out.println("requirement: lose at most " + maxRpo + " min of data, be back within " + maxRto + " min");
        Strategy pick = null;
        for (Strategy x : s) {
            boolean ok = x.rpoMin() <= maxRpo && x.rtoMin() <= maxRto;
            System.out.printf("  %-26s RPO %5d min  RTO %4d min  $%,6d/month  %s%n", x.name(), x.rpoMin(), x.rtoMin(), x.costPerMonth(), ok ? "meets it" : "too slow");
            if (ok && pick == null) pick = x;
        }
        System.out.println("cheapest that meets it: " + pick.name());
        // Restore drill: rebuild state from the last snapshot + replayed log, and verify
        Map<String, Integer> prod = new TreeMap<>(Map.of("a", 1, "b", 2, "c", 3));
        Map<String, Integer> snapshot = new TreeMap<>(prod);
        List<String[]> logSinceSnapshot = List.of(new String[]{"a", "10"}, new String[]{"d", "4"});
        for (String[] op : logSinceSnapshot) prod.put(op[0], Integer.parseInt(op[1]));
        Map<String, Integer> restored = new TreeMap<>(snapshot); for (String[] op : logSinceSnapshot) restored.put(op[0], Integer.parseInt(op[1]));
        System.out.println("restore drill: restored == production? " + restored.equals(prod) + " " + restored);
    }
}
