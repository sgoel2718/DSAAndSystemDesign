"""Start-here roadmap, interview frameworks and cheat-sheet data for the System Design section."""

ROADMAP = [
    ("Stage 1 · Foundations (week 1)", "Understand what a system is made of and the vocabulary every interviewer uses.",
     ["what-is-sd", "client-server", "url-journey", "latency-throughput", "scalability", "availability", "reliability-terms",
      "estimation", "latency-numbers", "osi-tcpip", "ip-dns", "tcp-udp", "http", "rest", "proxies", "load-balancer", "cdn",
      "caching", "sql-vs-nosql", "acid", "indexes", "message-queues", "storage-types", "cap-intro", "monolith-microservices", "authn-authz"]),
    ("Stage 2 · Building real systems (week 2)", "The tools you combine in every design and their trade-offs.",
     ["tls", "rpc-grpc", "graphql", "realtime-comm", "api-gateway", "rate-limiting", "lb-algorithms", "cache-strategies",
      "cache-eviction", "redis-memcached", "kafka", "replication", "sharding", "consistent-hashing", "db-scaling-path",
      "normalization", "nosql-types", "connection-pooling", "search-engines", "blob-metadata", "cap", "consistency-models",
      "unique-id", "bloom-filter", "geohash-quadtree", "idempotency", "resilience-patterns", "event-driven", "service-discovery",
      "deployments", "monitoring", "sessions-jwt", "oauth", "feed-fanout", "counters", "chat-delivery", "notification-pattern"]),
    ("Stage 3 · Senior depth (week 3)", "What separates a strong hire: distributed-systems theory and failure handling.",
     ["fallacies", "pacelc", "quorum", "time-clocks", "vector-clocks", "consensus", "leader-election", "distributed-locks",
      "gossip", "merkle-anti-entropy", "crdt", "byzantine", "isolation-levels", "storage-engines", "distributed-transactions",
      "cdc", "event-sourcing", "cqrs", "delivery-semantics", "backpressure", "stream-batch", "cache-problems", "hotspots",
      "hyperloglog", "service-mesh", "redundancy-failover", "disaster-recovery", "chaos-engineering", "config-multitenancy",
      "payments-ledger", "inventory-overselling", "file-sync", "video-streaming", "recsys-ml", "llm-systems"]),
    ("Stage 4 · Interview practice (week 4)", "Apply everything: one HLD and one LLD question a day, timed, out loud.",
     ["hld-framework", "lld-approach"]),
]

HLD_FRAMEWORK = [
    ("1 · Clarify requirements", "5 min", "Ask what the system must do (functional) and how well (non-functional: scale, latency, availability, consistency). Agree on 3–5 core features; park the rest. Ask about users, regions, read/write ratio."),
    ("2 · Estimate", "3–5 min", "DAU → QPS (avg and peak), read:write ratio, storage per year, bandwidth. Say what the numbers imply ('read-heavy → cache')."),
    ("3 · API design", "3–5 min", "List the key endpoints or RPCs with inputs/outputs. This pins down the scope."),
    ("4 · Data model", "3–5 min", "Main entities, their keys and access patterns. Choose SQL vs NoSQL with a reason; pick partition/shard keys."),
    ("5 · High-level design", "10 min", "Draw clients, load balancer, services, caches, databases, queues, CDN. Walk through the main read and write flows end to end."),
    ("6 · Deep dives", "10–15 min", "Go deep on 2–3 hardest parts (the interviewer often picks): scaling the hot path, consistency, a tricky algorithm (ID generation, matching, ranking), failure handling."),
    ("7 · Bottlenecks and trade-offs", "5 min", "Single points of failure, hot spots, what breaks at 10x, monitoring and alerting, what you'd do with more time."),
]

LEVELS_EXPECT = [
    ("New grad / SDE-1", "Correct basic design with standard building blocks; understands caching, load balancing, SQL vs NoSQL; LLD with clean classes is often more important at this level."),
    ("SDE-2 / mid-level", "Drives the interview, makes reasoned trade-offs, handles scale (sharding, replication, queues), identifies bottlenecks and failure modes without prompting."),
    ("Senior / SDE-3+", "Deep dives into consistency, distributed transactions, multi-region, operational concerns (deploys, observability, cost), and alternatives with crisp trade-offs; adapts to changing requirements."),
]

MISTAKES = [
    "Jumping into boxes before clarifying requirements.",
    "Designing for features nobody asked for; not managing time.",
    "Naming technologies ('use Kafka') without saying why.",
    "Ignoring failure: no replicas, no timeouts, no retries.",
    "One giant database for everything with no thought about access patterns.",
    "Forgetting the read/write ratio and peak traffic.",
    "Not discussing trade-offs or alternatives.",
    "Going silent: interviewers grade your thinking, so think out loud.",
]

