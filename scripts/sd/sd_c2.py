"""System Design concepts, part 2: Building blocks (load balancing, CDN, caching, queues & streaming, storage types)."""
from sd_util import C

LOAD_BALANCING = [
C("load-balancer", "Load balancers", "Basic",
  "A load balancer spreads incoming requests across many servers so no single one is overwhelmed, and stops sending traffic to servers that are down.",
  """### Why
- **Scale out**: add servers behind it.
- **Availability**: health checks remove dead servers automatically.
- **Zero-downtime deploys**: drain one server, update it, put it back.

### Where they sit
Between users and web servers, between web servers and internal services, and in front of databases/caches (e.g. read-replica pools).

### L4 vs L7
|Layer 4 (transport)|Layer 7 (application)|
|Routes by IP + port; doesn't read the request|Reads HTTP: path, headers, cookies|
|Very fast, handles millions of connections|Smarter: `/api` → API servers, `/static` → CDN origin|
|Can't do TLS termination per path or content routing|Terminates TLS, compresses, rewrites, rate limits|
|AWS NLB, LVS, Maglev|AWS ALB, NGINX, HAProxy, Envoy|

### Health checks
Active (LB pings `/health` every few seconds) or passive (watch for failed requests). Mark unhealthy after N failures, healthy again after M successes.

### Avoiding the LB as a single point of failure
Run LBs in pairs (**active–passive** with a floating virtual IP via VRRP/keepalived, or **active–active**), across availability zones. Cloud LBs are managed and redundant. At global scale use **DNS / Anycast** to spread across many LB clusters (**GSLB**).""",
  diagram={"rows": [["u:Clients"], ["Load balancer (active)", "Load balancer (standby)"], ["Server A", "Server B", "Server C"]],
           "edges": [["Clients", "Load balancer (active)"], ["Load balancer (active)", "Load balancer (standby)", "heartbeat"], ["Load balancer (active)", "Server A"], ["Load balancer (active)", "Server B"], ["Load balancer (active)", "Server C"]]},
  lab="lb"),

C("lb-algorithms", "Load-balancing algorithms", "Intermediate",
  "How the load balancer picks a server: round robin, weighted, least connections, least response time, IP hash, consistent hashing, random / power of two choices.",
  """|Algorithm|How|Use when|
|Round robin|Next server in turn|Servers identical, requests similar cost|
|Weighted round robin|Bigger servers get more turns|Mixed machine sizes, canary (5% weight)|
|Least connections|Server with fewest active connections|Requests vary in length (long uploads, WebSockets)|
|Least response time|Fastest + fewest connections|Latency-sensitive services|
|IP hash / sticky|`hash(client IP) % N`|Need the same client on the same server (session affinity)|
|Consistent hashing|Hash ring; adding a server moves only ~1/N keys|Caches and stateful shards|
|Power of two choices|Pick 2 random servers, send to the less loaded|Large fleets; nearly as good as least-connections, cheaper|

### Sticky sessions
Keep a user on one server (cookie or IP hash). Convenient for in-memory sessions but hurts balance and failover, so prefer **stateless servers + shared session store (Redis)**.""",
  lab="lb", see=("consistent-hashing",)),

C("cdn", "CDN (Content Delivery Network)", "Basic",
  "A network of servers around the world (edge locations) that cache your static content close to users, so a user in Chennai gets images from Chennai, not Virginia.",
  """### How it works
1. DNS points `cdn.myapp.com` to the **nearest edge** (GeoDNS or Anycast).
2. Edge has the file? Serve it (**cache hit**, ~10–30 ms).
3. Miss: edge fetches from your **origin** (S3 or your servers), caches it per `Cache-Control` TTL, then serves.

### Push vs pull CDNs
- **Pull** (most common): edge fetches from origin on first request. Easy; first user pays the miss.
- **Push**: you upload content to the CDN ahead of time. Good for big, predictable files (game patches, video releases).

### What to put on a CDN
Images, video segments, JS/CSS bundles, downloads, and increasingly **dynamic content** at the edge (edge functions, API caching with short TTL).

### Invalidation and versioning
Purging is slow and costly; instead use **versioned file names** (`app.3f9a2c.js`) with a long TTL, and change the name on each deploy.

### Benefits
Lower latency, far less origin load and bandwidth cost, absorbs DDoS traffic.
Examples: Cloudflare, Akamai, AWS CloudFront, Fastly. Netflix runs its own CDN (Open Connect) inside ISPs.""",
  diagram={"rows": [["u:User in India", "u:User in USA"], ["x:Edge Mumbai", "x:Edge Virginia"], ["db:Origin (S3)"]],
           "edges": [["User in India", "Edge Mumbai", "10 ms"], ["User in USA", "Edge Virginia", "10 ms"], ["Edge Mumbai", "Origin (S3)", "miss only"], ["Edge Virginia", "Origin (S3)", "miss only"]]}),
]

