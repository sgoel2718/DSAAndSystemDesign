import java.util.*;

public class DistributedFileSystemSystem {
    // Master keeps namespace + chunk locations; chunkservers store 64 MB chunks x3 replicas; client asks master once, then talks to chunkservers;
    // heartbeats detect dead servers and the master re-replicates under-replicated chunks.
    static final long CHUNK = 64L << 20;
    static final Map<String, List<String>> fileChunks = new TreeMap<>();                // path -> chunk handles
    static final Map<String, Set<String>> chunkLocations = new TreeMap<>();             // handle -> servers
    static final Map<String, Long> lastHeartbeat = new TreeMap<>();
    static int handleSeq = 0; static int rr = 0;

    static void create(String path, long size, List<String> servers) {
        List<String> handles = new ArrayList<>();
        for (long off = 0; off < size; off += CHUNK) {
            String h = "chunk-" + (++handleSeq); handles.add(h); Set<String> reps = new TreeSet<>();
            while (reps.size() < 3) reps.add(servers.get(rr++ % servers.size()));        // rack-aware placement in real life
            chunkLocations.put(h, reps);
        }
        fileChunks.put(path, handles);
    }

    public static void main(String[] args) {
        List<String> servers = List.of("cs1", "cs2", "cs3", "cs4", "cs5"); servers.forEach(s -> lastHeartbeat.put(s, 0L));
        create("/logs/2026-11-26.log", 200L << 20, servers);
        System.out.println("/logs/2026-11-26.log (200 MB) -> " + fileChunks.get("/logs/2026-11-26.log").size() + " chunks");
        chunkLocations.forEach((h, rs) -> System.out.println("  " + h + " on " + rs));
        long offset = 150L << 20; String h = fileChunks.get("/logs/2026-11-26.log").get((int) (offset / CHUNK));
        System.out.println("client reads offset 150 MB -> master says " + h + " on " + chunkLocations.get(h) + "; data flows directly from a chunkserver, not the master");
        for (String s : servers) if (!s.equals("cs2")) lastHeartbeat.put(s, 60L);           // cs2 stopped sending heartbeats
        long now = 60;
        List<String> dead = lastHeartbeat.entrySet().stream().filter(e -> now - e.getValue() > 30).map(Map.Entry::getKey).toList();
        System.out.println("t=60 heartbeat check -> dead: " + dead);
        for (var e : chunkLocations.entrySet()) {
            if (e.getValue().removeAll(dead)) {
                String target = servers.stream().filter(s -> !dead.contains(s) && !e.getValue().contains(s)).findFirst().get();
                e.getValue().add(target);
                System.out.println("  re-replicate " + e.getKey() + " to " + target + " -> " + e.getValue());
            }
        }
    }
}
