import java.util.*;

public class ReplicationDemo {
    static class Node { final String name; final Map<String, String> data = new HashMap<>(); long appliedLsn; Node(String n) { name = n; } }
    record LogEntry(long lsn, String key, String value) {}

    static final Node leader = new Node("leader");
    static final List<Node> followers = List.of(new Node("f1"), new Node("f2"));
    static final List<LogEntry> wal = new ArrayList<>();

    static long write(String k, String v) { long lsn = wal.size() + 1; wal.add(new LogEntry(lsn, k, v)); leader.data.put(k, v); leader.appliedLsn = lsn; return lsn; }
    static void replicate(Node f, int maxEntries) {                                  // async shipping of the log
        for (LogEntry e : wal) if (e.lsn() > f.appliedLsn && maxEntries-- > 0) { f.data.put(e.key(), e.value()); f.appliedLsn = e.lsn(); }
    }
    static String read(Node n, String k) { return n.name + "(lsn " + n.appliedLsn + ") " + k + "=" + n.data.get(k); }

    public static void main(String[] args) {
        write("bio", "hello");
        followers.forEach(f -> replicate(f, 10));
        long myWrite = write("bio", "system design fan");
        replicate(followers.get(0), 10);                                            // f2 is lagging
        System.out.println("read after write from f1: " + read(followers.get(0), "bio"));
        System.out.println("read after write from f2: " + read(followers.get(1), "bio") + "  <- replication lag, stale");
        // Read-your-writes: only read from a replica that has applied my write's LSN
        Node chosen = followers.stream().filter(f -> f.appliedLsn >= myWrite).findFirst().orElse(leader);
        System.out.println("read-your-writes routing picks " + chosen.name + ": " + read(chosen, "bio"));
        // Leader dies before f2 caught up; promote the most up-to-date follower
        write("bio", "unreplicated write");
        Node promoted = followers.stream().max(Comparator.comparingLong(f -> f.appliedLsn)).get();
        System.out.println("leader crashed; promote " + promoted.name + " (lsn " + promoted.appliedLsn + "); lost write at lsn " + wal.size() + " because replication was async");
    }
}
