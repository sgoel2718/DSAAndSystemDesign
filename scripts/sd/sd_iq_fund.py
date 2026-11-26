"""Theory interview questions: Fundamentals tab."""
from sd_iq_util import Q

Q("what-is-sd",
  ("B", "What is system design, and how is HLD different from LLD?", "System design decides the components of a system, how they communicate and where data lives so it meets its requirements at scale. **HLD** covers services, databases, caches, queues and data flow; **LLD** covers classes, interfaces, design patterns and method-level behaviour inside one service."),
  ("B", "What is the difference between functional and non-functional requirements? Give examples.", "Functional = what the system does (post a photo, send a message). Non-functional = how well it does it: latency (p99 < 200 ms), availability (99.99%), throughput (1M req/s), durability, consistency, security, cost. Non-functional requirements drive most architecture choices."),
  ("B", "What are the first things you do in a system design interview?", "Clarify scope and users, list functional requirements, agree non-functional targets, estimate scale (QPS, storage, bandwidth), sketch the API and data model, then a high-level design, then deep-dive bottlenecks and trade-offs."),
  ("I", "How does a typical web application evolve as it grows from 1,000 to 100 million users?", "Single server → separate DB → load balancer + stateless app servers → cache and CDN → read replicas → async queues → sharding / splitting services → multi-region. Each step is taken only when a measured bottleneck demands it."),
  ("I", "Why do interviewers say 'there is no right answer'? What are they actually grading?", "Every design is a set of trade-offs (consistency vs availability, latency vs cost, simplicity vs scale). They grade whether you gather requirements, justify choices with numbers, identify bottlenecks and failure modes, and communicate clearly."),
  ("I", "What is a single point of failure and how do you find them in a design?", "A component whose failure takes the whole system down. Walk the request path and ask 'what if this dies?' for each box: LB, DB primary, cache, DNS, config service, a single region. Fix with redundancy, failover and graceful degradation."),
  ("A", "How do you decide which part of a design to deep-dive into?", "Pick the part that carries the most risk for the stated requirements: the hottest read/write path, the component with the hardest consistency requirement, or the one closest to its capacity limit by your estimates. Ask the interviewer if they prefer a different area."))

Q("client-server",
  ("B", "Explain the client–server model.", "Clients send requests; servers process them and return responses. Clients initiate, servers listen. The contract between them is a protocol (HTTP) and an API format (JSON, protobuf)."),
  ("B", "What does 'stateless server' mean and why does it matter?", "The server keeps no per-user memory between requests; session data lives in a shared store or a token. Any server can handle any request, so you can add/remove servers, load-balance freely and survive crashes without logging users out."),
  ("I", "Where can session state live in a stateless architecture?", "In a shared store (Redis/Memcached), in a database, or on the client inside a signed token (JWT) or encrypted cookie. Trade-offs: shared store is revocable but adds a lookup; JWT avoids lookups but is hard to revoke."),
  ("I", "What are sticky sessions and what problems do they cause?", "The LB pins a user to one server (cookie or IP hash) so in-memory sessions keep working. Problems: uneven load, lost sessions when that server dies, harder deploys and autoscaling. Prefer externalising state."),
  ("I", "Compare thin clients and thick clients.", "Thin clients render what the server sends (server-side rendering). Thick clients (SPAs, mobile apps) run logic and cache data locally, calling APIs. Thick clients reduce server load and feel faster, but need API versioning and offline/consistency handling."),
  ("A", "What is the difference between peer-to-peer and client–server, and when would you use P2P?", "In P2P every node is both client and server (BitTorrent, WebRTC media). It removes central bandwidth costs and scales with users, but makes discovery, NAT traversal, trust and consistency harder. Used for large file distribution, mesh video calls, blockchains."))

