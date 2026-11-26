import java.util.*;

public class LsmTreeDemo {
    // A mini LSM tree: writes go to a WAL + sorted memtable; when full it flushes to an immutable SSTable;
    // reads check memtable, then SSTables newest-first (each with a tiny Bloom filter); compaction merges SSTables.
    static class SSTable {
        final TreeMap<String, String> data; final BitSet bloom = new BitSet(64);
        SSTable(TreeMap<String, String> d) { data = d; d.keySet().forEach(k -> { bloom.set(h1(k)); bloom.set(h2(k)); }); }
        boolean mightContain(String k) { return bloom.get(h1(k)) && bloom.get(h2(k)); }
        static int h1(String k) { return Math.floorMod(k.hashCode(), 64); }
        static int h2(String k) { return Math.floorMod(k.hashCode() * 31 + 7, 64); }
    }
    final List<String> wal = new ArrayList<>(); TreeMap<String, String> memtable = new TreeMap<>(); final LinkedList<SSTable> sstables = new LinkedList<>();
    int diskReads = 0;

    void put(String k, String v) {
        wal.add(k + "=" + v); memtable.put(k, v);
        if (memtable.size() >= 3) { sstables.addFirst(new SSTable(memtable)); System.out.println("  flush memtable -> SSTable " + memtable); memtable = new TreeMap<>(); wal.clear(); }
    }
    String get(String k) {
        if (memtable.containsKey(k)) return memtable.get(k);
        for (SSTable s : sstables) { if (!s.mightContain(k)) continue; diskReads++; if (s.data.containsKey(k)) return s.data.get(k); }
        return null;
    }
    void compact() {
        TreeMap<String, String> merged = new TreeMap<>();
        for (Iterator<SSTable> it = sstables.descendingIterator(); it.hasNext(); ) merged.putAll(it.next().data);   // newer overwrite older
        merged.values().removeIf(v -> v.equals("<tombstone>"));
        sstables.clear(); sstables.add(new SSTable(merged));
        System.out.println("  compaction -> 1 SSTable " + merged);
    }

    public static void main(String[] args) {
        LsmTreeDemo db = new LsmTreeDemo();
        String[][] writes = {{"apple", "1"}, {"kiwi", "2"}, {"mango", "3"}, {"apple", "10"}, {"banana", "4"}, {"kiwi", "<tombstone>"}, {"plum", "5"}};
        for (String[] w : writes) { System.out.println("put " + w[0] + "=" + w[1]); db.put(w[0], w[1]); }
        System.out.println("SSTables on disk: " + db.sstables.size() + ", memtable " + db.memtable);
        System.out.println("get apple -> " + db.get("apple") + " (newest version wins)");
        db.diskReads = 0; System.out.println("get grape -> " + db.get("grape") + ", disk reads " + db.diskReads + " (Bloom filters skipped files)");
        db.compact();
        System.out.println("get kiwi  -> " + db.get("kiwi") + " (deleted by tombstone)");
    }
}
