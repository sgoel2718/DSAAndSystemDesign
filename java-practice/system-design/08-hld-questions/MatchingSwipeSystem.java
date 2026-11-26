import java.util.*;

public class MatchingSwipeSystem {
    // Recommendation deck from nearby users matching preferences, exclude already swiped; a match happens when both swiped right.
    record User(String id, int age, double km, String gender, Set<String> wants) {}
    static final Map<String, User> users = new TreeMap<>();
    static final Map<String, Set<String>> rightSwipes = new HashMap<>(), seen = new HashMap<>();
    static final List<String> matches = new ArrayList<>();

    static List<String> deck(String uid, double radiusKm) {
        User me = users.get(uid);
        return users.values().stream().filter(o -> !o.id().equals(uid) && o.km() <= radiusKm && me.wants().contains(o.gender()) && o.wants().contains(me.gender())
            && !seen.getOrDefault(uid, Set.of()).contains(o.id())).sorted(Comparator.comparingDouble(User::km)).map(User::id).toList();
    }
    static void swipe(String from, String to, boolean right) {
        seen.computeIfAbsent(from, k -> new HashSet<>()).add(to);
        if (!right) return;
        rightSwipes.computeIfAbsent(from, k -> new HashSet<>()).add(to);
        if (rightSwipes.getOrDefault(to, Set.of()).contains(from)) { matches.add(from + " ❤ " + to); System.out.println("  MATCH: " + from + " and " + to + " -> open chat"); }
    }

    public static void main(String[] args) {
        users.put("asha", new User("asha", 27, 0, "F", Set.of("M"))); users.put("ravi", new User("ravi", 29, 2.1, "M", Set.of("F")));
        users.put("kiran", new User("kiran", 26, 5.5, "M", Set.of("F"))); users.put("dev", new User("dev", 31, 40, "M", Set.of("F"))); users.put("neha", new User("neha", 28, 1.0, "F", Set.of("M")));
        System.out.println("asha's deck (10 km): " + deck("asha", 10));
        swipe("ravi", "asha", true);                                     // ravi already liked asha
        swipe("asha", "ravi", true); swipe("asha", "kiran", false);
        System.out.println("asha's deck after swiping: " + deck("asha", 10) + " (seen profiles are excluded)");
        swipe("neha", "ravi", true);
        System.out.println("ravi's deck: " + deck("ravi", 10)); swipe("ravi", "neha", true);
        System.out.println("matches: " + matches);
    }
}
