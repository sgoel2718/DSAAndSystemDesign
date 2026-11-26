"""Theory interview questions: HLD questions (part 4)."""
from sd_iq_util import Q

Q("zoom-hld",
  ("B", "Mesh vs SFU vs MCU for video calls?", "Mesh: everyone sends to everyone (no server, doesn't scale). SFU: server forwards streams without decoding (scales, flexible). MCU: server mixes into one stream (low client load, high server CPU)."),
  ("I", "What is simulcast?", "A sender uploads several qualities; the SFU forwards the right one to each receiver based on bandwidth and layout."),
  ("I", "Why does real-time video use UDP?", "Late packets are useless; UDP (RTP over WebRTC) avoids retransmission delays and head-of-line blocking."),
  ("A", "How do you handle NAT traversal?", "ICE with STUN to discover public addresses and TURN relays when direct connections fail."),
  ("A", "How do you scale very large meetings or webinars?", "Cascaded SFUs across regions, and for huge audiences convert to HLS streaming."))

Q("spotify-hld",
  ("B", "How is music delivered to users?", "Encoded audio files in object storage served via CDN, with clients prefetching upcoming tracks."),
  ("I", "How do you count plays for royalties?", "Play events streamed to a pipeline, counted with rules (e.g., >30 s), aggregated in batch for payouts."),
  ("I", "How does offline mode work?", "Encrypted downloads with licence expiry requiring periodic online checks."),
  ("A", "How do you build personalised playlists?", "Collaborative filtering, audio/content features and NLP over playlists, generated in batch weekly."),
  ("A", "How do you handle search across millions of tracks?", "Search index with typo tolerance, popularity boosts and personalisation."))

Q("tinder-hld",
  ("B", "What are the main components of a swipe-based matching app?", "Profiles, recommendation deck service, swipe service, match detection, chat and notifications."),
  ("I", "How do you detect a match?", "On a right swipe, check whether the other user already swiped right on you (lookup in a swipes store); if yes, create a match."),
  ("I", "How do you generate the deck?", "Filter by location and preferences, exclude already-seen profiles, rank by compatibility and activity."),
  ("A", "How do you store swipes at scale?", "Partitioned KV/wide-column store keyed by user, plus Bloom filters for seen profiles."),
  ("A", "How do you handle location-based queries efficiently?", "Geosharding users by region/cell so deck generation stays local."))

Q("distributed-tracing-hld",
  ("B", "What is distributed tracing?", "Recording a request's path across services as a tree of timed spans sharing a trace id."),
  ("I", "How is context propagated?", "Trace id and parent span id travel in headers (W3C traceparent) and message metadata."),
  ("I", "Head-based vs tail-based sampling?", "Head-based decides at the start (cheap, may miss interesting traces); tail-based decides after completion, keeping slow/error traces (needs buffering)."),
  ("A", "How do you store and query traces?", "Spans written to a scalable store indexed by trace id, service and time, with retention limits."),
  ("A", "How do you minimise overhead on services?", "Async export, batching, sampling, and lightweight in-process instrumentation."))

Q("llmserving-hld",
  ("B", "What are the main components of an LLM chat service?", "API gateway with auth/quota, conversation store, prompt builder (with RAG/tools), inference cluster on GPUs, streaming responses, safety filters."),
  ("I", "Why stream responses and how?", "Tokens are generated sequentially; SSE/WebSockets show progress quickly and improve perceived latency."),
  ("I", "How do you maximise GPU utilisation?", "Continuous batching, KV-cache management (paged attention), quantisation, and routing by model size."),
  ("A", "How do you rate limit an LLM API?", "Token-based quotas (input + output tokens per minute) per user/org, plus concurrency limits."),
  ("A", "How do you manage conversation context length?", "Truncation, summarisation of older turns, and retrieving relevant history instead of sending everything."))

Q("gfs-hld",
  ("B", "What is the architecture of GFS/HDFS?", "A master (NameNode) holding namespace and chunk locations, and many chunkservers (DataNodes) storing large chunks with 3× replication."),
  ("I", "Why large chunk sizes (64–128 MB)?", "Fewer metadata entries in the master, fewer client-master interactions, and efficient sequential I/O for big files."),
  ("I", "How does a client read a file?", "Asks the master for chunk locations once, then reads directly from chunkservers."),
  ("A", "How is the master a bottleneck and how was it addressed?", "Single master memory and throughput limits; solved with federation, standby masters, and Colossus-style distributed metadata."),
  ("A", "How are lost replicas recovered?", "Heartbeats detect failed chunkservers; the master re-replicates under-replicated chunks."))

