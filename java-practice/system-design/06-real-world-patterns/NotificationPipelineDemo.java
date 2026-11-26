import java.util.*;

public class NotificationPipelineDemo {
    record Event(String id, String user, String type, int priority) {}
    record Prefs(boolean push, boolean email, boolean sms, int quietFrom, int quietTo) {}
    static final Map<String, Prefs> prefs = Map.of("asha", new Prefs(true, true, false, 23, 7), "ravi", new Prefs(false, true, true, 0, 0));
    static final Set<String> sent = new HashSet<>();
    static final Map<String, Integer> perUserToday = new HashMap<>();

    static void dispatch(Event e, int hour) {
        Prefs p = prefs.get(e.user());
        List<String> channels = new ArrayList<>();
        if (p.push()) channels.add("push"); if (p.email()) channels.add("email"); if (p.sms() && e.priority() == 1) channels.add("sms");
        for (String ch : channels) {
            String dedupe = e.id() + ":" + ch;
            if (!sent.add(dedupe)) { System.out.println("  skip duplicate " + dedupe); continue; }
            boolean quiet = p.quietFrom() > p.quietTo() ? (hour >= p.quietFrom() || hour < p.quietTo()) : (hour >= p.quietFrom() && hour < p.quietTo());
            if (quiet && e.priority() > 1 && ch.equals("push")) { System.out.println("  " + e.user() + " " + ch + " delayed to morning (quiet hours)"); continue; }
            if (e.priority() > 1 && perUserToday.merge(e.user(), 1, Integer::sum) > 3) { System.out.println("  " + e.user() + " " + ch + " dropped: daily marketing cap"); continue; }
            System.out.println("  -> " + ch + "-queue: " + e.type() + " for " + e.user());
        }
    }

    public static void main(String[] args) {
        System.out.println("23:30 OTP for asha (priority 1):"); dispatch(new Event("e1", "asha", "OTP 482913", 1), 23);
        System.out.println("23:31 promo for asha (priority 3):"); dispatch(new Event("e2", "asha", "Diwali sale", 3), 23);
        System.out.println("10:00 shipment for ravi:"); dispatch(new Event("e3", "ravi", "order shipped", 1), 10);
        System.out.println("10:00 same event delivered twice by the queue:"); dispatch(new Event("e3", "ravi", "order shipped", 1), 10);
    }
}
