import java.util.*;

public class MatchingEngineSystem {
    // Limit order book per symbol: bids (highest first) and asks (lowest first), price-time priority and partial fills.
    record Order(long id, String side, long price, long qty, long seq) {}
    static final TreeMap<Long, Deque<Order>> bids = new TreeMap<>(Comparator.reverseOrder()), asks = new TreeMap<>();
    static long seq = 0; static final List<String> trades = new ArrayList<>();

    static void submit(String side, long price, long qty) {
        Order o = new Order(++seq, side, price, qty, seq); long remaining = qty;
        TreeMap<Long, Deque<Order>> book = side.equals("BUY") ? asks : bids;
        while (remaining > 0 && !book.isEmpty()) {
            long best = book.firstKey();
            if (side.equals("BUY") ? best > price : best < price) break;          // no crossing
            Deque<Order> level = book.firstEntry().getValue(); Order resting = level.peekFirst();
            long fill = Math.min(remaining, resting.qty()); remaining -= fill;
            trades.add(String.format("trade %d @ %d (taker #%d %s, maker #%d)", fill, best, o.id(), side, resting.id()));
            level.pollFirst();
            if (resting.qty() > fill) level.addFirst(new Order(resting.id(), resting.side(), resting.price(), resting.qty() - fill, resting.seq()));
            if (level.isEmpty()) book.pollFirstEntry();
        }
        if (remaining > 0) (side.equals("BUY") ? bids : asks).computeIfAbsent(price, k -> new ArrayDeque<>()).addLast(new Order(o.id(), side, price, remaining, o.seq()));
    }
    static String book() { return "bids " + summary(bids) + " | asks " + summary(asks); }
    static String summary(TreeMap<Long, Deque<Order>> b) { List<String> out = new ArrayList<>(); b.forEach((p, q) -> out.add(q.stream().mapToLong(Order::qty).sum() + "@" + p)); return out.toString(); }

    public static void main(String[] args) {
        submit("SELL", 101, 50); submit("SELL", 102, 100); submit("SELL", 101, 30); submit("BUY", 99, 40); submit("BUY", 100, 25);
        System.out.println("book: " + book());
        submit("BUY", 102, 120);                                                   // sweeps 101 (two orders, time priority) then part of 102
        trades.forEach(t -> System.out.println("  " + t));
        System.out.println("book: " + book());
        submit("SELL", 99, 70);
        System.out.println("after aggressive sell: " + trades.subList(trades.size() - 2, trades.size()) + "\nbook: " + book());
    }
}
