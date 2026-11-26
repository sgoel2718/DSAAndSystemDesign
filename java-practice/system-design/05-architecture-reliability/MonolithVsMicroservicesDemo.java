import java.util.*;

public class MonolithVsMicroservicesDemo {
    // Same checkout written two ways. In-process calls can't fail halfway; network calls can.
    interface Inventory { boolean reserve(String sku); }
    interface Payments { boolean charge(int amount); }

    static String checkout(Inventory inv, Payments pay, String sku, int amount) {
        if (!inv.reserve(sku)) return "out of stock";
        if (!pay.charge(amount)) return "payment failed (stock reserved: must be released!)";
        return "order placed";
    }

    static class RemoteCall<T> {                                      // simulates a network hop: latency + possible failure
        static final Random net = new Random(21); static int totalMs = 0;
        static boolean call(String service, boolean result) {
            totalMs += 3;
            if (net.nextInt(10) == 0) throw new RuntimeException(service + " timed out");
            return result;
        }
    }

    public static void main(String[] args) {
        Inventory localInv = sku -> true; Payments localPay = amt -> true;
        System.out.println("monolith      : " + checkout(localInv, localPay, "shoe", 2499) + " (2 in-process calls, ~0 ms, one DB transaction)");
        Inventory remoteInv = sku -> RemoteCall.call("inventory-svc", true);
        Payments remotePay = amt -> RemoteCall.call("payment-svc", true);
        int ok = 0, failed = 0;
        for (int i = 0; i < 20; i++) {
            try { checkout(remoteInv, remotePay, "shoe", 2499); ok++; } catch (RuntimeException e) { failed++; }
        }
        System.out.println("microservices : 20 checkouts -> " + ok + " ok, " + failed + " hit a network failure, " + RemoteCall.totalMs + " ms spent on network hops");
        System.out.println("so microservices need timeouts, retries, idempotency and sagas; in return each service deploys and scales on its own.");
    }
}
