"""Detailed explanations with diagrams: Databases & Storage tab."""
from sd_x_util import X, P, H, AN, KEY, FLOW, SEQ, NOTE, ER, TABLE, CALC, BARS, CODE, UML, STATE, BA

X("sql-vs-nosql",
  P("The same e-commerce order stored two ways. **SQL** normalises into related tables joined at read time; a **document** store keeps everything the page needs in one record."),
  ER("Relational model", [("customers", "SQL", [("id", "bigint", "PK"), ("name", "text", ""), ("email", "text", "UQ")], ""),
                          ("orders", "SQL", [("id", "bigint", "PK"), ("customer_id", "bigint", "FK"), ("status", "text", ""), ("created_at", "timestamp", "")], ""),
                          ("order_items", "SQL", [("order_id", "bigint", "FK"), ("product_id", "bigint", "FK"), ("qty", "int", ""), ("price", "numeric", "")], "")],
     [("customers", "orders", "1 : N"), ("orders", "order_items", "1 : N")]),
  CODE("Document model (MongoDB)", """{ "_id": 987, "status": "PAID",
  "customer": { "id": 42, "name": "Asha" },          // copied in (denormalised)
  "items": [ { "product": "Shoes", "qty": 1, "price": 2499 },
             { "product": "Socks", "qty": 3, "price": 199 } ] }""", "json"),
  TABLE("How to choose", ["Pick SQL when", "Pick NoSQL when"], [["data is relational with many joins", "access patterns are simple and known (get by key)"], ["you need transactions across rows/tables", "you need massive write scale / horizontal partitioning built in"],
        ["schema is stable, integrity constraints matter", "schema varies per record"], ["ad-hoc queries and reporting", "very low latency at huge scale (Cassandra, DynamoDB)"]]),
  KEY("Default to PostgreSQL unless a concrete requirement (write volume, data shape, latency at scale) says otherwise; many 'NoSQL' needs are met by Postgres JSONB + read replicas + sharding later.", "Interview default"))

X("acid",
  P("Transfer ₹500 from Asha to Ravi. ACID guarantees this behaves as one indivisible, correct, isolated and permanent operation."),
  CODE("The transaction", """BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 'asha';   -- 1000 → 500
UPDATE accounts SET balance = balance + 500 WHERE id = 'ravi';   --  200 → 700
COMMIT;""", "sql"),
  TABLE("What each letter protects against", ["Letter", "Guarantee", "Failure it prevents"], [["Atomicity", "all statements or none", "crash after the debit: ₹500 vanishes"], ["Consistency", "constraints hold (balance ≥ 0, FKs)", "overdraft to −300"],
        ["Isolation", "concurrent transactions don't see each other's half-done work", "a report reads Asha debited but Ravi not yet credited"], ["Durability", "after COMMIT, survives a crash", "power cut loses a committed transfer"]]),
  SEQ("How durability and atomicity work: the write-ahead log", ["Transaction", "WAL (on disk)", "Data pages (memory)"],
      [["Transaction", "WAL (on disk)", "append: debit asha 500, credit ravi 500"], ["Transaction", "Data pages (memory)", "modify pages in memory"], ["Transaction", "WAL (on disk)", "append COMMIT + fsync", "", "COMMIT returns only after the log is on disk."],
       NOTE(["Transaction", "Data pages (memory)"], "crash here → on restart, replay committed WAL entries; discard uncommitted ones")]))

