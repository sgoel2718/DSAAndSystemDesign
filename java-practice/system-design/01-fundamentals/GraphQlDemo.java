import java.util.*;
import java.util.function.*;

public class GraphQlDemo {
    // A mini GraphQL-style executor: the client lists the fields it wants; resolvers fetch only those.
    record User(String id, String name, String city) {}
    record Post(String id, String authorId, String title, int likes) {}
    static final Map<String, User> users = Map.of("42", new User("42", "Asha", "Pune"), "7", new User("7", "Ravi", "Delhi"));
    static final List<Post> posts = List.of(new Post("p1", "42", "Hello", 10), new Post("p2", "42", "System design", 99), new Post("p3", "7", "Java", 5));
    static int dbCalls = 0;

    static Map<String, Object> user(String id, List<String> fields, Map<String, List<String>> nested) {
        dbCalls++; User u = users.get(id);
        Map<String, Object> out = new LinkedHashMap<>();
        for (String f : fields) switch (f) {
            case "name" -> out.put("name", u.name());
            case "city" -> out.put("city", u.city());
            case "posts" -> { dbCalls++; out.put("posts", posts.stream().filter(p -> p.authorId().equals(id)).map(p -> pick(p, nested.get("posts"))).toList()); }
        }
        return out;
    }

    static Map<String, Object> pick(Post p, List<String> fields) {
        Map<String, Object> m = new LinkedHashMap<>();
        for (String f : fields) m.put(f, f.equals("title") ? p.title() : f.equals("likes") ? p.likes() : p.id());
        return m;
    }

    public static void main(String[] args) {
        System.out.println("query { user(id:42) { name } }");
        System.out.println("  -> " + user("42", List.of("name"), Map.of()) + "   db calls: " + dbCalls);
        dbCalls = 0;
        System.out.println("query { user(id:42) { name city posts { title likes } } }");
        System.out.println("  -> " + user("42", List.of("name", "city", "posts"), Map.of("posts", List.of("title", "likes"))) + "   db calls: " + dbCalls);
        System.out.println("One request, exactly the fields asked for: no over-fetching, no second round trip.");
    }
}
