import java.security.MessageDigest;
import java.util.*;

public class FileSyncDemo {
    static final int CHUNK = 4;                                                 // 4 bytes for the demo (4 MB in real life)
    static final Map<String, byte[]> blockStore = new HashMap<>();              // hash -> bytes (dedup across all users)
    static final Map<String, List<String>> fileVersions = new HashMap<>();      // path -> chunk hashes of latest version
    static final Map<String, Integer> versionNo = new HashMap<>();

    static String sha(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)).substring(0, 6); }

    static void upload(String device, String path, String content, int baseVersion) throws Exception {
        int current = versionNo.getOrDefault(path, 0);
        if (baseVersion != current) {                                         // someone else changed it meanwhile
            String copy = path.replace(".txt", " (" + device + "'s conflicted copy).txt");
            System.out.println(device + ": conflict on " + path + " (based on v" + baseVersion + ", server has v" + current + ") -> saved as '" + copy + "'");
            upload(device, copy, content, versionNo.getOrDefault(copy, 0)); return;
        }
        byte[] data = content.getBytes(); List<String> hashes = new ArrayList<>(); int uploaded = 0;
        for (int i = 0; i < data.length; i += CHUNK) {
            byte[] c = Arrays.copyOfRange(data, i, Math.min(data.length, i + CHUNK)); String h = sha(c); hashes.add(h);
            if (!blockStore.containsKey(h)) { blockStore.put(h, c); uploaded++; }
        }
        fileVersions.put(path, hashes); versionNo.put(path, current + 1);
        System.out.println(device + ": " + path + " v" + (current + 1) + " = " + hashes.size() + " chunks, uploaded " + uploaded + " new, skipped " + (hashes.size() - uploaded));
    }

    public static void main(String[] args) throws Exception {
        upload("laptop", "notes.txt", "AAAABBBBCCCCDDDD", 0);
        upload("laptop", "notes.txt", "AAAABBBBXXXXDDDD", 1);                   // edit in the middle: only 1 chunk changes
        upload("phone", "copy.txt", "AAAABBBBCCCCDDDD", 0);                     // same content elsewhere: fully deduplicated
        upload("phone", "notes.txt", "AAAAZZZZCCCCDDDD", 1);                    // phone edited an old version offline
        System.out.println("block store holds " + blockStore.size() + " unique chunks for 4 files/versions");
    }
}
