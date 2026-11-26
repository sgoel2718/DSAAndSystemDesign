import java.util.*;

public class CreationalPatternsDemo {
    // Singleton (enum = thread-safe, serialisation-safe)
    enum Config { INSTANCE; final Map<String, String> values = new HashMap<>(Map.of("currency", "INR")); }

    // Factory method: callers ask for a type by name, never call 'new' on concrete classes
    interface Notification { String send(String to, String msg); }
    static class Email implements Notification { public String send(String to, String m) { return "email to " + to + ": " + m; } }
    static class Sms implements Notification { public String send(String to, String m) { return "sms to " + to + ": " + m; } }
    static Notification notificationFor(String channel) {
        return switch (channel) { case "email" -> new Email(); case "sms" -> new Sms(); default -> throw new IllegalArgumentException(channel); };
    }

    // Builder: many optional fields, readable construction, immutable result
    static final class Pizza {
        final String size; final List<String> toppings; final boolean extraCheese;
        private Pizza(Builder b) { size = b.size; toppings = List.copyOf(b.toppings); extraCheese = b.extraCheese; }
        static Builder builder(String size) { return new Builder(size); }
        static final class Builder {
            private final String size; private final List<String> toppings = new ArrayList<>(); private boolean extraCheese;
            Builder(String size) { this.size = size; }
            Builder topping(String t) { toppings.add(t); return this; }
            Builder extraCheese() { extraCheese = true; return this; }
            Pizza build() { if (toppings.size() > 5) throw new IllegalStateException("too many toppings"); return new Pizza(this); }
        }
        public String toString() { return size + " pizza " + toppings + (extraCheese ? " + extra cheese" : ""); }
    }

    // Prototype: copy a configured object instead of rebuilding it
    record Document(String template, Map<String, String> fields) { Document copyWith(String k, String v) { Map<String, String> f = new HashMap<>(fields); f.put(k, v); return new Document(template, f); } }

    public static void main(String[] args) {
        System.out.println("singleton same object? " + (Config.INSTANCE == Config.valueOf("INSTANCE")) + ", currency=" + Config.INSTANCE.values.get("currency"));
        for (String ch : List.of("email", "sms")) System.out.println("factory: " + notificationFor(ch).send("asha", "order shipped"));
        System.out.println("builder: " + Pizza.builder("large").topping("paneer").topping("onion").extraCheese().build());
        Document invoice = new Document("invoice-v2", Map.of("company", "ShopCo", "gst", "29ABCDE"));
        System.out.println("prototype: " + new TreeMap<>(invoice.copyWith("customer", "Ravi").fields()));
    }
}
