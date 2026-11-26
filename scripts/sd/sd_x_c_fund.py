"""Detailed explanations with diagrams: Fundamentals tab."""
from sd_x_util import X, P, H, AN, KEY, FLOW, SEQ, NOTE, ER, TABLE, CALC, BARS, CODE, UML, STATE, BA

X("what-is-sd",
  P("System design is deciding **which components** a product needs, **how they talk**, and **where data lives**, so that it keeps working as users grow from 100 to 100 million. The same app evolves through predictable stages:"),
  FLOW("How a typical app grows", [["u:1 · One server: app + DB together"], ["2 · Separate DB server"], ["3 · Load balancer + several app servers"], ["4 · Cache + read replicas + CDN"], ["5 · Queues, sharding, microservices, multi-region"]],
       [["1 · One server: app + DB together", "2 · Separate DB server", "~1k users"], ["2 · Separate DB server", "3 · Load balancer + several app servers", "~10k"], ["3 · Load balancer + several app servers", "4 · Cache + read replicas + CDN", "~100k–1M"],
        ["4 · Cache + read replicas + CDN", "5 · Queues, sharding, microservices, multi-region", "~10M+"]]),
  TABLE("Functional vs non-functional requirements", ["Type", "Question it answers", "Examples"], [["Functional", "what must it do?", "post a photo, follow a user, see a feed"],
        ["Non-functional", "how well must it do it?", "p99 latency < 200 ms, 99.99% available, 1 M req/s, data never lost, GDPR"]]),
  KEY("Every design answer is a trade-off between latency, throughput, consistency, availability, cost and complexity. Interviewers grade the reasoning ('reads are 100× writes, so cache…'), not the boxes.", "What's being tested"))

X("client-server",
  P("A **client** (browser, app) sends a **request**; a **server** does the work and sends a **response**. Servers should be **stateless** where possible: any server can handle any request because session data lives in a shared store, which is what lets you add servers freely."),
  SEQ("One request/response", ["Browser", "Web server", "App server", "Database"],
      [["Browser", "Web server", "GET /profile (cookie: session=abc)"], ["Web server", "App server", "forward"], ["App server", "Database", "SELECT * FROM users WHERE id = 42"],
       ["Database", "App server", "row", "r"], ["App server", "Browser", "200 OK, HTML/JSON", "r", "The server keeps no memory of this browser after replying; the cookie identifies it next time."]]),
  BA(SEQ("Session kept in server memory", ["Browser", "Load balancer", "Server A", "Server B"],
          [["Browser", "Load balancer", "POST /login"], ["Load balancer", "Server A", "forward"], ["Server A", "Browser", "OK (session stored in A's memory)", "r"],
           ["Browser", "Load balancer", "GET /cart"], ["Load balancer", "Server B", "forward (round robin)"], ["Server B", "Browser", "401: who are you? log in again", "r", "B has never heard of this session. Sticky sessions hide the problem until A restarts."]]),
     SEQ("Session in a shared store", ["Browser", "Load balancer", "Server B", "Redis (sessions)"],
          [["Browser", "Load balancer", "GET /cart (cookie sid=abc)"], ["Load balancer", "Server B", "forward (any server)"], ["Server B", "Redis (sessions)", "GET sess:abc"],
           ["Redis (sessions)", "Server B", "{user: 42}", "r"], ["Server B", "Browser", "200 cart", "r", "Any server can answer, so servers can be added, removed or restarted freely."]]),
     "Before: stateful servers", "After: stateless servers"),
  TABLE("Stateful vs stateless servers", ["", "Stateful (session in server memory)", "Stateless (session in Redis/JWT)"], [["scaling out", "needs sticky sessions", "any server works"], ["server crash", "users logged out", "nothing lost"], ["deploys", "drain carefully", "easy rolling deploys"]]))

