"""Java practice programs: Distributed Systems tab."""
from sd_j_util import J

J("fallacies", r'''
import java.util.*;
import java.util.concurrent.*;

public class UnreliableNetworkDemo {
    // A network that drops, delays and duplicates. A naive client double-charges; a careful one uses timeout + retry + idempotency key.
    static final Random net = new Random(12);
    static final Map<String, Integer> processedKeys = new HashMap<>();
    static int charges = 0;

    static String server(String idemKey, int amount) {
        if (idemKey != null && processedKeys.containsKey(idemKey)) return "OK (duplicate ignored)";
        charges += amount; if (idemKey != null) processedKeys.put(idemKey, amount); return "OK";
    }

    // returns null when the reply is lost or too slow (the client can't tell which)
    static String call(String idemKey, int amount, long timeoutMs) {
        int fate = net.nextInt(10);
        if (fate < 2) return null;                                          // request lost: server never saw it
        String reply = server(idemKey, amount);
        if (fate < 4) return null;                                          // reply lost: server DID charge
        long latency = fate == 9 ? 3000 : 40;                               // occasional very slow reply
        return latency > timeoutMs ? null : reply;
    }

    static void pay(String label, boolean useKey, int attempts) {
        charges = 0; processedKeys.clear();
        String key = useKey ? UUID.nameUUIDFromBytes(label.getBytes()).toString() : null;
        int tries = 0; String r = null;
        while (r == null && tries < attempts) { tries++; r = call(key, 500, 1000); }
        System.out.printf("%-34s tries=%d result=%-22s charged=%d%n", label, tries, r == null ? "gave up (unknown!)" : r, charges);
    }

    public static void main(String[] args) {
        for (int i = 1; i <= 4; i++) pay("retry without idempotency #" + i, false, 5);
        for (int i = 1; i <= 4; i++) pay("retry WITH idempotency key #" + i, true, 5);
        System.out.println("Without a key, a lost reply + retry = charged twice. With a key, retries are safe.");
    }
}
''', ["Add exponential backoff with jitter between retries and print the waits.",
      "Make the timeout 50 ms and count how many 'successful but slow' charges the client wrongly retries.",
      "Add a circuit breaker that stops calling after 3 failures in a row."])

J("cap", r'''
import java.util.*;

public class CapChoiceDemo {
    // 3 replicas; a partition isolates replica C. CP mode requires a majority; AP mode accepts locally and reconciles.
    static class Replica { final String name; int value; long ts; Replica(String n) { name = n; } }
    static final Replica A = new Replica("A"), B = new Replica("B"), C = new Replica("C");
    static Set<Replica> partitionWithC = Set.of(C);

    static List<Replica> reachableFrom(Replica r) { return partitionWithC.contains(r) ? List.of(C) : List.of(A, B); }

    static String write(String mode, Replica at, int v, long ts) {
        List<Replica> reach = reachableFrom(at);
        if (mode.equals("CP") && reach.size() < 2) return "write " + v + " at " + at.name + ": REJECTED (no majority)";
        for (Replica r : reach) { r.value = v; r.ts = ts; }
        return "write " + v + " at " + at.name + ": OK on " + reach.stream().map(r -> r.name).toList();
    }
    static String read(String mode, Replica at) {
        if (mode.equals("CP") && reachableFrom(at).size() < 2) return "read at " + at.name + ": ERROR (can't guarantee latest)";
        return "read at " + at.name + ": " + at.value;
    }
    static void heal() {                                                     // last-write-wins reconciliation
        Replica newest = List.of(A, B, C).stream().max(Comparator.comparingLong(r -> r.ts)).get();
        for (Replica r : List.of(A, B, C)) { r.value = newest.value; r.ts = newest.ts; }
    }

    public static void main(String[] args) {
        for (String mode : List.of("CP", "AP")) {
            A.value = B.value = C.value = 0; A.ts = B.ts = C.ts = 0;
            System.out.println("== " + mode + " ==");
            System.out.println(write(mode, A, 10, 1));
            System.out.println(write(mode, C, 20, 2));
            System.out.println(read(mode, C));
            System.out.println(read(mode, B));
            heal();
            System.out.println("after healing (last write wins): A=" + A.value + " B=" + B.value + " C=" + C.value);
        }
    }
}
''', ["In AP mode, write 20 at C *before* 10 at A (timestamps 1 and 2) and see last-write-wins silently drop an update.",
      "Replace last-write-wins with a merge rule for a shopping cart (union of items).",
      "Move the partition so A is alone, and check which side can still write in CP mode."])