X("isolation-levels",
  P("Two transactions run at the same time on `accounts(asha: 1000)`. Each isolation level allows or prevents different anomalies:"),
  BA(SEQ("Lost update: read-modify-write in two transactions", ["Txn A", "Database", "Txn B"],
          [["Txn A", "Database", "read balance → 1000"], ["Txn B", "Database", "read balance → 1000"], ["Txn A", "Database", "write 1000 − 300 = 700; commit"], ["Txn B", "Database", "write 1000 − 200 = 800; commit", "", "A's withdrawal is lost: the final balance should be 500."]]),
     SEQ("Atomic update (or row lock / version check)", ["Txn A", "Database", "Txn B"],
          [["Txn A", "Database", "UPDATE … SET balance = balance − 300 (row locked)"], ["Txn B", "Database", "UPDATE … SET balance = balance − 200 (waits for the lock)"], ["Txn A", "Database", "commit → 700"],
           ["Txn B", "Database", "now runs on 700 → 500; commit", "", "Same fix via SELECT … FOR UPDATE, or optimistic: UPDATE … WHERE version = 7 and retry if 0 rows changed."]]),
     "Before: lost update", "After: atomic / locked update"),
  TABLE("Anomalies by isolation level", ["Level", "Dirty read", "Non-repeatable read", "Phantom read", "Write skew"],
        [["Read uncommitted", "possible", "possible", "possible", "possible"], ["Read committed (Postgres default)", "✔ prevented", "possible", "possible", "possible"], ["Repeatable read / snapshot (MySQL default)", "✔", "✔", "mostly ✔", "possible"],
         ["Serializable", "✔", "✔", "✔", "✔"]]),
  TABLE("The anomalies in one line each", ["Anomaly", "Example"], [["dirty read", "you see a transfer that later rolls back"], ["non-repeatable read", "same SELECT twice in one txn gives different balances"], ["phantom", "COUNT(*) of today's bookings changes mid-transaction"],
        ["write skew", "two doctors both check 'another doctor is on call' and both go off call"]]))

X("indexes",
  P("Without an index, `SELECT * FROM users WHERE email = 'asha@x.com'` reads every row. A **B+ tree** index keeps keys sorted in a shallow tree, so lookups take a few page reads."),
  FLOW("B+ tree on email (fan-out ~100s per node in reality)", [["Root: [g | p]"], ["Internal: [b | d]", "Internal: [k | m]", "Internal: [s | v]"], ["Leaf: asha@… → row 17", "Leaf: kiran@… → row 3", "Leaf: zoya@… → row 41"]],
       [["Root: [g | p]", "Internal: [b | d]", "< g"], ["Root: [g | p]", "Internal: [k | m]", "g – p"], ["Root: [g | p]", "Internal: [s | v]", "≥ p"], ["Internal: [b | d]", "Leaf: asha@… → row 17"], ["Internal: [k | m]", "Leaf: kiran@… → row 3"], ["Internal: [s | v]", "Leaf: zoya@… → row 41"]],
       "Leaves are linked left-to-right, so range scans (`WHERE created_at BETWEEN …`) walk sideways."),
  BA(CALC("No index: full table scan", [("Rows", "n = 1e9", ""), ("Pages read (100 rows per page)", "n / 100", "pages"), ("At ~100 µs per page read", "n / 100 * 100e-6 / 60", "minutes")]),
     CALC("B+ tree index on email", [("Keys per page (fan-out)", "f = 500", ""), ("Tree height = log base f of 1e9", "math.log(1e9) / math.log(f)", "levels", "≈ 4 page reads, top levels usually cached"), ("Lookup time", "4 * 100e-6 * 1000", "ms")]),
     "Before: full scan", "After: indexed lookup"),
  TABLE("Composite index (country, city, age): which queries use it?", ["Query WHERE …", "Uses index?", "Why"], [["country = 'IN'", "✔", "leftmost prefix"], ["country = 'IN' AND city = 'Pune'", "✔", "prefix"], ["city = 'Pune'", "✘", "skips the first column"],
        ["country = 'IN' AND age > 30", "partly", "uses country; age not contiguous without city"], ["country = 'IN' AND city = 'Pune' ORDER BY age", "✔ incl. sort", "matches order"]]),
  KEY("Indexes speed reads but slow every write (each index must be updated) and use disk. Index columns used in WHERE/JOIN/ORDER BY with high selectivity; check with EXPLAIN.", "Trade-off"))

