import java.util.*;
import java.util.concurrent.*;

public class IdempotencyKeyDemo {
    record Response(int status, String body) {}
    static final ConcurrentHashMap<String, CompletableFuture<Response>> keys = new ConcurrentHashMap<>();
    static int charges = 0;

    static Response charge(String idemKey, int amount) throws Exception {
        CompletableFuture<Response> mine = new CompletableFuture<>();
        CompletableFuture<Response> existing = keys.putIfAbsent(idemKey, mine);       // atomic "INSERT ... ON CONFLICT DO NOTHING"
        if (existing != null) return existing.get();                                 // replay the stored response (waits if still running)
        synchronized (IdempotencyKeyDemo.class) { charges++; }
        Thread.sleep(20);                                                              // talk to the card network
        Response r = new Response(201, "charge ch_" + charges + " for Rs " + amount);
        mine.complete(r);
        return r;
    }

    public static void main(String[] args) throws Exception {
        System.out.println("first attempt : " + charge("k-81", 500));
        System.out.println("client retry  : " + charge("k-81", 500) + " (same response, no new charge)");
        ExecutorService pool = Executors.newFixedThreadPool(5);
        List<Future<Response>> fs = new ArrayList<>();
        for (int i = 0; i < 5; i++) fs.add(pool.submit(() -> charge("k-99", 700)));    // 5 concurrent duplicate requests
        Set<String> bodies = new TreeSet<>(); for (Future<Response> f : fs) bodies.add(f.get().body());
        pool.shutdown();
        System.out.println("5 concurrent duplicates -> distinct responses " + bodies);
        System.out.println("total charges made: " + charges + " (expected 2)");
    }
}
