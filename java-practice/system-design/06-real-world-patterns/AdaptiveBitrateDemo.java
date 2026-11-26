import java.util.*;

public class AdaptiveBitrateDemo {
    record Rendition(String name, int kbps) {}
    static final List<Rendition> ladder = List.of(new Rendition("240p", 400), new Rendition("360p", 800), new Rendition("480p", 1400),
        new Rendition("720p", 2800), new Rendition("1080p", 5000), new Rendition("4K", 16000));

    public static void main(String[] args) {
        int segmentSec = 4; double buffer = 0, estimateKbps = 0;
        int[] networkKbps = {6000, 8000, 8000, 1500, 1200, 6000, 9000, 25000, 25000};   // measured per segment (tunnel at 4-5)
        int stalls = 0;
        System.out.println("seg  network   pick    buffer  note");
        for (int i = 0; i < networkKbps.length; i++) {
            Rendition pick = ladder.get(0);
            if (i > 0) for (Rendition r : ladder) if (r.kbps() <= estimateKbps * 0.8 && (buffer > 6 || r.kbps() <= 1400)) pick = r;
            double downloadSec = pick.kbps() * segmentSec / (double) networkKbps[i];
            String note = "";
            if (downloadSec > buffer && i > 0) { stalls++; note = "STALL (rebuffering)"; buffer = 0; } else buffer -= downloadSec;
            buffer = Math.max(0, buffer) + segmentSec;
            estimateKbps = i == 0 ? networkKbps[i] : 0.7 * estimateKbps + 0.3 * networkKbps[i];   // smoothed throughput estimate
            System.out.printf("%3d  %5d kbps  %-6s  %4.1f s  %s%n", i + 1, networkKbps[i], pick.name(), buffer, note);
        }
        System.out.println("stalls: " + stalls + " - the smoothed throughput estimate lagged behind the sudden drop; a buffer-based rule (practice task 1) reacts faster");
        long totalKbps = ladder.stream().mapToLong(Rendition::kbps).sum();
        System.out.printf("storage for a 10-minute video, all renditions: %.2f GB%n", totalKbps * 1000L / 8.0 * 600 / 1e9);
    }
}