X("url-journey",
  P("Typing `https://www.example.com` and pressing Enter triggers a chain of systems. Step through it:"),
  SEQ("From Enter to pixels", ["Browser", "DNS resolver", "CDN / server", "App server"],
      [["Browser", "Browser", "check browser/OS DNS cache", "", "Most lookups end here."], ["Browser", "DNS resolver", "where is www.example.com?", "", "The resolver asks root → .com → example.com's name servers (and caches the answers by TTL)."],
       ["DNS resolver", "Browser", "93.184.216.34", "r"], ["Browser", "CDN / server", "TCP handshake (SYN, SYN-ACK, ACK)", "", "1 round trip."],
       ["Browser", "CDN / server", "TLS handshake (certificate, keys)", "", "1 round trip in TLS 1.3; the browser verifies the certificate chain."], ["Browser", "CDN / server", "GET / (HTTP/2)"],
       ["CDN / server", "App server", "cache miss → forward"], ["App server", "Browser", "200 HTML", "r"], ["Browser", "Browser", "parse HTML → fetch CSS/JS/images (parallel) → layout → paint"]]),
  BARS("Where the time goes on a first visit (typical, ms)", [("DNS lookup", 30, "~30 ms"), ("TCP handshake", 40, "~1 RTT"), ("TLS handshake", 40, "~1 RTT"), ("Server time (TTFB)", 120, "~120 ms"), ("Download + render", 300, "~300 ms")]))

X("latency-throughput",
  P("**Latency** = how long one request takes. **Throughput** = how many requests per second the system completes. **Bandwidth** = the maximum data rate of a link. They're related by **Little's law**: requests in flight = throughput × latency."),
  AN("A motorway: latency is how long one car takes from A to B; throughput is cars per hour arriving; bandwidth is the number of lanes. Adding lanes raises throughput but doesn't make any single car faster."),
  CALC("Little's law in practice", [("Throughput target", "t = 2000", "/s"), ("Average latency per request (s)", "l = 0.15", "s"), ("Requests in flight (concurrency needed)", "t * l", "", "so you need ≥ 300 worker threads/connections"),
                                    ("If latency doubles (slow DB)", "t * l * 2", "", "same throughput now needs 600 in flight, or requests queue up")]),
  BARS("Percentiles matter: a real latency distribution", [("p50 (median)", 42, "42 ms"), ("p90", 95, "95 ms"), ("p99", 380, "380 ms"), ("p99.9", 1200, "1.2 s")],
       caption="Averages hide the tail. A page making 100 backend calls hits the p99 on most page loads, so design and alert on p99."))

X("scalability",
  P("**Vertical scaling** = a bigger machine. **Horizontal scaling** = more machines behind a load balancer. Vertical is simple until you hit the biggest machine (and it's a single point of failure); horizontal scales further but needs **stateless** servers and data partitioning."),
  BA(FLOW("One big server", [["u:Users"], ["Single server: 96 cores (biggest available)"], ["db:Database"]],
          [["Users", "Single server: 96 cores (biggest available)", "all traffic"], ["Single server: 96 cores (biggest available)", "Database"]],
          "Traffic doubles again and there is no bigger machine to buy; if it crashes, everything is down."),
     FLOW("Many small servers behind a load balancer", [["u:Users"], ["Load balancer"], ["App 1", "App 2", "App 3", "App N…"], ["db:Database (scaled separately)"]],
          [["Users", "Load balancer"], ["Load balancer", "App 1"], ["Load balancer", "App 2"], ["Load balancer", "App 3"], ["Load balancer", "App N…"], ["App 2", "Database (scaled separately)"]],
          "Add a server when load grows; one failing server only removes a share of capacity."),
     "Before: vertical scaling hits a ceiling", "After: horizontal scaling"),
  TABLE("Trade-offs", ["", "Vertical", "Horizontal"], [["limit", "biggest machine available", "practically none"], ["failure", "single point of failure", "one node down = less capacity"], ["complexity", "none", "LB, state externalised, partitioning"],
                                                    ["cost curve", "high-end hardware is pricey", "commodity machines"], ["good for", "databases early on", "stateless web/app tiers"]]))

X("availability",
  P("Availability = fraction of time the system works. Each extra 'nine' cuts allowed downtime by 10×. Components in **series** multiply their availabilities (worse); **redundant** components in parallel fail only if all fail (better)."),
  CALC("Downtime budgets", [("99% per year", "0.01 * 365 * 24", "hours"), ("99.9% per year", "0.001 * 365 * 24", "hours"), ("99.99% per year", "0.0001 * 365 * 24 * 60", "minutes"), ("99.999% per year", "0.00001 * 365 * 24 * 60", "minutes"),
                            ("Series LB 99.99% × app 99.9% × DB 99.95% = 99.84%: downtime per year", "(1 - 0.9999 * 0.999 * 0.9995) * 365 * 24", "hours", "worse than any single part"), ("Parallel: two 99.9% replicas, both down at once, per year", "(0.001 ** 2) * 365 * 24 * 3600", "seconds", "99.9999% available")]),
  TABLE("SLI, SLO, SLA", ["Term", "Meaning", "Example"], [["SLI", "what you measure", "% of requests answered < 300 ms with 2xx"], ["SLO", "internal target", "99.9% over 30 days"], ["SLA", "contract with penalties", "99.5%, else 10% credit"], ["error budget", "1 − SLO", "43 min/month you may 'spend' on risky deploys"]]))

