import java.util.*;

public class DistributedLogQueueSystem {
    // Partitioned, replicated log: leader + followers per partition, acks=all with ISR, high-watermark, consumer offsets, leader failover.
    static class Replica { final String broker; final List<String> log = new ArrayList<>(); boolean alive = true; Replica(String b) { broker = b; } }
    static class Partition {
        final List<Replica> replicas; Replica leader; long highWatermark = 0;
        Partition(List<Replica> r) { replicas = r; leader = r.get(0); }
        String produce(String msg, int minInSync) {
            List<Replica> isr = replicas.stream().filter(r -> r.alive).toList();
            if (isr.size() < minInSync) return "REJECTED (not enough in-sync replicas)";
            for (Replica r : isr) r.log.add(msg);                                   // leader appends, followers fetch
            highWatermark = leader.log.size();                                       // committed = replicated to all ISR
            return "acked at offset " + (highWatermark - 1) + " on " + isr.stream().map(r -> r.broker).toList();
        }
        List<String> consume(long from) { return leader.log.subList((int) from, (int) highWatermark); }
        void failover() { leader.alive = false; leader = replicas.stream().filter(r -> r.alive).max(Comparator.comparingInt(r -> r.log.size())).get(); }
    }

    public static void main(String[] args) {
        Partition p0 = new Partition(List.of(new Replica("broker-1"), new Replica("broker-2"), new Replica("broker-3")));
        for (String m : List.of("order-1", "order-2", "order-3")) System.out.println("produce " + m + " -> " + p0.produce(m, 2));
        long committedOffset = 0;
        List<String> batch = p0.consume(committedOffset); committedOffset += batch.size();
        System.out.println("consumer group 'billing' read " + batch + ", committed offset " + committedOffset);
        p0.failover(); System.out.println("broker-1 (leader) dies -> new leader " + p0.leader.broker + " with " + p0.leader.log.size() + " messages (nothing committed was lost)");
        System.out.println("produce order-4 -> " + p0.produce("order-4", 2));
        System.out.println("billing resumes from offset " + committedOffset + " -> " + p0.consume(committedOffset));
        p0.replicas.get(1).alive = false;
        System.out.println("broker-2 also dies; produce order-5 with min.insync=2 -> " + p0.produce("order-5", 2));
    }
}
