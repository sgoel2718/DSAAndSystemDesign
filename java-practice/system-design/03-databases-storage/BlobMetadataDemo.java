import java.security.MessageDigest;
import java.util.*;

public class BlobMetadataDemo {
    record Photo(long id, long owner, String objectKey, int sizeBytes, String sha256, String status) {}
    static final Map<String, byte[]> objectStore = new HashMap<>();          // S3 stand-in: big bytes, cheap
    static final Map<Long, Photo> metadataDb = new TreeMap<>();              // SQL stand-in: small rows, queryable
    static long seq = 0;

    static String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)).substring(0, 12); }

    static Photo upload(long owner, byte[] bytes) throws Exception {
        String h = sha(bytes);
        Optional<Photo> dup = metadataDb.values().stream().filter(p -> p.sha256().equals(h)).findFirst();
        long id = ++seq;
        String key = dup.map(Photo::objectKey).orElse("photos/" + h);
        metadataDb.put(id, new Photo(id, owner, key, bytes.length, h, "PENDING"));        // 1. row first, PENDING
        if (dup.isEmpty()) objectStore.put(key, bytes);                                     // 2. client PUTs bytes (pre-signed URL)
        Photo ready = new Photo(id, owner, key, bytes.length, h, "READY");                  // 3. storage event flips to READY
        metadataDb.put(id, ready);
        return ready;
    }

    public static void main(String[] args) throws Exception {
        byte[] cat = new byte[2_000_000]; Arrays.fill(cat, (byte) 7);
        byte[] dog = new byte[3_000_000]; Arrays.fill(dog, (byte) 9);
        System.out.println(upload(42, cat));
        System.out.println(upload(42, dog));
        System.out.println(upload(7, cat) + "  <- same bytes, deduplicated");
        long stored = objectStore.values().stream().mapToLong(b -> b.length).sum();
        System.out.printf("object store holds %d blobs, %.1f MB; metadata DB holds %d small rows%n", objectStore.size(), stored / 1e6, metadataDb.size());
        System.out.println("query 'photos of user 42' hits only the DB: " + metadataDb.values().stream().filter(p -> p.owner() == 42).map(Photo::id).toList());
    }
}