X("storage-engines",
  FLOW("LSM tree write and read path", [["Write"], ["WAL (append) + MemTable (sorted, memory)"], ["Flush → SSTable L0 (immutable file)"], ["Compaction → L1, L2 … (merged, sorted)"]],
       [["Write", "WAL (append) + MemTable (sorted, memory)"], ["WAL (append) + MemTable (sorted, memory)", "Flush → SSTable L0 (immutable file)", "when full"], ["Flush → SSTable L0 (immutable file)", "Compaction → L1, L2 … (merged, sorted)", "background"]],
       "Read: check MemTable, then each level newest first; a Bloom filter per SSTable skips files that can't contain the key."),
  TABLE("B-tree vs LSM tree", ["", "B-tree (Postgres, MySQL InnoDB)", "LSM (Cassandra, RocksDB, HBase)"], [["write", "update page in place (random I/O)", "append + sequential flush (fast)"], ["read", "one tree walk (fast, predictable)", "may check several files"],
        ["space", "some fragmentation", "compaction overhead, but compresses well"], ["best for", "read-heavy, transactional", "write-heavy (logs, time series, messaging)"]]),
  TABLE("Amplification trade-offs", ["Type", "Meaning", "Worse in"], [["write amplification", "bytes written to disk per byte of data", "LSM (compaction rewrites data)"], ["read amplification", "disk reads per lookup", "LSM"], ["space amplification", "disk used per byte of live data", "LSM (old versions until compaction)"]]))

X("nosql-types",
  TABLE("The four NoSQL families", ["Type", "Data looks like", "Query by", "Examples", "Use for"],
        [["Key-value", "session:abc → {…}", "key only", "Redis, DynamoDB", "caching, sessions, carts"], ["Document", "{_id, name, address:{…}, tags:[…]}", "key + fields (indexes)", "MongoDB, Firestore", "catalogs, user profiles, CMS"],
         ["Wide-column", "partition key → sorted rows of columns", "partition key + clustering range", "Cassandra, HBase, Bigtable", "time series, messages, huge write volumes"], ["Graph", "nodes + edges with properties", "traversals", "Neo4j, Neptune", "social graphs, fraud rings, recommendations"]]),
  CODE("Wide-column: chat messages modelled for the query 'latest messages in a conversation'", """CREATE TABLE messages (
  conversation_id uuid,
  message_ts      timeuuid,
  sender_id       bigint,
  body            text,
  PRIMARY KEY ((conversation_id), message_ts)   -- partition key, clustering column
) WITH CLUSTERING ORDER BY (message_ts DESC);""", "sql"),
  KEY("In NoSQL you design tables **from the queries backwards**: one table per access pattern, denormalised, because there are no joins.", "Modelling rule"))

X("normalization",
  BA(TABLE("Unnormalised orders table: repeated data", ["order_id", "customer", "customer_city", "product", "price"],
        [["1", "Asha", "Pune", "Shoes", "2499"], ["2", "Asha", "Pune", "Socks", "199"], ["3", "Ravi", "Delhi", "Shoes", "2499"]], "If Asha moves, you must update many rows (update anomaly); delete order 3 and you lose that Ravi lives in Delhi (delete anomaly)."),
  ER("Normalised (3NF)", [("customers", "SQL", [("id", "int", "PK"), ("name", "text", ""), ("city", "text", "")], ""), ("products", "SQL", [("id", "int", "PK"), ("name", "text", ""), ("price", "numeric", "")], ""),
                          ("orders", "SQL", [("id", "int", "PK"), ("customer_id", "int", "FK"), ("product_id", "int", "FK")], "")], [("customers", "orders", "1 : N"), ("products", "orders", "1 : N")]),
     "Before: unnormalised table", "After: normalised (3NF)"),
  TABLE("Normalise vs denormalise", ["", "Normalised", "Denormalised"], [["writes", "update one place", "update every copy"], ["reads", "joins needed", "one lookup"], ["used in", "OLTP systems of record", "read-heavy views, NoSQL, analytics (star schema), caches"]]))

