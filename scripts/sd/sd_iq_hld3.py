"""Theory interview questions: HLD questions (part 3)."""
from sd_iq_util import Q

Q("adclick-hld",
  ("B", "What are the requirements of an ad click aggregation system?", "Ingest billions of clicks, aggregate per ad per minute in near real time, be accurate for billing, and support queries for dashboards."),
  ("I", "How do you handle late and duplicate events?", "Dedupe by click id, event-time windows with watermarks and allowed lateness, and batch reconciliation."),
  ("I", "Stream vs batch for this system?", "Streaming for real-time dashboards; batch recomputation from raw logs as the source of truth for billing."),
  ("A", "How do you guarantee exactly-once aggregation?", "Checkpointing (Flink), idempotent/transactional sinks, and dedup state."),
  ("A", "How do you detect click fraud?", "Rules and ML on patterns (IP, device, frequency, CTR anomalies), filtering before billing."))

Q("jobscheduler-hld",
  ("B", "What are the components of a distributed job scheduler?", "Job API and store, a scheduler finding due jobs, a queue, worker pool, retry/backoff, and monitoring."),
  ("I", "How do you ensure a job runs once?", "Claim with leases/locks in the job store; idempotent jobs as a safety net."),
  ("I", "How do you scale to millions of scheduled jobs?", "Partition jobs by time bucket and shard id so schedulers scan only due buckets in parallel."),
  ("A", "How do you handle long-running jobs and worker crashes?", "Heartbeats extending leases; expired leases make the job claimable again."),
  ("A", "How do you support dependencies between jobs (DAGs)?", "Store dependencies, trigger downstream jobs when upstream ones succeed (Airflow-like)."))

Q("email-hld",
  ("B", "What are the main components of an email service?", "SMTP servers for sending/receiving, spam/virus filtering, mailbox storage, search index, web/IMAP APIs, attachments in object storage."),
  ("I", "How do you store emails for millions of users?", "Message bodies once (dedup for many recipients), per-user mailbox metadata (labels, read state) partitioned by user."),
  ("I", "How does spam filtering work?", "Reputation (SPF, DKIM, DMARC, sender IP), content classifiers, user feedback."),
  ("A", "How do you implement fast search over a user's mailbox?", "Per-user inverted indexes partitioned by user."),
  ("A", "How do you ensure deliverability when sending?", "Authenticated domains (SPF/DKIM/DMARC), warmed IPs, bounce handling and rate limiting per recipient domain."))

Q("s3-hld",
  ("B", "What are the main components of an object storage system?", "API frontends, a metadata service (bucket/key → object location, versions), data storage nodes, and background repair/GC."),
  ("I", "How do you achieve high durability?", "Replication or erasure coding across disks, racks and zones; checksums; background scrubbing and repair."),
  ("I", "Replication vs erasure coding trade-offs?", "Replication: simple, fast, 3× storage. Erasure coding: ~1.4–1.5× storage, more CPU and slower reconstruction."),
  ("A", "How do you scale metadata for trillions of objects?", "Partition metadata by bucket/key prefix across a distributed KV store with consensus-replicated partitions."),
  ("A", "How do you support strong read-after-write consistency?", "Commit metadata only after data is durable, and route reads through the consistent metadata store."))

Q("fooddelivery-hld",
  ("B", "What are the main services of a food delivery app?", "Restaurant/menu catalogue, search, cart/order, payment, dispatch/rider assignment, location tracking, notifications."),
  ("I", "How do you assign riders?", "Consider rider location, current load and food prep time to minimise delivery time; batch nearby orders."),
  ("I", "How do you show live order tracking?", "Rider location updates streamed via WebSockets/push to the customer with ETA recalculation."),
  ("A", "How do you handle restaurant availability and menu changes?", "Cache menus, propagate updates via events, check availability at order time."),
  ("A", "How do you handle peak hours (lunch/dinner)?", "Autoscale, surge fees and delivery radius limits, and pre-positioning riders."))

Q("onlinejudge-hld",
  ("B", "How does code submission and judging work?", "Submission stored → queued → a sandboxed worker compiles and runs against test cases with limits → verdict stored and pushed to the user."),
  ("I", "How do you securely run untrusted code?", "Containers/VMs with seccomp, no network, CPU/memory/time limits, read-only filesystem, non-root users."),
  ("I", "How do you handle a contest with a submission spike?", "Queue with autoscaled workers, priority for contest submissions, rate limiting per user."),
  ("A", "How do you deliver results to users?", "Polling or WebSocket/SSE updates when the verdict is ready."),
  ("A", "How do you implement a live contest leaderboard?", "Sorted sets updated per accepted submission with penalty times; cache and throttle updates."))

