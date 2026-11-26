import java.security.MessageDigest;
import java.util.*;

public class ObjectStorageSystem {
    // Metadata service (bucket/key -> object version, placement) + data nodes; erasure-coding-lite with XOR parity; recovery from a lost node.
    static final Map<String, byte[][]> dataNodes = new TreeMap<>();                // node -> stored fragment (one per object here)
    record ObjectMeta(String bucket, String key, int size, String etag, List<String> placement) {}
    static final Map<String, ObjectMeta> metadata = new TreeMap<>();

    static String md5(byte[] b) throws Exception { return HexFormat.of().formatHex(MessageDigest.getInstance("MD5").digest(b)).substring(0, 12); }

    static void put(String bucket, String key, byte[] data) throws Exception {
        int half = (data.length + 1) / 2;
        byte[] a = Arrays.copyOfRange(data, 0, half), b = Arrays.copyOf(Arrays.copyOfRange(data, half, data.length), half), parity = new byte[half];
        for (int i = 0; i < half; i++) parity[i] = (byte) (a[i] ^ b[i]);          // 2 data + 1 parity: survives losing any one node (1.5x storage, not 3x)
        List<String> nodes = List.of("node-1", "node-2", "node-3");
        dataNodes.put("node-1", new byte[][]{a}); dataNodes.put("node-2", new byte[][]{b}); dataNodes.put("node-3", new byte[][]{parity});
        metadata.put(bucket + "/" + key, new ObjectMeta(bucket, key, data.length, md5(data), nodes));
    }
    static byte[] get(String bucket, String key) {
        ObjectMeta m = metadata.get(bucket + "/" + key);
        byte[][] a = dataNodes.get("node-1"), b = dataNodes.get("node-2"), p = dataNodes.get("node-3");
        byte[] x = a != null ? a[0] : null, y = b != null ? b[0] : null;
        if (x == null) { x = new byte[y.length]; for (int i = 0; i < y.length; i++) x[i] = (byte) (y[i] ^ p[0][i]); System.out.println("  node-1 lost -> rebuilt its fragment from node-2 XOR parity"); }
        if (y == null) { y = new byte[x.length]; for (int i = 0; i < x.length; i++) y[i] = (byte) (x[i] ^ p[0][i]); }
        byte[] out = new byte[m.size()]; System.arraycopy(x, 0, out, 0, x.length); System.arraycopy(y, 0, out, x.length, m.size() - x.length);
        return out;
    }

    public static void main(String[] args) throws Exception {
        byte[] photo = "PRETEND-JPEG-BYTES-OF-A-CAT-PHOTO".getBytes();
        put("photos", "2026/11/cat.jpg", photo);
        System.out.println("PUT photos/2026/11/cat.jpg -> " + metadata.get("photos/2026/11/cat.jpg"));
        System.out.println("GET -> " + new String(get("photos", "2026/11/cat.jpg")));
        dataNodes.remove("node-1");
        byte[] back = get("photos", "2026/11/cat.jpg");
        System.out.println("GET after losing node-1 -> " + new String(back) + " | etag matches: " + md5(back).equals(metadata.get("photos/2026/11/cat.jpg").etag()));
        System.out.println("storage overhead: 3 fragments of " + (photo.length + 1) / 2 + " bytes = 1.5x (3-way replication would be 3x)");
    }
}
