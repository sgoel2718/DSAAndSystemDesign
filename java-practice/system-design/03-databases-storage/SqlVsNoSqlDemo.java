import java.util.*;
import java.util.stream.*;

public class SqlVsNoSqlDemo {
    // Relational: normalised tables joined at read time. Document: one denormalised record per order.
    record Customer(int id, String name) {}
    record OrderRow(int id, int customerId, String status) {}
    record ItemRow(int orderId, String product, int qty, int price) {}

    public static void main(String[] args) {
        List<Customer> customers = List.of(new Customer(42, "Asha"), new Customer(7, "Ravi"));
        List<OrderRow> orders = List.of(new OrderRow(987, 42, "PAID"), new OrderRow(988, 7, "PENDING"));
        List<ItemRow> items = List.of(new ItemRow(987, "Shoes", 1, 2499), new ItemRow(987, "Socks", 3, 199), new ItemRow(988, "Cap", 1, 399));
        // SQL-style: SELECT ... FROM orders JOIN customers JOIN order_items WHERE orders.id = 987
        OrderRow o = orders.stream().filter(x -> x.id() == 987).findFirst().get();
        Customer c = customers.stream().filter(x -> x.id() == o.customerId()).findFirst().get();
        List<ItemRow> its = items.stream().filter(x -> x.orderId() == 987).toList();
        System.out.println("SQL join (3 tables): order " + o.id() + " by " + c.name() + " items " + its.stream().map(ItemRow::product).toList());
        // Document-style: everything the page needs in one record, fetched by key
        Map<Integer, Map<String, Object>> docs = new HashMap<>();
        for (OrderRow or : orders) {
            Customer cu = customers.stream().filter(x -> x.id() == or.customerId()).findFirst().get();
            docs.put(or.id(), Map.of("status", or.status(), "customer", Map.of("id", cu.id(), "name", cu.name()),
                "items", items.stream().filter(i -> i.orderId() == or.id()).map(i -> Map.of("product", i.product(), "qty", i.qty())).toList()));
        }
        System.out.println("Document get(987)  : " + docs.get(987));
        // The trade-off: Asha renames herself
        customers = List.of(new Customer(42, "Asha K"), new Customer(7, "Ravi"));
        System.out.println("\nAfter rename -> SQL reads the new name from one row: " + customers.get(0).name());
        System.out.println("Document still has the copied old name: " + ((Map<?, ?>) docs.get(987).get("customer")).get("name") + " (must update every copy)");
        int revenue = items.stream().mapToInt(i -> i.qty() * i.price()).sum();
        System.out.println("Ad-hoc report (SUM over all items) is easy in SQL: total revenue = " + revenue);
    }
}