CACHING = [
C("caching", "Caching: the basics", "Basic",
  "A cache keeps a copy of frequently used data in fast memory so you don't recompute it or hit the slow database every time.",
  """Reads from RAM take ~100 ns; a database query takes 1–10 ms or more. If 90% of requests hit the cache, the database sees 10x less load.

### Cache layers (from user to data)
1. **Browser cache** (HTTP `Cache-Control`, `ETag`).
2. **CDN** for static/edge content.
3. **Load balancer / reverse proxy cache** (NGINX, Varnish).
4. **Application cache**: in-process (Caffeine/Guava in Java) — fastest, but per-server.
5. **Distributed cache**: Redis / Memcached shared by all servers.
6. **Database cache**: buffer pool, query cache.

### Key terms
- **Hit ratio** = hits ÷ (hits + misses). Aim for 80–99%.
- **TTL** (time to live): entry expires after N seconds.
- **Eviction**: what to remove when memory is full (LRU, LFU...).
- **Invalidation**: removing/updating entries when the source changes — the famously hard part.

### What to cache
Data read far more than written: user profiles, product pages, feeds, session tokens, computed results (recommendations), rendered HTML.

### What not to cache
Rapidly changing data where staleness hurts (bank balance during payment), or data each user reads once.""",
  analogy="Keeping your most-used books on your desk (cache) instead of walking to the library (database) each time.",
  diagram={"rows": [["App server"], ["c:Cache (Redis)", "db:Database"]], "edges": [["App server", "Cache (Redis)", "1 get(key)"], ["App server", "Database", "2 on miss"], ["App server", "Cache (Redis)", ""]]},
  lab="cache"),

C("cache-strategies", "Cache read/write strategies", "Intermediate",
  "Cache-aside, read-through, write-through, write-behind (write-back), write-around and refresh-ahead: who loads and updates the cache, and when.",
  """|Strategy|How it works|Pros|Cons|
|**Cache-aside** (lazy loading)|App reads cache; on miss reads DB and puts value in cache. On write: update DB, **delete** cache key|Simple, only caches what's used, cache failure isn't fatal|First read is slow; possible stale data|
|**Read-through**|App only talks to cache; the cache loads from DB on miss|Cleaner app code|Needs a cache library/provider that supports it|
|**Write-through**|Write goes to cache and DB together (synchronously)|Cache always fresh|Slower writes; caches data that may never be read|
|**Write-behind / write-back**|Write to cache, which flushes to DB later in batches|Very fast writes, absorbs spikes|Data loss if cache dies before flush; complex|
|**Write-around**|Write to DB only; cache filled on later reads|Avoids polluting cache with write-once data|Recent writes miss the cache|
|**Refresh-ahead**|Refresh popular keys before they expire|No miss latency for hot keys|Wasted work if prediction is wrong|

### The default answer
**Cache-aside + TTL + delete-on-write** for most read-heavy systems.

```java
User getUser(long id) {
    String key = "user:" + id;
    User u = cache.get(key);
    if (u == null) {                       // miss
        u = db.findUser(id);
        cache.set(key, u, Duration.ofMinutes(10));
    }
    return u;
}
void updateUser(User u) {
    db.save(u);
    cache.delete("user:" + u.id);          // delete, don't update: avoids racing writers
}
```

Why delete instead of update? Two concurrent writers can update the cache in the opposite order to the DB, leaving it permanently wrong; deleting just forces a fresh load.""",
  tips=["Say which strategy and why; mention TTL as a safety net for any missed invalidation."]),

C("cache-eviction", "Cache eviction policies", "Intermediate",
  "When the cache is full, which entry goes? LRU (least recently used), LFU (least frequently used), FIFO, random, TTL-based.",
  """|Policy|Evicts|Good for|
|**LRU**|The entry not used for the longest time|General purpose; most common default|
|**LFU**|The entry used the fewest times|Stable popularity (top products)|
|**FIFO**|The oldest inserted entry|Simple; ignores usage|
|**Random**|A random entry|Surprisingly decent, very cheap|
|**TTL**|Expired entries|Freshness guarantees|

### Implementing LRU in O(1)
A **HashMap + doubly linked list**: the map finds the node; the list keeps recency order (move to head on access, evict from tail). In Java, `LinkedHashMap` with `accessOrder=true` and `removeEldestEntry` does it in a few lines. This is LeetCode 146, asked very often.

### Redis policies
`allkeys-lru`, `allkeys-lfu`, `volatile-lru` (only keys with TTL), `noeviction`... Redis uses *approximated* LRU by sampling keys to save memory.

### Variants
**W-TinyLFU** (used by Java's Caffeine) combines recency and frequency for higher hit rates; **ARC** adapts between LRU and LFU.""",
  lab="cache", see=("lru-lld",)),

C("cache-problems", "Cache problems: stampede, penetration, avalanche, hot keys, consistency", "Advanced",
  "Things that go wrong with caches at scale and the standard fixes.",
  """### Cache stampede (thundering herd / dog-piling)
A hot key expires and 10,000 requests miss at once and all hit the DB.
- **Fixes**: a **lock / single-flight** so only one request rebuilds while others wait or get the stale value; **probabilistic early refresh**; refresh-ahead for hot keys.

### Cache penetration
Requests for keys that **don't exist** (e.g. random IDs from an attacker) always miss and hit the DB.
- **Fixes**: cache the 'not found' result with a short TTL; put a **Bloom filter** of valid IDs in front.

### Cache avalanche
Many keys expire at the same time (all set with TTL 3600 at startup), or the cache cluster dies, so the DB is flooded.
- **Fixes**: add **random jitter** to TTLs; replicate the cache; circuit breakers and rate limits in front of the DB; warm the cache before switching traffic.

### Hot keys
One key (a celebrity's profile) gets millions of reads per second, overloading one cache shard.
- **Fixes**: local in-process cache for that key; **replicate the key** (`key#1..key#10`, read a random copy); detect hot keys automatically.

### Big keys
A 50 MB value blocks a single-threaded Redis. Split it, compress it, or store it in object storage.

### Cache–DB consistency
- Delete-after-write can still race: reader loads old value, writer updates DB and deletes, reader then writes the stale value back. Fixes: short TTL, **delayed double delete**, or invalidate from the DB change stream (**CDC** → delete keys).
- If you need strong consistency, don't cache that data, or use versioned values.""",
  tips=["Naming these three (stampede, penetration, avalanche) with fixes is a strong senior signal."],
  see=("bloom-filter", "cdc")),

C("redis-memcached", "Redis vs Memcached, and distributed caches", "Intermediate",
  "Both are in-memory key–value stores. Memcached is a simple multi-threaded cache; Redis adds rich data structures, persistence, replication and clustering.",
  """|Redis|Memcached|
|Data structures: strings, hashes, lists, sets, **sorted sets**, streams, bitmaps, HyperLogLog, geo|Strings (blobs) only|
|Persistence (RDB snapshots, AOF log)|None|
|Replication, Sentinel failover, Redis Cluster (16,384 hash slots)|Client-side sharding only|
|Mostly single-threaded command execution (simple, atomic ops), Lua scripts|Multi-threaded, very efficient for plain get/set|
|Pub/Sub, streams, transactions|—|

### Redis is used for much more than caching
- **Sessions**, **rate limiting** counters, **leaderboards** (sorted sets `ZADD/ZREVRANGE`), **distributed locks**, queues (lists/streams), **counting unique visitors** (HyperLogLog), geo search (`GEOSEARCH`), pub/sub for chat.

### Scaling a distributed cache
- **Shard** keys across nodes with consistent hashing (Redis Cluster uses hash slots).
- **Replicate** each shard for availability; failover promotes a replica.
- Remember: replication is asynchronous, so a failover can lose the last few writes — fine for a cache, risky as a primary DB.""",
  see=("leaderboard-hld", "distributed-locks")),
]

