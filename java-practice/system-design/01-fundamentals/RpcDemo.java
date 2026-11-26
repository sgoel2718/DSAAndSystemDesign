import java.io.*;
import java.lang.reflect.*;
import java.util.*;

public class RpcDemo {
    // A tiny RPC framework: the client calls an interface; a proxy serialises the call into bytes ("the wire"),
    // the server decodes it and invokes the real implementation. gRPC does the same with protobuf + HTTP/2.
    interface OrderService { String getOrder(String id); int total(int[] prices); }

    static class OrderServiceImpl implements OrderService {
        public String getOrder(String id) { return "Order{id=" + id + ", status=PAID}"; }
        public int total(int[] prices) { return Arrays.stream(prices).sum(); }
    }

    record Call(String method, Object[] args) implements Serializable {}

    static byte[] serverHandle(byte[] request, Object impl) throws Exception {
        Call call = (Call) new ObjectInputStream(new ByteArrayInputStream(request)).readObject();
        Method m = Arrays.stream(impl.getClass().getMethods()).filter(x -> x.getName().equals(call.method())).findFirst().orElseThrow();
        Object result = m.invoke(impl, call.args());
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        new ObjectOutputStream(bos).writeObject(result);
        return bos.toByteArray();
    }

    @SuppressWarnings("unchecked")
    static <T> T stub(Class<T> api, Object remoteImpl) {
        return (T) Proxy.newProxyInstance(api.getClassLoader(), new Class<?>[]{api}, (proxy, method, args) -> {
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            new ObjectOutputStream(bos).writeObject(new Call(method.getName(), args));
            byte[] wire = bos.toByteArray();
            System.out.println("  [wire] " + method.getName() + " request " + wire.length + " bytes");
            byte[] reply = serverHandle(wire, remoteImpl);               // in real life: an HTTP/2 network call
            return new ObjectInputStream(new ByteArrayInputStream(reply)).readObject();
        });
    }

    public static void main(String[] args) {
        OrderService client = stub(OrderService.class, new OrderServiceImpl());
        System.out.println("getOrder -> " + client.getOrder("987"));
        System.out.println("total    -> " + client.total(new int[]{2499, 199, 199}));
        System.out.println("The caller wrote client.getOrder(...) like a local call; the stub hid the network.");
    }
}
