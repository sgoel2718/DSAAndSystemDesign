"""Theory interview questions: LLD & OOP concepts and LLD questions."""
from sd_iq_util import Q

Q("oop-pillars",
  ("B", "What are the four pillars of OOP?", "Encapsulation (hide state behind methods), abstraction (expose what, hide how), inheritance (reuse via is-a), polymorphism (one interface, many implementations)."),
  ("B", "Abstract class vs interface in Java?", "Abstract classes can hold state, constructors and partial implementations, single inheritance. Interfaces define a contract, support multiple implementation, and can have default/static methods but no instance state."),
  ("I", "Compile-time vs runtime polymorphism?", "Compile-time: method overloading resolved by signature. Runtime: overriding resolved by the object's actual type via dynamic dispatch."),
  ("I", "Composition vs inheritance: which do you prefer and why?", "Prefer composition (has-a) for flexibility and loose coupling; behaviour can be swapped at runtime and you avoid fragile base classes. Use inheritance for genuine is-a with substitutable behaviour."),
  ("I", "What is encapsulation's practical benefit?", "Invariants are enforced in one place (e.g., balance can't go negative), and internals can change without breaking callers."),
  ("A", "What is the fragile base class problem?", "Changes in a base class unexpectedly break subclasses that depend on its internal behaviour, because inheritance exposes implementation details."),
  ("A", "Why are immutable objects useful?", "Thread-safe without locks, safe to share and cache, easier to reason about; Java records and final fields help."))

Q("solid",
  ("B", "What does SOLID stand for?", "Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion."),
  ("I", "Explain the Single Responsibility Principle with an example.", "A class should have one reason to change: split an InvoiceService that calculates totals, saves to DB and prints PDFs into a calculator, a repository and a printer."),
  ("I", "How do you follow the Open/Closed Principle?", "Depend on abstractions and add behaviour by adding new implementations (strategy/plugins) instead of editing if/else chains."),
  ("I", "Give a Liskov Substitution violation.", "Square extends Rectangle: setting width changes height, breaking code that relies on independent width/height; or a subclass throwing UnsupportedOperationException for inherited methods."),
  ("I", "What is Interface Segregation?", "Clients shouldn't depend on methods they don't use; prefer several small interfaces (Printer, Scanner) to one fat interface."),
  ("I", "Dependency Inversion vs dependency injection?", "DIP is the principle (high-level modules depend on abstractions); DI is a technique to supply concrete implementations from outside (constructor injection, Spring)."),
  ("A", "Can following SOLID too strictly be harmful?", "Yes: excessive abstraction, too many tiny classes and interfaces with one implementation hurt readability. Apply where change is likely."))

Q("uml",
  ("B", "What does a UML class diagram show?", "Classes with attributes and methods, and relationships: inheritance, implementation, association, aggregation, composition and dependency."),
  ("I", "Aggregation vs composition?", "Both are has-a. Composition: the part's lifecycle is owned by the whole (Order and its OrderLines). Aggregation: parts exist independently (Team and Players)."),
  ("I", "Association vs dependency?", "Association: a lasting structural link (field). Dependency: temporary use, like a parameter or local variable."),
  ("I", "What diagrams are useful in an LLD interview besides class diagrams?", "Sequence diagrams for key flows, state diagrams for entities with life cycles (order, elevator), and occasionally activity diagrams."),
  ("A", "How do you show multiplicity and why does it matter?", "Numbers at association ends (1, 0..1, *, 1..*); they drive data structures (List vs single field) and DB relationships."))

