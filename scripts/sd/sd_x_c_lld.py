"""Detailed explanations with diagrams: LLD & OOP concept cards."""
from sd_x_util import X, P, H, AN, KEY, FLOW, SEQ, NOTE, ER, TABLE, CALC, BARS, CODE, UML, STATE, BA

X("oop-pillars",
  P("Object-oriented design groups **data with the code that uses it**. The four pillars are four rules for doing that well. One running example, a payment system, shows all four:"),
  UML("All four pillars in one small design", [["PaymentMethod"], ["Card", "UpiId", "Wallet"]],
      {"PaymentMethod": ("abstract", ["# id: String", "- balanceCache (hidden)"], ["+ pay(amount): Receipt  (abstract)", "+ refund(receipt)"]),
       "Card": (["- number (masked)", "- expiry"], ["+ pay(amount)"]), "UpiId": (["- vpa"], ["+ pay(amount)"]), "Wallet": (["- balance"], ["+ pay(amount)"])},
      [["Card", "PaymentMethod", "inh"], ["UpiId", "PaymentMethod", "inh"], ["Wallet", "PaymentMethod", "inh"]]),
  TABLE("The pillars, in this design", ["Pillar", "What it means", "Where you see it"],
        [["**Encapsulation**", "hide internal state; expose safe methods", "`Wallet.balance` is private; only `pay()` can change it, so it can't go negative"],
         ["**Abstraction**", "callers use *what* something does, not *how*", "checkout calls `method.pay(499)` without knowing it's UPI"],
         ["**Inheritance**", "a subtype reuses and extends a parent", "`Card`, `UpiId`, `Wallet` share `refund()` from `PaymentMethod`"],
         ["**Polymorphism**", "one call, different behaviour per runtime type", "`for (PaymentMethod m : methods) m.pay(x)` runs Card's or Wallet's code"]]),
  CODE("Polymorphism in action", """List<PaymentMethod> methods = List.of(new Card("4111…"), new UpiId("asha@upi"), new Wallet(500));
for (PaymentMethod m : methods) {
    Receipt r = m.pay(100);        // dynamic dispatch: each subclass's pay() runs
    System.out.println(r);
}"""),
  KEY("Prefer **composition over inheritance** when the relationship is 'has a' or behaviour must change at runtime (e.g. a `Checkout` *has a* `PaymentMethod`, injected), and keep inheritance for true 'is a' relationships with shared behaviour.", "Rule of thumb"))

