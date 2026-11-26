"""Theory interview questions: Distributed Systems tab."""
from sd_iq_util import Q

Q("fallacies",
  ("B", "What are the fallacies of distributed computing?", "False assumptions: the network is reliable, latency is zero, bandwidth is infinite, the network is secure, topology doesn't change, there is one administrator, transport cost is zero, the network is homogeneous."),
  ("I", "Why does a timeout not tell you whether a request succeeded?", "The request may have been lost, the server may be slow, or the response may have been lost after the work was done; the client can't distinguish these."),
  ("I", "How do you design around an unreliable network?", "Timeouts on every call, retries with backoff and jitter, idempotent operations, circuit breakers, and asynchronous messaging with durable queues."),
  ("I", "What is a partial failure?", "Some parts of a distributed system fail while others keep working, often nondeterministically; unlike a single machine that either works or crashes."),
  ("A", "What is a gray failure?", "A component that appears healthy to its health checks but is failing or slow for real traffic (bad disk, packet loss on one path). Detect with client-side metrics and differential observability."),
  ("A", "Why are clocks unreliable across machines?", "Clock drift, NTP corrections (even backwards jumps), leap seconds and VM pauses. Don't order events by wall-clock timestamps across machines; use logical clocks or a single sequencer."))

Q("cap",
  ("B", "State the CAP theorem precisely.", "In the presence of a network partition, a distributed system must choose between linearizable consistency and availability (every non-failed node answers every request)."),
  ("I", "Classify common databases as CP or AP.", "CP-leaning: ZooKeeper, etcd, HBase, Spanner, MongoDB (default). AP-leaning: Cassandra, DynamoDB (default eventual reads), Riak, CouchDB, DNS. Many are tunable per request."),
  ("I", "How can a system be tunable between CP and AP?", "Quorum settings (R/W per request in Cassandra), read consistency options (DynamoDB strongly consistent reads), or per-feature choices."),
  ("I", "What happens to an AP system after a partition heals?", "Replicas reconcile divergent writes using last-write-wins, vector clocks + app merge, or CRDTs; anti-entropy and read repair bring replicas back in sync."),
  ("A", "What are common criticisms of CAP?", "It's binary and only about partitions; 'availability' is a strict definition rarely met; it ignores latency; real systems pick nuanced points. PACELC and consistency models give a richer picture."),
  ("A", "How would you design a shopping cart vs a payment ledger with respect to CAP?", "Cart: AP, always accept adds, merge carts on conflict (union). Ledger: CP, refuse or delay operations that can't be confirmed by a majority/leader, never risk double-spend."))

Q("pacelc",
  ("B", "What does PACELC add to CAP?", "Else (no partition), systems still trade Latency against Consistency, because strong consistency means waiting for replicas."),
  ("I", "Classify DynamoDB/Cassandra and Spanner under PACELC.", "Dynamo-style: PA/EL (available during partitions, low latency normally). Spanner/CockroachDB: PC/EC (consistent always, pays commit latency)."),
  ("I", "Why is the 'ELC' part relevant every day?", "Partitions are rare, but every write chooses whether to wait for remote replicas; across regions that's 50–200 ms per write."),
  ("A", "How do systems reduce the latency cost of consistency?", "Keep replicas close (same region, quorum in nearby zones), leader leases for local reads, follower reads with bounded staleness, and partitioning data so most transactions stay in one region."),
  ("A", "How does Spanner offer strong consistency with acceptable latency?", "Paxos groups per shard, TrueTime with bounded clock uncertainty and commit-wait for external consistency, and lock-free snapshot reads at past timestamps from any replica."))

