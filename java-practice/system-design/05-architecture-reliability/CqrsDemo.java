import java.util.*;

public class CqrsDemo {
    // Write side: normalised, validates commands. Read side: denormalised views updated from events (eventually).
    record OrderPlaced(int orderId, int userId, String item, int price) {}
    static final Map<Integer, int[]> ordersTable = new TreeMap<>();          // write model: orderId -> {userId, price}
    static final List<OrderPlaced> events = new ArrayList<>();
    static final Map<Integer, List<String>> myOrdersView = new TreeMap<>();  // read model 1: user's order list
    static final Map<String, Integer> salesByItemView = new TreeMap<>();     // read model 2: dashboard
    static int projectedUpTo = 0;

    static void placeOrder(int orderId, int userId, String item, int price) {
        if (price <= 0) throw new IllegalArgumentException("invalid price");
        ordersTable.put(orderId, new int[]{userId, price});
        events.add(new OrderPlaced(orderId, userId, item, price));
    }
    static void projector() {                                              // runs asynchronously in real life
        for (; projectedUpTo < events.size(); projectedUpTo++) {
            OrderPlaced e = events.get(projectedUpTo);
            myOrdersView.computeIfAbsent(e.userId(), k -> new ArrayList<>()).add(e.item() + "#" + e.orderId());
            salesByItemView.merge(e.item(), e.price(), Integer::sum);
        }
    }

    public static void main(String[] args) {
        placeOrder(1, 42, "shoes", 2499); placeOrder(2, 7, "shoes", 2499); projector();
        placeOrder(3, 42, "socks", 199);
        System.out.println("right after the 3rd command, user 42 view: " + myOrdersView.get(42) + "  <- not projected yet (lag)");
        projector();
        System.out.println("after projector runs   , user 42 view: " + myOrdersView.get(42));
        System.out.println("dashboard view (no joins needed)    : " + salesByItemView);
        myOrdersView.clear(); salesByItemView.clear(); projectedUpTo = 0; projector();
        System.out.println("read views can be dropped and rebuilt from events: " + myOrdersView);
    }
}
