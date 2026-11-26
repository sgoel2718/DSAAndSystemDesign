import java.util.*;

public class SchedulerDemo {
    // Jobs table + leases: several scheduler nodes poll; each job is claimed by exactly one node; an expired lease is re-claimed.
    static class Job { final String id; long nextRun; final long every; String owner; long leaseUntil; int runs; Job(String id, long nextRun, long every) { this.id = id; this.nextRun = nextRun; this.every = every; } }
    static final List<Job> jobs = new ArrayList<>(List.of(new Job("daily-report", 0, 60), new Job("cleanup", 10, 30), new Job("invoice", 20, 60)));

    static synchronized List<Job> claimDue(String node, long now) {       // like SELECT ... FOR UPDATE SKIP LOCKED
        List<Job> claimed = new ArrayList<>();
        for (Job j : jobs) if (j.nextRun <= now && (j.owner == null || j.leaseUntil <= now)) { j.owner = node; j.leaseUntil = now + 15; claimed.add(j); }
        return claimed;
    }
    static synchronized void complete(Job j, long now) { j.runs++; j.owner = null; j.nextRun = now + j.every; }

    static boolean invoiceCrashed = false;

    public static void main(String[] args) {
        for (long now = 0; now <= 90; now += 10) {
            List<String> nodes = (now / 10) % 2 == 0 ? List.of("node-A", "node-B") : List.of("node-B", "node-A");   // nodes poll in varying order
            for (String node : nodes) {
                for (Job j : claimDue(node, now)) {
                    boolean crash = j.id.equals("invoice") && !invoiceCrashed;
                    if (crash) { invoiceCrashed = true; System.out.printf("t=%2d %s claimed %-12s and CRASHED (lease until t=%d)%n", now, node, j.id, j.leaseUntil); continue; }
                    complete(j, now);
                    System.out.printf("t=%2d %s ran %-12s next at t=%d%n", now, node, j.id, j.nextRun);
                }
            }
        }
        jobs.forEach(j -> System.out.println(j.id + " ran " + j.runs + " times"));
    }
}
