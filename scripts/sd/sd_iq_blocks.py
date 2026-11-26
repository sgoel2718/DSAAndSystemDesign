"""Theory interview questions: Building Blocks tab."""
from sd_iq_util import Q

Q("load-balancer",
  ("B", "What does a load balancer do?", "Spreads incoming requests across a pool of servers, removes unhealthy ones via health checks, and gives clients a single stable address so servers can be added/removed transparently."),
  ("B", "Where do you place load balancers in a typical architecture?", "Between clients and web/app servers (public LB), between internal service tiers (internal LB or client-side balancing), and sometimes in front of DB read replicas."),
  ("I", "Active vs passive health checks?", "Active: the LB probes /health periodically. Passive: the LB marks a backend unhealthy after real requests fail or time out. Use both; health endpoints should check critical dependencies lightly."),
  ("I", "How do you avoid the load balancer itself being a single point of failure?", "Run LBs in pairs (active–passive with a floating/virtual IP via VRRP) or active–active behind DNS/anycast; managed cloud LBs are already redundant across zones."),
  ("I", "What is connection draining?", "When removing a backend (deploy, scale-in), stop sending new requests but let in-flight ones finish before termination."),
  ("I", "What is TLS termination at the LB and what are the trade-offs?", "The LB decrypts HTTPS so it can route on L7 data and offload CPU from backends. Trade-off: traffic behind the LB is plain unless re-encrypted (or mTLS), and the LB holds private keys."),
  ("A", "How do you load-balance long-lived connections like WebSockets?", "L4 or connection-aware L7 balancing using least connections, sticky routing for the connection's lifetime, connection limits per server, and graceful rebalancing (ask clients to reconnect) when scaling."),
  ("A", "What is global server load balancing (GSLB)?", "Routing users across regions/datacenters using DNS (geo/latency-based) or anycast, with health checks to fail over a whole region."))

Q("lb-algorithms",
  ("B", "Name common load-balancing algorithms.", "Round robin, weighted round robin, least connections, least response time, IP/consistent hash, random, power of two choices."),
  ("I", "When is least-connections better than round robin?", "When request durations vary a lot (uploads, WebSockets, slow queries): round robin keeps sending to a busy server, least-connections favours idle ones."),
  ("I", "Why use consistent hashing in a load balancer?", "Sticky routing for cache locality or stateful sessions, while adding/removing a server only remaps a small fraction of clients."),
  ("I", "What is 'power of two choices'?", "Pick two servers at random and send to the less loaded one. Almost as good as least-loaded across the whole pool with far less coordination; great for very large pools."),
  ("A", "What problems does IP-hash routing have?", "Many users behind one NAT/proxy map to the same server (hot spot), mobile users change IPs (lose stickiness), and modulo hashing reshuffles everyone when the pool changes."),
  ("A", "How do weights help during a canary or with heterogeneous hardware?", "Weights send proportionally more traffic to bigger machines, or a small share (1–5%) to a canary version so it can be evaluated with limited blast radius."))

Q("cdn",
  ("B", "What is a CDN and why use one?", "A network of edge servers worldwide caching content near users. Benefits: lower latency, less origin load and bandwidth cost, DDoS absorption, TLS at the edge."),
  ("B", "What kind of content belongs on a CDN?", "Static assets (images, JS, CSS, fonts), video segments, downloads, and cacheable API responses or whole pages for anonymous users."),
  ("I", "Push vs pull CDN?", "Pull: edge fetches from origin on first miss and caches by TTL (most common). Push: you upload content ahead of time (large/popular files you know about)."),
  ("I", "How do you invalidate content on a CDN?", "Prefer versioned/fingerprinted URLs (app.3f9c.js) so new content gets new URLs; otherwise purge by URL/tag via API or wait for TTL expiry. Purges are slow and eventually consistent."),
  ("I", "What is an origin shield?", "A middle cache tier that all edges go through on misses, so the origin sees one request per object instead of one per edge."),
  ("I", "How does a CDN help against DDoS?", "Huge distributed capacity and anycast absorb volumetric attacks at the edge; WAF rules and rate limits filter L7 attacks before they reach your origin."),
  ("A", "Can a CDN cache personalised or dynamic pages?", "Partly: cache the shell and fetch personal fragments via API, use edge compute (ESI/edge functions) to assemble, vary cache keys by a small set of segments (country, logged-in flag), and use short TTLs + stale-while-revalidate."),
  ("A", "What metrics matter for a CDN?", "Cache hit ratio (by requests and by bytes), origin offload, edge latency/TTFB per region, error rates, and egress cost."))