Q("consistency-models",
  ("B", "Strong vs eventual consistency?", "Strong: every read sees the latest completed write. Eventual: replicas converge if writes stop, but reads may be stale meanwhile."),
  ("I", "What is linearizability?", "Operations appear to occur atomically at a single point between their start and end, in a total order consistent with real time: the system behaves like one copy."),
  ("I", "Explain read-your-writes and monotonic reads.", "Read-your-writes: a user always sees their own updates. Monotonic reads: a user never sees data go back in time across successive reads."),
  ("I", "What is causal consistency?", "Causally related operations are seen in the same order by everyone (a reply never before its question); concurrent operations may be seen in different orders."),
  ("A", "Sequential consistency vs linearizability?", "Both give a single total order, but sequential consistency only needs to respect each client's program order, not real time; linearizability also respects real-time ordering."),
  ("A", "How do you choose a consistency model for a feature?", "By the cost of anomalies: money/inventory → strong; social content → eventual with read-your-writes and monotonic reads; collaborative/chat → causal ordering per conversation."))

Q("quorum",
  ("B", "What are N, R and W in quorum systems?", "N = replicas per key, W = replicas that must ack a write, R = replicas queried per read."),
  ("I", "Why does R + W > N give strong reads?", "Every read set overlaps every write set in at least one replica, so at least one replica returns the latest version (chosen by version/timestamp)."),
  ("I", "Typical settings and their trade-offs?", "N=3, W=2, R=2 balanced; W=1 fast writes but weaker durability; R=1 fast reads, may be stale; W=N slow writes that fail if any node is down."),
  ("I", "What is read repair?", "When a read finds replicas with stale versions, the coordinator writes the newest version back to them."),
  ("A", "What is a sloppy quorum and hinted handoff?", "If a home replica is down, writes go to another node with a 'hint' to forward them later; improves write availability but weakens the R + W > N guarantee until handoff."),
  ("A", "Can quorums alone give linearizability?", "Not fully: with concurrent writes, clock-based conflict resolution and sloppy quorums, anomalies remain. Linearizability needs read repair before returning, versioning and careful handling, or consensus."))

Q("time-clocks",
  ("B", "Why can't we use timestamps to order events across servers?", "Clocks drift and are corrected by NTP (even backwards), so an event later in reality can get an earlier timestamp on another machine."),
  ("I", "What is a Lamport clock?", "A counter per process: increment on each event; on receive, set to max(local, received) + 1. Gives an order consistent with causality (if a → b then L(a) < L(b))."),
  ("I", "Physical vs logical clocks?", "Physical clocks track real time (with error). Logical clocks only track ordering/causality, not real time."),
  ("A", "What is a hybrid logical clock?", "Combines physical time with a logical counter so timestamps are close to real time but still preserve causality and never go backwards (used by CockroachDB)."),
  ("A", "What is Google TrueTime?", "An API returning an interval [earliest, latest] with bounded uncertainty via GPS and atomic clocks; Spanner waits out the uncertainty before committing to get globally ordered timestamps."))

Q("vector-clocks",
  ("B", "What is a vector clock?", "A vector of counters, one per node, attached to data versions, used to determine whether versions are causally ordered or concurrent."),
  ("I", "How do you compare two vector clocks?", "A ≤ B if every entry of A ≤ the matching entry of B; if neither A ≤ B nor B ≤ A, they're concurrent (a conflict)."),
  ("I", "What does a system do when it finds concurrent versions?", "Keeps siblings and lets the application merge (Dynamo cart union), or resolves automatically with LWW or CRDT merge rules."),
  ("A", "What's the downside of vector clocks?", "Size grows with the number of writers; needs pruning (which can cause false conflicts) and pushes merge complexity to the application."),
  ("A", "Version vectors vs vector clocks?", "Version vectors track versions of replicas of data items (per replica counters); vector clocks track causality of events between processes. Often used interchangeably in practice."))

