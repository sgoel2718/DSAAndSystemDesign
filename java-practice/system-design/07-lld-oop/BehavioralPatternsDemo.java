import java.util.*;
import java.util.function.*;

public class BehavioralPatternsDemo {
    // Strategy: swap the algorithm at runtime
    interface FareStrategy { double fare(double km); }
    static final Map<String, FareStrategy> fares = Map.of("normal", km -> 30 + 12 * km, "surge", km -> (30 + 12 * km) * 1.8, "pool", km -> 20 + 8 * km);

    // Observer: subscribers are notified of changes
    static class OrderStatus {
        private final List<Consumer<String>> observers = new ArrayList<>(); private String status = "CREATED";
        void subscribe(Consumer<String> o) { observers.add(o); }
        void set(String s) { status = s; observers.forEach(o -> o.accept(s)); }
    }

    // State: behaviour depends on the current state object
    interface DoorState { DoorState press(StringBuilder log); }
    static final DoorState OPEN = new DoorState() { public DoorState press(StringBuilder l) { l.append("closing -> "); return CLOSED(); } };
    static DoorState CLOSED() { return log -> { log.append("opening -> "); return OPEN; }; }

    // Command: actions as objects, so they can be queued and undone
    interface Command { void run(); void undo(); }
    static final StringBuilder doc = new StringBuilder();
    static Command type(String s) { return new Command() { public void run() { doc.append(s); } public void undo() { doc.setLength(doc.length() - s.length()); } }; }

    // Chain of responsibility: each handler passes the request on or stops it
    static Function<Map<String, Object>, String> chain = req -> {
        List<Function<Map<String, Object>, String>> handlers = List.of(
            r -> r.get("token") == null ? "401 by auth handler" : null,
            r -> (int) r.get("calls") > 100 ? "429 by rate-limit handler" : null,
            r -> "200 handled by controller");
        for (var h : handlers) { String res = h.apply(req); if (res != null) return res; }
        return "unreachable";
    };

    public static void main(String[] args) {
        new TreeMap<>(fares).forEach((k, s) -> System.out.printf("strategy %-6s 10 km -> Rs %.0f%n", k, s.fare(10)));
        OrderStatus o = new OrderStatus();
        o.subscribe(s -> System.out.println("observer email: order is " + s)); o.subscribe(s -> System.out.println("observer app push: " + s));
        o.set("SHIPPED");
        StringBuilder log = new StringBuilder(); DoorState d = CLOSED(); for (int i = 0; i < 3; i++) d = d.press(log);
        System.out.println("state: " + log + "done");
        Deque<Command> history = new ArrayDeque<>();
        for (String w : List.of("Hello", " world", "!!")) { Command c = type(w); c.run(); history.push(c); }
        System.out.println("command: '" + doc + "'"); history.pop().undo(); System.out.println("after undo: '" + doc + "'");
        System.out.println("chain: " + chain.apply(Map.of("calls", 5)) + " | " + chain.apply(Map.of("token", "t", "calls", 500)) + " | " + chain.apply(Map.of("token", "t", "calls", 5)));
    }
}
