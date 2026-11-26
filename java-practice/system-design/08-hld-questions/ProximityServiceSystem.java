import java.util.*;

public class ProximityServiceSystem {
    // Businesses indexed by geohash prefix (read-heavy, rarely updated); search = rider cell + 8 neighbours, then exact distance + rating sort.
    record Business(String name, double lat, double lon, double rating) {}
    static final String B32 = "0123456789bcdefghjkmnpqrstuvwxyz";
    static String geohash(double lat, double lon, int len) {
        double[] la = {-90, 90}, lo = {-180, 180}; StringBuilder sb = new StringBuilder(); boolean even = true; int bits = 0, ch = 0;
        while (sb.length() < len) { double[] r = even ? lo : la; double v = even ? lon : lat, mid = (r[0] + r[1]) / 2; if (v >= mid) { ch = ch * 2 + 1; r[0] = mid; } else { ch *= 2; r[1] = mid; } even = !even; if (++bits == 5) { sb.append(B32.charAt(ch)); bits = 0; ch = 0; } }
        return sb.toString();
    }
    static double km(double a, double b, double c, double d) { double x = Math.toRadians(d - b) * Math.cos(Math.toRadians((a + c) / 2)), y = Math.toRadians(c - a); return Math.sqrt(x * x + y * y) * 6371; }
    static List<String> neighbours(double lat, double lon, int len) {
        double dLat = 180 / Math.pow(2, Math.floor(len * 5 / 2.0)), dLon = 360 / Math.pow(2, Math.ceil(len * 5 / 2.0));
        Set<String> out = new TreeSet<>(); for (int i = -1; i <= 1; i++) for (int j = -1; j <= 1; j++) out.add(geohash(lat + i * dLat, lon + j * dLon, len));
        return new ArrayList<>(out);
    }

    public static void main(String[] args) {
        List<Business> all = List.of(new Business("Vaishali", 18.5204, 73.8418, 4.5), new Business("Goodluck Cafe", 18.5178, 73.8414, 4.3),
            new Business("Cafe Paashh", 18.5367, 73.8930, 4.6), new Business("Le Plaisir", 18.5196, 73.8364, 4.7), new Business("Mumbai Bistro", 19.0760, 72.8777, 4.2));
        Map<String, List<Business>> index = new TreeMap<>(); for (Business b : all) index.computeIfAbsent(geohash(b.lat(), b.lon(), 5), k -> new ArrayList<>()).add(b);
        double lat = 18.5190, lon = 73.8400, radiusKm = 2;
        List<String> cells = neighbours(lat, lon, 5);
        System.out.println("user cell " + geohash(lat, lon, 5) + ", searching 9 cells " + cells);
        List<Business> cand = new ArrayList<>(); for (String c : cells) cand.addAll(index.getOrDefault(c, List.of()));
        System.out.println("candidates from index: " + cand.size() + " of " + all.size() + " businesses");
        cand.stream().filter(b -> km(lat, lon, b.lat(), b.lon()) <= radiusKm)
            .sorted(Comparator.comparingDouble(Business::rating).reversed())
            .forEach(b -> System.out.printf("  %-14s %.2f km  rating %.1f%n", b.name(), km(lat, lon, b.lat(), b.lon()), b.rating()));
    }
}
