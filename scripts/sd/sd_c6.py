"""System Design concepts, part 6: Real-world patterns used across many designs."""
from sd_util import C

PATTERNS = [
C("feed-fanout", "News feed: fan-out on write vs fan-out on read", "Intermediate",
  "To show a user posts from everyone they follow, either push each new post into every follower's feed when it's written, or pull and merge posts when the feed is read. Big systems use a hybrid.",
  """|Fan-out on write (push)|Fan-out on read (pull)|
|On post, insert post ID into each follower's precomputed feed (Redis list)|On read, fetch recent posts of everyone you follow and merge|
|Reads are instant|Writes are instant|
|A celebrity with 100M followers creates 100M writes per post|Reading is slow for users following thousands of accounts|
|Wasted work for inactive followers|Always fresh|

### Hybrid (Twitter/Instagram style)
- Normal users: **push** to followers' feeds.
- **Celebrities** (followers > ~10k–1M): **don't fan out**; at read time, merge the user's precomputed feed with recent posts from the celebrities they follow.
- Only precompute feeds for **active users**.
- Store just post IDs in feeds (8 bytes each), keep the last ~800 per user; hydrate post details from a cache.
- Rank with an ML model instead of pure time order.""",
  diagram={"rows": [["u:Author"], ["Post service"], ["q:Fan-out queue"], ["Fan-out workers"], ["c:Feed cache: follower 1", "c:Feed cache: follower 2", "c:Feed cache: follower N"]],
           "edges": [["Author", "Post service", "new post"], ["Post service", "Fan-out queue"], ["Fan-out queue", "Fan-out workers"], ["Fan-out workers", "Feed cache: follower 1", "push id"], ["Fan-out workers", "Feed cache: follower 2", "push id"], ["Fan-out workers", "Feed cache: follower N", "push id"]]},
  lab="fanout", see=("newsfeed-hld", "twitter-hld")),

C("counters", "Counting at scale: likes, views, followers", "Intermediate",
  "A single database row `UPDATE posts SET likes = likes + 1` becomes a hot spot when a viral post gets 50k likes a second. Shard, batch and approximate.",
  """- **Sharded counters**: split one counter into N sub-counters (`likes:post9:0..15`), increment a random one, sum on read (cache the sum).
- **Batch in memory or Redis**, flush to the DB every few seconds (`INCRBY` then periodic persist).
- **Stream aggregation**: write like events to Kafka; a stream job aggregates per minute.
- Store the **fact** (who liked what) separately from the **count** (so you can check 'did I like it?' and rebuild counts).
- Approximate where acceptable: show '1.2M' — exact numbers rarely matter for display.
- Unique counts (unique viewers) → HyperLogLog.""",
  see=("hyperloglog", "adclick-hld")),

C("notification-pattern", "Notifications: push, SMS, email at scale", "Intermediate",
  "Send notifications through providers (APNs for iOS, FCM for Android, SMS gateways, email services) using queues per channel, user preferences, rate limits and retries.",
  """- Services publish 'notify user X with template T' events.
- **Notification service**: checks user preferences/opt-outs, quiet hours, deduplication, renders templates, then enqueues per channel.
- **Channel workers** call third parties: **APNs** (Apple), **FCM** (Firebase/Google), Twilio/Gupshup (SMS), SES/SendGrid (email).
- Retries with backoff; DLQ; track delivery status and opens.
- Rate-limit per user (don't spam) and per provider (respect their limits).
- Priorities: OTPs and security alerts jump the queue ahead of marketing.""",
  see=("notification-hld",)),

C("chat-delivery", "Chat delivery, presence and read receipts", "Intermediate",
  "Real-time messaging needs persistent connections, per-conversation ordering, offline storage, delivery/read acknowledgements and presence.",
  """- Clients keep a **WebSocket** to a chat server; a session registry (Redis) maps `user → server`.
- **Message flow**: sender → chat server → store in DB (Cassandra, partitioned by conversation) → route to recipient's server → push. If offline → store for later + send a push notification.
- **Ordering**: per-conversation sequence numbers (assigned by the conversation's owner/partition), not wall-clock time.
- **Acks**: sent ✓ (server stored it), delivered ✓✓ (recipient device got it), read (blue ticks) — each is a small event back to the sender.
- **Presence** ('online', 'last seen'): heartbeats every ~30 s update a TTL key; publish changes only to friends who are currently online, and debounce flapping.
- **Group chat**: fan-out per member for small groups; for huge groups/channels, members pull.
- **Sync across devices**: each device keeps the last sequence number it saw and fetches the gap on reconnect.""",
  see=("chat-hld", "realtime-comm")),

C("video-streaming", "Video upload and streaming: transcoding, adaptive bitrate, HLS/DASH", "Intermediate",
  "Uploaded videos are split, transcoded into many resolutions and bitrates, and streamed as small segments so the player can switch quality as bandwidth changes.",
  """### Upload pipeline
1. Client uploads (resumable, chunked) directly to object storage via pre-signed URLs.
2. An event triggers a **DAG of jobs**: validate → split into chunks → **transcode** each chunk in parallel (H.264/H.265/VP9/AV1 at 240p…4K) → package → thumbnails → content moderation → captions.
3. Store renditions in object storage; publish to the **CDN**.

### Adaptive bitrate streaming (ABR)
- Video is cut into 2–10 s **segments** per quality level; a **manifest** (`.m3u8` for **HLS**, `.mpd` for **MPEG-DASH**) lists them.
- The player measures bandwidth and buffer, and picks the best quality per segment: no buffering on a slow train, 4K on Wi-Fi.

### Scale numbers
YouTube receives 500+ hours of video per minute. Most views are served from CDN edges (Netflix Open Connect boxes inside ISPs). Popular content is pre-positioned at edges overnight.""",
  diagram={"rows": [["u:Creator"], ["db:Raw storage (S3)"], ["q:Job queue"], ["Transcoders (240p…4K)"], ["db:Renditions + manifests"], ["x:CDN"], ["u:Viewers"]],
           "edges": [["Creator", "Raw storage (S3)", "upload"], ["Raw storage (S3)", "Job queue", "event"], ["Job queue", "Transcoders (240p…4K)"], ["Transcoders (240p…4K)", "Renditions + manifests"], ["Renditions + manifests", "CDN"], ["CDN", "Viewers", "HLS segments"]]},
  see=("youtube-hld",)),

C("file-sync", "File sync: chunking, deduplication, delta sync", "Advanced",
  "Dropbox-style sync splits files into chunks identified by their hash, uploads only chunks that changed or are new, and keeps a metadata log of file versions.",
  """- **Chunking**: split files into ~4 MB blocks; **content-defined chunking** (rolling hash, Rabin fingerprint) so an insert near the start doesn't shift every chunk.
- **Deduplication**: chunk ID = SHA-256 of content; if the server already has it (any user), skip the upload.
- **Delta sync**: editing one paragraph of a 1 GB file uploads one chunk.
- **Metadata service**: file → ordered list of chunk hashes, versions, owner, folder tree (SQL, strongly consistent).
- **Notification**: other devices learn about changes via long polling/WebSocket, then download only missing chunks.
- **Conflicts**: two offline edits → keep both ('conflicted copy') or merge.
- Compression and encryption per chunk; resumable uploads.""",
  see=("dropbox-hld",)),

C("payments-ledger", "Payments: idempotency, double-entry ledgers, reconciliation", "Advanced",
  "Moving money needs exactly-once effects, an immutable audit trail and constant checking against banks' records.",
  """- **Idempotency keys** on every payment API call; retries never double charge.
- **Payment state machine**: `CREATED → AUTHORIZED → CAPTURED → SETTLED` (or `FAILED / REFUNDED`); transitions are conditional updates.
- **Double-entry ledger**: every movement is two entries that sum to zero (debit customer wallet ₹500, credit merchant ₹500). Append-only; never update balances in place without a ledger entry. Balance = sum of entries (cached).
- **External PSPs**: you talk to Stripe/Razorpay/Adyen/bank networks; they reply asynchronously via **webhooks** → verify signature, dedupe, update state.
- **Reconciliation**: nightly compare your ledger with the PSP/bank settlement files; flag mismatches.
- Strong consistency (SQL, serializable where needed); PCI compliance via tokenisation; risk/fraud checks before authorisation.""",
  diagram={"rows": [["u:Customer"], ["Payment service"], ["db:Ledger (append-only)", "x:PSP (Razorpay/Stripe)"], ["Reconciliation job"]],
           "edges": [["Customer", "Payment service", "pay + idempotency key"], ["Payment service", "x:PSP (Razorpay/Stripe)", "authorize"], ["x:PSP (Razorpay/Stripe)", "Payment service", "webhook"], ["Payment service", "Ledger (append-only)", "debit/credit"], ["Reconciliation job", "Ledger (append-only)"], ["Reconciliation job", "x:PSP (Razorpay/Stripe)", "settlement file"]]},
  see=("payment-hld", "idempotency")),

C("inventory-overselling", "Inventory, flash sales and avoiding overselling", "Advanced",
  "When 1 lakh users try to buy 1,000 phones at 12:00, you must never sell 1,001 and the system must not collapse.",
  """- **Atomic decrement**: `UPDATE stock SET qty = qty - 1 WHERE sku = ? AND qty > 0` (check 1 row affected), or Redis `DECR` with a Lua check, or optimistic locking with a version.
- **Reservations with expiry**: hold the item for 10 minutes during checkout; release if payment doesn't complete (delayed job / TTL).
- **Pre-load stock into Redis** for the sale; persist results asynchronously.
- **Virtual waiting room / queue**: admit users at a controlled rate (token per user); show a queue position.
- Protect the rest of the site: separate sale infrastructure, rate limits, CDN for static pages, bot detection.
- Pre-scale and load-test; graceful 'sold out' quickly.""",
  see=("ticketmaster-hld", "isolation-levels")),

C("leaderboard-pattern", "Leaderboards and ranking", "Intermediate",
  "Redis sorted sets keep members ordered by score with O(log n) updates and rank lookups, the standard building block for real-time leaderboards.",
  """```java
ZINCRBY game:leaderboard 50 "user42"      // add points
ZREVRANGE game:leaderboard 0 9 WITHSCORES // top 10
ZREVRANK game:leaderboard "user42"        // my rank
```
- Very large boards: shard by score range or region, or keep exact top-N and approximate ranks below it.
- Daily/weekly boards: one key per period with TTL.
- Persist scores in a DB for durability; Redis is the fast view.""",
  see=("leaderboard-hld",)),

C("crawler-politeness", "Web crawling patterns", "Intermediate",
  "Crawlers keep a frontier of URLs to visit, fetch pages politely per host, extract links, deduplicate, and repeat at massive scale.",
  """- **URL frontier**: prioritised queues (by importance/freshness) + per-host queues so you never hit one site with many parallel requests.
- **Politeness**: obey `robots.txt`, crawl-delay, one connection per host.
- **DNS caching** (DNS is a bottleneck), **dedup** URLs (normalise, Bloom filter) and content (checksums/SimHash for near duplicates).
- **Traps**: infinite calendars, session IDs in URLs → depth limits, URL length limits.
- Distributed by hashing hosts to crawler nodes.""",
  see=("crawler-hld", "bloom-filter")),

C("recsys-ml", "Recommendation and ML system design basics", "Advanced",
  "Large recommenders use a funnel: candidate generation narrows millions of items to hundreds, ranking orders them with a heavy model, and re-ranking applies business rules.",
  """1. **Candidate generation**: collaborative filtering, embeddings + **approximate nearest neighbour** search, 'trending', 'because you watched X'.
2. **Ranking**: a model (gradient-boosted trees, deep networks) scores each candidate using user, item and context features.
3. **Re-ranking**: diversity, freshness, policies, ads.
- **Feature store** (online for serving, offline for training) keeps features consistent.
- **Training pipeline**: logs → labels (clicks, watch time) → train → validate → deploy (model registry); A/B test online.
- Watch for feedback loops, cold start (new users/items), and training–serving skew.
- Serving latency budget ~50–100 ms: precompute what you can, cache embeddings.""",
  diagram={"rows": [["Millions of items"], ["Candidate generation (~1000)"], ["Ranking model (~100)"], ["Re-ranking + rules (~20)"], ["u:User's feed"]],
           "edges": [["Millions of items", "Candidate generation (~1000)"], ["Candidate generation (~1000)", "Ranking model (~100)"], ["Ranking model (~100)", "Re-ranking + rules (~20)"], ["Re-ranking + rules (~20)", "User's feed"]]}),

C("llm-systems", "Designing LLM / GenAI systems: RAG, vector databases, serving", "Advanced",
  "Modern interviews increasingly ask for GenAI designs: chatbots over company documents (RAG), vector search, and serving large models cost-effectively.",
  """### Retrieval-Augmented Generation (RAG)
1. **Ingest**: split documents into chunks (~500 tokens), compute **embeddings**, store in a **vector database** with metadata.
2. **Query**: embed the question, retrieve top-k similar chunks (**ANN search**: HNSW graphs, IVF, product quantisation), optionally re-rank.
3. **Generate**: put the chunks into the prompt; the LLM answers with citations.

### Vector databases
Pinecone, Milvus, Weaviate, Qdrant, pgvector, OpenSearch k-NN. Trade recall vs latency vs memory; filter by metadata (tenant, permissions!).

### Serving concerns
- GPU cost dominates: batching (continuous batching), caching (prompt/KV cache, semantic cache of answers), smaller/quantised models, routing easy queries to cheap models.
- **Streaming** tokens to the client (SSE) for perceived latency.
- Rate limits and quotas per user (tokens/minute).
- Guardrails: prompt-injection defence, PII filtering, output moderation; evaluation sets and monitoring for quality and hallucinations.""",
  see=("realtime-comm", "search-engines")),

C("read-write-heavy", "Patterns for read-heavy vs write-heavy systems", "Intermediate",
  "Most designs are dominated by either reads or writes; the toolbox differs.",
  """### Read-heavy (feeds, catalogues, profiles, URL redirects — 100:1)
Caching at every layer, CDNs, read replicas, denormalised read models (CQRS), precomputation (fan-out on write), search indexes.

### Write-heavy (logs, metrics, chat, IoT, clicks)
Append-only logs (Kafka), LSM-tree stores (Cassandra), batching and buffering, sharding by a well-spread key, async processing, write-behind caches, sampling and aggregation, time-based partitioning with TTLs.

### Both heavy
Separate paths: write to a log, build read views asynchronously; partition users; accept eventual consistency where possible.""",
  see=("storage-engines", "cqrs")),

C("hotspots", "Hot spots and the celebrity problem", "Advanced",
  "When one key, partition or user gets a huge share of traffic, a perfectly sharded system still melts at that one shard.",
  """- Detect: per-key metrics, top-K sketches of keys.
- **Reads**: cache the hot key everywhere (local caches), replicate it to several shards (`key#r`), serve from CDN.
- **Writes**: split the key (`counter#0..#15`) and aggregate; buffer and batch; queue writes.
- **Fan-out**: special handling for celebrities in feeds and notifications.
- Choose partition keys with high cardinality; add a random or time bucket suffix to spread load.""",
  see=("counters", "feed-fanout", "cache-problems")),
]
