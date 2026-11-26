import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;

public class TcpUdpDemo {
    public static void main(String[] args) throws Exception {
        // TCP: connection, ordered reliable byte stream
        try (ServerSocket server = new ServerSocket(0, 50, InetAddress.getLoopbackAddress())) {
            Thread t = new Thread(() -> {
                try (Socket s = server.accept();
                     BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream()));
                     PrintWriter out = new PrintWriter(s.getOutputStream(), true)) {
                    String line;
                    while ((line = in.readLine()) != null) out.println("echo:" + line);
                } catch (IOException ignored) {}
            });
            t.start();
            try (Socket c = new Socket(InetAddress.getLoopbackAddress(), server.getLocalPort());
                 PrintWriter out = new PrintWriter(c.getOutputStream(), true);
                 BufferedReader in = new BufferedReader(new InputStreamReader(c.getInputStream()))) {
                for (String m : new String[]{"one", "two", "three"}) { out.println(m); System.out.println("TCP  sent " + m + " <- " + in.readLine()); }
            }
            t.join();
        }
        // UDP: no connection, each datagram stands alone; may be lost or reordered on real networks
        try (DatagramSocket server = new DatagramSocket(0, InetAddress.getLoopbackAddress());
             DatagramSocket client = new DatagramSocket()) {
            for (String m : new String[]{"frame-1", "frame-2", "frame-3"}) {
                byte[] b = m.getBytes(StandardCharsets.UTF_8);
                client.send(new DatagramPacket(b, b.length, InetAddress.getLoopbackAddress(), server.getLocalPort()));
            }
            server.setSoTimeout(500);
            byte[] buf = new byte[100];
            for (int i = 0; i < 3; i++) {
                DatagramPacket p = new DatagramPacket(buf, buf.length);
                server.receive(p);
                System.out.println("UDP  got  " + new String(p.getData(), 0, p.getLength(), StandardCharsets.UTF_8) + " (no handshake, no ack)");
            }
        }
    }
}
