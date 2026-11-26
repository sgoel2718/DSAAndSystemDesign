import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class JwtDemo {
    static final byte[] SECRET = "server-side-secret-key-32-bytes!".getBytes(StandardCharsets.UTF_8);
    static final Base64.Encoder B64 = Base64.getUrlEncoder().withoutPadding();

    static String hmac(String data) throws Exception { Mac m = Mac.getInstance("HmacSHA256"); m.init(new SecretKeySpec(SECRET, "HmacSHA256")); return B64.encodeToString(m.doFinal(data.getBytes(StandardCharsets.UTF_8))); }

    static String issue(String sub, long exp) throws Exception {
        String header = B64.encodeToString("{\"alg\":\"HS256\",\"typ\":\"JWT\"}".getBytes());
        String payload = B64.encodeToString(("{\"sub\":\"" + sub + "\",\"exp\":" + exp + "}").getBytes());
        return header + "." + payload + "." + hmac(header + "." + payload);
    }

    static final Set<String> revoked = new HashSet<>();
    static String verify(String jwt, long now) throws Exception {
        String[] p = jwt.split("\\.");
        if (!hmac(p[0] + "." + p[1]).equals(p[2])) return "REJECT: bad signature (tampered)";
        String json = new String(Base64.getUrlDecoder().decode(p[1]));
        long exp = Long.parseLong(json.replaceAll(".*\"exp\":(\\d+).*", "$1"));
        if (now >= exp) return "REJECT: expired";
        if (revoked.contains(p[2])) return "REJECT: on deny-list";
        return "OK " + json + " (no database lookup needed)";
    }

    public static void main(String[] args) throws Exception {
        String jwt = issue("user-42", 1000);
        System.out.println("token: " + jwt.substring(0, 40) + "...");
        System.out.println("verify at t=500   : " + verify(jwt, 500));
        String[] p = jwt.split("\\.");
        String forgedPayload = B64.encodeToString("{\"sub\":\"admin\",\"exp\":1000}".getBytes());
        System.out.println("forged sub=admin  : " + verify(p[0] + "." + forgedPayload + "." + p[2], 500));
        System.out.println("verify at t=1000  : " + verify(jwt, 1000));
        revoked.add(p[2]);
        System.out.println("after logout      : " + verify(jwt, 600) + "  (revocation needs a server-side list)");
        Map<String, String> sessions = new HashMap<>(Map.of("sid-abc", "user-42"));
        System.out.println("server session    : lookup sid-abc -> " + sessions.get("sid-abc") + "; logout = delete -> " + (sessions.remove("sid-abc") != null ? "revoked instantly" : ""));
    }
}
