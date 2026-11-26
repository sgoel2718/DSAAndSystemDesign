"""Theory interview questions: HLD questions (part 1)."""
from sd_iq_util import Q

Q("urlshortener-hld",
  ("B", "How do you generate short codes?", "Base62-encode a unique id (counter/Snowflake/ranges) or hash the URL (MD5 → first 7 chars) with collision handling. 7 base62 chars give ~3.5 trillion codes."),
  ("I", "Counter-based vs hash-based codes?", "Counter: no collisions, short, but predictable and needs id coordination (ranges per server). Hash: same URL → same code (dedup), but collisions need retries/salts."),
  ("I", "301 vs 302 redirect?", "301 is permanent and cached by browsers (less load, but you lose click analytics); 302 is temporary, so every click hits you (analytics, can change target)."),
  ("I", "How do you scale redirects?", "Heavily read-dominant: cache code → URL in Redis/CDN, replicas, and a key-value store partitioned by code."),
  ("A", "How do you collect click analytics without slowing redirects?", "Emit click events asynchronously to Kafka; aggregate with a stream processor into an analytics store."),
  ("A", "How do you handle custom aliases and expiry?", "Check alias uniqueness with a conditional insert; store expiry and return 404/410 after it; clean up lazily or with TTL indexes."))

Q("pastebin-hld",
  ("B", "Where do you store paste content vs metadata?", "Content in object storage (keyed by id or hash), metadata (owner, expiry, visibility, size) in a database."),
  ("I", "How do you handle expiration?", "Store expiry time; check on read, and run a background job or TTL index to delete expired metadata and blobs."),
  ("I", "How do you make reads fast?", "CDN/cache for popular public pastes; metadata in a cache; content served directly from object storage via CDN."),
  ("A", "How do you deduplicate identical pastes?", "Content-address blobs by hash with reference counts."),
  ("A", "How do you prevent abuse?", "Size limits, rate limits per IP/user, malware/spam scanning, and private pastes requiring auth."))

Q("ratelimiter-hld",
  ("B", "Where should a rate limiter sit?", "In the API gateway/middleware before business logic, applying limits per user/API key/IP and per endpoint."),
  ("I", "Which algorithm would you choose and why?", "Token bucket (bursts allowed, cheap state) or sliding window counter (accurate enough, two counters); fixed window has edge bursts."),
  ("I", "How do you keep counters consistent across many gateway nodes?", "Central Redis with atomic Lua scripts per key; shard Redis by key; set TTLs on counters."),
  ("I", "What should the client receive when limited?", "HTTP 429 with Retry-After and rate-limit headers (limit, remaining, reset)."),
  ("A", "How do you handle multi-region rate limiting?", "Per-region limits (share of the global quota) with async synchronisation, accepting slight over-admission."),
  ("A", "How do you reduce Redis load at extreme QPS?", "Local token caches/leases per gateway (grab N tokens at a time), approximate counters, and only syncing periodically."))

Q("idgen-hld",
  ("B", "What properties should distributed IDs have?", "Unique, ideally roughly time-ordered, compact (64-bit), high throughput, no single point of failure."),
  ("I", "Explain the Snowflake approach.", "Timestamp + machine id + sequence in 64 bits, generated locally on each node without coordination per id."),
  ("I", "What are alternatives?", "DB ticket servers handing out ranges, UUIDv4 (random), ULID/UUIDv7 (time-sortable 128-bit)."),
  ("A", "What happens if the clock goes backwards?", "Detect and wait (small skews) or refuse/alert; otherwise duplicates or ordering violations occur."),
  ("A", "How do you assign machine ids safely?", "Leases from ZooKeeper/etcd, or from deployment ordinals; ensure no two live generators share an id."))

Q("kvstore-hld",
  ("B", "What are the core techniques in a Dynamo-style key–value store?", "Consistent hashing for partitioning, replication to N nodes, quorum reads/writes, versioning (vector clocks/LWW), hinted handoff, read repair, Merkle-tree anti-entropy, gossip membership."),
  ("I", "How do you choose N, R and W?", "Commonly N=3, W=2, R=2 for R + W > N; tune lower for latency/availability or higher for consistency."),
  ("I", "How are conflicts resolved?", "Last-write-wins by timestamp (simple, lossy) or vector clocks returning siblings for app-level merges."),
  ("I", "How does each node store data locally?", "Usually an LSM-tree engine (memtable + WAL + SSTables) for high write throughput."),
  ("A", "How do you detect failures and membership changes?", "Gossip protocol with heartbeats/phi-accrual failure detection; seed nodes for bootstrapping."),
  ("A", "How do you add a node without downtime?", "It takes ownership of some token ranges (vnodes); data is streamed from current owners, then reads/writes shift."))

Q("cache-hld",
  ("B", "How do you distribute keys across cache nodes?", "Consistent hashing (client-side or proxy) or hash slots (Redis Cluster)."),
  ("I", "What eviction policies would you support?", "LRU/LFU/TTL with memory limits; approximated LRU via sampling for efficiency."),
  ("I", "How do you make the cache highly available?", "Replicas per shard with automatic failover; clients reroute on failure."),
  ("I", "How do you handle hot keys?", "Local near-caches, key replication across shards, and read replicas."),
  ("A", "What consistency guarantees does a distributed cache provide?", "Typically eventual: async replication can lose recent writes on failover; caches should be treated as non-authoritative."),
  ("A", "How do you resize the cluster without a stampede on the DB?", "Consistent hashing minimises remapped keys; warm new nodes gradually; migrate slots live (Redis Cluster)."))