THINK = [
    ("Read-heavy, latency-sensitive", "Cache (Redis) + CDN + read replicas; precompute"),
    ("Write-heavy (events, logs, chat, metrics)", "Kafka + LSM-tree store (Cassandra) + batching; time-partitioned data"),
    ("Need strong consistency / money", "SQL with transactions, idempotency keys, conditional updates, ledger"),
    ("Global users", "CDN, GeoDNS, multi-region replicas, data residency"),
    ("Spiky traffic", "Queues for load levelling, autoscaling, rate limiting, waiting room"),
    ("Real-time updates to clients", "WebSockets / SSE + pub/sub + presence registry"),
    ("Search by text", "Inverted index (Elasticsearch) fed asynchronously by CDC"),
    ("Nearby / location queries", "Geohash, quadtree, S2/H3 + in-memory geo index"),
    ("Large files", "Object storage + pre-signed URLs + CDN; chunked/resumable uploads"),
    ("Unique IDs across shards", "Snowflake-style IDs or range allocation"),
    ("Counting at massive scale", "Sharded counters, stream aggregation, HyperLogLog for uniques"),
    ("Top-K / trending", "Stream processing with windows + heaps / Count-Min Sketch"),
    ("Long-running or slow work", "Async job queue + workers + status polling/webhooks"),
    ("Exactly-once side effects", "At-least-once delivery + idempotent consumers / outbox"),
    ("Cross-service business transaction", "Saga (orchestrated) with compensations"),
    ("Leader / single worker needed", "Leader election with etcd/ZooKeeper leases + fencing tokens"),
    ("Protect APIs from abuse", "Token-bucket rate limiting at the gateway, WAF, auth"),
    ("Analytics on big data", "Data lake (S3 + Parquet) + warehouse (BigQuery/Snowflake), batch/stream jobs"),
]

DB_PICK = [
    ("PostgreSQL / MySQL", "Relational data, transactions, joins: orders, payments, users, inventory"),
    ("DynamoDB / Cassandra / ScyllaDB", "Massive scale key-value / wide-column: chat messages, timelines, IoT, sessions"),
    ("MongoDB / Firestore", "Flexible JSON documents: catalogues, profiles, content"),
    ("Redis", "Cache, sessions, counters, leaderboards, rate limits, locks, pub/sub"),
    ("Elasticsearch / OpenSearch", "Full-text search, log search, autocomplete"),
    ("Neo4j / Neptune", "Graph traversals: social graphs, recommendations, fraud"),
    ("InfluxDB / Prometheus / TimescaleDB", "Metrics and time series"),
    ("S3 / GCS / Azure Blob", "Files, media, backups, data lake"),
    ("BigQuery / Snowflake / Redshift / ClickHouse", "Analytics (OLAP), dashboards, reporting"),
    ("Spanner / CockroachDB", "Global SQL with strong consistency and horizontal scale"),
    ("Pinecone / Milvus / pgvector", "Vector similarity search for embeddings (RAG, recommendations)"),
]

POWERS = [("2¹⁰", "1 thousand", "1 KB"), ("2²⁰", "1 million", "1 MB"), ("2³⁰", "1 billion", "1 GB"), ("2⁴⁰", "1 trillion", "1 TB"), ("2⁵⁰", "1 quadrillion", "1 PB")]

QUICK_NUMBERS = [
    ("Seconds in a day", "86,400 ≈ 10⁵"), ("1M requests/day", "≈ 12 QPS"), ("100M requests/day", "≈ 1,200 QPS"),
    ("Peak vs average", "2–3×"), ("Web/app server", "1k–10k simple req/s"), ("Redis node", "~100k ops/s"),
    ("Postgres/MySQL node", "~5–10k simple writes/s, more reads"), ("Kafka broker", "100k–1M msgs/s"),
    ("WebSocket server", "50k–1M connections"), ("Same-DC round trip", "~0.5 ms"), ("Cross-continent round trip", "~150 ms"),
    ("Disk failure rate", "~1–2% per year"), ("Characters in a tweet ≈ bytes", "~300 B with metadata"),
    ("Photo (compressed)", "~200 KB–2 MB"), ("1 min HD video", "~50–100 MB raw, ~10 MB streamed"),
]

COMPANIES = [
    ("Google", "Scale and distributed-systems depth: data partitioning, consistency, search/maps/YouTube-style problems; Googleyness and clear reasoning. Often 'design X for billions of users'."),
    ("Amazon", "Practical, customer-focused designs (e-commerce, notifications, payments, warehouses) with Leadership Principles woven in; ownership of failure modes, cost and operations."),
    ("Microsoft", "Balanced HLD + LLD; object-oriented design and clean code; collaborative design discussion (Teams/Outlook/OneDrive-style systems)."),
    ("Meta", "Product design and system design rounds: feeds, messaging, Instagram/WhatsApp-scale problems, APIs and data modelling, fast iteration."),
    ("Uber / Flipkart / Swiggy / PhonePe", "Machine-coding (LLD) rounds with working code in 60–90 min, plus HLD for marketplace problems (dispatch, payments, catalogues)."),
    ("Startups / product companies", "End-to-end ownership: pragmatic designs, cost awareness, trade-offs over buzzwords."),
]
