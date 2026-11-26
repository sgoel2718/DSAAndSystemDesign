"""Detailed explanations with diagrams: Architecture, Reliability & Security tab."""
from sd_x_util import X, P, H, AN, KEY, FLOW, SEQ, NOTE, ER, TABLE, CALC, BARS, CODE, UML, STATE, BA

X("monolith-microservices",
  BA(FLOW("Monolith: one deployable, one database", [["u:Clients"], ["Monolith app: users · orders · payments modules"], ["db:One shared DB"]],
       [["Clients", "Monolith app: users · orders · payments modules"], ["Monolith app: users · orders · payments modules", "One shared DB", "in-process calls, one transaction"]]),
  FLOW("Microservices: one service and one database per domain", [["u:Clients"], ["API gateway"], ["User svc", "Order svc", "Payment svc"], ["db:Users DB", "db:Orders DB", "db:Payments DB"]],
       [["Clients", "API gateway"], ["API gateway", "User svc"], ["API gateway", "Order svc"], ["API gateway", "Payment svc"], ["Order svc", "Payment svc", "network call"], ["User svc", "Users DB"], ["Order svc", "Orders DB"], ["Payment svc", "Payments DB"]]),
     "Before: one monolith", "After: split into services"),
  TABLE("Trade-offs", ["", "Monolith", "Microservices"], [["deploy", "one unit; simple", "independent per team"], ["scaling", "scale everything together", "scale hot services only"], ["calls", "in-process (ns)", "network (ms), can fail"],
                                                     ["data", "one DB, joins + transactions", "DB per service; sagas, eventual consistency"], ["debugging", "one stack trace", "distributed tracing needed"], ["best for", "small teams, new products", "many teams, clear domain boundaries"]]),
  KEY("Start with a **modular monolith** (strict module boundaries inside one app). Extract a service when a module needs independent scaling, deployment cadence, or team ownership.", "Practical path"))

X("service-discovery",
  SEQ("Client-side discovery with a registry", ["Order svc instance", "Registry (Consul / etcd / k8s)", "Payment svc 10.0.3.7", "Payment svc 10.0.3.9"],
      [["Payment svc 10.0.3.7", "Registry (Consul / etcd / k8s)", "register payment → 10.0.3.7 (+ health check)"], ["Payment svc 10.0.3.9", "Registry (Consul / etcd / k8s)", "register payment → 10.0.3.9"],
       ["Order svc instance", "Registry (Consul / etcd / k8s)", "where is 'payment'?"], ["Registry (Consul / etcd / k8s)", "Order svc instance", "[10.0.3.7, 10.0.3.9]", "r"], ["Order svc instance", "Payment svc 10.0.3.9", "POST /charge (client picks one)"],
       NOTE(["Registry (Consul / etcd / k8s)", "Payment svc 10.0.3.7"], ".7 fails health checks → removed; clients stop using it")]),
  TABLE("Client-side vs server-side discovery", ["", "Client-side", "Server-side"], [["who picks the instance", "calling service (library)", "a load balancer / proxy"], ["example", "Netflix Eureka + Ribbon", "Kubernetes Service (DNS name → kube-proxy), AWS ALB"], ["pro", "no extra hop", "clients stay simple, any language"]]))

X("service-mesh",
  FLOW("Sidecar proxies handle networking for every service", [["Control plane (Istio): config, certificates, policies"], ["Order svc ↔ Envoy sidecar", "Payment svc ↔ Envoy sidecar"]],
       [["Control plane (Istio): config, certificates, policies", "Order svc ↔ Envoy sidecar", "push config"], ["Control plane (Istio): config, certificates, policies", "Payment svc ↔ Envoy sidecar", "push config"], ["Order svc ↔ Envoy sidecar", "Payment svc ↔ Envoy sidecar", "mTLS, retries, metrics"]]),
  TABLE("What the mesh gives without code changes", ["Feature", "Example"], [["mTLS everywhere", "services authenticate each other with certificates"], ["traffic control", "send 5% of traffic to v2 (canary)"], ["resilience", "timeouts, retries, circuit breaking"], ["observability", "per-call latency, error rate, traces"], ["policy", "only Order may call Payment"]]),
  KEY("Cost: an extra proxy hop (~1 ms) and real operational complexity. Worth it with many services and teams; overkill for five services.", "Trade-off"))