Q("consensus",
  ("B", "What is the consensus problem?", "Getting a group of nodes to agree on a value (or sequence of values) despite some nodes failing, so all correct nodes decide the same thing."),
  ("I", "How does Raft elect a leader?", "Followers that miss heartbeats become candidates, increment the term and request votes; a candidate with a majority of votes (and an up-to-date log) becomes leader. Randomised timeouts avoid split votes."),
  ("I", "How does Raft replicate a log entry?", "The leader appends the entry and sends AppendEntries to followers; once a majority has stored it, it's committed and applied to the state machine; followers learn the commit index via later messages."),
  ("I", "Why do consensus clusters have an odd number of nodes?", "A majority is needed; 3 nodes tolerate 1 failure, 4 still tolerate only 1, 5 tolerate 2. Even sizes add cost without extra fault tolerance."),
  ("I", "Where is consensus used in practice?", "etcd/ZooKeeper/Consul (configuration, leader election, locks), Kafka KRaft metadata, Spanner/CockroachDB replication, Kubernetes state."),
  ("A", "Raft vs Paxos?", "Same guarantees; Raft was designed for understandability with a strong leader, explicit terms and log matching. Multi-Paxos is more flexible but notoriously hard to implement correctly."),
  ("A", "What is the FLP impossibility result?", "In a fully asynchronous system with even one crash failure, no deterministic algorithm can guarantee consensus terminates. Real systems use timeouts/partial synchrony and randomisation."))

Q("leader-election",
  ("B", "Why do distributed systems need leader election?", "To have one node coordinate writes, schedule jobs or hold a role at a time, avoiding conflicts and duplicate work."),
  ("I", "How do you implement leader election with ZooKeeper or etcd?", "Create an ephemeral node/lease key; whoever creates it (or has the lowest sequence number) is leader; others watch it and take over when the session/lease expires."),
  ("I", "What is split brain?", "Two nodes both believe they are leader (e.g., after a pause or partition) and both act, corrupting data or duplicating work."),
  ("A", "How do fencing tokens prevent split-brain damage?", "Each new leader/lock holder gets a monotonically increasing token; resources reject operations with an older token, so a stale leader can't write."),
  ("A", "Why are lease durations a trade-off?", "Short leases fail over quickly but risk false failovers on GC pauses/network blips; long leases are stable but leave the system leaderless longer after a real crash."))

Q("distributed-locks",
  ("B", "What is a distributed lock?", "A lock shared across processes/machines so only one holder performs a critical operation at a time."),
  ("I", "How do you build one with Redis?", "SET key unique-token NX PX ttl to acquire; release with a Lua script that deletes only if the token matches; renew while working."),
  ("I", "Why does a lock need a TTL?", "So a crashed holder doesn't block everyone forever; but then a slow (not crashed) holder may lose the lock while still working."),
  ("I", "Efficiency lock vs correctness lock?", "Efficiency: avoids duplicate work; occasional double execution is OK (Redis lock fine). Correctness: double execution corrupts data; needs consensus-backed locks plus fencing tokens."),
  ("A", "What are the criticisms of Redlock?", "It relies on bounded clock drift and process pauses; GC pauses or clock jumps can let two clients hold the lock. Without fencing tokens it can't guarantee safety."),
  ("A", "How can you avoid distributed locks altogether?", "Single-writer partitioning (route all updates for a key to one consumer), conditional writes/compare-and-set, idempotent operations, and database constraints."))

Q("gossip",
  ("B", "What is a gossip protocol?", "Nodes periodically exchange state with a few random peers, so information spreads epidemically through the cluster without a central coordinator."),
  ("I", "How fast does gossip spread information?", "Roughly O(log N) rounds: each round the number of informed nodes multiplies, so even thousands of nodes converge in seconds."),
  ("I", "How is gossip used for failure detection?", "Nodes gossip heartbeat counters; if a node's counter doesn't increase for a timeout, it's marked suspect then dead (SWIM adds indirect probes)."),
  ("A", "Push vs pull vs push-pull gossip?", "Push sends updates; pull asks peers for newer data; push-pull exchanges both ways and converges fastest."),
  ("A", "What are the downsides of gossip?", "Eventual (not immediate) convergence, bandwidth overhead in very large clusters, and probabilistic rather than guaranteed delivery timing."))

