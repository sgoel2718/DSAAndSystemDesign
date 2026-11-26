import java.util.*;
import java.util.concurrent.*;

public class NotificationSystem {
    // API -> validation + prefs + dedupe -> per-channel queues (priority) -> workers -> provider with retry/failover -> status tracking.
    record Notification(String id, String user, String channel, String template, Map<String, String> vars, int priority) {}
    static final Map<String, String> templates = Map.of("ORDER_SHIPPED", "Hi {name}, order {orderId} has shipped", "OTP", "Your OTP is {code}");
    static final Map<String, Set<String>> optedOut = Map.of("ravi", Set.of("sms"));
    static final Set<String> dedupe = new HashSet<>();
    static final Map<String, String> status = new TreeMap<>();
    static final Map<String, PriorityQueue<Notification>> queues = new TreeMap<>();

    static String accept(Notification n) {
        if (!dedupe.add(n.id() + ":" + n.channel())) return "duplicate ignored";
        if (optedOut.getOrDefault(n.user(), Set.of()).contains(n.channel())) { status.put(n.id(), "SKIPPED (opted out)"); return "skipped"; }
        queues.computeIfAbsent(n.channel(), k -> new PriorityQueue<>(Comparator.comparingInt(Notification::priority))).add(n);
        status.put(n.id(), "QUEUED"); return "202 queued";
    }
    static String render(Notification n) { String s = templates.get(n.template()); for (var e : n.vars().entrySet()) s = s.replace("{" + e.getKey() + "}", e.getValue()); return s; }

    public static void main(String[] args) {
        System.out.println(accept(new Notification("n1", "asha", "push", "ORDER_SHIPPED", Map.of("name", "Asha", "orderId", "987"), 2)));
        System.out.println(accept(new Notification("n2", "asha", "sms", "OTP", Map.of("code", "482913"), 0)));
        System.out.println(accept(new Notification("n3", "ravi", "sms", "OTP", Map.of("code", "111222"), 0)));
        System.out.println(accept(new Notification("n1", "asha", "push", "ORDER_SHIPPED", Map.of("name", "Asha", "orderId", "987"), 2)));
        System.out.println(accept(new Notification("n4", "zoya", "push", "ORDER_SHIPPED", Map.of("name", "Zoya", "orderId", "990"), 2)));
        int[] smsAttempts = {0};
        Map<String, java.util.function.Predicate<String>> providers = new LinkedHashMap<>();
        providers.put("twilio", msg -> ++smsAttempts[0] > 2);                  // primary SMS provider fails twice
        providers.put("msg91", msg -> true);
        queues.forEach((channel, q) -> {
            while (!q.isEmpty()) {
                Notification n = q.poll(); String msg = render(n); String used = null;
                if (channel.equals("sms")) {
                    for (var p : providers.entrySet()) { for (int attempt = 1; attempt <= 2 && used == null; attempt++) { if (p.getValue().test(msg)) used = p.getKey() + " (attempt " + attempt + ")"; else System.out.println("    " + p.getKey() + " attempt " + attempt + " failed"); } if (used != null) break; }
                } else used = "FCM/APNs";
                status.put(n.id(), "SENT via " + used);
                System.out.println("[" + channel + "] to " + n.user() + ": '" + msg + "' -> " + used);
            }
        });
        System.out.println("status: " + status);
    }
}
