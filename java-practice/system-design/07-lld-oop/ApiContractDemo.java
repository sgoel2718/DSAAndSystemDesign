import java.util.*;

public class ApiContractDemo {
    // A clean service contract: typed requests/responses, explicit errors, validation, and idempotency.
    record CreateBookingRequest(String userId, String showId, List<String> seats, String idempotencyKey) {}
    record Booking(String id, String userId, String showId, List<String> seats, long amountPaise, String status) {}
    sealed interface Result<T> permits Ok, Err {}
    record Ok<T>(T value) implements Result<T> {}
    record Err<T>(String code, String message) implements Result<T> {}

    interface BookingService {
        Result<Booking> create(CreateBookingRequest req);
        Result<Booking> get(String bookingId);
    }

    static final class InMemoryBookingService implements BookingService {
        private final Map<String, Booking> byId = new HashMap<>(); private final Map<String, String> byKey = new HashMap<>(); private final Set<String> taken = new HashSet<>(); private int seq;
        public Result<Booking> create(CreateBookingRequest r) {
            if (r.seats() == null || r.seats().isEmpty() || r.seats().size() > 6) return new Err<>("INVALID_ARGUMENT", "1 to 6 seats required");
            if (byKey.containsKey(r.idempotencyKey())) return new Ok<>(byId.get(byKey.get(r.idempotencyKey())));
            for (String s : r.seats()) if (taken.contains(r.showId() + ":" + s)) return new Err<>("SEAT_UNAVAILABLE", "seat " + s + " already booked");
            r.seats().forEach(s -> taken.add(r.showId() + ":" + s));
            Booking b = new Booking("bk-" + (++seq), r.userId(), r.showId(), List.copyOf(r.seats()), r.seats().size() * 250_00L, "CONFIRMED");
            byId.put(b.id(), b); byKey.put(r.idempotencyKey(), b.id()); return new Ok<>(b);
        }
        public Result<Booking> get(String id) { Booking b = byId.get(id); return b == null ? new Err<>("NOT_FOUND", "no booking " + id) : new Ok<>(b); }
    }

    static String show(Result<?> r) { return switch (r) { case Ok<?> ok -> "OK  " + ok.value(); case Err<?> e -> "ERR " + e.code() + ": " + e.message(); }; }

    public static void main(String[] args) {
        BookingService api = new InMemoryBookingService();
        System.out.println(show(api.create(new CreateBookingRequest("asha", "show-7", List.of("A1", "A2"), "k1"))));
        System.out.println(show(api.create(new CreateBookingRequest("asha", "show-7", List.of("A1", "A2"), "k1"))) + "  <- retry, same booking");
        System.out.println(show(api.create(new CreateBookingRequest("ravi", "show-7", List.of("A2", "A3"), "k2"))));
        System.out.println(show(api.create(new CreateBookingRequest("ravi", "show-7", List.of(), "k3"))));
        System.out.println(show(api.get("bk-1")));
        System.out.println(show(api.get("bk-9")));
    }
}
