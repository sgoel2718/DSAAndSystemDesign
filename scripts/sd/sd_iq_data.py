"""Theory interview questions: Databases & Storage tab."""
from sd_iq_util import Q

Q("sql-vs-nosql",
  ("B", "SQL vs NoSQL: key differences?", "SQL: relational tables, fixed schema, joins, ACID transactions, vertical scaling first. NoSQL: key-value, document, wide-column or graph models, flexible schema, built-in horizontal partitioning, often tunable consistency."),
  ("B", "When would you pick a relational database?", "Relational data with joins, multi-row transactions, strong constraints, ad-hoc querying and reporting: payments, orders, inventory, user accounts."),
  ("I", "When would you pick a NoSQL database?", "Huge write volume or data size, simple known access patterns (by key/partition), flexible/varied schemas, or very low latency at scale: event logs, time series, messaging, carts, catalogues."),
  ("I", "Can NoSQL databases do transactions and joins?", "Many now offer limited transactions (MongoDB multi-document, DynamoDB TransactWrite) but at higher cost; joins are usually done in the app or avoided by denormalising."),
  ("I", "What is 'schema on write' vs 'schema on read'?", "SQL enforces structure when writing; document stores accept varied shapes and the reader interprets them. Flexibility shifts validation to application code."),
  ("A", "What is NewSQL / distributed SQL?", "Databases like Spanner, CockroachDB and YugabyteDB that offer SQL and ACID transactions while sharding and replicating automatically using consensus."),
  ("A", "How would you migrate from a single SQL DB when it reaches its limits?", "Profile first; add indexes, caching and read replicas; split by service/feature; then shard the biggest tables by a good key or move them to a distributed store, using dual-writes/CDC and backfills with verification."))

Q("acid",
  ("B", "What does ACID stand for?", "Atomicity (all or nothing), Consistency (constraints hold), Isolation (concurrent transactions don't interfere), Durability (committed data survives crashes)."),
  ("I", "How do databases implement atomicity and durability?", "A write-ahead log: changes are logged and fsynced before commit; on crash, committed entries are replayed (redo) and uncommitted ones rolled back (undo)."),
  ("I", "What is the difference between ACID consistency and CAP consistency?", "ACID C = transactions keep the database's invariants valid. CAP C = all replicas appear as one up-to-date copy (linearizability)."),
  ("I", "What is BASE?", "Basically Available, Soft state, Eventually consistent: the trade-off many NoSQL systems make instead of strict ACID across a distributed system."),
  ("A", "How does MVCC work?", "Writers create new row versions with transaction ids; readers see a snapshot as of their start time, so reads don't block writes. Old versions are cleaned up later (VACUUM in Postgres)."),
  ("A", "Why is fsync important and what happens if you disable it?", "fsync forces data from OS buffers to stable storage; without it, a power loss can lose committed transactions or corrupt data despite the database saying 'committed'."))

Q("isolation-levels",
  ("B", "What are the standard SQL isolation levels?", "Read uncommitted, read committed, repeatable read, serializable (strongest)."),
  ("I", "Explain dirty read, non-repeatable read and phantom read.", "Dirty: reading uncommitted data. Non-repeatable: the same row read twice gives different values. Phantom: the same range query returns different rows because others inserted/deleted."),
  ("I", "What is a lost update and how do you prevent it?", "Two read-modify-write transactions overwrite each other's change. Prevent with atomic updates (SET x = x − 1), SELECT … FOR UPDATE, optimistic versioning, or serializable isolation."),
  ("I", "Optimistic vs pessimistic locking?", "Pessimistic locks rows before changing them (blocks others; good under high contention). Optimistic checks a version at write time and retries on conflict (good when conflicts are rare)."),
  ("A", "What is write skew? Give an example.", "Two transactions read overlapping data, make decisions, and write different rows, violating an invariant together (two on-call doctors both going off call). Only serializable isolation or explicit locks prevent it."),
  ("A", "What is snapshot isolation and how does SSI improve it?", "Each transaction sees a consistent snapshot; it prevents dirty/non-repeatable reads but allows write skew. Serializable Snapshot Isolation tracks read/write dependencies and aborts transactions that would form an anomaly."))

