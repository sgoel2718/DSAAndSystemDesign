import java.util.*;

public class PaymentSystem {
    // Payment intent state machine, idempotent API, PSP call with timeout + status polling, double-entry ledger, reconciliation.
    enum State { CREATED, PROCESSING, SUCCEEDED, FAILED }
    record Intent(String id, long amountPaise, State state, String pspRef) {}
    static final Map<String, Intent> intents = new TreeMap<>(); static final Map<String, String> idem = new HashMap<>();
    static final List<String> ledger = new ArrayList<>(); static final Map<String, String> pspSide = new HashMap<>();
    static int seq = 0;

    static Intent create(String key, long amount) { String id = idem.computeIfAbsent(key, k -> "pi_" + (++seq)); intents.putIfAbsent(id, new Intent(id, amount, State.CREATED, null)); return intents.get(id); }
    static Intent pay(String id, boolean pspTimesOut) {
        Intent i = intents.get(id); if (i.state() != State.CREATED) return i;           // idempotent: no second charge
        intents.put(id, new Intent(id, i.amountPaise(), State.PROCESSING, null));
        String ref = "psp_" + id; pspSide.put(ref, "CAPTURED");                         // PSP actually charged the card
        if (pspTimesOut) return intents.get(id);                                         // ...but our call timed out: stay PROCESSING
        return succeed(id, ref);
    }
    static Intent succeed(String id, String ref) {
        Intent i = intents.get(id); intents.put(id, new Intent(id, i.amountPaise(), State.SUCCEEDED, ref));
        ledger.add(id + " DEBIT customer " + i.amountPaise()); ledger.add(id + " CREDIT merchant " + i.amountPaise());
        return intents.get(id);
    }
    static void pollStuck() { intents.values().stream().filter(i -> i.state() == State.PROCESSING).toList().forEach(i -> { String ref = "psp_" + i.id(); if ("CAPTURED".equals(pspSide.get(ref))) { System.out.println("  poller: PSP says " + ref + " captured -> mark SUCCEEDED"); succeed(i.id(), ref); } }); }

    public static void main(String[] args) {
        Intent a = create("order-987", 2_499_00); System.out.println("create  -> " + a);
        System.out.println("create again (same key) -> " + create("order-987", 2_499_00).id() + " (same intent)");
        System.out.println("pay     -> " + pay(a.id(), false));
        System.out.println("pay again -> " + pay(a.id(), false).state() + " (no second charge)");
        Intent b = create("order-988", 999_00);
        System.out.println("pay with PSP timeout -> " + pay(b.id(), true).state() + " (unknown outcome: do NOT retry blindly)");
        pollStuck();
        System.out.println("ledger: " + ledger);
        long ourTotal = intents.values().stream().filter(i -> i.state() == State.SUCCEEDED).mapToLong(Intent::amountPaise).sum();
        System.out.println("reconciliation: our captured total " + ourTotal + " vs PSP captured count " + pspSide.size() + " -> " + (pspSide.size() == intents.values().stream().filter(i -> i.state() == State.SUCCEEDED).count() ? "match" : "MISMATCH"));
    }
}
