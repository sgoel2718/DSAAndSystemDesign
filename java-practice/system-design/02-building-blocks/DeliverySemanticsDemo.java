import java.util.*;

public class DeliverySemanticsDemo {
    // The consumer may crash after applying a message but before committing its offset -> the message is redelivered.
    record Msg(String id, String user, int amount) {}
    static final List<Msg> log = List.of(new Msg("m1", "asha", 500), new Msg("m2", "asha", 200), new Msg("m3", "ravi", 300));

    static Map<String, Integer> run(String mode) {
        Map<String, Integer> wallet = new TreeMap<>(Map.of("asha", 1000, "ravi", 1000));
        Set<String> processed = new HashSet<>();
        int offset = 0; boolean crashedOnce = false;
        while (offset < log.size()) {
            Msg m = log.get(offset);
            if (mode.equals("at-most-once")) offset++;                                 // commit BEFORE processing
            boolean crash = m.id().equals("m2") && !crashedOnce;
            if (mode.equals("at-most-once") && crash) { crashedOnce = true; continue; }  // crashed: m2 is lost
            if (mode.equals("exactly-once") && processed.contains(m.id())) { offset++; continue; }
            wallet.merge(m.user(), -m.amount(), Integer::sum);                         // the side effect (charge)
            if (mode.equals("exactly-once")) processed.add(m.id());                    // same transaction as the charge
            if (crash && !mode.equals("at-most-once")) { crashedOnce = true; continue; } // crash before committing -> redelivered
            if (!mode.equals("at-most-once")) offset++;                                // commit AFTER processing
        }
        return wallet;
    }

    public static void main(String[] args) {
        System.out.println("expected                : {asha=300, ravi=700}");
        for (String mode : List.of("at-most-once", "at-least-once", "exactly-once"))
            System.out.printf("%-24s: %s%n", mode, run(mode));
        System.out.println("at-most-once lost m2; at-least-once charged m2 twice; dedup by message id fixes it.");
    }
}