Q("url-journey",
  ("B", "What happens when you type a URL into the browser and press Enter?", "Browser parses the URL → checks caches → DNS resolves the host to an IP → TCP handshake → TLS handshake → HTTP request (often to a CDN/LB) → server/app processes and returns HTML → browser parses, fetches CSS/JS/images, builds DOM/CSSOM, lays out and paints."),
  ("B", "How does DNS resolution work for a name not in any cache?", "The stub resolver asks a recursive resolver, which asks a root server (→ TLD servers for .com), then the TLD server (→ the domain's authoritative servers), then the authoritative server for the record. Answers are cached for their TTL at every layer."),
  ("I", "How many round trips does a first HTTPS request cost, and how can you reduce them?", "DNS (~1 RTT), TCP (1 RTT), TLS 1.3 (1 RTT), then the HTTP request (1 RTT): ~4 RTTs. Reduce with DNS caching/prefetch, keep-alive and connection reuse, TLS 1.3 / 0-RTT resumption, HTTP/3 (QUIC combines transport + TLS), and CDN edges close to users."),
  ("I", "What is the critical rendering path and how do you speed it up?", "The steps from HTML to pixels: parse HTML, load blocking CSS/JS, build DOM + CSSOM, layout, paint. Speed up by inlining critical CSS, deferring/async JS, compressing and caching assets, preloading fonts, lazy-loading images and serving from a CDN."),
  ("I", "Where can a request be served from before it ever reaches your application server?", "Browser cache, service worker, OS/DNS cache, CDN edge cache, reverse proxy cache (Nginx/Varnish), and API gateway cache. Each layer you hit earlier saves latency and backend load."),
  ("A", "How would you debug a page that loads slowly only for users in one country?", "Check RUM data (DNS, connect, TLS, TTFB, download per region), CDN PoP coverage and hit ratio there, DNS resolution (GeoDNS mapping), routing issues, regional backend latency, and third-party scripts. Fix with nearer PoPs/regions, better caching, or different DNS/anycast routing."))

Q("latency-throughput",
  ("B", "Define latency, throughput and bandwidth.", "Latency = time for one request to complete. Throughput = completed requests (or bytes) per unit time. Bandwidth = maximum data rate a link can carry. A link can have high bandwidth and still high latency (satellite)."),
  ("B", "Why do we measure p95/p99 latency instead of the average?", "Averages hide the slow tail. Users who hit p99 have a bad experience, and pages that fan out to many backends hit somebody's p99 on most loads. SLOs are usually defined on percentiles."),
  ("I", "State Little's law and use it in an example.", "L = λ × W: items in the system = arrival rate × time each spends. At 2,000 req/s and 150 ms latency you need ~300 concurrent workers/connections; if latency doubles you need 600 or requests queue."),
  ("I", "Can you increase throughput without reducing latency? How?", "Yes: add parallelism (more servers/threads), batching, pipelining and async processing. Each request still takes as long, but more are in flight at once."),
  ("I", "What is tail latency amplification?", "When one user request fans out to N backends and waits for all of them, the chance that at least one is slow grows with N. With 100 backends at 1% slow each, ~63% of requests are slow. Mitigate with hedged requests, timeouts, and reducing fan-out."),
  ("A", "How do batching and buffering trade latency for throughput?", "Grouping work (DB writes, Kafka producer batches, GPU batches) amortises per-request overhead and raises throughput, but each item waits for the batch to fill or a linger timeout. Tune batch size and max wait to the latency SLO."),
  ("A", "What are hedged requests?", "Send a request to one replica; if no reply within roughly the p95, send a duplicate to another and use whichever answers first. Cuts tail latency at the cost of a few percent extra load; requests must be idempotent."))

Q("scalability",
  ("B", "What is scalability?", "The ability to handle more load (users, data, requests) by adding resources, ideally with roughly proportional cost and without redesign, while keeping latency within targets."),
  ("B", "Vertical vs horizontal scaling: pros and cons?", "Vertical (bigger machine): simple, no code changes, but has a hard ceiling, is a single point of failure, and big machines are expensive. Horizontal (more machines): near-unlimited and fault tolerant, but needs stateless services, load balancing and data partitioning."),
  ("I", "What makes a service hard to scale horizontally?", "Local state (sessions, in-memory caches, files on local disk), shared mutable data needing coordination, singletons/cron jobs that must run once, and a database that can't be partitioned."),
  ("I", "How do you scale the database tier compared with the app tier?", "App servers scale by adding stateless copies. Databases scale reads with caches and replicas, and writes with vertical scaling, splitting by feature, then sharding (or a distributed SQL DB). Writes are the hard part because they need one source of truth."),
  ("I", "What is elasticity and how does it differ from scalability?", "Scalability is the capacity to grow; elasticity is growing and shrinking automatically with demand (autoscaling), so you pay only for what you use."),
  ("A", "Explain Amdahl's law and its implication for scaling.", "Speed-up from parallelism is limited by the serial fraction: with 5% serial work, max speed-up is 20× no matter how many nodes. Find and remove serial bottlenecks (single locks, single leader, one hot partition) before adding machines."),
  ("A", "What is the Universal Scalability Law?", "An extension of Amdahl that adds a coherency (cross-talk) cost growing with N², so throughput can actually *drop* when adding nodes (e.g., chatty coordination, lock contention, cache invalidations)."))

