import java.security.MessageDigest;
import java.util.*;

public class FileStorageSyncSystem {
    // Block server (chunk + dedup), metadata server (file -> block list, versions), notification of other devices, conflict copies.
    static final Map<String, byte[]> blocks = new HashMap<>();
    record Version(int no, List<String> blockHashes, String device) {}
    static final Map<String, List<Version>> files = new TreeMap<>();
    static final Map<String, List<String>> notifications = new TreeMap<>();
    static final List<String> devices = List.of("laptop", "phone", "tablet");
    static int uploadedBytes = 0;

    static String hash(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b)).substring(0, 8); }
    static List<String> chunk(String content) throws Exception {
        List<String> hs = new ArrayList<>(); byte[] d = content.getBytes();
        for (int i = 0; i < d.length; i += 8) { byte[] c = Arrays.copyOfRange(d, i, Math.min(d.length, i + 8)); String h = hash(c); if (blocks.putIfAbsent(h, c) == null) uploadedBytes += c.length; hs.add(h); }
        return hs;
    }
    static String commit(String device, String path, String content, int baseVersion) throws Exception {
        List<Version> vs = files.computeIfAbsent(path, k -> new ArrayList<>());
        if (baseVersion != vs.size()) { path = path.replace(".", " (" + device + " conflict)."); vs = files.computeIfAbsent(path, k -> new ArrayList<>()); }
        vs.add(new Version(vs.size() + 1, chunk(content), device));
        for (String d : devices) if (!d.equals(device)) notifications.computeIfAbsent(d, k -> new ArrayList<>()).add(path + " v" + vs.size());
        return path + " v" + vs.size();
    }
    static String download(String path, int version) { StringBuilder sb = new StringBuilder(); for (String h : files.get(path).get(version - 1).blockHashes()) sb.append(new String(blocks.get(h))); return sb.toString(); }

    public static void main(String[] args) throws Exception {
        System.out.println("laptop commits " + commit("laptop", "plan.txt", "Day1: arrays. Day2: strings. Day3: graphs.", 0) + ", uploaded " + uploadedBytes + " bytes");
        int before = uploadedBytes;
        System.out.println("laptop commits " + commit("laptop", "plan.txt", "Day1: arrays. Day2: hashing. Day3: graphs.", 1) + ", uploaded " + (uploadedBytes - before) + " bytes (only changed chunks)");
        System.out.println("phone (offline, based on v1) commits " + commit("phone", "plan.txt", "Day1: arrays. Day2: strings. Day3: DP!!!", 1));
        System.out.println("pending notifications: " + notifications);
        System.out.println("tablet downloads plan.txt v2: '" + download("plan.txt", 2) + "'");
        System.out.println("restore plan.txt v1: '" + download("plan.txt", 1) + "'");
    }
}
