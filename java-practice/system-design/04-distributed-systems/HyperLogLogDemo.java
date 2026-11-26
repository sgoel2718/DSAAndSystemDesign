import java.util.*;

public class HyperLogLogDemo {
    final int p = 14, m = 1 << p; final byte[] reg = new byte[m];

    static long hash64(long x) { x ^= x >>> 33; x *= 0xff51afd7ed558ccdL; x ^= x >>> 33; x *= 0xc4ceb9fe1a85ec53L; x ^= x >>> 33; return x; }

    void add(String item) {
        long h = hash64(item.hashCode() * 0x9E3779B97F4A7C15L + item.length());
        int idx = (int) (h >>> (64 - p));                                   // first 14 bits pick a register
        long rest = h << p;
        byte rank = (byte) (Long.numberOfLeadingZeros(rest) + 1);           // position of first 1-bit
        if (rank > reg[idx]) reg[idx] = rank;
    }
    double estimate() {
        double sum = 0; int zeros = 0;
        for (byte r : reg) { sum += Math.pow(2, -r); if (r == 0) zeros++; }
        double alpha = 0.7213 / (1 + 1.079 / m), e = alpha * m * m / sum;
        return (e < 2.5 * m && zeros > 0) ? m * Math.log((double) m / zeros) : e;   // small-range correction
    }

    public static void main(String[] args) {
        HyperLogLogDemo hll = new HyperLogLogDemo(); Set<String> exact = new HashSet<>(); Random r = new Random(2);
        for (int checkpoint : new int[]{1_000, 100_000, 1_000_000}) {
            while (exact.size() < checkpoint) { String u = "user" + r.nextInt(5_000_000); exact.add(u); hll.add(u); hll.add(u); }   // duplicates don't matter
            System.out.printf("true distinct %,9d   HLL estimate %,9.0f   error %+.2f%%%n", exact.size(), hll.estimate(), (hll.estimate() - exact.size()) / exact.size() * 100);
        }
        System.out.printf("HLL memory: %,d bytes; exact HashSet: tens of MB%n", hll.m);
    }
}
