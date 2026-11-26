import java.util.*;
import java.util.function.*;

public class EventBusDemo {
    record Event(String type, Map<String, Object> data) {}
    static class EventBus {
        final Map<String, List<Consumer<Event>>> subs = new TreeMap<>(); final List<Event> log = new ArrayList<>();
        void subscribe(String type, Consumer<Event> handler) { subs.computeIfAbsent(type, k -> new ArrayList<>()).add(handler); }
        void publish(Event e) { log.add(e); subs.getOrDefault(e.type(), List.of()).forEach(h -> h.accept(e)); }
    }

    public static void main(String[] args) {
        EventBus bus = new EventBus();
        // Each service only knows the events, not the other services (choreography)
        bus.subscribe("OrderPlaced", e -> { System.out.println("  payment-svc : charging order " + e.data().get("id")); bus.publish(new Event("PaymentSucceeded", e.data())); });
        bus.subscribe("OrderPlaced", e -> System.out.println("  analytics   : +1 order, Rs " + e.data().get("total")));
        bus.subscribe("PaymentSucceeded", e -> { System.out.println("  warehouse   : pick & pack order " + e.data().get("id")); bus.publish(new Event("OrderShipped", e.data())); });
        bus.subscribe("PaymentSucceeded", e -> System.out.println("  email-svc   : receipt sent for order " + e.data().get("id")));
        bus.subscribe("OrderShipped", e -> System.out.println("  email-svc   : 'your order is on the way'"));
        System.out.println("order-svc publishes OrderPlaced (a real bus is asynchronous; here handlers run inline so the output is in order):");
        bus.publish(new Event("OrderPlaced", Map.of("id", 987, "total", 2499)));
        System.out.println("event log: " + bus.log.stream().map(Event::type).toList());
        System.out.println("adding a new 'loyalty points' service = one more subscribe(...), no change to order-svc.");
    }
}
