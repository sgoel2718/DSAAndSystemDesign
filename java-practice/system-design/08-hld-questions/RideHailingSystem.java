import java.util.*;

public class RideHailingSystem {
    // Drivers send location every few seconds -> in-memory geo index; matching offers the ride to the nearest available
    // driver with a timeout; trip state machine; surge from demand/supply per cell.
    enum TripState { REQUESTED, ACCEPTED, ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED }
    record Driver(String id, double lat, double lon, boolean available) {}
    static final Map<String, Driver> drivers = new TreeMap<>();
    static double dist(double a, double b, double c, double d) { return Math.hypot(a - c, (b - d) * Math.cos(Math.toRadians(a))) * 111; }
    static String cell(double lat, double lon) { return String.format("%.2f,%.2f", Math.floor(lat * 50) / 50, Math.floor(lon * 50) / 50); }

    static void heartbeat(String id, double lat, double lon, boolean avail) { drivers.put(id, new Driver(id, lat, lon, avail)); }

    public static void main(String[] args) {
        heartbeat("d1", 18.520, 73.856, true); heartbeat("d2", 18.522, 73.860, true); heartbeat("d3", 18.540, 73.880, true); heartbeat("d4", 18.521, 73.857, false);
        double rLat = 18.5205, rLon = 73.8565;
        Set<String> declined = Set.of("d1");                                           // d1 ignores the offer (timeout)
        List<Driver> nearby = drivers.values().stream().filter(Driver::available).sorted(Comparator.comparingDouble(d -> dist(rLat, rLon, d.lat(), d.lon()))).toList();
        System.out.println("nearby available drivers: " + nearby.stream().map(d -> String.format("%s(%.2f km)", d.id(), dist(rLat, rLon, d.lat(), d.lon()))).toList());
        String assigned = null;
        for (Driver d : nearby) {
            System.out.print("offer to " + d.id() + " (15 s timeout) -> ");
            if (declined.contains(d.id())) { System.out.println("no response"); continue; }
            System.out.println("accepted"); assigned = d.id(); break;
        }
        heartbeat(assigned, drivers.get(assigned).lat(), drivers.get(assigned).lon(), false);   // lock driver: no double assignment
        TripState s = TripState.REQUESTED; StringBuilder path = new StringBuilder(s.name());
        for (TripState next : List.of(TripState.ACCEPTED, TripState.ARRIVED, TripState.IN_PROGRESS, TripState.COMPLETED)) { s = next; path.append(" -> ").append(s); }
        System.out.println("trip " + path);
        Map<String, int[]> demandSupply = new TreeMap<>();
        for (Driver d : drivers.values()) if (d.available()) demandSupply.computeIfAbsent(cell(d.lat(), d.lon()), k -> new int[2])[1]++;
        for (int i = 0; i < 9; i++) demandSupply.computeIfAbsent(cell(rLat, rLon), k -> new int[2])[0]++;
        demandSupply.forEach((c, ds) -> System.out.printf("cell %s: %d requests / %d drivers -> surge x%.1f%n", c, ds[0], ds[1], Math.min(3.0, Math.max(1.0, ds[0] / Math.max(1.0, ds[1]) / 2))));
    }
}