Q("caching",
  ("B", "What is caching and why does it help?", "Storing results of expensive operations in fast storage so repeated requests are served quickly; reduces latency and load on databases/services."),
  ("B", "Where can caches live in a system?", "Browser, CDN, reverse proxy/gateway, application in-process memory, distributed cache (Redis/Memcached), database buffer pool, OS page cache."),
  ("I", "What is cache hit ratio and why is it so important?", "Hits / total lookups. Latency and DB load are dominated by misses: going from 90% to 99% cuts DB traffic 10×."),
  ("I", "What should you not cache?", "Data needing strict consistency (balances, inventory decisions), highly personalised low-reuse data, data that changes faster than it's read, and anything with security implications if keys are wrong."),
  ("I", "In-process cache vs distributed cache?", "In-process: fastest (no network) but duplicated per server, inconsistent across servers, lost on restart. Distributed: shared and larger, one network hop. Often both (two-level cache)."),
  ("I", "How do you pick a TTL?", "Based on how stale the data may be for users, how often it changes and how expensive misses are. Add jitter to avoid synchronized expiry; combine with explicit invalidation on writes."),
  ("A", "What are the hardest problems in caching?", "Invalidation (keeping cache consistent with the source), cold starts, stampedes on hot-key expiry, hot keys, and memory sizing/eviction behaviour."))

Q("cache-strategies",
  ("B", "Explain cache-aside.", "The app checks the cache; on miss it reads the DB and populates the cache; on write it updates the DB and deletes the cache key. Most common pattern."),
  ("I", "Read-through vs cache-aside?", "In read-through, the cache library itself loads from the DB on a miss; the app only talks to the cache. Cache-aside puts that logic in the application."),
  ("I", "Write-through vs write-behind (write-back)?", "Write-through writes cache and DB synchronously: fresh cache, slower writes. Write-behind writes to cache and flushes to DB later in batches: fast writes, risk of data loss."),
  ("I", "Why delete the cache key on update instead of updating it?", "Deleting is idempotent and avoids race conditions where two concurrent writers set the cache in the wrong order; the next read repopulates from the DB."),
  ("A", "Describe a race condition in cache-aside and how to mitigate it.", "Reader misses and reads old value V1; writer updates DB to V2 and deletes the key; reader then writes V1 into the cache → stale until TTL. Mitigate with short TTLs, delayed double delete, versioned values, or CDC-driven invalidation."),
  ("A", "What is refresh-ahead?", "Proactively reload hot keys before they expire (e.g., when TTL < 10% remaining) so users rarely see misses; best for predictable hot data."),
  ("A", "What is write-around and when is it useful?", "Writes go only to the DB, not the cache; the cache is populated on the next read. Good for data written once and rarely read (logs, bulk imports) to avoid polluting the cache."))

Q("cache-eviction",
  ("B", "What is a cache eviction policy?", "The rule for which entry to remove when the cache is full."),
  ("B", "Explain LRU, LFU and FIFO.", "LRU evicts the least recently used entry; LFU the least frequently used; FIFO the oldest inserted regardless of use."),
  ("I", "How do you implement an O(1) LRU cache?", "Hash map from key to node + doubly linked list ordered by recency: get moves the node to the front, put inserts at the front, eviction removes the tail."),
  ("I", "When is LFU better than LRU?", "When popularity is stable over time (top products): a one-off scan of many keys flushes an LRU cache but not an LFU one. LFU needs ageing so old popular keys eventually leave."),
  ("A", "How does Redis approximate LRU?", "It samples a few keys (default 5) and evicts the best candidate among them using a per-key access clock, avoiding a global linked list for memory efficiency."),
  ("A", "What are TinyLFU/W-TinyLFU?", "Admission policies (used by Caffeine) that keep frequency sketches to decide whether a new item deserves to evict an existing one; better hit ratios than plain LRU for skewed workloads."))

