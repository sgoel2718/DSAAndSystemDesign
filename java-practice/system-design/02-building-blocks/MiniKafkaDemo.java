import java.util.*;

public class MiniKafkaDemo {
    // A topic = N append-only partitions. Producers pick partition = hash(key) % N. Consumers in a group split partitions
    // and keep their own offsets; messages are NOT deleted when read, so another group can read them again.
    static class Topic {
        final List<List<String>> partitions = new ArrayList<>();
        Topic(int n) { for (int i = 0; i < n; i++) partitions.add(new ArrayList<>()); }
        int send(String key, String value) { int p = Math.floorMod(key.hashCode(), partitions.size()); partitions.get(p).add(key + ":" + value); return p; }
    }

    static class ConsumerGroup {
        final String name; final Map<Integer, Integer> committed = new HashMap<>();
        ConsumerGroup(String name) { this.name = name; }
        Map<String, List<Integer>> assign(int partitions, List<String> members) {
            Map<String, List<Integer>> a = new TreeMap<>();
            for (int p = 0; p < partitions; p++) a.computeIfAbsent(members.get(p % members.size()), k -> new ArrayList<>()).add(p);
            return a;
        }
        List<String> poll(Topic t, int partition, int max) {
            int from = committed.getOrDefault(partition, 0);
            List<String> log = t.partitions.get(partition);
            List<String> batch = log.subList(from, Math.min(log.size(), from + max));
            committed.put(partition, from + batch.size());                 // commit after processing -> at-least-once
            return batch;
        }
    }

    public static void main(String[] args) {
        Topic orders = new Topic(3);
        String[][] events = {{"asha", "created"}, {"meera", "created"}, {"asha", "paid"}, {"zoya", "created"}, {"asha", "shipped"}, {"meera", "paid"}};
        for (String[] e : events) System.out.println("produce " + e[0] + ":" + e[1] + " -> partition " + orders.send(e[0], e[1]));
        for (int p = 0; p < 3; p++) System.out.println("partition " + p + " = " + orders.partitions.get(p));
        ConsumerGroup billing = new ConsumerGroup("billing");
        System.out.println("\ngroup 'billing' with 2 consumers: " + billing.assign(3, List.of("c1", "c2")));
        for (int p = 0; p < 3; p++) System.out.println("  billing reads p" + p + " " + billing.poll(orders, p, 10));
        ConsumerGroup analytics = new ConsumerGroup("analytics");
        System.out.println("group 'analytics' reads the same p0 from offset 0: " + analytics.poll(orders, 0, 1) + " then " + analytics.poll(orders, 0, 1));
        System.out.println("asha's events stay in order because they share a key -> same partition.");
    }
}
