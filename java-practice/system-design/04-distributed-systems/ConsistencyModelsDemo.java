import java.util.*;

public class ConsistencyModelsDemo {
    // A leader and two lagging replicas. Compare what a reader sees under different guarantees.
    record Version(long lsn, String text) {}
    static final List<Version> log = new ArrayList<>();
    static final Map<String, Long> replicaLsn = new HashMap<>(Map.of("leader", 0L, "r1", 0L, "r2", 0L));

    static void write(String text) { log.add(new Version(log.size() + 1, text)); replicaLsn.put("leader", (long) log.size()); }
    static String readAt(String node) { long lsn = replicaLsn.get(node); return lsn == 0 ? "(nothing)" : log.get((int) lsn - 1).text(); }

    public static void main(String[] args) {
        write("Asha: hi"); write("Ravi: hello Asha");
        replicaLsn.put("r1", 2L); replicaLsn.put("r2", 0L);                  // r2 is far behind
        System.out.println("eventual      : random replicas -> r1 '" + readAt("r1") + "', then r2 '" + readAt("r2") + "'  (went back in time!)");
        long seen = 0; StringBuilder sb = new StringBuilder();
        for (String node : List.of("r1", "r2", "r1")) {                          // monotonic reads: skip replicas behind what I've seen
            String chosen = replicaLsn.get(node) >= seen ? node : "leader";
            seen = Math.max(seen, replicaLsn.get(chosen));
            sb.append(chosen).append(" '").append(readAt(chosen)).append("'  ");
        }
        System.out.println("monotonic     : " + sb);
        write("Asha: how are you?");                                             // Asha's own write, lsn 3
        long myLsn = log.size();
        String node = replicaLsn.get("r1") >= myLsn ? "r1" : "leader";
        System.out.println("read-your-own : Asha reads from " + node + " -> '" + readAt(node) + "'");
        // causal: a reply must never appear without the message it answers
        replicaLsn.put("r2", 2L);
        boolean replyVisible = replicaLsn.get("r2") >= 2, originalVisible = replicaLsn.get("r2") >= 1;
        System.out.println("causal        : on r2 reply visible=" + replyVisible + ", original visible=" + originalVisible + " -> " + (replyVisible && !originalVisible ? "VIOLATION" : "OK, cause before effect"));
        System.out.println("linearizable  : read from the leader every time -> '" + readAt("leader") + "' (always latest, slowest)");
    }
}