J("pacelc", r'''
import java.util.*;

public class PacelcDemo {
    // No partition: should a write wait for remote replicas (consistency) or return after the local one (latency)?
    public static void main(String[] args) {
        int localMs = 1; int[] remoteRttMs = {2, 60, 180};                // same AZ, Singapore, US
        Random r = new Random(3);
        System.out.println("mode                     write latency   read on remote replica right after");
        for (String mode : List.of("EL: ack after local", "EC: ack after all replicas")) {
            int latency = mode.startsWith("EL") ? localMs : localMs + Arrays.stream(remoteRttMs).max().getAsInt();
            boolean remoteFresh = mode.startsWith("EC");
            System.out.printf("%-26s %5d ms        %s%n", mode, latency, remoteFresh ? "new value ✔" : "maybe old value (lag ~" + remoteRttMs[2] / 2 + " ms)");
        }
        // Tunable consistency (Cassandra-style): pick per request
        System.out.println();
        int n = 3; int[] lat = {1, 60, 180};
        for (int w = 1; w <= 3; w++) {
            int[] s = lat.clone(); Arrays.sort(s);
            System.out.printf("W=%d of N=%d -> write waits %3d ms (the %d%s fastest ack)%n", w, n, s[w - 1], w, w == 1 ? "st" : w == 2 ? "nd" : "rd");
        }
        if (r.nextInt() == 0) System.out.println();
    }
}
''', ["Add a quorum of 2 where replicas are in Mumbai, Chennai and Singapore and compute the write latency from Mumbai.",
      "Simulate 1,000 writes with random jitter on each RTT and print p50/p99 write latency for W=1, 2, 3.",
      "Add the read side: R=1 vs R=2 and show which combinations guarantee fresh reads (R + W > N)."])

J("consistency-models", r'''
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
''', ["Make replicas apply log entries out of order (2 before 1) and detect the causal violation.",
      "Implement 'bounded staleness': allow a replica read only if it is at most 1 entry behind the leader.",
      "Track a per-session token (last LSN seen) and pass it with each request, as many databases do."])

J("quorum", r'''
import java.util.*;

public class QuorumDemo {
    record Versioned(long version, String value) {}
    static final Versioned[] replicas = new Versioned[3];
    static final boolean[] down = new boolean[3];

    static boolean write(int w, long version, String value, int... skip) {
        int acks = 0; Set<Integer> s = new HashSet<>(); for (int x : skip) s.add(x);
        for (int i = 0; i < 3; i++) if (!down[i] && !s.contains(i)) { replicas[i] = new Versioned(version, value); acks++; }
        return acks >= w;
    }

    static String read(int r, int[] askOrder) {
        List<Integer> asked = new ArrayList<>(); Versioned best = null;
        for (int i : askOrder) {
            if (asked.size() == r) break;
            if (down[i]) continue;
            asked.add(i);
            if (replicas[i] != null && (best == null || replicas[i].version() > best.version())) best = replicas[i];
        }
        if (asked.size() < r) return "FAILED (only " + asked.size() + " replicas reachable)";
        for (int i : asked) if (best != null && (replicas[i] == null || replicas[i].version() < best.version())) replicas[i] = best;   // read repair
        return best.value() + " (v" + best.version() + ") from replicas " + asked;
    }

    public static void main(String[] args) {
        write(3, 1, "x=5");
        boolean ok = write(2, 2, "x=7", 2);                                    // replica 2 misses the write
        System.out.println("write x=7 with W=2 (replica 2 missed it): " + (ok ? "OK" : "FAIL"));
        System.out.println("R=1 asking replica 2 only     : " + read(1, new int[]{2, 0, 1}) + "  <- stale (R+W = 3, not > 3)");
        System.out.println("R=2 asking replicas 2 then 1  : " + read(2, new int[]{2, 1, 0}) + "  <- overlap guarantees latest");
        System.out.println("replica 2 after read repair   : " + replicas[2]);
        down[0] = true;
        System.out.println("replica 0 down, W=2 write x=9 : " + (write(2, 3, "x=9") ? "OK (2 acks)" : "FAIL"));
        down[1] = true;
        System.out.println("replicas 0,1 down, W=2 write  : " + (write(2, 4, "x=11") ? "OK" : "FAIL (only 1 ack): not available"));
        System.out.println("replicas 0,1 down, R=2 read   : " + read(2, new int[]{0, 1, 2}));
    }
}
''', ["Try N=5, W=3, R=3 and find how many failures you can tolerate for reads and for writes.",
      "Add 'sloppy quorum + hinted handoff': when a replica is down, write to a spare and hand the data back later.",
      "Use timestamps instead of versions and show what goes wrong when two clients write with skewed clocks."])

