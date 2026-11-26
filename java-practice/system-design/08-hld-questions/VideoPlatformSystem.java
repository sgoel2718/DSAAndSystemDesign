import java.util.*;
import java.util.concurrent.*;

public class VideoPlatformSystem {
    // Upload -> chunk -> parallel transcode DAG (renditions x chunks) -> manifest -> CDN; view counting buffered.
    record Segment(int index, String rendition) {}

    public static void main(String[] args) throws Exception {
        int durationSec = 60, chunkSec = 6; String[] renditions = {"240p", "480p", "720p", "1080p"};
        int chunks = durationSec / chunkSec;
        ExecutorService workers = Executors.newFixedThreadPool(4);
        List<Future<Segment>> jobs = new ArrayList<>();
        long t0 = System.nanoTime();
        for (int c = 0; c < chunks; c++) for (String r : renditions) { final int ci = c; final String rr = r;
            jobs.add(workers.submit(() -> { Thread.sleep(5); return new Segment(ci, rr); })); }      // each task = encode one chunk at one quality
        Map<String, List<Integer>> done = new TreeMap<>();
        for (Future<Segment> f : jobs) { Segment s = f.get(); done.computeIfAbsent(s.rendition(), k -> new ArrayList<>()).add(s.index()); }
        workers.shutdown();
        System.out.printf("transcoded %d chunks x %d renditions = %d tasks on 4 workers in ~%d ms (sequential would be ~%d ms)%n", chunks, renditions.length, jobs.size(), Math.round((System.nanoTime() - t0) / 1e7) * 10, jobs.size() * 5);
        StringBuilder manifest = new StringBuilder("#EXTM3U\n");
        int[] bw = {400_000, 1_400_000, 2_800_000, 5_000_000};
        for (int i = 0; i < renditions.length; i++) manifest.append("#EXT-X-STREAM-INF:BANDWIDTH=").append(bw[i]).append("\n").append(renditions[i]).append("/index.m3u8\n");
        System.out.print("master playlist (served from CDN):\n" + manifest);
        System.out.println("720p media playlist has " + done.get("720p").size() + " segments: " + done.get("720p").stream().map(i -> "seg" + i + ".ts").limit(3).toList() + " ...");
        Map<String, Long> viewBuffer = new HashMap<>(); long dbWrites = 0;
        for (int i = 0; i < 100_000; i++) { viewBuffer.merge("video:7", 1L, Long::sum); if (i % 20_000 == 19_999) { viewBuffer.clear(); dbWrites++; } }
        System.out.println("100,000 views -> " + dbWrites + " DB writes (buffered counts flushed every 20,000)");
    }
}
