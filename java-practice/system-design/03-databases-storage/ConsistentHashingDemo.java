import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;

public class ConsistentHashingDemo {
    static final TreeMap<Long, String> ring = new TreeMap<>();
    static final int VNODES = 100;

    static long hash(String s) {
        try { byte[] d = MessageDigest.getInstance("MD5").digest(s.getBytes(StandardCharsets.UTF_8)); long h = 0; for (int i = 0; i < 8; i++) h = (h << 8) | (d[i] & 0xff); return h; }
        catch (Exception e) { throw new RuntimeException(e); }
    }
    static void addServer(String s) { for (int v = 0; v < VNODES; v++) ring.put(hash(s + "#" + v), s); }
    static void removeServer(String s) { ring.values().removeIf(x -> x.equals(s)); }
    static String serverFor(String key) {
        Map.Entry<Long, String> e = ring.ceilingEntry(hash(key));             // next position clockwise
        return (e != null ? e : ring.firstEntry()).getValue();                // wrap around
    }

    static Map<String, String> assign(List<String> keys) { Map<String, String> m = new HashMap<>(); for (String k : keys) m.put(k, serverFor(k)); return m; }

    public static void main(String[] args) {
        List<String> keys = new ArrayList<>(); for (int i = 0; i < 100_000; i++) keys.add("user:" + i);
        for (String s : List.of("A", "B", "C", "D")) addServer(s);
        Map<String, String> before = assign(keys);
        Map<String, Integer> load = new TreeMap<>(); before.values().forEach(s -> load.merge(s, 1, Integer::sum));
        System.out.println("4 servers, 100 vnodes each, load: " + load);
        addServer("E");
        Map<String, String> after = assign(keys);
        long moved = keys.stream().filter(k -> !before.get(k).equals(after.get(k))).count();
        long wrong = keys.stream().filter(k -> !before.get(k).equals(after.get(k)) && !after.get(k).equals("E")).count();
        System.out.printf("add server E: %.1f%% of keys moved (ideal 20%%), all of them to E? %s%n", moved / 1000.0, wrong == 0);
        removeServer("B");
        Map<String, String> afterRemove = assign(keys);
        Map<String, Integer> gained = new TreeMap<>();
        for (String k : keys) if (after.get(k).equals("B")) gained.merge(afterRemove.get(k), 1, Integer::sum);
        System.out.println("remove server B: its keys spread over the survivors " + gained);
        long modMoved = 0; for (int i = 0; i < 100_000; i++) if (Math.floorMod(("user:" + i).hashCode(), 4) != Math.floorMod(("user:" + i).hashCode(), 5)) modMoved++;
        System.out.printf("compare: hash %% N from 4 to 5 servers moves %.1f%% of keys%n", modMoved / 1000.0);
    }
}
