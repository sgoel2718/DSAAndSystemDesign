import java.util.*;

public class EventSourcingDemo {
    sealed interface Event permits Opened, Deposited, Withdrew {}
    record Opened(String owner) implements Event {}
    record Deposited(int amount) implements Event {}
    record Withdrew(int amount) implements Event {}
    record Account(String owner, int balance, int version) {
        Account apply(Event e) {
            return switch (e) {
                case Opened o -> new Account(o.owner(), 0, version + 1);
                case Deposited d -> new Account(owner, balance + d.amount(), version + 1);
                case Withdrew w -> new Account(owner, balance - w.amount(), version + 1);
            };
        }
    }

    static final List<Event> store = new ArrayList<>();                   // append-only, the source of truth

    static void handleWithdraw(int amount) {                              // command -> validate against current state -> new event
        Account now = replay(store.size());
        if (now.balance() < amount) { System.out.println("withdraw " + amount + " rejected: balance " + now.balance()); return; }
        store.add(new Withdrew(amount));
    }
    static Account replay(int upTo) { Account a = new Account(null, 0, 0); for (int i = 0; i < upTo; i++) a = a.apply(store.get(i)); return a; }

    public static void main(String[] args) {
        store.add(new Opened("asha")); store.add(new Deposited(1000));
        handleWithdraw(300); store.add(new Deposited(50)); handleWithdraw(2000); handleWithdraw(200);
        for (int i = 0; i < store.size(); i++) System.out.println("#" + (i + 1) + " " + store.get(i) + "  -> balance " + replay(i + 1).balance());
        System.out.println("current state: " + replay(store.size()));
        System.out.println("time travel, state after event #3: " + replay(3));
        int deposits = store.stream().filter(e -> e instanceof Deposited).mapToInt(e -> ((Deposited) e).amount()).sum();
        System.out.println("new read model built later by replaying: total deposited = " + deposits);
    }
}