Q("merkle-anti-entropy",
  ("B", "What is a Merkle tree?", "A tree where each leaf is a hash of a data block and each parent is a hash of its children; the root summarises all data."),
  ("I", "How do Merkle trees speed up replica synchronisation?", "Compare roots; if they differ, descend only into differing subtrees until you find the differing leaf ranges, exchanging O(log n) hashes instead of all keys."),
  ("I", "Where are Merkle trees used?", "Cassandra/Dynamo anti-entropy repair, Git, blockchains, BitTorrent, certificate transparency logs, file sync systems."),
  ("A", "What is anti-entropy vs read repair?", "Read repair fixes stale replicas only for keys that are read. Anti-entropy is a background process comparing whole replicas (often with Merkle trees) to fix everything."),
  ("A", "What is the cost of maintaining Merkle trees?", "Recomputing hashes as data changes (update path to root) and building trees for large ranges uses CPU and I/O; systems often build them on demand during repair."))

Q("crdt",
  ("B", "What is a CRDT?", "A conflict-free replicated data type: replicas can be updated independently and merged in any order, always converging to the same state without coordination."),
  ("I", "Why does a CRDT merge need to be commutative, associative and idempotent?", "So the order, grouping and duplication of sync messages don't matter, which is exactly what unreliable networks produce."),
  ("I", "Give examples of CRDTs.", "G-Counter, PN-Counter, G-Set, 2P-Set, OR-Set, LWW-Register, RGA/sequence CRDTs for text (Yjs, Automerge)."),
  ("A", "How does an OR-Set handle concurrent add and remove?", "Each add gets a unique tag; remove deletes only observed tags, so a concurrent add with a new tag survives (add-wins)."),
  ("A", "What are the downsides of CRDTs?", "Metadata growth (tombstones, tags), limited semantics (can't enforce invariants like 'balance ≥ 0'), and complexity for rich data types."))

Q("byzantine",
  ("B", "Crash faults vs Byzantine faults?", "Crash: a node stops responding. Byzantine: a node behaves arbitrarily, including lying or sending conflicting messages."),
  ("I", "How many nodes do you need to tolerate f Byzantine faults?", "3f + 1 (vs 2f + 1 for crash faults)."),
  ("I", "Where does Byzantine fault tolerance matter?", "Open/permissionless systems (blockchains), aerospace and safety-critical hardware, and multi-organisation systems where participants don't trust each other."),
  ("A", "Why don't most company datacenters use BFT protocols?", "They trust their own nodes; BFT costs more messages, nodes and latency. Crash-tolerant consensus plus checksums, authentication and audits is sufficient."),
  ("A", "What is PBFT at a high level?", "A leader proposes; replicas run pre-prepare, prepare and commit phases, each requiring 2f + 1 matching messages, so honest replicas agree even if f are malicious."))

Q("unique-id",
  ("B", "Why not use auto-increment IDs in a distributed system?", "A single DB sequence is a bottleneck and single point of failure, and IDs from different shards collide."),
  ("I", "Explain the Snowflake ID format.", "64 bits: sign bit, 41-bit millisecond timestamp, 10-bit machine id, 12-bit per-ms sequence: roughly time-sortable, 4,096 IDs per ms per machine, no coordination per ID."),
  ("I", "UUID v4 vs Snowflake vs ULID/UUIDv7?", "UUIDv4: 128-bit random, no coordination, not sortable, poor index locality. Snowflake: 64-bit, sortable, needs machine ids. ULID/UUIDv7: 128-bit, time-prefixed, sortable, no coordination."),
  ("I", "Why does ID sortability matter for databases?", "Time-ordered keys append to the end of B-tree indexes (good locality, fewer page splits) and allow pagination by id."),
  ("A", "How do you handle clock going backwards in Snowflake?", "Detect it; wait until time catches up for small skews, refuse to generate (or use a reserved bit/sequence) for large skews, and alert."),
  ("A", "How do you assign machine ids?", "From config, from ZooKeeper/etcd with leases, or derived from IP/pod ordinal; must be unique among live generators."))