Q("indexes",
  ("B", "What is a database index?", "An auxiliary data structure (usually a B+ tree) that lets the database find rows by column values without scanning the whole table."),
  ("B", "Downsides of indexes?", "Every write must update every index (slower inserts/updates), extra storage, and the optimizer may pick bad indexes; too many indexes hurt write-heavy tables."),
  ("I", "How does a B+ tree index work?", "A balanced tree with high fan-out; internal nodes hold keys for navigation, leaves hold keys and row pointers and are linked for range scans. Lookups take ~3–4 page reads even for billions of rows."),
  ("I", "What is a composite index and the leftmost prefix rule?", "An index on (a, b, c) is sorted by a, then b, then c, so it helps queries filtering on a, (a, b), or (a, b, c), but not on b or c alone."),
  ("I", "Clustered vs non-clustered index?", "Clustered: table rows are physically stored in index order (one per table, e.g., InnoDB primary key). Non-clustered: separate structure pointing to rows, requiring an extra lookup."),
  ("I", "What is a covering index?", "An index containing all columns a query needs, so the database answers from the index alone without reading table rows."),
  ("A", "Hash index vs B-tree index?", "Hash: O(1) exact-match lookups, no ranges or ordering. B-tree: ordered, supports ranges, prefix and ORDER BY; the default for most cases."),
  ("A", "How do you find and fix a slow query?", "EXPLAIN/ANALYZE to see the plan; look for full scans, bad join orders, missing/unused indexes, functions on indexed columns, N+1 patterns; add the right composite index or rewrite the query."))

Q("storage-engines",
  ("B", "What is a storage engine?", "The component of a database that stores and retrieves data on disk/memory, e.g., InnoDB (B-tree) or RocksDB (LSM tree)."),
  ("I", "How does an LSM tree handle writes and reads?", "Writes go to a WAL and an in-memory sorted memtable, flushed to immutable sorted SSTables; reads check the memtable then SSTables (with Bloom filters); background compaction merges SSTables."),
  ("I", "B-tree vs LSM tree?", "B-trees update pages in place: predictable reads, good for read-heavy OLTP. LSM trees turn writes into sequential appends: high write throughput, compression, but read and compaction overhead."),
  ("A", "What are read, write and space amplification?", "Read: disk reads per query. Write: bytes written to disk per byte of user data (compaction rewrites). Space: disk used per byte of live data. LSM tuning trades between them."),
  ("A", "Leveled vs size-tiered compaction?", "Leveled keeps non-overlapping files per level: less space and better reads, more write amplification. Size-tiered merges similar-sized files: lower write amplification, more space and read cost."),
  ("A", "What is a tombstone and why can it hurt performance?", "A delete marker in LSM stores; until compaction removes them, reads must skip many tombstones (a known Cassandra problem with heavy deletes)."))

Q("nosql-types",
  ("B", "Name the four main NoSQL families with examples.", "Key-value (Redis, DynamoDB), document (MongoDB), wide-column (Cassandra, HBase, Bigtable), graph (Neo4j, Neptune)."),
  ("I", "How do you model data in Cassandra?", "Query-first: one table per access pattern, partition key spreads load and groups data read together, clustering columns sort within a partition, denormalise freely, avoid unbounded partitions."),
  ("I", "When is a graph database the right choice?", "When queries traverse relationships many hops deep (friends-of-friends, fraud rings, recommendations, network topology), which would need many self-joins in SQL."),
  ("I", "Document store vs relational for a product catalogue?", "Document stores handle varying attributes per category and read a product in one lookup; relational needs EAV tables or JSON columns but gives joins and constraints."),
  ("A", "What is a partition key hot spot in DynamoDB/Cassandra and how do you avoid it?", "Too much traffic on one partition key (date, celebrity id) overloads one node. Use high-cardinality keys, add a random/hash suffix (write sharding), or cache hot reads."),
  ("A", "What are secondary indexes in NoSQL and their trade-offs?", "Local indexes (per partition, cheap, query within a partition) vs global indexes (separate partitioned table, eventually consistent, extra write cost)."))

Q("normalization",
  ("B", "What is normalisation?", "Organising tables so each fact is stored once, removing redundancy and update/insert/delete anomalies (1NF, 2NF, 3NF, BCNF)."),
  ("I", "Explain 1NF, 2NF and 3NF briefly.", "1NF: atomic values, no repeating groups. 2NF: no partial dependency on part of a composite key. 3NF: no transitive dependency (non-key columns depend only on the key)."),
  ("I", "What is denormalisation and when is it justified?", "Deliberately duplicating data to avoid joins and speed up reads: read-heavy paths, NoSQL stores, analytics, caches and feeds. Cost: more complex writes and possible inconsistency."),
  ("I", "Give an example of an update anomaly.", "Customer city stored in every order row; updating it in some rows but not others leaves conflicting addresses."),
  ("A", "How do you keep denormalised copies consistent?", "Update copies in the same transaction where possible, or asynchronously via events/CDC with idempotent consumers; periodic reconciliation jobs; accept bounded staleness."))

