import java.util.*;

public class CollaborativeEditingSystem {
    // Operational Transformation for concurrent inserts/deletes on one text: the server orders ops and transforms late ones.
    record Op(String type, int pos, String text, String user, int baseVersion) {}
    static String doc = "Hello world"; static final List<Op> history = new ArrayList<>();

    static Op transform(Op op, Op applied) {                       // shift op's position by an op that was applied before it
        int pos = op.pos();
        if (applied.type().equals("ins") && (applied.pos() < pos || (applied.pos() == pos && applied.user().compareTo(op.user()) < 0))) pos += applied.text().length();
        if (applied.type().equals("del") && applied.pos() < pos) pos -= Math.min(applied.text().length(), pos - applied.pos());
        return new Op(op.type(), pos, op.text(), op.user(), op.baseVersion());
    }
    static void receive(Op op) {
        Op t = op;
        for (int v = op.baseVersion(); v < history.size(); v++) t = transform(t, history.get(v));      // ops the client hadn't seen
        if (t.type().equals("ins")) doc = doc.substring(0, t.pos()) + t.text() + doc.substring(t.pos());
        else doc = doc.substring(0, t.pos()) + doc.substring(t.pos() + t.text().length());
        history.add(t);
        System.out.printf("v%d %-5s %s %-9s at %2d (sent at %2d, base v%d) -> \"%s\"%n", history.size(), t.user(), t.type(), "'" + t.text() + "'", t.pos(), op.pos(), op.baseVersion(), doc);
    }

    public static void main(String[] args) {
        System.out.println("v0 \"" + doc + "\"");
        // Asha and Ravi both edit version 0 at the same time
        receive(new Op("ins", 5, ",", "asha", 0));                 // "Hello, world"
        receive(new Op("ins", 11, "!", "ravi", 0));                // Ravi meant the end of "Hello world" -> shifted by 1
        receive(new Op("del", 0, "Hello", "zoya", 0));             // Zoya deletes "Hello" at the start
        receive(new Op("ins", 0, "Hi", "kiran", 3));               // Kiran saw v3 and inserts at the start
        System.out.println("everyone converges to: \"" + doc + "\"");
    }
}