X("bff",
  BA(SEQ("Phone calls every service itself", ["Mobile app", "User svc", "Catalog svc", "Recs svc"],
          [["Mobile app", "User svc", "GET /users/42 (40 fields, needs 3)"], ["Mobile app", "Catalog svc", "GET /catalog?home"], ["Mobile app", "Recs svc", "GET /recs/42", "", "3 round trips on a slow mobile network, over-fetched payloads, and the app breaks whenever a service API changes."]]),
       FLOW("One backend per frontend", [["u:Mobile app", "u:Web app", "u:Smart TV"], ["Mobile BFF", "Web BFF", "TV BFF"], ["User svc", "Catalog svc", "Recommendation svc"]],
       [["Mobile app", "Mobile BFF"], ["Web app", "Web BFF"], ["Smart TV", "TV BFF"], ["Mobile BFF", "User svc"], ["Mobile BFF", "Catalog svc"], ["Web BFF", "Catalog svc"], ["Web BFF", "Recommendation svc"], ["TV BFF", "Recommendation svc"]]),
     "Before: client talks to every service", "After: backend for frontend"),
  TABLE("Why", ["Problem without BFF", "BFF fix"], [["mobile makes 6 calls on a slow network", "BFF aggregates into 1 response"], ["web needs 40 fields, mobile 8", "each BFF shapes its own payload"], ["one generic API changes break every client", "each frontend team owns its BFF"]]))

X("event-driven",
  BA(SEQ("Order service calls everyone synchronously", ["Order svc", "Payment svc", "Email svc", "Analytics"],
          [["Order svc", "Payment svc", "charge (200 ms)"], ["Order svc", "Email svc", "send receipt (300 ms)"], ["Order svc", "Analytics", "track (down! ✘)", "", "Checkout is slow (sum of all calls), fails if any one service is down, and every new consumer means editing order svc."]]),
       SEQ("Order placed: services react to an event instead of being called", ["Order svc", "Event bus (Kafka)", "Payment svc", "Email svc", "Analytics"],
      [["Order svc", "Event bus (Kafka)", "publish OrderPlaced {id: 987}"], ["Event bus (Kafka)", "Payment svc", "OrderPlaced", "a"], ["Event bus (Kafka)", "Email svc", "OrderPlaced", "a"], ["Event bus (Kafka)", "Analytics", "OrderPlaced", "a", "Order svc doesn't know or wait for consumers; adding a new consumer needs no change to it."],
       ["Payment svc", "Event bus (Kafka)", "publish PaymentSucceeded"]]),
     "Before: tight synchronous coupling", "After: event-driven"),
  TABLE("Choreography vs orchestration", ["", "Choreography (events)", "Orchestration (central coordinator)"], [["control", "each service reacts", "orchestrator tells each step"], ["coupling", "loose", "tighter to orchestrator"], ["visibility", "flow is implicit (hard to trace)", "flow is explicit in one place"], ["tools", "Kafka, SNS/SQS", "Temporal, Step Functions, Camunda"]]),
  TABLE("Event types", ["Type", "Contains", "Example"], [["notification", "id only; consumer calls back", "OrderPlaced {id}"], ["event-carried state transfer", "full data", "OrderPlaced {id, items, total}"], ["domain event (sourcing)", "the change itself", "ItemAdded {sku, qty}"]]))

X("event-sourcing",
  P("Instead of storing current state, store the **sequence of events**; current state is a fold (replay) over them. A bank account:"),
  TABLE("Event log for account 42", ["#", "Event", "Balance after replay"], [["1", "AccountOpened", "0"], ["2", "Deposited 1000", "1000"], ["3", "Withdrew 300", "700"], ["4", "Deposited 50", "750"], ["5", "Withdrew 200", "550"]],
        "Current balance = 550, computed by replaying. A snapshot every N events avoids replaying from the beginning."),
  TABLE("Pros and cons", ["Pros", "Cons"], [["complete audit history (finance, compliance)", "querying current state needs projections"], ["time travel: state at any past moment", "event schema evolution is hard"], ["rebuild new read models by replaying", "eventual consistency of projections"], ["natural fit with CQRS + Kafka", "more moving parts"]]))

