import java.security.MessageDigest;
import java.util.*;

public class PastebinSystem {
    // Metadata in a DB, content in object storage (keyed by content hash), expiry cleanup, and a size limit.
    record Paste(String id, String owner, String objectKey, int sizeBytes, long expiresAt, String visibility) {}
    static final Map<String, Paste> metadata = new LinkedHashMap<>();
    static final Map<String, String> objectStore = new HashMap<>();
    static final int MAX = 1_000_000; static int seq = 0;

    static String sha(String s) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(s.getBytes())).substring(0, 10); }

    static String create(String owner, String text, long ttl, String visibility, long now) throws Exception {
        if (text.length() > MAX) return "413 too large";
        String key = "pastes/" + sha(text);
        objectStore.putIfAbsent(key, text);                                     // identical content stored once
        String id = Long.toString(1_000_000L + (++seq) * 7919, 36);
        metadata.put(id, new Paste(id, owner, key, text.length(), now + ttl, visibility));
        return id;
    }
    static String read(String id, String viewer, long now) {
        Paste p = metadata.get(id);
        if (p == null || p.expiresAt() <= now) return "404";
        if (p.visibility().equals("private") && !p.owner().equals(viewer)) return "403";
        return objectStore.get(p.objectKey());
    }
    static int cleanup(long now) {                                              // background job: delete expired metadata, then orphaned blobs
        int removed = 0;
        for (Iterator<Paste> it = metadata.values().iterator(); it.hasNext(); ) if (it.next().expiresAt() <= now) { it.remove(); removed++; }
        Set<String> live = new HashSet<>(); metadata.values().forEach(p -> live.add(p.objectKey()));
        objectStore.keySet().retainAll(live);
        return removed;
    }

    public static void main(String[] args) throws Exception {
        String a = create("asha", "public static void main(String[] args) {}", 3600, "public", 0);
        String b = create("ravi", "public static void main(String[] args) {}", 60, "public", 0);
        String c = create("asha", "my secret notes", 3600, "private", 0);
        System.out.println("created " + a + ", " + b + ", " + c + "; blobs stored: " + objectStore.size() + " (duplicate content shared)");
        System.out.println("ravi reads " + a + " -> " + read(a, "ravi", 10));
        System.out.println("ravi reads " + c + " -> " + read(c, "ravi", 10));
        System.out.println("t=100 read " + b + " -> " + read(b, "x", 100) + " (expired)");
        System.out.println("cleanup removed " + cleanup(100) + " paste(s); blobs left " + objectStore.size());
        System.out.println("huge paste -> " + create("asha", "x".repeat(MAX + 1), 60, "public", 0));
    }
}