Q("creational-patterns",
  ("B", "What problem do creational patterns solve?", "They abstract object creation so code doesn't depend on concrete classes or complex construction logic."),
  ("I", "When would you use the Builder pattern?", "When an object has many optional parameters or construction steps; gives readable, validated, immutable construction (Pizza.builder().size(L).topping(x).build())."),
  ("I", "Factory method vs abstract factory?", "Factory method creates one product, chosen by subclass or parameter. Abstract factory creates families of related products (light/dark theme widgets)."),
  ("I", "How do you implement a thread-safe singleton in Java?", "Enum singleton, a static holder class (lazy and thread-safe via class loading), or double-checked locking with a volatile field."),
  ("A", "Why is Singleton often considered an anti-pattern?", "Global state, hidden dependencies, hard to test/mock, and lifecycle issues; prefer dependency injection with a single instance."),
  ("A", "What is the Prototype pattern?", "Create objects by cloning a configured prototype, useful when construction is expensive or configuration-heavy."))

Q("structural-patterns",
  ("B", "What is the Adapter pattern?", "Wraps an incompatible interface (third-party SDK) to match the interface your code expects."),
  ("I", "Decorator vs inheritance for adding behaviour?", "Decorators wrap objects at runtime and can be stacked (logging + retry + caching) without a subclass explosion."),
  ("I", "What is a Facade?", "A simple interface over a complex subsystem (one checkout() call coordinating inventory, payment and email)."),
  ("I", "Proxy vs decorator?", "Both wrap; a proxy controls access (lazy loading, caching, security, remote), a decorator adds responsibilities."),
  ("A", "What is the Composite pattern and where is it used?", "Treat individual objects and groups uniformly via a common interface (file/folder trees, product bundles, UI components)."),
  ("A", "What is the Bridge pattern?", "Separate an abstraction from its implementation so both vary independently (Shape × Renderer), avoiding a class per combination."))

Q("behavioral-patterns",
  ("B", "What is the Strategy pattern?", "Encapsulate interchangeable algorithms behind an interface and choose at runtime (fare calculation, payment method, eviction policy)."),
  ("I", "What is the Observer pattern?", "Subjects notify registered observers of changes (event listeners, pub/sub, UI updates)."),
  ("I", "State pattern vs a switch on an enum?", "State objects encapsulate behaviour per state and transitions, avoiding large switches repeated across methods (vending machine, order lifecycle)."),
  ("I", "Where is Chain of Responsibility used?", "Middleware/filters (auth → rate limit → controller), approval chains, ATM note dispensing."),
  ("I", "What is the Command pattern?", "Represent an action as an object so it can be queued, logged, retried or undone (editor undo, job queues)."),
  ("A", "Template Method vs Strategy?", "Template Method fixes the algorithm skeleton in a base class with overridable steps (inheritance); Strategy swaps whole algorithms via composition."))

Q("concurrency-java",
  ("B", "What is a race condition?", "When the outcome depends on the interleaving of threads accessing shared data without synchronisation (lost updates)."),
  ("I", "synchronized vs ReentrantLock?", "synchronized is simpler and auto-releases; ReentrantLock adds tryLock with timeout, fairness, interruptible waits and multiple conditions."),
  ("I", "What does volatile guarantee?", "Visibility and ordering of reads/writes to that variable across threads, not atomicity of compound actions like count++."),
  ("I", "Why use ConcurrentHashMap instead of synchronized HashMap?", "Fine-grained concurrency with atomic per-key operations (computeIfAbsent, merge) and no global lock for reads."),
  ("I", "What are the four conditions for deadlock and how do you prevent it?", "Mutual exclusion, hold and wait, no preemption, circular wait. Prevent by global lock ordering, tryLock with timeouts, or reducing lock scope."),
  ("A", "How do you size a thread pool?", "CPU-bound: about the number of cores. I/O-bound: cores × (1 + wait time / compute time). Measure and use bounded queues."),
  ("A", "What are virtual threads and when do they help?", "Lightweight JVM-managed threads (Java 21) enabling thread-per-request for huge numbers of blocking I/O tasks; they don't speed up CPU-bound work."))

