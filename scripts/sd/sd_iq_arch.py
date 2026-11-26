"""Theory interview questions: Architecture, Reliability & Security tab."""
from sd_iq_util import Q

Q("monolith-microservices",
  ("B", "Monolith vs microservices?", "A monolith is one deployable with all features and usually one database. Microservices split the system into independently deployable services, each owning its data, communicating over the network."),
  ("I", "What are the benefits of microservices?", "Independent deploys and scaling, team autonomy, technology choice per service, fault isolation, smaller codebases."),
  ("I", "What are the costs of microservices?", "Network latency and partial failure, distributed transactions and eventual consistency, harder debugging (needs tracing), more infrastructure (service discovery, CI/CD, monitoring), and data duplication."),
  ("I", "What is a modular monolith?", "One deployable with strictly separated modules and internal APIs; gets most organisational benefits without distributed-system costs, and modules can be extracted later."),
  ("I", "How do you decide service boundaries?", "Along business capabilities/bounded contexts (DDD), minimising chatty calls and shared data, aligned with team ownership."),
  ("A", "Why is a shared database between microservices an anti-pattern?", "It couples services through schema changes and hidden dependencies, prevents independent scaling/deploys and turns into a distributed monolith."),
  ("A", "How would you migrate a monolith to microservices?", "Strangler fig: put a facade/router in front, extract one capability at a time behind it, replicate data via CDC/events, cut over routes gradually, and delete the old code."))

Q("service-discovery",
  ("B", "What is service discovery?", "How services find the network locations of other services' healthy instances when instances come and go dynamically."),
  ("I", "Client-side vs server-side discovery?", "Client-side: the client queries a registry and picks an instance (Eureka + Ribbon). Server-side: the client calls a load balancer/DNS name that routes to instances (Kubernetes Services, AWS ALB)."),
  ("I", "How does Kubernetes do service discovery?", "Each Service gets a stable DNS name and virtual IP; kube-proxy (or eBPF) routes to healthy pod endpoints maintained by the control plane."),
  ("A", "What happens if the registry is down?", "Clients should cache the last known instance list and keep working; the registry itself should be replicated (Consul/etcd clusters)."),
  ("A", "Self-registration vs third-party registration?", "Self: instances register and heartbeat themselves. Third-party: the platform (orchestrator) registers instances, so services need no registry code."))

Q("service-mesh",
  ("B", "What is a service mesh?", "An infrastructure layer of sidecar proxies (data plane) and a control plane that handles service-to-service traffic: mTLS, retries, timeouts, routing, observability."),
  ("I", "Why use a mesh instead of client libraries?", "Language-agnostic, consistent policies across all services, centrally managed, without changing application code."),
  ("I", "What does the control plane do vs the data plane?", "Control plane: distributes config, certificates and policies (Istiod). Data plane: proxies (Envoy) that actually carry and act on the traffic."),
  ("A", "What are the downsides of a service mesh?", "Extra latency per hop, resource overhead per pod, operational complexity, and debugging another layer. Not worth it for a handful of services."),
  ("A", "How does a mesh enable canary releases?", "Traffic-splitting rules route a percentage of requests (or matching headers) to a new version, adjusted without redeploying clients."))

Q("bff",
  ("B", "What is the Backend for Frontend pattern?", "A dedicated backend per client type (mobile, web, TV) that aggregates and shapes data from downstream services for that UI."),
  ("I", "What problems does a BFF solve?", "Too many client round trips, over-fetching for small screens, and one general API becoming a compromise for every client."),
  ("I", "BFF vs API gateway?", "The gateway handles cross-cutting concerns for all traffic; a BFF contains client-specific composition logic, usually owned by the frontend team."),
  ("A", "What are the risks of BFFs?", "Duplicated logic across BFFs, more services to run, and BFFs becoming mini-monoliths if business logic leaks into them."),
  ("A", "Is GraphQL an alternative to BFFs?", "Often: a GraphQL layer lets each client request exactly what it needs from one endpoint, reducing the need for per-client BFFs."))

Q("event-driven",
  ("B", "What is event-driven architecture?", "Services communicate by publishing events about things that happened; interested services subscribe and react, instead of calling each other directly."),
  ("I", "Benefits and drawbacks of event-driven systems?", "Benefits: loose coupling, easy to add consumers, resilience to consumer outages, natural audit log. Drawbacks: eventual consistency, harder debugging and flow visibility, duplicate/out-of-order handling."),
  ("I", "Choreography vs orchestration?", "Choreography: services react to each other's events with no central controller. Orchestration: a coordinator tells each service what to do next and tracks state (Temporal, Step Functions)."),
  ("I", "Event notification vs event-carried state transfer?", "Notification carries only an id; consumers call back for data. State transfer carries the data so consumers don't need to call back, at the cost of larger events and duplication."),
  ("A", "How do you version events?", "Schema registry with compatibility rules, additive changes only, explicit version fields, upcasters for old events, and running old and new consumers during migration."),
  ("A", "How do you debug a flow across many event-driven services?", "Correlation/trace ids propagated in event headers, distributed tracing, event catalogues, and replayable logs."))