X("reliability-terms",
  TABLE("The words, precisely", ["Term", "Question it answers", "Measured by", "Example"],
        [["Reliability", "does it do the right thing over time?", "MTBF, failure rate", "a payment is never charged twice"], ["Availability", "can I use it right now?", "% uptime", "99.99%"],
         ["Durability", "will my data still exist?", "probability of loss", "S3: 11 nines"], ["Fault tolerance", "does it keep working when parts fail?", "failures survived", "loses 1 AZ, still serves"],
         ["Resilience", "how well does it recover and degrade?", "time to recover, graceful degradation", "shows cached feed when ranking is down"]]),
  CALC("MTBF and MTTR", [("Mean time between failures", "mtbf = 1000", "hours"), ("Mean time to repair", "mttr = 1", "hours"), ("Availability = MTBF / (MTBF + MTTR)", "mtbf / (mtbf + mttr) * 100", "%", "≈ 99.9%: faster repair helps as much as fewer failures")]))

X("estimation",
  P("Estimation turns vague scale ('a billion users') into numbers that drive design choices. Use round numbers: **1 day ≈ 10⁵ seconds**, peak ≈ 2–3× average, and say what each number implies."),
  CALC("Worked example: a photo-sharing app", [("Daily active users", "dau = 100e6", ""), ("Uploads per day (10% upload 1 photo)", "up = dau * 0.1", ""), ("Upload QPS", "up / 86400", "/s"),
                                               ("Feed views per day (10 per user)", "v = dau * 10", ""), ("Read QPS (avg) → peak ×3", "v / 86400 * 3", "/s", "read-heavy → caches + CDN"),
                                               ("Storage per day (2 MB per photo)", "s = up * 2e6", "B"), ("Storage over 5 years", "s * 365 * 5", "B", "object storage, not a DB")]),
  TABLE("Numbers to memorise", ["Quantity", "Value"], [["seconds per day", "86,400 ≈ 10⁵"], ["1 M requests/day", "≈ 12 QPS"], ["1 KB × 1 M", "1 GB"], ["Redis node", "~100k ops/s"], ["SQL node", "~5–10k writes/s"], ["SSD random read", "~100 µs"]]))

X("latency-numbers",
  BARS("How long things take (log scale)", [("L1 cache reference", 0.5, "0.5 ns"), ("Main memory reference", 100, "100 ns"), ("Compress 1 KB (Snappy)", 2000, "2 µs"), ("Read 1 MB from memory", 3000, "3 µs"),
                                              ("SSD random read", 16000, "16 µs"), ("Read 1 MB from SSD", 49000, "49 µs"), ("Same-datacenter round trip", 500000, "0.5 ms"),
                                              ("Read 1 MB from HDD", 825000, "825 µs"), ("Disk seek (HDD)", 2000000, "2 ms"), ("Round trip India ↔ US", 200000000, "~200 ms")], log=True),
  TABLE("What to conclude", ["Lesson", "Design consequence"], [["memory is ~1,000× faster than a network hop", "cache hot data in-process or in Redis"], ["cross-continent trips cost ~150–200 ms", "serve users from nearby regions / CDN"],
        ["sequential beats random I/O", "append-only logs (Kafka, LSM trees)"], ["compression is cheap vs network", "compress before sending"]]))