X("solid",
  P("SOLID is five rules that keep classes small, swappable and easy to test. Each rule below shows a **violation** and the **fix** as class diagrams."),
  H("S · Single Responsibility: one reason to change"),
  BA(UML("One class does three jobs", [["InvoiceService"]], {"InvoiceService": (["- db", "- pdfLib"], ["total(invoice)", "saveToDb(invoice)", "printPdf(invoice)"])}, [],
          "Three reasons to change (tax rules, database, PDF layout) all edit the same class, and testing totals needs a DB."),
     UML("Split by reason to change", [["InvoiceService"], ["InvoiceCalculator", "InvoiceRepository", "InvoicePrinter"]],
          {"InvoiceService": ([], ["finalise(invoice)"]), "InvoiceCalculator": ([], ["total(invoice)"]), "InvoiceRepository": ("interface", [], ["save(invoice)"]), "InvoicePrinter": ([], ["pdf(invoice)"])},
          [["InvoiceService", "InvoiceCalculator", "assoc"], ["InvoiceService", "InvoiceRepository", "assoc"], ["InvoiceService", "InvoicePrinter", "assoc"]],
          "A tax-rule change, a DB change and a PDF-layout change now touch three different classes."),
     "Before: violates S", "After: follows S"),
  H("O · Open/Closed: add behaviour by adding classes, not editing old ones"),
  BA(CODE("Every new discount edits this method", """long price(Cart cart, String type) {
    if (type.equals("PERCENT")) return cart.total() * 90 / 100;
    else if (type.equals("FLAT")) return cart.total() - 50_00;
    else if (type.equals("BUY_X_GET_Y")) ...   // edit, re-test, redeploy this class every time
}"""),
     UML("New discount = new class", [["Checkout"], ["Discount"], ["PercentOff", "FlatOff", "BuyXGetY"]],
      {"Checkout": ([], ["price(cart)"]), "Discount": ("interface", [], ["apply(cart): long"]), "PercentOff": ([], []), "FlatOff": ([], []), "BuyXGetY": (["(added later)"], [])},
      [["Checkout", "Discount", "assoc", "list of"], ["PercentOff", "Discount", "impl"], ["FlatOff", "Discount", "impl"], ["BuyXGetY", "Discount", "impl"]]),
     "Before: violates O (if/else on type)", "After: follows O (new class per rule)"),
  H("L · Liskov Substitution: a subtype must work wherever the parent works"),
  BA(TABLE("Subclasses that break the parent's promise", ["Code", "Problem"], [["`class Square extends Rectangle`; `setWidth(5)` also changes height", "code that sets width 5 and height 4 and expects area 20 gets 16 for a Square"],
                                                       ["`class Ostrich extends Bird`; `fly()` throws", "every caller of `bird.fly()` must now special-case ostriches"]]),
     UML("Model only what is really shared", [["Shape", "Bird"], ["Rectangle", "Square", "Flyer"], ["Sparrow", "Ostrich"]],
         {"Shape": ("interface", [], ["area()"]), "Rectangle": (["w, h"], ["area()"]), "Square": (["side"], ["area()"]), "Bird": ("interface", [], ["eat()"]), "Flyer": ("interface", [], ["fly()"]),
          "Sparrow": ([], ["eat()", "fly()"]), "Ostrich": ([], ["eat()"])},
         [["Rectangle", "Shape", "impl"], ["Square", "Shape", "impl"], ["Sparrow", "Bird", "impl"], ["Sparrow", "Flyer", "impl"], ["Ostrich", "Bird", "impl"]],
         "Square is no longer a Rectangle, and only birds that fly implement Flyer, so no subtype breaks a promise."),
     "Before: violates L", "After: follows L"),
  H("I · Interface Segregation: small, focused interfaces"),
  BA(UML("One fat interface", [["Machine"], ["SimplePrinter", "OfficeMachine"]],
          {"Machine": ("interface", [], ["print(doc)", "scan(): Doc", "fax(doc, no)"]), "SimplePrinter": ([], ["print(doc)", "scan() → throws ✘", "fax() → throws ✘"]), "OfficeMachine": ([], ["print · scan · fax"])},
          [["SimplePrinter", "Machine", "impl"], ["OfficeMachine", "Machine", "impl"]], "SimplePrinter is forced to implement methods it can't support."),
     UML("Split a fat interface", [["Printer", "Scanner", "Fax"], ["SimplePrinter", "OfficeMachine"]],
      {"Printer": ("interface", [], ["print(doc)"]), "Scanner": ("interface", [], ["scan(): Doc"]), "Fax": ("interface", [], ["fax(doc, no)"]), "SimplePrinter": ([], ["print(doc)"]), "OfficeMachine": ([], ["print · scan · fax"])},
      [["SimplePrinter", "Printer", "impl"], ["OfficeMachine", "Printer", "impl"], ["OfficeMachine", "Scanner", "impl"], ["OfficeMachine", "Fax", "impl"]],
      "A simple printer no longer has to implement `fax()` by throwing an exception."),
     "Before: violates I", "After: follows I"),
  H("D · Dependency Inversion: depend on interfaces; inject implementations"),
  BA(UML("Business logic creates its own concrete dependency", [["OrderService"], ["EmailNotifier"]],
          {"OrderService": (["- notifier = new EmailNotifier()"], ["place(order)"]), "EmailNotifier": ([], ["sendEmail(to, body)"])}, [["OrderService", "EmailNotifier", "comp"]],
          "Switching to SMS or testing without sending real emails means editing OrderService."),
     UML("High-level code depends on an abstraction", [["OrderService"], ["Notifier"], ["EmailNotifier", "SmsNotifier", "FakeNotifier (tests)"]],
      {"OrderService": (["- notifier: Notifier"], ["OrderService(Notifier n)", "place(order)"]), "Notifier": ("interface", [], ["send(user, msg)"]), "EmailNotifier": ([], []), "SmsNotifier": ([], []), "FakeNotifier (tests)": ([], [])},
      [["OrderService", "Notifier", "assoc"], ["EmailNotifier", "Notifier", "impl"], ["SmsNotifier", "Notifier", "impl"], ["FakeNotifier (tests)", "Notifier", "impl"]]),
     "Before: violates D", "After: follows D"))