Q("crawler-hld",
  ("B", "What are the main components of a web crawler?", "Seed URLs, URL frontier, DNS resolver/cache, fetchers, parser/link extractor, URL dedup, content dedup, content store, and scheduler for recrawls."),
  ("I", "How do you ensure politeness?", "Per-host queues, one connection per host with delays, robots.txt rules, and backing off on errors."),
  ("I", "How do you avoid duplicate URLs and content?", "URL normalisation + Bloom filter/KV seen-set; checksums and SimHash for content."),
  ("I", "How do you prioritise what to crawl?", "Priority by page importance (PageRank), freshness needs (news sites more often), and change frequency."),
  ("A", "How do you scale to billions of pages?", "Partition the frontier and fetchers by hash(host) across many nodes; distributed seen-set; store pages in a distributed file/object store."),
  ("A", "How do you handle spider traps and dynamic content?", "Depth and per-site limits, URL pattern filters; headless rendering for JS-heavy pages selectively."))

Q("notification-hld",
  ("B", "What are the main components of a notification system?", "Ingestion API, validation and preferences, template service, per-channel queues, channel workers, third-party providers, delivery tracking, and analytics."),
  ("I", "How do you guarantee delivery without duplicates?", "At-least-once queues, idempotent workers keyed by notification id + channel, and dedupe stores."),
  ("I", "How do you handle third-party provider limits and outages?", "Rate-limit per provider, retries with backoff, multiple providers with failover, and circuit breakers."),
  ("I", "How do you prioritise different notification types?", "Separate queues/topics by priority (OTP vs marketing) with dedicated workers."),
  ("A", "How do you support scheduled and bulk notifications?", "A scheduler emitting jobs at send time; bulk campaigns split into batches throttled over time."),
  ("A", "How do you track opens and clicks?", "Tracking pixels/links redirecting through a tracking service that records events to analytics."))

Q("newsfeed-hld",
  ("B", "Push vs pull feed generation?", "Push precomputes feeds at write time (fast reads, expensive for large followings); pull builds at read time (cheap writes, slower reads). Hybrid uses push for most and pull for celebrities."),
  ("I", "How do you store precomputed feeds?", "Per-user lists of post ids in Redis (capped), with post content cached separately."),
  ("I", "How do you rank the feed?", "Candidate posts → ranking model using affinity, engagement, recency, content type → diversity rules."),
  ("I", "How do you paginate a ranked feed?", "Cursor-based pagination using the last item's score/id, with a snapshot of candidates per session to avoid duplicates."),
  ("A", "How do you handle new posts appearing while scrolling?", "Show a 'new posts' indicator instead of inserting into the current page; refresh on pull-to-refresh."),
  ("A", "How do you reduce fan-out cost?", "Skip inactive users, batch fan-out jobs, prioritise close friends, and pull for high-follower authors."))

Q("twitter-hld",
  ("B", "What are the core APIs and data for Twitter?", "Post tweet, follow, home timeline, user timeline, search; tables for users, tweets, follows; caches for timelines."),
  ("I", "How is the home timeline built?", "Fan-out on write into followers' timeline caches, with celebrity tweets merged at read time."),
  ("I", "How do you implement search?", "Index tweets in an inverted index (Earlybird/Elasticsearch-like), partitioned by time, with real-time ingestion from a stream."),
  ("I", "How do you compute trending topics?", "Stream processing counting hashtags in sliding windows, comparing to baselines, per region, with spam filtering."),
  ("A", "How do you store and shard tweets?", "Partition by tweet id (Snowflake, time-sortable) or by user id; replicate; cache hot tweets."),
  ("A", "How do you handle a celebrity tweet going viral?", "Pull-based delivery for celebrities, aggressive caching of the tweet, and protecting counters (likes/retweets) with sharded counters."))

Q("instagram-hld",
  ("B", "How do you handle photo uploads?", "Client uploads directly to object storage via pre-signed URL; an async pipeline generates thumbnails/renditions; metadata stored in DB; served via CDN."),
  ("I", "How do you design the feed?", "Same as a news feed: fan-out to followers' feeds (hybrid for celebrities) and ranking."),
  ("I", "How do you store likes and comments at scale?", "Separate tables partitioned by post id; counters maintained asynchronously or with sharded counters."),
  ("A", "How do you implement stories that expire after 24 hours?", "Store with TTL, serve from cache, clean up via TTL/background jobs; track views per story."),
  ("A", "How do you serve images efficiently to different devices?", "Multiple resolutions/formats (WebP/AVIF), CDN with device-aware URLs, lazy loading."))

Q("chat-hld",
  ("B", "Why WebSockets for chat?", "Persistent bidirectional connections allow instant server-to-client delivery without polling."),
  ("I", "How do you route messages between users connected to different servers?", "A session registry (user → gateway), and pub/sub or direct RPC between gateway servers."),
  ("I", "How do you store messages?", "Wide-column store (Cassandra/HBase) partitioned by conversation id, clustered by message sequence/time."),
  ("I", "How do you handle offline users?", "Persist messages, send push notifications, and sync missed messages on reconnect using last seen sequence."),
  ("A", "How do you guarantee ordering and no duplicates?", "Server-assigned per-conversation sequence numbers and client message ids for dedup."),
  ("A", "How do you implement presence at scale?", "Heartbeats update last-seen in a fast store; publish presence changes only to interested contacts; throttle updates."))
