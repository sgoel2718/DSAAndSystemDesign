import java.util.*;

public class EmailServiceSystem {
    // SMTP receive -> spam score -> store message once + per-user mailbox entries -> labels/threads -> full-text search.
    record Message(String id, String from, List<String> to, String subject, String body, String threadId) {}
    static final Map<String, Message> messageStore = new LinkedHashMap<>();
    static final Map<String, Map<String, Set<String>>> mailboxes = new TreeMap<>();      // user -> messageId -> labels
    static final Map<String, Map<String, Set<String>>> searchIndex = new HashMap<>();   // user -> word -> messageIds
    static int seq = 0;

    static double spamScore(Message m) { double s = 0; String t = (m.subject() + " " + m.body()).toLowerCase(); for (String w : List.of("lottery", "winner", "free money", "click here")) if (t.contains(w)) s += 0.3; if (!m.from().endsWith(".com") && !m.from().endsWith(".in")) s += 0.2; return s; }

    static void receive(String from, List<String> to, String subject, String body, String inReplyTo) {
        String id = "m" + (++seq); String thread = inReplyTo != null ? messageStore.get(inReplyTo).threadId() : id;
        Message m = new Message(id, from, to, subject, body, thread); messageStore.put(id, m);           // stored once, even for many recipients
        String label = spamScore(m) >= 0.5 ? "SPAM" : "INBOX";
        for (String u : to) {
            mailboxes.computeIfAbsent(u, k -> new LinkedHashMap<>()).put(id, new TreeSet<>(Set.of(label, "UNREAD")));
            for (String w : (subject + " " + body).toLowerCase().split("\\W+")) searchIndex.computeIfAbsent(u, k -> new HashMap<>()).computeIfAbsent(w, k -> new TreeSet<>()).add(id);
        }
        System.out.printf("%s from %-20s -> %s [%s, spam score %.1f]%n", id, from, to, label, spamScore(m));
    }

    public static void main(String[] args) {
        receive("hr@company.com", List.of("asha@mail.com", "ravi@mail.com"), "Offsite on Friday", "Team offsite at Lonavala", null);
        receive("asha@mail.com", List.of("hr@company.com", "ravi@mail.com"), "Re: Offsite on Friday", "Count me in", "m1");
        receive("prize@win.biz", List.of("asha@mail.com"), "You are a WINNER", "Claim your lottery prize, click here", null);
        System.out.println("asha's inbox: " + mailboxes.get("asha@mail.com"));
        System.out.println("ravi's thread view: " + messageStore.values().stream().filter(m -> m.threadId().equals("m1") && mailboxes.get("ravi@mail.com").containsKey(m.id())).map(Message::subject).toList());
        System.out.println("asha searches 'offsite': " + searchIndex.get("asha@mail.com").get("offsite"));
        System.out.println("messages stored: " + messageStore.size() + ", mailbox entries: " + mailboxes.values().stream().mapToInt(Map::size).sum());
    }
}
