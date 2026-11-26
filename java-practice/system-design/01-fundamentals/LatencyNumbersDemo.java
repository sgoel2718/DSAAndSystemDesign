import java.io.*;
import java.nio.file.*;
import java.util.*;

public class LatencyNumbersDemo {
    // Measures a few of the 'latency numbers' on this machine. Your numbers will differ; the ratios are the lesson.
    public static void main(String[] args) throws Exception {
        int n = 4_000_000;
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = i;
        long t = System.nanoTime(); long sum = 0;
        for (int i = 0; i < n; i++) sum += arr[i];                          // sequential: cache-friendly
        double seqNs = (System.nanoTime() - t) / (double) n;
        int[] idx = new int[n]; Random r = new Random(1);
        for (int i = 0; i < n; i++) idx[i] = r.nextInt(n);
        t = System.nanoTime();
        for (int i = 0; i < n; i++) sum += arr[idx[i]];                     // random: cache misses
        double rndNs = (System.nanoTime() - t) / (double) n;
        Path f = Files.createTempFile("lat", ".bin");
        byte[] mb = new byte[1 << 20];
        t = System.nanoTime();
        try (OutputStream o = new FileOutputStream(f.toFile())) { for (int i = 0; i < 16; i++) o.write(mb); }
        double writeMs = (System.nanoTime() - t) / 1e6 / 16;
        t = System.nanoTime();
        try (InputStream in = new FileInputStream(f.toFile())) { while (in.read(mb) > 0) {} }
        double readMs = (System.nanoTime() - t) / 1e6 / 16;
        Files.delete(f);
        System.out.printf("sequential array read : %.2f ns per element%n", seqNs);
        System.out.printf("random array read     : %.2f ns per element (%.0fx slower: cache misses)%n", rndNs, rndNs / seqNs);
        System.out.printf("write 1 MB to file    : %.3f ms (OS page cache)%n", writeMs);
        System.out.printf("read 1 MB from file   : %.3f ms%n", readMs);
        System.out.println("reference: same-datacenter round trip ~0.5 ms, India<->US ~200 ms");
        if (sum == 42) System.out.println();
    }
}
