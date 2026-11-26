import java.util.*;
import java.util.concurrent.*;

public class RealtimeDemo {
    // Compares short polling, long polling and push (WebSocket/SSE style) for the same 3 messages.
    static final BlockingQueue<String> inbox = new LinkedBlockingQueue<>();
    static final List<Long> arrivalMs = List.of(120L, 450L, 460L);

    public static void main(String[] args) throws Exception {
        // Short polling every 200 ms: requests are made even when nothing is new
        int requests = 0; List<String> log = new ArrayList<>();
        for (long t = 0; t <= 600; t += 200) {
            requests++;
            for (long a : arrivalMs) if (a > t - 200 && a <= t) log.add("msg@" + a + " seen@" + t + " (late " + (t - a) + " ms)");
        }
        System.out.println("short polling: " + requests + " requests -> " + log);
        // Long polling: server holds the request until a message arrives (real threads + queue)
        ExecutorService server = Executors.newSingleThreadExecutor();
        long start = System.currentTimeMillis();
        server.submit(() -> { for (long a : arrivalMs) { sleepUntil(start + a); inbox.add("msg@" + a); } });
        List<String> got = new ArrayList<>(); int longPolls = 0;
        while (got.size() < 3) {
            longPolls++;
            String m = inbox.poll(2, TimeUnit.SECONDS);                  // held open until data or timeout
            if (m != null) { got.add(m); inbox.drainTo(got); }
        }
        server.shutdown();
        System.out.println("long polling : " + longPolls + " requests -> " + got + " (each delivered as soon as it arrived)");
        // Push: one open connection, server calls the client callback
        List<String> pushed = new ArrayList<>();
        java.util.function.Consumer<String> socket = pushed::add;
        for (long a : arrivalMs) socket.accept("msg@" + a);
        System.out.println("push (WS/SSE): 1 connection -> " + pushed);
    }

    static void sleepUntil(long t) { try { Thread.sleep(Math.max(0, t - System.currentTimeMillis())); } catch (InterruptedException ignored) {} }
}
