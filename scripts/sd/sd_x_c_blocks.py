"""Detailed explanations with diagrams: Building Blocks tab."""
from sd_x_util import X, P, H, AN, KEY, FLOW, SEQ, NOTE, ER, TABLE, CALC, BARS, CODE, UML, STATE

X("load-balancer",
  P("A load balancer (LB) is the single address clients talk to; it spreads requests over a pool of healthy servers, removes dead ones via **health checks**, and lets you add or remove servers without clients noticing."),
  FLOW("Where load balancers sit", [["u:Clients"], ["DNS (GeoDNS)"], ["L7 load balancer (active) + standby"], ["App 1", "App 2", "App 3"], ["L4 LB (internal)"], ["db:DB replicas"]],
       [["Clients", "DNS (GeoDNS)"], ["DNS (GeoDNS)", "L7 load balancer (active) + standby", "nearest region"], ["L7 load balancer (active) + standby", "App 1"], ["L7 load balancer (active) + standby", "App 2"], ["L7 load balancer (active) + standby", "App 3"],
        ["App 2", "L4 LB (internal)"], ["L4 LB (internal)", "DB replicas"]]),
  SEQ("A server dies: health checks route around it", ["Load balancer", "App 1", "App 2"],
      [["Load balancer", "App 1", "GET /health (every 5 s)"], ["App 1", "Load balancer", "200", "r"], ["Load balancer", "App 2", "GET /health"], ["App 2", "Load balancer", "timeout ×3", "r", "After N consecutive failures the LB marks App 2 unhealthy."],
       NOTE(["Load balancer", "App 2"], "App 2 removed from the pool"), ["Load balancer", "App 1", "all new requests go here (and other healthy servers)", "", "When App 2 passes checks again it's re-added. Connection draining lets in-flight requests finish during deploys."]]),
  TABLE("L4 vs L7", ["", "L4 (transport)", "L7 (application)"], [["sees", "IP + port", "full HTTP: path, headers, cookies"], ["can do", "forward TCP/UDP fast", "path routing, TLS termination, retries, header rewrite, auth, compression"],
                                                             ["speed", "very fast, cheap", "more CPU"], ["examples", "AWS NLB, LVS", "AWS ALB, Nginx, Envoy, HAProxy (both)"]]),
  KEY("The LB itself must not be a single point of failure: run an active–passive pair sharing a virtual IP (keepalived), or use a managed cloud LB that is already redundant.", "Avoid the SPOF"))

X("lb-algorithms",
  P("Same 6 requests, 3 servers, different algorithms. Server C is twice as powerful (weight 2); request 4 is a slow upload that keeps server A busy."),
  TABLE("Which server gets each request", ["Request", "Round robin", "Weighted RR (A1 B1 C2)", "Least connections", "IP hash (client)"],
        [["1 (user u1)", "A", "A", "A", "hash(u1) → B"], ["2 (u2)", "B", "B", "B", "hash(u2) → A"], ["3 (u3)", "C", "C", "C", "hash(u3) → C"], ["4 (u1, slow upload)", "A", "C", "A (all idle again)", "B (same user, same server)"],
         ["5 (u4)", "B", "A", "B (A still busy)", "hash(u4) → A"], ["6 (u5)", "C", "B", "C", "hash(u5) → C"]]),
  TABLE("When to use", ["Algorithm", "Best for", "Weakness"], [["Round robin", "identical servers, similar requests", "ignores load"], ["Weighted RR", "mixed server sizes", "static weights"], ["Least connections", "long or uneven requests (uploads, WebSockets)", "needs connection tracking"],
                                                             ["Least response time", "latency-sensitive", "noisy signal"], ["IP / consistent hash", "stickiness, cache locality", "uneven if few big clients"], ["Power of two choices", "huge pools: pick 2 random, use the less loaded", "slight randomness"]]))

