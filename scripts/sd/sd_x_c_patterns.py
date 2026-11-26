"""Detailed explanations with diagrams: Common Patterns tab."""
from sd_x_util import X, P, H, AN, KEY, FLOW, SEQ, NOTE, ER, TABLE, CALC, BARS, CODE, UML, STATE, BA

X("feed-fanout",
  SEQ("Fan-out on write (push) for a normal user", ["Asha (200 followers)", "Post svc", "Fan-out workers", "Feed cache (Redis lists)"],
      [["Asha (200 followers)", "Post svc", "create post 901"], ["Post svc", "Fan-out workers", "PostCreated (via Kafka)", "a"], ["Fan-out workers", "Feed cache (Redis lists)", "LPUSH feed:<follower> 901 for each of 200 followers"],
       NOTE(["Asha (200 followers)", "Feed cache (Redis lists)"], "reading a feed = LRANGE feed:me 0 49: one fast call")]),
  BA(CALC("Why celebrities break push", [("Celebrity followers", "f = 100e6", ""), ("Cache writes for ONE post", "f", ""), ("At 1 M writes/s of fan-out capacity", "f / 1e6", "seconds", "followers wait ~2 minutes, and fan-out capacity is tied up"), ("Normal user (200 followers)", "200", "writes")]),
  TABLE("Hybrid approach (used by Twitter/Instagram-style feeds)", ["Author type", "On post", "On feed read"], [["normal users", "push into followers' feed caches", "already there"], ["celebrities (> ~10k followers)", "store once in their own timeline", "pull recent celebrity posts and merge"], ["inactive followers", "skip push", "build on demand when they return"]]),
     "Before: push to everyone", "After: hybrid push/pull"))

X("counters",
  BA(CALC("Hot counter problem: likes on a viral post", [("Likes per second", "l = 50000", "/s"), ("Single-row UPDATE throughput (row lock)", "u = 1000", "/s"), ("Overload factor", "l / u", "×", "one row can't take this"),
                                                    ("Sharded counter with 64 sub-counters", "l / 64", "/s per shard", "read = sum of 64 values")]),
  SEQ("Buffered counting", ["Like API", "Redis", "Flusher (every 5 s)", "Database"],
      [["Like API", "Redis", "INCR likes:post:9 (and SADD to dedupe users)"], ["Like API", "Like API", "reply instantly"], ["Flusher (every 5 s)", "Redis", "GETSET delta:post:9 0 → 31,240"],
       ["Flusher (every 5 s)", "Database", "UPDATE posts SET likes = likes + 31240 WHERE id = 9", "", "One DB write per 5 s instead of 250,000."]]),
     "Before: one hot row", "After: sharded / buffered counting"),
  TABLE("Choose by need", ["Need", "Technique"], [["exact, low rate", "atomic DB UPDATE"], ["high rate, slightly delayed is fine", "Redis INCR + periodic flush"], ["very hot single key", "sharded counters"], ["unique counts (views by distinct users)", "HyperLogLog"], ["across regions", "CRDT PN-counter"]]))

X("notification-pattern",
  FLOW("Notification pipeline", [["Triggering services (order, social…)"], ["Notification svc: preferences, templates, rate limits, dedupe"], ["q:Email queue", "q:SMS queue", "q:Push queue"], ["Email workers → SES", "SMS workers → Twilio", "Push workers → APNs/FCM"]],
       [["Triggering services (order, social…)", "Notification svc: preferences, templates, rate limits, dedupe"], ["Notification svc: preferences, templates, rate limits, dedupe", "Email queue"], ["Notification svc: preferences, templates, rate limits, dedupe", "SMS queue"], ["Notification svc: preferences, templates, rate limits, dedupe", "Push queue"],
        ["Email queue", "Email workers → SES"], ["SMS queue", "SMS workers → Twilio"], ["Push queue", "Push workers → APNs/FCM"]]),
  TABLE("Must-haves", ["Concern", "How"], [["user preferences / opt-out", "check before sending; quiet hours"], ["no duplicates", "dedupe key (event_id + channel)"], ["provider down", "retry with backoff, fail over to a second provider"], ["priority", "separate queues: OTP before marketing"], ["tracking", "delivered/opened/clicked events back into analytics"]]),
  KEY("Full design with the LLD classes is in the Notification system questions (HLD + LLD tabs).", "See also"))