X("cqrs",
  FLOW("Separate write model and read models", [["u:Client"], ["Command side (validates, writes)", "Query side (reads only)"], ["db:Write DB (normalised)", "db:Read views (denormalised)"], ["q:Events / CDC"]],
       [["Client", "Command side (validates, writes)", "PlaceOrder"], ["Client", "Query side (reads only)", "GET my orders"], ["Command side (validates, writes)", "Write DB (normalised)"], ["Write DB (normalised)", "Events / CDC"], ["Events / CDC", "Read views (denormalised)", "project"], ["Query side (reads only)", "Read views (denormalised)"]]),
  TABLE("When it's worth it", ["Use CQRS when", "Skip it when"], [["reads and writes have very different shapes/scale (100:1)", "simple CRUD"], ["many read views (search, dashboards, feeds) of the same data", "you need read-after-write everywhere"], ["you already use events / event sourcing", "small team, small system"]]),
  KEY("The read side lags the write side by milliseconds–seconds. UI tricks: show the user's own change optimistically, or read from the write model right after a command.", "Consistency gap"))

X("serverless-containers",
  TABLE("VMs vs containers vs serverless", ["", "VMs", "Containers (Kubernetes)", "Serverless (Lambda)"], [["unit", "full OS", "process + filesystem image", "function"], ["start time", "minutes", "seconds", "ms–seconds (cold start)"],
        ["scaling", "slow, manual/ASG", "HPA, fast", "automatic per request, to zero"], ["billing", "per hour", "per node", "per invocation × duration"], ["limits", "none", "few", "time limits (15 min), statelessness, concurrency caps"],
        ["best for", "legacy, special OS needs", "long-running services", "spiky/event-driven work, glue code"]]),
  CALC("Cost crossover (illustrative)", [("Requests per month", "r = 100e6", ""), ("Serverless: $0.20 per million + compute ($0.0000167/GB-s, 0.2 s, 0.5 GB)", "r / 1e6 * 0.2 + r * 0.2 * 0.5 * 0.0000167", "$"),
                                         ("Two always-on small containers ($30 each)", "2 * 30", "$", "at steady high traffic, containers become cheaper")]))

X("resilience-patterns",
  BA(SEQ("No timeout, no breaker: cascading failure", ["Users", "Product page", "Recommendations (slow)"],
          [["Users", "Product page", "GET /product (1,000/s)"], ["Product page", "Recommendations (slow)", "call (hangs 30 s)"], NOTE(["Product page"], "all 200 threads stuck waiting"),
           ["Product page", "Users", "timeouts for EVERY page, even ones not needing recs ✘", "r", "One slow dependency takes down the whole service, then its callers."]]),
     SEQ("Timeout + circuit breaker + fallback", ["Users", "Product page", "Recommendations (slow)"],
          [["Users", "Product page", "GET /product"], ["Product page", "Recommendations (slow)", "call with 200 ms timeout"], ["Product page", "Product page", "3 failures → breaker OPEN"],
           ["Product page", "Users", "page with cached 'top sellers' instead ✔", "r", "Threads are freed in 200 ms; while OPEN no calls are made; after a cool-down one trial call tests recovery."]]),
     "Before: cascading failure", "After: resilience patterns"),
  STATE("Circuit breaker", [["[*]"], ["CLOSED"], ["OPEN"], ["HALF-OPEN"]],
        [["[*]", "CLOSED", ""], ["CLOSED", "OPEN", "failures > 50% in 10 s"], ["OPEN", "HALF-OPEN", "after 30 s cooldown"], ["HALF-OPEN", "CLOSED", "trial calls succeed"], ["HALF-OPEN", "OPEN", "trial call fails"], ["CLOSED", "CLOSED", "success"]]),
  TABLE("Retry with exponential backoff + jitter (base 100 ms, cap 5 s)", ["Attempt", "Backoff ceiling", "Actual wait (random 0..ceiling)"], [["1", "100 ms", "e.g. 63 ms"], ["2", "200 ms", "e.g. 151 ms"], ["3", "400 ms", "e.g. 298 ms"], ["4", "800 ms", "e.g. 512 ms"], ["5", "1.6 s", "give up → fallback"]],
        "Jitter spreads retries so thousands of clients don't retry in lockstep."),
  TABLE("The toolkit", ["Pattern", "Protects against", "Example"], [["Timeout", "waiting forever", "2 s on every remote call"], ["Retry + backoff", "transient errors", "only for idempotent calls"], ["Circuit breaker", "hammering a dead dependency", "fail fast, serve fallback"],
        ["Bulkhead", "one dependency using all threads", "separate pools per dependency"], ["Fallback / graceful degradation", "partial outage", "show cached recommendations"], ["Load shedding", "overload", "reject low-priority requests with 503"]]))

