import java.util.*;

public class ShardingDemo {
    interface Router { int shardFor(long userId); }

    public static void main(String[] args) {
        int shards = 4;
        Router range = id -> (int) Math.min(shards - 1, id / 250_000);              // 0-249,999 -> shard 0 ...
        Router hash = id -> Math.floorMod(Long.hashCode(id * 0x9E3779B97F4A7C15L), shards);
        long[] newestUsers = new long[10_000];
        for (int i = 0; i < newestUsers.length; i++) newestUsers[i] = 990_000 + i;    // new signups have the highest ids
        for (var e : Map.of("range", range, "hash ", hash).entrySet()) {
            int[] load = new int[shards];
            for (long id : newestUsers) load[e.getValue().shardFor(id)]++;
            System.out.println(e.getKey() + " sharding, writes from 10,000 new users per shard: " + Arrays.toString(load));
        }
        System.out.println("range sharding puts all new users on the last shard (hotspot); hashing spreads them.");
        // Co-location: shard orders by user_id so a user's orders live with the user -> single-shard query
        Map<Integer, List<String>> shardData = new TreeMap<>();
        long[][] orders = {{42, 9001}, {42, 9002}, {7, 9003}, {500_123, 9004}};
        for (long[] o : orders) shardData.computeIfAbsent(hash.shardFor(o[0]), k -> new ArrayList<>()).add("user" + o[0] + "/order" + o[1]);
        System.out.println("orders keyed by user_id: " + shardData);
        System.out.println("'all orders of user 42' -> query only shard " + hash.shardFor(42));
        System.out.println("'all orders over Rs 1000' -> scatter to all " + shards + " shards and merge (expensive)");
        // Resharding pain with modulo
        int moved = 0;
        for (long id = 0; id < 100_000; id++) if (Math.floorMod(Long.hashCode(id * 0x9E3779B97F4A7C15L), 4) != Math.floorMod(Long.hashCode(id * 0x9E3779B97F4A7C15L), 5)) moved++;
        System.out.printf("going from 4 to 5 shards with hash %% N moves %.0f%% of rows (see consistent hashing)%n", moved / 1000.0);
    }
}
