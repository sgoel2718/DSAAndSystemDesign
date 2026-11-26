import java.util.*;
import java.util.regex.*;

public class TwitterSystem {
    // Tweet write path: id, store, fan-out to home timelines (capped), hashtag index, trending counts in a time window.
    record Tweet(long id, String user, String text, long minute) {}
    static final Map<Long, Tweet> tweets = new HashMap<>();
    static final Map<String, Set<String>> followers = new HashMap<>();
    static final Map<String, Deque<Long>> homeTimeline = new HashMap<>();
    static final Map<String, List<Long>> hashtagIndex = new TreeMap<>();
    static final Map<Long, Map<String, Integer>> tagCountsPerMinute = new TreeMap<>();
    static long seq = 0; static final int TIMELINE_CAP = 3;

    static void tweet(String user, String text, long minute) {
        Tweet t = new Tweet(++seq, user, text, minute); tweets.put(t.id(), t);
        for (String f : followers.getOrDefault(user, Set.of())) {
            Deque<Long> tl = homeTimeline.computeIfAbsent(f, k -> new ArrayDeque<>()); tl.addFirst(t.id()); if (tl.size() > TIMELINE_CAP) tl.removeLast();
        }
        Matcher m = Pattern.compile("#(\\w+)").matcher(text);
        while (m.find()) { String tag = m.group(1).toLowerCase(); hashtagIndex.computeIfAbsent(tag, k -> new ArrayList<>()).add(t.id()); tagCountsPerMinute.computeIfAbsent(minute, k -> new HashMap<>()).merge(tag, 1, Integer::sum); }
    }
    static List<String> trending(long now, int windowMin) {
        Map<String, Integer> sum = new HashMap<>();
        tagCountsPerMinute.forEach((min, c) -> { if (min > now - windowMin) c.forEach((k, v) -> sum.merge(k, v, Integer::sum)); });
        return sum.entrySet().stream().sorted(Map.Entry.<String, Integer>comparingByValue().reversed().thenComparing(Map.Entry.comparingByKey())).limit(3).map(e -> "#" + e.getKey() + "=" + e.getValue()).toList();
    }

    public static void main(String[] args) {
        followers.put("ravi", Set.of("asha")); followers.put("zoya", Set.of("asha", "kiran"));
        tweet("ravi", "Watching #INDvAUS tonight", 1); tweet("zoya", "#INDvAUS what a catch!", 2); tweet("zoya", "Learning #SystemDesign", 3);
        tweet("kiran", "#INDvAUS #INDvAUS crazy finish", 9); tweet("ravi", "New blog on #SystemDesign and #Kafka", 9); tweet("zoya", "Lunch", 10);
        System.out.println("asha's home timeline (capped at " + TIMELINE_CAP + "): " + homeTimeline.get("asha").stream().map(id -> tweets.get(id).user() + ": " + tweets.get(id).text()).toList());
        System.out.println("search #systemdesign -> tweet ids " + hashtagIndex.get("systemdesign"));
        System.out.println("trending last 10 min at minute 10: " + trending(10, 10));
        System.out.println("trending last 3 min at minute 10 : " + trending(10, 3));
    }
}
