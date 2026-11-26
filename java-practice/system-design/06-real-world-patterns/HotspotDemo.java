import java.util.*;

public class HotspotDemo {
    static int mix(int h) { h ^= h >>> 16; h *= 0x85ebca6b; h ^= h >>> 13; h *= 0xc2b2ae35; return h ^ (h >>> 16); }   // murmur3 finaliser
    public static void main(String[] args) {
        int shards = 5; Random r = new Random(2);
        int[] load = new int[shards], loadFixed = new int[shards];
        for (int i = 0; i < 100_000; i++) {
            String key = r.nextInt(100) < 40 ? "celebrity:1" : "user:" + r.nextInt(1_000_000);   // 40% of traffic hits one key
            load[Math.floorMod(mix(key.hashCode()), shards)]++;
            int home = Math.floorMod(mix(key.hashCode()), shards);
            if (key.equals("celebrity:1")) loadFixed[(home + r.nextInt(shards)) % shards]++;   // copy #i of the hot key lives on shard home+i; readers pick a random copy
            else loadFixed[home]++;
        }
        System.out.println("requests per shard, one hot key : " + Arrays.toString(load));
        System.out.println("hot key copied to all 5 shards   : " + Arrays.toString(loadFixed));
        // Time-based partition key: all of today's writes hit one partition; add a salt
        int[] byDate = new int[8], salted = new int[8];
        for (int i = 0; i < 10_000; i++) { byDate[Math.floorMod("2026-11-26".hashCode(), 8)]++; salted[Math.floorMod(("2026-11-26#" + (i % 8)).hashCode(), 8)]++; }
        System.out.println("partition key = date            : " + Arrays.toString(byDate));
        System.out.println("partition key = (date, i % 8)   : " + Arrays.toString(salted) + "  (reads must query all 8 salts)");
    }
}