X("uml",
  P("A UML class diagram shows classes (name / fields / methods) and **how they relate**. Interviewers mostly care about six relationships; the arrow style tells you which one, and the diagrams on this site use exactly these:"),
  UML("Every relationship type in one diagram", [["Car"], ["Engine", "Driver", "Vehicle"], ["Wheel", "Insurer", "Truck"]],
      {"Car": (["- engine: Engine", "- wheels: List<Wheel>", "- driver: Driver"], ["drive()", "insure(Insurer)"]), "Engine": ([], ["start()"]), "Driver": (["name"], []), "Vehicle": ("interface", [], ["drive()"]),
       "Wheel": (["size"], []), "Insurer": ([], ["quote(car)"]), "Truck": ([], ["drive()"])},
      [["Car", "Engine", "comp", "1"], ["Car", "Wheel", "agg", "4"], ["Car", "Driver", "assoc"], ["Car", "Vehicle", "impl"], ["Truck", "Vehicle", "impl"], ["Car", "Insurer", "dep"]]),
  TABLE("How to read the arrows", ["Relationship", "Arrow", "Meaning", "Car example", "In Java"],
        [["Inheritance (is-a)", "solid line, hollow triangle", "subclass extends parent", "Truck extends Vehicle", "`extends`"], ["Realisation", "dashed line, hollow triangle", "implements an interface", "Car implements Vehicle", "`implements`"],
         ["Composition (owns)", "filled diamond at the owner", "part dies with the whole", "Car owns its Engine", "field created inside the class"], ["Aggregation (has)", "hollow diamond at the owner", "part can live on its own", "Car has 4 Wheels", "field passed in / shared"],
         ["Association (knows)", "solid line, open arrow", "holds a reference", "Car knows its Driver", "field of that type"], ["Dependency (uses)", "dashed line, open arrow", "uses temporarily", "Car uses an Insurer in one method", "parameter / local variable"]]),
  KEY("In an interview, draw the 4–6 main classes, label relationships with multiplicity (1, 0..*, 1..*), mark interfaces, and skip getters/setters. A clear diagram in 5 minutes beats a perfect one in 20.", "Interview tip"))

X("creational-patterns",
  P("Creational patterns control **how objects get created**, so calling code doesn't depend on concrete classes or messy constructors."),
  UML("Factory Method: callers ask for a Notification by type", [["NotificationFactory"], ["Notification"], ["EmailNotification", "SmsNotification", "PushNotification"]],
      {"NotificationFactory": ([], ["create(type): Notification"]), "Notification": ("interface", [], ["send(to, msg)"]), "EmailNotification": ([], []), "SmsNotification": ([], []), "PushNotification": ([], [])},
      [["NotificationFactory", "Notification", "dep", "creates"], ["EmailNotification", "Notification", "impl"], ["SmsNotification", "Notification", "impl"], ["PushNotification", "Notification", "impl"]]),
  CODE("Builder: readable construction with many optional fields", """HttpRequest req = HttpRequest.builder()
        .url("https://api.example.com/orders")
        .method("POST")
        .header("Idempotency-Key", key)
        .timeout(Duration.ofSeconds(2))
        .build();                // validates required fields once, returns an immutable object"""),
  TABLE("The five creational patterns", ["Pattern", "Problem it solves", "Typical example"],
        [["Singleton", "exactly one instance, global access", "configuration, logger (prefer DI; beware hidden global state and testing pain)"], ["Factory Method", "choose the subclass to create at runtime", "`NotificationFactory.create(\"SMS\")`"],
         ["Abstract Factory", "create families of related objects that must match", "UI kit: `DarkThemeFactory` makes dark buttons + dark dialogs"], ["Builder", "many optional parameters, step-by-step, immutable result", "`HttpRequest.builder()`, `StringBuilder`"],
         ["Prototype", "copy an existing configured object instead of building from scratch", "clone a document template"]]),
  CODE("Thread-safe lazy Singleton (holder idiom)", """public final class Config {
    private Config() { /* load once */ }
    private static class Holder { static final Config INSTANCE = new Config(); }   // created on first access, JVM guarantees thread safety
    public static Config get() { return Holder.INSTANCE; }
}"""))