Q("leaderboard-hld",
  ("B", "Which data store fits a real-time leaderboard?", "Redis sorted sets: O(log n) score updates and rank queries."),
  ("I", "How do you show a user's rank and nearby players?", "ZREVRANK and ZREVRANGE around that rank."),
  ("I", "How do you persist leaderboard data?", "Score events to a durable DB/log; Redis as the serving layer rebuilt from the log if needed."),
  ("A", "How do you scale to hundreds of millions of players?", "Shard by score range, approximate ranks for the tail, exact top-N."),
  ("A", "How do you prevent cheating?", "Server-authoritative scoring, anomaly detection, rate limits."))

Q("googledocs-hld",
  ("B", "What is the core challenge of collaborative editing?", "Merging concurrent edits from many users so everyone converges to the same document while preserving intent."),
  ("I", "OT vs CRDT?", "OT transforms operations against concurrent ones via a central server; CRDTs use data structures whose merges always converge, enabling peer-to-peer/offline."),
  ("I", "How are edits propagated to collaborators?", "WebSockets to a collaboration server per document, which orders operations and broadcasts them."),
  ("A", "How do you store document history?", "Operation logs with periodic snapshots for fast loading and version history."),
  ("A", "How do you scale many active documents?", "Route each document to one collaboration server (sharding by doc id), with failover recovering from the op log."))

Q("searchengine-hld",
  ("B", "What are the main components of a web search engine?", "Crawler, document store, indexer (inverted index), ranking (PageRank + text relevance + ML), query serving, caching."),
  ("I", "How is the index partitioned?", "By document (each shard indexes a subset; queries fan out) or by term; document partitioning is most common."),
  ("I", "How is ranking done?", "Retrieve candidates by text relevance, then rank with many signals (links, freshness, quality, user signals) via learning-to-rank."),
  ("A", "How do you keep query latency low with fan-out?", "Replicated shards, tail-latency mitigation (hedged requests), early termination, caching popular queries."),
  ("A", "How do you keep the index fresh?", "Tiered indexes: a real-time small index for new content merged with large periodic rebuilds."))

Q("stockexchange-hld",
  ("B", "What is a matching engine?", "The component that maintains order books and matches buy and sell orders by price-time priority."),
  ("I", "Why is the matching engine usually single-threaded per symbol?", "Deterministic ordering and lowest latency without locks; scaling by partitioning symbols."),
  ("I", "How do you make it fault tolerant?", "Sequence all input orders in a durable log; replicas replay the same sequence deterministically for hot standby."),
  ("A", "How do you achieve microsecond latency?", "In-memory data structures, no GC pauses, kernel bypass networking, colocation, binary protocols."),
  ("A", "How is market data distributed?", "Multicast feeds of trades and book updates with sequence numbers and recovery channels."))

Q("mq-hld",
  ("B", "What are the core concepts of a Kafka-like queue?", "Topics, partitions as append-only logs, producers, consumer groups with offsets, replication with leaders and followers."),
  ("I", "How is durability ensured?", "Replication factor 3, acks=all with min in-sync replicas, and leader election from in-sync replicas."),
  ("I", "How do consumers scale?", "Consumer groups split partitions; parallelism is limited by the partition count."),
  ("A", "How does the broker achieve high throughput?", "Sequential writes, page cache, zero-copy, batching and compression."),
  ("A", "How do you handle retention and replay?", "Time/size-based retention, compaction for keyed topics; consumers reset offsets to replay."))

Q("maps-hld",
  ("B", "How do you represent a road network?", "A graph of intersections (nodes) and road segments (edges) with weights such as travel time."),
  ("I", "Which algorithms compute routes?", "Dijkstra/A* for basic routing; contraction hierarchies or similar preprocessing for fast continental-scale queries."),
  ("I", "How do you incorporate live traffic?", "Aggregate anonymised GPS speeds per segment to update edge weights and ETAs."),
  ("A", "How do you serve map tiles?", "Pre-rendered or vector tiles per zoom level stored and cached on CDNs."),
  ("A", "How do you scale routing queries?", "Partition the graph by region, precompute shortcuts, and cache popular routes."))
