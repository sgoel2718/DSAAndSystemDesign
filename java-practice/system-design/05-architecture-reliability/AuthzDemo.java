import java.util.*;

public class AuthzDemo {
    // Authentication: who are you (token -> user). Authorization: may you do this (RBAC + ownership + ReBAC-style sharing).
    record User(String id, Set<String> roles) {}
    record Doc(String id, String owner, Set<String> sharedWith) {}
    static final Map<String, User> tokens = Map.of("tok-asha", new User("asha", Set.of("editor")), "tok-ravi", new User("ravi", Set.of("viewer")), "tok-admin", new User("root", Set.of("admin")));
    static final Map<String, Set<String>> rolePerms = Map.of("viewer", Set.of("read"), "editor", Set.of("read", "edit"), "admin", Set.of("read", "edit", "delete"));
    static final Map<String, Doc> docs = Map.of("d1", new Doc("d1", "asha", Set.of("ravi")), "d2", new Doc("d2", "zoya", Set.of()));

    static String request(String token, String action, String docId) {
        User u = tokens.get(token);
        if (u == null) return "401 Unauthorized (who are you?)";
        Doc d = docs.get(docId);
        boolean roleAllows = u.roles().stream().anyMatch(r -> rolePerms.get(r).contains(action));
        boolean relation = u.roles().contains("admin") || d.owner().equals(u.id()) || d.sharedWith().contains(u.id());
        if (!roleAllows || !relation) return "403 Forbidden (" + u.id() + " may not " + action + " " + docId + ")";
        return "200 OK " + u.id() + " " + action + " " + docId;
    }

    public static void main(String[] args) {
        System.out.println(request("bad-token", "read", "d1"));
        System.out.println(request("tok-ravi", "read", "d1") + "  <- shared with him");
        System.out.println(request("tok-ravi", "edit", "d1") + "  <- viewer role");
        System.out.println(request("tok-asha", "edit", "d1"));
        System.out.println(request("tok-asha", "read", "d2") + "  <- not hers (broken access control prevented)");
        System.out.println(request("tok-admin", "delete", "d2"));
    }
}
