import java.util.*;

public class SolidDemo {
    // S: each class has one reason to change. O: add new discount types without editing old code.
    // L: any Discount can replace another. I: small interfaces. D: high-level code depends on abstractions.
    interface Discount { long apply(long totalPaise); default String name() { return "custom rule"; } }
    record PercentOff(int pct) implements Discount { public long apply(long t) { return t - t * pct / 100; } public String name() { return pct + "% off"; } }
    record FlatOff(long paise) implements Discount { public long apply(long t) { return Math.max(0, t - paise); } public String name() { return "Rs " + paise / 100 + " off"; } }

    interface OrderRepository { void save(String order); }                 // D: abstraction the service depends on
    interface Notifier { void send(String msg); }                          // I: tiny interface, not a giant 'Utils'

    static class InMemoryRepo implements OrderRepository { final List<String> rows = new ArrayList<>(); public void save(String o) { rows.add(o); } }
    static class ConsoleNotifier implements Notifier { public void send(String m) { System.out.println("  notify: " + m); } }

    static class CheckoutService {                                          // S: only orchestrates checkout
        private final OrderRepository repo; private final Notifier notifier;
        CheckoutService(OrderRepository r, Notifier n) { repo = r; notifier = n; }
        long checkout(String user, long total, Discount d) {
            long finalPrice = d.apply(total);
            repo.save(user + ":" + finalPrice);
            notifier.send(user + " paid Rs " + finalPrice / 100 + " (" + d.name() + ")");
            return finalPrice;
        }
    }

    public static void main(String[] args) {
        InMemoryRepo repo = new InMemoryRepo();
        CheckoutService svc = new CheckoutService(repo, new ConsoleNotifier());   // dependencies injected
        svc.checkout("asha", 2_499_00, new PercentOff(10));
        svc.checkout("ravi", 2_499_00, new FlatOff(500_00));
        Discount buyMore = t -> t >= 2_000_00 ? t - 300_00 : t;                   // O: a new rule, zero edits elsewhere
        System.out.println("  lambda discount works too: Rs " + buyMore.apply(2_499_00) / 100);
        System.out.println("saved orders: " + repo.rows);
    }
}