X("replication",
  BA(SEQ("Async replication: the user reads a stale replica", ["App", "Leader", "Follower 1", "Follower 2"],
          [["App", "Leader", "UPDATE profile SET bio = 'hi'"], ["Leader", "App", "OK", "r", "Async: the leader confirms before followers have the change."], ["Leader", "Follower 1", "stream WAL entry", "a"], ["Leader", "Follower 2", "stream WAL entry (lagging 2 s)", "a"],
           ["App", "Follower 2", "read profile → old bio", "", "The user doesn't see their own edit and thinks it failed."]]),
     SEQ("Read-your-writes routing", ["App", "Leader", "Follower 2"],
          [["App", "Leader", "UPDATE profile (returns WAL position 8812)"], ["App", "Follower 2", "read, but only if you've applied ≥ 8812"], ["Follower 2", "App", "not yet (at 8790)", "r"],
           ["App", "Leader", "read from the leader instead"], ["Leader", "App", "new bio ✔", "r", "Simpler variant: send a user's reads to the leader for ~10 s after they write."]]),
     "Before: stale read after write", "After: read-your-writes"),
  TABLE("Sync vs async vs semi-sync", ["Mode", "Commit waits for", "Data loss on leader crash", "Latency"], [["Synchronous", "all followers", "none", "highest; one slow follower stalls writes"], ["Semi-sync", "≥ 1 follower", "none (if that follower survives)", "medium"], ["Asynchronous", "nobody", "last few seconds of writes", "lowest"]]),
  TABLE("Topologies", ["Topology", "Writes go to", "Hard part"], [["Single leader", "one node", "failover; leader is the write bottleneck"], ["Multi-leader", "a leader per region", "write conflicts (last-write-wins, CRDTs)"], ["Leaderless (Dynamo, Cassandra)", "any N replicas with quorum", "read repair, sloppy quorums, conflicts"]]))

X("sharding",
  P("Sharding splits one big table across many databases so each holds a slice. The **shard key** decides where each row lives, and it decides almost everything else too."),
  TABLE("Range vs hash sharding of users by user_id", ["Strategy", "Rule", "user 1,005", "user 5,000,123", "Strength", "Weakness"],
        [["Range", "shard 0: ids 0–1M, shard 1: 1M–2M …", "shard 0", "shard 5", "range scans", "hotspot on newest range"], ["Hash", "shard = hash(id) % 4", "shard 2", "shard 1", "even spread", "range queries hit all shards; resharding moves data"],
         ["Directory", "lookup table id → shard", "any", "any", "flexible moves", "lookup service is critical"]]),
  BA(FLOW("One database holds everything", [["u:App servers"], ["db:Single primary: 8 TB, 40k writes/s (limit ~10k)"]], [["App servers", "Single primary: 8 TB, 40k writes/s (limit ~10k)", "every read and write"]],
          "Disk, write throughput and backups have outgrown one machine; vertical scaling is exhausted."),
     FLOW("Routing a query", [["u:App"], ["Shard router (hash(user_id) % 4)"], ["db:Shard 0", "db:Shard 1", "db:Shard 2", "db:Shard 3"]],
       [["App", "Shard router (hash(user_id) % 4)", "user 1005"], ["Shard router (hash(user_id) % 4)", "Shard 2", "single-shard query"], ["Shard router (hash(user_id) % 4)", "Shard 0"], ["Shard router (hash(user_id) % 4)", "Shard 1"], ["Shard router (hash(user_id) % 4)", "Shard 3"]]),
     "Before: one database", "After: sharded by user_id"),
  TABLE("What sharding costs you", ["Problem", "Mitigation"], [["cross-shard joins", "denormalise; co-locate related data with the same key (user + their orders)"], ["cross-shard transactions", "sagas or avoid by key choice"], ["hot shard (celebrity)", "split key, add salt"], ["resharding", "consistent hashing / many virtual shards mapped to fewer machines"], ["global unique ids", "Snowflake ids"]]))

X("consistent-hashing",
  P("With `hash(key) % N`, changing N from 4 to 5 remaps ~80% of keys. **Consistent hashing** places servers and keys on a ring; a key belongs to the next server clockwise, so adding a server moves only the keys in one arc."),
  CALC("Keys that move when going from 4 to 5 servers (1 M keys)", [("Keys", "k = 1e6", ""), ("Modulo hashing moves ≈ 1 − 1/5 of keys", "k * (1 - 1/5)", "", "4 out of 5 keys change server"), ("Consistent hashing moves ≈ 1/5 of keys", "k / 5", "", "only the arc the new server takes over")]),
  BA(TABLE("Ring with servers A, B, C (positions 0–359°)", ["Item", "Hash position", "Owner (next server clockwise)"], [["Server A", "40°", ""], ["Server B", "150°", ""], ["Server C", "270°", ""], ["key 'user:7'", "95°", "B"], ["key 'user:9'", "200°", "C"], ["key 'cart:3'", "300°", "A (wraps around)"]]),
     TABLE("Same ring after adding server D at 230°", ["Item", "Hash position", "Owner"], [["Server A", "40°", ""], ["Server B", "150°", ""], ["Server D (new)", "230°", ""], ["Server C", "270°", ""], ["key 'user:7'", "95°", "B (unchanged)"], ["key 'user:9'", "200°", "D (moved from C)"], ["key 'cart:3'", "300°", "A (unchanged)"]],
           "Only keys between 150° and 230° move, and only to D; nothing else is reshuffled."),
     "Before: 3 servers", "After: server D added"),
  KEY("Each physical server gets ~100–200 **virtual nodes** at different ring positions, which evens out the load and spreads a dead server's keys across all survivors instead of one neighbour. Used by DynamoDB, Cassandra, CDNs, memcached clients.", "Virtual nodes"))