X("chat-delivery",
  SEQ("Message from Asha to Ravi (1:1)", ["Asha's app", "Chat server A", "Message store", "Presence / routing", "Chat server B", "Ravi's app"],
      [["Asha's app", "Chat server A", "send {client_msg_id, to: Ravi, text} over WebSocket"], ["Chat server A", "Message store", "persist with server seq no. 1042"], ["Chat server A", "Asha's app", "ack ✓ (sent)", "r"],
       ["Chat server A", "Presence / routing", "which server holds Ravi's connection?"], ["Presence / routing", "Chat server A", "server B", "r"], ["Chat server A", "Chat server B", "deliver"], ["Chat server B", "Ravi's app", "push message"],
       ["Ravi's app", "Chat server B", "delivered ✓✓ / read receipt"], NOTE(["Chat server A", "Ravi's app"], "Ravi offline → push notification; on reconnect he syncs 'messages after seq 1041'")]),
  TABLE("Guarantees and how they're met", ["Guarantee", "Mechanism"], [["no loss", "persist before ack; client retries until ack"], ["no duplicates", "client_msg_id dedupe"], ["ordering per chat", "per-conversation sequence numbers"], ["multi-device sync", "each device tracks last seen seq"]]))

X("video-streaming",
  FLOW("Upload → transcode → stream", [["u:Creator upload"], ["db:Raw video (object store)"], ["Transcoding DAG: split into chunks → encode in parallel"], ["db:Renditions: 240p … 4K, 2–6 s segments + manifest"], ["CDN"], ["u:Player (adaptive bitrate)"]],
       [["Creator upload", "Raw video (object store)"], ["Raw video (object store)", "Transcoding DAG: split into chunks → encode in parallel"], ["Transcoding DAG: split into chunks → encode in parallel", "Renditions: 240p … 4K, 2–6 s segments + manifest"], ["Renditions: 240p … 4K, 2–6 s segments + manifest", "CDN"], ["CDN", "Player (adaptive bitrate)"]]),
  TABLE("Adaptive bitrate: the player picks each segment's quality", ["Segment", "Measured bandwidth", "Buffer", "Chosen rendition"], [["1", "unknown", "0 s", "480p (safe start)"], ["2", "8 Mbps", "4 s", "1080p"], ["3", "8 Mbps", "10 s", "1080p"], ["4", "1.5 Mbps (entered a tunnel)", "8 s", "360p"], ["5", "6 Mbps", "6 s", "720p"]]),
  CALC("Storage per video", [("Length", "m = 10", "minutes"), ("Sum of all rendition bitrates", "b = 15e6 / 8", "B/s", "≈ 15 Mbps total across 240p..4K"), ("Storage for one 10-min video", "m * 60 * b", "B")]))

X("file-sync",
  SEQ("Dropbox-style sync with chunking and dedup", ["Laptop client", "Metadata svc", "Block store", "Phone client"],
      [["Laptop client", "Laptop client", "file changed → split into 4 MB chunks, hash each"], ["Laptop client", "Metadata svc", "commit file v7 = [h1, h2, h9]"], ["Metadata svc", "Laptop client", "missing: h9 (h1, h2 already stored)", "r", "Dedup: only new chunks are uploaded."],
       ["Laptop client", "Block store", "upload chunk h9"], ["Laptop client", "Metadata svc", "commit v7 again → OK"], ["Metadata svc", "Phone client", "notify: file changed (long poll / push)", "a"], ["Phone client", "Block store", "download h9 only"]]),
  TABLE("Conflict handling", ["Situation", "Result"], [["edit on laptop while phone offline edits the same file", "both commit based on v6; second commit sees base ≠ latest"], ["resolution", "keep both: 'report (Phone's conflicted copy).docx'"], ["real-time co-editing", "different approach: OT / CRDTs (Google Docs)"]]))

X("payments-ledger",
  P("Money is never just a balance column. A **double-entry ledger** records every movement as balanced debits and credits, immutable and append-only, so balances can always be recomputed and audited."),
  TABLE("Asha pays a merchant ₹1,000 (fee ₹20)", ["Entry", "Account", "Debit", "Credit"], [["1", "Asha's wallet", "1,000", ""], ["2", "Merchant payable", "", "980"], ["3", "Platform fee revenue", "", "20"]], "Total debits = total credits = 1,000. A transaction that doesn't balance is rejected."),
  STATE("Payment states", [["[*]"], ["CREATED"], ["AUTHORIZED"], ["CAPTURED", "FAILED"], ["REFUNDED"]],
        [["[*]", "CREATED", ""], ["CREATED", "AUTHORIZED", "card approved"], ["CREATED", "FAILED", "declined"], ["AUTHORIZED", "CAPTURED", "order shipped"], ["AUTHORIZED", "FAILED", "auth expired"], ["CAPTURED", "REFUNDED", "refund"]]),
  TABLE("Correctness rules", ["Rule", "Why"], [["idempotency keys on every payment API", "retries can't double charge"], ["amounts as integers (paise)", "no floating-point errors"], ["append-only ledger; corrections are new entries", "audit trail"], ["daily reconciliation with the bank/PSP", "catch mismatches"], ["outbox for events", "never lose 'payment succeeded'"]]))

