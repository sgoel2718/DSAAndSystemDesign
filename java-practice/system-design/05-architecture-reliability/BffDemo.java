import java.util.*;
import java.util.concurrent.*;

public class BffDemo {
    static Map<String, Object> userSvc(String id) { sleep(30); return Map.of("name", "Asha", "avatar", "a.png", "email", "asha@x.com", "address", "Pune", "joined", 2019); }
    static List<String> ordersSvc(String id) { sleep(40); return List.of("order-987", "order-988", "order-990"); }
    static List<String> recsSvc(String id) { sleep(50); return List.of("socks", "cap", "bottle", "bag"); }
    static void sleep(long ms) { try { Thread.sleep(ms); } catch (InterruptedException ignored) {} }

    // Mobile BFF: one call, parallel fan-out, small payload shaped for the phone screen
    static Map<String, Object> mobileHome(String user) throws Exception {
        ExecutorService ex = Executors.newFixedThreadPool(3);
        try {
            var u = ex.submit(() -> userSvc(user)); var o = ex.submit(() -> ordersSvc(user)); var r = ex.submit(() -> recsSvc(user));
            return Map.of("name", u.get().get("name"), "lastOrder", o.get().get(0), "recs", r.get().subList(0, 2));
        } finally { ex.shutdown(); }
    }

    public static void main(String[] args) throws Exception {
        mobileHome("warm-up");                                               // warm up the JVM before timing
        long t = System.nanoTime();
        Map<String, Object> raw = new LinkedHashMap<>(); raw.put("user", userSvc("42")); raw.put("orders", ordersSvc("42")); raw.put("recs", recsSvc("42"));
        long seqMs = (System.nanoTime() - t) / 1_000_000;
        t = System.nanoTime();
        Map<String, Object> mobile = mobileHome("42");
        long bffMs = (System.nanoTime() - t) / 1_000_000;
        System.out.println("without BFF: phone makes 3 calls one after another, ~" + Math.round(seqMs / 10.0) * 10 + " ms, payload " + raw.toString().length() + " chars");
        System.out.println("with BFF   : 1 call, BFF fans out in parallel, ~" + Math.round(bffMs / 10.0) * 10 + " ms, payload " + mobile.toString().length() + " chars -> " + new TreeMap<>(mobile));
        System.out.println("(on a phone each extra round trip also costs ~100+ ms of mobile network latency)");
    }
}
