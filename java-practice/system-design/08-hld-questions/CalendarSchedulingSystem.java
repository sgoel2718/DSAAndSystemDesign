import java.util.*;

public class CalendarSchedulingSystem {
    // Events stored per user (sorted by start), free/busy merge across attendees, find the earliest common slot, recurring events expanded.
    record Event(String title, int start, int end) {}                                       // minutes from 00:00
    static final Map<String, List<Event>> calendars = new TreeMap<>();

    static void add(String user, Event e) { calendars.computeIfAbsent(user, k -> new ArrayList<>()).add(e); calendars.get(user).sort(Comparator.comparingInt(Event::start)); }
    static List<int[]> busy(List<String> people) {
        List<int[]> all = new ArrayList<>(); for (String p : people) for (Event e : calendars.getOrDefault(p, List.of())) all.add(new int[]{e.start(), e.end()});
        all.sort(Comparator.comparingInt(a -> a[0])); List<int[]> merged = new ArrayList<>();
        for (int[] iv : all) if (merged.isEmpty() || merged.get(merged.size() - 1)[1] < iv[0]) merged.add(iv.clone()); else merged.get(merged.size() - 1)[1] = Math.max(merged.get(merged.size() - 1)[1], iv[1]);
        return merged;
    }
    static String t(int m) { return String.format("%02d:%02d", m / 60, m % 60); }

    public static void main(String[] args) {
        for (int day = 0; day < 1; day++) for (String u : List.of("asha", "ravi", "zoya")) add(u, new Event("standup", 9 * 60 + 30, 9 * 60 + 45));   // recurring daily event, expanded for today
        add("asha", new Event("design review", 10 * 60, 11 * 60)); add("ravi", new Event("1:1", 11 * 60, 11 * 60 + 30));
        add("zoya", new Event("interview", 12 * 60, 13 * 60)); add("ravi", new Event("lunch", 13 * 60, 14 * 60));
        List<String> people = List.of("asha", "ravi", "zoya");
        List<int[]> b = busy(people);
        System.out.println("merged busy: " + b.stream().map(iv -> t(iv[0]) + "-" + t(iv[1])).toList());
        int dayStart = 9 * 60, dayEnd = 18 * 60, need = 45, cursor = dayStart;
        for (int[] iv : b) { if (iv[0] - cursor >= need) break; cursor = Math.max(cursor, iv[1]); }
        System.out.println("earliest 45-min slot for " + people + ": " + (cursor + need <= dayEnd ? t(cursor) + "-" + t(cursor + need) : "none today"));
        int finalCursor = cursor;
        people.forEach(p -> add(p, new Event("planning", finalCursor, finalCursor + need)));
        System.out.println("invites sent; zoya's day: " + calendars.get("zoya").stream().map(e -> t(e.start()) + " " + e.title()).toList());
    }
}