Q("availability",
  ("B", "What is availability and how is it measured?", "The fraction of time (or of requests) the system serves successfully. Measured as uptime % or successful requests / total requests, usually per month."),
  ("B", "How much downtime does 99.9% vs 99.99% allow per year?", "99.9% ≈ 8.8 hours/year (43 min/month). 99.99% ≈ 53 minutes/year (4.3 min/month). Each extra nine is 10× less downtime."),
  ("I", "How do series and parallel components affect availability?", "Series (all must work): multiply availabilities, so the total is worse than any part. Parallel/redundant (any one works): 1 − Π(1 − a), so the total is better than any single copy."),
  ("I", "What are SLI, SLO, SLA and an error budget?", "SLI = measured indicator (good requests %). SLO = internal target (99.9% over 30 days). SLA = contract with penalties, looser than the SLO. Error budget = 1 − SLO; while budget remains you can ship faster, when exhausted you focus on reliability."),
  ("I", "Name techniques to improve availability.", "Redundancy at every tier, health checks and automatic failover, multi-AZ/region deployment, timeouts/retries/circuit breakers, graceful degradation, canary deploys and fast rollback, rate limiting/load shedding."),
  ("A", "Why can adding more replicas sometimes reduce availability?", "More components in the critical path (e.g., synchronous replication to all replicas, quorum across regions) means more things that can fail or slow down. Redundancy only helps when the system can proceed without the failed part."),
  ("A", "How would you design for 99.99% when a dependency only offers 99.9%?", "Take it off the critical path: cache its responses, call it asynchronously, provide a fallback or degraded mode, use multiple providers, or queue work for later. Otherwise your availability is capped by the dependency."))

Q("reliability-terms",
  ("B", "What is the difference between availability and reliability?", "Availability: is it up right now? Reliability: does it work correctly over time (no wrong answers, no data loss)? A system can be available but unreliable (returns wrong balances)."),
  ("B", "What is durability?", "The probability that committed data is not lost. Achieved with replication, WAL + fsync, backups and checksums; S3 advertises 11 nines."),
  ("I", "Fault tolerance vs high availability vs resilience?", "Fault tolerance: keeps working through a component failure with no visible impact. High availability: minimises downtime, may have brief failover. Resilience: the broader ability to absorb, degrade gracefully and recover."),
  ("I", "Define MTBF and MTTR. Which is easier to improve?", "MTBF = mean time between failures; MTTR = mean time to repair. Availability ≈ MTBF / (MTBF + MTTR). MTTR is often easier to improve: good monitoring, automated failover, fast rollback and runbooks."),
  ("I", "What is graceful degradation? Example?", "Serving a reduced but useful experience when parts fail: show cached recommendations, hide reviews, disable search suggestions, make the page read-only, instead of failing the whole page."),
  ("A", "What are the main failure categories you should design for?", "Hardware (disk, node, rack), network (partitions, latency), software bugs and bad deploys, overload/cascading failures, dependency outages, operator error, data corruption and region-wide disasters."))

Q("estimation",
  ("B", "Why do back-of-the-envelope estimates in an interview?", "To size the system: they decide whether you need caching, sharding, a CDN or queues, and show the interviewer your design is grounded in numbers."),
  ("B", "Convert 100 million requests per day to QPS.", "100M / 86,400 ≈ 1,160 QPS average; peak is typically 2–5× higher, so plan for ~3,000–5,000 QPS."),
  ("I", "Estimate storage for 10 million photo uploads a day at 2 MB each over 5 years.", "10M × 2 MB = 20 TB/day; × 365 × 5 ≈ 36.5 PB, before replication (×3) or resized thumbnails. Clearly object storage, with lifecycle tiers."),
  ("I", "How do you estimate the number of servers needed?", "Peak QPS ÷ QPS one server handles at target utilisation (e.g., 70%), plus redundancy (N+1 or per-AZ headroom). Example: 30k peak / (1,000 × 0.7) ≈ 43 → round up to 48 across 3 AZs."),
  ("I", "Which numbers should you know by heart?", "Seconds/day ≈ 10⁵; memory ref ~100 ns; SSD read ~100 µs; same-DC RTT ~0.5 ms; cross-continent RTT ~150 ms; Redis ~100k ops/s per node; SQL ~5–10k writes/s per node; 1 Gbps ≈ 125 MB/s."),
  ("A", "How do you estimate bandwidth and why does it matter?", "Bytes per request × QPS. 35k reads/s × 200 KB = 7 GB/s egress, which forces a CDN and impacts cost far more than compute. Ingress sizes the upload path and replication traffic."),
  ("A", "What mistakes do candidates make with estimates?", "Too much precision, forgetting peaks and replication, mixing bits and bytes, not stating assumptions, and computing numbers that never influence any design decision."))