X("inventory-overselling",
  BA(SEQ("Check-then-act race", ["Buyer 1", "Database", "Buyer 2"],
          [["Buyer 1", "Database", "SELECT stock → 1"], ["Buyer 2", "Database", "SELECT stock → 1"], ["Buyer 1", "Database", "UPDATE stock = 0; create order"], ["Buyer 2", "Database", "UPDATE stock = 0; create order ✘", "", "Two orders, one item."]]),
     SEQ("Atomic conditional decrement", ["Buyer 1", "Database", "Buyer 2"],
          [["Buyer 1", "Database", "UPDATE … SET stock = stock − 1 WHERE stock ≥ 1"], ["Database", "Buyer 1", "1 row updated → create order ✔", "r"], ["Buyer 2", "Database", "same UPDATE"], ["Database", "Buyer 2", "0 rows updated → sold out", "r", "The check and the write are one atomic statement, so they can't interleave."]]),
     "Before: oversold", "After: atomic decrement"),
  CODE("The fix in SQL", """UPDATE inventory
SET stock = stock - 1
WHERE sku = 'PS5' AND stock >= 1;      -- affected rows = 1 → success, 0 → sold out""", "sql"),
  TABLE("Flash-sale toolkit", ["Technique", "Purpose"], [["conditional update / optimistic version", "correctness at moderate load"], ["reservation with TTL (hold for 10 min)", "cart checkout; release if unpaid"], ["Redis DECR pre-check (Lua) then async order creation", "absorb 100k+ requests/s"],
        ["queue / virtual waiting room", "turn a stampede into a line"], ["split stock into buckets", "avoid one hot row"]]))

X("leaderboard-pattern",
  CODE("Redis sorted set leaderboard", """ZINCRBY lb:2026-11 50 asha         -- asha scores 50 more
ZINCRBY lb:2026-11 80 ravi
ZREVRANGE lb:2026-11 0 9 WITHSCORES -- top 10, O(log n + 10)
ZREVRANK lb:2026-11 asha            -- asha's rank, O(log n)""", "text"),
  TABLE("Example state", ["Member", "Score", "ZREVRANK (0 = first)"], [["ravi", "980", "0"], ["zoya", "945", "1"], ["asha", "910", "2"]]),
  TABLE("Scaling", ["Players", "Approach"], [["≤ tens of millions", "one Redis sorted set (+ replica)"], ["hundreds of millions", "shard by score range; rank = count in higher shards + rank within shard"], ["approximate ranks OK", "bucket histogram: 'top 3%'"], ["ties", "score = points × 10¹⁰ + (MAX_TS − timestamp) so earlier wins"]]))

X("crawler-politeness",
  FLOW("URL frontier: priority + per-host politeness", [["Seed + discovered URLs"], ["Prioritiser (PageRank, freshness)"], ["q:Front queues (by priority)"], ["Router: host → back queue"], ["q:Back queue host-a", "q:Back queue host-b", "q:Back queue host-c"], ["Fetcher threads (heap of next-allowed time per host)"]],
       [["Seed + discovered URLs", "Prioritiser (PageRank, freshness)"], ["Prioritiser (PageRank, freshness)", "Front queues (by priority)"], ["Front queues (by priority)", "Router: host → back queue"], ["Router: host → back queue", "Back queue host-a"], ["Router: host → back queue", "Back queue host-b"], ["Router: host → back queue", "Back queue host-c"],
        ["Back queue host-b", "Fetcher threads (heap of next-allowed time per host)"]]),
  TABLE("Politeness rules", ["Rule", "Example"], [["obey robots.txt (cached per host)", "Disallow: /private"], ["one connection per host, delay between requests", "≥ 1 s or Crawl-delay"], ["back off on 429/503", "double the delay"], ["identify yourself", "User-Agent: MyBot (+contact URL)"]]),
  KEY("Dedup with a Bloom filter of URLs seen and content checksums (SimHash for near-duplicates); avoid crawler traps with max depth per site.", "Other essentials"))

