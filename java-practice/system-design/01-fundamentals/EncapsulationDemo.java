public class EncapsulationDemo {
    // Shows how each layer wraps the one above it, then unwraps on the receiver.
    static String http(String path) { return "GET " + path + " HTTP/1.1|Host: shop.com"; }
    static String tcp(String payload, int srcPort, int dstPort) { return "[TCP src=" + srcPort + " dst=" + dstPort + " seq=1]" + payload; }
    static String ip(String segment, String src, String dst) { return "[IP " + src + "->" + dst + " ttl=64]" + segment; }
    static String ethernet(String packet, String srcMac, String dstMac) { return "[ETH " + srcMac + "->" + dstMac + "]" + packet + "[CRC]"; }

    static String strip(String frame, String layer) {
        int end = frame.indexOf(']') + 1;
        String rest = frame.substring(end);
        if (layer.equals("ETH")) rest = rest.substring(0, rest.length() - "[CRC]".length());
        return rest;
    }

    public static void main(String[] args) {
        String app = http("/cart");
        String seg = tcp(app, 51544, 443);
        String pkt = ip(seg, "10.0.0.7", "142.250.1.1");
        String frame = ethernet(pkt, "aa:bb", "cc:dd");
        System.out.println("L7 application: " + app);
        System.out.println("L4 transport  : " + seg);
        System.out.println("L3 network    : " + pkt);
        System.out.println("L2 link       : " + frame);
        String up = strip(strip(strip(frame, "ETH"), "IP"), "TCP");
        System.out.println("\nreceiver unwraps -> " + up);
        System.out.println("an L4 load balancer reads only up to [TCP ...]; an L7 one reads 'GET /cart' and can route by path");
    }
}