J("time-clocks", r'''
import java.util.*;

public class LamportClockDemo {
    static class Process {
        final String name; long clock = 0; final List<String> events = new ArrayList<>();
        Process(String n) { name = n; }
        void local(String what) { clock++; events.add(what + "@" + clock); }
        long send(String what) { clock++; events.add("send " + what + "@" + clock); return clock; }
        void receive(String what, long t) { clock = Math.max(clock, t) + 1; events.add("recv " + what + "@" + clock); }
    }

    public static void main(String[] args) {
        Process p1 = new Process("P1"), p2 = new Process("P2"), p3 = new Process("P3");
        p1.local("a");
        long m1 = p1.send("m1");
        p3.local("x"); p3.local("y");
        p2.receive("m1", m1);
        long m2 = p2.send("m2");
        p3.receive("m2", m2);
        p1.local("b");
        for (Process p : List.of(p1, p2, p3)) System.out.println(p.name + ": " + p.events);
        System.out.println("send m1 (" + m1 + ") < recv m1 on P2 (" + (m1 + 1) + "): causality preserved");
        System.out.println("P1 'b'@3 and P3 'x'@1 are concurrent; Lamport order says x<b but can't tell they're concurrent (use vector clocks)");
        // Wall clocks: skew can reverse order
        long serverA = 1_000_000 + 0, serverB = 1_000_000 - 120;              // B's clock is 120 ms behind
        System.out.println("\nwall clocks: A writes at " + serverA + ", then B overwrites at " + (serverB + 50) + " -> last-write-wins keeps A's older write!");
    }
}
''', ["Total-order all events by (lamport, processName) and print one global order.",
      "Implement a hybrid logical clock (wall time + counter) and show it never goes backwards when the wall clock does.",
      "Simulate 3 processes exchanging 20 random messages and assert every receive has a larger clock than its send."])

J("vector-clocks", r'''
import java.util.*;

public class VectorClockDemo {
    record VC(Map<String, Integer> c) {
        VC tick(String node) { Map<String, Integer> m = new TreeMap<>(c); m.merge(node, 1, Integer::sum); return new VC(m); }
        VC merge(VC o) { Map<String, Integer> m = new TreeMap<>(c); o.c.forEach((k, v) -> m.merge(k, v, Math::max)); return new VC(m); }
        String compare(VC o) {
            boolean le = true, ge = true;
            Set<String> keys = new TreeSet<>(c.keySet()); keys.addAll(o.c.keySet());
            for (String k : keys) { int a = c.getOrDefault(k, 0), b = o.c.getOrDefault(k, 0); if (a > b) le = false; if (a < b) ge = false; }
            return le && ge ? "equal" : le ? "happened-before" : ge ? "happened-after" : "CONCURRENT (conflict)";
        }
        public String toString() { return c.toString(); }
    }
    record Cart(Set<String> items, VC clock) {}

    public static void main(String[] args) {
        Cart start = new Cart(Set.of("milk"), new VC(new TreeMap<>()).tick("A"));
        Cart onA = new Cart(new TreeSet<>(Set.of("milk", "eggs")), start.clock().tick("A"));        // Asha on replica A
        Cart onB = new Cart(new TreeSet<>(Set.of("milk", "bread")), start.clock().tick("B"));       // Ravi on replica B, during a partition
        System.out.println("start " + start.clock() + "  A " + onA.clock() + " " + onA.items() + "  B " + onB.clock() + " " + onB.items());
        System.out.println("start vs A: " + start.clock().compare(onA.clock()));
        System.out.println("A vs B   : " + onA.clock().compare(onB.clock()));
        Set<String> merged = new TreeSet<>(onA.items()); merged.addAll(onB.items());
        Cart resolved = new Cart(merged, onA.clock().merge(onB.clock()).tick("A"));
        System.out.println("merge    : " + resolved.items() + " clock " + resolved.clock());
        System.out.println("resolved vs B: " + resolved.clock().compare(onB.clock()) + " -> B's version can be discarded");
    }
}
''', ["Add a 'remove bread' operation and show why a plain union brings it back (then look at OR-Set CRDTs).",
      "Store multiple sibling versions on the server when concurrent, like Dynamo, and return all of them on read.",
      "Prune vector clocks with more than 3 entries by dropping the oldest node, and explain the risk."])

