"""System Design concepts, part 5: Architecture, reliability & operations, security."""
from sd_util import C

ARCHITECTURE = [
C("monolith-microservices", "Monolith vs microservices vs modular monolith", "Basic",
  "A monolith is one deployable application. Microservices split it into small services, each owning its data and deployed independently. A modular monolith keeps one deployable but strict internal modules.",
  """|Monolith|Microservices|
|One codebase, one deploy, one database|Many small services, each with its own DB and deploy pipeline|
|Simple to build, test, debug, deploy early on|Teams work and deploy independently; scale hot parts separately|
|In-process calls: fast, transactional|Network calls: latency, partial failure, distributed transactions|
|Gets slow to build and risky to change as it grows|Operational overhead: service discovery, tracing, many pipelines|

### When microservices make sense
Large organisation (many teams), parts with very different scaling needs, need for independent releases. **Start with a (modular) monolith** and extract services along clear business boundaries (**bounded contexts** from Domain-Driven Design) when pain appears.

### Microservice rules of thumb
- **Database per service**: no other service reads your tables; share data via APIs or events.
- Communicate synchronously (REST/gRPC) for queries, asynchronously (events) for state changes.
- Design for failure: timeouts, retries, circuit breakers.
- Observability is mandatory: distributed tracing, centralised logs.

### SOA
Service-oriented architecture (2000s) used shared enterprise service buses (ESB) and shared schemas; microservices are a lighter, decentralised evolution.""",
  diagram={"rows": [["API gateway"], ["Users svc", "Catalog svc", "Orders svc", "Payments svc"], ["db:Users DB", "db:Catalog DB", "db:Orders DB", "db:Payments DB"]],
           "edges": [["API gateway", "Users svc"], ["API gateway", "Catalog svc"], ["API gateway", "Orders svc"], ["Orders svc", "Payments svc", "gRPC"], ["Users svc", "Users DB"], ["Catalog svc", "Catalog DB"], ["Orders svc", "Orders DB"], ["Payments svc", "Payments DB"]]}),

C("service-discovery", "Service discovery", "Intermediate",
  "In a dynamic cluster, service instances come and go with changing IPs. Service discovery lets callers find healthy instances by name.",
  """- **Service registry**: instances register on start and send heartbeats (Consul, Eureka, etcd, ZooKeeper).
- **Client-side discovery**: the caller queries the registry and load-balances itself (Netflix Eureka + Ribbon).
- **Server-side discovery**: the caller hits a load balancer/router that knows the instances (AWS ALB, Kubernetes Service).
- **DNS-based**: Kubernetes gives every Service a DNS name (`orders.default.svc.cluster.local`) pointing to a virtual IP that kube-proxy load-balances.
- Health checks remove dead instances; clients cache results briefly.""",
  see=("service-mesh",)),

C("service-mesh", "Service mesh and the sidecar pattern", "Advanced",
  "A service mesh puts a small proxy (sidecar) next to every service instance to handle networking concerns — mTLS, retries, timeouts, load balancing, metrics — without changing app code.",
  """- **Data plane**: sidecar proxies (Envoy) intercept all inbound/outbound traffic.
- **Control plane**: configures them centrally (Istio, Linkerd, Consul Connect).
- Features: mutual TLS between services, traffic splitting for canaries, retries and circuit breaking, rate limits, rich telemetry and tracing.
- Cost: extra latency per hop (~1 ms), memory per pod, operational complexity. Worth it at dozens–hundreds of services.

### Sidecar pattern in general
Run a helper container beside the main one in the same pod: log shippers, config reloaders, proxies.""",
  diagram={"rows": [["Service A", "Service B"], ["Envoy sidecar A", "Envoy sidecar B"], ["Control plane (Istio)"]],
           "edges": [["Service A", "Envoy sidecar A"], ["Envoy sidecar A", "Envoy sidecar B", "mTLS"], ["Envoy sidecar B", "Service B"], ["Control plane (Istio)", "Envoy sidecar A", "config"], ["Control plane (Istio)", "Envoy sidecar B", "config"]]}),

C("bff", "Backend for Frontend (BFF) and API composition", "Intermediate",
  "A thin backend per client type (web, iOS, Android, TV) that calls many microservices and returns exactly what that screen needs.",
  """- Mobile wants small payloads; web wants richer data; TV wants different layouts. One generic API serves none of them well.
- The BFF aggregates calls (often in parallel), trims fields, and is owned by the frontend team.
- Can be built with GraphQL. Netflix, SoundCloud and Spotify use BFF-style layers.
- Risk: duplicated logic across BFFs; keep business rules in the domain services.""",
  see=("api-gateway", "graphql")),

C("event-driven", "Event-driven architecture", "Intermediate",
  "Services announce facts ('OrderPlaced') as events; other services react to them. Producers don't know or wait for consumers.",
  """### Events vs commands
- **Command**: 'ChargeCard' — directed at one service, expects it to act.
- **Event**: 'PaymentSucceeded' — a fact that already happened; anyone may listen.

### Benefits
Loose coupling, easy to add new consumers (a new analytics service just subscribes), natural audit trail, absorbs spikes.

### Challenges
- **Eventual consistency**: the order page may show 'processing' for a second.
- Harder to follow the flow: use tracing and event catalogues.
- **Schema evolution**: use a schema registry (Avro/Protobuf) and only add optional fields.
- Duplicates and ordering: idempotent consumers, partition by entity ID.

### Patterns
Event notification (thin event, consumer calls back for details), **event-carried state transfer** (event contains the data), event sourcing, CQRS.""",
  see=("event-sourcing", "cqrs", "kafka")),

C("event-sourcing", "Event sourcing", "Advanced",
  "Instead of storing only the current state, store every change as an immutable event; current state is computed by replaying events.",
  """Bank account as events: `Opened(₹0) → Deposited(₹1000) → Withdrew(₹200)` → balance ₹800.

### Benefits
- Complete **audit trail** and history ('what was the balance on 1 March?').
- Rebuild new read models any time by replaying.
- Natural fit with event-driven systems and debugging (replay a bug).

### Costs
- Replaying millions of events is slow → periodic **snapshots**.
- Event schemas live forever; versioning is hard.
- Querying needs projections (read models) → usually combined with **CQRS**.
- GDPR 'right to be forgotten' with immutable logs needs crypto-shredding.

Used in banking ledgers, trading, Git (commits are events), Kafka-centric architectures.""",
  see=("cqrs", "payment-hld")),

C("cqrs", "CQRS (Command Query Responsibility Segregation)", "Advanced",
  "Use one model (and often one database) for writes and a different, denormalised model for reads, kept in sync by events.",
  """- **Command side**: validates and applies changes, normalised, transactional (Postgres).
- **Query side**: read-optimised projections — Elasticsearch for search, Redis for counters, a denormalised table per screen.
- Sync via events/CDC → reads are **eventually consistent**.
- Lets reads and writes scale independently (reads are often 100x writes).
- Overkill for simple CRUD; shines for complex domains and heavy, varied reads.""",
  diagram={"rows": [["u:Client"], ["Command API", "Query API"], ["db:Write DB", "db:Read models"], ["q:Events"]],
           "edges": [["Client", "Command API", "writes"], ["Client", "Query API", "reads"], ["Command API", "Write DB"], ["Write DB", "Events", "CDC"], ["Events", "Read models", "project"], ["Query API", "Read models"]]}),

C("serverless-containers", "Containers, Kubernetes and serverless", "Intermediate",
  "Containers package an app with its dependencies; Kubernetes runs and scales many containers across machines; serverless runs your function on demand without you managing servers.",
  """### Containers (Docker)
Lightweight, start in seconds, same image runs on a laptop and in production. Unlike VMs, they share the host OS kernel.

### Kubernetes basics
- **Pod**: one or more containers scheduled together. **Deployment**: keeps N replicas running, does rolling updates. **Service**: stable name + load balancing to pods. **Ingress**: HTTP routing from outside.
- **HPA** (horizontal pod autoscaler) scales on CPU or custom metrics; **cluster autoscaler** adds nodes.
- Self-healing: restarts crashed containers, reschedules pods from dead nodes; liveness/readiness probes.
- ConfigMaps/Secrets for configuration.

### Serverless (FaaS)
AWS Lambda, Google Cloud Functions, Azure Functions: pay per invocation, scale to zero and to thousands automatically.
- Great for spiky or event-driven work (image resize on upload, webhooks, cron jobs).
- Limits: **cold starts** (100 ms – seconds, worse for Java without SnapStart), execution time limits, statelessness, harder local debugging, vendor lock-in, cost at high steady load.""",
  see=("autoscaling",)),

C("resilience-patterns", "Resilience patterns: timeouts, retries with backoff and jitter, circuit breaker, bulkhead, fallback", "Intermediate",
  "Patterns that stop one slow or failing dependency from taking down the whole system.",
  """### Timeouts
Every network call needs one. Without it, threads pile up waiting forever. Set from the dependency's p99 plus margin; propagate **deadlines** down the call chain.

### Retries with exponential backoff and jitter
Retry only **idempotent** operations and only transient errors (timeouts, 503). Wait `base × 2^attempt` with random **jitter** so thousands of clients don't retry in sync; cap the attempts (e.g. 3) and use a **retry budget** to avoid retry storms.

### Circuit breaker
Track failures to a dependency:
- **Closed**: calls flow normally.
- **Open**: after e.g. 50% failures in 10 s, fail fast for 30 s without calling (gives the dependency time to recover).
- **Half-open**: let a few trial calls through; success → closed, failure → open again.
Libraries: Resilience4j (Java), Hystrix (retired), Envoy/Istio.

### Bulkhead
Separate thread pools / connection pools per dependency (like watertight compartments in a ship), so a slow recommendation service can't exhaust the threads checkout needs.

### Fallbacks and graceful degradation
Serve cached or default data (show popular items if personalised recommendations are down), hide non-critical widgets, queue writes for later.

### Others
Rate limiting, load shedding, health checks, idempotency keys, hedged requests (send a duplicate request to another replica if the first is slow at p95).""",
  diagram={"rows": [["Closed"], ["Open"], ["Half-open"]], "edges": [["Closed", "Open", "failures > threshold"], ["Open", "Half-open", "after cool-down"], ["Half-open", "Closed", "trial succeeds"]]},
  see=("idempotency",)),

C("idempotency", "Idempotency", "Intermediate",
  "An operation is idempotent if doing it several times has the same effect as doing it once. It makes retries safe.",
  """### Why it matters
Networks time out: the client doesn't know if 'charge ₹999' happened, so it retries. Without idempotency the customer is charged twice.

### How to implement (Stripe-style)
1. Client generates an **Idempotency-Key** (UUID) per logical operation and sends it with every retry.
2. Server, in one transaction: insert `(key, request_hash, status='processing')` with a **unique constraint**.
3. If the key already exists: return the stored response (or 409 if still processing / different payload).
4. After processing, store the response with the key; expire keys after ~24 h.

### Other techniques
- Natural keys + upserts: `INSERT ... ON CONFLICT (order_id) DO NOTHING`.
- Conditional updates: `UPDATE ... WHERE status = 'PENDING'`.
- Dedup tables for message consumers (processed message IDs).
- HTTP: GET, PUT, DELETE are idempotent by definition; POST is not unless you add a key.""",
  see=("payment-hld", "delivery-semantics")),

C("deployments", "Deployment strategies: rolling, blue-green, canary, feature flags", "Intermediate",
  "Ways to release new code without downtime and with a quick way back if something breaks.",
  """|Strategy|How|Pros|Cons|
|Rolling|Replace instances a few at a time|No extra capacity needed|Old and new run together; slow rollback|
|Blue-green|Run a full new environment (green), switch traffic at the LB|Instant switch and rollback|Double capacity during release|
|Canary|Send 1% → 5% → 25% → 100% of traffic to the new version, watch metrics|Limits blast radius|Needs good metrics and automation|
|Shadow / dark launch|Copy real traffic to the new version, discard its responses|Test with real load safely|Side effects must be disabled|
|Feature flags|Code ships off; turn features on per user/percentage at runtime|Decouple deploy from release, instant kill switch, A/B tests|Flag debt; test combinations|

### Database migrations
Use **expand–contract**: add the new column (expand), write to both, backfill, switch reads, remove the old column (contract). Each step is backward compatible.""",
  see=("monitoring",)),

C("config-multitenancy", "Configuration, multi-tenancy and data residency", "Advanced",
  "How SaaS systems isolate customers (tenants), keep configuration dynamic, and obey laws about where data lives.",
  """### Multi-tenancy models
|Model|Isolation|Cost|
|Shared DB, shared tables (`tenant_id` column)|Lowest (row-level security needed)|Cheapest, easiest to scale many small tenants|
|Shared DB, schema per tenant|Medium|Medium|
|Database / cluster per tenant (silo)|Highest; big enterprise customers|Most expensive|
Watch for **noisy neighbours**: per-tenant rate limits and quotas.

### Configuration
Central config service (Spring Cloud Config, Consul KV, AWS AppConfig) with dynamic reload; feature flags (LaunchDarkly, Unleash); never hard-code secrets.

### Data residency and compliance
- **GDPR** (EU): consent, right to access and erase, data minimisation; **DPDP Act** in India; data may need to stay in-region → geo-sharding.
- **PCI DSS** for card data: tokenise cards with the payment provider so raw card numbers never touch your servers.
- **HIPAA** for health data (US).""",
  see=("sharding",)),
]

