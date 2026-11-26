import java.util.*;

public class ReliabilityDemo {
    // Simulates a year of a service: failures arrive every ~MTBF hours, each takes MTTR hours to fix.
    static double simulate(double mtbfHours, double mttrHours, long seed) {
        Random r = new Random(seed);
        double t = 0, down = 0, year = 365 * 24;
        while (t < year) {
            double up = -Math.log(1 - r.nextDouble()) * mtbfHours;   // exponential time to next failure
            t += up;
            if (t >= year) break;
            double repair = Math.min(mttrHours, year - t);
            down += repair; t += repair;
        }
        return 1 - down / year;
    }

    public static void main(String[] args) {
        double[][] cases = {{1000, 1}, {1000, 0.1}, {5000, 1}};
        for (double[] c : cases) {
            double formula = c[0] / (c[0] + c[1]);
            double sim = simulate(c[0], c[1], 42);
            System.out.printf("MTBF %5.0f h, MTTR %4.1f h -> formula %.4f%%, simulated year %.4f%%%n", c[0], c[1], formula * 100, sim * 100);
        }
        System.out.println("\nCutting repair time 10x helps as much as making failures 10x rarer.");
        // Durability: chance to lose an object stored on 3 independent disks with 1% annual failure, no repair
        double loss3 = Math.pow(0.01, 3);
        System.out.printf("P(lose all 3 copies in a year, no re-replication) = %.0e%n", loss3);
    }
}