J("consensus", r'''
import java.util.*;

public class RaftLiteDemo {
    // Simplified Raft: leader election by majority vote with terms, and log replication committed on a majority.
    static class Node {
        final int id; int term = 0; Integer votedFor = null; String role = "follower"; boolean up = true; final List<String> log = new ArrayList<>(); int commitIndex = 0;
        Node(int id) { this.id = id; }
        boolean requestVote(int t, int candidate, int candidateLogLen) {
            if (!up || t < term) return false;
            if (t > term) { term = t; votedFor = null; role = "follower"; }
            if ((votedFor == null || votedFor == candidate) && candidateLogLen >= log.size()) { votedFor = candidate; return true; }
            return false;
        }
        boolean appendEntries(int t, List<String> leaderLog) {
            if (!up || t < term) return false;
            term = t; role = "follower"; log.clear(); log.addAll(leaderLog); return true;
        }
    }
    static final List<Node> cluster = new ArrayList<>();

    static Node elect(Node candidate) {
        candidate.term++; candidate.role = "candidate"; candidate.votedFor = candidate.id; int votes = 1;
        for (Node n : cluster) if (n != candidate && n.requestVote(candidate.term, candidate.id, candidate.log.size())) votes++;
        boolean won = votes > cluster.size() / 2;
        if (won) candidate.role = "leader";
        System.out.println("node " + candidate.id + " runs in term " + candidate.term + ": " + votes + " votes -> " + (won ? "LEADER" : "lost"));
        return won ? candidate : null;
    }

    static void replicate(Node leader, String cmd) {
        leader.log.add(cmd); int acks = 1;
        for (Node n : cluster) if (n != leader && n.appendEntries(leader.term, leader.log)) acks++;
        boolean committed = acks > cluster.size() / 2;
        if (committed) leader.commitIndex = leader.log.size();
        System.out.println("  " + cmd + ": " + acks + "/" + cluster.size() + " acks -> " + (committed ? "COMMITTED" : "not committed (no majority)"));
    }

    public static void main(String[] args) {
        for (int i = 1; i <= 5; i++) cluster.add(new Node(i));
        Node leader = elect(cluster.get(0));
        replicate(leader, "SET x=1"); replicate(leader, "SET y=2");
        leader.up = false; System.out.println("node 1 (leader) crashes");
        Node newLeader = elect(cluster.get(2));
        replicate(newLeader, "SET x=3");
        cluster.get(3).up = false; cluster.get(4).up = false; System.out.println("nodes 4 and 5 crash too (3 of 5 down)");
        replicate(newLeader, "SET z=9");
        System.out.println("node 3 log: " + newLeader.log + ", committed up to index " + newLeader.commitIndex);
        cluster.get(0).up = true; System.out.println("old leader 1 comes back in term " + cluster.get(0).term + " and steps down on seeing term " + newLeader.term);
        cluster.get(0).appendEntries(newLeader.term, newLeader.log.subList(0, newLeader.commitIndex));
        System.out.println("node 1 now: role=" + cluster.get(0).role + " term=" + cluster.get(0).term + " log=" + cluster.get(0).log);
    }
}
''', ["Have two candidates start an election in the same term and show a split vote, then retry with randomised timeouts.",
      "Make a candidate with a shorter log lose the vote (the log up-to-date check).",
      "Apply committed entries to a `Map<String,String>` state machine on every node."])

J("leader-election", r'''
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
''', ["Add a `Storage` class that rejects writes with a token lower than the highest seen, and let node-A try to write.",
      "Implement the bully algorithm: the alive node with the highest id wins.",
      "Run the three nodes as threads with a `ScheduledExecutorService` renewing every 3 ticks."])

J("distributed-locks", r'''
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
''', ["Add lock renewal (a watchdog that extends the TTL while work is in progress).",
      "Run 10 threads that each acquire the lock, increment a shared counter and release; verify the counter is 10.",
      "Implement a reentrant version that counts nested acquisitions by the same owner."])

J("gossip", r'''
import java.util.*;

public class GossipDemo {
    public static void main(String[] args) {
        int n = 1000, fanout = 2; Random r = new Random(8);
        boolean[] knows = new boolean[n]; knows[0] = true;
        int round = 0, informed = 1;
        System.out.println("rumour spreading, " + n + " nodes, each informed node tells " + fanout + " random peers per round");
        while (informed < n) {
            round++;
            boolean[] next = knows.clone();
            for (int i = 0; i < n; i++) if (knows[i]) for (int k = 0; k < fanout; k++) next[r.nextInt(n)] = true;
            knows = next; informed = 0; for (boolean b : knows) if (b) informed++;
            System.out.printf("round %2d: %4d informed%n", round, informed);
        }
        System.out.printf("everyone knows after %d rounds: spreading time grows like log(n), so 10x more nodes adds only a few rounds%n", round);
        // Failure detection with heartbeat counters merged by gossip
        Map<String, long[]> table = new TreeMap<>(Map.of("A", new long[]{1042, 100}, "B", new long[]{988, 99}, "C", new long[]{731, 88}));   // {heartbeat, lastUpdatedAt}
        long now = 100, suspectAfter = 5, deadAfter = 10;
        table.forEach((node, v) -> System.out.println("node " + node + " heartbeat " + v[0] + ", last change " + (now - v[1]) + " s ago -> " + (now - v[1] >= deadAfter ? "DEAD" : now - v[1] >= suspectAfter ? "suspect" : "alive")));
    }
}
''', ["Try fan-out 1, 3 and 5 and plot rounds-to-everyone.",
      "Make 20% of messages get lost and see how many extra rounds it takes.",
      "Implement push-pull: each round a node exchanges full state with one peer and both keep the higher heartbeats."])

