import java.util.*;

public class GossipDemo {
    public static void main(String[] args) {
        int n = 1000, fanout = 2; Random r = new Random(8);
        boolean[] knows = new boolean[n]; knows[0] = true;
        int round = 0, informed = 1;
        System.out.println("rumour spreading, " + n + " nodes, each informed node tells " + fanout + " random peers per round");
        while (informed < n) {
            round++;
            boolean[] next = knows.clone();
            for (int i = 0; i < n; i++) if (knows[i]) for (int k = 0; k < fanout; k++) next[r.nextInt(n)] = true;
            knows = next; informed = 0; for (boolean b : knows) if (b) informed++;
            System.out.printf("round %2d: %4d informed%n", round, informed);
        }
        System.out.printf("everyone knows after %d rounds: spreading time grows like log(n), so 10x more nodes adds only a few rounds%n", round);
        // Failure detection with heartbeat counters merged by gossip
        Map<String, long[]> table = new TreeMap<>(Map.of("A", new long[]{1042, 100}, "B", new long[]{988, 99}, "C", new long[]{731, 88}));   // {heartbeat, lastUpdatedAt}
        long now = 100, suspectAfter = 5, deadAfter = 10;
        table.forEach((node, v) -> System.out.println("node " + node + " heartbeat " + v[0] + ", last change " + (now - v[1]) + " s ago -> " + (now - v[1] >= deadAfter ? "DEAD" : now - v[1] >= suspectAfter ? "suspect" : "alive")));
    }
}
