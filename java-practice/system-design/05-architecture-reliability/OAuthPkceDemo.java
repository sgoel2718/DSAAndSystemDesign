import java.security.*;
import java.util.*;

public class OAuthPkceDemo {
    // Authorization Code flow with PKCE between an app, an auth server and an API, all simulated in memory.
    static final Base64.Encoder B64 = Base64.getUrlEncoder().withoutPadding();
    static String sha256(String s) throws Exception { return B64.encodeToString(MessageDigest.getInstance("SHA-256").digest(s.getBytes())); }

    static class AuthServer {
        final Map<String, String[]> codes = new HashMap<>(); final Map<String, String> accessTokens = new HashMap<>(); int n = 0;
        String authorize(String user, String clientId, String scope, String challenge) { String code = "code-" + (++n); codes.put(code, new String[]{user, clientId, scope, challenge}); return code; }
        String token(String code, String clientId, String verifier) throws Exception {
            String[] c = codes.remove(code);                                   // one-time use
            if (c == null) return "error: invalid or reused code";
            if (!c[1].equals(clientId) || !sha256(verifier).equals(c[3])) return "error: PKCE verification failed";
            String at = "at-" + UUID.nameUUIDFromBytes((code + verifier).getBytes()).toString().substring(0, 8);
            accessTokens.put(at, c[0] + "|" + c[2]); return at;
        }
    }

    public static void main(String[] args) throws Exception {
        AuthServer google = new AuthServer();
        String verifier = "random-secret-the-app-keeps-" + 12345;                // generated per login, never leaves the app until step 3
        String challenge = sha256(verifier);
        System.out.println("1. app redirects user to auth server with code_challenge=" + challenge.substring(0, 12) + "...");
        String code = google.authorize("asha@gmail.com", "photo-app", "email profile", challenge);
        System.out.println("2. user logs in + consents; redirected back with " + code);
        System.out.println("   attacker who stole the code tries: " + google.token(code + "", "photo-app", "guess") );
        code = google.authorize("asha@gmail.com", "photo-app", "email profile", challenge);
        String token = google.token(code, "photo-app", verifier);
        System.out.println("3. app exchanges " + code + " + verifier -> access token " + token);
        System.out.println("   reusing the same code -> " + google.token(code, "photo-app", verifier));
        String[] grant = google.accessTokens.get(token).split("\\|");
        System.out.println("4. API call with token -> user " + grant[0] + ", allowed scopes [" + grant[1] + "]; password never shared with the app");
    }
}
