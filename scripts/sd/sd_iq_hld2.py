"""Theory interview questions: HLD questions (part 2)."""
from sd_iq_util import Q

Q("autocomplete-hld",
  ("B", "How does typeahead return suggestions so fast?", "Precomputed top-k suggestions per prefix stored in a trie or prefix → list map in memory, plus caching at CDN/browser."),
  ("I", "How are suggestions built?", "Offline aggregation of query logs (counts, recency weighting) → build trie snapshots → deploy to serving nodes; periodic rebuilds plus a trending layer."),
  ("I", "How do you reduce request volume?", "Debounce keystrokes, minimum prefix length, browser caching, and CDN caching of popular prefixes."),
  ("A", "How do you personalise suggestions?", "Merge global suggestions with the user's history and context (location, language) at query time."),
  ("A", "How do you shard the trie?", "By prefix ranges or the first characters, balanced by query volume."))

Q("youtube-hld",
  ("B", "What happens after a video is uploaded?", "Store raw file, split into chunks, transcode into multiple resolutions/codecs in parallel, generate thumbnails and manifests, then publish to CDN."),
  ("I", "How does playback adapt to bandwidth?", "Adaptive bitrate (HLS/DASH): the player picks segment quality based on measured throughput and buffer."),
  ("I", "How do you store video metadata and counts?", "Metadata in a sharded DB; view counts via async events aggregated in batches."),
  ("I", "Why is a CDN essential?", "Video traffic is enormous; CDNs serve segments near users and save origin bandwidth."),
  ("A", "How do you handle a newly viral video?", "Pre-warm CDNs, multiple origin replicas, request coalescing at edges."),
  ("A", "How would you design recommendations?", "Two-stage retrieval and ranking using watch history embeddings, trained offline with online features."))

Q("dropbox-hld",
  ("B", "How do clients upload efficiently?", "Chunk files (~4 MB), hash chunks, upload only new chunks in parallel and resumably."),
  ("I", "How do other devices learn about changes?", "A notification service (long polling/WebSocket) tells clients to fetch the new metadata and missing chunks."),
  ("I", "Metadata vs block storage?", "Metadata DB tracks files, versions and chunk lists (needs consistency); block storage holds immutable content-addressed chunks."),
  ("I", "How do you handle conflicts?", "Optimistic version check on commit; on conflict, save a conflicted copy."),
  ("A", "How do you save storage across users?", "Deduplicate chunks by hash, compress, and tier cold data."),
  ("A", "How do you share folders securely?", "ACLs on folder namespaces, share links with tokens and expiry, permission checks on every metadata and download request."))

Q("proximity-hld",
  ("B", "How do you find nearby businesses efficiently?", "Geospatial indexing: geohash/quadtree/S2 cells; search the user's cell and neighbours, then filter by exact distance."),
  ("I", "Why is this system read-heavy and how do you scale it?", "Businesses change rarely; replicate the geo index widely, cache results per cell, and serve from memory."),
  ("I", "How do you choose cell size?", "Based on density and radius; use variable precision (bigger cells in sparse areas) or quadtrees."),
  ("A", "How do you rank results?", "Combine distance, rating, popularity, open now, and personalisation."),
  ("A", "How do you update the index when businesses are added?", "Write to the DB, rebuild/refresh the geo index asynchronously (nightly or via events)."))

Q("uber-hld",
  ("B", "How do drivers' locations get tracked?", "Driver apps send GPS every few seconds to a location service storing current positions in memory/Redis, indexed geographically."),
  ("I", "How is a rider matched with a driver?", "Query nearby available drivers, rank by ETA, send offers one at a time (or a few) with timeouts, and lock the driver on acceptance."),
  ("I", "How do you compute ETA?", "Routing on a road graph with live traffic speeds; ML corrections from historical trips."),
  ("I", "How do you handle surge pricing?", "Compute supply/demand per geo cell over short windows and apply multipliers."),
  ("A", "How do you scale location updates (millions per minute)?", "Shard location service by region/cell, keep only latest position in memory, stream history to analytics asynchronously."),
  ("A", "What consistency is needed for trip state?", "Strong: a driver must not be double-assigned; use transactions/conditional updates on driver and trip state."))

Q("ticketmaster-hld",
  ("B", "What is the hardest part of a ticket booking system?", "Preventing double booking under extreme concurrency during on-sales."),
  ("I", "How do you hold seats during checkout?", "Atomically mark seats HELD with an expiry for the user; confirm to BOOKED on payment; release on timeout."),
  ("I", "How do you handle a huge traffic spike when tickets go on sale?", "Virtual waiting room, rate limiting, caching the event/seat map, and admitting users in batches."),
  ("A", "SQL or NoSQL for seat inventory?", "SQL with row-level locks/conditional updates is natural for strong consistency; Redis can front it for fast holds with careful reconciliation."),
  ("A", "How do you prevent bots from buying all tickets?", "CAPTCHA, purchase limits per account/payment method, queue fairness, device fingerprinting."))