ASYNC = [
C("message-queues", "Message queues", "Basic",
  "A queue lets one service drop a message (a task) and move on, while another service processes it later. This decouples services and absorbs traffic spikes.",
  """### Why use a queue
- **Decoupling**: the producer doesn't need the consumer to be up or fast.
- **Spike absorption (load levelling)**: 100k orders arrive in a flash sale; workers process them at their own pace.
- **Retries**: failed messages are retried; poison messages go to a **dead-letter queue (DLQ)**.
- **Scaling**: add more consumers to drain faster.
- Slow work moves off the request path: sending emails, resizing images, generating reports, video transcoding.

### Point-to-point vs publish/subscribe
- **Queue (point-to-point)**: each message is processed by **one** consumer (work distribution). Examples: RabbitMQ queue, AWS SQS.
- **Pub/Sub (topic)**: each message goes to **every subscribed group** (fan-out). Example: an 'OrderPlaced' event read by email, inventory and analytics services. AWS SNS, Google Pub/Sub, Kafka topics.

### Message lifecycle (SQS-style)
1. Producer sends. 2. Consumer receives; the message becomes **invisible** for a visibility timeout. 3. Consumer processes, then **acks/deletes** it. 4. No ack in time → it reappears for another consumer (so processing must be **idempotent**).""",
  analogy="A restaurant ticket rail: waiters (producers) pin orders; cooks (consumers) take them when free. The waiter doesn't stand at the stove waiting.",
  diagram={"rows": [["Order service"], ["q:Queue / topic"], ["Email worker", "Inventory worker", "Analytics"]],
           "edges": [["Order service", "Queue / topic", "OrderPlaced"], ["Queue / topic", "Email worker"], ["Queue / topic", "Inventory worker"], ["Queue / topic", "Analytics"]]}),

C("kafka", "Kafka and log-based streaming", "Intermediate",
  "Kafka is a distributed, append-only log. Producers append events to topic partitions; consumers read at their own pace by tracking an offset. Events are kept for days, so they can be replayed.",
  """### Core concepts
- **Topic**: a named stream (`orders`).
- **Partition**: a topic is split into ordered logs spread over brokers. **Order is guaranteed only within a partition.** Messages with the same key (e.g. `orderId`) go to the same partition.
- **Offset**: position of a message in a partition. Consumers commit offsets to remember progress.
- **Consumer group**: consumers that share the work; each partition is read by exactly one consumer in the group. Max useful consumers = number of partitions.
- **Broker**: a Kafka server. Partitions are **replicated** (replication factor 3); one replica is the **leader**, others are followers; **ISR** = in-sync replicas.
- **Retention**: keep data for N days or forever (**log compaction** keeps the latest value per key).

### Why it's fast
Sequential disk writes, OS page cache, zero-copy transfer, batching and compression. Millions of messages per second per cluster.

### Kafka vs RabbitMQ
|Kafka|RabbitMQ / SQS|
|Durable log, replayable, many consumer groups read the same data|Messages deleted after ack|
|Huge throughput, ordering per partition|Rich routing (exchanges), per-message acks, priorities|
|Event streaming, analytics pipelines, CDC, event sourcing|Task queues, RPC-style work distribution|

### Producer settings to know
`acks=all` + `min.insync.replicas=2` for durability; **idempotent producer** to avoid duplicates on retry; transactions for exactly-once read-process-write.""",
  diagram={"rows": [["Producer A", "Producer B"], ["q:Partition 0", "q:Partition 1", "q:Partition 2"], ["Consumer 1 (group X)", "Consumer 2 (group X)"]],
           "edges": [["Producer A", "Partition 0", "key=a"], ["Producer B", "Partition 2", "key=b"], ["Partition 0", "Consumer 1 (group X)"], ["Partition 1", "Consumer 1 (group X)"], ["Partition 2", "Consumer 2 (group X)"]]},
  see=("delivery-semantics",)),

C("delivery-semantics", "Delivery guarantees: at-most-once, at-least-once, exactly-once", "Advanced",
  "How many times a message may be processed: maybe zero, at least one (possible duplicates), or effectively once.",
  """|Guarantee|How|Risk|
|At-most-once|Ack/commit **before** processing|Crash after ack → message lost|
|At-least-once (most common)|Ack **after** processing; retry on failure|Crash after processing, before ack → **processed twice**|
|Exactly-once|At-least-once delivery + **idempotent processing** or transactions|Complex; truly exactly-once only within one system (e.g. Kafka transactions)|

### Making consumers idempotent
- Store processed message IDs (in the same DB transaction as the side effect) and skip duplicates.
- Use natural idempotency: `SET balance = 100` is idempotent; `balance += 10` is not.
- Upserts with a unique key (e.g. `payment_id`).

### Ordering
- Global order is expensive; partition by key (user/order ID) for **per-key order**.
- Retries can reorder messages; use version numbers or sequence checks if order matters.

In interviews say: **"at-least-once delivery with idempotent consumers"** — that's the standard, practical answer.""",
  tips=["Exactly-once end to end across systems is really 'effectively once' = at-least-once + dedupe."]),

C("backpressure", "Backpressure, load shedding and dead-letter queues", "Advanced",
  "Ways to stay alive when producers are faster than consumers: slow producers down, drop low-priority work, or park failing messages.",
  """### Backpressure
The consumer signals 'slow down': bounded queues that block or reject when full, TCP flow control, reactive streams (`request(n)` in Project Reactor), Kafka consumers simply lag (the log buffers).

### Load shedding
When overloaded, reject some requests quickly (503) instead of slowing everyone down. Shed **low-priority** traffic first (analytics, prefetch) to keep checkout working.

### Dead-letter queue (DLQ)
A message that fails N times (bad data, a bug) moves to a DLQ so it doesn't block the queue forever. Alert on DLQ size, inspect, fix, and replay.

### Queue monitoring
Watch **queue depth / consumer lag** and **age of oldest message**; autoscale consumers on lag.""",
  see=("resilience-patterns",)),

C("stream-batch", "Batch vs stream processing (MapReduce, Spark, Flink)", "Advanced",
  "Batch processes a big bounded dataset at once (nightly reports). Stream processes an endless flow of events as they arrive (fraud detection in seconds).",
  """### Batch
- **MapReduce**: *map* each record to key/value pairs, *shuffle* by key, *reduce* each key's values. Example: word count over 10 TB of logs.
- **Spark**: keeps intermediate data in memory, 10–100x faster than Hadoop MapReduce; SQL, ML libraries.
- Runs hourly/daily on data lakes (S3/HDFS). High throughput, high latency.

### Stream
- **Kafka Streams, Apache Flink, Spark Structured Streaming, Google Dataflow**.
- Concepts: **windows** (tumbling 1-minute, sliding, session windows), **event time vs processing time**, **watermarks** (how long to wait for late events), stateful operators with checkpoints.
- Use cases: real-time dashboards, fraud detection, trending topics, ad click counting, alerting.

### Lambda vs Kappa architecture
- **Lambda**: a batch layer (accurate, slow) + a speed layer (approximate, fast), merged at query time. Two codebases.
- **Kappa**: everything is a stream; to recompute, replay the Kafka log through a new version of the job. One codebase.""",
  diagram={"rows": [["x:Events"], ["q:Kafka"], ["Flink (stream)", "Spark (batch)"], ["db:Real-time store", "db:Data lake / warehouse"]],
           "edges": [["Events", "Kafka"], ["Kafka", "Flink (stream)", "seconds"], ["Kafka", "Spark (batch)", "hourly"], ["Flink (stream)", "Real-time store"], ["Spark (batch)", "Data lake / warehouse"]]},
  see=("adclick-hld",)),

C("scheduler-cron", "Job schedulers, cron and delayed tasks", "Intermediate",
  "Running work later or on a schedule: cron jobs, delayed queues and distributed schedulers.",
  """- **Cron**: run at fixed times on one machine. Problem: single point of failure, and running on many machines runs it many times.
- **Distributed scheduler**: jobs stored in a DB; workers poll for due jobs and claim them atomically (`UPDATE ... SET owner=me WHERE id=? AND owner IS NULL`) or with a lease/lock. Examples: Quartz (clustered), Airflow (DAG workflows), Temporal (durable workflows), Kubernetes CronJob.
- **Delayed messages**: SQS delay, RabbitMQ delayed exchange, Redis sorted set keyed by run time (`ZRANGEBYSCORE now`), timing wheels in Kafka.
- **Exactly-once execution**: use leases with expiry + idempotent jobs; record completion.""",
  see=("jobscheduler-hld",)),
]