X("idempotency",
  BA(SEQ("Retry without a key", ["App", "Payment API"],
          [["App", "Payment API", "POST /charges ₹500"], ["Payment API", "Payment API", "charge card ✔"], ["Payment API", "App", "response lost (timeout)", "r"], ["App", "Payment API", "retry POST /charges ₹500"],
           ["Payment API", "App", "second charge ✘ customer pays ₹1,000", "r"]]),
       SEQ("Idempotency key prevents a double charge", ["App", "Payment API", "Idempotency store"],
      [["App", "Payment API", "POST /charges ₹500, Idempotency-Key: k-81"], ["Payment API", "Idempotency store", "INSERT k-81 (status IN_PROGRESS)"], ["Payment API", "Payment API", "charge card…"], ["Payment API", "Idempotency store", "save k-81 → response {charge_id: ch_9}"],
       ["Payment API", "App", "response lost (timeout)", "r"], ["App", "Payment API", "retry: same body, Idempotency-Key: k-81"], ["Payment API", "Idempotency store", "k-81 exists → return saved response"],
       ["Payment API", "App", "200 {charge_id: ch_9} (no second charge)", "r"]]),
     "Before: retries double-charge", "After: idempotency key"),
  TABLE("Ways to make operations idempotent", ["Technique", "Example"], [["client-generated key", "Idempotency-Key header (Stripe)"], ["natural unique constraint", "UNIQUE(order_id) on payments"], ["absolute instead of relative updates", "SET status = 'PAID' vs balance = balance − 500"],
        ["conditional writes", "UPDATE … WHERE version = 7"], ["dedup table of processed message ids", "Kafka consumers"]]))

X("deployments",
  TABLE("Deployment strategies", ["Strategy", "How", "Rollback", "Cost / risk"], [["Recreate", "stop old, start new", "redeploy old", "downtime"], ["Rolling", "replace instances a few at a time", "roll back gradually", "mixed versions run together"],
        ["Blue-green", "full new env (green); switch the LB", "switch back instantly", "2× infrastructure briefly"], ["Canary", "1% → 10% → 50% → 100% while watching metrics", "route back to old", "needs good metrics"], ["Feature flags", "deploy dark, enable per user", "flip the flag", "flag debt"]]),
  BA(SEQ("Big-bang deploy to every server at once", ["Deploy pipeline", "All 50 servers", "Users"],
          [["Deploy pipeline", "All 50 servers", "replace v1 with v2 everywhere"], ["Users", "All 50 servers", "requests"], ["All 50 servers", "Users", "v2 bug → 100% of users see errors ✘", "r", "Rollback means another full deploy while everyone is affected."]]),
       SEQ("Canary release with automatic rollback", ["Deploy pipeline", "Load balancer / mesh", "v2 pods", "Monitoring"],
      [["Deploy pipeline", "v2 pods", "deploy v2 (2 pods)"], ["Deploy pipeline", "Load balancer / mesh", "send 5% of traffic to v2"], ["Monitoring", "Deploy pipeline", "compare v2 vs v1: errors 0.1% vs 0.1%, p99 210 vs 205 ms ✔", "r"],
       ["Deploy pipeline", "Load balancer / mesh", "25% → 50% → 100%"], NOTE(["Deploy pipeline", "Monitoring"], "if v2 error rate spikes at any stage → traffic back to v1 automatically")]),
     "Before: all at once", "After: canary"),
  KEY("Database changes must be backward compatible across versions: **expand → migrate → contract** (add the new column, write both, backfill, switch reads, drop the old column later).", "Schema changes"))

X("config-multitenancy",
  TABLE("Multi-tenancy models", ["Model", "Isolation", "Cost per tenant", "Example"], [["Shared DB, shared tables (tenant_id column)", "lowest (row-level security)", "lowest", "most SaaS (small customers)"],
        ["Shared DB, schema per tenant", "medium", "medium", "B2B with customisation"], ["Database per tenant", "high", "high", "enterprise / regulated customers"], ["Stack per tenant (silo)", "highest", "highest", "very large or government customers"]]),
  CODE("Row-level security in Postgres", """ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON invoices
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
-- every query now only sees the current tenant's rows""", "sql"),
  TABLE("Noisy neighbour & config", ["Concern", "Approach"], [["one tenant floods the system", "per-tenant rate limits and quotas"], ["config per tenant/env", "central config service (Consul, AppConfig), feature flags per tenant"], ["secrets", "secret manager (Vault, AWS Secrets Manager), never in code"]]))

