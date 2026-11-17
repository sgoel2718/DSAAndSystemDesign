import com.sun.jdi.*;
import com.sun.jdi.connect.*;
import com.sun.jdi.event.*;
import com.sun.jdi.request.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/**
 * Records a line-by-line trace of one approach running on one input, using the Java Debug Interface.
 * Usage: java Tracer <classpath> <mainClass> <approachClass> <maxSteps> <out.json>
 * Output JSON: {"steps":[{"l":line,"m":method,"d":depth,"v":{name:value}}...],"truncated":bool}
 * Values: numbers/booleans/strings as JSON; arrays as {"a":[...]}; ListNode as {"n":id,"c":[[id,val],...]};
 * other objects as {"o":"text"} from the harness's fmt(Object).
 */
public class Tracer {
    static VirtualMachine vm;
    static ClassType mainType;
    static Method fmt;
    static String approach;

    public static void main(String[] args) throws Exception {
        String cp = args[0], mainClass = args[1];
        approach = args[2];
        int maxSteps = Integer.parseInt(args[3]);
        LaunchingConnector lc = Bootstrap.virtualMachineManager().defaultConnector();
        Map<String, Connector.Argument> ca = lc.defaultArguments();
        ca.get("main").setValue(mainClass);
        ca.get("options").setValue("-cp " + cp + " -Xss8m");
        vm = lc.launch(ca);
        drain(vm.process().getInputStream());
        drain(vm.process().getErrorStream());
        EventRequestManager erm = vm.eventRequestManager();
        ClassPrepareRequest cpr = erm.createClassPrepareRequest();
        cpr.addClassFilter(approach);
        cpr.enable();
        ClassPrepareRequest cpm = erm.createClassPrepareRequest();
        cpm.addClassFilter(mainClass);
        cpm.enable();

        List<String> steps = new ArrayList<>();
        boolean truncated = false, done = false;
        StepRequest step = null;
        String entryMethod = null;
        int lastLine = -1, lastDepth = -1;
        long lastIndex = -1, rawEvents = 0;
        EventQueue q = vm.eventQueue();
        outer:
        while (!done) {
            EventSet set = q.remove(20000);
            if (set == null) { truncated = true; break; }
            for (Event ev : set) {
                if (ev instanceof VMDeathEvent || ev instanceof VMDisconnectEvent) { done = true; break; }
                if (ev instanceof ClassPrepareEvent cpe) {
                    ReferenceType rt = cpe.referenceType();
                    if (rt.name().equals(mainClass)) {
                        mainType = (ClassType) rt;
                        fmt = mainType.methodsByName("fmt").get(0);
                    }
                    if (rt.name().equals(approach)) {
                        MethodEntryRequest mer = erm.createMethodEntryRequest();
                        mer.addClassFilter(approach);
                        mer.enable();
                    }
                } else if (ev instanceof MethodEntryEvent me && step == null) {
                    if (me.method().isConstructor()) continue;
                    erm.deleteEventRequests(erm.methodEntryRequests());
                    entryMethod = me.method().name();
                    steps.add(snapshot(me.thread(), me.location(), null, false));
                    lastLine = me.location().lineNumber(); lastIndex = me.location().codeIndex(); lastDepth = 1;
                    step = erm.createStepRequest(me.thread(), StepRequest.STEP_MIN, StepRequest.STEP_INTO);
                    step.addClassFilter(approach);
                    step.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
                    step.enable();
                    MethodExitRequest mx = erm.createMethodExitRequest();
                    mx.addClassFilter(approach);
                    mx.setSuspendPolicy(EventRequest.SUSPEND_EVENT_THREAD);
                    mx.enable();
                } else if (ev instanceof MethodExitEvent mxe) {
                    if (mxe.method().name().equals(entryMethod) && depthOf(mxe.thread()) == 1) {
                        step.disable();
                        steps.add(snapshot(mxe.thread(), mxe.location(), mxe.returnValue(), true));
                        vm.exit(0);
                        break outer;
                    }
                } else if (ev instanceof StepEvent se) {
                    Location loc = se.location();
                    int depth = depthOf(se.thread());
                    boolean newLine = loc.lineNumber() != lastLine || depth != lastDepth;
                    boolean loopBack = !newLine && loc.codeIndex() < lastIndex;
                    lastIndex = loc.codeIndex();
                    if (++rawEvents > 400000) { truncated = true; vm.exit(0); break outer; }
                    if (!newLine && !loopBack) continue;
                    lastLine = loc.lineNumber(); lastDepth = depth;
                    if (steps.size() >= maxSteps) {
                        truncated = true;
                        step.disable();
                        vm.exit(0);
                        break outer;
                    }
                    step.disable();
                    steps.add(snapshot(se.thread(), loc, null, false));
                    step.enable();
                }
            }
            set.resume();
        }
        try { vm.dispose(); } catch (Exception ignored) {}
        String json = "{\"steps\":[" + String.join(",", steps) + "],\"truncated\":" + truncated + "}";
        Files.writeString(Path.of(args[4]), json, StandardCharsets.UTF_8);
    }

