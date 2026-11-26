import java.util.*;

public class NoSqlTypesDemo {
    public static void main(String[] args) {
        // Key-value: opaque value, get by key only
        Map<String, String> kv = new HashMap<>();
        kv.put("session:abc", "{user:42, cart:[sku1]}");
        System.out.println("key-value   GET session:abc -> " + kv.get("session:abc"));
        // Document: nested fields you can query/index
        List<Map<String, Object>> products = List.of(
            Map.of("_id", 1, "name", "Shoes", "tags", List.of("sport", "running"), "price", 2499),
            Map.of("_id", 2, "name", "Kettle", "tags", List.of("home"), "price", 999));
        System.out.println("document    find tags contains 'sport' -> " + products.stream().filter(p -> ((List<?>) p.get("tags")).contains("sport")).map(p -> p.get("name")).toList());
        // Wide-column: partition key -> rows sorted by clustering key (like Cassandra)
        Map<String, TreeMap<Long, String>> messages = new HashMap<>();
        long[] ts = {1005, 1001, 1003, 1010};
        for (long t : ts) messages.computeIfAbsent("chat:42", k -> new TreeMap<>(Comparator.reverseOrder())).put(t, "msg@" + t);
        System.out.println("wide-column chat:42 latest 3 -> " + messages.get("chat:42").values().stream().limit(3).toList() + " (one partition, already sorted)");
        // Graph: adjacency lists + traversal (friends of friends)
        Map<String, List<String>> follows = Map.of("asha", List.of("ravi", "zoya"), "ravi", List.of("meera", "zoya"), "zoya", List.of("kiran"), "meera", List.of(), "kiran", List.of());
        Set<String> fof = new TreeSet<>();
        for (String f : follows.get("asha")) fof.addAll(follows.get(f));
        fof.removeAll(follows.get("asha")); fof.remove("asha");
        System.out.println("graph       people asha may know (2 hops) -> " + fof);
    }
}
