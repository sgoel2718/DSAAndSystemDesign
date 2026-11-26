import java.util.*;

public class EcommerceCheckoutSystem {
    // Cart -> price & tax -> reserve inventory -> payment (idempotent) -> order -> outbox events, with compensation on failure.
    record Line(String sku, int qty) {}
    static final Map<String, Integer> priceRs = Map.of("shoes", 2499, "socks", 199, "watch", 15999);
    static final Map<String, Integer> stock = new TreeMap<>(Map.of("shoes", 5, "socks", 1, "watch", 2));
    static final List<String> outbox = new ArrayList<>(); static final Map<String, String> paymentsByKey = new HashMap<>();
    static int orderSeq = 0;

    static String checkout(String user, List<Line> cart, String idemKey, boolean cardDeclines) {
        int subtotal = cart.stream().mapToInt(l -> priceRs.get(l.sku()) * l.qty()).sum(), gst = subtotal * 18 / 100, total = subtotal + gst;
        List<Line> reserved = new ArrayList<>();
        for (Line l : cart) {                                                      // reserve atomically per SKU (UPDATE ... WHERE stock >= qty)
            if (stock.get(l.sku()) < l.qty()) { reserved.forEach(r -> stock.merge(r.sku(), r.qty(), Integer::sum)); return "FAILED: " + l.sku() + " out of stock (released " + reserved.size() + " reservation(s))"; }
            stock.merge(l.sku(), -l.qty(), Integer::sum); reserved.add(l);
        }
        String payment = paymentsByKey.computeIfAbsent(idemKey, k -> cardDeclines ? "DECLINED" : "pay_" + k);
        if (payment.equals("DECLINED")) { reserved.forEach(r -> stock.merge(r.sku(), r.qty(), Integer::sum)); paymentsByKey.remove(idemKey); return "FAILED: card declined, inventory released"; }
        String orderId = "OD" + (++orderSeq);
        outbox.add("OrderPlaced{" + orderId + ", user=" + user + ", total=" + total + "}");   // same transaction as the order row
        return String.format("OK %s subtotal %d + GST %d = Rs %d, payment %s", orderId, subtotal, gst, total, payment);
    }

    public static void main(String[] args) {
        System.out.println(checkout("asha", List.of(new Line("shoes", 1), new Line("socks", 1)), "k1", false));
        System.out.println(checkout("ravi", List.of(new Line("shoes", 1), new Line("socks", 1)), "k2", false));
        System.out.println(checkout("zoya", List.of(new Line("watch", 1)), "k3", true));
        System.out.println(checkout("zoya", List.of(new Line("watch", 1)), "k4", false));
        System.out.println("stock now " + stock);
        System.out.println("outbox events for email/warehouse/analytics: " + outbox);
    }
}