X("cdn",
  P("A CDN keeps copies of content on **edge servers** in hundreds of cities. A user in Pune is served from a Mumbai edge (5 ms away) instead of the origin in Virginia (200 ms away)."),
  SEQ("First request (miss) vs second request (hit)", ["User (Pune)", "CDN edge (Mumbai)", "Origin (Virginia)"],
      [["User (Pune)", "CDN edge (Mumbai)", "GET /img/cat.jpg"], ["CDN edge (Mumbai)", "Origin (Virginia)", "MISS → fetch from origin", "", "Only the first user in a region pays the long trip."], ["Origin (Virginia)", "CDN edge (Mumbai)", "image + Cache-Control: max-age=86400", "r"],
       ["CDN edge (Mumbai)", "User (Pune)", "image (≈ 210 ms total)", "r"], ["User (Pune)", "CDN edge (Mumbai)", "another user: GET /img/cat.jpg"], ["CDN edge (Mumbai)", "User (Pune)", "HIT → image (≈ 10 ms)", "r", "Served from the edge cache until max-age expires."]]),
  TABLE("Push vs pull CDN", ["", "Pull (lazy)", "Push"], [["how content arrives", "edge fetches on first miss", "you upload ahead of time"], ["good for", "most websites", "big files you know will be popular (game patches, video)"], ["first request", "slow", "fast"]]),
  KEY("Invalidate by **versioned file names** (`app.3f9c.js`) instead of purging: new deploy = new URL, so caches never serve stale code. CDNs also absorb DDoS traffic and terminate TLS near users.", "Practical tip"))

X("caching",
  P("A cache stores the result of expensive work (DB queries, rendered pages, API calls) in fast memory so repeat requests skip the work. Caches exist at every layer:"),
  FLOW("Cache layers from user to database", [["u:Browser cache"], ["CDN edge cache"], ["c:App in-process cache"], ["c:Distributed cache (Redis)"], ["db:DB buffer pool"]],
       [["Browser cache", "CDN edge cache", "miss"], ["CDN edge cache", "App in-process cache", "miss"], ["App in-process cache", "Distributed cache (Redis)", "miss"], ["Distributed cache (Redis)", "DB buffer pool", "miss"]]),
  CALC("Why hit ratio is everything", [("DB read latency", "db = 10", "ms"), ("Cache read latency", "c = 0.5", "ms"), ("Average latency at 90% hit ratio", "0.9 * c + 0.1 * db", "ms"),
                                       ("Average latency at 99% hit ratio", "0.99 * c + 0.01 * db", "ms"), ("DB load at 90% hits (of 50k reads/s)", "50000 * 0.1", "/s"), ("DB load at 99% hits", "50000 * 0.01", "/s", "10× less load from a 9-point hit-ratio gain")]),
  TABLE("What to cache, what not to", ["Cache well", "Cache carefully / not"], [["read-heavy, rarely changing data (profiles, product pages)", "balances, inventory counts (correctness)"], ["expensive computed results (feeds, recommendations)", "per-user data with low reuse"], ["sessions, rate-limit counters", "data that must be instantly consistent"]]))

X("cache-strategies",
  SEQ("Cache-aside (lazy loading): the most common", ["App", "Redis", "Database"],
      [["App", "Redis", "GET user:42"], ["Redis", "App", "nil (miss)", "r"], ["App", "Database", "SELECT … WHERE id = 42"], ["Database", "App", "row", "r"], ["App", "Redis", "SET user:42 row EX 600"],
       NOTE(["App", "Database"], "on update"), ["App", "Database", "UPDATE users SET … WHERE id = 42"], ["App", "Redis", "DEL user:42", "", "Delete (not update) the key so the next read reloads fresh data."]]),
  SEQ("Write-through vs write-behind", ["App", "Cache", "Database"],
      [NOTE(["App", "Database"], "Write-through"), ["App", "Cache", "write x = 5"], ["Cache", "Database", "write x = 5 (synchronously)"], ["Cache", "App", "OK after both", "r", "Cache always fresh; writes are slower."],
       NOTE(["App", "Database"], "Write-behind (write-back)"), ["App", "Cache", "write x = 5"], ["Cache", "App", "OK immediately", "r"], ["Cache", "Database", "flush later in batches", "a", "Fast writes, but data is lost if the cache dies before flushing."]]),
  TABLE("Comparison", ["Strategy", "Read path", "Write path", "Risk"], [["Cache-aside", "app checks cache, loads on miss", "write DB, delete key", "brief staleness; race on concurrent update"], ["Read-through", "cache loads from DB itself", "—", "cache library must know the DB"],
                                                                     ["Write-through", "hits", "cache + DB synchronously", "write latency"], ["Write-behind", "hits", "cache now, DB later", "data loss"], ["Write-around", "miss after write", "DB only", "first read after write is slow"]]))