X("redundancy-failover",
  BA(SEQ("Single database, no standby", ["App", "Database"],
          [["App", "Database", "writes"], NOTE(["Database"], "disk fails"), ["App", "Database", "write"], ["Database", "App", "connection refused ✘", "r", "Full outage until someone restores a backup: hours, and data since the last backup is lost."]]),
       SEQ("Active–passive database failover", ["App", "Primary DB", "Standby DB", "Failover manager"],
      [["Primary DB", "Standby DB", "stream WAL (sync or async)", "a"], ["Failover manager", "Primary DB", "health check"], NOTE(["Primary DB"], "primary dies"), ["Failover manager", "Primary DB", "no response × 3 (≈ 30 s)"],
       ["Failover manager", "Standby DB", "promote to primary"], ["Failover manager", "App", "update DNS / virtual IP to standby"], ["App", "Standby DB", "reconnect; writes resume", "", "Downtime ≈ detection + promotion + reconnection. Async replication may lose the last seconds of writes."]]),
     "Before: single point of failure", "After: standby + automatic failover"),
  TABLE("Active–passive vs active–active", ["", "Active–passive", "Active–active"], [["traffic", "one serves, one waits", "both serve"], ["failover", "seconds–minutes", "near-instant (just stop routing)"], ["utilisation", "standby idle", "both used"], ["hard part", "fast detection, avoiding split brain", "write conflicts, data sync"]]))

X("disaster-recovery",
  TABLE("RPO and RTO", ["Term", "Question", "Example"], [["RPO (recovery point objective)", "how much data can we lose?", "≤ 5 minutes of writes"], ["RTO (recovery time objective)", "how long can we be down?", "≤ 1 hour"]]),
  TABLE("DR strategies (cheapest → fastest)", ["Strategy", "What runs in the DR region", "RTO", "RPO", "Cost"],
        [["Backup & restore", "nothing; backups in another region", "hours–day", "hours", "$"], ["Pilot light", "data replicated; minimal core services off/small", "tens of minutes", "minutes", "$$"], ["Warm standby", "scaled-down full copy running", "minutes", "seconds–minutes", "$$$"],
         ["Multi-site active–active", "full capacity serving traffic", "~0", "~0", "$$$$"]]),
  KEY("A backup you haven't restored is a hope, not a backup. Run regular restore drills and region-failover game days, and keep backups immutable (ransomware).", "Test it"))

X("monitoring",
  TABLE("The three pillars", ["Pillar", "Answers", "Example", "Tools"], [["Metrics", "is something wrong? (numbers over time)", "p99 latency, error rate, CPU", "Prometheus, Datadog"], ["Logs", "what happened in this event?", "structured JSON with request_id", "ELK, Loki"],
        ["Traces", "where did the time go across services?", "a request's span tree", "OpenTelemetry, Jaeger"]]),
  BARS("One trace: GET /checkout (total 420 ms)", [("API gateway", 420, "420 ms"), ("Order svc", 390, "390 ms"), ("Inventory call", 60, "60 ms"), ("Payment call", 280, "280 ms ← bottleneck"), ("DB insert", 25, "25 ms")]),
  TABLE("What to alert on", ["Method", "Signals"], [["RED (services)", "Rate, Errors, Duration"], ["USE (resources)", "Utilisation, Saturation, Errors"], ["Golden signals (Google SRE)", "latency, traffic, errors, saturation"], ["SLO burn rate", "alert when the error budget is being consumed too fast"]]))

X("autoscaling",
  CALC("Horizontal Pod Autoscaler decision", [("Current replicas", "c = 4", ""), ("Current average CPU", "u = 90", "%"), ("Target CPU", "t = 60", "%"), ("Desired = ceil(current × current/target)", "math.ceil(c * u / t)", "replicas")]),
  TABLE("Scaling signals", ["Signal", "Good for", "Watch out"], [["CPU / memory", "compute-bound services", "lags for I/O-bound work"], ["requests per second / concurrency", "web tiers", "need per-pod capacity number"], ["queue lag / depth", "workers, consumers", "best leading indicator"], ["schedule", "known peaks (9 am, sales)", "manual upkeep"], ["predictive", "daily patterns", "needs history"]]),
  KEY("Scale-up must beat the spike: new instances take 30 s–minutes. Keep headroom, scale up fast and down slowly (cooldown), and make sure the database can take the extra app servers' connections.", "Pitfalls"))

