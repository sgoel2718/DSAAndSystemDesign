import java.util.*;

public class HotelReservationSystem {
    // Inventory per (room type, night) with optimistic versions; a booking reserves every night or none; overbooking allowance.
    record Key(String roomType, int night) {}
    static final class Inv { int total, reserved, version; Inv(int t) { total = t; } }
    static final Map<Key, Inv> inventory = new TreeMap<>(Comparator.comparing(Key::roomType).thenComparingInt(Key::night));
    static final double OVERBOOK = 1.10;

    static String book(String guest, String type, int checkIn, int checkOut, int rooms) {
        Map<Key, Integer> seen = new HashMap<>();
        for (int n = checkIn; n < checkOut; n++) {                                         // read phase: check every night
            Inv inv = inventory.get(new Key(type, n));
            if (inv.reserved + rooms > Math.floor(inv.total * OVERBOOK)) return guest + ": SOLD OUT on night " + n;
            seen.put(new Key(type, n), inv.version);
        }
        for (var e : seen.entrySet()) if (inventory.get(e.getKey()).version != e.getValue()) return guest + ": conflict, retry";   // optimistic check
        for (Key k : seen.keySet()) { Inv inv = inventory.get(k); inv.reserved += rooms; inv.version++; }                     // write phase (one transaction)
        return guest + ": BOOKED " + rooms + " x " + type + " nights " + checkIn + "-" + (checkOut - 1);
    }

    public static void main(String[] args) {
        for (int night = 1; night <= 5; night++) { inventory.put(new Key("deluxe", night), new Inv(10)); inventory.put(new Key("suite", night), new Inv(2)); }
        System.out.println(book("asha", "suite", 1, 4, 1));
        System.out.println(book("ravi", "suite", 2, 3, 1));
        System.out.println(book("zoya", "suite", 3, 5, 1) + " (2 rooms x 1.10 overbooking = 2)");
        System.out.println(book("kiran", "deluxe", 1, 3, 11) + " (10 x 1.10 = 11 allowed)");
        System.out.println(book("meera", "deluxe", 2, 3, 1));
        inventory.forEach((k, v) -> { if (k.roomType().equals("suite")) System.out.println("  suite night " + k.night() + ": reserved " + v.reserved + "/" + v.total); });
    }
}