X("perf-vs-scale",
  P("A **performance** problem: the system is slow for one user. A **scalability** problem: it's fast for one user but slow under load. Under load, latency stays flat until a resource saturates, then **queues** form and latency explodes."),
  BARS("Queueing: latency vs utilisation (M/M/1: wait ∝ 1/(1 − ρ))", [("50% busy", 2, "2× base"), ("70% busy", 3.3, "3.3×"), ("80% busy", 5, "5×"), ("90% busy", 10, "10×"), ("95% busy", 20, "20×"), ("99% busy", 100, "100×")]),
  TABLE("How systems fail under load", ["Failure", "What happens", "Mitigation"], [["queue build-up", "latency rises sharply past ~80% utilisation", "keep headroom, autoscale early"], ["retry storm", "timeouts cause retries that add more load", "backoff + jitter, retry budgets"],
        ["cascading failure", "one slow dependency ties up threads everywhere", "timeouts, circuit breakers, bulkheads"], ["thundering herd", "cache expiry sends everyone to the DB", "request coalescing, jittered TTLs"]]))

X("cap-intro",
  P("When the network between two replicas breaks, a system must choose: **refuse** some requests to stay consistent, or **answer** from possibly stale data to stay available. Which is right depends on the data."),
  SEQ("A network partition between two replicas", ["User (Mumbai)", "Replica Mumbai", "Replica Chennai", "User (Chennai)"],
      [["User (Mumbai)", "Replica Mumbai", "set balance = 500"], NOTE(["Replica Mumbai", "Replica Chennai"], "✂ network link cut: replicas can't sync"),
       ["User (Chennai)", "Replica Chennai", "read balance"], ["Replica Chennai", "User (Chennai)", "CP choice: error 'try later' / AP choice: old value 800", "r", "Consistent-but-unavailable, or available-but-stale. You can't have both during the partition."]]),
  TABLE("Pick per feature", ["Data", "Choice", "Why"], [["bank balance, seat booking, inventory", "consistency (CP)", "a wrong answer costs money"], ["likes count, feed, profile picture", "availability (AP)", "slightly stale is fine"], ["shopping cart", "availability", "always let users add items; merge later"]]))

X("osi-tcpip",
  TABLE("Layers, with what each adds to an HTTP request", ["TCP/IP layer", "OSI layers", "Protocol examples", "Adds"],
        [["Application", "7, 6, 5", "HTTP, gRPC, DNS, TLS", "the request: `GET /feed` + headers"], ["Transport", "4", "TCP, UDP, QUIC", "ports, ordering, retransmission (TCP)"],
         ["Internet", "3", "IP, ICMP", "source/destination IP, routing across networks"], ["Link", "2, 1", "Ethernet, Wi-Fi", "MAC addresses, bits on the wire"]]),
  FLOW("Encapsulation: each layer wraps the one above", [["HTTP request"], ["TCP segment = TCP header + HTTP request"], ["IP packet = IP header + TCP segment"], ["Ethernet frame = MAC header + IP packet + checksum"]],
       [["HTTP request", "TCP segment = TCP header + HTTP request"], ["TCP segment = TCP header + HTTP request", "IP packet = IP header + TCP segment"], ["IP packet = IP header + TCP segment", "Ethernet frame = MAC header + IP packet + checksum"]]),
  KEY("Load balancers are often described by layer: an **L4** LB routes by IP/port (fast, protocol-agnostic); an **L7** LB reads HTTP (route by path, headers, cookies; terminate TLS).", "Why layers matter in design"))

X("ip-dns",
  SEQ("Recursive DNS resolution for www.example.com", ["Laptop", "Recursive resolver (ISP / 8.8.8.8)", "Root server", ".com TLD server", "example.com name server"],
      [["Laptop", "Recursive resolver (ISP / 8.8.8.8)", "A record for www.example.com?"], ["Recursive resolver (ISP / 8.8.8.8)", "Root server", "who handles .com?"], ["Root server", "Recursive resolver (ISP / 8.8.8.8)", "ask a.gtld-servers.net", "r"],
       ["Recursive resolver (ISP / 8.8.8.8)", ".com TLD server", "who handles example.com?"], [".com TLD server", "Recursive resolver (ISP / 8.8.8.8)", "ask ns1.example.com", "r"],
       ["Recursive resolver (ISP / 8.8.8.8)", "example.com name server", "www.example.com?"], ["example.com name server", "Recursive resolver (ISP / 8.8.8.8)", "93.184.216.34 (TTL 300 s)", "r"],
       ["Recursive resolver (ISP / 8.8.8.8)", "Laptop", "93.184.216.34", "r", "Cached for the TTL, so most lookups are one hop."]]),
  TABLE("Record types", ["Record", "Maps", "Example"], [["A / AAAA", "name → IPv4 / IPv6", "api.example.com → 203.0.113.7"], ["CNAME", "name → another name", "www → example.cdn.net"], ["MX", "domain → mail servers", "example.com → mx1.mail.com"],
                                                       ["NS", "domain → its name servers", ""], ["TXT", "free text (SPF, verification)", "v=spf1 include:…"]]),
  KEY("DNS is also a load-balancing and failover tool: GeoDNS returns the nearest region, weighted records split traffic, health-checked records drop dead endpoints. Low TTLs make failover faster but increase DNS load.", "DNS in system design"))