Q("bloom-filter",
  ("B", "What is a Bloom filter?", "A space-efficient probabilistic set using a bit array and k hash functions; answers 'definitely not present' or 'probably present'."),
  ("B", "Can a Bloom filter give false negatives?", "No. Only false positives, with a probability that depends on size, item count and number of hash functions."),
  ("I", "Where are Bloom filters used in systems?", "Skipping SSTable reads in LSM databases, crawlers' seen-URL checks, cache penetration protection, malicious URL lists, join optimisation in big data."),
  ("I", "How do you size a Bloom filter?", "m = −n ln p / (ln 2)² bits and k = (m/n) ln 2 hashes; ~10 bits per item gives ~1% false positives."),
  ("A", "How do you support deletions?", "Counting Bloom filters (small counters instead of bits) or cuckoo filters."),
  ("A", "What happens if you insert many more items than planned?", "The false-positive rate rises sharply; use scalable Bloom filters (add new layers) or rebuild with a bigger size."))

Q("hyperloglog",
  ("B", "What does HyperLogLog estimate?", "The number of distinct elements (cardinality) in a stream using a tiny fixed amount of memory."),
  ("I", "How does HyperLogLog work intuitively?", "Hash items; the maximum number of leading zeros seen hints at cardinality (seeing 10 leading zeros suggests ~1,000 items). Many registers averaged harmonically reduce variance."),
  ("I", "What accuracy and memory does Redis HLL give?", "~0.81% standard error with 12 KB per counter, regardless of how many items."),
  ("A", "Why are HLLs mergeable and why is that useful?", "Merging takes the max per register, giving the HLL of the union: combine per-day or per-shard counters into weekly/global unique counts."),
  ("A", "When would you not use HyperLogLog?", "When exact counts are required (billing) or when you need to know which items are in the set."))

Q("geohash-quadtree",
  ("B", "Why can't you just index latitude and longitude with normal B-tree indexes?", "A 2-D proximity query becomes a range scan on one dimension plus filtering on the other, which scans huge strips of data."),
  ("I", "How does geohash work?", "Interleaves bits of latitude and longitude and encodes them in base32; longer strings mean smaller cells and nearby points usually share prefixes."),
  ("I", "Why search neighbouring cells as well?", "Points near a cell border can be very close but have different prefixes, so you search the cell plus its 8 neighbours."),
  ("I", "Quadtree vs geohash?", "Geohash is a fixed grid that's easy to store in any key-value DB. Quadtrees adapt cell size to density (split crowded cells) and are usually held in memory."),
  ("A", "Why did Uber create H3?", "Hexagonal cells have uniform distance to all neighbours and fewer edge distortions, useful for surge pricing, supply/demand analysis and smoothing."),
  ("A", "How do you handle very frequent location updates (drivers every 4 s)?", "Keep current locations in memory (Redis GEO or in-memory geo index sharded by region), don't write each update to the primary DB, and stream updates to analytics separately."))

Q("trie-structures",
  ("B", "What is a trie?", "A tree where each edge is a character and paths from the root spell prefixes, so all words sharing a prefix share a path."),
  ("I", "How do you make autocomplete fast with a trie?", "Store the top-k completions at each node so a lookup is just walking the prefix (O(length)) and returning the cached list."),
  ("I", "Trie vs hash map of prefixes?", "A hash map of prefix → top-k is fast but duplicates data heavily; a trie shares structure. At scale, both are built offline and served from memory/cache."),
  ("A", "How do you update suggestions with trending queries?", "Rebuild offline from logs periodically and push snapshots; add a small real-time layer for trending terms merged at query time."),
  ("A", "How do you reduce trie memory?", "Compressed/radix tries (merge single-child chains), storing ids instead of strings, sharding by prefix, and limiting depth."))
