import java.util.*;

public class StructuralPatternsDemo {
    interface PaymentGateway { boolean charge(String user, long paise); }

    // Adapter: a third-party SDK with a different interface, wrapped to fit ours
    static class LegacyPayU { int makePayment(double rupees, String customerId) { return rupees < 100_000 ? 200 : 402; } }
    static class PayUAdapter implements PaymentGateway {
        private final LegacyPayU sdk = new LegacyPayU();
        public boolean charge(String u, long p) { return sdk.makePayment(p / 100.0, u) == 200; }
    }

    // Decorator: add logging and retries without changing the gateway
    static class LoggingGateway implements PaymentGateway {
        private final PaymentGateway inner; LoggingGateway(PaymentGateway i) { inner = i; }
        public boolean charge(String u, long p) { boolean ok = inner.charge(u, p); System.out.println("  [log] charge " + u + " Rs " + p / 100 + " -> " + ok); return ok; }
    }

    // Proxy: controls access (here a cache in front of a slow service)
    interface ExchangeRates { double usdToInr(); }
    static class SlowRatesApi implements ExchangeRates { int calls; public double usdToInr() { calls++; return 83.2; } }
    static class CachingRatesProxy implements ExchangeRates {
        private final SlowRatesApi real; private Double cached; CachingRatesProxy(SlowRatesApi r) { real = r; }
        public double usdToInr() { if (cached == null) cached = real.usdToInr(); return cached; }
    }

    // Facade: one simple method over many subsystems
    static class CheckoutFacade {
        private final PaymentGateway pay = new LoggingGateway(new PayUAdapter());
        String placeOrder(String user, long paise) {
            boolean reserved = true;                                             // inventory subsystem
            boolean paid = reserved && pay.charge(user, paise);                  // payment subsystem
            return paid ? "order confirmed, invoice emailed" : "payment failed, stock released";
        }
    }

    // Composite: treat a single item and a bundle the same way
    interface CartItem { long price(); }
    record Product(String name, long price) implements CartItem {}
    record Bundle(String name, List<CartItem> items, int discountPct) implements CartItem {
        public long price() { return items.stream().mapToLong(CartItem::price).sum() * (100 - discountPct) / 100; }
    }

    public static void main(String[] args) {
        CheckoutFacade shop = new CheckoutFacade();
        System.out.println("facade: " + shop.placeOrder("asha", 2_499_00));
        System.out.println("facade: " + shop.placeOrder("ravi", 2_00_000_00));
        SlowRatesApi api = new SlowRatesApi(); ExchangeRates rates = new CachingRatesProxy(api);
        for (int i = 0; i < 3; i++) rates.usdToInr();
        System.out.println("proxy: 3 lookups, real API called " + api.calls + " time");
        CartItem combo = new Bundle("cricket kit", List.of(new Product("bat", 3000), new Product("ball", 500), new Bundle("pads+gloves", List.of(new Product("pads", 1500), new Product("gloves", 800)), 10)), 5);
        System.out.println("composite: bundle price Rs " + combo.price());
    }
}