Q("cache-problems",
  ("B", "What is a cache stampede?", "When a hot key expires, many requests miss simultaneously and all hit the database at once."),
  ("I", "How do you prevent a stampede?", "Single-flight/request coalescing (one loader, others wait), a mutex key (SET NX), probabilistic early refresh, refresh-ahead, serving stale while revalidating, and jittered TTLs."),
  ("I", "What is cache penetration?", "Requests for keys that don't exist always miss and hit the DB (often malicious). Fix: cache negative results briefly, or use a Bloom filter of valid keys."),
  ("I", "What is cache avalanche?", "Many keys expire at the same time or the cache cluster restarts, flooding the DB. Fix: random TTL jitter, warm-up, replicas, and DB-side rate limiting."),
  ("I", "How do you handle a hot key?", "Local in-process caching, replicating the key across shards (key#1..N) and reading a random copy, and read replicas for the cache shard."),
  ("A", "How do you keep cache and database consistent?", "Delete-after-write with TTL as a safety net; CDC-based invalidation from the DB log; versioning; for strict needs, avoid caching or use write-through with transactions. Accept bounded staleness otherwise."))

Q("redis-memcached",
  ("B", "Why is Redis so fast?", "In-memory data, efficient data structures, single-threaded command execution (no lock overhead), non-blocking I/O, and a simple protocol."),
  ("B", "Redis vs Memcached?", "Redis: rich data types, persistence, replication, clustering, Lua scripts, pub/sub, streams. Memcached: simple multi-threaded key-value cache with no persistence. Redis is the default choice."),
  ("I", "Which Redis data structure would you use for a leaderboard, a rate limiter and a feed?", "Leaderboard: sorted set (ZINCRBY, ZREVRANGE). Rate limiter: string counters with INCR + EXPIRE or a sorted set sliding window. Feed: list (LPUSH + LTRIM) or sorted set by time."),
  ("I", "RDB vs AOF persistence?", "RDB: periodic snapshots, compact and fast restart, but loses data since the last snapshot. AOF: logs every write, fsync policy configurable (every second), more durable, larger files. Often both."),
  ("I", "How does Redis Cluster shard data?", "16,384 hash slots; key → CRC16(key) mod 16384; slots are assigned to masters, each with replicas. Hash tags {user:42} keep related keys in the same slot for multi-key ops."),
  ("A", "Is Redis safe as a primary database?", "Possible for some use cases with AOF + replicas, but async replication can lose acknowledged writes on failover and memory cost is high. Usually used as cache, session store, counters and queues with a durable DB behind."),
  ("A", "How do you implement a distributed lock in Redis and what are the caveats?", "SET key token NX PX ttl; release with a Lua script that deletes only if the token matches. Caveats: clock/GC pauses and failover can break mutual exclusion; use fencing tokens or a consensus store for correctness-critical locks."))

Q("message-queues",
  ("B", "What is a message queue and why use one?", "A buffer where producers put messages and consumers process them asynchronously. Decouples services, smooths traffic spikes, enables retries and background work."),
  ("B", "Point-to-point vs publish/subscribe?", "Point-to-point: each message is processed by one consumer (work queue). Pub/sub: every subscriber gets a copy of each message."),
  ("I", "What is a visibility timeout?", "After a consumer receives a message, it's hidden from others for a period; if not acknowledged in time it reappears for another consumer, so crashed workers don't lose work."),
  ("I", "What is a dead-letter queue?", "Where messages go after failing processing N times, so poison messages don't block the queue and can be inspected/replayed."),
  ("I", "How do you guarantee ordering?", "Use FIFO queues or partition by a key (order id) so one consumer processes a key's messages in order; global ordering doesn't scale."),
  ("I", "Why must consumers be idempotent?", "Most queues provide at-least-once delivery; retries and redeliveries produce duplicates, so processing the same message twice must have no extra effect."),
  ("A", "Kafka vs RabbitMQ vs SQS?", "Kafka: distributed log, high throughput, retention and replay, partitions for ordering. RabbitMQ: flexible routing (exchanges), per-message acks, lower latency. SQS: fully managed, simple, scales automatically, limited ordering (FIFO queues)."),
  ("A", "How do you handle a consumer that is much slower than producers?", "Scale consumers (up to partitions), batch processing, backpressure/bounded queues, shed or sample low-priority messages, alert on lag."))

