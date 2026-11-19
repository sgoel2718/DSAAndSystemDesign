"""'In the interview' answers, part 1: for every tip / likely question, the words to actually say.
SAY[concept_id] = [(prompt, answer), ...]. Where a concept already has tips, prompts are those tips in order;
otherwise the prompt is a likely interviewer question."""

SAY1 = {
"what-is-sd": [
  ("Interviewers grade the conversation, not a perfect diagram: clarify, estimate, design, then deep-dive.",
   "\"Before I draw anything, let me confirm scope: the core features are X, Y and Z, and I'll leave A and B out unless you want them. For scale I'm assuming 50 million daily users, read-heavy, and we need 99.9% availability. I'll do a quick estimate, sketch the high-level design, then go deep on the hardest part — probably the feed generation. Stop me anywhere you want more detail.\""),
  ("Always say the trade-off out loud: 'I choose X, which costs us Y'.",
   "\"I'll use Cassandra for messages because the access pattern is 'latest 50 messages of a conversation' at very high write volume, and it scales writes horizontally. The cost is that we lose joins and strong consistency by default, so read-after-write for the sender is handled by writing at QUORUM and reading at QUORUM.\""),
],
"url-journey": [
  ("Go as deep as the interviewer wants: they may stop you at DNS and ask how DNS scales.",
   "\"DNS scales through hierarchy and caching. The root servers only point to TLD servers, TLDs only point to a domain's authoritative servers, and every answer is cached for its TTL in the browser, OS and recursive resolvers — so most lookups never reach the authoritative server. Root and big DNS providers also use Anycast, so the same IP is served from hundreds of locations. For our own service I'd use a managed DNS like Route 53 with low TTLs and health-checked failover records.\""),
  ("Mention connection reuse (keep-alive) and that TLS 1.3/QUIC cut round trips.",
   "\"A new HTTPS connection costs one round trip for TCP and one for TLS 1.3 before the first byte, so about 2 RTTs — 300 ms on a cross-continent link. That's why browsers keep connections alive and HTTP/2 multiplexes all requests over one connection. TLS 1.3 needs only 1 round trip (0-RTT on resumption), and HTTP/3 on QUIC combines transport and TLS setup into one round trip and avoids TCP head-of-line blocking. Plus a CDN terminates connections close to the user so those RTTs are short.\""),
],
"latency-throughput": [
  ("Always talk in p99, not averages.",
   "\"I'll set the SLO on p99, not the mean: say p99 under 200 ms. Averages hide the slow tail, and since one page fans out to many services, the user's latency is the slowest call. If p50 is 40 ms but p99 is 900 ms, one in a hundred requests is terrible, and for a page making 20 calls that's most page loads.\""),
  ("Use Little's Law to size thread pools and connection pools.",
   "\"By Little's Law, concurrency equals throughput times latency. At 2,000 requests per second with 50 ms DB latency, about 100 queries are in flight, so a DB pool of ~100 connections spread across instances — say 10 servers with 10–15 each — is enough. If latency doubles under load, concurrency doubles too, so I'd add headroom and timeouts.\""),
],
"scalability": [
  ("Say 'stateless app tier behind a load balancer, scale horizontally' early in any design.",
   "\"The application servers will be stateless — sessions live in Redis or in a JWT — so I can put them behind a load balancer and add instances with autoscaling on CPU or request rate. That makes the app tier easy; the real scaling work is in the data layer, which I'll handle with caching, read replicas and sharding by user ID.\""),
],
"availability": [
  ("Availability ≠ durability: availability is 'can I reach it now', durability is 'is my data still there'.",
   "\"These are different promises. Availability is whether the service answers right now — 99.99% allows ~52 minutes of downtime a year. Durability is whether data we acknowledged is never lost — S3 offers eleven nines. A system can be temporarily unavailable but fully durable, like a database that's failing over. For payments I prioritise durability and correctness; for a feed I prioritise availability.\""),
],
"reliability-terms": [
  ("Find and remove single points of failure in every design you draw.",
   "\"Let me walk the diagram for single points of failure: the load balancer runs as a redundant pair across availability zones; app servers are many instances; the database has a synchronous standby in another AZ with automatic failover; Redis has replicas with Sentinel; Kafka has replication factor 3. The remaining SPOF is the region itself, which we'd cover with a warm standby region if the SLA requires it.\""),
],
"estimation": [
  ("State assumptions out loud, then compute.",
   "\"I'll assume 100 million daily active users, each reading 20 times and writing twice a day. Reads: 100M × 20 ÷ 86,400 ≈ 23,000 QPS, peak ~70,000. Writes: 100M × 2 ÷ 86,400 ≈ 2,300 QPS, peak ~7,000. Each write is ~1 KB, so 200 GB a day, about 70 TB a year before replication.\""),
  ("Point out what the numbers imply: 'read-heavy 50:1, so caching and read replicas'.",
   "\"So reads outnumber writes about 10 to 1, which tells me to cache aggressively and serve reads from replicas. 7,000 peak writes per second is more than one SQL primary is comfortable with long-term, so I'll plan to shard by user ID. 70 TB a year means the media itself goes to object storage and only metadata stays in the database.\""),
],
"latency-numbers": [
  ("You don't need exact values; know the ratios (RAM ≈ 100 ns, SSD ≈ 100 µs, same-DC RTT ≈ 0.5 ms, cross-continent ≈ 150 ms).",
   "\"Memory is about a thousand times faster than an SSD read and a network hop inside the data centre is about half a millisecond, so a Redis lookup is ~1 ms end to end versus maybe 5–10 ms for a database query. Cross-continent round trips are ~150 ms, so I won't make synchronous cross-region calls on the request path; instead I'll replicate data to the user's region.\""),
],
"perf-vs-scale": [
  ("Mention load testing (JMeter, k6, Gatling) and capacity planning with headroom (~30–50%).",
   "\"Before launch I'd load-test with k6 at 2–3× expected peak to find the first bottleneck — usually DB connections or a hot lock — and set autoscaling thresholds so we run at about 60% utilisation at normal peak. That leaves 30–50% headroom for traffic spikes and for losing one availability zone.\""),
],
"osi-tcpip": [
  ("Know 'L4 vs L7' cold; it comes up in every load-balancer discussion.",
   "\"An L4 load balancer works on TCP/UDP — it sees IPs and ports and forwards connections without reading them, so it's extremely fast and good for non-HTTP traffic or millions of connections. An L7 balancer understands HTTP: it can route /api to one pool and /images to another, terminate TLS, add headers, rate-limit and do canary splits. I'd typically use an L4 NLB at the edge for raw scale and L7 ALBs or Envoy for application routing.\""),
],
"http": [
  ("301 vs 302 matters in URL-shortener design (caching vs analytics).",
   "\"A 301 is permanent, so browsers cache it and later clicks never hit our servers — great for load, bad for click analytics. A 302 is temporary, so every click comes to us and we can count it. For a shortener that sells analytics I'd return 302, and absorb the load with a cache and CDN.\""),
  ("429 + Retry-After is the right answer for rate limits.",
   "\"When a client exceeds its limit we return HTTP 429 Too Many Requests with a Retry-After header saying when to try again, plus X-RateLimit-Limit and X-RateLimit-Remaining so well-behaved clients can slow down before they hit it.\""),
],
"rest": [
  ("In interviews write 3–6 key endpoints with request/response fields; that's enough.",
   "\"The core API: POST /v1/tweets {text, mediaIds} returns 201 with the tweet; GET /v1/timeline?cursor=&limit=20 returns tweets and a nextCursor; POST /v1/users/{id}/follow; GET /v1/users/{id}/tweets?cursor=. All authenticated with a bearer token, cursor-paginated, and POSTs accept an Idempotency-Key.\""),
],
"rpc-grpc": [
  ("RPC hides the network but the network can still fail: always set timeouts and retries with idempotency.",
   "\"Every gRPC call gets a deadline — say 200 ms for this dependency — propagated downstream. We retry only idempotent calls, at most twice with exponential backoff and jitter, and wrap the client in a circuit breaker so a failing dependency fails fast instead of tying up our threads.\""),
],
"rate-limiting": [
  ("Pick token bucket by default and explain burst + refill.",
   "\"I'll use a token bucket per API key: capacity 100 tokens, refilled at 10 per second. Each request takes a token; an empty bucket means 429. That allows short bursts of up to 100 requests while enforcing an average of 10 per second, and it only needs two numbers per key — tokens and last refill time.\""),
  ("Mention race conditions and why Lua/atomic ops are needed.",
   "\"With many gateway servers sharing counters in Redis, a read-then-write would race: two servers read 1 token left and both allow the request. So the refill-and-decrement runs as one Lua script in Redis, which executes atomically. If Redis is unavailable we fail open with a conservative local in-memory limit so the limiter itself never takes the API down.\""),
],
"cache-strategies": [
  ("Say which strategy and why; mention TTL as a safety net for any missed invalidation.",
   "\"I'll use cache-aside: reads check Redis, on a miss load from the DB and populate with a 10-minute TTL; writes update the DB and then delete the key rather than updating it, to avoid racing writers. The TTL is a safety net — if an invalidation is ever missed, the stale value lives at most 10 minutes.\""),
],
"cache-problems": [
  ("Naming these three (stampede, penetration, avalanche) with fixes is a strong senior signal.",
   "\"Three things can melt the DB behind the cache. A stampede when a hot key expires — I'd use single-flight locking so one request rebuilds while others get the stale value. Penetration from lookups of keys that don't exist — cache the 'not found' briefly and put a Bloom filter of valid IDs in front. And an avalanche when many keys expire together or the cache cluster fails — add random jitter to TTLs, replicate the cache, and protect the DB with rate limits and circuit breakers.\""),
],
"delivery-semantics": [
  ("Exactly-once end to end across systems is really 'effectively once' = at-least-once + dedupe.",
   "\"Kafka gives us at-least-once delivery: consumers commit offsets after processing, so after a crash a message may be processed twice. To make the effect exactly-once, the consumer is idempotent — it records the message ID in the same transaction as its side effect and skips IDs it has already seen. So delivery is at-least-once, but the outcome is effectively once.\""),
],
"sql-vs-nosql": [
  ("Never say 'NoSQL because it's faster'. Say which access pattern and scale makes it fit.",
   "\"Orders and payments need multi-row transactions and constraints, so they go in PostgreSQL. Chat messages are written at hundreds of thousands per second and always read as 'latest N in a conversation', so a wide-column store like Cassandra with partition key conversation_id and clustering by time fits that access pattern and scales writes horizontally.\""),
],
"isolation-levels": [
  ("Ticket/seat booking questions are really about lost updates: show optimistic or pessimistic locking.",
   "\"To stop two people booking the same seat, the claim must be atomic: UPDATE seats SET status='HELD', hold_id=? WHERE show_id=? AND seat_id=? AND status='AVAILABLE', and check that exactly one row changed. That's effectively optimistic concurrency. Under very high contention I could use SELECT … FOR UPDATE instead. Holds expire after 10 minutes if payment doesn't complete.\""),
],
"fallacies": [
  ("Whenever you draw a network arrow, ask 'what if this times out?'.",
   "\"If the call to the payment service times out we don't know whether the charge happened. So the request carries an idempotency key, we retry with the same key, and if we still can't tell we mark the order PENDING and resolve it by querying the payment provider's status API — never by blindly charging again.\""),
],
"byzantine": [
  ("Mentioning that you assume crash (non-Byzantine) faults shows you know the difference.",
   "\"Inside our own data centres I'll assume crash faults — nodes stop or restart but don't lie — so Raft with three or five replicas is enough. Byzantine fault tolerance needs 3f + 1 nodes and is only worth it when participants don't trust each other, like blockchains. We still use checksums to detect corrupted data.\""),
],
"oop-pillars": [
  ("In LLD rounds, start from entities (nouns) and their behaviours (verbs), then relationships.",
   "\"From the requirements the nouns are ParkingLot, Floor, Spot, Vehicle, Ticket and Payment; the verbs are park, unpark and pay. A ParkingLot has many Floors, a Floor has many Spots, a Ticket references a Vehicle and a Spot. Vehicle and Spot have types, so I'll use enums, and fee calculation varies, so that will be a Strategy interface.\""),
],
"solid": [
  ("Name the principle when you apply it in an LLD answer: 'Strategy here keeps us open/closed'.",
   "\"Pricing is a FeeStrategy interface injected into the ParkingLot — that's dependency inversion — so adding weekend pricing means adding a class, not editing existing code, which keeps us open/closed. Each class has one job: ParkingLot allocates, FeeStrategy prices, PaymentService charges — single responsibility.\""),
],
"lld-approach": [
  ("Get a working core flow first; polish later.",
   "\"I'll first get park → ticket → unpark → fee working end to end with a small main() demo, then add validation, thread safety and the extra features you mentioned, so we always have something that runs.\""),
  ("Use interfaces for anything likely to change (pricing, allocation, payment).",
   "\"Anything likely to change sits behind an interface: SpotAllocationStrategy, FeeStrategy and PaymentGateway. The core classes depend only on these interfaces, so new rules are new implementations and I can unit-test the lot with fakes.\""),
],
}