Q("event-sourcing",
  ("B", "What is event sourcing?", "Storing every state change as an immutable event and deriving current state by replaying events, instead of storing only the latest state."),
  ("I", "What are the benefits of event sourcing?", "Complete audit history, time travel/debugging, rebuilding new read models from history, and natural integration with event-driven systems."),
  ("I", "What are snapshots and why are they needed?", "Periodically saving the computed state so rebuilding doesn't replay all events from the beginning."),
  ("A", "What are the challenges of event sourcing?", "Event schema evolution, eventual consistency of projections, querying current state requires projections, GDPR deletion of personal data in immutable logs, and higher complexity."),
  ("A", "How do you handle concurrent commands on the same aggregate?", "Optimistic concurrency: append only if the stream's expected version matches; otherwise reload and retry."))

Q("cqrs",
  ("B", "What is CQRS?", "Command Query Responsibility Segregation: separate models (and often stores) for writes (commands) and reads (queries)."),
  ("I", "When is CQRS useful?", "When read and write workloads differ greatly in shape or scale, when you need multiple specialised read views (search, dashboards, feeds), or with event sourcing."),
  ("I", "How are read models kept up to date?", "By projecting events or CDC from the write side, asynchronously and idempotently."),
  ("A", "How do you handle the lag between write and read models in the UI?", "Return the result of the command directly, apply optimistic UI updates, read your own writes from the write model briefly, or wait for the projection version."),
  ("A", "When is CQRS overkill?", "Simple CRUD apps, small teams, or when strong read-after-write consistency is needed everywhere."))

Q("serverless-containers",
  ("B", "What is serverless computing?", "Running code without managing servers: the platform runs functions per event/request, scales automatically (to zero), and bills per invocation and duration."),
  ("I", "Containers vs VMs?", "VMs virtualise hardware with a full OS each (strong isolation, heavier). Containers share the host kernel and package the app and its dependencies (lightweight, fast start)."),
  ("I", "What is a cold start?", "Latency when a serverless platform must create a new execution environment (load runtime, code, init) before handling a request; mitigated with provisioned concurrency, smaller packages, lighter runtimes."),
  ("I", "When is serverless a good fit?", "Spiky or low-traffic workloads, event-driven glue (S3 triggers, queues), scheduled jobs, prototypes. Less suited to long-running, latency-critical or steady high-throughput services."),
  ("A", "What problems arise connecting serverless functions to a relational DB?", "Many concurrent functions open many connections, exhausting the DB; use a connection proxy (RDS Proxy), HTTP data APIs, or serverless databases."),
  ("A", "What does Kubernetes provide on top of containers?", "Scheduling, self-healing, service discovery, rolling deploys, autoscaling, config/secret management, and declarative desired-state management."))

Q("resilience-patterns",
  ("B", "Why must every remote call have a timeout?", "Without one, a slow dependency holds threads/connections indefinitely, exhausting resources and causing cascading failure."),
  ("I", "Explain the circuit breaker pattern.", "Closed: calls pass; failures counted. Open (after threshold): calls fail fast without hitting the dependency. Half-open (after cool-down): a few trial calls decide whether to close or reopen."),
  ("I", "What is the bulkhead pattern?", "Isolating resources (thread pools, connection pools) per dependency or feature so one failing dependency can't consume all resources."),
  ("I", "Why add jitter to retries?", "Without jitter, many clients retry in lockstep, creating synchronized load spikes; randomising waits spreads them out."),
  ("I", "When should you NOT retry?", "On non-idempotent operations without idempotency keys, on client errors (4xx), when the deadline is already exceeded, or when the dependency is overloaded (breaker open)."),
  ("A", "What is a retry budget?", "Limit retries to a percentage of normal traffic (e.g., 10%) so retries can't multiply load during an outage."),
  ("A", "How do you implement graceful degradation for a product page?", "Identify critical vs optional components; give optional ones short timeouts and fallbacks (cached recommendations, hide reviews); keep checkout and price paths protected."))

