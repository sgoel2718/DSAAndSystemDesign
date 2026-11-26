import java.util.*;

public class ScalabilityDemo {
    interface Server { String name(); int capacity(); }
    record Machine(String name, int cores) implements Server { public int capacity() { return cores * 250; } }

    static int handle(List<? extends Server> servers, int load) {
        int capacity = servers.stream().mapToInt(Server::capacity).sum();
        return Math.min(load, capacity);
    }

    public static void main(String[] args) {
        int load = 20_000;
        // Vertical: keep buying a bigger single machine
        for (int cores : new int[]{8, 32, 96}) {
            List<Machine> one = List.of(new Machine("big-" + cores, cores));
            System.out.printf("vertical   1 x %2d cores -> serves %,6d of %,d req/s%n", cores, handle(one, load), load);
        }
        System.out.println("           (no 300-core machine to buy; and if it dies, everything is down)");
        // Horizontal: add identical 8-core machines behind a load balancer
        for (int n : new int[]{2, 5, 10}) {
            List<Machine> fleet = new ArrayList<>();
            for (int i = 0; i < n; i++) fleet.add(new Machine("app-" + i, 8));
            System.out.printf("horizontal %2d x 8 cores -> serves %,6d of %,d req/s%n", n, handle(fleet, load), load);
        }
        List<Machine> fleet = new ArrayList<>();
        for (int i = 0; i < 10; i++) fleet.add(new Machine("app-" + i, 8));
        fleet.remove(3);
        System.out.printf("one of 10 servers fails -> still serves %,d req/s%n", handle(fleet, load));
    }
}