Q("reddit-hld",
  ("B", "How do you rank posts by 'hot'?", "Combine vote score (log-scaled) with post age so newer posts with fewer votes can outrank older popular ones."),
  ("I", "How do you store votes and prevent double voting?", "One record per (user, post) with upsert semantics; counters updated asynchronously."),
  ("I", "How do you serve front pages quickly?", "Precompute and cache ranked lists per subreddit, refreshed periodically."),
  ("A", "How do you store and render comment trees?", "Comments with parent ids (or materialised paths), fetched per post and sorted per level by score."),
  ("A", "How do you handle vote manipulation?", "Rate limits, account age checks, anomaly detection on voting rings, vote fuzzing."))

Q("newsagg-hld",
  ("B", "What are the main components of a news aggregator?", "Feed crawlers/ingesters, normalisation, deduplication and clustering, ranking, personalisation, serving."),
  ("I", "How do you group the same story from many sources?", "Near-duplicate detection (MinHash/SimHash on text) and clustering by similarity and time."),
  ("I", "How do you rank stories?", "Freshness, number and authority of sources, user interests, and diversity."),
  ("A", "How do you keep it fresh?", "Frequent polling/push feeds (RSS, WebSub) for high-priority sources, streaming clustering."),
  ("A", "How do you avoid filter bubbles?", "Diversity constraints and exploration in ranking."))

Q("wallet-hld",
  ("B", "What are the key requirements of a digital wallet/UPI app?", "Correct balances, no double spend, idempotent transfers, high availability, security, compliance and audit trails."),
  ("I", "How do you transfer money between two wallets safely?", "A single DB transaction debiting and crediting with balance checks, ledger entries, and idempotency keys."),
  ("I", "How do you avoid deadlocks when locking two accounts?", "Always lock accounts in a consistent order (e.g., by account id)."),
  ("A", "How do you handle UPI/bank timeouts?", "Mark PENDING, poll status or wait for callbacks, reconcile, then succeed or reverse."),
  ("A", "How do you scale hot merchant accounts?", "Split into sub-accounts or buffered credits aggregated periodically."))

Q("auction-hld",
  ("B", "What are the main requirements of an online auction?", "Accept bids in order, always show the current highest bid, end auctions on time, handle many concurrent bidders."),
  ("I", "How do you handle concurrent bids?", "Atomic compare-and-set on the current price (or a single-threaded bid processor per auction)."),
  ("I", "How do you broadcast bid updates?", "WebSockets/SSE pushing new highest bids to watchers."),
  ("A", "How do you prevent last-second sniping issues?", "Soft close: extend the auction when a bid arrives in the final minutes."),
  ("A", "How do you implement proxy bidding?", "Store each bidder's maximum and auto-bid the minimum needed increment on their behalf."))

Q("calendar-hld",
  ("B", "What are the main entities of a calendar system?", "Users, calendars, events, attendees/invites, recurrence rules, reminders."),
  ("I", "How do you store recurring events?", "Store the recurrence rule (RRULE) and exceptions, expanding instances on demand for queries."),
  ("I", "How do you find a common free slot?", "Merge attendees' busy intervals (free/busy query) and search for a gap of the needed length."),
  ("A", "How do you handle time zones and DST?", "Store times in UTC with the event's time zone and expand recurrences in that zone."),
  ("A", "How do you send reminders reliably?", "A scheduler with time-bucketed reminder jobs, idempotent delivery."))

Q("cdn-hld",
  ("B", "How do users get routed to the nearest CDN PoP?", "GeoDNS or anycast routes users to nearby, healthy points of presence."),
  ("I", "How does caching work across tiers?", "Edge caches → regional shields → origin; misses go up tiers, reducing origin load."),
  ("I", "How do you invalidate content?", "Purge APIs propagated to edges, or versioned URLs."),
  ("A", "How do you route around a failing PoP?", "Health checks remove it from DNS/anycast announcements; traffic shifts to the next nearest."),
  ("A", "How do you optimise cache hit ratio?", "Consistent hashing within a PoP, normalised cache keys, longer TTLs, tiered caching."))

Q("pricealert-hld",
  ("B", "What are the components of a price alert system?", "Price ingestion (scrapers/feeds), alert subscriptions, matching engine, notification service."),
  ("I", "How do you check millions of alerts efficiently on a price change?", "Index alerts per product sorted by target price; on change, fetch only alerts whose target ≥ new price."),
  ("I", "How do you avoid spamming users?", "One-shot or rate-limited alerts, deduplication and cooldowns."),
  ("A", "How do you scale ingestion of price updates?", "Stream updates through Kafka partitioned by product; process only actual changes."),
  ("A", "How do you handle price data quality?", "Validate outliers, require confirmation for big drops, and track source reliability."))
