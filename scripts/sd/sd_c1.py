"""System Design concepts, part 1: Foundations, Networking & APIs.
Body text is "markdown-lite": blank-line paragraphs, '- ' bullets, '1. ' steps, '### ' subheads, **bold**, `code`,
'|a|b|' tables (first row = header), ```java fenced code```.
Diagram specs: {"rows": [[node,...],...], "edges": [[a,b,label],...], "dir": "down"|"right"} where a node can be
prefixed "db:", "q:" (queue), "c:" (cache), "u:" (user/client), "x:" (external) to pick its shape.
Sequence specs: {"seq": [actor,...], "msgs": [[from,to,label],...]}."""
from sd_util import C

FOUNDATIONS = [
C("what-is-sd", "What is system design?", "Basic",
  "Deciding how the pieces of a software system (servers, databases, caches, queues) fit together so it works for many users, fast and without breaking.",
  """When you write a LeetCode solution, one program runs on one computer with one input. Real products such as YouTube, Uber or Gmail serve **millions of people at the same time**, store **petabytes** of data and must keep working when machines crash. System design is the skill of planning that.

### Two kinds of system design
- **High-level design (HLD):** the big boxes and arrows. Which services exist, how data flows, which database, where the cache goes, how it scales. Asked as "Design Instagram".
- **Low-level design (LLD):** the code structure inside one service: classes, interfaces, design patterns, how objects talk. Asked as "Design a parking lot" and answered in Java.

### What every design balances
- **Scalability:** can it handle 10x more users?
- **Availability:** is it up when people need it?
- **Latency:** how fast does one request finish?
- **Consistency:** does everyone see the same data?
- **Cost and simplicity:** can a team build and run it?

You can never maximise all of them. **System design is the art of trade-offs**, and interviews test whether you can explain *why* you chose one.""",
  analogy="Designing a restaurant: one cook in a tiny kitchen works for 10 guests. For 10,000 guests you need more cooks (servers), a waiter system (load balancer), pre-made dishes (cache), a pantry (database) and a ticket rail (queue).",
  tips=["Interviewers grade the conversation, not a perfect diagram: clarify, estimate, design, then deep-dive.",
        "Always say the trade-off out loud: 'I choose X, which costs us Y'."],
  diagram={"rows": [["u:Users"], ["Load balancer"], ["App server 1", "App server 2"], ["c:Cache", "db:Database", "q:Queue"]],
           "edges": [["Users", "Load balancer", "HTTPS"], ["Load balancer", "App server 1"], ["Load balancer", "App server 2"],
                     ["App server 1", "Cache"], ["App server 1", "Database"], ["App server 2", "Database"], ["App server 2", "Queue"]]}),

C("client-server", "Client–server model", "Basic",
  "A client (browser, app) asks; a server (a program on a machine somewhere) answers.",
  """Almost every system starts here. The **client** sends a **request** over the network; the **server** does the work (reads a database, runs logic) and sends back a **response**.

- A server is just a program listening on a **port** (e.g. 443 for HTTPS) on a machine with an **IP address**.
- Clients are many and untrusted; servers are few and controlled by you.
- **Thin client** (browser just shows HTML from the server) vs **thick client** (mobile app with lots of logic and local storage).

### Peer-to-peer (the alternative)
In P2P (BitTorrent, early Skype) every machine is both client and server. No central bottleneck, but hard to control, secure and keep consistent. Most products use client–server with P2P only for special cases (WebRTC video calls).""",
  analogy="You (client) order at a counter; the kitchen (server) cooks and hands the plate back.",
  example="Opening instagram.com: your browser (client) sends `GET /feed` to Instagram's servers, which return JSON with posts.",
  diagram={"seq": ["Client", "Server", "Database"], "msgs": [["Client", "Server", "GET /feed"], ["Server", "Database", "SELECT posts"], ["Database", "Server", "rows"], ["Server", "Client", "200 OK + JSON"]]}),

C("url-journey", "What happens when you type a URL and press Enter", "Basic",
  "The classic end-to-end question: DNS lookup, TCP + TLS connection, HTTP request, load balancer, server, database, response, rendering.",
  """This single question touches most of system design. Walk through it in order:

1. **Parse the URL**: scheme `https`, host `www.amazon.in`, path `/cart`.
2. **DNS lookup**: browser cache → OS cache → router → ISP resolver → root server → `.in` TLD server → Amazon's authoritative server returns an **IP address** (often of a CDN or load balancer near you).
3. **TCP connection**: the 3-way handshake (SYN, SYN-ACK, ACK) to port 443.
4. **TLS handshake**: agree on encryption, verify the certificate, derive session keys. (TLS 1.3 needs 1 round trip.)
5. **HTTP request**: `GET /cart` with headers and cookies.
6. **Edge**: a **CDN** may answer static files directly; otherwise the request reaches a **load balancer**.
7. **Load balancer** picks a healthy **app server**.
8. **App server** checks the **cache**, falls back to the **database**, maybe calls other **microservices**.
9. **Response**: `200 OK` with HTML/JSON, compressed (gzip/brotli).
10. **Browser renders**: parses HTML, fetches CSS/JS/images (many from the CDN), runs JavaScript, paints the page.

Each hop adds **latency**, which is why CDNs, keep-alive connections, caching and HTTP/2 exist.""",
  tips=["Go as deep as the interviewer wants: they may stop you at DNS and ask how DNS scales.",
        "Mention connection reuse (keep-alive) and that TLS 1.3/QUIC cut round trips."],
  diagram={"rows": [["u:Browser"], ["x:DNS resolver", "x:CDN edge"], ["Load balancer"], ["App server"], ["c:Cache", "db:Database"]],
           "edges": [["Browser", "DNS resolver", "1 IP?"], ["Browser", "CDN edge", "2 static"], ["Browser", "Load balancer", "3 HTTPS"], ["Load balancer", "App server", "4"], ["App server", "Cache", "5"], ["App server", "Database", "6 miss"]]}),

C("latency-throughput", "Latency, throughput and bandwidth", "Basic",
  "Latency = how long one request takes. Throughput = how many requests per second the system finishes. Bandwidth = the maximum data per second a link can carry.",
  """These three are often confused.

- **Latency**: time for one operation, e.g. 120 ms for a page load. Measured as **percentiles**: p50 (median), p95, **p99** (the slowest 1%). Tail latency matters because one page may call 50 services; the slowest one decides.
- **Throughput**: work done per unit time, e.g. 20,000 requests/second (**QPS** or **RPS**).
- **Bandwidth**: capacity of the pipe, e.g. 1 Gbps. Throughput can never exceed bandwidth.

### How they relate
A highway: **bandwidth** = number of lanes, **latency** = travel time for one car, **throughput** = cars that actually arrive per hour. Adding lanes raises throughput but does not make one car faster.

### Little's Law
`concurrent requests = throughput × latency`. At 1,000 RPS with 200 ms latency you have about 200 requests in flight, so you need enough threads/connections for 200.""",
  example="A search service answers in 40 ms p50 but 900 ms p99 because of garbage-collection pauses. Users notice the p99, so you fix tails, not averages.",
  tips=["Always talk in p99, not averages.", "Use Little's Law to size thread pools and connection pools."]),

C("scalability", "Scalability: vertical vs horizontal", "Basic",
  "Scalability is handling more load by adding resources. Vertical = a bigger machine. Horizontal = more machines.",
  """|Vertical scaling (scale up)|Horizontal scaling (scale out)|
|Buy a bigger server: more CPU, RAM, SSD|Add more servers behind a load balancer|
|Simple: no code changes|Needs stateless servers, load balancing, data partitioning|
|Hard ceiling (largest machine) and expensive at the top|Almost unlimited, uses cheap commodity machines|
|Single point of failure|Survives individual machine failures|

### Making servers horizontally scalable
- Keep app servers **stateless**: store sessions in Redis or a database, not in server memory, so any server can handle any request.
- Scale the **database** separately: read replicas, caching, then sharding.

### Other dimensions
- **Functional decomposition**: split into services (users, payments, search) that scale independently.
- **Data partitioning**: split data across machines (sharding).

Real systems start vertical (simple) and go horizontal when they must.""",
  analogy="Vertical: replace your car with a bus. Horizontal: run ten cars. The bus has a size limit; you can always add cars.",
  tips=["Say 'stateless app tier behind a load balancer, scale horizontally' early in any design."],
  diagram={"rows": [["Small server"], ["Big server"]], "edges": [["Small server", "Big server", "scale up"]]}),

C("availability", "Availability, the 'nines' and SLAs", "Basic",
  "Availability is the percentage of time a system works. 99.9% ('three nines') still allows 8.8 hours of downtime a year.",
  """|Availability|Downtime per year|Per month|
|99% (two nines)|3.65 days|7.3 hours|
|99.9% (three nines)|8.77 hours|43.8 minutes|
|99.99% (four nines)|52.6 minutes|4.4 minutes|
|99.999% (five nines)|5.3 minutes|26 seconds|

### Combining components
- **In series** (request needs A *and* B): availability multiplies. Two 99.9% services → 99.8%.
- **In parallel** (A *or* its copy B): `1 − (1−a)²`. Two 99% replicas → 99.99%.

That is why we add **redundancy**: replicas, multiple availability zones, failover.

### SLA, SLO, SLI
- **SLI** (indicator): what you measure, e.g. % of requests answered under 300 ms.
- **SLO** (objective): your internal target, e.g. 99.9% per month.
- **SLA** (agreement): the contract with customers, with penalties (refunds) if missed. SLA is looser than the SLO.
- **Error budget** = 100% − SLO. If you still have budget, ship features; if it is spent, focus on reliability.""",
  example="AWS S3 is designed for 99.99% availability and 99.999999999% (11 nines) durability: rarely down, almost never loses data.",
  tips=["Availability ≠ durability: availability is 'can I reach it now', durability is 'is my data still there'."]),

C("reliability-terms", "Reliability, durability, fault tolerance, resilience", "Basic",
  "Related words with different meanings: reliable = gives correct results; durable = never loses data; fault tolerant = keeps working when parts fail.",
  """- **Reliability**: the system does the right thing, even with bad input or failures. Measured by **MTBF** (mean time between failures).
- **Durability**: once you were told 'saved', the data survives crashes and disk failures (replication, write-ahead logs, backups).
- **Fault tolerance**: individual failures (a disk, a server, a whole data centre) don't take the system down. Achieved with **redundancy** and **no single point of failure (SPOF)**.
- **Resilience**: ability to recover quickly. Measured by **MTTR** (mean time to recovery).
- **Fault vs failure**: a *fault* is one component misbehaving; a *failure* is the whole system stopping for users. Good design stops faults from becoming failures.

### Types of faults
- **Hardware**: disks die (~1–2%/year), machines crash, power and network fail.
- **Software**: bugs, memory leaks, a bad deploy, cascading failures.
- **Human**: misconfiguration is the top cause of outages, so use automation, canary deploys and quick rollback.""",
  tips=["Find and remove single points of failure in every design you draw."]),

C("estimation", "Back-of-the-envelope estimation", "Basic",
  "Quick maths to size a system: requests per second, storage, bandwidth and number of servers, using round numbers.",
  """Interviewers expect 3–5 minutes of estimation. Round aggressively; the goal is the **order of magnitude**.

### Handy numbers
- 1 day ≈ **86,400 s ≈ 10⁵ s**. 1 month ≈ 2.5 × 10⁶ s. 1 year ≈ 3 × 10⁷ s.
- 1 million requests/day ≈ **12 requests/second**.
- Peak traffic ≈ **2–3 × average**.
- 1 KB = 10³ bytes, 1 MB = 10⁶, 1 GB = 10⁹, 1 TB = 10¹², 1 PB = 10¹⁵.
- One modern app server handles roughly 1,000–10,000 simple requests/second; one Redis node ~100,000 ops/s; one Postgres node a few thousand writes/s.

### Recipe
1. **Users**: DAU (daily active users).
2. **QPS**: `DAU × actions per user ÷ 86,400`; then peak = ×2 or ×3. Split read vs write.
3. **Storage**: `writes/day × size of each × days retained × replication factor (3)`.
4. **Bandwidth**: `QPS × response size`.
5. **Servers**: `peak QPS ÷ QPS per server`, plus headroom.

### Worked example: a Twitter-like app
- 200M DAU, each posts 2 tweets and reads 100 per day.
- Write QPS = 200M × 2 / 10⁵ = **4,000/s** (peak ~10,000/s).
- Read QPS = 200M × 100 / 10⁵ = **200,000/s** → read-heavy, so cache aggressively.
- Storage: 400M tweets/day × 300 bytes ≈ 120 GB/day ≈ **45 TB/year** text (media goes to object storage).""",
  tips=["State assumptions out loud, then compute.", "Point out what the numbers imply: 'read-heavy 50:1, so caching and read replicas'."],
  lab="estimator"),

C("latency-numbers", "Latency numbers every engineer should know", "Basic",
  "Approximate times for common operations. Memory is ~1,000x faster than disk; crossing an ocean costs ~150 ms.",
  """|Operation|Time|
|L1 cache reference|0.5 ns|
|Branch mispredict|5 ns|
|Main memory (RAM) reference|100 ns|
|Compress 1 KB with Snappy|3 µs|
|Send 1 KB over 1 Gbps network|10 µs|
|SSD random read|16–100 µs|
|Read 1 MB sequentially from RAM|3–250 µs|
|Round trip within same data centre|0.5 ms|
|Read 1 MB sequentially from SSD|1 ms|
|HDD disk seek|10 ms|
|Read 1 MB sequentially from HDD|20 ms|
|Round trip California ↔ Netherlands|150 ms|

### Lessons
- **Memory is fast, disk is slow, network across regions is slowest.** Cache in memory.
- **Sequential reads beat random reads** (why Kafka and LSM trees append to logs).
- Compress before sending over the network.
- Avoid cross-region calls inside a single user request; replicate data closer to users.""",
  tips=["You don't need exact values; know the ratios (RAM ≈ 100 ns, SSD ≈ 100 µs, same-DC RTT ≈ 0.5 ms, cross-continent ≈ 150 ms)."]),

C("perf-vs-scale", "Performance vs scalability, and how systems fail under load", "Intermediate",
  "A performance problem: slow for one user. A scalability problem: fast for one user, slow under heavy load.",
  """- **Performance**: optimise the single request: better algorithms, indexes, fewer network calls, caching.
- **Scalability**: keep performance as load grows: more machines, partitioning, async processing.

### What happens as load rises
Latency stays flat until a resource (CPU, DB connections, disk IO, a lock) saturates, then **queues build up and latency shoots up** (the 'hockey stick'). Past that point, more requests time out, clients retry, and load gets even worse: a **retry storm**.

### Bottleneck hunting
1. Find the saturated resource (CPU %, connection pool waits, DB slow queries, GC).
2. Remove it: cache, index, batch, add replicas, partition, or make work async.
3. Repeat: removing one bottleneck reveals the next.

### Amdahl's law
If 10% of the work is serial (e.g. a single DB lock), you can never get more than 10x speed-up however many machines you add. Remove serial parts first.""",
  tips=["Mention load testing (JMeter, k6, Gatling) and capacity planning with headroom (~30–50%)."]),

C("cap-intro", "Consistency vs availability: a first look", "Basic",
  "When data is copied to several machines and the network breaks, you must choose: refuse requests (stay consistent) or answer with possibly stale data (stay available).",
  """Imagine your bank balance is stored on two servers in two cities. The cable between them is cut. A request arrives at server A.

- **Choose consistency (CP):** A refuses or waits, because it cannot be sure B didn't change the balance. Correct but unavailable.
- **Choose availability (AP):** A answers with what it has. Always responsive, but maybe stale.

Banks and inventory counts usually pick **consistency**; social feeds, likes and view counters pick **availability** ('eventually' everyone sees the same thing).

This is the **CAP theorem** in one paragraph; the full version (and PACELC) is in the Distributed systems tab.""",
  analogy="Two shopkeepers share one stock register by phone. The phone line dies. Do they stop selling (consistent) or keep selling and fix the count later (available)?",
  see=("cap", "consistency-models")),
]

