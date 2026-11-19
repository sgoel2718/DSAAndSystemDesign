"""Follow-up questions interviewers ask after each HLD answer, with model answers. FOLLOW[hld_id] = [(question, answer)]."""

FOLLOW = {
"urlshortener-hld": [
  ("How would you support 10x traffic?", "Redirects are reads, so scale the stateless redirect tier horizontally, grow the Redis cluster (hot codes are a small fraction), and serve the hottest redirects from CDN edges. The KV store shards by code, so adding nodes adds capacity; ID ranges are allocated in bigger blocks so the counter isn't a bottleneck."),
  ("How to prevent two users getting the same custom alias?", "Insert the alias with a conditional write — `PutItem ... if attribute_not_exists(code)` in DynamoDB or a unique primary key in SQL. Only one insert succeeds; the other gets a conflict and we ask them to choose another alias."),
  ("How to make codes unpredictable?", "Don't expose the raw counter. Either pick random 7-character base62 codes (retry on the rare collision), or pass the counter through a reversible bit-shuffle / Feistel cipher before base62 encoding, so consecutive IDs produce unrelated-looking codes."),
],
"ratelimiter-hld": [
  ("How to rate-limit by IP behind NAT?", "Many users can share one IP, so IP-only limits punish whole offices. Prefer limits by authenticated user or API key; use generous per-IP limits only for unauthenticated traffic, plus device fingerprints or cookies, and escalate to CAPTCHA instead of hard blocks."),
  ("How to support 'burst of 20 then 5/s'?", "That's exactly a token bucket with capacity 20 and refill rate 5 tokens per second: a client that was idle can send 20 at once, then is held to 5 per second on average."),
],
"kvstore-hld": [
  ("How do you add a node with zero downtime?", "The new node joins the ring via gossip and takes ownership of some virtual-node ranges. It streams those ranges from the current owners while they keep serving reads and writes (writes go to both during handoff); once caught up, ownership flips and the old owners drop the data."),
  ("How to support range scans?", "Hash partitioning scatters adjacent keys, so for range scans use range partitioning on the sort order (with automatic splitting of hot ranges, like Bigtable), or keep hash partitioning by a partition key and put range-ordered clustering keys inside each partition (Cassandra), so scans within one partition are sequential."),
],
"llmserving-hld": [
  ("How would you add tool use / function calling?", "The orchestrator gives the model tool schemas; when the model emits a tool call, the orchestrator validates arguments, executes the tool in a sandbox with the user's permissions and timeouts, appends the result to the conversation and continues generation. Tool calls are logged and rate-limited."),
  ("How do you evaluate answer quality after a model upgrade?", "Run an offline evaluation set (golden questions, rubric or model-graded scoring, safety tests) comparing old and new models, then a shadow or small A/B rollout watching user feedback, regeneration rate and safety metrics before ramping to 100%."),
],
"pastebin-hld": [
  ("How do you delete expired pastes efficiently?", "Lazy check on read (expired → 404) plus S3 lifecycle rules or a daily job that deletes by an expiry index; don't scan the whole table."),
  ("How do you stop abuse like malware or spam pastes?", "Rate-limit creation per IP/user, scan content asynchronously, allow reporting, and keep unlisted pastes out of search engines."),
],
"idgen-hld": [
  ("What if a machine's clock goes backwards?", "The generator remembers the last timestamp; if the clock is behind it either waits until it catches up or refuses IDs and alerts, so it never issues duplicates."),
  ("How do you assign unique worker IDs?", "Lease them from ZooKeeper/etcd at startup (ephemeral node) or derive from a stable pod ordinal; a lease expiry frees the ID safely."),
],
"cache-hld": [
  ("A node dies — what happens to its keys?", "Its replica is promoted; if there is no replica, those keys simply miss and reload from the database. Consistent hashing means only that node's share of keys is affected."),
  ("How do you handle a hot key?", "Replicate it under several keys (key#1..#N) or cache it in-process on app servers with a short TTL, and use single-flight so a miss triggers only one reload."),
],
"crawler-hld": [
  ("How do you decide what to recrawl and when?", "Estimate each page's change rate from history and its importance (PageRank, traffic); schedule high-value, frequently changing pages more often, others rarely."),
  ("How do you detect near-duplicate pages?", "Compute SimHash/MinHash fingerprints of the page content; pages whose fingerprints differ by only a few bits are near-duplicates and are skipped or clustered."),
],
"notification-hld": [
  ("How do you avoid sending the same notification twice?", "Each notification has an idempotency key; workers record sent keys and skip duplicates, and provider calls carry our message ID where supported."),
  ("How do you send a campaign to 50 million users without overloading?", "Expand the segment in batches into the queue, throttle per provider and per user, respect quiet hours, and run campaigns at lower priority than transactional messages."),
],
"newsfeed-hld": [
  ("How do you rank the feed?", "Generate candidates from followed accounts, then score with an ML model using features like affinity to the author, post engagement, recency and content type; apply diversity rules and cache the ranked page."),
  ("What if a user follows 5,000 accounts?", "Fan-out on write still keeps their precomputed feed bounded (last ~800 IDs); only celebrity accounts are merged at read time, so read cost stays small."),
],
"twitter-hld": [
  ("How do you compute trending topics?", "Stream tweets through Kafka to a job that counts hashtags per region in sliding windows (Count-Min Sketch + heap), compares against the baseline to find spikes, filters spam, and publishes top-K every minute."),
  ("How do you support search over recent tweets?", "Index tweets in near-real-time into an inverted index partitioned by time, query recent partitions first, and merge results by relevance and recency."),
],
"instagram-hld": [
  ("How do stories expire after 24 hours?", "Store stories with an expiry timestamp and TTL (Cassandra/Redis TTL, S3 lifecycle); the story tray only queries unexpired ones, and media is deleted by lifecycle rules."),
  ("How do you serve images fast to users everywhere?", "Generate several sizes at upload, store in object storage and serve through a CDN; the app requests the size that fits the screen."),
],
"chat-hld": [
  ("How do you support group chats with 100,000 members?", "Don't fan out each message to 100,000 sockets synchronously; treat it like a channel: store once, push only to currently online members via pub/sub in batches, and let others pull when they open the chat."),
  ("How does multi-device sync work?", "Each device keeps its last seen sequence number per conversation; on reconnect it fetches everything after that, and read state is synced as its own event."),
],
"autocomplete-hld": [
  ("How do you include trending queries quickly?", "Run a streaming job that counts queries in the last hour and boosts them in a small 'trending' trie merged with the daily trie at query time."),
  ("How do you personalise suggestions?", "Blend global suggestions with the user's own recent searches (kept client-side or in a per-user store), re-ranking the top few."),
],
"youtube-hld": [
  ("How do you count views accurately at this scale?", "Send view events to Kafka, dedupe by (user/session, video, time window), aggregate in a stream job into sharded counters, and reconcile with a batch job; displayed counts are approximate."),
  ("How do you reduce bandwidth costs?", "Serve from CDN edges and ISP caches, use efficient codecs (VP9/AV1) for popular videos, and adaptive bitrate so clients don't fetch more quality than they can show."),
],
"dropbox-hld": [
  ("How do you resolve conflicting edits from two offline devices?", "Each commit carries the base version; if the server already has a newer version, the second commit is saved as a 'conflicted copy' for the user to merge."),
  ("How do you avoid storing the same file many times?", "Content-addressed blocks: identical chunks have the same hash and are stored once with a reference count."),
],
"proximity-hld": [
  ("What if there are too few results in the user's cell?", "Expand the search to neighbouring cells or a lower geohash precision (larger cells) until we have enough results."),
  ("How do you handle businesses being added or updated?", "Write to the business DB; rebuild or incrementally update the geo index (e.g. nightly), since changes need not appear instantly."),
],
"uber-hld": [
  ("How do you prevent two riders getting the same driver?", "Assignment is an atomic conditional update on the driver's state (AVAILABLE → ON_TRIP) or handled by a single dispatcher per city partition; the loser moves to the next driver."),
  ("How do you calculate surge pricing?", "Stream ride requests and available drivers per geo cell, compute demand/supply ratios every minute, and apply a smoothed multiplier per cell."),
],
"ticketmaster-hld": [
  ("How do you handle 1 million users when sales open?", "A virtual waiting room admits users at a sustainable rate; the seat map is cached; holds use atomic conditional updates or Redis SET NX with expiry; bots are filtered at the edge."),
  ("What if payment succeeds but the hold already expired?", "Check the hold before charging; if it expired during payment, try to re-hold the seats, otherwise refund automatically and tell the user."),
],
"ecommerce-hld": [
  ("How do you keep prices consistent between cart and checkout?", "Re-validate prices and stock at checkout and snapshot the final price into the order; the cart only shows indicative prices."),
  ("How do you scale for Big Billion Days?", "Pre-scale, cache product pages and search heavily, queue order intake, protect inventory with atomic decrements, and shed non-critical features like recommendations if needed."),
],
"payment-hld": [
  ("The PSP call timed out — do you retry?", "Not blindly: query the PSP's status API with our payment ID first; if unknown, keep the payment PENDING, retry with the same idempotency key, and let reconciliation settle it."),
  ("How do you prove the ledger is correct?", "Double-entry: every transaction's debits and credits sum to zero, so totals must balance; nightly reconciliation compares our ledger with bank/PSP settlement files and flags mismatches."),
],
"hotel-hld": [
  ("How do you prevent double-booking a room?", "In one transaction, conditionally increment `reserved` for every night only where `reserved < total`; if any night fails, roll back."),
  ("Why can search show a room that is gone at booking time?", "Search uses an eventually consistent index for speed; the booking transaction re-checks availability, which is the source of truth."),
],
"metrics-hld": [
  ("How do you handle high-cardinality labels like user_id?", "Reject or drop them at ingestion with per-tenant cardinality limits, and steer such data to logs or traces instead of metrics."),
  ("How do you store a year of data cheaply?", "Downsample: keep raw points for a week, 1-minute rollups for a month and 1-hour rollups for a year, in compressed blocks on object storage."),
],
"logging-hld": [
  ("Elasticsearch is down — do you lose logs?", "No: shippers buffer locally and Kafka retains logs for days, so indexing resumes from where it stopped."),
  ("How do you control logging costs?", "Index only key fields, sample debug logs, use short hot retention and cheap compressed archives in S3 for long retention."),
],
"topk-hld": [
  ("How do you get exact top-K for billing or reports?", "Run a batch job over the full raw data (MapReduce/Spark) for exact counts; the stream gives fast approximate results."),
  ("How do you handle a sliding 1-hour window?", "Keep per-minute counts and add the newest minute while subtracting the one that fell out, maintaining the heap incrementally."),
],
"adclick-hld": [
  ("How do you handle clicks that arrive late?", "Window on event time with watermarks and an allowed lateness; very late events update the aggregate via the daily batch recount."),
  ("How do you avoid double counting after a failure?", "Dedupe by click ID and use exactly-once processing (Kafka transactions plus checkpointed state and idempotent writes to the sink)."),
],
"jobscheduler-hld": [
  ("A worker crashes mid-job — what happens?", "Its lease expires, the run is marked failed or re-queued, and another worker retries it; jobs are idempotent so a partial run is safe to repeat."),
  ("How do you handle thousands of jobs scheduled at exactly midnight?", "Time-bucketed partitions spread across scheduler shards, enqueue slightly ahead of time, and add jitter where exact timing doesn't matter."),
],
"email-hld": [
  ("How do you filter spam?", "Check sender authentication (SPF, DKIM, DMARC) and reputation, run an ML classifier on content and behaviour, and learn from users' 'report spam' actions."),
  ("How does search across years of mail stay fast?", "Each user has their own inverted index, so queries are small; recent mail is in a hot tier and older mail in cheaper storage."),
],
"s3-hld": [
  ("How do you get 11 nines of durability?", "Store data across multiple availability zones with replication or erasure coding, checksum every chunk, continuously scrub and repair lost or corrupt chunks quickly."),
  ("How does LIST work over billions of keys?", "Metadata is sorted by bucket and key and partitioned by key ranges, so a prefix listing reads a contiguous range and returns a continuation token."),
],
"fooddelivery-hld": [
  ("When do you assign a delivery partner?", "Not at order time: predict the restaurant's prep time and dispatch so the partner arrives just as food is ready, reducing waiting."),
  ("How do you show accurate ETAs?", "Combine prep-time prediction, partner travel time from a routing engine with live traffic, and historical data per restaurant and area."),
],
"onlinejudge-hld": [
  ("How do you stop malicious code from harming the system?", "Run each submission in an isolated sandbox (container plus seccomp/gVisor or Firecracker) with no network, read-only filesystem and strict CPU, memory and time limits."),
  ("How do you handle a contest spike?", "Pre-warm and autoscale judge workers on queue depth, prioritise contest submissions, and cache test data on workers."),
],
"leaderboard-hld": [
  ("What if the leaderboard has 500 million players?", "Keep exact ranks for the top segment in a sorted set and compute approximate ranks for others from score-bucket histograms, or shard by score range."),
  ("How do you break ties?", "Encode time into the score (higher score first, then earlier achievement), e.g. score × 10^10 − timestamp."),
],
"googledocs-hld": [
  ("OT or CRDT?", "OT with a central server is simpler when every doc has an owner server and clients are mostly online (Google Docs); CRDTs suit offline-first and peer-to-peer editing at the cost of more metadata."),
  ("How do you show version history?", "The operation log plus periodic snapshots lets us rebuild any revision; named versions just point to a revision number."),
],
"searchengine-hld": [
  ("How do you keep results fresh for news?", "A separate small real-time index tier for recent documents is queried alongside the large base index, and results are merged."),
  ("How do you handle typos?", "Spelling correction from query logs and edit-distance candidates, suggesting 'Did you mean…' or auto-correcting when confidence is high."),
],
"stockexchange-hld": [
  ("How do you recover if the matching engine crashes?", "Replay the sequenced event log from the last snapshot to rebuild the order book deterministically; a hot standby consuming the same log takes over in milliseconds."),
  ("How do you ensure fairness?", "A single sequencer stamps every order in arrival order, and matching is price-time priority on that sequence."),
],
"mq-hld": [
  ("How does a consumer group rebalance?", "When consumers join or leave, the group coordinator reassigns partitions; consumers commit offsets before giving up partitions so new owners resume from there."),
  ("How do you avoid losing messages when a broker dies?", "Replicate each partition (factor 3), require acks from all in-sync replicas with min.insync.replicas = 2, and elect the new leader only from in-sync replicas."),
],
"maps-hld": [
  ("How do you compute routes across a whole country fast?", "Precompute a hierarchy (contraction hierarchies) so a query only explores a few thousand nodes, then apply live traffic weights on top."),
  ("How do you know current traffic?", "Map-match anonymised location pings from navigating users onto road segments and aggregate speeds in sliding windows."),
],
"zoom-hld": [
  ("Why an SFU instead of each client sending to everyone?", "In a mesh each client uploads N−1 streams, which breaks beyond 3–4 people; with an SFU each client uploads once and the server forwards the right quality to each receiver."),
  ("What happens when a participant's network is poor?", "Simulcast lets the SFU forward a lower-resolution layer to that user, and the client lowers its own upload bitrate; audio is prioritised over video."),
],
"spotify-hld": [
  ("How do you start playback instantly?", "Prefetch the first seconds of the next likely tracks, cache popular tracks on device, and serve chunks from a nearby CDN."),
  ("How do you count streams for royalties?", "Clients send play events with a unique ID; a play counts after 30 seconds; events are deduped and aggregated in batch for payouts."),
],
"tinder-hld": [
  ("How do you avoid showing the same profile twice?", "Keep a per-user record of swiped profiles (and a Bloom filter for fast checks) and exclude them when building decks."),
  ("How do you detect a match instantly?", "On a right swipe, check whether the target already liked the swiper (a lookup in their likes-received set); if so, create the match atomically and notify both."),
],
"distributed-tracing-hld": [
  ("How do you keep tracing overhead low?", "Export spans asynchronously in batches, sample most traces, and keep all traces with errors or high latency via tail-based sampling."),
  ("Spans have clock skew across hosts — how do you show a timeline?", "Use parent-child relationships for structure and adjust child spans to fit within their parent when clocks disagree."),
],
"gfs-hld": [
  ("Isn't the single master a bottleneck?", "It only handles metadata, which fits in memory, and clients cache chunk locations; data never flows through it. At larger scale, metadata is partitioned (HDFS Federation, Colossus)."),
  ("What happens when a chunk server dies?", "The master notices missing heartbeats and re-replicates its chunks from the remaining replicas to other servers, prioritising chunks with the fewest copies."),
],
"reddit-hld": [
  ("How do you stop vote manipulation?", "One vote per user per item (unique key), rate limits, bot detection, vote fuzzing on displayed scores, and discounting votes from new or suspicious accounts."),
  ("How do you load a thread with 10,000 comments?", "Store comments with a materialised path and score; fetch the top-level comments and best replies to a depth, then load more on demand."),
],
"newsagg-hld": [
  ("How do you know two articles are the same story?", "Compare text embeddings and near-duplicate fingerprints within a time window; articles above a similarity threshold join the same cluster."),
  ("How do you avoid showing only one publisher?", "Diversity constraints in ranking: cap articles per source per cluster and prefer authoritative, varied sources."),
],
"wallet-hld": [
  ("A UPI payment shows 'pending' — what does the system do?", "Keep the transaction PENDING, poll the bank/NPCI status API with backoff, update via callback when it arrives, and resolve leftovers through the daily reconciliation file; if debited but failed, auto-refund."),
  ("How do you handle festival peaks?", "Autoscale the stateless tiers, shard ledgers by user, queue non-critical work (history, rewards), and apply backpressure toward partner banks that are slow."),
],
"auction-hld": [
  ("How do you handle many bids in the last second?", "Bids are ordered per auction in one partition and processed by a single writer, so they're applied sequentially; the deadline uses server receive time."),
  ("How does proxy (automatic) bidding work?", "Users store a maximum; the system bids the minimum increment needed on their behalf up to that maximum whenever they're outbid."),
],
"calendar-hld": [
  ("How do you find a free slot for 6 people?", "Fetch each person's busy intervals in the window, sort and merge them into one busy list, then return the gaps that fit the meeting length within working hours."),
  ("How do you handle time zones and daylight saving?", "Store the event's time zone with UTC instants and expand recurring events in that zone, so a 9 am weekly meeting stays at 9 am local time across DST changes."),
],
"cdn-hld": [
  ("How do you purge content quickly across 200 PoPs?", "The control plane fans out purge messages to all PoPs (seconds); better still, use versioned URLs so purges are rarely needed."),
  ("How do you protect the origin during a cache miss storm?", "Request collapsing (only one fetch per object per PoP), a mid-tier cache shared by many edges, and serving stale content while revalidating."),
],
"pricealert-hld": [
  ("How do you avoid spamming users when the price hovers around the threshold?", "Fire once and disarm the alert, or require the price to cross back by a margin (hysteresis) before it can fire again."),
  ("How do you rebuild matcher state after a crash?", "Reload alerts for the matcher's partition from the database and the change stream, then resume consuming prices from the last committed offset."),
],
}