Q("replication",
  ("B", "Why replicate a database?", "High availability (failover), read scaling (replicas), lower latency (replicas near users), and durability."),
  ("B", "Synchronous vs asynchronous replication?", "Sync: commit waits for replicas (no data loss on failover, higher latency). Async: commit returns immediately (fast, may lose recent writes, replicas lag)."),
  ("I", "What is replication lag and what problems does it cause?", "Delay before replicas apply writes. Users may not see their own writes, see data go 'backwards' between replicas, or see effects before causes."),
  ("I", "How do you guarantee read-your-writes with replicas?", "Read from the leader for a short time after a user writes, or track the user's last write position (LSN/GTID) and only read from replicas that have applied it."),
  ("I", "Single-leader vs multi-leader vs leaderless?", "Single-leader: simple, writes bottlenecked on one node. Multi-leader: writes in several regions, needs conflict resolution. Leaderless (Dynamo): writes to N replicas with quorums, read repair and anti-entropy."),
  ("A", "What can go wrong during leader failover?", "Lost writes (async), split brain (two leaders), clients writing to the old leader, conflicting auto-increment ids, and choosing a stale follower. Use fencing, consensus-based election and careful timeouts."),
  ("A", "How do you resolve write conflicts in multi-leader replication?", "Last-write-wins (lossy), merge functions/CRDTs, application-level resolution, or avoid conflicts by routing each record's writes to one home region."))

Q("sharding",
  ("B", "What is sharding?", "Splitting data horizontally across multiple databases (shards) so each holds a subset of rows, scaling storage and write throughput."),
  ("I", "How do you choose a shard key?", "High cardinality, even distribution, matches the main access pattern (queries hit one shard), keeps related data together, and avoids time-ordered hot spots."),
  ("I", "Range vs hash vs directory-based sharding?", "Range: efficient range scans, prone to hot spots. Hash: even spread, range queries hit all shards. Directory: a lookup table maps keys to shards, flexible but the lookup is a critical dependency."),
  ("I", "What problems does sharding introduce?", "Cross-shard joins and transactions, global unique ids, rebalancing/resharding, hot shards, and operational complexity (backups, schema changes per shard)."),
  ("A", "How do you reshard with minimal downtime?", "Use many logical shards mapped to fewer machines and move logical shards; or consistent hashing. Migrate with dual writes/CDC, backfill, verify, then flip routing."),
  ("A", "How do you query across shards efficiently?", "Scatter-gather with limits and merge; maintain secondary global indexes or denormalised read models (search index, data warehouse) for cross-shard queries."))

Q("consistent-hashing",
  ("B", "What problem does consistent hashing solve?", "With hash(key) % N, changing N remaps almost every key. Consistent hashing maps keys and servers onto a ring so adding/removing a server moves only ~1/N of keys."),
  ("I", "How does it work?", "Hash servers and keys onto the same ring; each key belongs to the next server clockwise. Adding a server takes over one arc; removing one hands its arc to the next server."),
  ("I", "What are virtual nodes and why use them?", "Each physical server is placed at many ring positions. This evens out load, lets bigger servers own more vnodes, and spreads a failed server's keys across all survivors."),
  ("I", "Where is consistent hashing used?", "Distributed caches (memcached clients), Dynamo/Cassandra/Riak partitioning, CDNs and load balancers for cache affinity, sharded message routing."),
  ("A", "How do you replicate data with consistent hashing?", "Store each key on the next N distinct physical servers clockwise (the preference list), skipping duplicate vnodes of the same server and ideally spreading across racks/zones."),
  ("A", "Alternatives to ring-based consistent hashing?", "Rendezvous (highest random weight) hashing, jump consistent hash (no memory, fixed numbered buckets), and Maglev hashing (fast lookup tables for load balancers)."))