X("db-scaling-path",
  FLOW("Scale a database step by step: do the cheap thing first", [["1 · Optimise queries + indexes"], ["2 · Vertical scale (bigger box)"], ["3 · Cache hot reads (Redis)"], ["4 · Read replicas"], ["5 · Split by feature (users DB, orders DB)"], ["6 · Shard the biggest table"]],
       [["1 · Optimise queries + indexes", "2 · Vertical scale (bigger box)"], ["2 · Vertical scale (bigger box)", "3 · Cache hot reads (Redis)"], ["3 · Cache hot reads (Redis)", "4 · Read replicas"], ["4 · Read replicas", "5 · Split by feature (users DB, orders DB)"], ["5 · Split by feature (users DB, orders DB)", "6 · Shard the biggest table"]]),
  TABLE("Signal → step", ["You see", "Do"], [["a few slow queries", "EXPLAIN, add indexes, fix N+1"], ["CPU/RAM maxed, < few TB", "bigger instance"], ["same reads repeated", "cache"], ["read QPS high, writes fine", "replicas"], ["one service's tables dominate", "separate databases"], ["write QPS or size beyond one node", "shard (or a distributed SQL DB)"]]))

X("connection-pooling",
  BA(CALC("A connection per thread", [("App servers", "a = 50", ""), ("Threads per server, each with its own connection", "t = 100", ""), ("Connections opened against Postgres", "a * t", "", "Postgres uses a process per connection: ~10 MB each"), ("Memory for connections", "a * t * 10e6", "B", "plus a TCP + TLS + auth handshake for every new one")]),
     CALC("Pool per app server + PgBouncer", [("Pool size per app server", "p = 10", ""), ("Client connections (50 servers)", "50 * p", ""), ("Real DB connections behind PgBouncer", "c = 200", "", "client connections multiplexed onto 200"), ("Memory for connections", "c * 10e6", "B")]),
     "Before: unpooled", "After: pooled"),
  SEQ("Borrow and return", ["Request thread", "Pool (HikariCP)", "Database"],
      [["Request thread", "Pool (HikariCP)", "getConnection()"], ["Pool (HikariCP)", "Request thread", "an idle, already-open connection (µs)", "r", "No TCP + TLS + auth handshake per request (would be ms)."], ["Request thread", "Database", "query"],
       ["Request thread", "Pool (HikariCP)", "close() → returned to pool"], NOTE(["Request thread", "Pool (HikariCP)"], "pool empty → wait up to connectionTimeout, then fail fast")]),
  KEY("Size pools small: roughly cores × 2 per DB is often optimal; a bigger pool just moves the queue into the database. Use PgBouncer/RDS Proxy when many app instances (or serverless functions) connect.", "Sizing rule"))

