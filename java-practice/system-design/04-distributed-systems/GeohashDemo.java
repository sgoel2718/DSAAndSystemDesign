import java.util.*;

public class GeohashDemo {
    static final String B32 = "0123456789bcdefghjkmnpqrstuvwxyz";

    static String encode(double lat, double lon, int len) {
        double[] la = {-90, 90}, lo = {-180, 180}; StringBuilder sb = new StringBuilder(); boolean even = true; int bit = 0, ch = 0;
        while (sb.length() < len) {
            double[] r = even ? lo : la; double v = even ? lon : lat, mid = (r[0] + r[1]) / 2;
            if (v >= mid) { ch = (ch << 1) | 1; r[0] = mid; } else { ch <<= 1; r[1] = mid; }
            even = !even;
            if (++bit == 5) { sb.append(B32.charAt(ch)); bit = 0; ch = 0; }
        }
        return sb.toString();
    }

    static double km(double lat1, double lon1, double lat2, double lon2) {
        double dLat = Math.toRadians(lat2 - lat1), dLon = Math.toRadians(lon2 - lon1);
        double a = Math.pow(Math.sin(dLat / 2), 2) + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) * Math.pow(Math.sin(dLon / 2), 2);
        return 6371 * 2 * Math.asin(Math.sqrt(a));
    }

    record Driver(String id, double lat, double lon) {}

    public static void main(String[] args) {
        double riderLat = 18.5204, riderLon = 73.8567;                       // Pune
        List<Driver> drivers = List.of(new Driver("d1", 18.5210, 73.8570), new Driver("d2", 18.5300, 73.8470),
            new Driver("d3", 18.6000, 73.7500), new Driver("d4", 19.0760, 72.8777), new Driver("d5", 18.5195, 73.8590));
        Map<String, List<Driver>> cells = new TreeMap<>();
        for (Driver d : drivers) cells.computeIfAbsent(encode(d.lat(), d.lon(), 5), k -> new ArrayList<>()).add(d);
        String riderCell = encode(riderLat, riderLon, 5);
        System.out.println("rider geohash5 = " + riderCell + " (cell ~4.9 km)");
        cells.forEach((c, ds) -> System.out.println("  cell " + c + " -> " + ds.stream().map(Driver::id).toList() + (c.equals(riderCell) ? "  <- rider's cell" : "")));
        List<Driver> candidates = cells.getOrDefault(riderCell, List.of());
        candidates.stream().sorted(Comparator.comparingDouble(d -> km(riderLat, riderLon, d.lat(), d.lon())))
            .forEach(d -> System.out.printf("  nearby %s at %.2f km%n", d.id(), km(riderLat, riderLon, d.lat(), d.lon())));
        System.out.println("prefix property: Pune " + encode(18.52, 73.85, 7) + " vs nearby " + encode(18.53, 73.84, 7) + " vs Mumbai " + encode(19.07, 72.87, 7));
        System.out.println("(a driver just across a cell edge is missed unless you also search the 8 neighbouring cells)");
    }
}