Q("kafka",
  ("B", "What is Kafka?", "A distributed, partitioned, replicated append-only log used for event streaming. Producers append; consumers read at their own offsets; data is retained by time/size."),
  ("B", "What are topics, partitions and offsets?", "A topic is a named stream split into partitions; each partition is an ordered log where each message has an offset (position)."),
  ("I", "How does Kafka guarantee ordering?", "Only within a partition. Messages with the same key go to the same partition, so per-key order is preserved."),
  ("I", "What is a consumer group?", "A set of consumers sharing a topic's partitions; each partition is read by exactly one consumer in the group. Different groups read independently."),
  ("I", "Explain acks=all, ISR and min.insync.replicas.", "The leader acknowledges a write only after all in-sync replicas have it; with min.insync.replicas=2 and RF=3, writes fail if fewer than 2 replicas are in sync, so acknowledged data survives a broker loss."),
  ("I", "Why is Kafka so fast?", "Sequential disk appends, OS page cache, zero-copy sendfile to consumers, batching and compression, and partition parallelism."),
  ("A", "How does Kafka achieve exactly-once semantics?", "Idempotent producers (sequence numbers per partition), transactions spanning writes to multiple partitions + consumer offset commits, and read_committed consumers."),
  ("A", "What is log compaction?", "Kafka keeps at least the latest value per key and removes older ones, turning a topic into a durable changelog/table (used for state stores and CDC)."),
  ("A", "What happens during a consumer group rebalance and why is it a problem?", "Partitions are reassigned when consumers join/leave; processing pauses and in-flight work may be duplicated. Mitigate with cooperative/incremental rebalancing, static membership and committing offsets carefully."))

Q("delivery-semantics",
  ("B", "Explain at-most-once, at-least-once and exactly-once.", "At-most-once: may lose messages, never duplicates. At-least-once: never loses, may duplicate. Exactly-once: each message affects state once."),
  ("I", "How do you get at-least-once with Kafka?", "Commit offsets only after processing succeeds; on crash, uncommitted messages are reprocessed."),
  ("I", "Why is true exactly-once delivery impossible over an unreliable network?", "The sender can't distinguish a lost message from a lost acknowledgement, so it must either risk loss (don't resend) or duplicates (resend). Systems achieve 'effectively once' processing via idempotency/dedup."),
  ("I", "How do you make a consumer idempotent?", "Track processed message ids in the same transaction as the side effect (unique constraint), use natural idempotent operations (set status = PAID), or conditional updates with versions."),
  ("A", "What is the transactional outbox pattern?", "Write the business change and an outbox event row in one DB transaction; a relay publishes outbox rows to the broker. Avoids losing or inventing events when the DB commit and publish can't be atomic."),
  ("A", "How does Kafka Streams/Flink achieve exactly-once end to end?", "Checkpointing state and offsets together, transactional/idempotent sinks, and replay from the last consistent checkpoint after failure."))

Q("backpressure",
  ("B", "What is backpressure?", "A mechanism for a slow consumer to signal producers to slow down, preventing unbounded queues, memory exhaustion and exploding latency."),
  ("I", "What can a system do when it receives more work than it can handle?", "Block or slow producers, buffer (bounded), drop/sample, shed load with 429/503, or scale consumers."),
  ("I", "Why are unbounded queues dangerous?", "They hide overload until memory runs out or latency becomes useless; by the time items are processed, clients have given up and retried."),
  ("I", "How does TCP implement backpressure?", "Receive windows: the receiver advertises how much it can accept; when its buffer is full the window shrinks to zero and the sender pauses."),
  ("A", "What is load shedding and how do you decide what to shed?", "Rejecting work early under overload to protect the rest. Shed by priority (keep checkout, drop analytics), by cost, or by deadline (drop requests that will time out anyway)."),
  ("A", "How do reactive streams handle backpressure?", "Pull-based demand: subscribers request(n) items, and publishers never emit more than requested (Reactor, RxJava, Akka Streams)."))

Q("stream-batch",
  ("B", "Batch vs stream processing?", "Batch processes bounded data periodically (hours) with high throughput; stream processes unbounded events continuously with low latency (seconds)."),
  ("I", "Event time vs processing time?", "Event time is when the event happened; processing time is when the system sees it. Correct analytics use event time and handle late events."),
  ("I", "What are watermarks?", "A stream processor's estimate that no events older than time T are still expected, used to decide when a window is complete."),
  ("I", "Tumbling vs sliding vs session windows?", "Tumbling: fixed, non-overlapping. Sliding/hopping: fixed size, overlapping. Session: grouped by activity separated by inactivity gaps."),
  ("A", "Lambda vs Kappa architecture?", "Lambda runs a batch layer (accurate) and a speed layer (fast) and merges them; complex to maintain two code paths. Kappa uses only streaming and reprocesses by replaying the log."),
  ("A", "How do stream processors keep state fault tolerant?", "Local state stores (RocksDB) backed by changelog topics or periodic distributed snapshots (Flink checkpoints); on failure, restore state and replay from the matching offsets."))