Q("idempotency",
  ("B", "What does idempotent mean?", "Performing an operation multiple times has the same effect as performing it once."),
  ("I", "Why is idempotency essential in distributed systems?", "Retries after timeouts and at-least-once message delivery cause duplicates; idempotent operations make duplicates harmless."),
  ("I", "How do idempotency keys work?", "The client sends a unique key per logical operation; the server stores the key with the result; repeats with the same key return the stored result without re-executing."),
  ("I", "What should happen if a retry with the same key arrives while the first is still processing?", "Return 409/'in progress' or wait for the first to finish and return its result; never run both."),
  ("A", "What if the same key is reused with a different request body?", "Reject it (e.g., 422) because it's a client bug; store a hash of the request with the key to detect it."),
  ("A", "How long should idempotency keys be kept?", "At least as long as clients may retry (often 24 hours to several days), then expire them to bound storage."))

Q("deployments",
  ("B", "Rolling vs blue-green vs canary deployments?", "Rolling replaces instances gradually. Blue-green runs a full new environment and flips traffic at once (instant rollback). Canary sends a small percentage of traffic to the new version and increases it while monitoring."),
  ("I", "What are feature flags and why use them?", "Runtime switches to enable code paths for some users; decouple deploy from release, enable gradual rollout, A/B tests and kill switches."),
  ("I", "How do you deploy database schema changes safely?", "Expand–migrate–contract: add backward-compatible changes first, deploy code that writes both, backfill, switch reads, then remove old columns in a later release."),
  ("I", "What metrics decide whether a canary is healthy?", "Error rate, latency percentiles, saturation, and business metrics (checkout success) compared against the baseline version."),
  ("A", "What is a dark launch / shadow traffic?", "Sending a copy of real production traffic to a new version whose responses are discarded, to test performance and correctness without user impact."),
  ("A", "How do you roll back when a release included a data migration?", "Design migrations to be backward compatible so old code still works; roll back code first; keep data changes reversible or forward-fix."))

Q("config-multitenancy",
  ("B", "What is multi-tenancy?", "One system instance serving many customers (tenants) with logically isolated data and configuration."),
  ("I", "Compare shared tables, schema per tenant and database per tenant.", "Shared tables: cheapest, weakest isolation, needs tenant_id everywhere. Schema per tenant: medium. Database per tenant: strong isolation and per-tenant backup, highest cost and operational load."),
  ("I", "What is the noisy neighbour problem?", "One tenant's heavy usage degrades others on shared resources; mitigate with per-tenant quotas, rate limits, isolation pools and moving big tenants to dedicated resources."),
  ("I", "How do you prevent one tenant from seeing another's data?", "Tenant context on every request, enforced at the data layer (row-level security, scoped repositories), tests for isolation, and audits."),
  ("A", "How should configuration and secrets be managed?", "Externalised config service with versioning and safe rollout, feature flags, and secrets in a vault/KMS with rotation; never in code or images."))

Q("redundancy-failover",
  ("B", "What is redundancy?", "Having duplicate components so the system survives when one fails."),
  ("I", "Active–passive vs active–active?", "Active–passive: a standby takes over on failure (simpler, wastes idle capacity, failover delay). Active–active: all copies serve traffic (better utilisation, instant failover, harder consistency)."),
  ("I", "What determines failover time?", "Failure detection (health check interval × threshold), promotion/election, DNS/VIP/connection updates, and client reconnects."),
  ("A", "How do you avoid split brain during failover?", "Quorum-based decisions, fencing (STONITH or fencing tokens), and witness nodes in a third zone."),
  ("A", "Why should you test failover regularly?", "Untested failover often fails (stale configs, missing capacity, data lag); game days and chaos tests validate it."))

Q("disaster-recovery",
  ("B", "What are RPO and RTO?", "RPO: maximum acceptable data loss (time). RTO: maximum acceptable downtime to restore service."),
  ("I", "Describe DR strategies from cheapest to fastest.", "Backup & restore, pilot light, warm standby, multi-site active–active; each lowers RPO/RTO at higher cost."),
  ("I", "Backups vs replication?", "Replication protects against hardware/zone failures but copies mistakes (deletes, corruption) instantly. Backups (point-in-time, immutable) protect against those logical errors."),
  ("A", "How do you protect backups from ransomware?", "Immutable/WORM storage, separate accounts and credentials, offsite copies, and regular restore tests."),
  ("A", "What must a DR plan include besides data?", "Infrastructure as code, DNS/traffic switching, secrets, runbooks, dependency availability in the DR region, and regular drills."))