X("recsys-ml",
  FLOW("Two-stage recommendation at serving time", [["u:User opens home page"], ["Candidate generation: ~1,000 items (ANN over embeddings, co-watch, trending)"], ["Ranking model: score each with features (user × item × context)"], ["Re-rank: diversity, business rules, freshness"], ["Top 20 shown"]],
       [["User opens home page", "Candidate generation: ~1,000 items (ANN over embeddings, co-watch, trending)"], ["Candidate generation: ~1,000 items (ANN over embeddings, co-watch, trending)", "Ranking model: score each with features (user × item × context)"],
        ["Ranking model: score each with features (user × item × context)", "Re-rank: diversity, business rules, freshness"], ["Re-rank: diversity, business rules, freshness", "Top 20 shown"]]),
  TABLE("Offline vs online pieces", ["Piece", "Where", "Freshness"], [["embedding & model training", "offline (Spark/GPU), daily", "hours"], ["feature store", "offline + online (Redis)", "seconds–hours"], ["candidate index (ANN: FAISS, ScaNN)", "online, rebuilt periodically", "hours"], ["event logging (impressions, clicks)", "stream (Kafka)", "real time"], ["A/B testing", "online", "per experiment"]]),
  CALC("Latency budget (p99 200 ms)", [("Candidate generation", "a = 30", "ms"), ("Feature fetch", "b = 40", "ms"), ("Ranking 1,000 items", "c = 80", "ms"), ("Re-rank + response", "d = 20", "ms"), ("Total", "a + b + c + d", "ms", "30 ms left for network")]))

X("llm-systems",
  FLOW("RAG (retrieval-augmented generation) request path", [["u:User question"], ["Embed question"], ["db:Vector DB: top-k similar chunks"], ["Prompt = instructions + chunks + question"], ["LLM (GPU serving, streaming)"], ["Answer with citations (SSE stream)"]],
       [["User question", "Embed question"], ["Embed question", "Vector DB: top-k similar chunks"], ["Vector DB: top-k similar chunks", "Prompt = instructions + chunks + question"], ["Prompt = instructions + chunks + question", "LLM (GPU serving, streaming)"], ["LLM (GPU serving, streaming)", "Answer with citations (SSE stream)"]]),
  TABLE("Serving concerns", ["Concern", "Technique"], [["latency to first token", "streaming, smaller models for simple queries, prompt caching"], ["GPU throughput", "continuous batching, KV-cache, quantisation"], ["cost", "route by difficulty, cache answers to repeated prompts"], ["quality / safety", "evals, guardrails, citations"], ["rate limiting", "token-based quotas per user"]]),
  KEY("Full numbers (tokens/s, GPUs needed) are worked out in the LLM chat-assistant HLD question.", "See also"))

X("read-write-heavy",
  TABLE("Same app, two very different shapes", ["", "Read-heavy (news site, catalog)", "Write-heavy (IoT, logs, metrics, clicks)"],
        [["ratio", "100–1000 reads per write", "writes ≫ reads"], ["first moves", "CDN, cache, read replicas, denormalised views", "append-only logs, batching, queues to absorb bursts"], ["storage", "B-tree SQL + caches", "LSM stores (Cassandra), time-series DBs, Kafka"],
         ["indexes", "many, for query flexibility", "few (each index slows writes)"], ["consistency", "cached/stale reads acceptable", "accept async aggregation"]]),
  CALC("Read-heavy: how far caching gets you", [("Reads per second", "r = 100000", "/s"), ("CDN serves", "cdn = 0.8", "", "80%"), ("Redis serves of the rest", "red = 0.9", "", "90%"), ("Reads reaching the DB", "r * (1 - cdn) * (1 - red)", "/s", "a single DB + replica handles this")]))

X("hotspots",
  P("A hotspot is one key, partition or server receiving far more load than others: a celebrity's profile, a viral post, today's date as a partition key, or a flash-sale item."),
  BA(BARS("Requests per shard with a celebrity on shard 3", [("Shard 0", 1200, "1.2k/s"), ("Shard 1", 1100, "1.1k/s"), ("Shard 2", 1300, "1.3k/s"), ("Shard 3 (celebrity)", 48000, "48k/s ← overloaded"), ("Shard 4", 1000, "1.0k/s")]),
     BARS("Celebrity key copied to all 5 shards + local cache absorbing 80%", [("Shard 0", 3120, "3.1k/s"), ("Shard 1", 3020, "3.0k/s"), ("Shard 2", 3220, "3.2k/s"), ("Shard 3", 2920, "2.9k/s"), ("Shard 4", 2920, "2.9k/s")],
          caption="48k/s → 9.6k/s reach the shards (80% served from in-process caches), split as 1.9k/s per copy across 5 shards."),
     "Before: hot shard", "After: replicated hot key"),
  TABLE("Fixes", ["Hotspot", "Fix"], [["hot read key", "in-process cache + CDN; replicate key across N copies (key#1…key#N)"], ["hot write key (counter)", "sharded counters, buffer and batch"], ["time-based partition key (all writes hit 'today')", "add a hash prefix/salt: (hash(id) % 16, date)"],
        ["hot partition in Kafka", "better key; more partitions; split heavy keys"], ["sequential ids in range-sharded DB", "hash or randomised ids"]]))