X("cache-eviction",
  P("When the cache is full, something must go. Watch LRU (least recently used) with capacity 3 on the access sequence **A B C A D B**:"),
  TABLE("LRU, capacity 3 (most recent on the right)", ["Access", "Hit?", "Cache after", "Evicted"],
        [["A", "miss", "A", ""], ["B", "miss", "A B", ""], ["C", "miss", "A B C", ""], ["A", "hit", "B C A", ""], ["D", "miss", "C A D", "B (least recently used)"], ["B", "miss", "A D B", "C"]]),
  TABLE("Same sequence with LFU and FIFO", ["Policy", "Evicts when D arrives", "Why"], [["LRU", "B", "B was touched longest ago"], ["LFU", "B (A has 2 uses; B and C have 1, tie broken by age)", "keeps the most frequently used"], ["FIFO", "A", "A entered first, even though it was just used: FIFO ignores reuse"]]),
  TABLE("Choosing", ["Policy", "Good when"], [["LRU", "recent items are likely reused (default for most caches)"], ["LFU", "stable popularity (top products)"], ["TTL", "data goes stale after a known time"], ["Random / approximated LRU", "huge caches (Redis samples 5 keys and evicts the oldest)"]]))

X("cache-problems",
  SEQ("Cache stampede (thundering herd) and the fix", ["1,000 requests", "Redis", "Database"],
      [["1,000 requests", "Redis", "GET hot:key"], ["Redis", "1,000 requests", "expired → miss for everyone", "r"], ["1,000 requests", "Database", "1,000 identical queries at once", "", "DB overloads; latency explodes."],
       NOTE(["1,000 requests", "Database"], "Fix: single-flight lock"), ["1,000 requests", "Redis", "SET lock:key NX EX 5 (one wins)"], ["1,000 requests", "Database", "only the winner queries"], ["1,000 requests", "Redis", "winner SETs value; others wait/retry or get the stale value", "", "Also: jittered TTLs, refresh-ahead before expiry."]]),
  TABLE("The classic problems", ["Problem", "What happens", "Fix"], [["Stampede", "a hot key expires; everyone hits the DB", "lock / single-flight, early refresh, jittered TTL"], ["Penetration", "requests for keys that don't exist always miss", "cache the 'not found' briefly; Bloom filter of valid keys"],
        ["Avalanche", "many keys expire at once or the cache restarts", "random TTL spread, warm-up, replicas"], ["Hot key", "one key gets millions of reads, one Redis node melts", "local in-process cache, replicate key as key#1..key#N"], ["Inconsistency", "DB updated, cache still old", "delete-after-write, short TTL, CDC-driven invalidation"]]))

X("redis-memcached",
  TABLE("Redis data structures and what they're for", ["Type", "Command example", "Use case"],
        [["String", "INCR views:post:9", "counters, cached JSON, locks (SET NX)"], ["Hash", "HSET user:42 name Asha city Pune", "objects"], ["List", "LPUSH feed:42 post9 ; LTRIM feed:42 0 799", "recent items, simple queues"],
         ["Set", "SADD online u1 u2", "unique members, tags"], ["Sorted set", "ZINCRBY leaderboard 50 asha ; ZREVRANGE leaderboard 0 9", "leaderboards, rate-limit windows, scheduling"], ["Stream", "XADD orders * id 9", "event log with consumer groups"],
         ["HyperLogLog / Bitmap / Geo", "PFADD, SETBIT, GEOSEARCH", "unique counts, daily active flags, nearby search"]]),
  TABLE("Redis vs Memcached", ["", "Redis", "Memcached"], [["data types", "rich (above)", "strings only"], ["persistence", "RDB snapshots + AOF log", "none"], ["replication / cluster", "built in (16,384 hash slots)", "client-side sharding"],
                                                       ["threads", "single-threaded command execution (I/O threads)", "multi-threaded"], ["choose when", "almost always", "pure, simple, huge key-value cache"]]),
  KEY("Redis commands are atomic, and a Lua script runs atomically too, which is why Redis is used for counters, rate limiters and locks, not just caching.", "Why Redis is everywhere"))