Q("latency-numbers",
  ("B", "Order these by speed: memory read, SSD read, network round trip in the same datacenter, disk seek.", "Memory (~100 ns) < SSD random read (~16–100 µs) < same-DC round trip (~500 µs) < HDD seek (~2–10 ms) < cross-continent round trip (~150 ms)."),
  ("I", "Why is sequential I/O so much faster than random I/O?", "Sequential reads avoid seeks (HDD) and use prefetching, large blocks and fewer IOPS. That's why append-only logs, LSM trees and Kafka are fast."),
  ("I", "Why does an in-memory cache help so much even though the network is involved?", "A Redis call (~0.5 ms in-DC) avoids a DB query that may touch disk, take locks and run a plan (5–50 ms). An in-process cache avoids even the network hop."),
  ("I", "How do latency numbers influence multi-region design?", "Cross-region RTTs of 50–200 ms make synchronous cross-region writes slow, so designs serve reads locally, keep writes in a home region, or accept async replication / eventual consistency."),
  ("A", "Why is compressing data before sending it usually worth it?", "Compressing 1 KB takes ~µs; sending bytes across a network or to disk costs far more. Compression reduces bandwidth and egress cost; it's skipped only for already-compressed media or extremely latency-sensitive tiny payloads."),
  ("A", "What does 'mechanical sympathy' mean in system design?", "Designing with hardware realities in mind: cache lines, sequential I/O, batching syscalls, avoiding cross-core contention, keeping hot data in memory. Example: LMAX disruptor, Kafka's zero-copy sendfile."))

Q("perf-vs-scale",
  ("B", "What's the difference between a performance problem and a scalability problem?", "Performance: slow even for one user (bad query, slow algorithm). Scalability: fast for one user, but slows down or fails as load increases (resource saturation, contention)."),
  ("I", "Why does latency rise sharply as utilisation approaches 100%?", "Queueing: in M/M/1, wait ∝ 1/(1 − ρ). At 50% busy latency is ~2× service time, at 90% ~10×, at 99% ~100×. Keep headroom (~60–70%)."),
  ("I", "What is a cascading failure?", "One overloaded or slow component causes callers to back up (threads blocked, retries), which overloads them, spreading the outage. Prevented with timeouts, circuit breakers, bulkheads and load shedding."),
  ("I", "What is a retry storm and how do you prevent it?", "Clients retry failed requests, multiplying load exactly when the service is struggling. Prevent with exponential backoff + jitter, retry budgets (e.g., max 10% extra), and server-side load shedding."),
  ("A", "How do you find the bottleneck in a slow system?", "Measure: distributed traces for where time goes, USE metrics (utilisation, saturation, errors) per resource, profiling, DB slow-query logs. Load test to find which resource saturates first."),
  ("A", "What is the thundering herd problem?", "Many clients wake up or retry at once (cache key expiry, server restart, cron at :00), overwhelming a resource. Fix with jitter, request coalescing/single-flight, and staggered schedules."))

Q("cap-intro",
  ("B", "What does the CAP theorem say?", "During a network partition, a distributed data store can guarantee either consistency (every read sees the latest write or errors) or availability (every request gets a non-error answer), not both."),
  ("B", "Why can't you just choose 'CA'?", "Partitions happen in any real distributed system; you can't opt out of them. 'CA' only describes a single-node system or one that stops working entirely during a partition."),
  ("I", "Give examples where you'd choose consistency over availability, and vice versa.", "CP: payments, bank balances, seat booking, inventory, leader election/locks. AP: social feeds, likes, view counts, shopping cart adds, DNS, product catalogue."),
  ("I", "Does CAP mean a system is always either fully consistent or fully available?", "No. It only constrains behaviour *during* a partition, and choices can be per operation or per data type. Most of the time there's no partition and systems trade latency vs consistency instead (PACELC)."),
  ("A", "What does 'consistency' mean in CAP versus ACID?", "CAP's C is linearizability (single-copy recency across replicas). ACID's C means transactions preserve invariants/constraints within a database. Different concepts that share a word."))

