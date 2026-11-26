"""Theory interview questions: Real-world Patterns tab."""
from sd_iq_util import Q

Q("feed-fanout",
  ("B", "Fan-out on write vs fan-out on read?", "On write (push): when a user posts, insert into every follower's precomputed feed, so reads are fast and writes expensive. On read (pull): build the feed at read time from followees' posts, so writes are cheap and reads expensive."),
  ("I", "Why does pure push break for celebrities?", "One post must be written to millions of feeds, delaying delivery and consuming huge write capacity."),
  ("I", "How does the hybrid approach work?", "Push for normal users; for celebrities store posts once and merge them into followers' feeds at read time."),
  ("I", "Where do you store precomputed feeds?", "In Redis lists/sorted sets of post ids per user (capped length), with post bodies fetched from a cache/DB by id."),
  ("A", "How do you rank a feed?", "Candidate generation from followees + recommendations, a ranking model using affinity, recency and engagement, then diversity rules; cache results briefly."),
  ("A", "How do you handle inactive users in push fan-out?", "Skip pushing to users inactive for a while and rebuild their feed on login, saving most of the write cost."))

Q("counters",
  ("B", "Why is a counter like 'likes' hard at scale?", "Millions of increments on one row create a hot spot: row locks and a single node limit throughput."),
  ("I", "How do sharded counters work?", "Split one counter into N sub-counters, increment a random one, and sum them on read (optionally cached)."),
  ("I", "How does buffering help?", "Increment in memory/Redis and periodically flush aggregated deltas to the DB, turning millions of writes into a few."),
  ("I", "How do you count unique viewers efficiently?", "HyperLogLog for approximate uniques; exact sets only for small counts."),
  ("A", "What's the risk of buffered counters and how do you mitigate it?", "Losing buffered increments if a node crashes; use durable logs (Kafka) as the source and recompute, or accept small inaccuracy for non-critical counters."),
  ("A", "How would you show a 'live' view count for a viral video?", "Approximate counts in Redis updated in real time, displayed rounded (1.2M), with accurate totals computed by a stream/batch job."))

Q("notification-pattern",
  ("B", "What are the components of a notification system?", "API to accept requests, preference/template service, per-channel queues, workers per channel, third-party providers (APNs, FCM, SMS, email), and delivery tracking."),
  ("I", "How do you avoid sending duplicates?", "Deduplicate by event id + channel before enqueueing and make workers idempotent."),
  ("I", "How do you prioritise OTPs over marketing?", "Separate queues/priorities and worker pools so bulk campaigns can't delay transactional messages."),
  ("I", "How do you handle provider failures?", "Retries with backoff, failover to a secondary provider, circuit breakers, and dead-letter queues."),
  ("A", "How do you respect user preferences and quiet hours at scale?", "Cache preferences, check them in the pipeline, schedule delayed delivery for quiet hours, and enforce per-user frequency caps."),
  ("A", "How do you send a campaign to 100 million users?", "Segment users, enqueue in batches, rate-limit to providers' quotas, spread over time, and track progress so it can resume."))

Q("chat-delivery",
  ("B", "Why do chat apps use WebSockets?", "They need low-latency, bidirectional, server-initiated delivery over persistent connections."),
  ("I", "How do you route a message to a user connected to another server?", "A presence/session registry maps user → gateway server; the sender's server forwards via pub/sub or direct RPC to that server."),
  ("I", "How do you guarantee message ordering?", "Per-conversation sequence numbers assigned by the server (or a partitioned log keyed by conversation)."),
  ("I", "How do you avoid losing or duplicating messages?", "Persist before acknowledging, client retries with a client message id, server deduplicates, and clients sync from the last seen sequence after reconnect."),
  ("A", "How do delivery and read receipts work?", "Recipients' devices send delivered/read acks with the sequence number; the server updates per-user state and forwards receipts to the sender."),
  ("A", "How do group chats scale?", "Fan out per member (small groups) or per gateway server (large groups); store the message once and track per-member read positions."))

