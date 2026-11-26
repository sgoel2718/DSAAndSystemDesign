import java.util.*;

public class PriceAlertSystem {
    // Millions of alerts indexed by product and sorted by target price: a price update only scans alerts whose target >= new price.
    record Alert(String user, String product, long targetPaise, String id) {}
    static final Map<String, TreeMap<Long, List<Alert>>> index = new HashMap<>();      // product -> target -> alerts
    static final Set<String> fired = new HashSet<>();

    static void subscribe(Alert a) { index.computeIfAbsent(a.product(), k -> new TreeMap<>()).computeIfAbsent(a.targetPaise(), k -> new ArrayList<>()).add(a); }
    static void onPriceChange(String product, long newPrice) {
        NavigableMap<Long, List<Alert>> hit = index.getOrDefault(product, new TreeMap<>()).tailMap(newPrice, true);   // all targets >= new price
        int checked = hit.values().stream().mapToInt(List::size).sum();
        System.out.printf("%s now Rs %,d -> %d alert(s) triggered (no scan of the rest)%n", product, newPrice / 100, checked);
        for (List<Alert> l : hit.values()) for (Alert a : l) if (fired.add(a.id())) System.out.println("   notify " + a.user() + ": " + product + " dropped below Rs " + String.format("%,d", a.targetPaise() / 100));
        hit.clear();                                                                       // one-shot alerts are removed after firing
    }

    public static void main(String[] args) {
        subscribe(new Alert("asha", "iphone-16", 65_000_00, "a1")); subscribe(new Alert("ravi", "iphone-16", 60_000_00, "a2"));
        subscribe(new Alert("zoya", "iphone-16", 70_000_00, "a3")); subscribe(new Alert("kiran", "ps5", 40_000_00, "a4"));
        Random r = new Random(1); for (int i = 0; i < 100_000; i++) subscribe(new Alert("u" + i, "iphone-16", (30_000 + r.nextInt(20_000)) * 100L, "b" + i));
        System.out.println("alerts indexed: " + index.get("iphone-16").values().stream().mapToInt(List::size).sum() + " for iphone-16");
        onPriceChange("iphone-16", 72_000_00);
        onPriceChange("iphone-16", 68_000_00);
        onPriceChange("iphone-16", 64_999_00);
        onPriceChange("ps5", 44_990_00);
        System.out.println("prices come from scrapers/partner feeds into a stream; only changed prices trigger this check");
    }
}
