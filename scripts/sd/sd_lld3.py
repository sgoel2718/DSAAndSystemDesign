"""Low-level design questions with complete, runnable Java code (part 3: gap fill)."""
from sd_util2 import L

LLD3 = [
L("chess-lld", "Design a chess game", "Advanced",
  ["Microsoft", "Amazon", "Google", "Adobe"],
  ["8×8 board, two players, standard piece moves", "Validate moves (no moving through pieces, can't capture own piece)", "Turns alternate; detect check; game ends on king capture/checkmate (simplified)"],
  ["Game, Board, Cell/Position", "Piece (abstract) with King, Queen, Rook, Bishop, Knight, Pawn", "Move, Player, Color"],
  ["Polymorphism: each piece validates its own moves", "Template-style shared path checking", "Command (Move objects enable undo/history)"],
  r"""
import java.util.*;

public class ChessDemo {
    enum Color { WHITE, BLACK }
    record Pos(int r, int c) { boolean in() { return r >= 0 && r < 8 && c >= 0 && c < 8; }
        static Pos of(String s) { return new Pos(s.charAt(1) - '1', s.charAt(0) - 'a'); } }

    static abstract class Piece {
        final Color color; Piece(Color c) { color = c; }
        abstract boolean canMove(Board b, Pos from, Pos to);
        abstract char symbol();
        char show() { return color == Color.WHITE ? Character.toUpperCase(symbol()) : symbol(); }
    }
    static boolean clearPath(Board b, Pos f, Pos t) {             // for sliding pieces
        int dr = Integer.signum(t.r() - f.r()), dc = Integer.signum(t.c() - f.c());
        for (int r = f.r() + dr, c = f.c() + dc; r != t.r() || c != t.c(); r += dr, c += dc) if (b.at(new Pos(r, c)) != null) return false;
        return true;
    }
    static final class Rook extends Piece { Rook(Color c) { super(c); } char symbol() { return 'r'; }
        boolean canMove(Board b, Pos f, Pos t) { return (f.r() == t.r() || f.c() == t.c()) && clearPath(b, f, t); } }
    static final class Bishop extends Piece { Bishop(Color c) { super(c); } char symbol() { return 'b'; }
        boolean canMove(Board b, Pos f, Pos t) { return Math.abs(f.r() - t.r()) == Math.abs(f.c() - t.c()) && clearPath(b, f, t); } }
    static final class Queen extends Piece { Queen(Color c) { super(c); } char symbol() { return 'q'; }
        boolean canMove(Board b, Pos f, Pos t) { return new Rook(color).canMove(b, f, t) || new Bishop(color).canMove(b, f, t); } }
    static final class Knight extends Piece { Knight(Color c) { super(c); } char symbol() { return 'n'; }
        boolean canMove(Board b, Pos f, Pos t) { int dr = Math.abs(f.r() - t.r()), dc = Math.abs(f.c() - t.c()); return dr * dc == 2; } }
    static final class King extends Piece { King(Color c) { super(c); } char symbol() { return 'k'; }
        boolean canMove(Board b, Pos f, Pos t) { return Math.max(Math.abs(f.r() - t.r()), Math.abs(f.c() - t.c())) == 1; } }
    static final class Pawn extends Piece { Pawn(Color c) { super(c); } char symbol() { return 'p'; }
        boolean canMove(Board b, Pos f, Pos t) {
            int dir = color == Color.WHITE ? 1 : -1, start = color == Color.WHITE ? 1 : 6, dr = t.r() - f.r(), dc = Math.abs(t.c() - f.c());
            Piece target = b.at(t);
            if (dc == 0 && target == null) return dr == dir || (f.r() == start && dr == 2 * dir && b.at(new Pos(f.r() + dir, f.c())) == null);
            return dc == 1 && dr == dir && target != null;          // diagonal capture
        } }

    static final class Board {
        private final Piece[][] g = new Piece[8][8];
        Piece at(Pos p) { return g[p.r()][p.c()]; }
        void set(Pos p, Piece x) { g[p.r()][p.c()] = x; }
        static Board standard() {
            Board b = new Board();
            for (Color col : Color.values()) {
                int back = col == Color.WHITE ? 0 : 7, pawns = col == Color.WHITE ? 1 : 6;
                Piece[] row = {new Rook(col), new Knight(col), new Bishop(col), new Queen(col), new King(col), new Bishop(col), new Knight(col), new Rook(col)};
                for (int c = 0; c < 8; c++) { b.g[back][c] = row[c]; b.g[pawns][c] = new Pawn(col); }
            }
            return b;
        }
        Pos kingOf(Color c) { for (int r = 0; r < 8; r++) for (int k = 0; k < 8; k++) if (g[r][k] instanceof King && g[r][k].color == c) return new Pos(r, k); return null; }
        boolean attacked(Pos target, Color by) {
            for (int r = 0; r < 8; r++) for (int c = 0; c < 8; c++) { Piece p = g[r][c]; if (p != null && p.color == by && p.canMove(this, new Pos(r, c), target)) return true; }
            return false;
        }
        void print() { for (int r = 7; r >= 0; r--) { StringBuilder sb = new StringBuilder((r + 1) + " "); for (int c = 0; c < 8; c++) sb.append(g[r][c] == null ? '.' : g[r][c].show()); System.out.println(sb); } System.out.println("  abcdefgh"); }
    }
    record Move(Pos from, Pos to, Piece moved, Piece captured) {}

    static final class Game {
        final Board board = Board.standard(); Color turn = Color.WHITE; final Deque<Move> history = new ArrayDeque<>(); Color winner;
        void move(String from, String to) {
            if (winner != null) throw new IllegalStateException("Game over");
            Pos f = Pos.of(from), t = Pos.of(to); Piece p = board.at(f), cap = board.at(t);
            if (p == null || p.color != turn) throw new IllegalArgumentException("No " + turn + " piece at " + from);
            if (!t.in() || (cap != null && cap.color == turn) || !p.canMove(board, f, t)) throw new IllegalArgumentException("Illegal move " + from + "-" + to);
            board.set(t, p); board.set(f, null);
            if (board.attacked(board.kingOf(turn), other(turn))) { board.set(f, p); board.set(t, cap); throw new IllegalArgumentException("Move leaves king in check"); }
            history.push(new Move(f, t, p, cap));
            if (cap instanceof King) winner = turn;
            turn = other(turn);
            if (winner == null && board.attacked(board.kingOf(turn), other(turn))) System.out.println("  " + turn + " is in check");
        }
        void undo() { Move m = history.pop(); board.set(m.from(), m.moved()); board.set(m.to(), m.captured()); turn = other(turn); winner = null; }
        static Color other(Color c) { return c == Color.WHITE ? Color.BLACK : Color.WHITE; }
    }

    public static void main(String[] args) {
        Game g = new Game();
        String[][] moves = {{"e2", "e4"}, {"e7", "e5"}, {"f1", "c4"}, {"b8", "c6"}, {"d1", "h5"}, {"g8", "f6"}, {"h5", "f7"}};  // scholar's mate
        for (String[] m : moves) { System.out.println(g.turn + ": " + m[0] + "-" + m[1]); g.move(m[0], m[1]); }
        try { g.move("e8", "e7"); } catch (IllegalArgumentException e) { System.out.println("rejected: " + e.getMessage()); }
        g.board.print();
        g.undo(); System.out.println("after undo, turn = " + g.turn);
    }
}
""",
  ["Full checkmate/stalemate detection (try all legal moves)", "Castling, en passant, promotion", "Timers per player; online play with a game server", "AI opponent (minimax with alpha-beta)"]),

L("meetingroom-lld", "Design a meeting room booking system", "Intermediate",
  ["Microsoft", "Google", "Atlassian", "Amazon"],
  ["Rooms with capacity", "Book a room for [start, end) if free; no overlaps", "Find available rooms for a time and size", "Cancel bookings; thread-safe"],
  ["Room", "Booking (interval)", "RoomScheduler with TreeMap per room", "BookingService"],
  ["TreeMap floor/ceiling for O(log n) overlap checks", "Per-room locking", "Strategy for room selection (smallest room that fits)"],
  r"""
import java.time.*;
import java.util.*;
import java.util.concurrent.*;

public class MeetingRoomDemo {
    record Room(String id, int capacity) {}
    record Booking(String id, String roomId, LocalDateTime start, LocalDateTime end, String owner) {}

    static final class RoomCalendar {
        private final TreeMap<LocalDateTime, Booking> byStart = new TreeMap<>();
        synchronized boolean isFree(LocalDateTime s, LocalDateTime e) {
            Map.Entry<LocalDateTime, Booking> before = byStart.lowerEntry(e);   // latest booking starting before our end
            return before == null || !before.getValue().end().isAfter(s);       // it must finish by our start
        }
        synchronized boolean tryAdd(Booking b) { if (!isFree(b.start(), b.end())) return false; byStart.put(b.start(), b); return true; }
        synchronized boolean remove(Booking b) { return byStart.remove(b.start(), b); }
    }

    interface RoomPicker { Optional<Room> pick(List<Room> candidates, int people); }
    static final class SmallestFit implements RoomPicker {
        public Optional<Room> pick(List<Room> c, int people) { return c.stream().filter(r -> r.capacity() >= people).min(Comparator.comparingInt(Room::capacity)); }
    }

    static final class BookingService {
        private final Map<String, Room> rooms = new LinkedHashMap<>(); private final Map<String, RoomCalendar> cal = new ConcurrentHashMap<>();
        private final Map<String, Booking> bookings = new ConcurrentHashMap<>(); private final RoomPicker picker;
        BookingService(RoomPicker p) { picker = p; }
        void addRoom(Room r) { rooms.put(r.id(), r); cal.put(r.id(), new RoomCalendar()); }
        List<Room> available(LocalDateTime s, LocalDateTime e, int people) {
            return rooms.values().stream().filter(r -> r.capacity() >= people && cal.get(r.id()).isFree(s, e)).toList();
        }
        Booking book(LocalDateTime s, LocalDateTime e, int people, String owner) {
            if (!e.isAfter(s)) throw new IllegalArgumentException("end must be after start");
            List<Room> cands = new ArrayList<>(available(s, e, people));
            while (!cands.isEmpty()) {                                      // another thread may win a room: try the next
                Room r = picker.pick(cands, people).orElseThrow();
                Booking b = new Booking(UUID.randomUUID().toString().substring(0, 8), r.id(), s, e, owner);
                if (cal.get(r.id()).tryAdd(b)) { bookings.put(b.id(), b); return b; }
                cands.remove(r);
            }
            throw new IllegalStateException("No room available for " + people + " people");
        }
        void cancel(String bookingId) { Booking b = bookings.remove(bookingId); if (b != null) cal.get(b.roomId()).remove(b); }
    }

    public static void main(String[] args) throws Exception {
        BookingService svc = new BookingService(new SmallestFit());
        svc.addRoom(new Room("Huddle", 4)); svc.addRoom(new Room("Board", 12)); svc.addRoom(new Room("Hall", 50));
        LocalDateTime ten = LocalDateTime.of(2026, 11, 20, 10, 0), eleven = ten.plusHours(1);
        Booking a = svc.book(ten, eleven, 3, "asha");
        System.out.println("asha -> " + a.roomId());                                   // Huddle (smallest that fits)
        ExecutorService pool = Executors.newFixedThreadPool(4);                        // 4 teams of 10 want 10:30-11:30
        List<Future<String>> fs = new ArrayList<>();
        for (int i = 0; i < 4; i++) { String o = "team" + i; fs.add(pool.submit(() -> { try { return o + " -> " + svc.book(ten.plusMinutes(30), eleven.plusMinutes(30), 10, o).roomId(); } catch (IllegalStateException e) { return o + " -> none"; } })); }
        List<String> res = new ArrayList<>(); for (Future<String> f : fs) res.add(f.get()); pool.shutdown();
        Collections.sort(res); res.forEach(System.out::println);                      // one gets Board, one gets Hall, two get none
        System.out.println("free at 11:00-12:00 for 4: " + svc.available(eleven, eleven.plusHours(1), 4).stream().map(Room::id).toList());
        svc.cancel(a.id());
        System.out.println("after cancel, free at 10:00 for 2: " + svc.available(ten, eleven, 2).stream().map(Room::id).toList());
    }
}
""",
  ["Recurring bookings", "Equipment requirements (projector, VC)", "Waitlists and auto-release if nobody checks in", "Persist in SQL with an exclusion constraint on (room, tsrange)"]),

L("carrental-lld", "Design a car rental system (Zoomcar / Hertz)", "Intermediate",
  ["Amazon", "Microsoft", "Uber", "Ola"],
  ["Branches with vehicles of types", "Search available vehicles for a date range", "Reserve, pick up, return; charge by day plus extras", "Late returns cost extra"],
  ["Vehicle, VehicleType", "Branch", "Reservation (state machine)", "PricingStrategy", "RentalService"],
  ["Strategy (pricing)", "State machine for reservation", "Interval overlap checks per vehicle"],
  r"""
import java.time.*;
import java.util.*;

public class CarRentalDemo {
    enum Type { HATCHBACK, SEDAN, SUV }
    enum Status { RESERVED, PICKED_UP, RETURNED, CANCELLED }
    record Vehicle(String plate, Type type, String branch) {}
    static final class Reservation {
        final String id; final Vehicle v; final LocalDate from, to; Status status = Status.RESERVED; final List<String> extras;
        Reservation(String id, Vehicle v, LocalDate f, LocalDate t, List<String> extras) { this.id = id; this.v = v; from = f; to = t; this.extras = extras; }
        boolean overlaps(LocalDate f, LocalDate t) { return status != Status.CANCELLED && status != Status.RETURNED && f.isBefore(to) && from.isBefore(t); }
    }
    interface Pricing { long price(Reservation r, LocalDate actualReturn); }
    static final class DailyPricing implements Pricing {
        private final Map<Type, Long> perDay = Map.of(Type.HATCHBACK, 1500L, Type.SEDAN, 2200L, Type.SUV, 3500L);
        private final Map<String, Long> extra = Map.of("GPS", 200L, "CHILD_SEAT", 300L);
        public long price(Reservation r, LocalDate ret) {
            long days = Math.max(1, Duration.between(r.from.atStartOfDay(), r.to.atStartOfDay()).toDays());
            long late = Math.max(0, Duration.between(r.to.atStartOfDay(), ret.atStartOfDay()).toDays());
            long perDayExtras = r.extras.stream().mapToLong(e -> extra.getOrDefault(e, 0L)).sum();
            return (days + late) * (perDay.get(r.v.type()) + perDayExtras) + late * 500;     // late fee per day
        }
    }
    static final class RentalService {
        final List<Vehicle> fleet = new ArrayList<>(); final Map<String, Reservation> res = new HashMap<>(); final Pricing pricing; int seq;
        RentalService(Pricing p) { pricing = p; }
        synchronized List<Vehicle> search(String branch, Type t, LocalDate f, LocalDate to) {
            return fleet.stream().filter(v -> v.branch().equals(branch) && v.type() == t)
                        .filter(v -> res.values().stream().noneMatch(r -> r.v.equals(v) && r.overlaps(f, to))).toList();
        }
        synchronized Reservation reserve(String branch, Type t, LocalDate f, LocalDate to, List<String> extras) {
            Vehicle v = search(branch, t, f, to).stream().findFirst().orElseThrow(() -> new IllegalStateException("No " + t + " available"));
            Reservation r = new Reservation("R" + (++seq), v, f, to, extras); res.put(r.id, r); return r;
        }
        synchronized void pickUp(String id) { Reservation r = res.get(id); require(r, Status.RESERVED); r.status = Status.PICKED_UP; }
        synchronized long giveBack(String id, LocalDate when) { Reservation r = res.get(id); require(r, Status.PICKED_UP); r.status = Status.RETURNED; return pricing.price(r, when); }
        synchronized void cancel(String id) { Reservation r = res.get(id); require(r, Status.RESERVED); r.status = Status.CANCELLED; }
        private void require(Reservation r, Status s) { if (r == null || r.status != s) throw new IllegalStateException("Reservation not in state " + s); }
    }

    public static void main(String[] args) {
        RentalService svc = new RentalService(new DailyPricing());
        svc.fleet.add(new Vehicle("TN09AA1111", Type.SUV, "Chennai")); svc.fleet.add(new Vehicle("TN09BB2222", Type.SEDAN, "Chennai"));
        LocalDate d1 = LocalDate.of(2026, 12, 20), d4 = d1.plusDays(3);
        Reservation r = svc.reserve("Chennai", Type.SUV, d1, d4, List.of("GPS"));
        System.out.println("reserved " + r.v.plate() + " " + r.id);
        try { svc.reserve("Chennai", Type.SUV, d1.plusDays(1), d4.plusDays(1), List.of()); } catch (IllegalStateException e) { System.out.println(e.getMessage()); }
        System.out.println("SUVs free after: " + svc.search("Chennai", Type.SUV, d4, d4.plusDays(2)).size());
        svc.pickUp(r.id);
        System.out.println("bill Rs " + svc.giveBack(r.id, d4.plusDays(1)));            // 3 days + 1 late day, GPS, late fee
    }
}
""",
  ["Interval tree per vehicle for faster availability", "Payments and deposits", "One-way rentals across branches", "Damage reports and insurance add-ons"]),

L("stackoverflow-lld", "Design Stack Overflow (questions, answers, votes, reputation)", "Intermediate",
  ["Microsoft", "Amazon", "Google", "Atlassian"],
  ["Users post questions with tags, answers and comments", "Upvote/downvote with one vote per user per post; can change vote", "Reputation: +10 per upvote on answers, +5 on questions, −2 per downvote; +15 for accepted answer", "Search questions by tag"],
  ["User", "Post (abstract) → Question, Answer", "Vote", "ReputationPolicy", "QAService (tag index)"],
  ["Inheritance for posts", "Strategy (reputation rules)", "Observer-like updates of reputation on vote events"],
  r"""
import java.util.*;

public class StackOverflowDemo {
    static final class User { final String name; int rep = 1; User(String n) { name = n; } }
    static abstract class Post {
        final long id; final User author; final String body; final Map<User, Integer> votes = new HashMap<>();
        Post(long id, User a, String b) { this.id = id; author = a; body = b; }
        int score() { return votes.values().stream().mapToInt(Integer::intValue).sum(); }
        abstract int upRep();
    }
    static final class Question extends Post {
        final String title; final Set<String> tags; final List<Answer> answers = new ArrayList<>(); Answer accepted;
        Question(long id, User a, String title, String b, Set<String> tags) { super(id, a, b); this.title = title; this.tags = tags; }
        int upRep() { return 5; }
    }
    static final class Answer extends Post { final Question q; Answer(long id, User a, String b, Question q) { super(id, a, b); this.q = q; } int upRep() { return 10; } }

    interface ReputationPolicy { int forVote(Post p, int vote); int forAccept(); }
    static final class DefaultRep implements ReputationPolicy {
        public int forVote(Post p, int v) { return v > 0 ? p.upRep() : v < 0 ? -2 : 0; }
        public int forAccept() { return 15; }
    }

    static final class QAService {
        private long ids; private final Map<String, List<Question>> byTag = new HashMap<>(); private final ReputationPolicy rep;
        QAService(ReputationPolicy r) { rep = r; }
        Question ask(User u, String title, String body, Set<String> tags) {
            Question q = new Question(++ids, u, title, body, tags);
            tags.forEach(t -> byTag.computeIfAbsent(t.toLowerCase(), k -> new ArrayList<>()).add(q)); return q;
        }
        Answer answer(User u, Question q, String body) { Answer a = new Answer(++ids, u, body, q); q.answers.add(a); return a; }
        void vote(User voter, Post p, int dir) {                       // dir: +1, -1, 0 (remove)
            if (voter == p.author) throw new IllegalArgumentException("Cannot vote on your own post");
            int old = p.votes.getOrDefault(voter, 0);
            p.author.rep += rep.forVote(p, dir) - rep.forVote(p, old);   // undo old vote's effect, apply new
            if (dir == 0) p.votes.remove(voter); else p.votes.put(voter, dir);
        }
        void accept(User asker, Answer a) {
            if (asker != a.q.author) throw new IllegalArgumentException("Only the asker can accept");
            if (a.q.accepted != null) a.q.accepted.author.rep -= rep.forAccept();
            a.q.accepted = a; a.author.rep += rep.forAccept();
        }
        List<Question> byTag(String tag) {
            return byTag.getOrDefault(tag.toLowerCase(), List.of()).stream().sorted(Comparator.comparingInt(Post::score).reversed()).toList();
        }
    }

    public static void main(String[] args) {
        QAService so = new QAService(new DefaultRep());
        User asha = new User("asha"), ravi = new User("ravi"), meera = new User("meera");
        Question q = so.ask(asha, "Why is HashMap not thread-safe?", "...", Set.of("java", "concurrency"));
        Answer a = so.answer(ravi, q, "Use ConcurrentHashMap because ...");
        so.vote(meera, a, +1); so.vote(asha, a, +1); so.vote(meera, q, +1);
        so.vote(meera, a, -1);                                         // meera changes her mind: +10 removed, -2 applied
        so.accept(asha, a);
        System.out.println("ravi rep " + ravi.rep + ", asha rep " + asha.rep + ", answer score " + a.score());
        System.out.println("java questions: " + so.byTag("Java").stream().map(x -> x.title).toList());
        try { so.vote(ravi, a, +1); } catch (IllegalArgumentException e) { System.out.println("rejected: " + e.getMessage()); }
    }
}
""",
  ["Bounties, badges (Observer on events)", "Full-text search with an inverted index", "Moderation, flags, closing duplicates", "Persist votes with a unique (user, post) constraint"]),
]