Q("video-streaming",
  ("B", "What is adaptive bitrate streaming?", "Videos are encoded at multiple qualities and split into short segments; the player picks the quality per segment based on bandwidth and buffer (HLS/DASH)."),
  ("I", "Why transcode videos into many renditions?", "Different devices, screen sizes and network speeds need different resolutions/bitrates and codecs."),
  ("I", "How do you transcode quickly?", "Split the upload into chunks and encode chunks in parallel across many workers (a DAG of tasks), then stitch manifests."),
  ("I", "Why is a CDN essential for video?", "Video dominates bandwidth; serving segments from edges near users cuts latency and origin/egress cost."),
  ("A", "How do you handle live streaming differently from VOD?", "Low-latency ingestion (RTMP/SRT/WebRTC), real-time transcoding, short segments or chunked CMAF, and acceptance of a few seconds of latency vs interactivity."),
  ("A", "How would you reduce storage cost for billions of videos?", "Encode only popular videos at all renditions, archive cold originals, use efficient codecs (AV1/HEVC) for popular content, and deduplicate re-uploads."))

Q("file-sync",
  ("B", "Why split files into chunks for sync?", "Only changed chunks need uploading, uploads can resume and run in parallel, and identical chunks can be deduplicated."),
  ("I", "How does deduplication work?", "Chunks are identified by content hash; if the server already has a hash, the client skips uploading it."),
  ("I", "How do other devices learn about changes?", "Long polling, WebSockets or push notifications from a notification service; they then fetch updated metadata and missing chunks."),
  ("I", "How do you handle conflicting edits from two offline devices?", "Detect via version mismatch on commit and keep both (a 'conflicted copy'), or merge for structured formats."),
  ("A", "What is content-defined chunking?", "Chunk boundaries chosen by a rolling hash of content rather than fixed offsets, so inserting bytes only changes nearby chunks."),
  ("A", "How do you separate metadata and block services?", "A metadata DB tracks files, versions and chunk lists (strongly consistent); a block store holds immutable chunks (object storage)."))

Q("payments-ledger",
  ("B", "Why use a double-entry ledger for payments?", "Every movement is recorded as balanced debits and credits, so money is never created or lost, balances can be recomputed, and audits are possible."),
  ("I", "Why store money as integers?", "Floating point can't represent decimals exactly, causing rounding errors; use the smallest unit (paise/cents) as integers."),
  ("I", "How do you prevent double charges?", "Idempotency keys on payment APIs, unique constraints on payment intents per order, and state machines that only allow valid transitions."),
  ("I", "What is reconciliation?", "Regularly comparing your records with banks/PSPs to detect missing, duplicate or mismatched transactions and resolve them."),
  ("A", "How do you handle an unknown outcome from a payment provider (timeout)?", "Mark the payment PENDING, query the provider's status API or wait for the webhook, and never blindly retry the charge."),
  ("A", "Why are ledger entries immutable?", "Auditability: corrections are new reversing entries, preserving full history."))

Q("inventory-overselling",
  ("B", "How does overselling happen?", "Concurrent check-then-act: two buyers both see stock 1 and both decrement/create orders."),
  ("I", "How do you prevent overselling in SQL?", "An atomic conditional update (`UPDATE … SET stock = stock − 1 WHERE stock ≥ 1`), row locks, or optimistic versioning."),
  ("I", "What is a reservation with TTL?", "Hold stock for a buyer during checkout for a limited time; release automatically if they don't pay."),
  ("A", "How do you handle a flash sale with 1M users for 1,000 items?", "Virtual waiting room/queue, Redis atomic decrement (Lua) as a fast gate, async order creation, rate limiting, and pre-warmed caches."),
  ("A", "How do you avoid one hot inventory row?", "Split stock into several buckets/rows and decrement any bucket with stock, or keep the counter in Redis and reconcile with the DB."))

Q("leaderboard-pattern",
  ("B", "What data structure fits a real-time leaderboard?", "A sorted set (Redis ZSET / skip list) keyed by score, giving O(log n) updates and rank queries."),
  ("I", "How do you get a user's rank and the players around them?", "ZREVRANK for rank, then ZREVRANGE from rank−k to rank+k."),
  ("I", "How do you break ties?", "Encode a tiebreaker into the score (score × 10^k + (max_ts − ts)) so earlier achievers rank higher."),
  ("A", "How do you scale beyond one Redis node?", "Shard by score range (rank = players in higher shards + local rank), or approximate ranks with histograms/percentiles for the long tail."),
  ("A", "How do you support daily/weekly/all-time boards?", "Separate keys per period (lb:2026-11-26), weekly boards via ZUNIONSTORE of daily ones, TTLs for old periods."))