RELIABILITY = [
C("redundancy-failover", "Redundancy, failover and multi-region design", "Intermediate",
  "Duplicate every critical component and switch automatically when one fails; for the highest availability run in several regions.",
  """### Levels of redundancy
1. Multiple instances per service (behind a load balancer).
2. Across **availability zones** (separate data centres in one region, ~1–2 ms apart): survive a building/power failure. Standard for production.
3. Across **regions** (Mumbai, Singapore, Frankfurt): survive a regional outage and serve users with lower latency.

### Failover modes
- **Active–passive**: standby takes over when the primary fails (cold, warm or hot standby). Simpler; some downtime and possible data loss with async replication.
- **Active–active**: all sites serve traffic. No idle capacity and instant failover, but writes in several places need conflict handling or partitioning of users by home region.

### Multi-region patterns
- Read local, write to a single home region (simple).
- **Geo-partition** users: each user's data lives in their home region (also helps residency laws).
- Globally replicated DBs: Spanner, CockroachDB, DynamoDB Global Tables (LWW conflicts), Cosmos DB.
- Route users with **GeoDNS / Anycast**; health checks shift traffic away from a failing region.""",
  diagram={"rows": [["x:GeoDNS"], ["Region Mumbai", "Region Singapore"], ["db:DB primary", "db:DB replica"]],
           "edges": [["GeoDNS", "Region Mumbai", "India users"], ["GeoDNS", "Region Singapore", "SEA users"], ["Region Mumbai", "DB primary"], ["Region Singapore", "DB replica"], ["DB primary", "DB replica", "async replication"]]}),

C("disaster-recovery", "Disaster recovery: RPO, RTO and backups", "Intermediate",
  "RPO = how much data you can afford to lose (time since last good copy). RTO = how long you can afford to be down. Backups and standby sites are chosen to meet both.",
  """|Strategy|RPO|RTO|Cost|
|Backup & restore (nightly snapshots to S3)|Hours–a day|Hours|Lowest|
|Pilot light (DB replicated, minimal app servers off)|Minutes|Tens of minutes|Low|
|Warm standby (scaled-down copy running)|Seconds–minutes|Minutes|Medium|
|Multi-site active–active|~0|~0 (seconds)|Highest|

### Backup rules
- **3-2-1**: 3 copies, 2 different media, 1 off-site. Keep immutable copies against ransomware.
- Point-in-time recovery from continuous WAL archiving (RDS keeps up to 35 days).
- **Test restores regularly** — an untested backup isn't a backup.
- Protect against human error (accidental `DROP TABLE`) with delayed replicas and soft deletes.""",
  see=("redundancy-failover",)),

C("monitoring", "Observability: metrics, logs, traces and alerting", "Intermediate",
  "You can't run what you can't see. Metrics show trends, logs explain individual events, traces follow one request across services.",
  """### The three pillars
- **Metrics**: numbers over time (QPS, error rate, latency p99, CPU, queue lag). Cheap to store, great for dashboards and alerts. Prometheus + Grafana, Datadog, CloudWatch.
- **Logs**: structured (JSON) events with a **request ID**. Centralised in ELK/OpenSearch, Splunk, Loki. Expensive at volume → sample debug logs.
- **Traces**: a trace ID passed through every service call; each hop records a span with timing. Shows where the 2 seconds went. OpenTelemetry, Jaeger, Zipkin, AWS X-Ray.

### What to measure
- **Golden signals** (Google SRE): latency, traffic, errors, saturation.
- **RED** for services: Rate, Errors, Duration. **USE** for resources: Utilisation, Saturation, Errors.
- Business metrics: orders/minute, sign-ups, payment success rate.

### Alerting
Alert on **symptoms users feel** (error rate, latency SLO burn rate), not every CPU spike. Every alert must be actionable, with a runbook; on-call rotations; blameless post-mortems.""",
  see=("metrics-hld",)),

C("autoscaling", "Autoscaling and capacity planning", "Intermediate",
  "Add or remove servers automatically based on load, and plan enough headroom for peaks and failures.",
  """- **Reactive autoscaling**: scale on CPU %, request rate, queue depth or custom metrics (AWS ASG, Kubernetes HPA). Has a lag of minutes, so keep headroom.
- **Scheduled scaling**: scale up before known peaks (9 am, IPL final, Big Billion Days sale).
- **Predictive scaling**: ML forecasts from history.
- Scale-in gently (cool-down periods) to avoid flapping; drain connections first.
- Databases scale much slower than stateless app servers — plan them ahead.
- **N+1 / N+2 capacity**: survive losing one AZ at peak (e.g. 3 AZs each able to carry 50% of peak).
- Pre-warm caches and load balancers before big events; load-test at 2–3× expected peak.""",
  see=("serverless-containers", "estimation")),

C("chaos-engineering", "Chaos engineering and game days", "Advanced",
  "Deliberately break things in a controlled way (kill servers, add latency, cut a region) to prove the system survives before a real outage does it for you.",
  """- Netflix **Chaos Monkey** randomly kills production instances; **Chaos Kong** evacuates a whole region.
- Start in staging, then small production experiments with a clear hypothesis ('if one Redis node dies, p99 stays < 200 ms') and an abort button.
- Tools: Gremlin, AWS Fault Injection Simulator, Chaos Mesh, Litmus.
- **Game days**: teams practise incident response on simulated failures.""",
  see=("resilience-patterns",)),

C("cost", "Cost awareness in design", "Intermediate",
  "Senior engineers design for cost too: storage tiers, caching, right-sizing, and avoiding expensive cross-region traffic.",
  """- **Egress (data out) and cross-region traffic** are often the surprise bill; keep chatty services in one AZ/region and use CDNs.
- Tier storage: hot (SSD, Redis) → warm (S3 Standard) → cold (S3 Glacier). Lifecycle policies.
- Compress and batch; use columnar formats (Parquet) for analytics.
- Reserved instances/savings plans for steady load, **spot instances** for batch jobs.
- Delete what you don't need: log retention, old snapshots, unused indexes.
- Estimate cost alongside capacity in interviews when relevant ('45 TB/year on S3 ≈ ₹1 lakh/month').""",
  see=("estimation",)),
]