Q("osi-tcpip",
  ("B", "Name the TCP/IP layers and what each does.", "Application (HTTP, DNS), Transport (TCP/UDP: ports, reliability), Internet (IP: addressing and routing), Link (Ethernet/Wi-Fi: frames on a local network)."),
  ("B", "Map common protocols to OSI layers.", "HTTP/DNS/SMTP – L7; TLS – roughly L6/L5; TCP/UDP – L4; IP/ICMP – L3; Ethernet/ARP – L2; cables/radio – L1."),
  ("I", "What's the difference between an L4 and an L7 load balancer?", "L4 routes on IP/port and forwards TCP/UDP without reading content: fast and protocol-agnostic. L7 parses HTTP, so it can route by path/host/header, terminate TLS, retry, rewrite and authenticate, at more CPU cost."),
  ("I", "What is encapsulation in networking?", "Each layer wraps the payload from the layer above with its own header: HTTP request inside a TCP segment inside an IP packet inside an Ethernet frame. The receiver unwraps in reverse."),
  ("A", "What is MTU and what happens when a packet is too large?", "Maximum transmission unit (~1,500 bytes on Ethernet). Larger IP packets are fragmented or dropped (with DF set, triggering ICMP 'too big' for path MTU discovery). Misconfigured MTUs cause mysterious hangs, often in tunnels/VPNs."))

Q("ip-dns",
  ("B", "What is DNS and why do we need it?", "The internet's directory that maps human names to IP addresses (and other records). It lets services move IPs without clients changing anything."),
  ("B", "Explain A, AAAA, CNAME, MX, NS and TXT records.", "A → IPv4; AAAA → IPv6; CNAME → alias to another name; MX → mail servers; NS → authoritative name servers for a zone; TXT → free text (SPF, domain verification)."),
  ("I", "What is TTL in DNS and how do you choose it?", "How long resolvers may cache a record. Long TTLs reduce load and latency; short TTLs (30–60 s) allow fast failover/migration. Lower TTLs before a planned change."),
  ("I", "How is DNS used for load balancing and failover?", "Return multiple A records (round robin), weighted records, GeoDNS/latency-based routing to the nearest region, and health-checked records that stop returning dead endpoints."),
  ("I", "What is anycast?", "The same IP address is announced from many locations; BGP routes each user to the nearest one. Used by CDNs and DNS root servers for low latency and DDoS absorption."),
  ("A", "Why can't you rely on DNS alone for instant failover?", "Resolvers and clients cache beyond TTLs, some ignore TTLs, and connections stay open to old IPs. Combine DNS with load balancers/virtual IPs or anycast for fast failover."),
  ("A", "Private vs public IPs, NAT and why it matters for system design?", "Private ranges (10/8, 172.16/12, 192.168/16) aren't routable on the internet; NAT maps them to public IPs. Services in a VPC talk privately; egress via NAT gateways has bandwidth/cost limits; P2P needs NAT traversal (STUN/TURN)."))

Q("tcp-udp",
  ("B", "TCP vs UDP?", "TCP: connection-oriented, reliable, ordered, flow and congestion control, more overhead. UDP: connectionless, best-effort, no ordering, minimal overhead; the app handles loss if it cares."),
  ("B", "Describe the TCP three-way handshake.", "Client sends SYN(seq x); server replies SYN-ACK(seq y, ack x+1); client sends ACK(y+1). Costs one round trip before data flows."),
  ("I", "When would you choose UDP?", "When late data is useless or you implement your own reliability: live video/voice, games, DNS, telemetry, and QUIC/HTTP/3 (reliability built on UDP in user space)."),
  ("I", "What is head-of-line blocking?", "A lost packet in an ordered stream blocks delivery of everything behind it. HTTP/2 multiplexes streams over one TCP connection, so one loss stalls all streams; QUIC fixes this with independent streams."),
  ("I", "What are TCP flow control and congestion control?", "Flow control (receive window) prevents overwhelming the receiver. Congestion control (slow start, AIMD, CUBIC/BBR) prevents overwhelming the network by adapting send rate to loss/latency."),
  ("A", "What is TIME_WAIT and why can it cause problems on busy servers?", "After closing, the active closer keeps the socket in TIME_WAIT (~60 s) to absorb stray packets. Many short connections can exhaust ephemeral ports; fix with connection pooling/keep-alive and reuse settings."),
  ("A", "Why is QUIC used for HTTP/3?", "It combines transport and TLS handshakes (1-RTT, 0-RTT resumption), has per-stream loss recovery (no TCP HOL blocking), supports connection migration across networks (Wi-Fi → 4G), and can evolve in user space."))

