import java.util.*;

public class MusicStreamingSystem {
    // Audio files in object storage behind a CDN; client prefetches the next track; play events -> royalties count; offline downloads with licence expiry.
    record Track(String id, String title, int seconds, int kbps) {}

    public static void main(String[] args) {
        List<Track> queue = List.of(new Track("t1", "Kesariya", 268, 160), new Track("t2", "Shape of You", 233, 160), new Track("t3", "Naatu Naatu", 216, 320));
        Set<String> cdnEdge = new HashSet<>(List.of("t1", "t2"));                    // popular tracks already at the edge
        Map<String, Long> playCounts = new TreeMap<>(); long bytes = 0;
        for (int i = 0; i < queue.size(); i++) {
            Track t = queue.get(i);
            String src = cdnEdge.contains(t.id()) ? "CDN edge (hit)" : "origin -> CDN (miss, now cached)"; cdnEdge.add(t.id());
            long size = (long) t.seconds() * t.kbps() * 1000 / 8; bytes += size;
            System.out.printf("play %-13s %3ds @%dkbps from %-28s %.1f MB%s%n", t.title(), t.seconds(), t.kbps(), src, size / 1e6, i + 1 < queue.size() ? "  | prefetch next: " + queue.get(i + 1).title() : "");
            if (t.seconds() >= 30) playCounts.merge(t.id(), 1L, Long::sum);              // a 'stream' counts after 30 s
        }
        System.out.printf("session data: %.1f MB; play events for royalties: %s%n", bytes / 1e6, playCounts);
        long licenceExpires = 30; long[] checkDays = {10, 31};
        for (long day : checkDays) System.out.println("offline track on day " + day + ": " + (day < licenceExpires ? "plays (licence valid)" : "locked until the app comes online and renews the licence"));
        double monthlyPlays = 600e6 * 30 * 25;
        System.out.printf("scale: 600M users x 25 tracks/day = %.1e streams/month -> play events go to Kafka, counted in batch%n", monthlyPlays);
    }
}