Q("monitoring",
  ("B", "What are the three pillars of observability?", "Metrics (numbers over time), logs (discrete events), traces (a request's path across services)."),
  ("I", "What are the golden signals?", "Latency, traffic, errors and saturation."),
  ("I", "RED vs USE methods?", "RED (Rate, Errors, Duration) for request-driven services; USE (Utilisation, Saturation, Errors) for resources like CPU, disks, queues."),
  ("I", "Why alert on symptoms rather than causes?", "Users feel symptoms (errors, latency); cause-based alerts (high CPU) are noisy and may not matter. Use cause metrics for diagnosis."),
  ("I", "What is distributed tracing and how is context propagated?", "Each request gets a trace id; each hop creates spans with parent ids, propagated in headers (W3C traceparent), so you can see where time was spent."),
  ("A", "What is SLO burn-rate alerting?", "Alert when the error budget is being consumed much faster than sustainable over multiple windows (e.g., 14× over 1 h and 5 min), reducing noise and catching real incidents fast."),
  ("A", "How do you control the cost of observability at scale?", "Sampling traces (tail-based), log levels and retention tiers, metric cardinality limits, and aggregating before storing."))

Q("autoscaling",
  ("B", "What is autoscaling?", "Automatically adding or removing instances based on load metrics or schedules."),
  ("I", "Which metrics should drive scaling?", "CPU/memory for compute-bound services, requests/concurrency for web tiers, and queue lag/depth for workers (often the best leading indicator)."),
  ("I", "Why scale up fast and down slowly?", "Scaling up late causes outages; scaling down too eagerly causes flapping and cold capacity when load returns."),
  ("A", "What can go wrong with autoscaling?", "New instances take minutes to warm up, downstream DBs get overwhelmed by more app servers, flapping, hitting account quotas, and scaling on misleading metrics."),
  ("A", "What is predictive scaling?", "Forecasting load from historical patterns and adding capacity before the expected peak."))

Q("chaos-engineering",
  ("B", "What is chaos engineering?", "Deliberately injecting failures in controlled experiments to verify the system withstands them and to find weaknesses before real incidents do."),
  ("I", "How do you run a chaos experiment?", "Define steady state, hypothesise it will hold under a fault, inject the fault with a small blast radius, observe, abort if needed, then fix and expand."),
  ("I", "Examples of faults to inject?", "Killing instances, adding latency, dropping network, failing a zone, exhausting CPU/disk, breaking DNS or certificates."),
  ("I", "What is a game day?", "A planned exercise where teams simulate a real incident (region loss, dependency outage) to practise response, validate runbooks and test failover end to end."),
  ("A", "How do you do chaos safely in production?", "Start in staging, limit blast radius (small % or one cell), automatic abort conditions, run during business hours with owners present, and have rollback ready."))

Q("cost",
  ("B", "Why should system designs consider cost?", "Architectures can be technically fine but too expensive; cost is a real constraint and trade-off (e.g., cross-region replication, egress)."),
  ("I", "What are the biggest cost drivers in cloud systems?", "Compute, storage, network egress (often underestimated), managed services, and data transfer between zones/regions."),
  ("I", "How do you reduce storage cost?", "Lifecycle tiers (hot → infrequent → archive), compression, deduplication, deleting unused data, and right-sizing replication."),
  ("A", "Reserved/committed vs on-demand vs spot capacity?", "Commitments discount steady baseline usage; on-demand for variable load; spot (up to ~70–90% cheaper) for interruptible batch work."),
  ("A", "How do you attribute cost per feature or tenant?", "Tagging resources, metering usage per tenant/request, and unit-economics metrics like cost per 1,000 requests or per active user."))

Q("authn-authz",
  ("B", "Authentication vs authorization?", "Authentication verifies who you are; authorization decides what you're allowed to do."),
  ("I", "RBAC vs ABAC vs ReBAC?", "RBAC: permissions via roles. ABAC: rules over attributes of user, resource and context. ReBAC: permissions from relationships (owner, shared via folder/group), like Google Zanzibar."),
  ("I", "Where should authorization checks happen?", "At the gateway for coarse checks and inside each service for resource-level checks; never only in the UI."),
  ("I", "What is broken object level authorization?", "An API that returns or modifies a resource by id without checking the caller owns/has access to it (GET /invoices/124 shows someone else's invoice)."),
  ("A", "How would you design permissions like Google Drive sharing?", "Store relation tuples (doc#viewer@user, folder#parent, group#member) and evaluate by graph traversal with caching (Zanzibar/OpenFGA)."),
  ("A", "How do you secure service-to-service calls?", "mTLS identities, short-lived service tokens (JWT/SPIFFE), least-privilege policies, and network segmentation."))