    static int depthOf(ThreadReference t) throws Exception {
        int depth = 0;
        for (StackFrame fr : t.frames()) if (fr.location().declaringType().name().equals(approach)) depth++;
        return depth;
    }

    static String snapshot(ThreadReference t, Location loc, Value ret, boolean isRet) throws Exception {
        int depth = depthOf(t);
        StackFrame f = t.frame(0);
        List<LocalVariable> vars;                       // read everything from the frame BEFORE any method invocation,
        try { vars = f.visibleVariables(); } catch (AbsentInformationException e) { vars = List.of(); }
        Map<LocalVariable, Value> vals = f.getValues(vars);   // because invoking fmt() resumes the thread and invalidates frames
        StringBuilder sb = new StringBuilder();
        sb.append("{\"l\":").append(loc.lineNumber()).append(",\"m\":\"").append(loc.method().name()).append("\",\"d\":").append(depth);
        if (isRet) sb.append(",\"ret\":").append(ret == null ? "null" : fmtValue(t, ret, 0));
        sb.append(",\"v\":{");
        boolean first = true;
        for (LocalVariable lv : vars) {
            String v = fmtValue(t, vals.get(lv), 0);
            if (!first) sb.append(',');
            first = false;
            sb.append(js(lv.name())).append(':').append(v);
        }
        sb.append("}}");
        return sb.toString();
    }

    static String fmtValue(ThreadReference t, Value v, int depth) throws Exception {
        if (v == null) return "null";
        if (v instanceof VoidValue) return "\"(void)\"";
        if (v instanceof CharValue c) return js(String.valueOf(c.value()));
        if (v instanceof BooleanValue b) return String.valueOf(b.value());
        if (v instanceof PrimitiveValue p) {
            String s = p.toString();
            if (s.equals("NaN") || s.contains("Infinity")) return js(s);
            return s;
        }
        if (v instanceof StringReference s) return js(s.value());
        if (v instanceof ArrayReference arr) {
            int n = arr.length(), cap = depth == 0 ? 64 : 16;
            StringBuilder sb = new StringBuilder("{\"a\":[");
            for (int i = 0; i < Math.min(n, cap); i++) {
                if (i > 0) sb.append(',');
                sb.append(fmtValue(t, arr.getValue(i), depth + 1));
            }
            sb.append("]").append(n > cap ? ",\"more\":" + (n - cap) : "").append("}");
            return sb.toString();
        }
        if (v instanceof ObjectReference o) {
            String type = o.referenceType().name();
            if (type.endsWith("$ListNode")) {
                Field val = o.referenceType().fieldByName("val"), next = o.referenceType().fieldByName("next");
                StringBuilder sb = new StringBuilder("{\"n\":" + o.uniqueID() + ",\"c\":[");
                Set<Long> seen = new HashSet<>();
                ObjectReference cur = o;
                int k = 0;
                while (cur != null && k < 30) {
                    if (k > 0) sb.append(',');
                    sb.append('[').append(cur.uniqueID()).append(',').append(cur.getValue(val)).append(']');
                    if (!seen.add(cur.uniqueID())) break;          // cycle: repeated node closes the chain
                    cur = (ObjectReference) cur.getValue(next);
                    k++;
                }
                return sb.append("]}").toString();
            }
            if (type.startsWith("java.lang.") && (type.endsWith("Integer") || type.endsWith("Long") || type.endsWith("Character")
                    || type.endsWith("Boolean") || type.endsWith("Double") || type.endsWith("Short") || type.endsWith("Byte"))) {
                return fmtValue(t, o.getValue(o.referenceType().fieldByName("value")), depth);
            }
            if (fmt != null && depth == 0) {
                Value r = mainType.invokeMethod(t, fmt, List.of(o), ClassType.INVOKE_SINGLE_THREADED);
                return "{\"o\":" + js(((StringReference) r).value()) + "}";
            }
            return "{\"o\":" + js(type.substring(type.lastIndexOf('.') + 1)) + "}";
        }
        return js(v.toString());
    }

    static String js(String s) {
        StringBuilder sb = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> { if (c < 0x20) sb.append(String.format("\\u%04x", (int) c)); else sb.append(c); }
            }
        }
        return sb.append('"').toString();
    }

    static void drain(InputStream in) {
        Thread th = new Thread(() -> { try { in.transferTo(OutputStream.nullOutputStream()); } catch (IOException ignored) {} });
        th.setDaemon(true);
        th.start();
    }
}
