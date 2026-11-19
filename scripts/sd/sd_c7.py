"""System Design concepts, part 7: Low-level design (OOP, SOLID, UML, design patterns, concurrency) in Java."""
from sd_util import C

LLD = [
C("oop-pillars", "OOP: the four pillars", "Basic",
  "Encapsulation, abstraction, inheritance and polymorphism — the foundation of every low-level design answer.",
  """- **Encapsulation**: keep data private, expose behaviour. `account.withdraw(500)` checks the balance; nobody sets `balance` directly.
- **Abstraction**: show what an object does, hide how. Callers use `PaymentGateway.pay()`, not the HTTP details.
- **Inheritance**: `class SavingsAccount extends Account` reuses code (use sparingly).
- **Polymorphism**: one interface, many implementations, chosen at runtime.

```java
interface Shape { double area(); }
record Circle(double r) implements Shape { public double area() { return Math.PI * r * r; } }
record Rect(double w, double h) implements Shape { public double area() { return w * h; } }

double total(List<Shape> shapes) {           // works for any future Shape too
    return shapes.stream().mapToDouble(Shape::area).sum();
}
```

### Composition over inheritance
Prefer 'has-a' to 'is-a': a `Car` *has an* `Engine` (swap petrol for electric at runtime) instead of `ElectricCar extends Car`. Deep inheritance trees are rigid and fragile.""",
  tips=["In LLD rounds, start from entities (nouns) and their behaviours (verbs), then relationships."]),

C("solid", "SOLID principles", "Basic",
  "Five rules for classes that are easy to change: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion.",
  """### S — Single Responsibility
A class should have one reason to change. Split `InvoiceService` that calculates, prints and emails into `InvoiceCalculator`, `InvoicePrinter`, `InvoiceMailer`.

### O — Open/Closed
Open for extension, closed for modification. Add a new discount type by adding a class, not by editing a giant `if/else`.
```java
interface Discount { double apply(double price); }
class FestiveDiscount implements Discount { public double apply(double p) { return p * 0.9; } }
```

### L — Liskov Substitution
Subclasses must work wherever the parent works. A `Square extends Rectangle` whose `setWidth` also changes height breaks code expecting a rectangle → don't inherit there.

### I — Interface Segregation
Many small interfaces beat one fat one. A `Printer` shouldn't force `fax()` on devices that can't fax: split into `Printable`, `Scannable`, `Faxable`.

### D — Dependency Inversion
Depend on abstractions, not concrete classes; inject them.
```java
class OrderService {
    private final PaymentGateway gateway;              // interface
    OrderService(PaymentGateway gateway) { this.gateway = gateway; }   // Razorpay, Stripe or a test fake
}
```
Also know **DRY** (don't repeat yourself), **KISS**, **YAGNI**, and the **Law of Demeter** (talk only to your direct friends).""",
  tips=["Name the principle when you apply it in an LLD answer: 'Strategy here keeps us open/closed'."]),

C("uml", "UML class diagrams and relationships", "Basic",
  "A quick way to show classes and how they relate: association, aggregation, composition, inheritance, realisation, dependency.",
  """|Relationship|Meaning|Example|Notation|
|Association|Uses / knows about|`Driver` — `Car`|plain line|
|Aggregation|Has-a, parts can live alone|`Team` ◇— `Player`|hollow diamond|
|Composition|Owns, parts die with the whole|`House` ◆— `Room`|filled diamond|
|Inheritance (generalisation)|Is-a|`Dog` —▷ `Animal`|hollow triangle|
|Realisation|Implements an interface|`ArrayList` ⇢▷ `List`|dashed + triangle|
|Dependency|Temporarily uses (parameter)|`Report` ⇢ `Printer`|dashed arrow|

Multiplicity: `1`, `0..1`, `*`, `1..*` on each end (one `ParkingLot` has `1..*` `Floor`s).

In interviews a simple text diagram is enough: list classes with key fields/methods and arrows between them. Sequence diagrams help for flows (checkout, booking).""",
  diagram={"rows": [["ParkingLot"], ["Floor"], ["Spot", "EntryGate"], ["CarSpot", "BikeSpot"]],
           "edges": [["ParkingLot", "Floor", "1..* composition"], ["Floor", "Spot", "1..*"], ["Floor", "EntryGate"], ["CarSpot", "Spot", "is-a"], ["BikeSpot", "Spot", "is-a"]]}),

C("creational-patterns", "Creational patterns: Singleton, Factory, Abstract Factory, Builder, Prototype", "Intermediate",
  "Patterns about creating objects in a controlled, flexible way.",
  """### Singleton — one instance (config, connection pool registry)
```java
public final class AppConfig {
    private AppConfig() {}
    private static class Holder { static final AppConfig INSTANCE = new AppConfig(); }  // lazy, thread-safe
    public static AppConfig get() { return Holder.INSTANCE; }
}
// or simply: enum AppConfig { INSTANCE; }
```
Caution: global state hurts testing; prefer dependency injection.

### Factory Method — decide which class to create
```java
static Notification create(String type) {
    return switch (type) { case "SMS" -> new SmsNotification(); case "EMAIL" -> new EmailNotification(); default -> new PushNotification(); };
}
```

### Abstract Factory — families of related objects
`UIFactory` with `DarkFactory` / `LightFactory` creating matching `Button` + `Checkbox`.

### Builder — many optional parameters, readable construction
```java
Pizza p = new Pizza.Builder("large").cheese(true).topping("paneer").topping("olives").build();
```

### Prototype — copy an existing object instead of building from scratch (`clone()` / copy constructors), e.g. game objects, document templates.""",
  see=("lld-approach",)),

C("structural-patterns", "Structural patterns: Adapter, Decorator, Facade, Proxy, Composite, Bridge, Flyweight", "Intermediate",
  "Patterns about composing classes and objects into larger structures.",
  """- **Adapter**: make an incompatible interface fit. Wrap a third-party `LegacyPayClient` so it implements your `PaymentGateway`.
- **Decorator**: add behaviour by wrapping, without subclassing. Java IO: `new BufferedReader(new InputStreamReader(in))`; coffee + milk + sugar pricing.
```java
interface Coffee { double cost(); }
record Basic() implements Coffee { public double cost() { return 50; } }
record Milk(Coffee c) implements Coffee { public double cost() { return c.cost() + 15; } }
double price = new Milk(new Milk(new Basic())).cost();   // 80
```
- **Facade**: one simple entry point over a complex subsystem (`OrderFacade.placeOrder()` calls inventory, payment, shipping).
- **Proxy**: a stand-in controlling access — lazy loading (Hibernate proxies), caching proxy, access-control proxy, remote proxy (RPC stubs).
- **Composite**: treat single objects and groups the same (files and folders both have `size()`; a folder sums its children).
- **Bridge**: separate abstraction from implementation so both vary (`Shape` × `Renderer`: vector or raster).
- **Flyweight**: share common state among many objects to save memory (characters in a text editor, trees in a game map).""",
  see=("lld-approach",)),

C("behavioral-patterns", "Behavioural patterns: Strategy, Observer, Command, State, Template, Chain of Responsibility, Iterator, Mediator, Memento, Visitor", "Intermediate",
  "Patterns about how objects communicate and divide responsibilities.",
  """- **Strategy**: swap algorithms at runtime (pricing, parking fee, payment, sorting). The most used pattern in LLD rounds.
```java
interface FeeStrategy { long fee(Duration d); }
class HourlyFee implements FeeStrategy { public long fee(Duration d) { return Math.max(1, d.toHours()) * 40; } }
```
- **Observer**: subscribers get notified on changes (stock price alerts, event listeners, notification on order status).
```java
interface Listener { void onEvent(String e); }
class EventBus { private final List<Listener> ls = new ArrayList<>();
  void subscribe(Listener l) { ls.add(l); } void publish(String e) { ls.forEach(l -> l.onEvent(e)); } }
```
- **Command**: wrap a request as an object → undo/redo, queues, macros (text editor, remote control).
- **State**: behaviour changes with internal state (vending machine: Idle → HasMoney → Dispensing; order lifecycle). Replaces big switch statements.
- **Template Method**: base class fixes the algorithm's skeleton; subclasses fill steps (data importers: open → parse → validate → save).
- **Chain of Responsibility**: pass a request along handlers until one handles it (ATM note dispensing ₹2000 → ₹500 → ₹100; logging levels; middleware filters).
- **Iterator**: traverse a collection without exposing its structure.
- **Mediator**: objects talk through a central mediator (chat room, air-traffic control) instead of to each other.
- **Memento**: save and restore state (undo, game save points).
- **Visitor**: add operations over an object structure without changing its classes (export shapes to XML/JSON).""",
  see=("lld-approach",)),

C("concurrency-java", "Concurrency in Java for LLD", "Advanced",
  "LLD questions often add 'make it thread-safe': know synchronized, locks, atomic variables, concurrent collections, executors and producer–consumer.",
  """### Tools
- `synchronized` methods/blocks (intrinsic lock), `volatile` (visibility, no atomicity).
- `ReentrantLock` (tryLock, fairness), `ReentrantReadWriteLock` (many readers, one writer), `StampedLock`.
- `AtomicInteger`, `AtomicLong`, `LongAdder` (high-contention counters), CAS (`compareAndSet`).
- `ConcurrentHashMap` (`computeIfAbsent`, `merge` are atomic), `CopyOnWriteArrayList`, `BlockingQueue`.
- `ExecutorService`, `CompletableFuture`, virtual threads (Java 21: `Executors.newVirtualThreadPerTaskExecutor()`).
- `CountDownLatch`, `Semaphore` (limit concurrent access), `CyclicBarrier`.

### Producer–consumer
```java
BlockingQueue<Order> q = new ArrayBlockingQueue<>(1000);   // bounded = backpressure
Runnable producer = () -> { try { q.put(new Order()); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } };
Runnable consumer = () -> { try { while (true) process(q.take()); } catch (InterruptedException e) { Thread.currentThread().interrupt(); } };
```

### Classic problems
- **Race condition**: `count++` is read–modify–write → use atomics or locks.
- **Deadlock**: two threads lock A→B and B→A. Prevent with a global lock order, `tryLock` with timeout.
- **Livelock / starvation**: fair locks, backoff.
- **Double-checked locking** needs `volatile`.

### Thread-safe booking (no double booking)
Lock per seat (or `ConcurrentHashMap.putIfAbsent(seatId, bookingId)`) rather than one global lock, so different seats can be booked in parallel.""",
  see=("lld-approach",)),

C("lld-approach", "How to answer a low-level design (machine coding) round", "Basic",
  "A repeatable 6-step method for 'Design a parking lot / Splitwise / elevator' in 45–90 minutes, in Java.",
  """1. **Clarify requirements (5 min)**: core use cases only. 'Multiple floors? Vehicle types? Payment? Concurrency?' Write them down.
2. **Identify entities**: nouns → classes (`ParkingLot`, `Floor`, `Spot`, `Vehicle`, `Ticket`, `Payment`). Verbs → methods (`park()`, `unpark()`, `pay()`).
3. **Define relationships**: has-a / is-a, multiplicities; draw a quick class diagram.
4. **Pick patterns where they genuinely help**: Strategy (fees, allocation), Factory (vehicles/spots), Observer (display boards), State (vending machine, elevator), Singleton (only if asked).
5. **Write code**: interfaces first, then core classes, then a `main`/demo that runs the main flow. Use enums, small methods, meaningful names, exceptions for invalid operations.
6. **Discuss extensions**: thread safety, persistence (repositories), new vehicle types, testing.

### What interviewers grade
Working code for the core flow, clean separation of responsibilities (SOLID), extensibility, correct handling of edge cases and concurrency, and how you communicate trade-offs.""",
  tips=["Get a working core flow first; polish later.", "Use interfaces for anything likely to change (pricing, allocation, payment)."]),

C("api-contract-lld", "Designing clean APIs and models inside a service", "Intermediate",
  "Layering and modelling choices that make LLD code look professional: controller → service → repository, DTOs, enums, immutability, exceptions.",
  """- **Layers**: Controller (HTTP) → Service (business rules) → Repository (data access). Each layer depends on interfaces of the next.
- **Immutable value objects** (`record Money(long paise, String currency)`), enums for fixed sets (`VehicleType`, `OrderStatus`).
- Validate inputs at the boundary; throw domain exceptions (`SpotNotAvailableException`).
- Keep money as integers (paise) or `BigDecimal`, never `double`.
- Return `Optional` instead of null for 'not found'.
- Make collaborators injectable for testing (constructor injection).""",
  see=("solid",)),
]