Q("sessions-jwt",
  ("B", "Server sessions vs JWT?", "Sessions: a random id in a cookie maps to server-side state (easy revocation, needs a shared store). JWT: a signed self-contained token verified without a lookup (scales easily, hard to revoke)."),
  ("I", "What is inside a JWT?", "Header (algorithm), payload (claims: sub, exp, iat, aud, roles), and signature over both; it's encoded, not encrypted."),
  ("I", "How do you revoke JWTs?", "Short expiry access tokens + refresh tokens stored server-side (revocable), a deny-list of token ids, or rotating signing keys."),
  ("I", "Where should a browser store tokens?", "Prefer HttpOnly, Secure, SameSite cookies (not readable by JS, mitigating XSS theft) over localStorage."),
  ("A", "What is refresh token rotation?", "Each refresh issues a new refresh token and invalidates the old; reuse of an old one signals theft and revokes the whole family."),
  ("A", "What are common JWT security mistakes?", "Accepting alg=none, mixing up symmetric/asymmetric keys, not checking exp/aud/iss, putting secrets in the payload, and long-lived tokens."))

Q("oauth",
  ("B", "What is OAuth 2.0?", "A delegated authorization framework letting an app access a user's resources at another service with limited scope, without getting the user's password."),
  ("B", "OAuth vs OpenID Connect?", "OAuth is authorization (access tokens for APIs); OIDC adds authentication: an ID token describing who the user is."),
  ("I", "Walk through the authorization code flow.", "App redirects user to the auth server → user logs in and consents → auth server redirects back with a one-time code → app exchanges code (+ secret or PKCE verifier) for tokens on the back channel."),
  ("I", "What is PKCE and why is it needed?", "Proof Key for Code Exchange: the app sends a hash of a random verifier at the start and the verifier at exchange, so a stolen code can't be redeemed; essential for mobile/SPA public clients."),
  ("I", "What are scopes?", "Named permissions requested by the app (read:email, photos.write) that limit what the access token can do."),
  ("A", "Which OAuth grant types should you avoid today?", "Implicit flow and resource owner password credentials; use authorization code + PKCE, and client credentials for machine-to-machine."),
  ("A", "What is the purpose of the 'state' parameter?", "A random value tied to the user's session to prevent CSRF/login injection in the redirect callback."))

Q("encryption",
  ("B", "Encryption in transit vs at rest?", "In transit protects data moving over networks (TLS). At rest protects stored data on disks, databases and backups (AES)."),
  ("B", "Hashing vs encryption?", "Hashing is one-way (integrity, passwords). Encryption is reversible with the key (confidentiality)."),
  ("I", "How should passwords be stored?", "With a slow, salted password hash (Argon2id, bcrypt, scrypt, PBKDF2), never encrypted or with fast hashes like SHA-256."),
  ("I", "What is envelope encryption?", "Encrypt data with a data key; encrypt the data key with a master key held in a KMS. Only encrypted data keys are stored; rotation re-wraps keys, not data."),
  ("A", "What is key rotation and how is it done without re-encrypting everything?", "Periodically creating new keys; with envelope encryption you re-encrypt only data keys with the new master key and keep old versions to decrypt existing data."),
  ("A", "What is end-to-end encryption and its trade-offs?", "Only endpoints hold keys, so servers can't read content (Signal, WhatsApp). Trade-offs: server can't search, moderate or recover data; multi-device key management is complex."))

Q("web-security",
  ("B", "What is SQL injection and how do you prevent it?", "Untrusted input concatenated into SQL changes the query's meaning. Prevent with parameterised queries/ORMs, least-privilege DB users and input validation."),
  ("I", "What is XSS and how do you prevent it?", "Injected scripts run in other users' browsers. Prevent with output encoding/escaping, Content-Security-Policy, HttpOnly cookies and sanitising rich HTML."),
  ("I", "What is CSRF and how do you prevent it?", "A malicious site causes a logged-in browser to send unwanted requests. Prevent with SameSite cookies, CSRF tokens and checking Origin headers."),
  ("I", "What is SSRF?", "Making a server fetch attacker-chosen URLs, reaching internal services or cloud metadata. Prevent with allow-lists, blocking private ranges after DNS resolution, and IMDSv2."),
  ("A", "How do you protect an API from DDoS?", "CDN/anycast absorption, WAF rules, rate limiting per IP/key, autoscaling, caching, and challenge pages for suspicious traffic."),
  ("A", "What is defence in depth?", "Multiple independent layers of security (edge, network, identity, application, data, monitoring) so one failure doesn't expose the system."))
