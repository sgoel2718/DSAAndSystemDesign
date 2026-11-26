import java.security.*;
import java.util.*;

public class ObjectStoreDemo {
    // Object storage: flat key -> bytes + metadata, whole-object PUT/GET, multipart upload, pre-signed URLs.
    record Obj(byte[] data, Map<String, String> meta) {}
    static final Map<String, Obj> bucket = new TreeMap<>();
    static final Map<String, List<byte[]>> multipart = new HashMap<>();
    static final String SECRET = "server-secret";

    static String presign(String key, long expiresAt) throws Exception {
        String sig = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest((key + expiresAt + SECRET).getBytes())).substring(0, 16);
        return "/" + key + "?expires=" + expiresAt + "&sig=" + sig;
    }
    static boolean verify(String key, long expiresAt, String sig, long now) throws Exception {
        return now < expiresAt && presign(key, expiresAt).endsWith("sig=" + sig);
    }

    public static void main(String[] args) throws Exception {
        String url = presign("videos/7/raw.mp4", 900);
        System.out.println("API hands the client a pre-signed URL: " + url);
        String sig = url.substring(url.indexOf("sig=") + 4);
        System.out.println("client PUT at t=100 allowed? " + verify("videos/7/raw.mp4", 900, sig, 100));
        System.out.println("client PUT at t=1000 allowed? " + verify("videos/7/raw.mp4", 900, sig, 1000) + " (expired)");
        multipart.put("up-1", new ArrayList<>());
        for (int part = 1; part <= 3; part++) multipart.get("up-1").add(new byte[5 * 1024 * 1024]);   // 3 x 5 MB parts, uploaded in parallel in real life
        int size = multipart.get("up-1").stream().mapToInt(b -> b.length).sum();
        bucket.put("videos/7/raw.mp4", new Obj(new byte[size], Map.of("content-type", "video/mp4", "owner", "user-42")));
        System.out.println("multipart complete -> object size " + size / (1024 * 1024) + " MB, metadata " + bucket.get("videos/7/raw.mp4").meta());
        bucket.put("videos/7/thumb.jpg", new Obj(new byte[40_000], Map.of("content-type", "image/jpeg")));
        System.out.println("LIST prefix videos/7/ -> " + bucket.keySet().stream().filter(k -> k.startsWith("videos/7/")).toList());
        System.out.println("Keys look like paths, but the namespace is flat: there are no real folders.");
    }
}
