public class AvailabilityDemo {
    static double series(double... parts) { double a = 1; for (double p : parts) a *= p; return a; }
    static double parallel(double each, int copies) { return 1 - Math.pow(1 - each, copies); }
    static String downtime(double a) {
        double minutes = (1 - a) * 365 * 24 * 60;
        return minutes > 120 ? String.format("%.1f hours/year", minutes / 60) : String.format("%.1f minutes/year", minutes);
    }

    public static void main(String[] args) {
        for (double a : new double[]{0.99, 0.999, 0.9999, 0.99999})
            System.out.printf("%.3f%% -> %s%n", a * 100, downtime(a));
        double chain = series(0.9999, 0.999, 0.9995);                     // LB -> app -> DB
        System.out.printf("%nseries LB(99.99) x app(99.9) x DB(99.95) = %.3f%% -> %s%n", chain * 100, downtime(chain));
        double app2 = parallel(0.999, 2), db2 = parallel(0.9995, 2);
        double redundant = series(0.9999, app2, db2);
        System.out.printf("with 2 app servers and a DB standby          = %.4f%% -> %s%n", redundant * 100, downtime(redundant));
        // error budget for an SLO of 99.9% over 30 days
        double budgetMin = 0.001 * 30 * 24 * 60;
        System.out.printf("%nSLO 99.9%% over 30 days -> error budget %.1f minutes; a 25-minute outage uses %.0f%% of it%n", budgetMin, 25 / budgetMin * 100);
    }
}