SECURITY = [
C("authn-authz", "Authentication vs authorization", "Basic",
  "Authentication = who are you? (login). Authorization = what are you allowed to do? (permissions).",
  """### Authentication methods
Passwords (+ **MFA**: OTP, authenticator app, passkeys/WebAuthn), social login (OAuth/OIDC), SSO in companies (SAML/OIDC), API keys for machines, mTLS for services.

### Authorization models
- **RBAC** (role-based): admin, editor, viewer roles with permissions.
- **ABAC** (attribute-based): rules on attributes ('managers can approve expenses under ₹1 lakh in their department').
- **ReBAC** (relationship-based, Google Zanzibar): 'can user U view doc D?' answered from a graph of relationships (owner, shared-with, folder parent). Used by Google Drive, and open-source SpiceDB/OpenFGA.
- Enforce authorization **on the server for every request**; never trust the client.

### Storing passwords
Never store plain or simply hashed (SHA-256) passwords. Use a slow, salted hash: **bcrypt, scrypt or Argon2**. Rate-limit login attempts; lock or add CAPTCHA after failures.""",
  see=("sessions-jwt", "oauth")),

C("sessions-jwt", "Sessions vs tokens (JWT)", "Intermediate",
  "After login the server must remember you: either a session ID that points to server-side data, or a signed token (JWT) that carries the data itself.",
  """|Server-side session|JWT (stateless token)|
|Cookie holds a random session ID; data in Redis/DB|Token holds claims (`userId`, `roles`, `exp`) signed by the server|
|Easy to revoke (delete the session)|Hard to revoke before expiry (need a deny-list or short expiry)|
|Every request needs a session store lookup|Any service can verify the signature locally, no lookup|
|Best for classic web apps|Best for APIs, mobile, microservices|

### Good JWT practice
- Short-lived **access token** (5–15 min) + long-lived **refresh token** (stored securely, rotated, revocable).
- Sign with RS256/ES256 (public key verification across services); never put secrets in the payload — it's only base64, not encrypted.
- Store in `HttpOnly; Secure; SameSite` cookies (protects from XSS) or secure storage on mobile.

```java
header.payload.signature
{"alg":"RS256"} . {"sub":"42","roles":["user"],"exp":1795200000} . <signature>
```""",
  see=("oauth",)),

C("oauth", "OAuth 2.0, OpenID Connect and SSO", "Intermediate",
  "OAuth 2.0 lets an app act on your behalf at another service without your password ('Allow this app to read your Google Calendar'). OpenID Connect adds login (an ID token) on top. SSO lets one login work across many apps.",
  """### Authorization Code flow with PKCE (the standard for web and mobile)
1. App redirects you to the **authorization server** (Google) with the requested scopes and a PKCE code challenge.
2. You log in and consent.
3. Google redirects back with a short-lived **authorization code**.
4. The app exchanges the code (+ PKCE verifier) for an **access token** (and refresh token) on a back channel.
5. The app calls the **resource server** (Calendar API) with the access token.

### Other grant types
**Client credentials** (service-to-service, no user), **device code** (smart TVs). The implicit and password grants are deprecated.

### OpenID Connect (OIDC)
Adds an **ID token** (a JWT about who logged in) and a `/userinfo` endpoint → 'Sign in with Google'.

### SSO in companies
One identity provider (Okta, Azure AD/Entra ID, Google Workspace) via **SAML** or **OIDC**; employees log in once for all apps.""",
  diagram={"seq": ["User", "App", "Auth server", "API"], "msgs": [["User", "App", "click 'Sign in with Google'"], ["App", "Auth server", "redirect (scopes, PKCE)"], ["User", "Auth server", "login + consent"], ["Auth server", "App", "auth code (redirect)"], ["App", "Auth server", "code + verifier"], ["Auth server", "App", "access + ID token"], ["App", "API", "Bearer access token"]]}),

C("encryption", "Encryption at rest and in transit, hashing, key management", "Intermediate",
  "In transit = TLS on every network hop. At rest = encrypted disks/databases/objects. Keys live in a key management service, never in code.",
  """- **Symmetric** (AES-256): one key encrypts and decrypts; fast; used for data.
- **Asymmetric** (RSA, ECC): public/private keys; used for key exchange, signatures, certificates.
- **Hashing** (SHA-256): one-way fingerprint for integrity and checksums; for passwords use bcrypt/Argon2.
- **Envelope encryption**: data encrypted with a data key; the data key is encrypted with a master key in **KMS** (AWS KMS, GCP KMS, HashiCorp Vault). Rotating the master key doesn't require re-encrypting all data.
- **Secrets management**: DB passwords and API keys in Vault/Secrets Manager, injected at runtime, rotated automatically.
- **End-to-end encryption** (WhatsApp, Signal protocol): only the two devices have the keys; the server can't read messages.
- **Tokenisation**: replace sensitive data (card number) with a random token; the real value lives in a secure vault.""",
  see=("tls",)),

C("web-security", "Web and API security: OWASP basics, DDoS, WAF, CORS", "Intermediate",
  "The common attacks every design should defend against, and where the defences sit.",
  """|Attack|What it is|Defence|
|SQL injection|User input becomes SQL|Prepared statements / parameterised queries, ORM|
|XSS|Attacker's script runs in other users' browsers|Escape output, Content-Security-Policy, HttpOnly cookies|
|CSRF|A malicious site makes your browser send authenticated requests|SameSite cookies, CSRF tokens|
|Broken access control / IDOR|`GET /invoices/124` returns someone else's invoice|Check ownership on every request|
|SSRF|Server tricked into calling internal URLs|Allow-list outbound hosts, block metadata IPs|
|Credential stuffing / brute force|Leaked passwords tried at scale|Rate limits, MFA, breached-password checks, CAPTCHA|
|DDoS|Flood of traffic|CDN/Anycast absorption (Cloudflare, AWS Shield), rate limiting, autoscaling, WAF rules|

### Defence in depth
WAF at the edge → API gateway (auth, rate limits) → services validate input → least-privilege IAM → private subnets for DBs → encryption → audit logs.

### CORS
Browsers block JavaScript from calling another origin unless the server returns `Access-Control-Allow-Origin` for that origin. It's a browser protection, not server security.

### Zero trust
Don't trust the internal network either: authenticate and authorise every service call (mTLS, short-lived credentials).""",
  see=("rate-limiting",)),
]