X("chaos-engineering",
  FLOW("The chaos experiment loop", [["Define steady state (e.g. checkout success ≥ 99.5%)"], ["Hypothesis: 'losing one AZ won't affect it'"], ["Inject fault in a small blast radius"], ["Observe metrics; abort if steady state breaks"], ["Fix weaknesses; widen scope"]],
       [["Define steady state (e.g. checkout success ≥ 99.5%)", "Hypothesis: 'losing one AZ won't affect it'"], ["Hypothesis: 'losing one AZ won't affect it'", "Inject fault in a small blast radius"], ["Inject fault in a small blast radius", "Observe metrics; abort if steady state breaks"], ["Observe metrics; abort if steady state breaks", "Fix weaknesses; widen scope"]]),
  TABLE("Typical faults to inject", ["Fault", "Reveals"], [["kill instances (Chaos Monkey)", "missing redundancy, slow failover"], ["add 300 ms latency to a dependency", "missing timeouts, thread exhaustion"], ["drop a zone/region", "DR gaps"], ["fill disk / exhaust CPU", "alerting gaps"], ["expire certificates / DNS failure", "hidden single points of failure"]]))

X("cost",
  CALC("Back-of-envelope monthly cost (illustrative cloud prices)", [("App servers: 20 × $150", "20 * 150", "$"), ("Database primary + 2 replicas: 3 × $1,200", "3 * 1200", "$"), ("Object storage 200 TB × $23/TB", "200 * 23", "$"),
                                                                    ("CDN egress 500 TB × $20/TB", "500 * 20", "$", "egress is often the biggest line"), ("Total", "20 * 150 + 3 * 1200 + 200 * 23 + 500 * 20", "$")]),
  TABLE("Biggest levers", ["Lever", "Saving"], [["serve via CDN, compress, cache", "egress + compute"], ["storage lifecycle tiers (hot → cold → archive)", "50–90% of storage"], ["right-size + autoscale; spot instances for batch", "30–70% compute"], ["reserved / savings plans for baseline", "~30–60%"], ["keep traffic in one AZ/region where safe", "cross-zone fees"]]))

X("authn-authz",
  P("**Authentication (AuthN)**: who are you? **Authorization (AuthZ)**: what may you do? Login proves identity; every request is then checked against permissions."),
  SEQ("A request passes both checks", ["Client", "API gateway", "Policy engine", "Document svc"],
      [["Client", "API gateway", "DELETE /docs/55 (Bearer JWT)"], ["API gateway", "API gateway", "AuthN: verify JWT signature + expiry → user 42"], ["API gateway", "Document svc", "forward with user 42"],
       ["Document svc", "Policy engine", "can user 42 'delete' doc 55?"], ["Policy engine", "Document svc", "deny: user is 'viewer'", "r"], ["Document svc", "Client", "403 Forbidden", "r", "401 = not authenticated; 403 = authenticated but not allowed."]]),
  TABLE("Authorization models", ["Model", "Rule looks like", "Good for"], [["RBAC", "role 'editor' can 'edit'", "most apps"], ["ABAC", "allow if user.dept == doc.dept and time in office hours", "fine-grained enterprise rules"], ["ReBAC (Zanzibar)", "user is 'viewer' of doc via folder → group membership", "Google Drive-style sharing"], ["ACL", "list of (user, permission) per object", "simple object sharing"]]))

X("sessions-jwt",
  SEQ("Server session vs JWT", ["Browser", "App server", "Session store (Redis)"],
      [NOTE(["Browser", "Session store (Redis)"], "Server-side session"), ["Browser", "App server", "login"], ["App server", "Session store (Redis)", "SET sess:abc {user: 42} EX 3600"], ["App server", "Browser", "Set-Cookie: sid=abc; HttpOnly; Secure", "r"],
       ["Browser", "App server", "request + cookie sid=abc"], ["App server", "Session store (Redis)", "GET sess:abc (lookup every request)"],
       NOTE(["Browser", "Session store (Redis)"], "JWT"), ["App server", "Browser", "JWT = header.payload{sub:42, exp}.signature", "r"], ["Browser", "App server", "Authorization: Bearer <JWT>", "", "Server only verifies the signature: no lookup. But it can't be revoked before expiry without a deny-list."]]),
  TABLE("Comparison", ["", "Server session", "JWT"], [["state", "server-side store", "self-contained token"], ["revocation", "delete the session: instant", "hard: short expiry + refresh tokens + deny-list"], ["scaling", "shared store needed", "no lookup"], ["size", "tiny cookie", "hundreds of bytes per request"]]),
  KEY("Common pattern: short-lived access JWT (5–15 min) + long-lived refresh token stored server-side (revocable, rotated on use).", "Best of both"))