X("structural-patterns",
  P("Structural patterns are about **how classes and objects are composed**: wrapping, adapting and simplifying them without changing their code."),
  UML("Decorator: add behaviour by wrapping (same interface)", [["DataSource"], ["FileDataSource", "DataSourceDecorator"], ["EncryptionDecorator", "CompressionDecorator"]],
      {"DataSource": ("interface", [], ["write(data)", "read()"]), "FileDataSource": ([], ["write / read"]), "DataSourceDecorator": ("abstract", ["- inner: DataSource"], ["write → inner.write"]),
       "EncryptionDecorator": ([], ["write: encrypt then inner"]), "CompressionDecorator": ([], ["write: compress then inner"])},
      [["FileDataSource", "DataSource", "impl"], ["DataSourceDecorator", "DataSource", "impl"], ["DataSourceDecorator", "DataSource", "agg", "wraps"], ["EncryptionDecorator", "DataSourceDecorator", "inh"], ["CompressionDecorator", "DataSourceDecorator", "inh"]],
      "`new CompressionDecorator(new EncryptionDecorator(new FileDataSource(\"x\")))`: features stack in any order, chosen at runtime. Java I/O streams work this way."),
  UML("Adapter: make an incompatible class fit the interface you need", [["PaymentGateway"], ["RazorpayAdapter"], ["RazorpaySdk (3rd party)"]],
      {"PaymentGateway": ("interface", [], ["charge(paise, token)"]), "RazorpayAdapter": (["- sdk: RazorpaySdk"], ["charge(...) → sdk.createPayment(...)"]), "RazorpaySdk (3rd party)": ([], ["createPayment(json)"])},
      [["RazorpayAdapter", "PaymentGateway", "impl"], ["RazorpayAdapter", "RazorpaySdk (3rd party)", "assoc", "translates to"]]),
  TABLE("The seven structural patterns", ["Pattern", "In one line", "Example"],
        [["Adapter", "converts one interface into another", "wrap a vendor SDK behind your `PaymentGateway`"], ["Decorator", "adds responsibilities by wrapping", "`BufferedInputStream`, async log appender"],
         ["Facade", "one simple entry point to a complex subsystem", "`OrderFacade.placeOrder()` calls inventory, payment, shipping"], ["Proxy", "a stand-in that controls access", "lazy loading, caching, access checks, RPC stubs"],
         ["Composite", "treat a tree of objects like a single object", "folders containing files and folders (`size()` recurses)"], ["Bridge", "separate an abstraction from its implementation so both vary", "`Shape` × `Renderer` (vector/raster)"],
         ["Flyweight", "share common state among many small objects", "glyphs in a text editor, chess piece images"]]))

X("behavioral-patterns",
  P("Behavioural patterns are about **how objects communicate and divide responsibilities**. The three most asked in LLD rounds are Strategy, Observer and State; the diagrams below show each."),
  UML("Strategy: swap an algorithm at runtime", [["Navigator"], ["RouteStrategy"], ["FastestRoute", "ShortestRoute", "AvoidTolls"]],
      {"Navigator": (["- strategy: RouteStrategy"], ["setStrategy(s)", "route(a, b)"]), "RouteStrategy": ("interface", [], ["compute(a, b): Route"]), "FastestRoute": ([], []), "ShortestRoute": ([], []), "AvoidTolls": ([], [])},
      [["Navigator", "RouteStrategy", "assoc"], ["FastestRoute", "RouteStrategy", "impl"], ["ShortestRoute", "RouteStrategy", "impl"], ["AvoidTolls", "RouteStrategy", "impl"]]),
  SEQ("Observer: a subject notifies subscribers", ["Stock (subject)", "PriceAlert", "Dashboard", "Logger"],
      [["PriceAlert", "Stock (subject)", "subscribe(this)"], ["Dashboard", "Stock (subject)", "subscribe(this)"], ["Logger", "Stock (subject)", "subscribe(this)"],
       ["Stock (subject)", "Stock (subject)", "setPrice(1,415)"], ["Stock (subject)", "PriceAlert", "onChange(1,415)", "", "The subject only knows the Observer interface, not concrete classes."],
       ["Stock (subject)", "Dashboard", "onChange(1,415)"], ["Stock (subject)", "Logger", "onChange(1,415)"]]),
  STATE("State: behaviour depends on the current state object (document workflow)", [["Draft"], ["InReview"], ["Published", "Rejected"]],
        [["Draft", "InReview", "submit()"], ["InReview", "Published", "approve()"], ["InReview", "Rejected", "reject()"], ["Rejected", "Draft", "edit()"]],
        "Each state is a class implementing the same interface; `doc.approve()` in `Draft` throws, in `InReview` publishes."),
  TABLE("All ten behavioural patterns", ["Pattern", "In one line", "LLD example"],
        [["Strategy", "interchangeable algorithms behind one interface", "pricing, fee rules, routing"], ["Observer", "subscribers notified of changes", "price alerts, event listeners"], ["Command", "a request as an object (undo, queue, log)", "editor undo, job queue"],
         ["State", "behaviour changes with internal state", "vending machine, order life cycle"], ["Template Method", "fixed algorithm skeleton, subclasses fill steps", "`AbstractReportGenerator.generate()`"], ["Chain of Responsibility", "pass a request along handlers", "ATM note dispensing, middleware"],
         ["Iterator", "traverse without exposing internals", "`Iterator<T>`"], ["Mediator", "objects talk via a hub, not each other", "chat room, air-traffic control"], ["Memento", "save and restore state without breaking encapsulation", "editor snapshots"],
         ["Visitor", "add operations to a class hierarchy without editing it", "tax calculation over different product types"]]))

