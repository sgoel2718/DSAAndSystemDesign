public class EstimationDemo {
    static String human(double v, String unit) {
        String[] counts = {"", " thousand", " million", " billion", " trillion"}, bytes = {" B", " KB", " MB", " GB", " TB", " PB", " EB"};
        String[] u = unit.equals("B") ? bytes : counts; int i = 0;
        while (Math.abs(v) >= 1000 && i < u.length - 1) { v /= 1000; i++; }
        return String.format("%.1f%s", v, u[i]) + (unit.equals("B") || unit.isEmpty() ? "" : " " + unit);
    }

    public static void main(String[] args) {
        double dau = 100e6, uploadShare = 0.10, photoBytes = 2e6, viewsPerUser = 10, peak = 3;
        double uploadsPerDay = dau * uploadShare;
        double writeQps = uploadsPerDay / 86_400;
        double readQps = dau * viewsPerUser / 86_400;
        double storagePerDay = uploadsPerDay * photoBytes;
        System.out.println("Photo app estimate");
        System.out.println("  uploads/day      = " + human(uploadsPerDay, ""));
        System.out.println("  write QPS        = " + human(writeQps, "/s") + ", peak " + human(writeQps * peak, "/s"));
        System.out.println("  read QPS         = " + human(readQps, "/s") + ", peak " + human(readQps * peak, "/s"));
        System.out.println("  read:write ratio = " + Math.round(readQps / writeQps) + " : 1  -> read-heavy, cache + CDN");
        System.out.println("  storage/day      = " + human(storagePerDay, "B"));
        System.out.println("  storage 5 years  = " + human(storagePerDay * 365 * 5, "B") + " -> object storage");
        double egress = readQps * 200e3;                                  // 200 KB thumbnails
        System.out.println("  egress bandwidth = " + human(egress, "B") + "/s -> CDN essential");
    }
}