X("message-queues",
  P("A queue lets a **producer** hand work to **consumers** without waiting for it: the API replies immediately, and workers process at their own pace. This decouples services, absorbs spikes, and lets failed jobs be retried."),
  SEQ("Upload a video without making the user wait", ["Client", "API", "Queue", "Transcode worker"],
      [["Client", "API", "POST /videos"], ["API", "Queue", "publish {videoId: 7}"], ["API", "Client", "202 Accepted (processing…)", "r", "The user isn't blocked by a 5-minute transcode."],
       ["Transcode worker", "Queue", "receive message (invisible for 30 min)"], ["Transcode worker", "Transcode worker", "transcode…"], ["Transcode worker", "Queue", "ACK → message deleted", "", "If the worker crashes before ACK, the message becomes visible again and another worker retries it."]]),
  FLOW("Point-to-point vs publish/subscribe", [["Producer A", "Publisher B"], ["q:Queue", "q:Topic"], ["Worker 1", "Worker 2", "Email svc", "Search svc"]],
       [["Producer A", "Queue"], ["Queue", "Worker 1", "msg 1"], ["Queue", "Worker 2", "msg 2"], ["Publisher B", "Topic"], ["Topic", "Email svc", "every msg"], ["Topic", "Search svc", "every msg"]]),
  TABLE("Must-know features", ["Feature", "Why"], [["ack / visibility timeout", "retry if a consumer dies"], ["dead-letter queue", "park messages that fail N times"], ["retries with backoff", "transient failures"], ["ordering (FIFO / partition key)", "per-entity order"], ["idempotent consumers", "at-least-once delivery means duplicates"]]))

X("kafka",
  P("Kafka is a **distributed append-only log**. A topic is split into **partitions**; each message gets an **offset**. Messages aren't deleted on read: consumers just remember their offset, so many groups can read the same data, and replay is possible."),
  FLOW("Topic 'orders' with 3 partitions and a consumer group", [["Producer: key = userId"], ["q:P0: offsets 0..812", "q:P1: offsets 0..790", "q:P2: offsets 0..805"], ["Consumer 1 (group 'billing')", "Consumer 2 (group 'billing')"]],
       [["Producer: key = userId", "P0: offsets 0..812", "hash(key) % 3"], ["Producer: key = userId", "P1: offsets 0..790"], ["Producer: key = userId", "P2: offsets 0..805"], ["P0: offsets 0..812", "Consumer 1 (group 'billing')"], ["P1: offsets 0..790", "Consumer 1 (group 'billing')"], ["P2: offsets 0..805", "Consumer 2 (group 'billing')"]]),
  TABLE("Key rules", ["Rule", "Consequence"], [["order is guaranteed only within a partition", "use a key (userId, orderId) so related events go to the same partition"], ["one partition → at most one consumer per group", "max parallelism = number of partitions"],
        ["each partition is replicated (RF = 3) with a leader", "acks=all + min.insync.replicas=2 → no loss if a broker dies"], ["consumers commit offsets", "commit after processing → at-least-once"], ["retention by time/size, or compaction by key", "replay history; rebuild state"]]),
  CALC("Sizing a cluster", [("Events per second", "e = 200000", "/s"), ("Average event size", "s = 1000", "B"), ("Ingest bandwidth", "e * s", "B/s"), ("With replication factor 3, per day", "e * s * 3 * 86400", "B"),
                            ("Partitions at ~10 MB/s per partition", "e * s / 10e6", "", "→ use 24–32 for headroom")]))

X("delivery-semantics",
  SEQ("Why exactly-once is hard: where duplicates come from", ["Producer", "Broker", "Consumer", "DB"],
      [["Producer", "Broker", "send msg #5"], ["Broker", "Producer", "ack lost in network", "r", "Producer can't tell if #5 was stored, so it retries."], ["Producer", "Broker", "send msg #5 again → duplicate"],
       ["Consumer", "Broker", "read #5"], ["Consumer", "DB", "apply #5 (charge ₹500)"], ["Consumer", "Consumer", "crash before committing offset", "", "On restart the consumer re-reads #5 and charges again, unless the write is idempotent."]]),
  TABLE("The three guarantees", ["Guarantee", "How", "Risk", "Use for"], [["At-most-once", "commit offset before processing", "lost messages", "metrics, logs"], ["At-least-once", "commit after processing; retry", "duplicates", "almost everything (+ idempotency)"],
                                                                     ["Exactly-once (effectively)", "idempotent producer + transactions, or dedup by message id in the same DB transaction", "complexity", "payments, ledgers"]]),
  CODE("Effectively-once consumer: dedup in the same transaction", """BEGIN;
INSERT INTO processed_messages(msg_id) VALUES ('m-5');   -- fails on duplicate (primary key)
UPDATE wallets SET balance = balance - 500 WHERE user_id = 42;
COMMIT;                                                    -- both or neither""", "sql"))

