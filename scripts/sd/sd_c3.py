"""System Design concepts, part 3: Databases & storage."""
from sd_util import C

DATABASES = [
C("sql-vs-nosql", "SQL vs NoSQL", "Basic",
  "SQL (relational) databases store data in tables with a fixed schema and support joins and transactions. NoSQL databases trade some of that for flexible schemas and easier horizontal scaling.",
  """|SQL (relational)|NoSQL|
|Tables, rows, fixed schema, foreign keys|Key–value, document, wide-column, graph|
|Powerful queries: joins, aggregates, SQL|Simple access patterns, query by key|
|**ACID transactions**|Often BASE / eventual consistency (many now offer transactions too)|
|Scale up first; sharding is manual/hard|Built to shard across many nodes|
|PostgreSQL, MySQL, Oracle, SQL Server|DynamoDB, Cassandra, MongoDB, Redis, Neo4j|

### How to choose (say this in interviews)
- Data is **relational with transactions** (payments, orders, inventory, bookings) → **SQL**.
- **Massive scale, simple access by key**, high write volume (chat messages, events, IoT, timelines) → **NoSQL** (Cassandra/DynamoDB).
- **Flexible, nested documents** (product catalogue with varying attributes, CMS) → **document DB** (MongoDB).
- **Relationships are the query** (friends of friends, fraud rings) → **graph DB**.
- Many systems use **both** (polyglot persistence): Postgres for orders, Redis for cache, Elasticsearch for search, S3 for files.

### NewSQL
Google Spanner, CockroachDB, YugabyteDB, TiDB: SQL + ACID **and** horizontal scaling, using consensus (Raft/Paxos). Costs: higher write latency, operational complexity.""",
  tips=["Never say 'NoSQL because it's faster'. Say which access pattern and scale makes it fit."]),

C("acid", "ACID transactions", "Basic",
  "A transaction is a group of operations that succeed or fail together. ACID = Atomicity, Consistency, Isolation, Durability.",
  """Transfer ₹500 from A to B: debit A **and** credit B. Never just one.

- **Atomicity**: all or nothing. If the credit fails, the debit is rolled back. (Implemented with an undo/redo log.)
- **Consistency**: the transaction moves the DB from one valid state to another; constraints (balance ≥ 0, foreign keys) always hold.
- **Isolation**: concurrent transactions don't see each other's half-done work; the result is as if they ran one by one (to a degree set by the **isolation level**).
- **Durability**: once committed, it survives crashes (the **write-ahead log** is flushed to disk before 'commit' returns).

```java
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 'A' AND balance >= 500;
UPDATE accounts SET balance = balance + 500 WHERE id = 'B';
COMMIT;   -- or ROLLBACK on any error
```

### BASE (the NoSQL counterpart)
**B**asically **A**vailable, **S**oft state, **E**ventually consistent: stay available, let replicas converge later.""",
  see=("isolation-levels", "distributed-transactions")),

C("isolation-levels", "Isolation levels and concurrency anomalies", "Advanced",
  "How much concurrent transactions can interfere: read uncommitted, read committed, repeatable read, serializable — each stops more anomalies but costs more.",
  """### Anomalies
- **Dirty read**: you read data another transaction hasn't committed (and may roll back).
- **Non-repeatable read**: you read a row twice and get different values because someone committed in between.
- **Phantom read**: re-running `WHERE price < 100` returns new rows inserted by someone else.
- **Lost update**: two transactions read balance 100, both add 10, both write 110 — one update lost.
- **Write skew**: two doctors each check 'at least one other doctor on call' and both go off call.

|Level|Dirty read|Non-repeatable|Phantom|
|Read uncommitted|possible|possible|possible|
|Read committed (Postgres/Oracle default)|prevented|possible|possible|
|Repeatable read (MySQL InnoDB default)|prevented|prevented|possible (InnoDB mostly prevents)|
|Serializable|prevented|prevented|prevented|

### How databases implement it
- **Locks**: shared (read) and exclusive (write) locks; **two-phase locking (2PL)** for serializable.
- **MVCC** (multi-version concurrency control): writers create new row versions; readers see a **snapshot**, so readers never block writers. Postgres, MySQL InnoDB, Oracle.
- **SSI** (serializable snapshot isolation): detect dangerous conflicts and abort one transaction.

### Practical fixes for lost updates
- Atomic update: `UPDATE ... SET stock = stock - 1 WHERE id = ? AND stock > 0`.
- **Pessimistic locking**: `SELECT ... FOR UPDATE`.
- **Optimistic locking**: a `version` column; `UPDATE ... WHERE id = ? AND version = 7`, retry if 0 rows changed.""",
  tips=["Ticket/seat booking questions are really about lost updates: show optimistic or pessimistic locking."],
  see=("ticketmaster-hld",)),

C("indexes", "Database indexes (B-tree, hash, composite, covering)", "Intermediate",
  "An index is a sorted lookup structure (like a book's index) that finds rows without scanning the whole table: O(log n) instead of O(n).",
  """### B-tree / B+tree (the default in SQL databases)
- Balanced tree with high fan-out (hundreds of keys per node), so even a billion rows need only 3–4 disk reads.
- Supports equality and **range** queries (`BETWEEN`, `ORDER BY`, prefix `LIKE 'abc%'`).
- Leaf nodes are linked, so range scans are fast.

### Other index types
- **Hash index**: O(1) equality lookups, no ranges.
- **Composite index** `(country, city, age)`: follows the **leftmost prefix rule** — helps `WHERE country=?` and `WHERE country=? AND city=?`, not `WHERE city=?` alone.
- **Covering index**: contains every column the query needs, so the table isn't touched ('index-only scan').
- **Clustered** (rows stored in index order; one per table — InnoDB primary key) vs **non-clustered/secondary** (points to the row).
- **Full-text (inverted)**, **geospatial** (R-tree, geohash), **bitmap** (low-cardinality columns in warehouses).

### Costs
Every index slows **writes** (it must be updated) and uses storage. Index columns you filter, join and sort on; check with `EXPLAIN`.

### Secondary indexes in sharded databases
- **Local** (per shard): writes are cheap, but queries by that column must hit every shard (scatter-gather).
- **Global** (partitioned by the indexed column): fast reads, but writes touch several shards (usually updated asynchronously, as in DynamoDB GSIs).""",
  diagram={"rows": [["[10 | 50]"], ["[3 | 7]", "[20 | 35]", "[60 | 80]"], ["rows 1-9", "rows 10-49", "rows 50-99"]],
           "edges": [["[10 | 50]", "[3 | 7]", "<10"], ["[10 | 50]", "[20 | 35]", "10-49"], ["[10 | 50]", "[60 | 80]", "≥50"], ["[3 | 7]", "rows 1-9"], ["[20 | 35]", "rows 10-49"], ["[60 | 80]", "rows 50-99"]]}),

C("storage-engines", "Storage engines: B-tree vs LSM tree, WAL", "Advanced",
  "B-trees update data in place (fast reads). LSM trees append writes to memory and sorted files, merging them later (very fast writes). The write-ahead log makes both crash-safe.",
  """### Write-ahead log (WAL)
Before changing data pages, append the change to a sequential log on disk. After a crash, replay the log. Also the basis of **replication** (ship the log to replicas) and **CDC**.

### LSM tree (Log-Structured Merge tree)
1. Write goes to the WAL and an in-memory sorted table (**memtable**).
2. When the memtable is full, flush it to disk as an immutable sorted file (**SSTable**).
3. Background **compaction** merges SSTables and drops overwritten/deleted keys (**tombstones**).
4. Reads check memtable, then SSTables newest → oldest; **Bloom filters** skip files that can't contain the key.

Used by Cassandra, RocksDB, LevelDB, HBase, ScyllaDB, Bigtable.

|B-tree|LSM tree|
|In-place updates, random writes|Sequential appends|
|Faster reads, predictable|Much faster writes, great compression|
|Write amplification from page splits|Read and space amplification; compaction uses CPU/IO|
|Postgres, MySQL, Oracle|Cassandra, RocksDB, DynamoDB internals, Kafka-like logs|

Pick LSM-based stores for **write-heavy** workloads (chat, logs, metrics, IoT).""",
  diagram={"rows": [["Write"], ["WAL (disk)", "Memtable (RAM)"], ["SSTable L0", "SSTable L1", "SSTable L2"]],
           "edges": [["Write", "WAL (disk)", "append"], ["Write", "Memtable (RAM)", "insert"], ["Memtable (RAM)", "SSTable L0", "flush"], ["SSTable L0", "SSTable L1", "compact"], ["SSTable L1", "SSTable L2", "compact"]]},
  see=("bloom-filter", "kvstore-hld")),

C("nosql-types", "NoSQL families: key–value, document, wide-column, graph", "Intermediate",
  "Four main kinds of NoSQL database, each built around a different access pattern.",
  """|Type|Model|Examples|Great for|
|Key–value|`key → value` blob|Redis, DynamoDB, Riak|Sessions, carts, caches, feature flags|
|Document|JSON-like documents, queries on fields|MongoDB, Couchbase, Firestore|Catalogues, user profiles, CMS, varying attributes|
|Wide-column|Rows with a **partition key** + **clustering key**, sparse columns|Cassandra, HBase, Bigtable, ScyllaDB|Huge write volume: messages, time series, activity logs|
|Graph|Nodes + edges with properties|Neo4j, Amazon Neptune, JanusGraph|Social graphs, recommendations, fraud detection|

### Modelling for Cassandra/DynamoDB: query-first
You design tables **per query**, denormalising freely.
- Chat messages: partition key `conversation_id`, clustering key `message_time DESC` → 'last 50 messages in this chat' is one fast partition read.
- Avoid **hot partitions**: a partition key with too much traffic (one celebrity) or unbounded size; add a bucket (`conversation_id + month`).

### DynamoDB essentials
Partition key (+ optional sort key), on-demand or provisioned capacity, **GSIs** for other access patterns, DynamoDB Streams for CDC, conditional writes for optimistic locking, single-table design.""",
  see=("chat-hld",)),

C("normalization", "Normalization vs denormalization", "Intermediate",
  "Normalize = store each fact once (no duplication, joins at read time). Denormalize = copy data where it's read (fast reads, harder writes).",
  """### Normal forms (short)
- **1NF**: atomic columns, no repeating groups.
- **2NF**: no column depends on only part of a composite key.
- **3NF**: no column depends on another non-key column (store `city_id`, not city name + state in every row).

### Denormalization
Store `author_name` inside each post row, or a precomputed `like_count`, so the feed doesn't join 4 tables. Read-heavy systems denormalize on purpose.

|Normalized|Denormalized|
|No duplicate data, easy updates|Fast reads, no joins|
|Joins get expensive at scale and across shards|Updates must touch many copies; risk of inconsistency|
|OLTP core data (orders, accounts)|Feeds, search documents, read models (CQRS), NoSQL tables|

Typical answer: **normalized source of truth + denormalized read models / caches** kept in sync by events.""",
  see=("cqrs",)),

C("replication", "Replication: leader–follower, multi-leader, leaderless", "Intermediate",
  "Keeping copies of the same data on several machines for availability, durability and read scaling.",
  """### Leader–follower (primary–replica / master–slave)
- All writes go to the **leader**; it streams its log to **followers**; reads can go to followers.
- Great for **read-heavy** apps (add read replicas). Used by Postgres, MySQL, MongoDB, Redis.
- **Failover**: if the leader dies, promote a follower (automatic with Patroni, RDS Multi-AZ). Risks: losing un-replicated writes, **split brain** (two leaders).

### Synchronous vs asynchronous
- **Sync**: leader waits for the follower before confirming. No data loss, but slower and blocked if the follower is down.
- **Async**: confirm immediately. Fast, but a crash can lose recent writes and followers lag.
- **Semi-sync**: wait for one follower, the rest async — common compromise.

### Replication lag problems (and fixes)
- **Read-your-own-writes**: user updates profile, reads from a lagging replica, sees old data → read from the leader for a short time after a write, or for the user's own data.
- **Monotonic reads**: user sees new data then old → pin a user to one replica.
- **Consistent prefix**: answers seen before questions → keep causally related writes in one partition.

### Multi-leader
Several leaders (e.g. one per region) accept writes and sync with each other. Low-latency writes everywhere, survives a region loss, but **write conflicts** must be resolved (last-write-wins, merge, CRDTs). Used for multi-region apps and offline-first apps (Google Docs-like).

### Leaderless (Dynamo-style)
Client writes to **W** of **N** replicas and reads from **R**; if `R + W > N` the read sees the latest write. **Read repair** and **anti-entropy** (Merkle trees) fix stale replicas; **hinted handoff** covers temporarily down nodes. Cassandra, DynamoDB, Riak.""",
  diagram={"rows": [["App"], ["db:Leader"], ["db:Follower 1", "db:Follower 2"]],
           "edges": [["App", "Leader", "writes"], ["Leader", "Follower 1", "replication log"], ["Leader", "Follower 2", "replication log"], ["App", "Follower 2", "reads"]]},
  lab="quorum", see=("quorum", "crdt")),

C("sharding", "Partitioning and sharding", "Intermediate",
  "Splitting a big dataset across many machines (shards), each holding part of the data, so storage and load scale horizontally.",
  """### Strategies
|Strategy|How|Pros|Cons|
|**Range**|`user_id 1–1M → shard 1, 1M–2M → shard 2`|Range queries easy|Hot spots (new users all hit the last shard)|
|**Hash**|`shard = hash(user_id) % N`|Even spread|Range queries scatter; changing N moves almost everything|
|**Consistent hashing**|Hash ring with virtual nodes|Adding a shard moves ~1/N of data|Slightly more complex|
|**Directory / lookup**|A service maps key → shard|Fully flexible moves|Lookup service is an extra hop and must be highly available|
|**Geo**|By region (India users in Mumbai)|Low latency, data residency laws|Uneven sizes|

### Choosing a shard key
- High **cardinality**, even distribution, and matches the **main query** (all of a user's data on one shard → no cross-shard joins).
- Bad keys: country (skewed), timestamp (all writes hit one shard), boolean flags.

### Problems sharding brings
- **Cross-shard queries and joins**: scatter-gather or denormalise.
- **Cross-shard transactions**: avoid, or use Sagas / 2PC.
- **Hot partitions / celebrity problem**: split hot keys, add a random suffix, cache.
- **Rebalancing / resharding**: move data while online (consistent hashing, pre-split into many logical shards like 4,096 and move whole logical shards between machines).
- **Unique IDs** across shards: Snowflake-style IDs instead of auto-increment.

### Before sharding, try
Vertical scaling → read replicas → caching → **vertical partitioning** (split tables by feature into separate DBs). Shard only when writes or storage outgrow one machine.""",
  see=("consistent-hashing", "unique-id")),

C("consistent-hashing", "Consistent hashing", "Intermediate",
  "Place servers and keys on a hash ring; each key belongs to the next server clockwise. Adding or removing a server moves only the keys next to it (~1/N), not almost all of them.",
  """### The problem with `hash(key) % N`
Going from 4 to 5 servers changes the result for ~80% of keys: a cache would suddenly miss on almost everything.

### The ring
1. Hash each server (e.g. `hash("cache-3")`) onto a ring of 0 … 2³²−1.
2. Hash each key onto the same ring.
3. A key is stored on the **first server clockwise** from it.
4. Add a server: it takes over only the keys between it and its predecessor. Remove one: its keys go to the next server.

### Virtual nodes
With few servers the ring is uneven. Give each physical server 100–200 **virtual nodes** (hash `cache-3#1`, `cache-3#2`, …) spread around the ring. This evens out load and lets stronger machines get more vnodes.

### Replication on the ring
Store each key on the next **N distinct** servers clockwise (Dynamo, Cassandra).

### Used by
DynamoDB, Cassandra, Riak, Memcached clients (Ketama), Discord, Akamai, load balancers (Maglev uses a related lookup table).

```java
TreeMap<Long, String> ring = new TreeMap<>();
void add(String node) { for (int v = 0; v < 150; v++) ring.put(hash(node + "#" + v), node); }
String nodeFor(String key) {
    Map.Entry<Long, String> e = ring.ceilingEntry(hash(key));
    return (e != null ? e : ring.firstEntry()).getValue();   // wrap around
}
```""",
  lab="ring", see=("sharding", "kvstore-hld")),

C("db-scaling-path", "How to scale a database step by step", "Intermediate",
  "The usual path from one database to a planet-scale one, and what each step costs.",
  """1. **Optimise queries**: indexes, `EXPLAIN`, avoid N+1 queries, connection pooling (HikariCP, PgBouncer).
2. **Vertical scaling**: bigger machine, faster SSDs, more RAM for the buffer pool.
3. **Caching**: Redis in front for hot reads.
4. **Read replicas**: route reads to followers; handle replication lag.
5. **Vertical partitioning / functional split**: users DB, orders DB, catalogue DB per service.
6. **Denormalisation and materialised views** for expensive joins.
7. **Sharding** (horizontal partitioning) when writes or data size exceed one machine.
8. **Move suitable data to purpose-built stores**: logs/events to Cassandra or Kafka, search to Elasticsearch, files to S3, analytics to a warehouse.
9. **Multi-region**: replicas per region, or a globally distributed DB (Spanner, CockroachDB, DynamoDB Global Tables).

### Federation
Split databases by function (users, products, forums), each its own primary/replicas. Less load per DB, but cross-DB joins move into the application.""",
  diagram={"rows": [["App servers"], ["c:Redis cache", "db:Primary"], ["db:Replica 1", "db:Replica 2", "db:Shard 2 primary"]],
           "edges": [["App servers", "Redis cache", "hot reads"], ["App servers", "Primary", "writes"], ["Primary", "Replica 1"], ["Primary", "Replica 2"], ["App servers", "Shard 2 primary", "users M-Z"]]}),

C("connection-pooling", "Connection pooling and N+1 queries", "Intermediate",
  "Opening a DB connection is slow (TCP + TLS + auth), so apps keep a pool of open connections and reuse them. N+1 is the classic ORM mistake of running one query per item.",
  """### Connection pools
- **HikariCP** (Java default in Spring Boot), PgBouncer/ProxySQL (proxy-level pools).
- Pool size: small! Roughly `cores × 2` per DB; thousands of app threads share tens of connections. A DB with 5,000 open connections spends its time context-switching.
- With 200 app servers × 20 connections = 4,000 connections → put **PgBouncer / RDS Proxy** in between.

### N+1 queries
```java
List<Order> orders = repo.findByUser(42);        // 1 query
for (Order o : orders) o.getItems().size();     // +N queries (lazy loading)
```
Fix: `JOIN FETCH`, batch loading (`WHERE order_id IN (...)`), or GraphQL DataLoader.""",
  see=("graphql",)),

C("distributed-transactions", "Distributed transactions: 2PC, 3PC, Saga, outbox", "Advanced",
  "When one business action touches several databases or services, you need a way to commit all-or-nothing (2PC) or to undo with compensations (Saga).",
  """### Two-phase commit (2PC)
1. **Prepare**: the coordinator asks every participant 'can you commit?'; each locks resources and votes yes/no.
2. **Commit/abort**: all yes → commit everywhere; any no → abort everywhere.
- Strong consistency, but **blocking**: if the coordinator dies after prepare, participants hold locks indefinitely. Slow (several round trips). Used inside databases (XA, Spanner) rather than across microservices.

### Three-phase commit (3PC)
Adds a pre-commit phase and timeouts to avoid blocking, but still unsafe under network partitions; rarely used.

### Saga (the microservices answer)
A sequence of **local transactions**; if step k fails, run **compensating transactions** for steps k−1 … 1.
Order saga: create order → reserve inventory → charge payment → ship. Payment fails → release inventory → cancel order.
- **Choreography**: each service listens for events and emits the next (simple, but the flow is implicit).
- **Orchestration**: a central orchestrator (e.g. Temporal, AWS Step Functions, Camunda) tells each service what to do (explicit, easier to monitor).
- Sagas give **eventual consistency**; design for intermediate states ('payment pending') and idempotent steps.

### Transactional outbox
Problem: update DB **and** publish an event — if you do both separately, one can fail. Fix: in the **same DB transaction**, write the business row and an `outbox` row; a relay (poller or CDC like Debezium) publishes outbox rows to Kafka. Guarantees the event is sent at least once.""",
  diagram={"rows": [["Order service"], ["Inventory service", "Payment service", "Shipping service"]],
           "edges": [["Order service", "Inventory service", "1 reserve"], ["Order service", "Payment service", "2 charge"], ["Payment service", "Inventory service", "fail → release"], ["Order service", "Shipping service", "3 ship"]]},
  see=("cdc", "event-sourcing", "payment-hld")),

C("cdc", "Change Data Capture (CDC)", "Advanced",
  "Read the database's own change log (binlog/WAL) and turn every insert/update/delete into an event stream, so caches, search indexes and warehouses stay in sync without dual writes.",
  """- Tools: **Debezium** (reads MySQL binlog / Postgres WAL → Kafka), DynamoDB Streams, MongoDB change streams.
- Uses: update Elasticsearch, invalidate caches, feed the data warehouse, power the outbox pattern, migrate databases with zero downtime.
- Benefits: the DB is the single source of truth; no 'write to DB and also to Kafka' inconsistency.
- Watch out: schema changes, ordering per key, and replaying from a snapshot on first start.""",
  diagram={"rows": [["db:Postgres (WAL)"], ["Debezium"], ["q:Kafka"], ["x:Elasticsearch", "c:Cache invalidator", "db:Warehouse"]],
           "edges": [["Postgres (WAL)", "Debezium", "changes"], ["Debezium", "Kafka"], ["Kafka", "Elasticsearch"], ["Kafka", "Cache invalidator"], ["Kafka", "Warehouse"]]}),

C("blob-metadata", "Storing files: blob store + metadata DB", "Basic",
  "Never store large files (images, videos, PDFs) inside the relational database. Put the bytes in object storage and keep a small metadata row pointing to them.",
  """```java
files(id, owner_id, s3_key, size_bytes, content_type, checksum_sha256, created_at)
```
- Upload via **pre-signed URL** directly to S3; the app only records metadata.
- Serve via **CDN** in front of the bucket.
- Generate thumbnails/transcodes asynchronously from an 'object created' event (S3 → queue → workers).
- Deduplicate identical files by checksum (content-addressed storage).""",
  see=("storage-types", "youtube-hld")),
]