J("merkle-anti-entropy", r'''
import java.security.MessageDigest;
import java.util.*;

public class MerkleTreeDemo {
    static String h(String s) { try { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getBytes())).substring(0, 8); } catch (Exception e) { throw new RuntimeException(e); } }

    // Build a tree over 8 key ranges; level 0 = leaves
    static List<List<String>> build(TreeMap<String, String> data) {
        List<String> leaves = new ArrayList<>();
        for (int b = 0; b < 8; b++) { StringBuilder sb = new StringBuilder(); for (var e : data.entrySet()) if (Math.floorMod(e.getKey().hashCode(), 8) == b) sb.append(e); leaves.add(h(sb.toString())); }
        List<List<String>> levels = new ArrayList<>(List.of(leaves));
        while (levels.get(levels.size() - 1).size() > 1) {
            List<String> prev = levels.get(levels.size() - 1), up = new ArrayList<>();
            for (int i = 0; i < prev.size(); i += 2) up.add(h(prev.get(i) + prev.get(i + 1)));
            levels.add(up);
        }
        return levels;
    }

    static int comparisons = 0;
    static void diff(List<List<String>> a, List<List<String>> b, int level, int idx, List<Integer> out) {
        comparisons++;
        if (a.get(level).get(idx).equals(b.get(level).get(idx))) return;      // identical subtree: skip it entirely
        if (level == 0) { out.add(idx); return; }
        diff(a, b, level - 1, idx * 2, out); diff(a, b, level - 1, idx * 2 + 1, out);
    }

    public static void main(String[] args) {
        TreeMap<String, String> r1 = new TreeMap<>(), r2 = new TreeMap<>();
        for (int i = 0; i < 10_000; i++) { r1.put("k" + i, "v" + i); r2.put("k" + i, "v" + i); }
        r2.put("k4242", "STALE"); r2.remove("k777");
        List<List<String>> t1 = build(r1), t2 = build(r2);
        System.out.println("root hashes: " + t1.get(3).get(0) + " vs " + t2.get(3).get(0) + " -> " + (t1.get(3).get(0).equals(t2.get(3).get(0)) ? "in sync" : "differ"));
        List<Integer> bad = new ArrayList<>(); diff(t1, t2, 3, 0, bad);
        int keysToSync = 0; for (String k : r1.keySet()) if (bad.contains(Math.floorMod(k.hashCode(), 8))) keysToSync++;
        System.out.println("differing key ranges " + bad + " found with " + comparisons + " hash comparisons");
        System.out.println("only " + keysToSync + " of 10,000 keys need to be compared/streamed");
    }
}
''', ["Use 1,024 leaf ranges instead of 8 and print how few keys need syncing now.",
      "Finish the repair: for the differing ranges, copy r1's values into r2 and check the roots match.",
      "Update one key and recompute only the hashes on its path to the root (log n work)."])

J("crdt", r'''
import java.util.*;

public class CrdtDemo {
    // PN-Counter: one increment and one decrement slot per replica; merge = max per slot.
    static class PNCounter {
        final String me; final Map<String, Integer> p = new TreeMap<>(), n = new TreeMap<>();
        PNCounter(String me) { this.me = me; }
        void inc(int k) { p.merge(me, k, Integer::sum); }
        void dec(int k) { n.merge(me, k, Integer::sum); }
        int value() { return p.values().stream().mapToInt(i -> i).sum() - n.values().stream().mapToInt(i -> i).sum(); }
        void merge(PNCounter o) { o.p.forEach((k, v) -> p.merge(k, v, Math::max)); o.n.forEach((k, v) -> n.merge(k, v, Math::max)); }
    }

    // OR-Set: each add gets a unique tag; remove deletes only the tags it has seen, so a concurrent add survives.
    static class ORSet {
        final Map<String, Set<String>> adds = new TreeMap<>(); final Set<String> removedTags = new TreeSet<>(); int seq = 0; final String me;
        ORSet(String me) { this.me = me; }
        void add(String x) { adds.computeIfAbsent(x, k -> new TreeSet<>()).add(me + (++seq)); }
        void remove(String x) { removedTags.addAll(adds.getOrDefault(x, Set.of())); }
        Set<String> value() { Set<String> v = new TreeSet<>(); adds.forEach((x, tags) -> { for (String t : tags) if (!removedTags.contains(t)) { v.add(x); break; } }); return v; }
        void merge(ORSet o) { o.adds.forEach((x, t) -> adds.computeIfAbsent(x, k -> new TreeSet<>()).addAll(t)); removedTags.addAll(o.removedTags); }
    }

    public static void main(String[] args) {
        PNCounter a = new PNCounter("A"), b = new PNCounter("B");
        a.inc(3); b.inc(2); b.dec(1);
        System.out.println("likes: A sees " + a.value() + ", B sees " + b.value());
        a.merge(b); b.merge(a); a.merge(b);                                    // duplicate merges are harmless
        System.out.println("after merging both ways (twice): A=" + a.value() + " B=" + b.value());
        ORSet cartA = new ORSet("A"), cartB = new ORSet("B");
        cartA.add("milk"); cartB.merge(cartA);
        cartA.remove("milk");                                                 // Asha removes milk...
        cartB.add("milk");                                                    // ...while Ravi adds milk again, concurrently
        cartB.add("bread");
        cartA.merge(cartB); cartB.merge(cartA);
        System.out.println("cart after concurrent remove/add: A=" + cartA.value() + " B=" + cartB.value() + " (add wins, both converge)");
    }
}
''', ["Implement a G-Set and an LWW-Register and merge them across 3 replicas in random orders; assert they always converge.",
      "Show that merging in any order (A then B, or B then A) gives the same result for the PN-Counter.",
      "Make an OR-Set where remove wins instead, and compare results."])

