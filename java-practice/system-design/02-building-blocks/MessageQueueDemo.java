import java.util.*;

public class MessageQueueDemo {
    // An SQS-style queue: receive hides the message for a visibility timeout; ACK deletes it; un-acked messages reappear;
    // after maxReceives the message goes to a dead-letter queue.
    record Msg(String id, String body) {}
    static class Queue {
        final Deque<Msg> ready = new ArrayDeque<>(); final Map<String, Long> invisibleUntil = new HashMap<>(); final Map<String, Msg> inFlight = new HashMap<>();
        final Map<String, Integer> receives = new HashMap<>(); final List<Msg> dlq = new ArrayList<>(); final long visibility = 30; final int maxReceives = 3;
        void send(Msg m) { ready.addLast(m); }
        Optional<Msg> receive(long now) {
            inFlight.entrySet().removeIf(e -> { if (invisibleUntil.get(e.getKey()) <= now) { ready.addLast(e.getValue()); return true; } return false; });
            Msg m = ready.pollFirst(); if (m == null) return Optional.empty();
            int n = receives.merge(m.id(), 1, Integer::sum);
            if (n > maxReceives) { dlq.add(m); return receive(now); }
            inFlight.put(m.id(), m); invisibleUntil.put(m.id(), now + visibility); return Optional.of(m);
        }
        void ack(String id) { inFlight.remove(id); }
    }

    public static void main(String[] args) {
        Queue q = new Queue();
        q.send(new Msg("m1", "transcode video 7")); q.send(new Msg("m2", "send email 9")); q.send(new Msg("m3", "corrupt file"));
        long t = 0;
        for (int round = 0; round < 7; round++, t += 31) {
            Optional<Msg> m = q.receive(t);
            if (m.isEmpty()) { System.out.println("t=" + t + " queue empty, DLQ=" + q.dlq); continue; }
            Msg msg = m.get();
            boolean workerCrashes = msg.id().equals("m1") && round == 0;
            boolean poison = msg.id().equals("m3");
            if (workerCrashes) System.out.println("t=" + t + " worker took " + msg.id() + " and crashed (no ACK) -> will reappear after 30 s");
            else if (poison) System.out.println("t=" + t + " worker failed on " + msg.id() + " (receive #" + q.receives.get("m3") + ")");
            else { q.ack(msg.id()); System.out.println("t=" + t + " processed " + msg.id() + " '" + msg.body() + "' and ACKed"); }
        }
    }
}