X("tcp-udp",
  SEQ("TCP: connect, send reliably, close", ["Client", "Server"],
      [["Client", "Server", "SYN (seq = x)"], ["Server", "Client", "SYN-ACK (seq = y, ack = x+1)", "r"], ["Client", "Server", "ACK", "", "3-way handshake: 1 round trip before any data."],
       ["Client", "Server", "data segment 1"], ["Server", "Client", "ACK 1", "r"], ["Client", "Server", "data segment 2 (lost → resent after timeout)", "", "Retransmission, ordering, flow and congestion control are what make TCP reliable but slower to start."],
       ["Client", "Server", "FIN"], ["Server", "Client", "ACK + FIN", "r"]]),
  TABLE("TCP vs UDP", ["", "TCP", "UDP"], [["connection", "handshake first", "none"], ["delivery", "reliable, ordered", "best effort, may drop/reorder"], ["overhead", "higher", "minimal"],
                                         ["used by", "HTTP/1–2, databases, SSH", "DNS, video calls, games, QUIC (HTTP/3 builds reliability on UDP)"], ["good when", "every byte matters", "late data is useless"]]))

X("http",
  TABLE("Methods", ["Method", "Purpose", "Safe", "Idempotent"], [["GET", "read", "✔", "✔"], ["POST", "create / action", "✘", "✘ (use an Idempotency-Key)"], ["PUT", "replace", "✘", "✔"], ["PATCH", "partial update", "✘", "usually ✘"], ["DELETE", "remove", "✘", "✔"]]),
  TABLE("Status codes you must know", ["Code", "Meaning", "When"], [["200 / 201 / 204", "OK / Created / No content", "success"], ["301 / 302 / 304", "moved / temporary redirect / not modified", "redirects, caching"],
        ["400 / 401 / 403 / 404", "bad request / not authenticated / not allowed / not found", "client errors"], ["409 / 429", "conflict / too many requests", "version clash, rate limit"], ["500 / 502 / 503 / 504", "server error / bad gateway / unavailable / gateway timeout", "server-side"]]),
  TABLE("HTTP versions", ["Version", "Key change", "Fixes"], [["HTTP/1.1", "keep-alive connections", "a new TCP connection per request"], ["HTTP/2", "binary, multiplexed streams over one connection, header compression", "head-of-line blocking at HTTP level"],
                                                            ["HTTP/3", "runs on QUIC (UDP) with built-in TLS", "TCP head-of-line blocking; faster handshakes, connection migration on mobile"]]))

X("tls",
  SEQ("TLS 1.3 handshake (one round trip)", ["Browser", "Server"],
      [["Browser", "Server", "ClientHello: supported ciphers + key share (ECDHE)"], ["Server", "Browser", "ServerHello: chosen cipher + key share, certificate, signature, Finished", "r", "Both sides can now derive the same session keys from the two key shares (Diffie–Hellman)."],
       ["Browser", "Browser", "verify certificate chain → trusted CA, hostname matches, not expired"], ["Browser", "Server", "Finished + encrypted HTTP request", "", "Symmetric encryption (AES-GCM / ChaCha20) protects all further data."]]),
  TABLE("What TLS gives you", ["Property", "How"], [["confidentiality", "symmetric encryption with per-session keys"], ["integrity", "authenticated encryption (AEAD)"], ["authentication of the server", "certificate signed by a trusted CA"], ["forward secrecy", "ephemeral key exchange: old traffic stays safe if the server key leaks"]]),
  KEY("In system design: terminate TLS at the load balancer/CDN (offloads CPU, central certificate management), and use mTLS between internal services (often via a service mesh).", "Design note"))

