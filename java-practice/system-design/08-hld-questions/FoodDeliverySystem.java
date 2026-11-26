import java.util.*;

public class FoodDeliverySystem {
    // Order state machine across restaurant + rider; rider assignment by ETA (distance + current load); live ETA updates.
    enum S { PLACED, ACCEPTED, PREPARING, RIDER_ASSIGNED, PICKED_UP, DELIVERED, CANCELLED }
    static final Map<S, Set<S>> allowed = new EnumMap<>(Map.of(S.PLACED, EnumSet.of(S.ACCEPTED, S.CANCELLED), S.ACCEPTED, EnumSet.of(S.PREPARING, S.CANCELLED),
        S.PREPARING, EnumSet.of(S.RIDER_ASSIGNED), S.RIDER_ASSIGNED, EnumSet.of(S.PICKED_UP), S.PICKED_UP, EnumSet.of(S.DELIVERED), S.DELIVERED, EnumSet.noneOf(S.class), S.CANCELLED, EnumSet.noneOf(S.class)));
    record Rider(String id, double kmFromRestaurant, int activeOrders) {}

    static S move(S from, S to) { if (!allowed.get(from).contains(to)) throw new IllegalStateException(from + " -> " + to + " not allowed"); System.out.println("  order: " + from + " -> " + to); return to; }

    public static void main(String[] args) {
        S s = S.PLACED;
        s = move(s, S.ACCEPTED); s = move(s, S.PREPARING);
        int prepMin = 15;
        List<Rider> riders = List.of(new Rider("r1", 0.5, 2), new Rider("r2", 1.8, 0), new Rider("r3", 4.0, 0));
        Rider best = riders.stream().min(Comparator.comparingDouble(r -> Math.max(r.kmFromRestaurant() / 20 * 60 + r.activeOrders() * 8, prepMin))).get();
        riders.forEach(r -> System.out.printf("  rider %s: %.1f km away, %d active -> ready to pick up in %.0f min%n", r.id(), r.kmFromRestaurant(), r.activeOrders(), Math.max(r.kmFromRestaurant() / 20 * 60 + r.activeOrders() * 8, prepMin)));
        System.out.println("  assign " + best.id() + " (arrives as food is ready, not the nearest one who is busy)");
        s = move(s, S.RIDER_ASSIGNED); s = move(s, S.PICKED_UP);
        double kmToCustomer = 3.2;
        for (int minute = 0; minute <= 9; minute += 3) System.out.printf("  live ETA at +%d min: %.0f min (rider location every 5 s, sent to the customer app)%n", minute, Math.max(0, kmToCustomer / 20 * 60 - minute));
        s = move(s, S.DELIVERED);
        try { move(s, S.CANCELLED); } catch (IllegalStateException e) { System.out.println("  rejected: " + e.getMessage()); }
    }
}
