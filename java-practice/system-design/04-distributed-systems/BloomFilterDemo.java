import java.util.*;

public class BloomFilterDemo {
    final BitSet bits; final int m, k;
    BloomFilterDemo(int expected, double fpRate) {
        m = (int) Math.ceil(-expected * Math.log(fpRate) / (Math.log(2) * Math.log(2)));
        k = Math.max(1, (int) Math.round((double) m / expected * Math.log(2)));
        bits = new BitSet(m);
    }
    int[] positions(String s) {                                         // double hashing: h1 + i*h2
        int h1 = s.hashCode(), h2 = Integer.reverse(h1) * 0x9E3779B9 | 1; int[] p = new int[k];
        for (int i = 0; i < k; i++) p[i] = Math.floorMod(h1 + i * h2, m);
        return p;
    }
    void add(String s) { for (int p : positions(s)) bits.set(p); }
    boolean mightContain(String s) { for (int p : positions(s)) if (!bits.get(p)) return false; return true; }

    public static void main(String[] args) {
        BloomFilterDemo seen = new BloomFilterDemo(100_000, 0.01);
        for (int i = 0; i < 100_000; i++) seen.add("https://site.com/page/" + i);
        System.out.printf("m=%,d bits (%.0f KB), k=%d hash functions for 100,000 URLs%n", seen.m, seen.m / 8.0 / 1024, seen.k);
        int fn = 0; for (int i = 0; i < 100_000; i++) if (!seen.mightContain("https://site.com/page/" + i)) fn++;
        int fp = 0; for (int i = 0; i < 100_000; i++) if (seen.mightContain("https://other.org/x/" + i)) fp++;
        System.out.println("false negatives: " + fn + " (never)");
        System.out.printf("false positives: %d of 100,000 unseen URLs = %.2f%% (target 1%%)%n", fp, fp / 1000.0);
        long setBytes = 100_000L * ("https://site.com/page/99999".length() * 2 + 40);
        System.out.printf("a HashSet<String> of the same URLs would need roughly %.1f MB%n", setBytes / 1e6);
    }
}