Q("lld-approach",
  ("B", "How should you start an LLD/machine-coding round?", "Clarify requirements and scope, list core entities and their responsibilities, then relationships, then interfaces and patterns, then code the main flow."),
  ("I", "What do interviewers evaluate in LLD?", "Clean OOP modelling, SOLID, appropriate patterns, extensibility, correctness of core flows, edge cases, thread safety when asked, and readable working code."),
  ("I", "How do you make a design extensible?", "Interfaces for variable behaviour (pricing, allocation, notification), dependency injection, avoiding hard-coded type checks, and keeping domain separate from I/O."),
  ("I", "How much should you code vs discuss?", "In machine coding, a working core in time matters most: model and code the main use cases, then discuss extensions verbally."),
  ("A", "How do you handle concurrency in an LLD solution?", "Identify shared mutable state (seats, spots, balances), protect with locks/atomic operations or single-threaded ownership, and explain lock ordering and contention."),
  ("A", "Common mistakes in LLD rounds?", "Jumping into code without requirements, God classes, overusing patterns, ignoring edge cases, no separation of concerns, and not leaving time to run/test."))

Q("api-contract-lld",
  ("B", "What makes a good service/API contract?", "Clear method names, typed request/response objects, explicit errors, validation, documented side effects and idempotency."),
  ("I", "Exceptions vs result objects for errors?", "Exceptions for unexpected failures; typed results/error codes for expected business outcomes (seat unavailable) so callers handle them explicitly."),
  ("I", "How do you make an API backward compatible?", "Only add optional fields/methods, don't change meanings or remove fields, version breaking changes, and deprecate gradually."),
  ("A", "How do you design for idempotency at the method level?", "Accept a client request id, store results by id, and return the stored result on retries."),
  ("A", "Why validate inputs at service boundaries even if the UI validates?", "Clients can be bypassed or buggy; boundaries enforce invariants and security."))

# ---------- LLD questions ----------
Q("parkinglot-lld",
  ("B", "What are the core entities of a parking lot design?", "ParkingLot, Floor, ParkingSpot (by type), Vehicle (by type), Ticket, Gate, FeeStrategy, Payment."),
  ("I", "How do you allocate spots efficiently?", "Maintain free spots per type (e.g., a min-heap or queue per floor/type) so allocation is O(log n) or O(1), with an allocation strategy interface (nearest, per-floor)."),
  ("I", "How do you support different pricing models?", "Strategy pattern: FeeStrategy implementations (hourly, flat, weekend), selected by configuration."),
  ("I", "How do you handle concurrency when two cars enter at the same time?", "Atomic spot assignment: lock per spot type pool or compare-and-set on spot status so one spot is never given twice."),
  ("A", "How would you extend it for EV charging spots and reservations?", "New SpotType with charger, a reservation entity with time window holds, and pricing including charging fees."),
  ("A", "How do you scale to many lots in a city?", "Each lot as a service instance with its own data; central availability aggregated via events; app queries nearest lots with availability."))

Q("lru-lld",
  ("B", "How do you implement an LRU cache with O(1) get and put?", "HashMap from key to node plus a doubly linked list ordered by recency; move to head on access, evict tail when full."),
  ("I", "Why a doubly linked list and not a singly linked one?", "Removing an arbitrary node in O(1) needs its previous pointer."),
  ("I", "How do you make it thread-safe?", "A lock around get/put (simple), or a ReadWriteLock; for high concurrency use segmented caches or libraries like Caffeine."),
  ("I", "How does LinkedHashMap help?", "With accessOrder=true and removeEldestEntry, it implements LRU directly."),
  ("A", "How would you add TTL per entry?", "Store expiry time in the node; treat expired entries as misses on access and clean lazily or with a background sweeper/priority queue."),
  ("A", "How would you turn it into LFU?", "Track frequency per key with buckets of doubly linked lists per frequency and a minFreq pointer for O(1) eviction."))