J("byzantine", r'''
import java.util.*;

public class ByzantineDemo {
    // Majority voting over reported values: works while honest nodes outnumber liars enough.
    static String decide(List<String> reports, int f) {
        Map<String, Integer> votes = new HashMap<>();
        for (String r : reports) votes.merge(r, 1, Integer::sum);
        for (var e : votes.entrySet()) if (e.getValue() >= 2 * f + 1) return e.getKey();      // need 2f+1 matching votes out of 3f+1
        return "NO DECISION";
    }

    public static void main(String[] args) {
        int f = 1;
        List<String> fourNodes = List.of("commit", "commit", "commit", "abort");                 // 3f+1 = 4, one liar
        System.out.println("4 nodes, 1 liar  -> " + decide(fourNodes, f));
        List<String> threeNodes = List.of("commit", "commit", "abort");
        System.out.println("3 nodes, 1 liar  -> " + decide(threeNodes, f) + " (3 < 3f+1, can't tolerate a Byzantine node)");
        List<String> equivocating = List.of("commit", "abort", "commit", "abort");               // liar tells different nodes different things
        System.out.println("liar equivocates -> " + decide(equivocating, f));
        for (int faults = 1; faults <= 3; faults++)
            System.out.printf("tolerate %d faulty: crash faults need %d nodes, Byzantine faults need %d%n", faults, 2 * faults + 1, 3 * faults + 1);
    }
}
''', ["Simulate PBFT-style rounds: pre-prepare, prepare (collect 2f+1), commit (collect 2f+1) with one lying node.",
      "Add message signatures (use `java.security.Signature`) so a liar can't forge other nodes' votes.",
      "Find the smallest number of liars that breaks a 7-node cluster."])

J("unique-id", r'''
import java.util.*;
import java.util.concurrent.*;

public class SnowflakeDemo {
    static class Snowflake {
        static final long EPOCH = 1_700_000_000_000L; final long machine; long lastMs = -1, seq = 0;
        Snowflake(long machine) { if (machine < 0 || machine > 1023) throw new IllegalArgumentException(); this.machine = machine; }
        synchronized long next(long nowMs) {
            if (nowMs < lastMs) throw new IllegalStateException("clock moved backwards");
            if (nowMs == lastMs) {
                seq = (seq + 1) & 4095;
                if (seq == 0) { while (nowMs <= lastMs) nowMs = Math.max(nowMs, System.currentTimeMillis()); }   // 4096 ids used this ms: wait for the next ms
            }
            else seq = 0;
            lastMs = nowMs;
            return ((nowMs - EPOCH) << 22) | (machine << 12) | seq;
        }
        synchronized long next() { return next(System.currentTimeMillis()); }     // read the clock inside the lock
        static String explain(long id) { return String.format("ts=+%dms machine=%d seq=%d", id >>> 22, (id >> 12) & 1023, id & 4095); }
    }

    public static void main(String[] args) throws Exception {
        Snowflake m7 = new Snowflake(7), m8 = new Snowflake(8);
        long now = 1_764_140_000_000L;
        long a = m7.next(now), b = m7.next(now), c = m8.next(now), d = m7.next(now + 1);
        for (long id : new long[]{a, b, c, d}) System.out.println(id + "  " + Snowflake.explain(id));
        System.out.println("sorted by id == sorted by time: " + (a < b && b < d));
        Set<Long> ids = ConcurrentHashMap.newKeySet();
        Snowflake shared = new Snowflake(1); ExecutorService pool = Executors.newFixedThreadPool(8);
        List<Future<?>> fs = new ArrayList<>();
        for (int t = 0; t < 8; t++) fs.add(pool.submit(() -> { for (int i = 0; i < 50_000; i++) ids.add(shared.next()); }));
        try { for (Future<?> f : fs) f.get(); } finally { pool.shutdown(); }
        System.out.println("8 threads x 50,000 ids -> " + ids.size() + " unique");
        try { m7.next(now - 5); } catch (IllegalStateException e) { System.out.println("clock went back 5 ms -> " + e.getMessage() + " (wait or refuse)"); }
        System.out.println("UUIDv4 for comparison: " + UUID.randomUUID().toString().length() + " chars, random order");
    }
}
''', ["Handle a backwards clock by waiting until it catches up (if the gap is < 10 ms) instead of throwing.",
      "Build a 'ticket server' that hands out ranges of 1,000 ids to each app server.",
      "Encode a Snowflake id in base62 for short URLs and decode it back."])

