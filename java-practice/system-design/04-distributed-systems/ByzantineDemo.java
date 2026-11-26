import java.util.*;

public class ByzantineDemo {
    // Majority voting over reported values: works while honest nodes outnumber liars enough.
    static String decide(List<String> reports, int f) {
        Map<String, Integer> votes = new HashMap<>();
        for (String r : reports) votes.merge(r, 1, Integer::sum);
        for (var e : votes.entrySet()) if (e.getValue() >= 2 * f + 1) return e.getKey();      // need 2f+1 matching votes out of 3f+1
        return "NO DECISION";
    }

    public static void main(String[] args) {
        int f = 1;
        List<String> fourNodes = List.of("commit", "commit", "commit", "abort");                 // 3f+1 = 4, one liar
        System.out.println("4 nodes, 1 liar  -> " + decide(fourNodes, f));
        List<String> threeNodes = List.of("commit", "commit", "abort");
        System.out.println("3 nodes, 1 liar  -> " + decide(threeNodes, f) + " (3 < 3f+1, can't tolerate a Byzantine node)");
        List<String> equivocating = List.of("commit", "abort", "commit", "abort");               // liar tells different nodes different things
        System.out.println("liar equivocates -> " + decide(equivocating, f));
        for (int faults = 1; faults <= 3; faults++)
            System.out.printf("tolerate %d faulty: crash faults need %d nodes, Byzantine faults need %d%n", faults, 2 * faults + 1, 3 * faults + 1);
    }
}