X("backpressure",
  P("Backpressure is how a slow consumer tells a fast producer to slow down. Without it, queues grow until memory runs out or latency becomes useless."),
  CALC("Queue growth without backpressure", [("Producer rate", "p = 5000", "/s"), ("Consumer capacity", "c = 4000", "/s"), ("Backlog growth", "p - c", "/s"), ("Backlog after 1 hour", "(p - c) * 3600", ""), ("Time for a new item to be processed after 1 h", "(p - c) * 3600 / c / 60", "minutes", "useless for real-time")]),
  TABLE("Strategies", ["Strategy", "How", "Example"], [["Block / slow producer", "bounded queue; put() waits", "TCP flow control, Java BlockingQueue"], ["Drop / sample", "discard extra or low-priority items", "metrics, video frames"], ["Shed load", "reject with 429/503", "API under overload"],
                                                    ["Scale consumers", "autoscale on lag", "Kafka consumer lag → more pods"], ["Buffer durably", "spill to Kafka/disk", "absorb short spikes"], ["Pull-based consumption", "consumer requests N items", "Reactive Streams, Kafka"]]))

X("stream-batch",
  FLOW("Lambda vs Kappa architecture", [["Events (Kafka)"], ["Batch layer (Spark, hourly)", "Stream layer (Flink, seconds)"], ["db:Serving view (merged)"]],
       [["Events (Kafka)", "Batch layer (Spark, hourly)", "complete, slow"], ["Events (Kafka)", "Stream layer (Flink, seconds)", "fast, approximate"], ["Batch layer (Spark, hourly)", "Serving view (merged)"], ["Stream layer (Flink, seconds)", "Serving view (merged)"]],
       "Kappa drops the batch layer: everything is a stream, and reprocessing = replay the log."),
  TABLE("Windows in stream processing (clicks per page)", ["Window", "Definition", "Example"], [["Tumbling", "fixed, non-overlapping", "clicks per 1-minute bucket"], ["Sliding / hopping", "fixed size, overlapping", "last 5 minutes, updated every minute"], ["Session", "ends after a gap of inactivity", "a user's browsing session (30 min gap)"]]),
  TABLE("Batch vs stream", ["", "Batch", "Stream"], [["latency", "minutes–hours", "milliseconds–seconds"], ["input", "bounded files/tables", "unbounded events"], ["tools", "Spark, Hive, BigQuery", "Flink, Kafka Streams, Spark Structured Streaming"], ["hard parts", "big joins, cost", "late events (watermarks), state, exactly-once"]]))

X("scheduler-cron",
  SEQ("Distributed scheduler: run each job exactly once even with 3 scheduler nodes", ["Scheduler A", "Scheduler B", "DB (jobs table)", "Worker"],
      [["Scheduler A", "DB (jobs table)", "SELECT jobs due ≤ now FOR UPDATE SKIP LOCKED LIMIT 100"], ["Scheduler B", "DB (jobs table)", "same query → skips rows A locked", "", "Row locks make each job claimed by exactly one scheduler."],
       ["Scheduler A", "DB (jobs table)", "UPDATE status = RUNNING, lease_until = now + 5 min"], ["Scheduler A", "Worker", "run job 77"], ["Worker", "DB (jobs table)", "status = DONE; compute next_run from cron expression"],
       NOTE(["Scheduler A", "Worker"], "if the worker dies, lease_until passes and the job is picked up again")]),
  ER("Jobs table", [("jobs", "PostgreSQL", [("job_id", "bigint", "PK"), ("cron_expr", "text", ""), ("next_run_at", "timestamptz", "IDX"), ("status", "enum", ""), ("lease_until", "timestamptz", ""), ("attempts", "int", ""), ("payload", "jsonb", "")], "index on (status, next_run_at)")]),
  KEY("Jobs will occasionally run twice (lease expiry, retries), so make them idempotent. For huge scale, bucket jobs by time (a 'timing wheel' or per-minute partitions) instead of scanning one table.", "Design rules"))

