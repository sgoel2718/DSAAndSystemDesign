import java.util.*;

public class LeaseElectionDemo {
    // A coordination store (like etcd) holding /leader with a lease; nodes renew; when renewal stops the lease expires.
    static String leader = null; static long leaseExpires = 0; static long fencingToken = 0;

    static synchronized Optional<Long> tryAcquire(String node, long now, long ttl) {
        if (leader == null || leaseExpires <= now) { leader = node; leaseExpires = now + ttl; return Optional.of(++fencingToken); }
        return Optional.empty();
    }
    static synchronized boolean renew(String node, long now, long ttl) {
        if (node.equals(leader) && leaseExpires > now) { leaseExpires = now + ttl; return true; } return false;
    }

    public static void main(String[] args) {
        Map<String, Long> tokens = new HashMap<>();
        Set<String> paused = new HashSet<>();
        long ttl = 10;
        for (long t = 0; t <= 40; t += 5) {
            if (t == 15) { paused.add("node-A"); System.out.println("t=15 node-A freezes (GC pause)"); }
            if (t == 35) { paused.remove("node-A"); System.out.println("t=35 node-A wakes up"); }
            for (String n : List.of("node-A", "node-B", "node-C")) {
                if (paused.contains(n)) continue;
                if (n.equals(leader)) { if (renew(n, t, ttl)) continue; }
                Optional<Long> tok = tryAcquire(n, t, ttl);
                if (tok.isPresent()) { tokens.put(n, tok.get()); System.out.println("t=" + t + " " + n + " became leader with fencing token " + tok.get()); }
            }
        }
        System.out.println("node-A still holds token " + tokens.get("node-A") + " but the storage has seen token " + fencingToken + " -> its writes get rejected");
    }
}
