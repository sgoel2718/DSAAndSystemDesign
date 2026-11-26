import java.util.*;

public class ChatSystem {
    // Connection registry (which gateway holds each user), per-conversation sequence numbers, persistence before ack,
    // offline delivery + sync, group fan-out, and delivered/read receipts.
    record Message(String conv, long seq, String from, String text) {}
    static final Map<String, String> sessions = new HashMap<>();                    // user -> gateway server
    static final Map<String, List<Message>> store = new HashMap<>();
    static final Map<String, List<String>> members = new HashMap<>();
    static final Map<String, Map<String, Long>> readUpTo = new HashMap<>();          // conv -> user -> seq
    static final Map<String, List<String>> pushQueue = new TreeMap<>();

    static void send(String conv, String from, String text) {
        List<Message> log = store.computeIfAbsent(conv, k -> new ArrayList<>());
        Message m = new Message(conv, log.size() + 1, from, text); log.add(m);           // 1. persist
        System.out.println(from + " -> " + conv + " #" + m.seq() + " '" + text + "' ✓ (stored)");
        for (String u : members.get(conv)) {                                         // 2. fan out to members
            if (u.equals(from)) continue;
            String gw = sessions.get(u);
            if (gw != null) System.out.println("    deliver to " + u + " via " + gw + " ✓✓");
            else pushQueue.computeIfAbsent(u, k -> new ArrayList<>()).add(conv + "#" + m.seq());
        }
    }
    static void connect(String user, String gw) {
        sessions.put(user, gw);
        for (var e : members.entrySet()) if (e.getValue().contains(user)) {
            long last = readUpTo.computeIfAbsent(e.getKey(), k -> new HashMap<>()).getOrDefault(user, 0L);
            List<String> missed = store.getOrDefault(e.getKey(), List.of()).stream().filter(m -> m.seq() > last && !m.from().equals(user)).map(m -> m.seq() + ":" + m.text()).toList();
            if (!missed.isEmpty()) System.out.println(user + " connects to " + gw + ", syncs " + e.getKey() + " after #" + last + " -> " + missed);
        }
    }
    static void read(String user, String conv) { long top = store.get(conv).size(); readUpTo.computeIfAbsent(conv, k -> new HashMap<>()).put(user, top); System.out.println(user + " read " + conv + " up to #" + top + " (blue ticks sent to sender)"); }

    public static void main(String[] args) {
        members.put("dm:asha:ravi", List.of("asha", "ravi")); members.put("group:trip", List.of("asha", "ravi", "zoya", "kiran"));
        sessions.put("asha", "gw-1"); sessions.put("zoya", "gw-3");
        send("dm:asha:ravi", "asha", "Are you coming?");
        send("group:trip", "asha", "Goa in December?");
        send("group:trip", "zoya", "Yes!!");
        System.out.println("offline push notifications: " + pushQueue);
        connect("ravi", "gw-2"); read("ravi", "group:trip");
        send("group:trip", "ravi", "Count me in");
    }
}
