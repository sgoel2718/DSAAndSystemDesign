import java.util.*;

public class ChatDeliveryDemo {
    record Msg(String clientId, String from, String to, String text, long seq) {}
    static final Map<String, List<Msg>> store = new HashMap<>();                 // conversation -> messages
    static final Map<String, Long> seqByConv = new HashMap<>();
    static final Map<String, String> connectedServer = new HashMap<>(Map.of("asha", "chat-A"));   // presence/routing table
    static final Set<String> seenClientIds = new HashSet<>();

    static String conv(String a, String b) { return a.compareTo(b) < 0 ? a + ":" + b : b + ":" + a; }

    static String send(String from, String to, String clientId, String text) {
        if (!seenClientIds.add(clientId)) return "ack (duplicate " + clientId + " ignored)";
        String c = conv(from, to); long seq = seqByConv.merge(c, 1L, Long::sum);
        Msg m = new Msg(clientId, from, to, text, seq);
        store.computeIfAbsent(c, k -> new ArrayList<>()).add(m);                    // persist BEFORE acking
        String server = connectedServer.get(to);
        String delivery = server == null ? to + " offline -> push notification" : "routed to " + server + " -> delivered to " + to;
        return "ack ✓ seq=" + seq + ", " + delivery;
    }

    static List<String> syncAfter(String user, String other, long lastSeq) {
        return store.getOrDefault(conv(user, other), List.of()).stream().filter(m -> m.seq() > lastSeq).map(m -> m.seq() + ":" + m.text()).toList();
    }

    public static void main(String[] args) {
        System.out.println("asha -> ravi 'hi'        : " + send("asha", "ravi", "c-1", "hi"));
        System.out.println("asha -> ravi 'you there?': " + send("asha", "ravi", "c-2", "you there?"));
        System.out.println("network retry of c-2     : " + send("asha", "ravi", "c-2", "you there?"));
        connectedServer.put("ravi", "chat-B");
        System.out.println("ravi reconnects, had seen seq 0 -> sync " + syncAfter("ravi", "asha", 0));
        System.out.println("ravi -> asha 'yes!'      : " + send("ravi", "asha", "c-3", "yes!"));
        System.out.println("asha's phone (seen seq 2) syncs -> " + syncAfter("asha", "ravi", 2));
    }
}