Q("db-scaling-path",
  ("B", "What is the first thing to do when a database is slow?", "Measure: find slow queries, check indexes and query plans, fix N+1 patterns, before adding hardware or architecture."),
  ("I", "Order the usual steps for scaling a relational database.", "Query/index optimisation → vertical scaling → caching → read replicas → connection pooling → functional partitioning (separate DBs per domain) → sharding or distributed SQL."),
  ("I", "When do read replicas stop helping?", "When the bottleneck is writes (replicas must apply every write too), or when reads need strong consistency and must go to the leader."),
  ("I", "What is functional partitioning?", "Moving tables of different domains (users, orders, payments) into separate databases so each scales and fails independently."),
  ("A", "How do you archive old data to keep tables fast?", "Partition tables by time and detach/drop old partitions, move cold rows to cheaper storage or a warehouse, and keep hot tables small."),
  ("A", "What signals tell you it's time to shard?", "Write throughput or data size near a single primary's limit even after optimisation, replication/backups taking too long, and vertical scaling becoming cost-prohibitive."))

Q("connection-pooling",
  ("B", "What is connection pooling?", "Reusing a set of open database connections across requests instead of opening a new one each time, avoiding TCP/TLS/auth handshakes."),
  ("I", "Why is a huge pool bad?", "Databases degrade with too many concurrent connections (context switching, memory per connection, lock contention). A small pool queues work in the app instead of thrashing the DB."),
  ("I", "What is PgBouncer and when do you need it?", "A lightweight Postgres connection pooler/proxy that multiplexes many client connections onto few server connections; needed with many app instances or serverless functions."),
  ("I", "What is the N+1 query problem?", "Fetching a list with one query and then running one query per item (often via ORM lazy loading). Fix with joins, IN batching or eager loading."),
  ("A", "How do you size a connection pool?", "Start near (cores × 2) + effective spindles per DB node, measure throughput/latency under load, and remember total = pool size × app instances must stay under DB limits."),
  ("A", "Session vs transaction pooling modes?", "Session pooling assigns a server connection per client session; transaction pooling per transaction (more multiplexing) but breaks session features like prepared statements, temp tables and SET variables."))

Q("distributed-transactions",
  ("B", "Why are transactions across services hard?", "Each service owns its own database; there's no single transaction manager, networks fail, and locking across services hurts availability."),
  ("I", "How does two-phase commit work?", "Prepare: the coordinator asks each participant to promise it can commit (holding locks). Commit: if all vote yes, the coordinator tells all to commit; otherwise abort."),
  ("I", "What are the problems with 2PC?", "Blocking if the coordinator crashes after prepare (locks held), latency of multiple rounds, reduced availability, and limited support across heterogeneous systems."),
  ("I", "What is a saga?", "A sequence of local transactions where each step has a compensating action; if a step fails, compensations undo earlier steps. Orchestrated (central coordinator) or choreographed (events)."),
  ("A", "What are the challenges with sagas?", "No isolation (others see intermediate states), compensations must be idempotent and always succeed eventually, semantic locks/pending states needed, and debugging flows across services."),
  ("A", "How do you combine a saga with reliable messaging?", "Each step writes its state change and the next event via a transactional outbox; consumers are idempotent; the orchestrator persists saga state so it can resume after crashes."))

Q("cdc",
  ("B", "What is Change Data Capture?", "Streaming every committed insert/update/delete from a database's transaction log to other systems as events."),
  ("I", "Why is CDC better than dual writes?", "Dual writes (DB then Kafka) can fail halfway and diverge. CDC derives events from the DB's own committed log, so events match the DB exactly and nothing is lost."),
  ("I", "Common uses of CDC?", "Keeping search indexes, caches and data warehouses in sync, event-driven microservices, audit trails, and zero-downtime database migrations."),
  ("A", "How do you handle schema changes in CDC pipelines?", "Use a schema registry with compatibility rules (Avro/Protobuf), make changes backward compatible, and version consumers."),
  ("A", "CDC vs transactional outbox?", "CDC captures raw table changes (no app changes, but exposes internal schema). Outbox publishes intentional domain events written by the app in the same transaction, often tailed via CDC itself."))

Q("blob-metadata",
  ("B", "Why separate blob storage from metadata?", "Blobs are large and immutable, best in cheap object storage behind a CDN; metadata is small, queried and updated, best in a database."),
  ("I", "How do you upload large files efficiently?", "The client gets a pre-signed URL, uploads directly (multipart, resumable) to object storage, and the server records metadata when upload completes."),
  ("I", "How do you keep blob and metadata consistent?", "Create the row as PENDING, flip to READY on the storage completion event, and run cleanup jobs for orphans in both directions."),
  ("A", "How do you deduplicate stored files?", "Content-address blobs by hash (SHA-256): identical files share one stored object with a reference count; per-user rows point to the hash."),
  ("A", "How do you serve private files securely through a CDN?", "Short-lived signed URLs or signed cookies validated at the edge, private buckets accessible only by the CDN (origin access control)."))
