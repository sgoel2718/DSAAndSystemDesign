import java.util.*;

public class SagaDemo {
    // Orchestrated saga: each step is a local transaction with a compensating action.
    interface Step { String name(); boolean run(Map<String, Object> ctx); void compensate(Map<String, Object> ctx); }

    static Step step(String name, java.util.function.Predicate<Map<String, Object>> run, java.util.function.Consumer<Map<String, Object>> comp) {
        return new Step() { public String name() { return name; } public boolean run(Map<String, Object> c) { return run.test(c); } public void compensate(Map<String, Object> c) { comp.accept(c); } };
    }

    static int wallet = 5000, stock = 0; static String orderStatus = "NONE";
    static final List<String> outbox = new ArrayList<>();

    static void runSaga(List<Step> steps) {
        Map<String, Object> ctx = new HashMap<>(); Deque<Step> done = new ArrayDeque<>();
        for (Step s : steps) {
            if (s.run(ctx)) { done.push(s); System.out.println("  ✔ " + s.name()); continue; }
            System.out.println("  ✘ " + s.name() + " failed -> compensating in reverse order");
            while (!done.isEmpty()) { Step d = done.pop(); d.compensate(ctx); System.out.println("    ↺ undo " + d.name()); }
            return;
        }
    }

    public static void main(String[] args) {
        List<Step> placeOrder = List.of(
            step("create order (PENDING)", c -> { orderStatus = "PENDING"; outbox.add("OrderCreated"); return true; }, c -> { orderStatus = "CANCELLED"; outbox.add("OrderCancelled"); }),
            step("charge Rs 2499", c -> { if (wallet < 2499) return false; wallet -= 2499; return true; }, c -> { wallet += 2499; outbox.add("PaymentRefunded"); }),
            step("reserve 1 item", c -> { if (stock < 1) return false; stock--; return true; }, c -> stock++),
            step("confirm order", c -> { orderStatus = "CONFIRMED"; return true; }, c -> {}));
        System.out.println("Saga 1: stock = 0");
        runSaga(placeOrder);
        System.out.println("  result: order=" + orderStatus + " wallet=" + wallet + " stock=" + stock + " events=" + outbox);
        stock = 3; outbox.clear();
        System.out.println("Saga 2: stock = 3");
        runSaga(placeOrder);
        System.out.println("  result: order=" + orderStatus + " wallet=" + wallet + " stock=" + stock + " events=" + outbox);
    }
}