Q("http",
  ("B", "What are the main HTTP methods and which are idempotent?", "GET (read), POST (create/action), PUT (replace), PATCH (partial update), DELETE (remove). GET, PUT, DELETE (and HEAD, OPTIONS) are idempotent; POST is not; PATCH usually isn't."),
  ("B", "Explain status code classes with examples.", "1xx informational, 2xx success (200, 201, 204), 3xx redirect (301, 302, 304), 4xx client error (400, 401, 403, 404, 409, 429), 5xx server error (500, 502, 503, 504)."),
  ("I", "401 vs 403? 502 vs 503 vs 504?", "401 = not authenticated; 403 = authenticated but not allowed. 502 = upstream returned an invalid response; 503 = service unavailable/overloaded; 504 = upstream timed out."),
  ("I", "How does HTTP caching work?", "Cache-Control (max-age, no-store, private/public), ETag/If-None-Match and Last-Modified/If-Modified-Since for revalidation (304 Not Modified), Vary for content negotiation. CDNs and browsers obey these headers."),
  ("I", "HTTP/1.1 vs HTTP/2 vs HTTP/3?", "1.1: text, keep-alive, one request at a time per connection. 2: binary framing, multiplexed streams, header compression, one TCP connection. 3: HTTP/2 semantics over QUIC (UDP) avoiding TCP HOL blocking with faster handshakes."),
  ("A", "What is the difference between safe and idempotent methods?", "Safe = no server state change (GET, HEAD). Idempotent = repeating has the same effect as once (PUT, DELETE). All safe methods are idempotent; not all idempotent methods are safe."),
  ("A", "How do cookies work and what security flags matter?", "Server sets Set-Cookie; the browser sends it back on matching requests. Flags: HttpOnly (no JS access, mitigates XSS theft), Secure (HTTPS only), SameSite (CSRF protection), Domain/Path/Expires scope."))

Q("tls",
  ("B", "What does TLS provide?", "Confidentiality (encryption), integrity (tamper detection) and server authentication via certificates; optionally client authentication (mTLS)."),
  ("I", "Walk through a TLS 1.3 handshake.", "ClientHello with supported ciphers and a key share → ServerHello with chosen cipher and its key share, certificate, signature and Finished → both derive session keys via (EC)DHE → client verifies the cert chain and sends Finished + encrypted data. One round trip."),
  ("I", "How does certificate validation work?", "The client checks the certificate chain up to a trusted root CA, signatures, validity dates, hostname match (SAN), and revocation (OCSP/CRL, often stapled)."),
  ("I", "Symmetric vs asymmetric encryption in TLS?", "Asymmetric crypto (ECDHE key exchange, RSA/ECDSA signatures) is used to agree on keys and authenticate; symmetric (AES-GCM, ChaCha20) encrypts the bulk data because it's much faster."),
  ("I", "What is forward secrecy?", "Session keys come from ephemeral key exchange, so stealing the server's long-term private key later can't decrypt previously recorded traffic."),
  ("A", "Where should TLS be terminated in a large system?", "Usually at the CDN/edge or load balancer (central cert management, offloaded CPU, L7 routing), then re-encrypted to backends or using mTLS inside (often via a service mesh) for zero-trust networks."),
  ("A", "What is mTLS and when is it used?", "Both sides present certificates, so the server also authenticates the client. Used for service-to-service auth in zero-trust networks, B2B APIs, and IoT devices."))