Q("crawler-politeness",
  ("B", "What is crawler politeness?", "Not overloading websites: respecting robots.txt, crawl delays and limiting concurrent requests per host."),
  ("I", "How is a URL frontier organised?", "Front queues by priority, back queues per host, and a heap of the next allowed fetch time per host."),
  ("I", "How do you avoid crawling the same URL twice?", "Normalise URLs and check a seen set (Bloom filter or a distributed key-value store)."),
  ("A", "How do you detect duplicate or near-duplicate content?", "Checksums for exact duplicates and SimHash/MinHash for near-duplicates."),
  ("A", "What are crawler traps and how do you avoid them?", "Infinite URL spaces (calendars, session ids, infinite links). Avoid with max depth per site, URL length limits, parameter filtering and per-site page budgets."))

Q("recsys-ml",
  ("B", "Why do recommender systems use two stages?", "Scoring every item with a heavy model is too slow; first retrieve a few hundred candidates cheaply, then rank them with a richer model."),
  ("I", "How is candidate generation done?", "Approximate nearest neighbour search over embeddings, collaborative filtering, co-occurrence, trending and rule-based sources, merged together."),
  ("I", "What is a feature store?", "A system serving consistent features for training (offline) and serving (online, low latency), avoiding training/serving skew."),
  ("A", "How do you evaluate a recommender?", "Offline metrics (precision@k, NDCG, AUC) on historical data, then online A/B tests on engagement, retention and revenue."),
  ("A", "What is the cold-start problem and how do you handle it?", "New users/items lack interaction data; use popularity, content features, onboarding questions and exploration (bandits)."))

Q("llm-systems",
  ("B", "What is RAG?", "Retrieval-augmented generation: retrieve relevant documents (via embeddings/vector search) and include them in the prompt so the LLM answers grounded in your data."),
  ("I", "Why stream LLM responses?", "Generation is token by token and can take seconds; streaming (SSE) shows the first tokens quickly, improving perceived latency."),
  ("I", "What drives LLM serving cost?", "GPU time per token (prompt + output), model size, batch efficiency and KV-cache memory."),
  ("A", "What is continuous batching?", "Adding new requests to and removing finished ones from the GPU batch at every decoding step, keeping GPUs busy and reducing latency for short requests."),
  ("A", "How do you reduce LLM latency and cost?", "Smaller/quantised models for easy queries (routing), prompt/prefix caching, response caching, shorter prompts, speculative decoding and continuous batching."),
  ("A", "How do you evaluate a RAG system?", "Retrieval quality (recall@k), answer faithfulness/groundedness, relevance, and human/LLM-judged evals on a fixed test set, tracked per release."))

Q("read-write-heavy",
  ("B", "How do you optimise a read-heavy system?", "Caching at many layers, CDNs, read replicas, denormalised read models and precomputation."),
  ("B", "How do you optimise a write-heavy system?", "Append-only/log-structured storage, batching, async writes via queues, sharding, and minimal indexes."),
  ("I", "Which databases suit write-heavy workloads?", "LSM-based stores (Cassandra, ScyllaDB, RocksDB), time-series DBs, and Kafka as a buffer/log."),
  ("A", "How do you handle a system that is both read- and write-heavy?", "CQRS: optimise the write path for ingestion, project into separate read-optimised stores, and accept eventual consistency between them."),
  ("A", "Why do indexes hurt write-heavy workloads?", "Each index must be updated on every write, multiplying I/O and contention."))

Q("hotspots",
  ("B", "What is a hot spot?", "A key, partition or node receiving disproportionate load (celebrity, viral post, today's date), becoming the bottleneck."),
  ("I", "How do you fix a hot read key?", "In-process caching, CDN, and replicating the key across shards so reads are spread."),
  ("I", "How do you fix a hot write key?", "Sharded counters, buffering and batching, or splitting the key with a suffix and aggregating on read."),
  ("I", "Why is a timestamp a bad partition key?", "All current writes go to the same partition; add a hash prefix/salt or use a high-cardinality key."),
  ("A", "How do you detect hot keys automatically?", "Sample request keys at the proxy/client, maintain top-k counters (Count-Min Sketch), and alert or auto-cache keys exceeding thresholds."))