J("bloom-filter", r'''
import java.util.*;

public class BloomFilterDemo {
    final BitSet bits; final int m, k;
    BloomFilterDemo(int expected, double fpRate) {
        m = (int) Math.ceil(-expected * Math.log(fpRate) / (Math.log(2) * Math.log(2)));
        k = Math.max(1, (int) Math.round((double) m / expected * Math.log(2)));
        bits = new BitSet(m);
    }
    int[] positions(String s) {                                         // double hashing: h1 + i*h2
        int h1 = s.hashCode(), h2 = Integer.reverse(h1) * 0x9E3779B9 | 1; int[] p = new int[k];
        for (int i = 0; i < k; i++) p[i] = Math.floorMod(h1 + i * h2, m);
        return p;
    }
    void add(String s) { for (int p : positions(s)) bits.set(p); }
    boolean mightContain(String s) { for (int p : positions(s)) if (!bits.get(p)) return false; return true; }

    public static void main(String[] args) {
        BloomFilterDemo seen = new BloomFilterDemo(100_000, 0.01);
        for (int i = 0; i < 100_000; i++) seen.add("https://site.com/page/" + i);
        System.out.printf("m=%,d bits (%.0f KB), k=%d hash functions for 100,000 URLs%n", seen.m, seen.m / 8.0 / 1024, seen.k);
        int fn = 0; for (int i = 0; i < 100_000; i++) if (!seen.mightContain("https://site.com/page/" + i)) fn++;
        int fp = 0; for (int i = 0; i < 100_000; i++) if (seen.mightContain("https://other.org/x/" + i)) fp++;
        System.out.println("false negatives: " + fn + " (never)");
        System.out.printf("false positives: %d of 100,000 unseen URLs = %.2f%% (target 1%%)%n", fp, fp / 1000.0);
        long setBytes = 100_000L * ("https://site.com/page/99999".length() * 2 + 40);
        System.out.printf("a HashSet<String> of the same URLs would need roughly %.1f MB%n", setBytes / 1e6);
    }
}
''', ["Change the target false-positive rate to 0.1% and see how m and k change.",
      "Build a counting Bloom filter (small counters instead of bits) that supports remove.",
      "Use the filter in front of a slow 'database' lookup and count how many lookups it saves for absent keys."])

J("hyperloglog", r'''
import java.util.*;

public class HyperLogLogDemo {
    final int p = 14, m = 1 << p; final byte[] reg = new byte[m];

    static long hash64(long x) { x ^= x >>> 33; x *= 0xff51afd7ed558ccdL; x ^= x >>> 33; x *= 0xc4ceb9fe1a85ec53L; x ^= x >>> 33; return x; }

    void add(String item) {
        long h = hash64(item.hashCode() * 0x9E3779B97F4A7C15L + item.length());
        int idx = (int) (h >>> (64 - p));                                   // first 14 bits pick a register
        long rest = h << p;
        byte rank = (byte) (Long.numberOfLeadingZeros(rest) + 1);           // position of first 1-bit
        if (rank > reg[idx]) reg[idx] = rank;
    }
    double estimate() {
        double sum = 0; int zeros = 0;
        for (byte r : reg) { sum += Math.pow(2, -r); if (r == 0) zeros++; }
        double alpha = 0.7213 / (1 + 1.079 / m), e = alpha * m * m / sum;
        return (e < 2.5 * m && zeros > 0) ? m * Math.log((double) m / zeros) : e;   // small-range correction
    }

    public static void main(String[] args) {
        HyperLogLogDemo hll = new HyperLogLogDemo(); Set<String> exact = new HashSet<>(); Random r = new Random(2);
        for (int checkpoint : new int[]{1_000, 100_000, 1_000_000}) {
            while (exact.size() < checkpoint) { String u = "user" + r.nextInt(5_000_000); exact.add(u); hll.add(u); hll.add(u); }   // duplicates don't matter
            System.out.printf("true distinct %,9d   HLL estimate %,9.0f   error %+.2f%%%n", exact.size(), hll.estimate(), (hll.estimate() - exact.size()) / exact.size() * 100);
        }
        System.out.printf("HLL memory: %,d bytes; exact HashSet: tens of MB%n", hll.m);
    }
}
''', ["Use p = 10 (1,024 registers) and compare the error (expected ~3.2%).",
      "Merge two HLLs (max per register) for Monday and Tuesday visitors and compare with the true union.",
      "Count distinct words in a long text both exactly and with HLL."])

