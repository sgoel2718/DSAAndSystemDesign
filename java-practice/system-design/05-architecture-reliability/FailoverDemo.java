import java.util.*;

public class FailoverDemo {
    static class Db { final String name; boolean alive = true; long lsn = 0; Db(String n) { name = n; } }

    public static void main(String[] args) {
        Db primary = new Db("db-primary"), standby = new Db("db-standby");
        String vip = primary.name; int missed = 0; long lostWrites = 0;
        for (int t = 0; t <= 60; t += 5) {
            if (primary.alive) { primary.lsn += 10; if (t % 10 == 0) standby.lsn = primary.lsn; }    // async replication every 10 s
            if (t == 25) { primary.alive = false; System.out.println("t=25 primary crashes (lsn " + primary.lsn + ", standby at " + standby.lsn + ")"); }
            if (vip.equals(primary.name)) {
                if (primary.alive) missed = 0; else missed++;
                if (missed == 3) {
                    lostWrites = primary.lsn - standby.lsn;
                    vip = standby.name;
                    System.out.println("t=" + t + " 3 health checks failed -> promote standby, move virtual IP -> " + vip);
                }
            }
            System.out.printf("t=%2d app writes go to %-11s %s%n", t, vip, vip.equals(primary.name) && !primary.alive ? "(FAILING: downtime)" : "");
        }
        System.out.println("downtime ~ detection (3 x 5 s) = 15 s; writes lost because replication was async: " + lostWrites);
        System.out.println("old primary must be fenced (never accept writes again) to avoid split brain.");
    }
}