Q("elevator-lld",
  ("B", "What are the main entities of an elevator system?", "ElevatorController/Dispatcher, Elevator (car), Floor/requests (hall calls, car calls), Direction/State, Door, Display."),
  ("I", "How do you assign a hall call to an elevator?", "Strategy pattern: score elevators by distance, direction compatibility and load (nearest car moving towards the floor), pick the lowest cost."),
  ("I", "What scheduling algorithm does an elevator use?", "SCAN/LOOK: keep moving in one direction serving stops in order, then reverse; avoids starvation compared with nearest-first."),
  ("I", "How do you model elevator states?", "State machine: IDLE, MOVING_UP, MOVING_DOWN, DOORS_OPEN, MAINTENANCE with defined transitions."),
  ("A", "How do you handle concurrency of requests?", "Requests queued per elevator in thread-safe structures; a controller loop processes events; elevators run as separate threads or a simulated tick loop."),
  ("A", "How would you add peak-hour optimisation?", "Zone-based dispatch or parking idle cars at the lobby in the morning rush, via a swappable dispatch strategy."))

Q("vending-lld",
  ("B", "Which design pattern fits a vending machine?", "State pattern: Idle, HasMoney/HasSelection, Dispensing, OutOfStock, each handling insertCoin/select/dispense differently."),
  ("I", "How do you compute change?", "Greedy over denominations from largest to smallest with inventory limits; if exact change isn't possible, refuse the sale and return the money."),
  ("I", "How do you handle insufficient stock or funds?", "Validate in the current state; reject the selection or ask for more money, and allow cancel/refund at any time before dispensing."),
  ("A", "How do you make it thread-safe for concurrent API calls?", "Serialize operations (one transaction at a time) with a lock, since the machine is a single physical resource."),
  ("A", "How would you support card/UPI payments?", "Payment strategy interface (Cash, Card, UPI) with the state machine waiting for payment confirmation callbacks."))

Q("splitwise-lld",
  ("B", "What are the key entities in Splitwise?", "User, Group, Expense, Split (equal, exact, percentage), BalanceSheet."),
  ("I", "How do you support different split types?", "Strategy/subclass per split type with validation (percentages sum to 100, exact amounts sum to total)."),
  ("I", "How do you simplify debts?", "Compute net balance per user, then greedily match the largest creditor with the largest debtor until all are settled, minimising transactions."),
  ("A", "Why is debt simplification hard in general?", "Minimising the number of transactions exactly is NP-hard; greedy gives at most n−1 transactions which is good in practice."),
  ("A", "How do you avoid rounding errors when splitting?", "Use integer paise, distribute remainders deterministically (first k people pay one extra paisa)."))

Q("bookmyshow-lld",
  ("B", "What are the entities in a movie booking system?", "Movie, Theatre, Screen, Show, Seat, ShowSeat (seat state per show), Booking, Payment, User."),
  ("I", "How do you prevent double booking of seats?", "Temporarily lock seats per show (status HELD with expiry) using atomic updates or row locks; confirm to BOOKED after payment."),
  ("I", "What happens if payment fails or times out?", "Release held seats when the hold expires or payment fails, via a scheduler or lazy expiry checks."),
  ("A", "How do you handle a popular show with huge concurrency?", "Virtual waiting room, seat holds in Redis with TTL/atomic ops, rate limits, and async confirmation."),
  ("A", "How do you support dynamic pricing?", "PricingStrategy per show/seat category based on time, demand and seat type."))

Q("library-lld",
  ("B", "What entities does a library management system have?", "Book (title/ISBN), BookCopy/BookItem, Member, Loan, Reservation, Fine, Librarian."),
  ("I", "Why separate Book from BookCopy?", "A title can have many physical copies with independent status (available, borrowed, lost)."),
  ("I", "How do you implement reservations?", "A FIFO queue per book title; when a copy is returned, assign it to the next reservation and notify the member."),
  ("A", "How do you calculate fines flexibly?", "FinePolicy strategy (per day, capped, membership-based) applied on return."),
  ("A", "How do you enforce borrowing limits?", "Member type defines max loans and loan period; check active loans before issuing."))

