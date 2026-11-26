import java.util.*;

public class UmlRelationshipsDemo {
    // Each relationship from a UML class diagram, as Java code.
    interface Payable { long amount(); }                                   // realisation (implements)  ..|>
    static abstract class Vehicle { abstract int wheels(); }               // generalisation (extends)  --|>
    static class Car extends Vehicle { int wheels() { return 4; } }

    static class Engine { final int cc; Engine(int cc) { this.cc = cc; } }
    static class Bus extends Vehicle {
        private final Engine engine = new Engine(5000);                    // composition *-- : created and owned, dies with Bus
        private final List<Passenger> passengers = new ArrayList<>();      // aggregation o-- : passengers exist on their own
        int wheels() { return 6; }
        void board(Passenger p) { passengers.add(p); }
        Ticket sell(Passenger p, PricingService pricing) { return new Ticket(p, pricing.price(p)); }   // dependency ..> : used, not stored
    }
    record Passenger(String name, int age) {}
    record Ticket(Passenger passenger, long amount) implements Payable {}   // association --> : Ticket knows its Passenger
    static class PricingService { long price(Passenger p) { return p.age() < 12 ? 50 : 100; } }

    public static void main(String[] args) {
        Bus bus = new Bus(); Passenger asha = new Passenger("Asha", 30), kid = new Passenger("Kiran", 8);
        bus.board(asha); bus.board(kid);
        PricingService pricing = new PricingService();
        List<Payable> bills = List.of(bus.sell(asha, pricing), bus.sell(kid, pricing));
        System.out.println("Bus is-a Vehicle with " + bus.wheels() + " wheels, has-a Engine " + bus.engine.cc + "cc (composition)");
        System.out.println("Bus aggregates passengers " + bus.passengers.stream().map(Passenger::name).toList());
        bills.forEach(b -> System.out.println("Ticket (Payable) " + b + " -> Rs " + b.amount()));
        bus = null;
        System.out.println("bus discarded: its Engine is gone too, but " + asha.name() + " still exists (aggregation)");
    }
}