X("rest",
  TABLE("Designing a REST API for orders", ["Action", "Request", "Response"], [["create", "POST /v1/orders {items} + Idempotency-Key", "201 + Location: /v1/orders/987"], ["read one", "GET /v1/orders/987", "200 {id, status, total}"],
        ["list (paginated)", "GET /v1/orders?status=PAID&limit=20&after=cursor", "200 {items, next_cursor}"], ["update status", "PATCH /v1/orders/987 {status: CANCELLED} + If-Match: \"v3\"", "200 or 412 if the version changed"], ["delete", "DELETE /v1/orders/987", "204"]]),
  TABLE("Good habits", ["Habit", "Why"], [["nouns + HTTP verbs", "predictable"], ["cursor pagination", "stable under inserts; offsets get slow and skip items"], ["ETag / If-Match", "optimistic concurrency, no lost updates"], ["consistent error body", "`{code, message, details}`"], ["versioning", "evolve without breaking clients"]]))

X("rpc-grpc",
  P("RPC makes a remote call look like a local function call. **gRPC** defines services in **Protocol Buffers**, generates client/server code, sends compact binary messages over **HTTP/2**, and supports streaming in both directions."),
  CODE("A .proto contract", """service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc WatchOrder (GetOrderRequest) returns (stream OrderEvent);   // server streaming
}
message GetOrderRequest { string id = 1; }
message Order { string id = 1; string status = 2; int64 total_paise = 3; }""", "protobuf"),
  TABLE("REST vs gRPC vs GraphQL", ["", "REST/JSON", "gRPC", "GraphQL"], [["payload", "text JSON", "binary protobuf (smaller, faster)", "JSON"], ["contract", "OpenAPI (optional)", "strict .proto", "schema"], ["streaming", "no (use SSE/WS)", "built in", "subscriptions"],
                                                                  ["best for", "public APIs, browsers", "internal service-to-service", "flexible client queries (mobile/web)"]]))

X("graphql",
  P("GraphQL exposes **one endpoint** and a typed schema; the client asks for **exactly the fields it needs**, possibly across several resources, in one request. This avoids over-fetching (REST returns too much) and under-fetching (several REST calls for one screen)."),
  CODE("One query for a profile screen", """query {
  user(id: "42") {
    name
    avatar(size: 64)
    posts(first: 3) { title likeCount }
  }
}""", "graphql"),
  TABLE("Watch-outs", ["Problem", "Fix"], [["N+1 resolver calls (posts → author per post)", "DataLoader batching"], ["expensive queries", "depth/complexity limits, persisted queries"], ["HTTP caching harder (POST to one URL)", "persisted queries via GET, client caches (Apollo)"]]))

X("realtime-comm",
  SEQ("Four ways to get updates to a browser", ["Browser", "Server"],
      [NOTE(["Browser", "Server"], "Short polling"), ["Browser", "Server", "any news? (every 5 s)"], ["Server", "Browser", "no", "r", "Simple but wasteful and up to 5 s late."],
       NOTE(["Browser", "Server"], "Long polling"), ["Browser", "Server", "any news? (server holds the request)"], ["Server", "Browser", "yes: message (when it happens)", "r", "Instant, but one HTTP request per message."],
       NOTE(["Browser", "Server"], "Server-Sent Events"), ["Browser", "Server", "GET /events (stays open)"], ["Server", "Browser", "event: … event: …", "r", "One-way server → client stream over HTTP; auto-reconnect."],
       NOTE(["Browser", "Server"], "WebSocket"), ["Browser", "Server", "HTTP Upgrade → WebSocket"], ["Server", "Browser", "messages both ways, any time", "r", "Full duplex: chat, games, collaboration."]]),
  TABLE("Choosing", ["Need", "Use"], [["occasional updates, simple", "polling"], ["server → client notifications, feeds, LLM token streams", "SSE"], ["two-way, low latency (chat, games)", "WebSocket"], ["server → another server on events", "webhooks"]]))