NETWORKING = [
C("osi-tcpip", "Network layers: OSI and TCP/IP models", "Basic",
  "Networking is built in layers; each layer uses the one below. You mostly care about L3 (IP), L4 (TCP/UDP) and L7 (HTTP).",
  """|OSI layer|What it does|Examples|
|7 Application|What apps speak|HTTP, gRPC, DNS, SMTP, WebSocket|
|6 Presentation|Encoding, encryption|TLS, JSON, compression|
|5 Session|Conversations|(merged into others in practice)|
|4 Transport|Process-to-process delivery, ports|TCP, UDP, QUIC|
|3 Network|Routing between networks|IP, ICMP|
|2 Data link|Frames on one link|Ethernet, Wi-Fi, MAC addresses|
|1 Physical|Bits on the wire|Fibre, radio|

The practical **TCP/IP model** collapses this to 4 layers: Link, Internet (IP), Transport (TCP/UDP), Application.

### Why system designers care
- **L4 load balancers** route by IP and port (fast, can't read URLs).
- **L7 load balancers** read HTTP (can route `/api` vs `/images`, terminate TLS).
- Firewalls/security groups usually work at L3/L4; WAFs at L7.""",
  tips=["Know 'L4 vs L7' cold; it comes up in every load-balancer discussion."]),

C("ip-dns", "IP addresses and DNS", "Basic",
  "Every machine on a network has an IP address; DNS is the internet's phone book that turns names like google.com into IPs.",
  """### IP addresses
- **IPv4**: 32-bit, e.g. `142.250.183.14` (~4.3 billion addresses, ran out). **IPv6**: 128-bit.
- **Private ranges** (`10.x`, `192.168.x`) are used inside data centres and homes; **NAT** maps them to a public IP.
- **CIDR** `10.0.0.0/16` means the first 16 bits are fixed: 65,536 addresses.

### How DNS resolves `www.example.com`
1. Browser and OS caches.
2. **Recursive resolver** (your ISP, or 8.8.8.8) does the work:
3. asks a **root server** → 'ask the .com servers',
4. asks the **TLD server** → 'ask example.com's nameserver',
5. asks the **authoritative nameserver** → `93.184.216.34`.
6. Result is cached for its **TTL** (e.g. 300 s).

### Record types
`A` (name→IPv4), `AAAA` (IPv6), `CNAME` (alias to another name), `MX` (mail), `NS` (nameserver), `TXT` (verification), `SRV` (service + port).

### DNS in system design
- **DNS load balancing**: return several IPs, or different IPs per region (**GeoDNS**, latency-based routing in Route 53).
- **Failover**: health-checked records switch to a backup region.
- Low TTL = fast failover but more lookups; high TTL = fewer lookups but slow changes.
- DNS is massively cached and replicated, which is why it scales to the whole internet.""",
  diagram={"seq": ["Browser", "Resolver", "Root", "TLD .com", "Authoritative"], "msgs": [["Browser", "Resolver", "example.com?"], ["Resolver", "Root", "example.com?"], ["Root", "Resolver", "ask .com"], ["Resolver", "TLD .com", "example.com?"], ["TLD .com", "Resolver", "ask ns1.example"], ["Resolver", "Authoritative", "example.com?"], ["Authoritative", "Resolver", "93.184.216.34"], ["Resolver", "Browser", "IP (cached TTL)"]]}),

C("tcp-udp", "TCP vs UDP", "Basic",
  "TCP is reliable and ordered (web, databases, payments). UDP is fast and fire-and-forget (live video, games, DNS, voice).",
  """|TCP|UDP|
|Connection-oriented (3-way handshake)|Connectionless|
|Guarantees delivery (retransmits lost packets)|No guarantee; packets may be lost|
|Keeps order|May arrive out of order|
|Flow control and congestion control|None: sends as fast as you want|
|Higher latency, header 20+ bytes|Lower latency, header 8 bytes|
|HTTP/1.1, HTTP/2, databases, SSH, email|DNS, video calls, online games, live streaming, QUIC|

### The TCP handshake and teardown
`SYN → SYN-ACK → ACK` opens a connection (1 round trip before data). `FIN/ACK` closes it. Because the handshake costs a round trip, we **reuse connections** (keep-alive, connection pools).

### Head-of-line blocking
With TCP one lost packet stalls everything behind it. HTTP/3 runs over **QUIC (on UDP)** to avoid this.

### When to pick UDP
When late data is useless: a video frame that arrives 2 s late is worse than a skipped frame.""",
  diagram={"seq": ["Client", "Server"], "msgs": [["Client", "Server", "SYN"], ["Server", "Client", "SYN-ACK"], ["Client", "Server", "ACK"], ["Client", "Server", "data (HTTP request)"], ["Server", "Client", "data + ACK"], ["Client", "Server", "FIN"], ["Server", "Client", "FIN-ACK"]]}),

C("http", "HTTP: methods, status codes, headers, versions", "Basic",
  "HTTP is the request/response language of the web: a method + URL + headers + optional body, answered by a status code + headers + body.",
  """### Methods
|Method|Meaning|Safe?|Idempotent?|
|GET|Read a resource|Yes|Yes|
|POST|Create / trigger an action|No|No|
|PUT|Replace a resource fully|No|Yes|
|PATCH|Update part of a resource|No|Not necessarily|
|DELETE|Remove|No|Yes|
|HEAD / OPTIONS|Headers only / allowed methods (CORS preflight)|Yes|Yes|

**Idempotent** = doing it twice has the same effect as once. Important for safe **retries**.

### Status codes
- **2xx success**: 200 OK, 201 Created, 202 Accepted (async), 204 No Content.
- **3xx redirect**: 301 Moved Permanently (cached by browsers), 302/307 temporary, 304 Not Modified (cache still valid).
- **4xx client error**: 400 Bad Request, 401 Unauthenticated, 403 Forbidden, 404 Not Found, 409 Conflict, 429 Too Many Requests.
- **5xx server error**: 500 Internal, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout.

### Useful headers
`Cache-Control`, `ETag`/`If-None-Match` (conditional GET → 304), `Authorization`, `Content-Type`, `Accept-Encoding: gzip`, `Retry-After`, `X-Request-Id` (tracing), `Idempotency-Key`.

### Versions
- **HTTP/1.1**: one request at a time per connection (browsers open ~6 connections), keep-alive.
- **HTTP/2**: binary, **multiplexes** many requests over one TCP connection, header compression (HPACK), server push.
- **HTTP/3**: runs over **QUIC (UDP)**, no TCP head-of-line blocking, 0–1 RTT setup, survives network changes (Wi-Fi → 4G).

HTTP is **stateless**: each request carries everything needed (cookies/tokens), which makes servers easy to scale.""",
  tips=["301 vs 302 matters in URL-shortener design (caching vs analytics).", "429 + Retry-After is the right answer for rate limits."]),

C("tls", "HTTPS and TLS: how encryption on the web works", "Intermediate",
  "TLS encrypts traffic and proves the server's identity with a certificate; HTTPS is HTTP inside TLS.",
  """### What TLS gives you
- **Confidentiality**: nobody on the path can read data.
- **Integrity**: nobody can change it unnoticed.
- **Authentication**: the server proves it really is `bank.com` using a **certificate** signed by a trusted **Certificate Authority (CA)**.

### Handshake (TLS 1.3, simplified)
1. Client hello: supported ciphers + a key share (Diffie–Hellman).
2. Server hello: chosen cipher + its key share + certificate + signature.
3. Both compute the same **session key** (asymmetric crypto used only to agree on it).
4. All data then uses fast **symmetric encryption** (AES-GCM / ChaCha20).

TLS 1.3 needs **1 round trip** (0-RTT for resumed sessions); TLS 1.2 needed 2.

### In system design
- **TLS termination** at the load balancer or API gateway: it decrypts, then talks to backends over a private network (or re-encrypts: **end-to-end TLS**, required in banking).
- **mTLS** (mutual TLS): both sides present certificates. Used for service-to-service auth inside a service mesh.
- Certificates expire, so automate renewal (Let's Encrypt, AWS ACM).""",
  diagram={"seq": ["Client", "Server"], "msgs": [["Client", "Server", "ClientHello + key share"], ["Server", "Client", "ServerHello + key share + certificate"], ["Client", "Server", "Finished (keys derived)"], ["Client", "Server", "encrypted HTTP request"], ["Server", "Client", "encrypted response"]]}),

C("rest", "REST API design", "Basic",
  "REST models your system as resources (nouns) addressed by URLs and manipulated with HTTP methods, using JSON and status codes.",
  """### Good REST design
- **Nouns, plural**: `GET /users/42/orders`, not `GET /getOrdersForUser?id=42`.
- **Methods carry the verb**: `POST /orders` (create), `GET /orders/9` (read), `PATCH /orders/9` (update), `DELETE /orders/9`.
- **Status codes**: 201 + `Location` header on create, 404 when missing, 409 on conflicts, 422 on validation errors.
- **Stateless**: auth token on every request.
- **Filtering, sorting**: `GET /products?category=books&sort=-price`.

### Pagination
- **Offset**: `?limit=20&offset=40`. Simple; slow for deep pages and can skip/duplicate rows when data changes.
- **Cursor (keyset)**: `?limit=20&after=eyJpZCI6MTIzfQ`. The cursor encodes the last seen key; the query is `WHERE id < 123 ORDER BY id DESC LIMIT 20`. Fast and stable; used by Twitter, Facebook, Slack.

### Versioning
`/v1/users` in the path (most common), or a header (`Accept: application/vnd.app.v2+json`). Never break existing clients; add fields, don't rename.

### Idempotency
For `POST /payments`, the client sends `Idempotency-Key: <uuid>`; the server stores the result per key, so a retried request returns the same result instead of charging twice.

### Errors
Return a consistent body: `{"error": {"code": "CARD_DECLINED", "message": "...", "requestId": "..."}}`.""",
  example="Stripe's API is a famous example: plural nouns, idempotency keys, cursor pagination (`starting_after`), dated versions.",
  tips=["In interviews write 3–6 key endpoints with request/response fields; that's enough."]),

C("rpc-grpc", "RPC and gRPC", "Intermediate",
  "RPC makes calling a remote service look like calling a local function. gRPC is Google's fast binary RPC over HTTP/2 using Protocol Buffers.",
  """### gRPC
- You define services and messages in a `.proto` file; code is generated for Java, Go, Python etc.
- **Protocol Buffers**: compact binary encoding (3–10x smaller than JSON), strongly typed, versionable with field numbers.
- Runs on **HTTP/2**: multiplexing, and **streaming** in four modes: unary, server-streaming, client-streaming, bidirectional.
- Deadlines/timeouts and cancellation built in.

```java
// orders.proto (simplified)
service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc WatchOrders (WatchRequest) returns (stream Order);
}
```

### REST vs gRPC vs GraphQL
|REST|gRPC|GraphQL|
|JSON over HTTP, human-readable|Binary, fastest, typed contracts|Client asks exactly the fields it needs|
|Best for public APIs, browsers|Best for internal service-to-service calls|Best for many clients (web/mobile) with varied data needs|
|Easy caching with HTTP|Needs gRPC-Web for browsers|Harder caching; risk of expensive queries|

Typical big-company setup: **REST/GraphQL at the edge, gRPC between microservices.**""",
  tips=["RPC hides the network but the network can still fail: always set timeouts and retries with idempotency."]),

C("graphql", "GraphQL", "Intermediate",
  "A query language where the client describes exactly the data it wants in one request; the server resolves each field.",
  """```java
query {
  user(id: 42) {
    name
    orders(last: 3) { id total items { title } }
  }
}
```

### Why teams use it
- **No over-fetching** (REST returns fields you don't need) and **no under-fetching** (REST needs 3 calls for user + orders + items).
- One endpoint, strongly typed **schema**, great tooling. Used by Facebook, GitHub, Shopify.

### Problems to mention
- **N+1 queries**: resolving `items` for each order separately → use **DataLoader** batching.
- Expensive or malicious deep queries → **query depth/complexity limits**, persisted queries.
- HTTP caching is harder (everything is `POST /graphql`) → cache at the resolver/data layer.

GraphQL often sits as a **Backend-for-Frontend** layer that calls REST/gRPC microservices behind it.""",
  see=("rest", "rpc-grpc", "bff")),

C("realtime-comm", "Real-time communication: polling, long polling, WebSockets, SSE, webhooks", "Intermediate",
  "Ways to push updates to clients: ask repeatedly (polling), hold the request open (long polling), keep a two-way pipe (WebSocket), one-way stream (SSE), or server-to-server callbacks (webhooks).",
  """|Technique|How it works|Good for|Cost|
|Short polling|Client asks every N seconds|Rare updates, simplest|Wasteful requests, delay up to N s|
|Long polling|Server holds the request until data arrives (or ~30 s), client re-asks|Notifications where WebSockets are blocked|One pending request per client|
|WebSocket|One TCP connection upgraded from HTTP; both sides send anytime|Chat, multiplayer games, collaborative editing, live trading|Stateful connections: harder to load-balance and scale|
|Server-Sent Events (SSE)|Server streams events over a long HTTP response, one way|Live scores, stock tickers, AI token streaming|One-way only|
|Webhooks|Your server calls the customer's URL when something happens|Payment succeeded (Stripe), Git push (GitHub)|Must retry, sign payloads, handle duplicates|

### Scaling WebSockets
- Each server holds, say, 50k–1M connections. Store **which user is connected to which server** in Redis.
- To deliver a message to user B, look up B's server and route it there (via pub/sub such as Redis Pub/Sub or Kafka).
- Load balancers must support long-lived connections; use **heartbeats** to detect dead clients.
- When a server dies, clients reconnect (with backoff) to another one.""",
  diagram={"rows": [["u:User A", "u:User B"], ["WS server 1", "WS server 2"], ["q:Pub/Sub", "c:Presence (Redis)"]],
           "edges": [["User A", "WS server 1", "socket"], ["User B", "WS server 2", "socket"], ["WS server 1", "Pub/Sub", "msg to B"], ["Pub/Sub", "WS server 2", "deliver"], ["WS server 1", "Presence (Redis)", "B is on server 2?"]]},
  see=("chat-hld",)),

C("api-gateway", "API gateway", "Intermediate",
  "A single front door for all client requests that handles cross-cutting work (auth, rate limiting, routing, TLS) before forwarding to the right microservice.",
  """### What it does
- **Routing**: `/orders/*` → order service, `/users/*` → user service.
- **Authentication**: validates JWT/OAuth tokens once, so services trust the gateway.
- **Rate limiting and quotas** per API key / user.
- **TLS termination**, request/response transformation, compression.
- **Aggregation**: one client call fans out to several services and merges results.
- **Observability**: logs, metrics, tracing IDs for every request.
- Canary routing (send 5% to v2), caching, request validation.

### Examples
AWS API Gateway, Kong, Apigee, NGINX, Envoy, Spring Cloud Gateway, Netflix Zuul.

### Risks
- It's on every request: must be **highly available** (multiple instances behind a load balancer) and fast.
- Don't put business logic in it, or it becomes a bottleneck 'god service'.

### Backend for Frontend (BFF)
A separate gateway per client type (web BFF, mobile BFF) that shapes data for that client. Netflix and SoundCloud popularised it.""",
  diagram={"rows": [["u:Web", "u:Mobile"], ["API gateway"], ["User service", "Order service", "Payment service"]],
           "edges": [["Web", "API gateway"], ["Mobile", "API gateway"], ["API gateway", "User service", "/users"], ["API gateway", "Order service", "/orders"], ["API gateway", "Payment service", "/pay"]]}),

C("proxies", "Forward proxy vs reverse proxy", "Basic",
  "A forward proxy acts for clients (hides who is browsing). A reverse proxy acts for servers (hides and protects the servers).",
  """|Forward proxy|Reverse proxy|
|Sits in front of **clients**|Sits in front of **servers**|
|Server sees the proxy's IP, not the user's|Client sees the proxy, not the real servers|
|Uses: corporate filtering, caching, bypassing geo-blocks, anonymity (VPN-like)|Uses: load balancing, TLS termination, caching, compression, DDoS protection, hiding internal topology|
|Example: Squid, corporate proxy|Example: NGINX, HAProxy, Envoy, Cloudflare|

A **load balancer** is a reverse proxy that spreads load. An **API gateway** is a reverse proxy with API features. A **CDN** is a geographically distributed caching reverse proxy.""",
  diagram={"rows": [["u:Clients"], ["Reverse proxy"], ["Server 1", "Server 2"]], "edges": [["Clients", "Reverse proxy"], ["Reverse proxy", "Server 1"], ["Reverse proxy", "Server 2"]]}),

C("rate-limiting", "Rate limiting algorithms", "Intermediate",
  "Limit how many requests a client can make in a time window to protect services from abuse and overload. Five classic algorithms: token bucket, leaky bucket, fixed window, sliding log, sliding window counter.",
  """### 1. Token bucket (most used: AWS, Stripe)
A bucket holds up to **B tokens**, refilled at **R tokens/second**. Each request takes one token; empty bucket → reject (429). Allows short **bursts** up to B while enforcing the average rate R.

### 2. Leaky bucket
Requests enter a FIFO queue that drains at a constant rate. Smooths traffic into a steady flow; bursts wait or are dropped. Good when the downstream needs a constant rate.

### 3. Fixed window counter
Count requests per window (e.g. per minute: key `user42:12:05`). Simple, but **bursts at window edges**: 100 at 12:05:59 and 100 at 12:06:00 = 200 in 2 seconds.

### 4. Sliding window log
Store each request's timestamp (Redis sorted set); count those in the last 60 s. Exact, but memory-heavy.

### 5. Sliding window counter
`count = current window + previous window × (overlap fraction)`. Close to exact with only two counters. Used by Cloudflare.

### Distributed rate limiting
- Keep counters in **Redis**, updated atomically with a **Lua script** (or `INCR` + `EXPIRE`).
- Limit by user ID, API key or IP; different tiers for free/paid.
- Return **429 Too Many Requests** with `Retry-After` and `X-RateLimit-Remaining` headers.
- Where: API gateway (global), plus per-service limits. Fail open or closed when Redis is down? Usually **fail open** to avoid an outage.""",
  example="GitHub API: 5,000 requests/hour per authenticated user, reported in `X-RateLimit-*` headers.",
  tips=["Pick token bucket by default and explain burst + refill.", "Mention race conditions and why Lua/atomic ops are needed."],
  lab="ratelimit", see=("ratelimiter-hld",)),
]
