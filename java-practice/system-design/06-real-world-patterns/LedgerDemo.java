import java.util.*;

public class LedgerDemo {
    record Entry(long txId, String account, long debitPaise, long creditPaise) {}
    static final List<Entry> ledger = new ArrayList<>();                       // append-only
    static final Map<String, Long> idempotency = new HashMap<>();
    static long txSeq = 0;

    static long post(String idemKey, List<Entry> lines) {
        if (idempotency.containsKey(idemKey)) return idempotency.get(idemKey);
        long d = lines.stream().mapToLong(Entry::debitPaise).sum(), c = lines.stream().mapToLong(Entry::creditPaise).sum();
        if (d != c) throw new IllegalArgumentException("unbalanced transaction: debits " + d + " != credits " + c);
        long id = ++txSeq;
        for (Entry e : lines) ledger.add(new Entry(id, e.account(), e.debitPaise(), e.creditPaise()));
        idempotency.put(idemKey, id); return id;
    }
    static long balance(String acct) { return ledger.stream().filter(e -> e.account().equals(acct)).mapToLong(e -> e.creditPaise() - e.debitPaise()).sum(); }
    static String rs(long paise) { return String.format("Rs %,.2f", paise / 100.0); }

    public static void main(String[] args) {
        post("topup-1", List.of(new Entry(0, "bank:settlement", 200_000, 0), new Entry(0, "wallet:asha", 0, 200_000)));
        post("pay-77", List.of(new Entry(0, "wallet:asha", 100_000, 0), new Entry(0, "merchant:shoeshop", 0, 98_000), new Entry(0, "revenue:fees", 0, 2_000)));
        post("pay-77", List.of(new Entry(0, "wallet:asha", 100_000, 0), new Entry(0, "merchant:shoeshop", 0, 98_000), new Entry(0, "revenue:fees", 0, 2_000)));   // retry
        try { post("bad-1", List.of(new Entry(0, "wallet:asha", 500, 0), new Entry(0, "merchant:shoeshop", 0, 400))); }
        catch (IllegalArgumentException e) { System.out.println("rejected: " + e.getMessage()); }
        post("refund-77", List.of(new Entry(0, "merchant:shoeshop", 98_000, 0), new Entry(0, "revenue:fees", 2_000, 0), new Entry(0, "wallet:asha", 0, 100_000)));
        ledger.forEach(e -> System.out.printf("tx%d %-18s debit %10s credit %10s%n", e.txId(), e.account(), e.debitPaise() > 0 ? rs(e.debitPaise()) : "", e.creditPaise() > 0 ? rs(e.creditPaise()) : ""));
        for (String a : List.of("wallet:asha", "merchant:shoeshop", "revenue:fees")) System.out.println("balance " + a + " = " + rs(balance(a)));
        System.out.println("sum of all balances (+ settlement) = " + rs(ledger.stream().mapToLong(e -> e.creditPaise() - e.debitPaise()).sum()) + "  (always zero)");
    }
}