Q("ecommerce-hld",
  ("B", "What are the main services in an e-commerce platform?", "Catalog, search, cart, inventory, pricing/promotions, checkout/order, payment, shipping, notifications, user accounts."),
  ("I", "How do you keep inventory accurate during checkout?", "Reserve stock atomically at checkout, confirm after payment, release on failure/timeout."),
  ("I", "How does order placement span services?", "A saga: create order, reserve inventory, charge payment, confirm; compensate on failure; events via outbox."),
  ("I", "How do you scale the product catalogue?", "Read-heavy: caches, CDN for images, search index for queries, replicas for the catalogue DB."),
  ("A", "How do you handle a flash sale?", "Pre-allocate stock, queue/waiting room, Redis atomic counters, async order creation, rate limits."),
  ("A", "How do you show consistent prices?", "Pricing service computes final price with promotions at checkout and snapshots it in the order."))

Q("payment-hld",
  ("B", "What are the key requirements of a payment system?", "Correctness (no double charges, no lost money), idempotency, auditability, security/compliance, and high availability."),
  ("I", "How do you prevent double charges?", "Idempotency keys, payment intent state machines, and unique constraints."),
  ("I", "How do you integrate with external payment providers reliably?", "Timeouts, status polling and webhooks for unknown outcomes, idempotent requests, and reconciliation."),
  ("I", "Why use a double-entry ledger?", "Balanced immutable debits and credits make balances auditable and reconstructable."),
  ("A", "How do you handle PCI compliance?", "Tokenise card data via the PSP, never store raw card numbers, isolate the cardholder data environment."),
  ("A", "How do you reconcile with banks?", "Daily settlement files compared to the internal ledger; mismatches flagged and resolved."))

Q("hotel-hld",
  ("B", "How do you model hotel room inventory?", "Per room type per date: total and reserved counts, rather than individual rooms at booking time."),
  ("I", "How do you prevent overbooking?", "Transactions updating all requested nights atomically with conditional checks or optimistic versions."),
  ("I", "Why might hotels intentionally overbook?", "To offset cancellations/no-shows; allow a small percentage above capacity with policies to relocate guests."),
  ("A", "How do you handle concurrent bookings for the last room?", "Row locks or optimistic concurrency with retries; idempotent reservation requests."),
  ("A", "How do you design search vs booking?", "Search uses cached/denormalised availability (eventually consistent); booking checks the source of truth."))

Q("metrics-hld",
  ("B", "What are the components of a metrics monitoring system?", "Agents/exporters, collectors (push or pull), time-series database, query engine, dashboards, alerting rules and notification."),
  ("I", "Push vs pull metric collection?", "Pull (Prometheus) scrapes targets: easy health detection. Push sends to a gateway/collector: works for short-lived jobs and across firewalls."),
  ("I", "How do you store time series efficiently?", "Compression (delta-of-delta, XOR floats), time-based partitions, downsampling and retention tiers."),
  ("I", "How do alerting rules avoid noise?", "Use 'for' durations, multi-window burn rates, grouping and deduplication, and inhibition rules."),
  ("A", "What is high cardinality and how do you control it?", "Too many label combinations; enforce label limits, avoid ids as labels, aggregate early."),
  ("A", "How do you query across many servers at scale?", "Sharded TSDB with distributed query fan-out and pre-aggregated recording rules."))

Q("logging-hld",
  ("B", "What are the components of a centralised logging system?", "Log shippers/agents, a buffer (Kafka), processors (parse, enrich, mask PII), an indexing store (Elasticsearch/Loki), and a search UI."),
  ("I", "Why put Kafka between agents and the index?", "Absorbs spikes, decouples ingestion from indexing, and allows replay when indexers fall behind or fail."),
  ("I", "How do you control log volume and cost?", "Log levels, sampling, retention tiers (hot/warm/cold), and indexing only selected fields."),
  ("A", "How do you correlate logs with traces?", "Include trace and span ids in structured logs."),
  ("A", "How do you handle PII in logs?", "Masking/redaction in agents or processors, access controls and retention policies."))

Q("topk-hld",
  ("B", "How do you compute top-K items over a stream?", "Count per item (exact or approximate) in time windows and maintain a min-heap of size K."),
  ("I", "Why use a Count-Min Sketch?", "Bounded memory approximate counts for huge key spaces; only overestimates."),
  ("I", "How do you get a global top-K from many partitions?", "Each partition computes local top-K (or larger) and an aggregator merges them."),
  ("A", "How do you handle sliding windows efficiently?", "Per-minute buckets merged over the window, or exponential decay scores."),
  ("A", "Exact vs approximate top-K: when does each matter?", "Approximate for trending UIs; exact via batch jobs for billing/reporting."))