X("storage-types",
  TABLE("Block vs file vs object storage", ["", "Block", "File", "Object"], [["unit", "fixed-size blocks on a volume", "files in folders", "objects (key → bytes + metadata)"], ["access", "mounted disk (one machine)", "NFS/SMB, shared", "HTTP API (PUT/GET)"],
        ["examples", "AWS EBS, SAN", "EFS, NFS", "S3, GCS, Azure Blob"], ["latency", "lowest", "low", "higher (tens of ms)"], ["scale / cost", "TBs, expensive", "TBs", "exabytes, cheap"], ["use for", "databases, OS disks", "shared files, legacy apps", "images, videos, backups, data lakes"]]),
  SEQ("Uploading big files directly to object storage", ["Client", "API", "Object store (S3)"],
      [["Client", "API", "I want to upload cat.mp4 (500 MB)"], ["API", "Client", "pre-signed PUT URL (valid 15 min)", "r"], ["Client", "Object store (S3)", "multipart upload directly", "", "The API servers never carry the bytes."], ["Object store (S3)", "API", "event: upload complete", "a"], ["API", "API", "save metadata row (owner, key, size)"]]),
  TABLE("Storage tiers (S3-style)", ["Tier", "Access", "Relative cost"], [["Hot / Standard", "milliseconds, frequent", "1×"], ["Infrequent access", "milliseconds, retrieval fee", "~0.5×"], ["Archive (Glacier)", "minutes–hours", "~0.1×"]]))

X("search-engines",
  P("Full-text search uses an **inverted index**: for each word, the list of documents containing it. Here's one built from three tiny documents:"),
  TABLE("Documents", ["Doc", "Text"], [["1", "red running shoes"], ["2", "blue running jacket"], ["3", "red jacket"]]),
  TABLE("Inverted index (after lowercasing, stemming 'running' → 'run')", ["Term", "Postings (doc ids)"], [["red", "1, 3"], ["run", "1, 2"], ["shoe", "1"], ["blue", "2"], ["jacket", "2, 3"]],
        "Query 'red jacket' → intersect {1,3} and {2,3} → doc 3 for AND; union {1,2,3} ranked by BM25 for OR."),
  FLOW("Keeping a search index in sync", [["db:Primary DB (source of truth)"], ["CDC / outbox events"], ["q:Kafka"], ["Indexer"], ["db:Elasticsearch shards + replicas"], ["u:Search API"]],
       [["Primary DB (source of truth)", "CDC / outbox events"], ["CDC / outbox events", "Kafka"], ["Kafka", "Indexer"], ["Indexer", "Elasticsearch shards + replicas"], ["Search API", "Elasticsearch shards + replicas", "query"]]),
  KEY("Elasticsearch/OpenSearch is a search index, not the system of record: it's near-real-time (~1 s refresh) and can be rebuilt from the DB. Relevance = BM25 text score + business signals (popularity, recency).", "Design rules"))

X("timeseries-analytics",
  TABLE("Row store vs column store for analytics", ["Query: average price of all orders in 2025", "Row store (PostgreSQL)", "Column store (ClickHouse, BigQuery)"],
        [["data read", "every column of every row", "only the price and date columns"], ["compression", "low (mixed types per row)", "very high (similar values together)"], ["best for", "OLTP: fetch/update one order", "OLAP: aggregate millions of rows"]]),
  CALC("Why columnar wins for scans", [("Rows", "r = 1e9", ""), ("Row size (30 columns)", "rs = 300", "B"), ("Row store scans", "r * rs", "B"), ("Column store scans 2 columns × 8 B, then ~5× compression", "r * 16 / 5", "B"), ("Speed-up", "(r * rs) / (r * 16 / 5)", "×")]),
  TABLE("Time-series tricks", ["Technique", "What"], [["downsampling / rollups", "keep raw 1 s data for 7 days, 1-min averages for 90 days, 1-hour for years"], ["time partitioning", "one partition per day: drop old data instantly"], ["delta + gorilla encoding", "store differences between timestamps/values: ~1.4 bytes per point"],
                                                     ["tools", "Prometheus, InfluxDB, TimescaleDB, Druid, ClickHouse"]]))
