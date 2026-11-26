import java.util.*;

public class LldApproachDemo {
    // The interview approach in code, for a small "library checkout":
    // 1 requirements -> 2 entities -> 3 relationships -> 4 interfaces/patterns -> 5 core flow -> 6 edge cases
    enum CopyStatus { AVAILABLE, BORROWED }
    record Book(String isbn, String title) {}
    static final class Copy { final String id; final Book book; CopyStatus status = CopyStatus.AVAILABLE; Copy(String id, Book b) { this.id = id; book = b; } }
    record Member(String id, String name, int maxLoans) {}
    record Loan(Copy copy, Member member, int dueDay) {}
    interface FinePolicy { int fine(int daysLate); }                       // strategy: rules can change

    static final class Library {
        private final Map<String, List<Copy>> copiesByIsbn = new HashMap<>(); private final List<Loan> loans = new ArrayList<>(); private final FinePolicy fines;
        Library(FinePolicy f) { fines = f; }
        void addCopy(Copy c) { copiesByIsbn.computeIfAbsent(c.book.isbn(), k -> new ArrayList<>()).add(c); }
        Loan borrow(Member m, String isbn, int today) {
            if (loans.stream().filter(l -> l.member().equals(m)).count() >= m.maxLoans()) throw new IllegalStateException(m.name() + " has reached the loan limit");
            Copy c = copiesByIsbn.getOrDefault(isbn, List.of()).stream().filter(x -> x.status == CopyStatus.AVAILABLE).findFirst()
                .orElseThrow(() -> new IllegalStateException("no copy of " + isbn + " available"));
            c.status = CopyStatus.BORROWED; Loan l = new Loan(c, m, today + 14); loans.add(l); return l;
        }
        int giveBack(Loan l, int today) { loans.remove(l); l.copy().status = CopyStatus.AVAILABLE; return fines.fine(Math.max(0, today - l.dueDay())); }
    }

    public static void main(String[] args) {
        Book ddia = new Book("978-1449373320", "Designing Data-Intensive Applications");
        Library lib = new Library(days -> days * 5);
        lib.addCopy(new Copy("c1", ddia)); lib.addCopy(new Copy("c2", ddia));
        Member asha = new Member("m1", "Asha", 1), ravi = new Member("m2", "Ravi", 3), zoya = new Member("m3", "Zoya", 2);
        Loan a = lib.borrow(asha, ddia.isbn(), 1); System.out.println("Asha borrowed " + a.copy().id + ", due day " + a.dueDay());
        Loan r = lib.borrow(ravi, ddia.isbn(), 2); System.out.println("Ravi borrowed " + r.copy().id);
        for (Runnable edge : List.<Runnable>of(() -> lib.borrow(zoya, ddia.isbn(), 3), () -> lib.borrow(asha, ddia.isbn(), 3)))
            try { edge.run(); } catch (IllegalStateException e) { System.out.println("edge case handled: " + e.getMessage()); }
        System.out.println("Asha returns on day 20 -> fine Rs " + lib.giveBack(a, 20));
        System.out.println("Zoya now borrows " + lib.borrow(zoya, ddia.isbn(), 21).copy().id);
    }
}