Q("rest",
  ("B", "What are the principles of REST?", "Resources identified by URLs, standard HTTP methods, stateless requests, representations (JSON), cacheability, uniform interface; optionally hypermedia (HATEOAS)."),
  ("B", "Design REST endpoints for a blog with posts and comments.", "GET/POST /posts, GET/PATCH/DELETE /posts/{id}, GET/POST /posts/{id}/comments, DELETE /comments/{id}. Use plural nouns, nesting only for ownership."),
  ("I", "Offset vs cursor pagination?", "Offset (`?page=5`) is simple but slow for deep pages and skips/duplicates items when data changes. Cursor (`?after=<id>`) uses an indexed position: stable and fast, but no random page jumps."),
  ("I", "How do you version a REST API?", "URL (/v1/…), header (Accept: application/vnd.x.v2+json), or query param. Prefer additive, backward-compatible changes; version only for breaking changes and keep old versions for a deprecation window."),
  ("I", "How do you make a POST endpoint safe to retry?", "Require a client-generated Idempotency-Key; store the key with the response; on retry return the stored response instead of creating again."),
  ("I", "How do you prevent lost updates in a REST API?", "Optimistic concurrency with ETags: GET returns ETag; PATCH sends If-Match; the server returns 412 Precondition Failed if the resource changed."),
  ("A", "What makes a good error response design?", "Correct status code plus a consistent body: machine-readable code, human message, details per field, a request/trace id, and docs link. Never leak stack traces or internals."))

Q("rpc-grpc",
  ("B", "What is RPC?", "Remote Procedure Call: calling a function on another machine as if it were local; a stub serialises arguments, sends them over the network and deserialises the result."),
  ("B", "What is gRPC and what does it use under the hood?", "Google's RPC framework: services and messages defined in Protocol Buffers, code-generated clients/servers, binary messages over HTTP/2 with streaming, deadlines and metadata."),
  ("I", "REST vs gRPC: when would you choose each?", "REST/JSON for public APIs and browsers (human-readable, cacheable, universal). gRPC for internal service-to-service calls: smaller/faster payloads, strict contracts, streaming, multi-language codegen."),
  ("I", "What streaming modes does gRPC support?", "Unary, server streaming, client streaming, and bidirectional streaming."),
  ("I", "How do you evolve protobuf schemas without breaking clients?", "Never reuse or renumber field tags; add new optional fields; don't change types; mark removed fields as reserved. Old clients ignore unknown fields."),
  ("A", "Why are deadlines important in gRPC/microservices?", "A deadline propagates the remaining time budget across calls so downstream services stop work the caller has already given up on, preventing wasted work and cascading slowness."),
  ("A", "What are the downsides of making remote calls look local?", "Hides latency, partial failure and serialisation cost (the fallacies of distributed computing). Developers may call in loops (N+1), forget timeouts and retries, or assume exactly-once."))

Q("graphql",
  ("B", "What is GraphQL?", "A query language and runtime where clients send a query against a typed schema to one endpoint and get exactly the fields they asked for, possibly spanning multiple resources."),
  ("B", "What problems does GraphQL solve compared with REST?", "Over-fetching (too many fields), under-fetching (several round trips for one screen), and frequent backend changes per client screen."),
  ("I", "What is the N+1 problem in GraphQL and how do you fix it?", "Resolving a list then a field per item triggers one query per item. Fix with DataLoader-style batching and caching per request, or join-aware resolvers."),
  ("I", "Why is caching harder with GraphQL?", "Queries are usually POSTs to one URL with varied shapes, so HTTP/CDN caching doesn't work out of the box. Use persisted queries over GET, normalised client caches (Apollo), and field-level server caches."),
  ("I", "Queries, mutations and subscriptions?", "Queries read; mutations change data; subscriptions push updates to clients (often via WebSockets)."),
  ("A", "How do you protect a GraphQL API from expensive queries?", "Depth and complexity limits, query cost analysis, timeouts, pagination limits, persisted/allow-listed queries, and per-client rate limits."))

Q("realtime-comm",
  ("B", "Short polling vs long polling vs WebSockets vs SSE?", "Short polling: ask periodically (simple, wasteful, delayed). Long polling: server holds the request until data arrives. SSE: one-way server → client stream over HTTP. WebSocket: full-duplex persistent connection."),
  ("I", "When would you choose SSE over WebSockets?", "When updates only flow server → client (notifications, live scores, LLM token streaming): simpler, works over plain HTTP/2, auto-reconnect and event ids built in."),
  ("I", "How do you scale WebSocket servers?", "Many connections per server (async I/O), a connection registry (user → server), pub/sub (Redis/Kafka) to route messages to the right server, sticky routing at the LB, and graceful reconnect on deploys."),
  ("I", "How do you detect dead WebSocket connections?", "Application-level heartbeats/ping-pong with timeouts; close and clean up sessions when missed; clients reconnect with backoff."),
  ("A", "How do you avoid missing messages when a client reconnects?", "Sequence numbers per stream; the client sends its last seen id on reconnect (SSE Last-Event-ID) and the server replays from a durable log."),
  ("A", "What are webhooks and what makes them reliable?", "Server-to-server HTTP callbacks on events. Reliability: retries with backoff, idempotent receivers (event ids), signatures (HMAC) for authenticity, and a dead-letter/replay UI."))