X("oauth",
  SEQ("OAuth 2.0 Authorization Code flow with PKCE ('Sign in with Google')", ["User", "Your app", "Google auth server", "Google API"],
      [["User", "Your app", "click 'Sign in with Google'"], ["Your app", "User", "redirect to Google with client_id, scope, code_challenge", "r"], ["User", "Google auth server", "log in + consent to 'email, profile'"],
       ["Google auth server", "User", "redirect back to app with one-time code", "r"], ["Your app", "Google auth server", "exchange code + code_verifier (back channel)", "", "PKCE proves the same app that started the flow is finishing it."],
       ["Google auth server", "Your app", "access token (+ ID token for OIDC, refresh token)", "r"], ["Your app", "Google API", "GET /userinfo with access token"]]),
  TABLE("Terms", ["Term", "Meaning"], [["OAuth 2.0", "delegated authorization: app gets limited access without your password"], ["OpenID Connect (OIDC)", "identity layer on top: the ID token says who you are"], ["scope", "what the token allows (read:email)"], ["access vs refresh token", "short-lived for APIs vs long-lived to get new access tokens"], ["SSO", "one login across many apps (SAML/OIDC)"]]))

X("encryption",
  TABLE("Encryption in transit vs at rest", ["", "In transit", "At rest"], [["protects", "data moving on networks", "data on disks, backups"], ["how", "TLS / mTLS", "AES-256 (disk, DB, S3 server-side encryption)"], ["keys", "certificates", "KMS-managed keys"]]),
  SEQ("Envelope encryption with a KMS", ["App", "KMS", "Storage"],
      [["App", "KMS", "GenerateDataKey(master key 'orders')"], ["KMS", "App", "plaintext data key + encrypted data key", "r"], ["App", "App", "encrypt file with plaintext data key (AES-GCM), then discard that key"], ["App", "Storage", "store ciphertext + encrypted data key"],
       NOTE(["App", "Storage"], "to read: send encrypted data key to KMS → get plaintext key → decrypt. The master key never leaves the KMS.")]),
  TABLE("Hashing vs encryption", ["", "Hashing", "Encryption"], [["reversible?", "no", "yes, with the key"], ["use for", "passwords (bcrypt/argon2 with salt), integrity checks", "data you must read back"], ["example", "argon2id(password, salt)", "AES-256-GCM"]]))

X("web-security",
  TABLE("OWASP-style top threats", ["Attack", "Example", "Defence"],
        [["SQL injection", "`' OR 1=1 --` in a login field", "parameterised queries / ORM"], ["XSS", "`<script>` in a comment steals cookies", "escape output, Content-Security-Policy, HttpOnly cookies"], ["CSRF", "a hidden form on evil.com posts to your bank", "SameSite cookies, CSRF tokens"],
         ["SSRF", "server fetches http://169.254.169.254 (cloud metadata)", "allow-list outbound URLs, block internal ranges"], ["Broken access control", "GET /invoices/124 shows someone else's invoice", "check ownership on every request"], ["DDoS", "1 M requests/s from a botnet", "CDN/WAF, rate limits, autoscaling"]]),
  BA(CODE("Vulnerable: string concatenation", """String q = "SELECT * FROM users WHERE email = '" + email + "'";
// email = "x' OR '1'='1"  ->  WHERE email = 'x' OR '1'='1'  ->  every row returned"""),
     CODE("Safe: parameterised query", """PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE email = ?");
ps.setString(1, email);   // sent as data, never parsed as SQL"""),
     "Before: SQL injection", "After: prepared statement"),
  KEY("Defence in depth: WAF at the edge, authN/authZ at the gateway and service, least-privilege IAM, secrets in a vault, encrypted data, audit logs.", "Layering"))
