import java.util.*;
import java.util.concurrent.*;

public class UnreliableNetworkDemo {
    // A network that drops, delays and duplicates. A naive client double-charges; a careful one uses timeout + retry + idempotency key.
    static final Random net = new Random(12);
    static final Map<String, Integer> processedKeys = new HashMap<>();
    static int charges = 0;

    static String server(String idemKey, int amount) {
        if (idemKey != null && processedKeys.containsKey(idemKey)) return "OK (duplicate ignored)";
        charges += amount; if (idemKey != null) processedKeys.put(idemKey, amount); return "OK";
    }

    // returns null when the reply is lost or too slow (the client can't tell which)
    static String call(String idemKey, int amount, long timeoutMs) {
        int fate = net.nextInt(10);
        if (fate < 2) return null;                                          // request lost: server never saw it
        String reply = server(idemKey, amount);
        if (fate < 4) return null;                                          // reply lost: server DID charge
        long latency = fate == 9 ? 3000 : 40;                               // occasional very slow reply
        return latency > timeoutMs ? null : reply;
    }

    static void pay(String label, boolean useKey, int attempts) {
        charges = 0; processedKeys.clear();
        String key = useKey ? UUID.nameUUIDFromBytes(label.getBytes()).toString() : null;
        int tries = 0; String r = null;
        while (r == null && tries < attempts) { tries++; r = call(key, 500, 1000); }
        System.out.printf("%-34s tries=%d result=%-22s charged=%d%n", label, tries, r == null ? "gave up (unknown!)" : r, charges);
    }

    public static void main(String[] args) {
        for (int i = 1; i <= 4; i++) pay("retry without idempotency #" + i, false, 5);
        for (int i = 1; i <= 4; i++) pay("retry WITH idempotency key #" + i, true, 5);
        System.out.println("Without a key, a lost reply + retry = charged twice. With a key, retries are safe.");
    }
}
