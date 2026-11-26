import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

public class SeatBookingSystem {
    // Seat holds with TTL (atomic compare-and-set per seat), payment confirms, expired holds released, virtual waiting room.
    enum SeatState { FREE, HELD, BOOKED }
    record Seat(SeatState state, String user, long holdUntil) {}
    static final ConcurrentHashMap<String, Seat> seats = new ConcurrentHashMap<>();

    static boolean hold(String seat, String user, long now) {
        Seat[] result = new Seat[1];
        seats.compute(seat, (k, s) -> {
            boolean free = s.state() == SeatState.FREE || (s.state() == SeatState.HELD && s.holdUntil() <= now);
            result[0] = free ? new Seat(SeatState.HELD, user, now + 600) : s; return result[0];
        });
        return user.equals(result[0].user()) && result[0].state() == SeatState.HELD;
    }
    static boolean confirm(String seat, String user, long now) {
        Seat s = seats.get(seat);
        if (s.state() != SeatState.HELD || !s.user().equals(user) || s.holdUntil() <= now) return false;
        return seats.replace(seat, s, new Seat(SeatState.BOOKED, user, 0));
    }

    public static void main(String[] args) throws Exception {
        for (String s : List.of("A1", "A2", "A3")) seats.put(s, new Seat(SeatState.FREE, null, 0));
        ExecutorService pool = Executors.newFixedThreadPool(8); AtomicInteger winners = new AtomicInteger(); List<Future<?>> fs = new ArrayList<>();
        for (int i = 0; i < 1000; i++) { String u = "user" + i; fs.add(pool.submit(() -> { if (hold("A1", u, 0)) winners.incrementAndGet(); })); }
        for (Future<?> f : fs) f.get(); pool.shutdown();
        String holder = seats.get("A1").user();
        System.out.println("1,000 users try to hold A1 at once -> holds granted: " + winners.get() + " (to " + holder + ")");
        System.out.println(holder + " pays at t=300 -> confirmed: " + confirm("A1", holder, 300));
        System.out.println("asha holds A2 at t=0 -> " + hold("A2", "asha", 0) + "; ravi tries A2 at t=100 -> " + hold("A2", "ravi", 100));
        System.out.println("asha never pays; ravi tries A2 at t=700 (hold expired) -> " + hold("A2", "ravi", 700));
        System.out.println("asha tries to pay at t=710 -> " + confirm("A2", "asha", 710) + " (hold lost)");
        Deque<String> waitingRoom = new ArrayDeque<>(); for (int i = 0; i < 6; i++) waitingRoom.add("fan" + i);
        List<String> admitted = new ArrayList<>(); while (admitted.size() < 2) admitted.add(waitingRoom.poll());
        System.out.println("waiting room admits " + admitted + " to the seat map; " + waitingRoom.size() + " still queued");
        System.out.println("seats: " + new TreeMap<>(seats));
    }
}