Q("snakeladder-lld",
  ("B", "How do you model the board?", "A board of N cells with a map from start → end for snakes and ladders, players with positions, and a dice abstraction."),
  ("I", "How do you make the dice testable?", "Inject a Dice interface so tests can use a fixed sequence instead of randomness."),
  ("I", "How do you handle exceeding the last cell?", "Configurable rule: stay in place or bounce back; encapsulate in the game rules."),
  ("A", "How would you validate the board?", "No cycles between snakes and ladders, no snake/ladder starting at the same cell or at the final cell."),
  ("A", "How do you support multiple dice or special rules?", "Strategy for movement rules and composable dice; open/closed for new rules."))

Q("tictactoe-lld",
  ("B", "How do you represent the board?", "A 2-D array or array of cells, players with symbols, and a game state (in progress, win, draw)."),
  ("I", "How do you check a win in O(1) per move?", "Keep counters for each row, column and the two diagonals: +1 for X, −1 for O; a counter reaching ±n means a win."),
  ("I", "How do you generalise to N×N and K in a row?", "Parameterise board size and check K consecutive cells in four directions from the last move."),
  ("A", "How would you add an AI player?", "Player interface with Human and AI implementations; AI uses minimax with alpha-beta pruning for small boards."),
  ("A", "How do you support undo?", "Command pattern storing moves, reverting board and counters."))

Q("ratelimiter-lld",
  ("B", "Which algorithms can you implement for an in-process rate limiter?", "Token bucket, leaky bucket, fixed window, sliding window log, sliding window counter."),
  ("I", "How do you design for multiple algorithms and per-user limits?", "RateLimiter interface with algorithm implementations, a factory/config per client tier, and a map of client id → limiter."),
  ("I", "How do you make the token bucket thread-safe?", "Synchronise refill+consume, or use atomic CAS on a combined state; avoid a background refill thread by computing tokens lazily from elapsed time."),
  ("A", "How do you prevent memory from growing with many clients?", "Evict idle limiters (LRU/TTL map)."),
  ("A", "How would you make it distributed?", "Move state to Redis with atomic Lua scripts, or use local limits per node as an approximation."))

Q("atm-lld",
  ("B", "What are the main ATM components?", "ATM, CardReader, Keypad, CashDispenser, Bank/Account service, Transaction types, and states."),
  ("I", "Which patterns apply?", "State (Idle, CardInserted, Authenticated, Dispensing), Chain of Responsibility for note dispensing, Strategy/Command for transaction types."),
  ("I", "How do you dispense cash with available notes?", "Chain of note handlers from highest denomination down, each dispensing as many as possible; verify the full amount can be met before dispensing."),
  ("A", "How do you keep the bank balance and cash dispensed consistent?", "Debit via the bank in a transaction, dispense, then confirm; if dispensing fails, reverse the debit (compensation) and log for reconciliation."),
  ("A", "How do you handle PIN security?", "Never store PINs; send them encrypted to the bank, limit attempts and lock/retain the card."))

Q("logger-lld",
  ("B", "What are the key components of a logging framework?", "Logger, log levels, Appenders/sinks (console, file, remote), Formatter/Layout, configuration."),
  ("I", "Which patterns are used?", "Chain of Responsibility or level filtering, Observer/composite for multiple appenders, Strategy for formatters, Singleton/factory for logger instances."),
  ("I", "How do you make logging non-blocking?", "Async appenders: enqueue log events into a bounded queue processed by a background thread."),
  ("A", "What happens when the async queue is full?", "Choose a policy: block, drop lowest-level logs, or drop newest; never let logging take down the app."),
  ("A", "How do you support structured logging and context?", "Key-value fields and MDC/thread-local context (request id, user id) added to every event."))

