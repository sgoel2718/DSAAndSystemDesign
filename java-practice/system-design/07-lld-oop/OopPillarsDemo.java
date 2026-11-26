import java.util.*;

public class OopPillarsDemo {
    // Abstraction: callers depend on what a Payment does, not how.
    interface Payment { String pay(long paise); }

    // Encapsulation: balance can't be changed from outside except through validated methods.
    static class Wallet {
        private long balancePaise;
        Wallet(long initial) { balancePaise = initial; }
        long balance() { return balancePaise; }
        void debit(long p) { if (p <= 0 || p > balancePaise) throw new IllegalArgumentException("invalid debit " + p); balancePaise -= p; }
    }

    // Inheritance: shared behaviour in a base class.
    static abstract class CardPayment implements Payment {
        protected final String last4;
        CardPayment(String last4) { this.last4 = last4; }
        protected String mask() { return "**** " + last4; }
    }
    static class CreditCard extends CardPayment { CreditCard(String l) { super(l); } public String pay(long p) { return "credit card " + mask() + " charged Rs " + p / 100; } }
    static class DebitCard extends CardPayment { DebitCard(String l) { super(l); } public String pay(long p) { return "debit card " + mask() + " charged Rs " + p / 100 + " (PIN verified)"; } }
    static class WalletPayment implements Payment {
        private final Wallet w; WalletPayment(Wallet w) { this.w = w; }
        public String pay(long p) { w.debit(p); return "wallet debited Rs " + p / 100 + ", left Rs " + w.balance() / 100; }
    }

    public static void main(String[] args) {
        Wallet w = new Wallet(1_00_000);
        List<Payment> methods = List.of(new CreditCard("4242"), new DebitCard("1881"), new WalletPayment(w));
        for (Payment p : methods) System.out.println(p.pay(49_900));                 // Polymorphism: one call, many behaviours
        try { new WalletPayment(w).pay(10_00_000); } catch (IllegalArgumentException e) { System.out.println("encapsulation guard: " + e.getMessage()); }
    }
}
