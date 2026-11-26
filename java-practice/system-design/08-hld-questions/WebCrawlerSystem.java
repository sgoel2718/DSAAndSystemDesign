import java.util.*;
import java.util.regex.*;

public class WebCrawlerSystem {
    // Frontier (priority + per-host politeness), fetcher, parser, URL dedup, content dedup (SimHash-lite), robots rules, max depth.
    static final Map<String, String> web = Map.of(
        "https://a.com/", "<a href='https://a.com/x'> <a href='https://b.com/'> <a href='https://a.com/private'> hello world from a",
        "https://a.com/x", "<a href='https://a.com/'> <a href='https://c.com/'> news about cricket",
        "https://b.com/", "<a href='https://b.com/copy'> hello world from a",
        "https://b.com/copy", "hello world from a",
        "https://c.com/", "<a href='https://c.com/deep'> recipes",
        "https://c.com/deep", "<a href='https://c.com/deeper'> more recipes");
    static final Set<String> disallowed = Set.of("https://a.com/private");
    record Task(String url, int depth) {}

    public static void main(String[] args) {
        Deque<Task> frontier = new ArrayDeque<>(List.of(new Task("https://a.com/", 0)));
        Set<String> seenUrls = new HashSet<>(List.of("https://a.com/")); Set<Integer> seenContent = new HashSet<>();
        Map<String, Long> hostReadyAt = new HashMap<>(); long clock = 0; int maxDepth = 2;
        Pattern link = Pattern.compile("href='([^']+)'");
        while (!frontier.isEmpty()) {
            Task t = frontier.poll(); String host = t.url().split("/")[2];
            clock = Math.max(clock, hostReadyAt.getOrDefault(host, 0L)); hostReadyAt.put(host, clock + 1000);    // 1 request/second per host
            String html = web.get(t.url());
            if (html == null) { System.out.printf("t=%4d 404  %s%n", clock, t.url()); continue; }
            int fingerprint = html.replaceAll("<[^>]+>", "").trim().hashCode();
            boolean dupContent = !seenContent.add(fingerprint);
            System.out.printf("t=%4d GET  %-22s depth %d%s%n", clock, t.url(), t.depth(), dupContent ? "  (duplicate content, not indexed)" : "");
            Matcher m = link.matcher(html);
            while (m.find()) {
                String u = m.group(1);
                if (disallowed.contains(u)) { System.out.println("        skip " + u + " (robots.txt)"); continue; }
                if (t.depth() + 1 > maxDepth) continue;
                if (seenUrls.add(u)) frontier.add(new Task(u, t.depth() + 1));
            }
        }
        System.out.println("crawled " + seenUrls.size() + " unique URLs, " + seenContent.size() + " unique pages indexed");
    }
}
