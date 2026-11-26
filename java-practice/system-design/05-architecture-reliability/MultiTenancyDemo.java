import java.util.*;

public class MultiTenancyDemo {
    record Invoice(String tenant, int id, int amount) {}
    static final List<Invoice> sharedTable = List.of(new Invoice("acme", 1, 500), new Invoice("acme", 2, 700), new Invoice("globex", 3, 900));
    static final ThreadLocal<String> currentTenant = new ThreadLocal<>();

    static List<Invoice> findInvoices() {                                        // every query is automatically scoped (like row-level security)
        String t = Objects.requireNonNull(currentTenant.get(), "no tenant in context");
        return sharedTable.stream().filter(i -> i.tenant().equals(t)).toList();
    }

    static final Map<String, Map<String, Object>> tenantConfig = Map.of(
        "acme", Map.of("plan", "enterprise", "rateLimit", 1000, "darkMode", true),
        "globex", Map.of("plan", "free", "rateLimit", 50, "darkMode", false));
    static final Map<String, Integer> usage = new HashMap<>();

    static String handle(String tenant, String path) {
        currentTenant.set(tenant);
        try {
            int limit = (Integer) tenantConfig.get(tenant).get("rateLimit");
            if (usage.merge(tenant, 1, Integer::sum) > limit) return tenant + " " + path + " -> 429 (noisy neighbour contained)";
            return tenant + " " + path + " -> " + findInvoices().stream().map(Invoice::id).toList();
        } finally { currentTenant.remove(); }
    }

    public static void main(String[] args) {
        System.out.println(handle("acme", "/invoices"));
        System.out.println(handle("globex", "/invoices"));
        for (int i = 0; i < 60; i++) handle("globex", "/invoices");
        System.out.println(handle("globex", "/invoices"));
        System.out.println(handle("acme", "/invoices") + " (acme unaffected)");
        try { findInvoices(); } catch (NullPointerException e) { System.out.println("query without tenant context -> refused: " + e.getMessage()); }
    }
}
