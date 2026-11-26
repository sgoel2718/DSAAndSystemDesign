import java.util.*;

public class ColumnStoreDemo {
    // Same 1,000,000 orders stored row-wise and column-wise; an analytics query only needs 2 columns.
    record Order(long id, int customerId, String city, String product, int qty, int priceRs, int year, String status) {}

    public static void main(String[] args) {
        int n = 1_000_000; Random r = new Random(9);
        String[] cities = {"Pune", "Delhi", "Chennai", "Mumbai"};
        Order[] rows = new Order[n];
        int[] priceCol = new int[n]; short[] yearCol = new short[n];
        for (int i = 0; i < n; i++) {
            Order o = new Order(i, r.nextInt(100_000), cities[r.nextInt(4)], "sku-" + r.nextInt(5000), 1 + r.nextInt(3), 100 + r.nextInt(5000), 2023 + r.nextInt(3), "PAID");
            rows[i] = o; priceCol[i] = o.priceRs(); yearCol[i] = (short) o.year();
        }
        long t = System.nanoTime(); long s1 = 0, c1 = 0;
        for (Order o : rows) if (o.year() == 2025) { s1 += o.priceRs(); c1++; }
        double rowMs = (System.nanoTime() - t) / 1e6;
        t = System.nanoTime(); long s2 = 0, c2 = 0;
        for (int i = 0; i < n; i++) if (yearCol[i] == 2025) { s2 += priceCol[i]; c2++; }
        double colMs = (System.nanoTime() - t) / 1e6;
        System.out.printf("AVG(price) WHERE year=2025 -> row store %.1f (scanned whole records), column store %.1f%n", s1 / (double) c1, s2 / (double) c2);
        System.out.printf("columns touched: row store all 8, column store 2 (%d bytes per row instead of ~80)%n", 4 + 2);
        System.out.println("column store was " + (colMs < rowMs ? "faster" : "not faster this run") + " (timings vary; the I/O saving on disk is the big win)");
        // Rollup / downsampling: 1-second CPU samples -> 1-minute averages
        double[] perSecond = new double[3600]; for (int i = 0; i < 3600; i++) perSecond[i] = 40 + 20 * Math.sin(i / 600.0) + r.nextInt(5);
        double[] perMinute = new double[60];
        for (int m = 0; m < 60; m++) { double sum = 0; for (int s = 0; s < 60; s++) sum += perSecond[m * 60 + s]; perMinute[m] = sum / 60; }
        System.out.printf("downsampling: 3600 points -> 60 points; minute 0 avg %.1f%%, minute 30 avg %.1f%%%n", perMinute[0], perMinute[30]);
        // Delta encoding of timestamps
        long[] ts = {1764140000, 1764140010, 1764140020, 1764140031};
        List<Long> deltas = new ArrayList<>(); for (int i = 1; i < ts.length; i++) deltas.add(ts[i] - ts[i - 1]);
        System.out.println("delta encoding: " + Arrays.toString(ts) + " -> first " + ts[0] + " + deltas " + deltas + " (tiny numbers compress well)");
    }
}
