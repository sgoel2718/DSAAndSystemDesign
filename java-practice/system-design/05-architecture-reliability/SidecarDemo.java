import java.util.*;
import java.util.function.*;

public class SidecarDemo {
    // A sidecar wraps every outgoing call with retries, timeouts, metrics and an mTLS identity check, without touching business code.
    record Call(String from, String to, String path) {}

    static class Sidecar {
        final String identity; final Set<String> allowedCallers; final Map<String, int[]> metrics = new TreeMap<>(); final Random r = new Random(2);
        Sidecar(String identity, Set<String> allowedCallers) { this.identity = identity; this.allowedCallers = allowedCallers; }
        String send(Call c, Function<Call, String> app, Sidecar dest) {
            if (!dest.allowedCallers.contains(c.from())) return "403 denied by mesh policy (" + c.from() + " may not call " + c.to() + ")";
            for (int attempt = 1; attempt <= 3; attempt++) {
                boolean fail = r.nextInt(2) == 0;                          // flaky network: half the attempts fail
                metrics.computeIfAbsent(c.to(), k -> new int[2])[fail ? 1 : 0]++;
                if (!fail) return app.apply(c) + " (attempt " + attempt + ", mTLS " + identity + "->" + dest.identity + ")";
            }
            return "503 after 3 attempts";
        }
    }

    public static void main(String[] args) {
        Sidecar orderSide = new Sidecar("spiffe://shop/order", Set.of());
        Sidecar paymentSide = new Sidecar("spiffe://shop/payment", Set.of("order"));
        Function<Call, String> paymentApp = c -> "200 charged";              // business code knows nothing about retries/TLS
        for (int i = 0; i < 5; i++) System.out.println("order -> payment: " + orderSide.send(new Call("order", "payment", "/charge"), paymentApp, paymentSide));
        System.out.println("search -> payment: " + orderSide.send(new Call("search", "payment", "/charge"), paymentApp, paymentSide));
        orderSide.metrics.forEach((k, v) -> System.out.println("sidecar metrics to " + k + ": ok=" + v[0] + " errors=" + v[1]));
    }
}
