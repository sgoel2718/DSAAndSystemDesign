import java.util.*;
import java.util.concurrent.*;

public class DistributedJobSchedulerSystem {
    // Jobs bucketed by due minute (time-bucketed table), workers claim with leases, retries with backoff, at-least-once execution.
    record Job(String id, long dueAt, int attempt, int maxAttempts) {}
    static final TreeMap<Long, List<Job>> buckets = new TreeMap<>();
    static final Map<String, Long> leases = new HashMap<>(); static final Map<String, String> results = new TreeMap<>();

    static void schedule(Job j) { buckets.computeIfAbsent(j.dueAt() / 60 * 60, k -> new ArrayList<>()).add(j); }

    public static void main(String[] args) {
        schedule(new Job("send-report", 0, 1, 3)); schedule(new Job("charge-subscription", 30, 1, 3)); schedule(new Job("flaky-webhook", 30, 1, 3));
        schedule(new Job("cleanup", 300, 1, 1));
        Map<String, Integer> failuresLeft = new HashMap<>(Map.of("flaky-webhook", 2));
        for (long now = 0; now <= 420; now += 60) {
            var due = new ArrayList<Job>(); buckets.headMap(now, true).values().forEach(due::addAll); buckets.headMap(now, true).clear();   // only scan buckets that are due
            for (Job j : due) {
                String worker = "worker-" + (Math.abs(j.id().hashCode()) % 3 + 1);
                leases.put(j.id(), now + 30);
                boolean fail = failuresLeft.merge(j.id(), -1, Integer::sum) >= 0 && failuresLeft.get(j.id()) >= 0 && j.id().equals("flaky-webhook");
                if (!fail) { results.put(j.id(), "DONE at t=" + now + " by " + worker + " (attempt " + j.attempt() + ")"); System.out.println("t=" + now + " " + worker + " ran " + j.id() + " ✔"); }
                else if (j.attempt() < j.maxAttempts()) { long backoff = 60L << (j.attempt() - 1); schedule(new Job(j.id(), now + backoff, j.attempt() + 1, j.maxAttempts())); System.out.println("t=" + now + " " + worker + " ran " + j.id() + " ✘ -> retry in " + backoff + " s"); }
                else { results.put(j.id(), "FAILED after " + j.attempt() + " attempts -> dead-letter + alert"); }
                leases.remove(j.id());
            }
        }
        results.forEach((k, v) -> System.out.println(k + ": " + v));
    }
}
