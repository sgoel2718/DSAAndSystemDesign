import java.util.*;

public class VideoConferencingSystem {
    // SFU (selective forwarding unit): each participant uploads one stream with simulcast layers; the SFU forwards a layer
    // per receiver based on their bandwidth and layout. Compare upload/download cost with mesh (peer-to-peer).
    record Layer(String name, int kbps) {}
    static final List<Layer> simulcast = List.of(new Layer("180p", 150), new Layer("360p", 500), new Layer("720p", 1500));

    public static void main(String[] args) {
        int n = 6;
        System.out.printf("%d participants, 720p = 1500 kbps%n", n);
        System.out.printf("mesh: each uploads %d copies = %,d kbps up, downloads %,d kbps -> phones melt beyond ~4 people%n", n - 1, (n - 1) * 1500, (n - 1) * 1500);
        int up = simulcast.stream().mapToInt(Layer::kbps).sum();
        System.out.printf("SFU : each uploads 3 simulcast layers once = %,d kbps up; the server picks what to forward%n", up);
        Map<String, Integer> downlink = new LinkedHashMap<>(); downlink.put("asha (fibre)", 20_000); downlink.put("ravi (4G)", 2_500); downlink.put("zoya (weak wifi)", 900);
        String speaker = "kiran";
        for (var e : downlink.entrySet()) {
            int budget = e.getValue(); List<String> plan = new ArrayList<>(); int used = 0;
            Layer sp = simulcast.stream().filter(l -> l.kbps() <= budget * 0.6).reduce((a, b) -> b).orElse(simulcast.get(0));
            plan.add(speaker + "@" + sp.name()); used += sp.kbps();
            for (int i = 0; i < n - 2; i++) { Layer th = used + 150 <= budget ? simulcast.get(0) : null; if (th == null) { plan.add("(+" + (n - 2 - i) + " paused)"); break; } plan.add("tile" + (i + 1) + "@180p"); used += 150; }
            System.out.printf("  %-17s %,6d kbps -> %s = %,d kbps%n", e.getKey(), budget, plan, used);
        }
        System.out.println("audio: mixed or forwarded separately (Opus ~32 kbps), prioritised over video when bandwidth drops");
    }
}
