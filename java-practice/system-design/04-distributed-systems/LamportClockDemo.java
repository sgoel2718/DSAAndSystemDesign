import java.util.*;

public class LamportClockDemo {
    static class Process {
        final String name; long clock = 0; final List<String> events = new ArrayList<>();
        Process(String n) { name = n; }
        void local(String what) { clock++; events.add(what + "@" + clock); }
        long send(String what) { clock++; events.add("send " + what + "@" + clock); return clock; }
        void receive(String what, long t) { clock = Math.max(clock, t) + 1; events.add("recv " + what + "@" + clock); }
    }

    public static void main(String[] args) {
        Process p1 = new Process("P1"), p2 = new Process("P2"), p3 = new Process("P3");
        p1.local("a");
        long m1 = p1.send("m1");
        p3.local("x"); p3.local("y");
        p2.receive("m1", m1);
        long m2 = p2.send("m2");
        p3.receive("m2", m2);
        p1.local("b");
        for (Process p : List.of(p1, p2, p3)) System.out.println(p.name + ": " + p.events);
        System.out.println("send m1 (" + m1 + ") < recv m1 on P2 (" + (m1 + 1) + "): causality preserved");
        System.out.println("P1 'b'@3 and P3 'x'@1 are concurrent; Lamport order says x<b but can't tell they're concurrent (use vector clocks)");
        // Wall clocks: skew can reverse order
        long serverA = 1_000_000 + 0, serverB = 1_000_000 - 120;              // B's clock is 120 ms behind
        System.out.println("\nwall clocks: A writes at " + serverA + ", then B overwrites at " + (serverB + 50) + " -> last-write-wins keeps A's older write!");
    }
}