X("concurrency-java",
  P("Machine-coding rounds often add 'make it thread-safe'. The core problem is a **race condition**: two threads read-modify-write shared data and one update is lost. Below is the race, then the toolbox to fix it."),
  BA(SEQ("A lost update (balance = 100, two ₹50 deposits)", ["Thread 1", "Thread 2", "balance field"],
          [["Thread 1", "balance field", "read 100"], ["Thread 2", "balance field", "read 100", "", "Both read before either writes."], ["Thread 1", "balance field", "write 150"], ["Thread 2", "balance field", "write 150 ✘", "", "Should be 200: one deposit is lost."]]),
     SEQ("synchronized / AtomicLong makes read+write one step", ["Thread 1", "Thread 2", "balance field"],
          [["Thread 1", "balance field", "lock; read 100; write 150; unlock"], ["Thread 2", "balance field", "waits for the lock…"], ["Thread 2", "balance field", "lock; read 150; write 200; unlock ✔"]]),
     "Before: race condition", "After: synchronized"),
  TABLE("Choosing the tool", ["Need", "Tool", "Note"],
        [["protect a few lines", "`synchronized` / `ReentrantLock`", "lock has tryLock with timeout and fairness"], ["single counter / flag", "`AtomicLong`, `AtomicBoolean.compareAndSet`", "lock-free CAS"],
         ["shared map", "`ConcurrentHashMap` (`computeIfAbsent`, `merge`)", "atomic per-key operations"], ["many readers, few writers", "`ReadWriteLock` / `CopyOnWriteArrayList`", "readers don't block each other"],
         ["producer–consumer", "`BlockingQueue`", "put/take block when full/empty"], ["run tasks", "`ExecutorService`, `CompletableFuture`", "never create unbounded raw threads"],
         ["wait for N things", "`CountDownLatch`, `Semaphore`", "limit concurrent access with permits"], ["visibility of a flag", "`volatile`", "visibility only, not atomic read-modify-write"]]),
  BA(STATE("Deadlock: each thread holds one lock and waits for the other", [["T1 holds A"], ["T1 waits for B", "T2 holds B"], ["T2 waits for A"]],
          [["T1 holds A", "T1 waits for B"], ["T2 holds B", "T2 waits for A"], ["T1 waits for B", "T2 holds B", "blocked by"], ["T2 waits for A", "T1 holds A", "blocked by"]],
          "transfer(A→B) locks A then B; transfer(B→A) locks B then A."),
     SEQ("Lock ordering: both threads lock the lower account id first", ["Thread 1", "Lock A (id 1)", "Lock B (id 2)", "Thread 2"],
          [["Thread 1", "Lock A (id 1)", "lock A ✔"], ["Thread 2", "Lock A (id 1)", "lock A → waits (does NOT grab B first)"], ["Thread 1", "Lock B (id 2)", "lock B ✔, transfer, unlock both"], ["Thread 2", "Lock A (id 1)", "gets A, then B ✔", "", "No cycle is possible, so no deadlock. tryLock with a timeout is the other fix."]]),
     "Before: deadlock", "After: global lock order"),

  CODE("Deadlock-free transfer: lock in id order", """void transfer(Account a, Account b, long amt) {
    Account first = a.id < b.id ? a : b, second = a.id < b.id ? b : a;   // same order for every thread
    synchronized (first) { synchronized (second) {
        if (a.balance < amt) throw new IllegalStateException("insufficient");
        a.balance -= amt; b.balance += amt;
    } }
}"""))

