import java.util.*;

public class CostModelDemo {
    record Line(String item, double qty, double unitPrice, String unit) { double cost() { return qty * unitPrice; } }

    public static void main(String[] args) {
        List<Line> bill = new ArrayList<>(List.of(
            new Line("app servers", 20, 150, "server-month"), new Line("database primary + 2 replicas", 3, 1200, "node-month"),
            new Line("object storage", 200, 23, "TB-month"), new Line("CDN egress", 500, 20, "TB"), new Line("Redis cache", 2, 400, "node-month")));
        print("baseline", bill);
        List<Line> optimised = new ArrayList<>();
        for (Line l : bill) switch (l.item()) {
            case "app servers" -> optimised.add(new Line("app servers (autoscaled, avg 12)", 12, 150 * 0.7, "server-month, 1-yr commit"));
            case "object storage" -> { optimised.add(new Line("object storage hot", 40, 23, "TB-month")); optimised.add(new Line("object storage archive", 160, 4, "TB-month")); }
            case "CDN egress" -> optimised.add(new Line("CDN egress (WebP + better caching)", 300, 20, "TB"));
            default -> optimised.add(l);
        }
        print("optimised", optimised);
    }

    static void print(String title, List<Line> bill) {
        double total = bill.stream().mapToDouble(Line::cost).sum();
        System.out.println(title + ":");
        for (Line l : bill) System.out.printf("  %-36s %6.0f x $%6.1f = $%,9.0f  (%4.1f%%)%n", l.item(), l.qty(), l.unitPrice(), l.cost(), l.cost() / total * 100);
        System.out.printf("  %-36s %29s $%,9.0f per month%n", "TOTAL", "", total);
    }
}
