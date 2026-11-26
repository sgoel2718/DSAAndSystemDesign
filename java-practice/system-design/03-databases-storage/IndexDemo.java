import java.util.*;

public class IndexDemo {
    record User(int id, String email, String country, String city, int age) {}

    public static void main(String[] args) {
        int n = 1_000_000; Random r = new Random(4);
        String[] countries = {"IN", "US", "DE"}, cities = {"Pune", "Delhi", "Austin", "Berlin"};
        List<User> table = new ArrayList<>(n);
        for (int i = 0; i < n; i++) table.add(new User(i, String.format("user%07d@x.com", i), countries[r.nextInt(3)], cities[r.nextInt(4)], 18 + r.nextInt(50)));
        String target = "user0777777@x.com";
        // Full table scan
        int scanned = 0; User found = null;
        for (User u : table) { scanned++; if (u.email().equals(target)) { found = u; break; } }
        System.out.println("full scan     : found id " + found.id() + " after reading " + String.format("%,d", scanned) + " rows");
        // B-tree-like sorted index: TreeMap (red-black tree) email -> row id
        TreeMap<String, Integer> emailIdx = new TreeMap<>();
        for (User u : table) emailIdx.put(u.email(), u.id());
        int depth = (int) Math.ceil(Math.log(n) / Math.log(2));
        System.out.println("tree index    : found id " + emailIdx.get(target) + " in ~" + depth + " comparisons (a B+ tree with fan-out 500 needs ~3 page reads)");
        // Range scan uses the sorted order
        System.out.println("range scan    : emails from 'user0100000' to 'user0100100' -> " + emailIdx.subMap("user0100000", "user0100100").size() + " rows, read in order without scanning the table");
        // Composite index (country, city, age): works for leftmost prefixes
        TreeMap<String, List<Integer>> composite = new TreeMap<>();
        for (User u : table) composite.computeIfAbsent(u.country() + "|" + u.city() + "|" + String.format("%03d", u.age()), k -> new ArrayList<>()).add(u.id());
        int prefixRows = composite.subMap("IN|Pune|", "IN|Pune|~").values().stream().mapToInt(List::size).sum();
        int prefixAge = composite.subMap("IN|Pune|030", "IN|Pune|~").values().stream().mapToInt(List::size).sum();
        System.out.println("composite     : country=IN AND city=Pune -> " + prefixRows + " rows via prefix seek");
        System.out.println("composite     : ... AND age >= 30        -> " + prefixAge + " rows, still a range seek");
        System.out.println("composite     : city=Pune alone can't use it (not a leftmost prefix) -> full scan");
        System.out.println("write cost    : each insert now updates the table + " + 2 + " indexes");
    }
}
