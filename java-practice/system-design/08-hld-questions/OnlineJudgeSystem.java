import javax.tools.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public class OnlineJudgeSystem {
    // Submission -> queue -> sandboxed worker compiles & runs against test cases with a time limit -> verdict.
    // Here the 'sandbox' is a separate JVM process with a timeout; production adds containers, seccomp, memory/CPU limits.
    static String judge(String code, List<String[]> tests) throws Exception {
        Path dir = Files.createTempDirectory("judge"); Path src = dir.resolve("Solution.java"); Files.writeString(src, code);
        JavaCompiler javac = ToolProvider.getSystemJavaCompiler();
        ByteArrayOutputStream err = new ByteArrayOutputStream();
        if (javac.run(null, null, err, src.toString()) != 0) return "Compilation Error";
        int passed = 0;
        for (String[] t : tests) {
            ProcessBuilder pb = new ProcessBuilder("java", "-Xmx64m", "-cp", dir.toString(), "Solution");
            pb.environment().remove("JAVA_TOOL_OPTIONS"); pb.redirectError(ProcessBuilder.Redirect.DISCARD);
            Process p = pb.start();
            try (Writer w = new OutputStreamWriter(p.getOutputStream())) { w.write(t[0]); }
            if (!p.waitFor(2, TimeUnit.SECONDS)) { p.destroyForcibly(); return "Time Limit Exceeded on test " + (passed + 1); }
            String out = new String(p.getInputStream().readAllBytes()).trim();
            if (p.exitValue() != 0) return "Runtime Error on test " + (passed + 1);
            if (!out.equals(t[1])) return "Wrong Answer on test " + (passed + 1) + " (expected " + t[1] + ", got " + out + ")";
            passed++;
        }
        return "Accepted (" + passed + "/" + tests.size() + ")";
    }

    public static void main(String[] args) throws Exception {
        List<String[]> twoSumTests = List.of(new String[]{"2 7 11 15\n9", "0 1"}, new String[]{"3 2 4\n6", "1 2"}, new String[]{"3 3\n6", "0 1"});
        String good = "import java.util.*; public class Solution { public static void main(String[] a) { Scanner s = new Scanner(System.in); String[] p = s.nextLine().trim().split(\" \"); int t = Integer.parseInt(s.nextLine().trim()); Map<Integer,Integer> m = new HashMap<>(); for (int i = 0; i < p.length; i++) { int x = Integer.parseInt(p[i]); if (m.containsKey(t - x)) { System.out.println(m.get(t - x) + \" \" + i); return; } m.put(x, i); } } }";
        String wrong = good.replace("m.get(t - x) + \" \" + i", "i + \" \" + m.get(t - x)");
        String slow = "public class Solution { public static void main(String[] a) { while (true) {} } }";
        String broken = "public class Solution { void x( }";
        Map<String, String> subs = new LinkedHashMap<>(); subs.put("asha (hash map)", good); subs.put("ravi (swapped output)", wrong); subs.put("zoya (infinite loop)", slow); subs.put("kiran (syntax error)", broken);
        ExecutorService workers = Executors.newFixedThreadPool(2); Map<String, Future<String>> verdicts = new LinkedHashMap<>();
        for (var e : subs.entrySet()) verdicts.put(e.getKey(), workers.submit(() -> judge(e.getValue(), twoSumTests)));
        for (var e : verdicts.entrySet()) System.out.printf("%-22s -> %s%n", e.getKey(), e.getValue().get());
        workers.shutdown();
    }
}
