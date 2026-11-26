import java.util.*;

public class InstagramSystem {
    // Upload flow (pre-signed URL -> object store -> async thumbnail job -> ready), likes with buffered counters, profile grid query.
    record Photo(long id, String owner, String objectKey, List<String> thumbs, String status, long ts) {}
    static final Map<Long, Photo> photos = new TreeMap<>(); static final Map<String, byte[]> objectStore = new HashMap<>();
    static final Deque<Long> thumbnailQueue = new ArrayDeque<>(); static final Map<Long, Long> likeBuffer = new HashMap<>(), likesDb = new HashMap<>();
    static long seq = 0;

    static long requestUpload(String owner, long ts) { long id = ++seq; photos.put(id, new Photo(id, owner, "raw/" + id + ".jpg", List.of(), "PENDING", ts)); return id; }
    static void clientUploads(long id, int bytes) { objectStore.put(photos.get(id).objectKey(), new byte[bytes]); thumbnailQueue.add(id); }   // storage event -> queue
    static void thumbnailWorker() {
        while (!thumbnailQueue.isEmpty()) {
            Photo p = photos.get(thumbnailQueue.poll()); List<String> t = new ArrayList<>();
            for (int size : new int[]{150, 640, 1080}) { String k = "thumb/" + p.id() + "_" + size + ".jpg"; objectStore.put(k, new byte[size * 50]); t.add(k); }
            photos.put(p.id(), new Photo(p.id(), p.owner(), p.objectKey(), t, "READY", p.ts()));
        }
    }
    static void like(long photoId) { likeBuffer.merge(photoId, 1L, Long::sum); }
    static void flushLikes() { likeBuffer.forEach((k, v) -> likesDb.merge(k, v, Long::sum)); likeBuffer.clear(); }

    public static void main(String[] args) {
        long a = requestUpload("asha", 100), b = requestUpload("asha", 200), c = requestUpload("ravi", 150);
        clientUploads(a, 3_000_000); clientUploads(b, 2_500_000);
        System.out.println("before worker: " + photos.values().stream().map(p -> p.id() + "=" + p.status()).toList());
        thumbnailWorker();
        System.out.println("after worker : " + photos.values().stream().map(p -> p.id() + "=" + p.status()).toList() + " (photo " + c + " never uploaded: cleanup job deletes it later)");
        for (int i = 0; i < 10_000; i++) like(i % 10 == 0 ? b : a);
        flushLikes();
        System.out.println("likes after buffered flush: " + likesDb + " (1 DB write per photo per flush, not 10,000)");
        List<String> grid = photos.values().stream().filter(p -> p.owner().equals("asha") && p.status().equals("READY")).sorted(Comparator.comparingLong(Photo::ts).reversed()).map(p -> p.thumbs().get(0)).toList();
        System.out.println("asha's profile grid (newest first, 150px thumbs via CDN): " + grid);
    }
}
