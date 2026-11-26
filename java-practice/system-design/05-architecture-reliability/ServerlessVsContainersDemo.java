import java.util.*;

public class ServerlessVsContainersDemo {
    // Cost and cold-start model for a spiky workload over one day (per hour request counts).
    public static void main(String[] args) {
        int[] reqPerHour = new int[24];
        for (int h = 0; h < 24; h++) reqPerHour[h] = (h >= 9 && h <= 11) ? 400_000 : (h >= 19 && h <= 21 ? 250_000 : 5_000);
        long total = Arrays.stream(reqPerHour).asLongStream().sum();
        double lambdaPerReq = 0.20 / 1e6 + 0.2 * 0.5 * 0.0000166667;         // request fee + 200 ms x 0.5 GB
        double serverless = total * lambdaPerReq;
        double containerPerHour = 0.04;                                       // one small container
        int perContainerPerHour = 100_000;
        double fixedFleet = 24 * containerPerHour * Math.ceil(400_000.0 / perContainerPerHour);
        double autoscaled = 0; for (int r : reqPerHour) autoscaled += containerPerHour * Math.max(1, Math.ceil(r / (double) perContainerPerHour));
        System.out.printf("requests per day: %,d (spiky)%n", total);
        System.out.printf("serverless (pay per request)        : $%.2f/day, scales to zero, cold starts ~%d ms on first requests%n", serverless, 400);
        System.out.printf("containers sized for peak, always on : $%.2f/day%n", fixedFleet);
        System.out.printf("containers with autoscaling          : $%.2f/day, min 1 instance, no cold start for the base load%n", autoscaled);
        int[] steady = new int[24]; Arrays.fill(steady, 400_000);
        double sSteady = Arrays.stream(steady).asLongStream().sum() * lambdaPerReq, cSteady = 24 * containerPerHour * 4;
        System.out.printf("steady 400k/hour all day             : serverless $%.2f vs containers $%.2f -> containers win at constant high load%n", sSteady, cSteady);
    }
}
