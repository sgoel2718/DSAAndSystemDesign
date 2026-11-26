import java.util.*;

public class ServiceDiscoveryDemo {
    record Instance(String service, String address) {}
    static class Registry {
        final Map<String, Map<String, Long>> instances = new TreeMap<>();      // service -> (address -> last heartbeat)
        void register(Instance i, long now) { instances.computeIfAbsent(i.service(), k -> new TreeMap<>()).put(i.address(), now); }
        void heartbeat(Instance i, long now) { register(i, now); }
        List<String> lookup(String service, long now) {
            return instances.getOrDefault(service, Map.of()).entrySet().stream().filter(e -> now - e.getValue() <= 10).map(Map.Entry::getKey).toList();
        }
    }

    public static void main(String[] args) {
        Registry reg = new Registry();
        Instance p1 = new Instance("payment", "10.0.3.7:8080"), p2 = new Instance("payment", "10.0.3.9:8080");
        reg.register(p1, 0); reg.register(p2, 0);
        System.out.println("t=0  payment -> " + reg.lookup("payment", 0));
        reg.heartbeat(p2, 8);                                               // p1 stopped sending heartbeats (crashed)
        System.out.println("t=12 payment -> " + reg.lookup("payment", 12) + " (10.0.3.7 missed heartbeats, removed)");
        Instance p3 = new Instance("payment", "10.0.4.2:8080"); reg.register(p3, 13);    // autoscaler added an instance
        List<String> live = reg.lookup("payment", 14);
        System.out.println("t=14 payment -> " + live);
        for (int i = 0; i < 4; i++) System.out.println("  order-svc call " + (i + 1) + " -> " + live.get(i % live.size()) + "  (client-side round robin)");
    }
}