Q("scheduler-cron",
  ("B", "What problems arise running cron on multiple servers?", "Jobs run once per server (duplicates), or if you pick one server, it's a single point of failure."),
  ("I", "How do you ensure a scheduled job runs exactly once across a cluster?", "Store jobs in a DB and claim them with row locks (SELECT … FOR UPDATE SKIP LOCKED) or leader election; use leases so a crashed worker's job is re-claimed; make jobs idempotent because rare duplicates still happen."),
  ("I", "How do you scale a scheduler to millions of jobs?", "Bucket jobs by due time (time-partitioned tables or a timing wheel), shard by job id, separate the scheduler (who's due) from workers (execution) with a queue."),
  ("I", "How do you handle job failures?", "Retries with exponential backoff, max attempts, dead-letter storage, alerting, and timeouts with leases."),
  ("A", "What is a timing wheel?", "A circular array of buckets, each holding tasks due in that tick; the pointer advances each tick. O(1) insert and expiry, used in Kafka, Netty, and high-volume timers."),
  ("A", "How do you handle time zones and DST in schedules?", "Store schedules with their time zone, compute next run in that zone, and define behaviour for skipped/repeated hours (run once, skip, or shift)."))

Q("storage-types",
  ("B", "Block vs file vs object storage?", "Block: raw volumes attached to one machine (databases, OS disks). File: hierarchical shared filesystem (NFS). Object: flat key → blob with metadata over HTTP, massive scale and cheap (S3)."),
  ("I", "Why store images and videos in object storage instead of the database?", "Large blobs bloat DB rows, backups and replication; object storage is cheaper, scales to exabytes, is highly durable and integrates with CDNs. Keep only metadata/keys in the DB."),
  ("I", "What is a pre-signed URL?", "A time-limited URL signed by the server that lets a client upload/download directly to object storage without credentials, keeping large transfers off app servers."),
  ("I", "What are storage tiers and lifecycle policies?", "Hot, infrequent-access and archive tiers trade price for access latency/fees; lifecycle rules move or delete objects automatically by age."),
  ("A", "Replication vs erasure coding for durability?", "3× replication: simple, fast reads, 200% overhead. Erasure coding (e.g., 10+4): survives multiple losses with ~40% overhead but costs CPU and slower reconstruction; used for cold/large data."),
  ("A", "How does multipart upload work and why use it?", "Split a large object into parts uploaded in parallel (and retried individually), then complete to assemble; improves throughput and resilience for big files."))

Q("search-engines",
  ("B", "What is an inverted index?", "A map from each term to the list of documents (and positions) containing it, so a search looks up terms instead of scanning documents."),
  ("I", "What happens during text analysis/indexing?", "Tokenising, lowercasing, removing stop words, stemming/lemmatisation, synonyms; the same analyser runs on queries."),
  ("I", "How are search results ranked?", "Text relevance (TF-IDF/BM25), plus signals like popularity, recency, personalisation and business rules; often a learning-to-rank model re-ranks top candidates."),
  ("I", "How do you keep Elasticsearch in sync with the primary database?", "Index from change events (CDC/outbox via Kafka) rather than dual writes; support full reindex from the DB; accept ~1 s near-real-time lag."),
  ("A", "How does Elasticsearch scale?", "An index is split into shards distributed across nodes, each with replicas; queries scatter to shards and gather/merge top results."),
  ("A", "Why shouldn't search be your source of truth?", "It's eventually consistent, lacks transactions/constraints, and can be rebuilt; the DB remains authoritative."))

Q("timeseries-analytics",
  ("B", "What is OLTP vs OLAP?", "OLTP: many small transactional reads/writes on current data (orders). OLAP: large analytical scans and aggregations over historical data (dashboards)."),
  ("I", "Why are column stores fast for analytics?", "They read only needed columns, compress similar values extremely well, and use vectorised execution over column chunks."),
  ("I", "What makes time-series data special?", "Append-mostly, time-ordered, high write volume, queries over recent ranges, and old data needed only in aggregate, so you partition by time, downsample and expire old data."),
  ("I", "What is downsampling/rollup?", "Pre-aggregating raw points into coarser intervals (1 s → 1 min → 1 h) for long-term storage and fast dashboards."),
  ("A", "What is high cardinality and why does it hurt time-series databases?", "Too many unique label combinations (e.g., user_id as a tag) create millions of series, blowing up memory and index size. Keep labels bounded; put ids in logs/traces."),
  ("A", "How do star schemas work in a data warehouse?", "A central fact table (events with measures and foreign keys) joined to denormalised dimension tables (date, product, customer) for simple, fast analytical queries."))