J("geohash-quadtree", r'''
import java.util.*;

public class GeohashDemo {
    static final String B32 = "0123456789bcdefghjkmnpqrstuvwxyz";

    static String encode(double lat, double lon, int len) {
        double[] la = {-90, 90}, lo = {-180, 180}; StringBuilder sb = new StringBuilder(); boolean even = true; int bit = 0, ch = 0;
        while (sb.length() < len) {
            double[] r = even ? lo : la; double v = even ? lon : lat, mid = (r[0] + r[1]) / 2;
            if (v >= mid) { ch = (ch << 1) | 1; r[0] = mid; } else { ch <<= 1; r[1] = mid; }
            even = !even;
            if (++bit == 5) { sb.append(B32.charAt(ch)); bit = 0; ch = 0; }
        }
        return sb.toString();
    }

    static double km(double lat1, double lon1, double lat2, double lon2) {
        double dLat = Math.toRadians(lat2 - lat1), dLon = Math.toRadians(lon2 - lon1);
        double a = Math.pow(Math.sin(dLat / 2), 2) + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) * Math.pow(Math.sin(dLon / 2), 2);
        return 6371 * 2 * Math.asin(Math.sqrt(a));
    }

    record Driver(String id, double lat, double lon) {}

    public static void main(String[] args) {
        double riderLat = 18.5204, riderLon = 73.8567;                       // Pune
        List<Driver> drivers = List.of(new Driver("d1", 18.5210, 73.8570), new Driver("d2", 18.5300, 73.8470),
            new Driver("d3", 18.6000, 73.7500), new Driver("d4", 19.0760, 72.8777), new Driver("d5", 18.5195, 73.8590));
        Map<String, List<Driver>> cells = new TreeMap<>();
        for (Driver d : drivers) cells.computeIfAbsent(encode(d.lat(), d.lon(), 5), k -> new ArrayList<>()).add(d);
        String riderCell = encode(riderLat, riderLon, 5);
        System.out.println("rider geohash5 = " + riderCell + " (cell ~4.9 km)");
        cells.forEach((c, ds) -> System.out.println("  cell " + c + " -> " + ds.stream().map(Driver::id).toList() + (c.equals(riderCell) ? "  <- rider's cell" : "")));
        List<Driver> candidates = cells.getOrDefault(riderCell, List.of());
        candidates.stream().sorted(Comparator.comparingDouble(d -> km(riderLat, riderLon, d.lat(), d.lon())))
            .forEach(d -> System.out.printf("  nearby %s at %.2f km%n", d.id(), km(riderLat, riderLon, d.lat(), d.lon())));
        System.out.println("prefix property: Pune " + encode(18.52, 73.85, 7) + " vs nearby " + encode(18.53, 73.84, 7) + " vs Mumbai " + encode(19.07, 72.87, 7));
        System.out.println("(a driver just across a cell edge is missed unless you also search the 8 neighbouring cells)");
    }
}
''', ["Implement `neighbours(cell)` by decoding the cell centre, moving one cell width in 8 directions and re-encoding.",
      "Build a point quadtree that splits a cell when it holds more than 2 drivers, and query a radius.",
      "Index 100,000 random drivers in a `TreeMap<String geohash, ...>` and find all with a given 6-char prefix using `subMap`."])

J("trie-structures", r'''
import java.util.*;

public class TypeaheadTrieDemo {
    static class Node { final TreeMap<Character, Node> kids = new TreeMap<>(); long count; List<String> top = new ArrayList<>(); }
    final Node root = new Node(); final int K = 3;

    void add(String q, long count) {
        Node n = root;
        List<Node> path = new ArrayList<>(List.of(root));
        for (char c : q.toCharArray()) { n = n.kids.computeIfAbsent(c, x -> new Node()); path.add(n); }
        n.count += count;
        final long total = n.count;
        for (Node p : path) {                                                     // update cached top-K on the path
            p.top.remove(q); p.top.add(q);
            p.top.sort(Comparator.comparingLong((String s) -> -countOf(s)).thenComparing(s -> s));
            if (p.top.size() > K) p.top.remove(K);
        }
    }
    long countOf(String q) { Node n = root; for (char c : q.toCharArray()) { n = n.kids.get(c); if (n == null) return 0; } return n.count; }
    List<String> suggest(String prefix) {
        Node n = root;
        for (char c : prefix.toCharArray()) { n = n.kids.get(c); if (n == null) return List.of(); }
        return n.top;                                                             // cached: no subtree search
    }

    public static void main(String[] args) {
        TypeaheadTrieDemo t = new TypeaheadTrieDemo();
        Object[][] logs = {{"car", 500}, {"cart", 300}, {"cat", 900}, {"cat videos", 700}, {"catalog", 50}, {"dog", 400}, {"career", 250}};
        for (Object[] l : logs) t.add((String) l[0], (Integer) l[1]);
        for (String p : List.of("c", "ca", "car", "cat", "d", "x")) System.out.println("'" + p + "' -> " + t.suggest(p) + "  (" + p.length() + " node hops)");
        t.add("cart", 1000);                                                      // 'cart' trends
        System.out.println("after 'cart' trends: 'ca' -> " + t.suggest("ca"));
    }
}
''', ["Add `delete(query)` that removes a banned query from every top-K list on its path.",
      "Make suggestions case-insensitive and ignore leading spaces.",
      "Shard the trie by first letter into 3 'servers' and route each prefix to the right shard."])