Q("api-gateway",
  ("B", "What is an API gateway?", "A single entry point in front of backend services that handles cross-cutting concerns: routing, authentication, rate limiting, TLS termination, logging, request transformation."),
  ("I", "API gateway vs load balancer vs reverse proxy?", "A reverse proxy forwards requests to servers; a load balancer is a reverse proxy focused on distributing load; a gateway is an L7 proxy with API-aware features (auth, quotas, versioning, aggregation)."),
  ("I", "What should NOT go into the gateway?", "Business logic and per-feature aggregation; that couples teams to the gateway and makes it a bottleneck. Keep it thin; use BFFs for client-specific composition."),
  ("I", "How does the gateway pass user identity to services?", "Validate the token (or JWT signature) at the gateway, then forward a trusted header (user id, scopes) or a short-lived internal token over an authenticated internal network (mTLS)."),
  ("A", "How do you keep the gateway from being a single point of failure or bottleneck?", "Run many stateless instances behind an LB across AZs, keep rate-limit state in a fast shared store, cache auth keys, set timeouts per route, and autoscale."),
  ("A", "What is the BFF pattern and how is it related?", "A backend-for-frontend is a per-client (mobile, web) aggregation layer behind the gateway that shapes responses for that UI, owned by the frontend team."))

Q("proxies",
  ("B", "Forward proxy vs reverse proxy?", "A forward proxy sits in front of clients and makes requests on their behalf (corporate egress, anonymity). A reverse proxy sits in front of servers and receives requests for them (load balancing, TLS, caching)."),
  ("I", "What can a reverse proxy do?", "Load balancing, TLS termination, caching, compression, rate limiting, WAF, request routing, serving static files, hiding backend topology."),
  ("I", "What is a sidecar proxy?", "A proxy deployed next to each service instance (same pod) that handles its network traffic: retries, mTLS, metrics. The building block of a service mesh (Envoy)."),
  ("I", "Can a reverse proxy cache dynamic content? What are the risks?", "Yes, with short TTLs, cache keys that include the right headers (Vary), and never caching per-user/private responses unless the key includes the user. Risks: serving one user's data to another, and stale data after updates."),
  ("A", "How does a transparent proxy differ from an explicit one?", "Clients don't know about a transparent proxy (traffic is intercepted by routing/iptables); an explicit proxy is configured in the client. Transparent proxies are used in meshes and corporate networks."))

Q("rate-limiting",
  ("B", "Why rate limit an API?", "Protect against abuse and DDoS, prevent one client from starving others, control costs, and enforce plan quotas."),
  ("B", "Name common rate-limiting algorithms.", "Token bucket, leaky bucket, fixed window counter, sliding window log, sliding window counter."),
  ("I", "Explain the token bucket.", "A bucket holds up to C tokens and refills at R per second; each request takes a token or is rejected. Allows bursts up to C while enforcing average rate R; needs only two numbers per key."),
  ("I", "What's the problem with fixed-window counters?", "Bursts at window edges: a client can send the full limit at the end of one window and again at the start of the next, 2× the limit in a short time."),
  ("I", "How do you implement a distributed rate limiter?", "Central counters in Redis keyed by client + window, updated atomically (INCR + EXPIRE or a Lua script for sliding window/token bucket), checked at the gateway. Return 429 with Retry-After."),
  ("A", "Should a rate limiter fail open or fail closed if Redis is down?", "Usually fail open (allow traffic) to avoid an outage caused by the limiter, with local fallback limits; fail closed for security-sensitive endpoints like login or payments."),
  ("A", "How do you reduce latency/cost of a central limiter at very high QPS?", "Local in-memory pre-limits per gateway, batched counter syncs, approximate counters, sharding Redis by key, and only checking the central store when near the limit."))