Q("pubsub-lld",
  ("B", "What are the entities in a pub/sub system?", "Topic, Publisher, Subscriber, Message, Broker managing subscriptions and delivery."),
  ("I", "How do you deliver messages to subscribers without blocking publishers?", "Per-subscriber queues and worker threads; publishing only enqueues."),
  ("I", "How do you support a slow subscriber?", "Bounded per-subscriber queues with backpressure/drop policies and offsets so others aren't affected."),
  ("A", "How do you add at-least-once delivery and replay?", "Persist messages in an append-only log per topic and track subscriber offsets; redeliver after failures."),
  ("A", "How do you support message filtering?", "Subscriptions with predicates or topic hierarchies/wildcards evaluated before delivery."))

Q("taskscheduler-lld",
  ("B", "How do you schedule tasks to run at future times?", "A priority queue (or DelayQueue) ordered by next run time, with worker threads taking due tasks."),
  ("I", "How do you support recurring tasks?", "After execution, compute the next run time (fixed rate vs fixed delay) and re-enqueue."),
  ("I", "Fixed rate vs fixed delay?", "Fixed rate schedules relative to start times (may overlap/catch up); fixed delay waits a delay after each run finishes."),
  ("A", "How do you cancel a scheduled task?", "Keep a handle/flag; remove from the queue or skip when popped if cancelled."),
  ("A", "How would you make it survive restarts?", "Persist tasks and next-run times in a database and reload on startup; use leases for multiple scheduler instances."))

Q("kvstore-lld",
  ("B", "What operations should an in-memory key-value store support?", "get, put, delete, often with TTL and maybe transactions (begin/commit/rollback)."),
  ("I", "How do you implement transactions with rollback?", "Keep a stack of change logs per open transaction; on rollback restore previous values; on commit merge into the parent."),
  ("I", "How do you implement TTL?", "Store expiry per key; lazy expiration on access plus periodic sampling cleanup."),
  ("A", "How do you make it durable?", "Append-only log of writes (and periodic snapshots); replay on startup."),
  ("A", "How do you make it thread-safe with good performance?", "ConcurrentHashMap with atomic operations, or striped locks; transactions need isolation via locks or MVCC."))

Q("shoppingcart-lld",
  ("B", "What are the main entities of a shopping cart?", "Cart, CartItem, Product, Inventory, Discount/Coupon, PricingService, Checkout/Order."),
  ("I", "How do you apply multiple discounts?", "A list of Discount strategies applied in a defined order with stacking rules and caps."),
  ("I", "Where should price calculation live?", "In a pricing service/calculator, not in Cart, so pricing rules change independently (SRP)."),
  ("A", "How do you handle a price change between adding to cart and checkout?", "Re-price at checkout and show the change; keep price snapshot only after order placement."),
  ("A", "How do you ensure inventory at checkout?", "Reserve stock atomically during checkout with expiry, release on failure."))

Q("filesystem-lld",
  ("B", "Which pattern models files and directories?", "Composite: File and Directory share a common interface (name, size), and directories contain children."),
  ("I", "How do you implement path resolution like /home/a/b.txt?", "Split by '/', walk from the root through child maps, and handle '.' and '..'."),
  ("I", "How do you compute a directory's size?", "Recursively sum children (or cache sizes and update on changes)."),
  ("A", "How would you add permissions?", "Owner/group/mode bits or ACLs on each node checked on operations."),
  ("A", "How would you implement search by name pattern?", "DFS/BFS traversal with a filter strategy (name, extension, size)."))

Q("ridesharing-lld",
  ("B", "What entities does a ride-sharing LLD need?", "Rider, Driver, Vehicle, Location, Ride/Trip with states, MatchingStrategy, PricingStrategy, Payment."),
  ("I", "How do you match riders to drivers?", "A strategy that finds nearby available drivers (distance/ETA) and offers the ride; accept/decline with timeouts."),
  ("I", "How do you model a trip's life cycle?", "State machine: REQUESTED → ACCEPTED → ARRIVED → IN_PROGRESS → COMPLETED/CANCELLED."),
  ("A", "How do you prevent one driver being assigned two rides?", "Atomically mark the driver busy (compare-and-set on status) when they accept."),
  ("A", "How do you support surge pricing?", "PricingStrategy using demand/supply per area; computed when the ride is quoted."))

