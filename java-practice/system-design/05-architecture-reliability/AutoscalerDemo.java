public class AutoscalerDemo {
    // HPA-style: desired = ceil(current * currentUtil / targetUtil), with a scale-down cooldown and a startup delay.
    public static void main(String[] args) {
        int[] loadPerMin = {200, 220, 600, 1400, 1800, 1800, 1700, 900, 400, 300, 250, 220};
        int capacityPerPod = 100, pods = 3, target = 60, minPods = 2, maxPods = 30, coolDown = 3, lastScaleDown = -10;
        int[] ready = new int[loadPerMin.length + 3];
        System.out.println("min  load  pods  util   action");
        for (int m = 0; m < loadPerMin.length; m++) {
            pods += ready[m];                                                 // pods requested 1 min ago are now ready
            int util = (int) Math.min(999, Math.round(loadPerMin[m] * 100.0 / (pods * capacityPerPod)));
            int desired = Math.max(minPods, Math.min(maxPods, (int) Math.ceil(pods * util / (double) target)));
            String action = "hold";
            if (desired > pods) { ready[m + 1] += desired - pods; action = "scale up +" + (desired - pods) + " (ready next minute)"; }
            else if (desired < pods && m - lastScaleDown >= coolDown) { action = "scale down -" + (pods - desired); pods = desired; lastScaleDown = m; }
            else if (desired < pods) action = "would scale down, in cooldown";
            System.out.printf("%3d  %4d  %4d  %3d%%  %s%s%n", m, loadPerMin[m], pods, util, action, util > 100 ? "  <- overloaded while new pods start" : "");
        }
    }
}
