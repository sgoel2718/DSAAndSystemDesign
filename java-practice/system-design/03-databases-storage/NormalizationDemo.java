import java.util.*;

public class NormalizationDemo {
    record FlatOrder(int orderId, String customer, String city, String product, int price) {}

    public static void main(String[] args) {
        List<FlatOrder> flat = new ArrayList<>(List.of(new FlatOrder(1, "Asha", "Pune", "Shoes", 2499),
            new FlatOrder(2, "Asha", "Pune", "Socks", 199), new FlatOrder(3, "Ravi", "Delhi", "Shoes", 2499)));
        // Update anomaly: Asha moves; we forget one row
        flat.set(0, new FlatOrder(1, "Asha", "Mumbai", "Shoes", 2499));
        Set<String> ashaCities = new TreeSet<>(); for (FlatOrder f : flat) if (f.customer().equals("Asha")) ashaCities.add(f.city());
        System.out.println("unnormalised: Asha now lives in " + ashaCities + "  <- update anomaly");
        // Delete anomaly: removing order 3 loses the fact that Ravi lives in Delhi
        flat.removeIf(f -> f.orderId() == 3);
        System.out.println("unnormalised: after deleting order 3, do we know Ravi's city? " + flat.stream().anyMatch(f -> f.customer().equals("Ravi")));
        // Normalised (3NF): each fact stored once
        Map<Integer, String[]> customers = new TreeMap<>(Map.of(1, new String[]{"Asha", "Pune"}, 2, new String[]{"Ravi", "Delhi"}));
        Map<Integer, Object[]> products = new TreeMap<>(Map.of(10, new Object[]{"Shoes", 2499}, 11, new Object[]{"Socks", 199}));
        List<int[]> orders = new ArrayList<>(List.of(new int[]{1, 1, 10}, new int[]{2, 1, 11}, new int[]{3, 2, 10}));
        customers.get(1)[1] = "Mumbai";                                    // one update, everywhere consistent
        orders.removeIf(o -> o[0] == 3);
        System.out.println("normalised  : Asha's city " + customers.get(1)[1] + "; Ravi still known: " + customers.get(2)[0] + " in " + customers.get(2)[1]);
        for (int[] o : orders) System.out.println("  join -> order " + o[0] + ": " + customers.get(o[1])[0] + " (" + customers.get(o[1])[1] + ") bought " + products.get(o[2])[0]);
    }
}