X("api-gateway",
  BA(FLOW("Clients call every service directly", [["u:Mobile / web clients"], ["User service (own auth + rate limit)", "Order service (own auth + rate limit)", "Search service (own auth + rate limit)"]],
          [["Mobile / web clients", "User service (own auth + rate limit)"], ["Mobile / web clients", "Order service (own auth + rate limit)"], ["Mobile / web clients", "Search service (own auth + rate limit)"]],
          "Clients must know every service address; auth, TLS and rate limiting are re-implemented (differently) in each service."),
     FLOW("One front door for many services", [["u:Mobile / web clients"], ["API gateway: auth · rate limit · routing · TLS · logging"], ["User service", "Order service", "Search service"]],
          [["Mobile / web clients", "API gateway: auth · rate limit · routing · TLS · logging"], ["API gateway: auth · rate limit · routing · TLS · logging", "User service", "/users/*"],
           ["API gateway: auth · rate limit · routing · TLS · logging", "Order service", "/orders/*"], ["API gateway: auth · rate limit · routing · TLS · logging", "Search service", "/search"]],
          "One public address; cross-cutting concerns live in one place; services can move or split without clients noticing."),
     "Before: no gateway", "After: API gateway"),
  SEQ("What happens at the gateway", ["Client", "API gateway", "Auth", "Order service"],
      [["Client", "API gateway", "GET /orders/9 (Bearer token)"], ["API gateway", "Auth", "validate token (or verify JWT locally)"], ["API gateway", "API gateway", "rate limit check; route by path; add request id"],
       ["API gateway", "Order service", "GET /orders/9 + X-User-Id"], ["Order service", "Client", "200", "r", "Services trust identity headers from the gateway, so they don't each re-implement auth."]]),
  KEY("Keep the gateway thin (cross-cutting concerns only). Business logic in the gateway turns it into a bottleneck and a monolith; per-client aggregation belongs in a BFF.", "Pitfall"))

X("proxies",
  FLOW("Forward vs reverse proxy", [["u:Employees", "u:Internet users"], ["Forward proxy (company)", "Reverse proxy / LB"], ["x:Any website", "Server 1", "Server 2"]],
       [["Employees", "Forward proxy (company)"], ["Forward proxy (company)", "Any website", "hides clients"], ["Internet users", "Reverse proxy / LB"], ["Reverse proxy / LB", "Server 1", "hides servers"], ["Reverse proxy / LB", "Server 2"]]),
  TABLE("Which side it protects", ["", "Forward proxy", "Reverse proxy"], [["sits in front of", "clients", "servers"], ["client knows about it?", "yes (configured)", "no (looks like the site)"],
                                                                         ["used for", "filtering, caching, anonymity, egress control", "load balancing, TLS termination, caching, compression, WAF"], ["examples", "Squid, corporate proxies", "Nginx, HAProxy, Envoy, Cloudflare"]]))

X("rate-limiting",
  TABLE("Token bucket, capacity 5, refill 1 token/s", ["Time", "Requests", "Tokens before", "Allowed", "Tokens after"],
        [["0 s", "5", "5", "5 ✔", "0"], ["0 s", "1 more", "0", "✘ 429", "0"], ["1 s", "1", "1", "1 ✔", "0"], ["4 s", "2", "3", "2 ✔", "1"]], "Bursts up to the capacity are allowed; the long-run average is the refill rate."),
  BA(BARS("Fixed window, limit 100 per minute: a burst across the boundary", [("10:00:59 burst (window 10:00)", 100, "100 allowed"), ("10:01:00 burst (window 10:01)", 100, "100 allowed")],
          caption="200 requests in 2 seconds pass a '100 per minute' limit because the counter resets at 10:01:00."),
     BARS("Sliding window, same burst", [("10:00:59 burst", 100, "100 allowed"), ("10:01:00 burst", 100, "0 allowed (last 60 s already has 100)")],
          caption="The window always looks back 60 s from now, so the limit holds across the boundary. A token bucket gives the same protection."),
     "Before: fixed window lets 2× through", "After: sliding window holds the limit"),
  TABLE("Algorithms", ["Algorithm", "Memory", "Accuracy", "Bursts"], [["Token bucket", "2 numbers", "good", "up to capacity"], ["Leaky bucket", "queue", "smooth output", "none"], ["Fixed window", "1 counter", "edge spikes", "2× at edges"],
                                                                    ["Sliding log", "1 timestamp per request", "exact", "none"], ["Sliding window counter", "2 counters", "approximate", "small"]]),
  KEY("Where to enforce: at the API gateway per key/user/IP, with counters in Redis updated by an atomic Lua script. Return 429 with `Retry-After`. See the distributed rate limiter HLD for the full design.", "In practice"))
