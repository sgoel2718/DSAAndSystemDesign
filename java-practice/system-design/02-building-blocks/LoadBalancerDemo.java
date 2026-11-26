import java.util.*;

public class LoadBalancerDemo {
    static class Backend {
        final String name; boolean alive = true, healthy = true; int failedChecks, served;
        Backend(String name) { this.name = name; }
        boolean healthCheck() { return alive; }                             // real LB: GET /health with a timeout
    }

    static class LoadBalancer {
        final List<Backend> pool; int next = 0; final int unhealthyAfter = 3;
        LoadBalancer(List<Backend> pool) { this.pool = pool; }
        void runHealthChecks() {
            for (Backend b : pool) {
                if (b.healthCheck()) { b.failedChecks = 0; if (!b.healthy) System.out.println("  health: " + b.name + " back in pool"); b.healthy = true; }
                else if (++b.failedChecks >= unhealthyAfter && b.healthy) { b.healthy = false; System.out.println("  health: " + b.name + " removed after 3 failed checks"); }
            }
        }
        String route(int reqId) {
            for (int i = 0; i < pool.size(); i++) {
                Backend b = pool.get(next++ % pool.size());
                if (!b.healthy) continue;
                if (!b.alive) return "req " + reqId + " -> " + b.name + " FAILED (not yet detected)";
                b.served++; return "req " + reqId + " -> " + b.name;
            }
            return "req " + reqId + " -> 503 no healthy backends";
        }
    }

    public static void main(String[] args) {
        List<Backend> pool = List.of(new Backend("app-1"), new Backend("app-2"), new Backend("app-3"));
        LoadBalancer lb = new LoadBalancer(pool);
        int req = 0;
        for (int tick = 1; tick <= 6; tick++) {
            if (tick == 2) { pool.get(1).alive = false; System.out.println("tick 2: app-2 crashes"); }
            if (tick == 6) { pool.get(1).alive = true; System.out.println("tick 6: app-2 restarted"); }
            lb.runHealthChecks();
            System.out.println("tick " + tick + ": " + lb.route(++req) + " | " + lb.route(++req) + " | " + lb.route(++req));
        }
        pool.forEach(b -> System.out.println(b.name + " served " + b.served));
    }
}
