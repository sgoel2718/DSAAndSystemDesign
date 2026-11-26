import java.util.*;
import java.util.function.*;

public class LbAlgorithmsDemo {
    record Server(String name, int weight) {}
    static final List<Server> servers = List.of(new Server("A", 1), new Server("B", 1), new Server("C", 2));

    static int rr = 0;
    static Server roundRobin(String user) { return servers.get(rr++ % servers.size()); }

    static int wIdx = 0; static final List<Server> weighted = new ArrayList<>();
    static { for (Server s : servers) for (int i = 0; i < s.weight(); i++) weighted.add(s); }
    static Server weightedRoundRobin(String user) { return weighted.get(wIdx++ % weighted.size()); }

    static final Map<String, Integer> active = new HashMap<>();
    static int tie = 0;
    static Server leastConnections(String user) {
        int min = servers.stream().mapToInt(s -> active.getOrDefault(s.name(), 0)).min().getAsInt();
        List<Server> least = servers.stream().filter(s -> active.getOrDefault(s.name(), 0) == min).toList();
        return least.get(tie++ % least.size());                              // rotate among equally idle servers
    }

    static Server ipHash(String user) { return servers.get(Math.floorMod(user.hashCode(), servers.size())); }

    static final Random rnd = new Random(3);
    static Server powerOfTwo(String user) {
        Server a = servers.get(rnd.nextInt(3)), b = servers.get(rnd.nextInt(3));
        return active.getOrDefault(a.name(), 0) <= active.getOrDefault(b.name(), 0) ? a : b;
    }

    public static void main(String[] args) {
        String[] users = {"u1", "u2", "u3", "u1", "u4", "u5", "u2", "u6"};
        boolean[] slow = {false, false, false, true, false, false, false, false};   // request 4 is a long upload
        Map<String, Function<String, Server>> algos = new LinkedHashMap<>();
        algos.put("round robin      ", LbAlgorithmsDemo::roundRobin);
        algos.put("weighted RR      ", LbAlgorithmsDemo::weightedRoundRobin);
        algos.put("least connections", LbAlgorithmsDemo::leastConnections);
        algos.put("IP/user hash     ", LbAlgorithmsDemo::ipHash);
        algos.put("power of two     ", LbAlgorithmsDemo::powerOfTwo);
        for (var e : algos.entrySet()) {
            active.clear(); tie = 0; StringBuilder sb = new StringBuilder();
            for (int i = 0; i < users.length; i++) {
                Server s = e.getValue().apply(users[i]);
                sb.append(users[i]).append("→").append(s.name()).append("  ");
                if (slow[i]) active.merge(s.name(), 5, Integer::sum);            // long request keeps 5 connections busy
            }
            System.out.println(e.getKey() + ": " + sb);
        }
        System.out.println("IP hash always sends u1 and u2 to the same server (sticky); least connections avoids the server busy with the upload.");
    }
}