X("distributed-transactions",
  SEQ("Two-phase commit (2PC)", ["Coordinator", "Orders DB", "Payments DB"],
      [["Coordinator", "Orders DB", "PREPARE"], ["Coordinator", "Payments DB", "PREPARE"], ["Orders DB", "Coordinator", "YES (locked, ready)", "r"], ["Payments DB", "Coordinator", "YES", "r"],
       ["Coordinator", "Orders DB", "COMMIT"], ["Coordinator", "Payments DB", "COMMIT", "", "If the coordinator crashes after PREPARE, participants hold locks and wait: 2PC is blocking."]]),
  SEQ("Saga (orchestrated) with compensation", ["Order saga", "Orders", "Payments", "Inventory"],
      [["Order saga", "Orders", "create order (PENDING)"], ["Order saga", "Payments", "charge ₹2,499"], ["Payments", "Order saga", "charged", "r"], ["Order saga", "Inventory", "reserve 1 pair"], ["Inventory", "Order saga", "out of stock ✘", "r"],
       ["Order saga", "Payments", "compensate: refund ₹2,499"], ["Order saga", "Orders", "mark order CANCELLED", "", "Each step is a local transaction; failures are undone by compensating actions, not rollbacks."]]),
  TABLE("2PC vs Saga", ["", "2PC", "Saga"], [["consistency", "atomic", "eventual"], ["locks held", "across the whole protocol", "only per local step"], ["failure", "blocking if coordinator dies", "compensations"], ["use", "within one DB vendor / XA, rarely across services", "microservices (orders, payments, booking)"]]),
  KEY("Pair sagas with the **transactional outbox**: write the business row and an 'event to publish' row in the same local transaction; a relay publishes it, so you never update the DB but lose the event (or vice versa).", "Outbox"))

X("cdc",
  P("Change Data Capture reads the database's own **replication log** (Postgres WAL, MySQL binlog) and turns each committed change into an event, without touching application code."),
  BA(SEQ("Dual write from the app", ["App", "Postgres", "Kafka"],
          [["App", "Postgres", "UPDATE order 987 → PAID; commit ✔"], ["App", "Kafka", "publish OrderPaid", "", "The app crashes or Kafka is down right here."], NOTE(["App", "Kafka"], "DB says PAID, but search, cache and email never hear about it")]),
     SEQ("Change data capture from the WAL", ["App", "Postgres", "Debezium", "Kafka"],
          [["App", "Postgres", "UPDATE order 987 → PAID; commit ✔"], ["Debezium", "Postgres", "tail WAL"], ["Debezium", "Kafka", "orders.changes: op=u, after={PAID}", "", "If anything crashes, Debezium resumes from its saved WAL position: no event is lost."]]),
     "Before: dual write can lose events", "After: CDC (or a transactional outbox)"),
  FLOW("CDC pipeline", [["db:Postgres (orders)"], ["Debezium reads WAL"], ["q:Kafka topic orders.changes"], ["Search indexer", "Cache invalidator", "Data warehouse"]],
       [["Postgres (orders)", "Debezium reads WAL"], ["Debezium reads WAL", "Kafka topic orders.changes"], ["Kafka topic orders.changes", "Search indexer"], ["Kafka topic orders.changes", "Cache invalidator"], ["Kafka topic orders.changes", "Data warehouse"]]),
  CODE("One change event", """{ "op": "u", "table": "orders", "ts_ms": 1764140000000,
  "before": { "id": 987, "status": "PENDING" },
  "after":  { "id": 987, "status": "PAID" },
  "source": { "lsn": 2398456712 } }""", "json"),
  KEY("Dual writes (app writes DB and then Kafka) can diverge if one fails. CDC or the outbox pattern gives one source of truth: the DB commit.", "Why not just publish from the app?"))

X("blob-metadata",
  P("Store **bytes** in object storage and **facts about the bytes** in a database. Never put large files in your SQL rows."),
  FLOW("Photo upload: bytes vs metadata", [["u:Client"], ["API (metadata)", "Object store (bytes)"], ["db:Metadata DB", "CDN"]],
       [["Client", "API (metadata)", "1 · ask for upload URL"], ["Client", "Object store (bytes)", "2 · PUT bytes (pre-signed)"], ["API (metadata)", "Metadata DB", "3 · save row"], ["Object store (bytes)", "CDN", "4 · served via CDN"]]),
  ER("Metadata row", [("photos", "SQL", [("photo_id", "bigint", "PK"), ("owner_id", "bigint", "IDX"), ("object_key", "text", ""), ("size_bytes", "bigint", ""), ("sha256", "char(64)", "IDX"), ("width/height", "int", ""), ("status", "enum", ""), ("created_at", "timestamp", "")], "sha256 enables dedup")]),
  KEY("The row is created as PENDING, flipped to READY when storage confirms the upload; a cleanup job deletes orphans in either direction.", "Keep them in sync"))
