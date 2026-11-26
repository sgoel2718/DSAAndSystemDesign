import java.util.*;

public class CacheEvictionDemo {
    interface Cache { boolean access(String key); String contents(); }

    static class Lru implements Cache {
        final LinkedHashMap<String, Boolean> map; Lru(int cap) { map = new LinkedHashMap<>(16, 0.75f, true) { protected boolean removeEldestEntry(Map.Entry<String, Boolean> e) { return size() > cap; } }; }
        public boolean access(String k) { boolean hit = map.containsKey(k); map.put(k, true); return hit; }
        public String contents() { return map.keySet().toString(); }
    }

    static class Fifo implements Cache {
        final int cap; final Deque<String> q = new ArrayDeque<>(); Fifo(int cap) { this.cap = cap; }
        public boolean access(String k) { if (q.contains(k)) return true; if (q.size() == cap) q.pollFirst(); q.addLast(k); return false; }
        public String contents() { return q.toString(); }
    }

    static class Lfu implements Cache {
        final int cap; final Map<String, Integer> freq = new LinkedHashMap<>(); Lfu(int cap) { this.cap = cap; }
        public boolean access(String k) {
            if (freq.containsKey(k)) { freq.merge(k, 1, Integer::sum); return true; }
            if (freq.size() == cap) { String victim = Collections.min(freq.entrySet(), Map.Entry.comparingByValue()).getKey(); freq.remove(victim); }
            freq.put(k, 1); return false;
        }
        public String contents() { return freq.toString(); }
    }

    public static void main(String[] args) {
        String[] seq = "A B C A D B A E A B".split(" ");
        for (Cache c : List.of(new Lru(3), new Fifo(3), new Lfu(3))) {
            int hits = 0; StringBuilder trace = new StringBuilder();
            for (String k : seq) { boolean h = c.access(k); if (h) hits++; trace.append(k).append(h ? "✓ " : "· "); }
            System.out.printf("%-4s %s hits=%d final=%s%n", c.getClass().getSimpleName().toUpperCase(), trace, hits, c.contents());
        }
    }
}
