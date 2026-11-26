import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class DistributedLockDemo {
    // Redis-style lock: SET key value NX PX ttl, release only if the value is still ours; storage checks fencing tokens.
    static final ConcurrentHashMap<String, String[]> store = new ConcurrentHashMap<>();   // key -> {owner, expiresAt}
    static final AtomicLong tokenSeq = new AtomicLong();
    static long clock = 0;

    static Long acquire(String key, String owner, long ttl) {
        String[] now = store.compute(key, (k, v) -> v == null || Long.parseLong(v[1]) <= clock ? new String[]{owner, String.valueOf(clock + ttl)} : v);
        return now[0].equals(owner) ? tokenSeq.incrementAndGet() : null;
    }
    static boolean release(String key, String owner) {                 // like the Lua script: GET == owner ? DEL
        return store.computeIfPresent(key, (k, v) -> v[0].equals(owner) ? null : v) == null;
    }

    static long highestTokenSeen = 0; static final List<String> fileWrites = new ArrayList<>();
    static void storageWrite(String who, long token, String data) {
        if (token < highestTokenSeen) { System.out.println("  storage REJECTS " + who + " (token " + token + " < " + highestTokenSeen + ")"); return; }
        highestTokenSeen = token; fileWrites.add(data); System.out.println("  storage accepts " + who + " token " + token + ": " + data);
    }

    public static void main(String[] args) {
        Long t1 = acquire("lock:invoice:9", "worker-1", 30);
        System.out.println("t=0  worker-1 acquire -> token " + t1);
        System.out.println("t=0  worker-2 acquire -> " + acquire("lock:invoice:9", "worker-2", 30) + " (held)");
        clock = 40;                                                      // worker-1 paused longer than the TTL
        Long t2 = acquire("lock:invoice:9", "worker-2", 30);
        System.out.println("t=40 lock expired, worker-2 acquire -> token " + t2);
        storageWrite("worker-2", t2, "invoice 9 = PAID");
        storageWrite("worker-1", t1, "invoice 9 = PENDING (stale!)");
        System.out.println("t=41 worker-1 release -> " + (release("lock:invoice:9", "worker-1") ? "released" : "refused: not the owner anymore"));
        System.out.println("t=42 worker-2 release -> " + (release("lock:invoice:9", "worker-2") ? "released" : "refused"));
        System.out.println("final file: " + fileWrites);
    }
}