X("lld-approach",
  P("A machine-coding round is 60–90 minutes: requirements → design → working code → extensions. Time management matters as much as patterns. Follow this timeline:"),
  BARS("Suggested time split for a 75-minute round", [("Clarify requirements & scope", 7, "5–8 min"), ("Identify entities & draw the class diagram", 10, "8–10 min"), ("Define interfaces / method signatures", 5, "5 min"),
                                                     ("Implement the core flow (happy path)", 30, "25–30 min"), ("Edge cases, validation, concurrency", 12, "10–12 min"), ("Demo in main(), explain extensions", 8, "5–8 min")]),
  FLOW("The method", [["1 Requirements: must-haves vs nice-to-haves"], ["2 Nouns → classes, verbs → methods"], ["3 Relationships + patterns (Strategy, State, Observer…)"], ["4 Code: models → services → main() demo"], ["5 Test edge cases, thread safety, extensions"]],
       [["1 Requirements: must-haves vs nice-to-haves", "2 Nouns → classes, verbs → methods"], ["2 Nouns → classes, verbs → methods", "3 Relationships + patterns (Strategy, State, Observer…)"],
        ["3 Relationships + patterns (Strategy, State, Observer…)", "4 Code: models → services → main() demo"], ["4 Code: models → services → main() demo", "5 Test edge cases, thread safety, extensions"]]),
  TABLE("What evaluators score", ["Area", "What good looks like"], [["working code", "runs end-to-end with a demo in main()"], ["modelling", "clear entities, no god class, enums for fixed types"], ["extensibility", "Strategy/State/Factory where rules vary"],
        ["correctness", "validation, edge cases, exceptions with clear messages"], ["concurrency", "atomic check-and-act where needed"], ["communication", "explain trade-offs as you go"]]),
  KEY("Every LLD question on this site follows the same structure: requirements, class diagram, sequence diagram of the main flow, patterns table, full Java, and real output. Practise by drawing the class diagram yourself before opening the solution.", "How to practise here"))

X("api-contract-lld",
  P("Inside a service, a clean design separates **what callers see** (API contract and DTOs) from **business rules** (services/domain) and **storage** (repositories). Each layer depends only on the one below through interfaces."),
  FLOW("Layered service", [["Controller (HTTP/JSON, validation)"], ["Service (business rules, transactions)"], ["Repository interface"], ["db:JPA / JDBC implementation"]],
       [["Controller (HTTP/JSON, validation)", "Service (business rules, transactions)", "DTO → domain"], ["Service (business rules, transactions)", "Repository interface"], ["Repository interface", "JPA / JDBC implementation", "implemented by"]]),
  TABLE("Contract checklist", ["Rule", "Example"], [["nouns in URLs, verbs as HTTP methods", "`POST /orders`, `GET /orders/{id}`"], ["DTOs separate from entities", "`CreateOrderRequest` ≠ `OrderEntity` (no leaking DB fields)"],
        ["validate at the edge", "`@NotNull`, ranges, formats → 400 with field errors"], ["idempotency for creates/payments", "`Idempotency-Key` header"], ["consistent errors", "`{code, message, details}`"], ["pagination", "cursor-based `?after=…&limit=50`"],
        ["versioning", "`/v1/…` or a header; never break existing clients"], ["immutable models", "records / final fields, builders for many options"]]),
  CODE("A clean slice in Java", """record CreateOrderRequest(@NotNull String userId, @NotEmpty List<Item> items) {}
record OrderResponse(String id, String status, long totalPaise) {}

interface OrderRepository { Order save(Order o); Optional<Order> find(String id); }

final class OrderService {
    private final OrderRepository repo; private final PricingStrategy pricing;
    OrderService(OrderRepository repo, PricingStrategy pricing) { this.repo = repo; this.pricing = pricing; }
    OrderResponse create(CreateOrderRequest r) {
        Order o = Order.create(r.userId(), r.items(), pricing);   // business rules live in the domain
        return OrderMapper.toResponse(repo.save(o));
    }
}"""))
