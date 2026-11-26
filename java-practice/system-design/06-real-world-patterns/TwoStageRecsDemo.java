import java.util.*;

public class TwoStageRecsDemo {
    // Stage 1: cheap candidate generation (embedding similarity). Stage 2: richer ranking. Stage 3: diversity re-rank.
    record Item(String id, String category, double[] emb, double ctr, int ageDays) {}

    static double cos(double[] a, double[] b) { double d = 0, na = 0, nb = 0; for (int i = 0; i < a.length; i++) { d += a[i] * b[i]; na += a[i] * a[i]; nb += b[i] * b[i]; } return d / Math.sqrt(na * nb); }

    public static void main(String[] args) {
        Random r = new Random(3); List<Item> catalog = new ArrayList<>(); String[] cats = {"cricket", "cooking", "tech", "music"};
        for (int i = 0; i < 2000; i++) { String c = cats[i % 4]; double[] e = new double[8]; for (int k = 0; k < 8; k++) e[k] = r.nextGaussian() * 0.3 + (k == i % 4 ? 1.5 : 0) + (k == 4 + (i % 2) ? 0.5 : 0); catalog.add(new Item("v" + i, c, e, 0.01 + r.nextDouble() * 0.1, r.nextInt(60))); }
        double[] user = {1.2, 0.1, 0.9, 0.0, 0.3, 0.2, 0, 0};                    // likes cricket and tech
        List<Item> candidates = catalog.stream().sorted(Comparator.comparingDouble((Item it) -> -cos(user, it.emb()))).limit(50).toList();
        System.out.println("stage 1: 2,000 items -> 50 candidates by embedding similarity (an ANN index at scale)");
        List<Item> ranked = new ArrayList<>(candidates);
        ranked.sort(Comparator.comparingDouble((Item it) -> -(0.6 * cos(user, it.emb()) + 3 * it.ctr() + 0.2 / (1 + it.ageDays()))));
        System.out.println("stage 2: ranked by similarity + predicted CTR + freshness");
        List<Item> page = new ArrayList<>(); Map<String, Integer> perCat = new HashMap<>();
        for (Item it : ranked) { if (perCat.merge(it.category(), 1, Integer::sum) <= 3) page.add(it); if (page.size() == 5) break; }
        System.out.println("stage 3: max 3 per category ->");
        for (Item it : page) System.out.printf("  %-6s %-8s sim %.2f ctr %.3f age %2dd%n", it.id(), it.category(), cos(user, it.emb()), it.ctr(), it.ageDays());
    }
}