Q("notification-lld",
  ("B", "What are the key classes of a notification service?", "Notification, Channel (email/SMS/push) implementations, Template, UserPreferences, NotificationService, retry policy."),
  ("I", "Which patterns are used?", "Strategy/Factory for channels, Template method or template engine for content, Observer for events, Decorator for retries/logging."),
  ("I", "How do you add a new channel without changing existing code?", "Implement the Channel interface and register it (Open/Closed)."),
  ("A", "How do you handle retries and failures?", "Retry policy with backoff per channel, fallback channel, and dead-letter storage."),
  ("A", "How do you respect user preferences?", "Check preferences and quiet hours before dispatch; per-user channel opt-outs."))

Q("chess-lld",
  ("B", "How do you model chess pieces?", "Abstract Piece with color and a method for legal moves; subclasses for King, Queen, Rook, Bishop, Knight, Pawn."),
  ("I", "How do you validate a move?", "Check the piece's movement rules, path obstruction, destination occupancy, and that the move doesn't leave your king in check."),
  ("I", "How do you detect check and checkmate?", "Check: any opponent move attacks the king. Checkmate: in check and no legal move removes it."),
  ("A", "How do you handle special moves?", "Castling, en passant and promotion as special cases tracked by move history and piece state."),
  ("A", "How do you support undo and game replay?", "Store moves (Command pattern) with captured pieces and state to revert."))

Q("meetingroom-lld",
  ("B", "What entities are in a meeting room booking system?", "Room (capacity, features), Booking (time interval), User, Scheduler/BookingService."),
  ("I", "How do you check availability quickly?", "Keep bookings per room sorted by start time (TreeMap) and check neighbours for overlap in O(log n)."),
  ("I", "How do you find any free room for a time slot?", "Filter rooms by capacity/features and check each room's availability; pick by a strategy (smallest fitting room)."),
  ("A", "How do you prevent double booking under concurrency?", "Lock per room or atomic insert with overlap check in a transaction."),
  ("A", "How do you support recurring meetings?", "Store a recurrence rule and expand instances for conflict checking within a horizon."))

Q("carrental-lld",
  ("B", "What are the main entities of a car rental system?", "Vehicle (types), Branch/Location, Reservation, Customer, Invoice, Add-ons, PricingStrategy."),
  ("I", "How do you check vehicle availability for date ranges?", "Per vehicle, check reservations for overlap; index by type and branch for searches."),
  ("I", "How do you compute the bill?", "Pricing strategy per vehicle type × days + add-ons + late fees + taxes."),
  ("A", "How do you handle concurrency on the last car?", "Atomic reservation with overlap check in a transaction or per-vehicle lock."),
  ("A", "How do you support one-way rentals?", "Allow different pickup/drop branches with relocation fees and update vehicle location on return."))

Q("stackoverflow-lld",
  ("B", "What are the entities in a Q&A site like Stack Overflow?", "User, Question, Answer, Comment, Vote, Tag, Reputation, Badge."),
  ("I", "How do you implement voting and reputation?", "Vote entity per user per post (one vote, changeable); reputation changes computed by rules on vote events."),
  ("I", "How do you prevent a user voting twice?", "Unique (user, post) vote record; changing a vote updates it and adjusts reputation by the difference."),
  ("A", "How do you implement search by tags and text?", "Inverted index (search engine) plus tag indexes; rank by votes and recency."),
  ("A", "Which patterns apply?", "Observer for notifications/badges on events, Strategy for reputation rules, Composite-like structure for posts and comments."))