STORAGE_TYPES = [
C("storage-types", "Block, file and object storage", "Basic",
  "Three ways to store bytes: block (raw disks for databases), file (shared folders), object (S3: huge, cheap, accessed by key over HTTP).",
  """|Block storage|File storage|Object storage|
|Raw disk volumes (AWS EBS)|Hierarchical folders over a network (NFS, AWS EFS)|Flat namespace of objects: key → bytes + metadata (S3, GCS, Azure Blob)|
|Lowest latency; one machine mounts it|Many machines share it|Accessed over HTTP; virtually unlimited|
|Databases, VM disks|Shared config, legacy apps, home directories|Images, videos, backups, logs, data lakes, static websites|
|Expensive per GB|Medium|Cheapest per GB, 11 nines durability|

### Object storage patterns
- Store the **file in S3** and only its **URL/metadata in the database**.
- **Pre-signed URLs**: the client uploads/downloads directly to S3 with a time-limited signed URL, so files never pass through your servers.
- **Multipart upload** for large files (parallel parts, resumable).
- **Storage classes / lifecycle rules**: move old data to cheaper tiers (S3 Glacier).""",
  diagram={"seq": ["Client", "App server", "S3"], "msgs": [["Client", "App server", "I want to upload photo.jpg"], ["App server", "Client", "pre-signed PUT URL (5 min)"], ["Client", "S3", "PUT photo bytes directly"], ["Client", "App server", "done: save metadata"]]},
  see=("s3-hld", "dropbox-hld")),

C("search-engines", "Search systems and inverted indexes (Elasticsearch)", "Intermediate",
  "Full-text search uses an inverted index: a map from each word to the list of documents containing it, so 'find all products with \"red shoes\"' is fast.",
  """### Inverted index
```java
"red"   -> [doc1, doc4, doc9]
"shoes" -> [doc4, doc7, doc9]
query "red shoes" = intersect -> [doc4, doc9]
```
Building it: **tokenise** text, lowercase, remove stop words, **stem** ('running' → 'run'), then map term → postings list (doc IDs, positions, frequencies).

### Ranking
**TF-IDF** / **BM25**: a term matters more if it appears often in this doc but rarely overall. Plus signals: popularity, recency, personalisation, then ML re-ranking.

### Elasticsearch / OpenSearch / Solr
- Built on Lucene. An index is split into **shards** (each a Lucene index) with **replicas**.
- Query is **scattered** to all shards, each returns its top-k, results are **gathered** and merged.
- Near-real-time: new docs visible after a refresh (~1 s).

### In system design
Keep the **database as the source of truth** and sync to Elasticsearch asynchronously (CDC or events). Search is a **derived, eventually consistent** view.""",
  see=("autocomplete-hld", "searchengine-hld", "cdc")),

C("timeseries-analytics", "Time-series databases, data warehouses and OLAP", "Intermediate",
  "OLTP databases run the app (many small reads/writes). OLAP warehouses answer big analytical questions over billions of rows. Time-series DBs specialise in metrics over time.",
  """|OLTP|OLAP|
|Many small transactions: 'place order #123'|Few huge queries: 'revenue by city by month'|
|Row-oriented storage|**Column-oriented** storage: read only needed columns, compresses well|
|Postgres, MySQL, DynamoDB|Snowflake, BigQuery, Redshift, ClickHouse, Druid|

### ETL / ELT
Extract from OLTP (often via CDC/Kafka), transform, load into the warehouse; a **data lake** (S3 + Parquet files) stores raw data cheaply; a **lakehouse** (Delta Lake, Iceberg) adds tables and transactions on top.

### Time-series databases
InfluxDB, Prometheus, TimescaleDB, M3. Optimised for appending timestamped points, **downsampling** old data (keep 1-minute averages after a week), and range queries. Used for metrics and IoT.""",
  see=("metrics-hld",)),
]
