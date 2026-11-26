import java.util.*;

public class CapDemo {
    static class Replica {
        final String name; int balance = 800; boolean partitioned;
        Replica(String name) { this.name = name; }
    }

    static Replica mumbai = new Replica("Mumbai"), chennai = new Replica("Chennai");

    static void write(Replica at, int value) {
        at.balance = value;
        if (!at.partitioned) { mumbai.balance = value; chennai.balance = value; }   // replicate when the link works
    }

    static String read(Replica at, boolean preferConsistency) {
        if (at.partitioned && preferConsistency) return "ERROR: can't confirm latest value (CP)";
        return at.balance + (at.partitioned ? " (may be stale, AP)" : "");
    }

    public static void main(String[] args) {
        write(mumbai, 500);
        System.out.println("link OK      : Chennai reads " + read(chennai, true));
        mumbai.partitioned = chennai.partitioned = true;                 // cut the network
        write(mumbai, 200);
        System.out.println("partitioned  : Mumbai wrote 200");
        System.out.println("  CP choice  : Chennai reads " + read(chennai, true));
        System.out.println("  AP choice  : Chennai reads " + read(chennai, false));
        mumbai.partitioned = chennai.partitioned = false;                // heal and resync
        chennai.balance = mumbai.balance;
        System.out.println("healed       : Chennai reads " + read(chennai, true));
    }
}
