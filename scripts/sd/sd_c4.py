"""System Design concepts, part 4: Distributed systems theory and probabilistic data structures."""
from sd_util import C

DISTRIBUTED = [
C("fallacies", "Why distributed systems are hard: the 8 fallacies, two generals", "Intermediate",
  "Once a system runs on many machines, the network can drop, delay or duplicate messages, clocks disagree and machines fail independently.",
  """### The eight fallacies of distributed computing
Developers wrongly assume: 1. the network is reliable, 2. latency is zero, 3. bandwidth is infinite, 4. the network is secure, 5. topology doesn't change, 6. there is one administrator, 7. transport cost is zero, 8. the network is homogeneous.

### Partial failure
A call to another service can: succeed, fail, or **time out — and you don't know whether it happened**. The payment may have gone through. That's why we need **timeouts, retries and idempotency**.

### Two generals problem
Two armies must attack together, communicating by messengers who may be captured. No finite number of messages can make both *certain* the other will attack. Lesson: you can't get perfect agreement over an unreliable network; you design with acknowledgements, retries and idempotency, and accept uncertainty.

### FLP impossibility (advanced)
In a fully asynchronous network with even one crashing process, no algorithm can guarantee consensus *always terminates*. Real systems (Raft, Paxos) use **timeouts** to get around it in practice.""",
  tips=["Whenever you draw a network arrow, ask 'what if this times out?'."]),

C("cap", "CAP theorem", "Intermediate",
  "During a network partition (P), a distributed data store must choose between Consistency (every read sees the latest write) and Availability (every request gets a non-error answer).",
  """- **C – Consistency** (linearizability): all nodes see the same data at the same time; a read returns the most recent write.
- **A – Availability**: every request to a non-failed node gets a response (maybe stale).
- **P – Partition tolerance**: the system keeps working even if messages between nodes are lost.

Networks *will* partition, so P is not optional. The real choice is **during a partition: C or A?**

|CP systems|AP systems|
|Reject or delay requests to stay correct|Answer with possibly stale data, reconcile later|
|HBase, MongoDB (default majority writes), Zookeeper, etcd, Spanner, bank ledgers|Cassandra, DynamoDB (default), Couchbase, DNS, shopping carts, social feeds|

### Common mistakes
- 'CA systems' don't exist in a distributed setting; a single-node DB is 'CA' only because it has no partition.
- CAP's 'C' is not ACID's 'C'.
- Many databases are **tunable** (Cassandra consistency level ONE vs QUORUM vs ALL).

### Per-feature choice
In one product you choose differently per feature: Amazon's **cart** is AP (always let users add items), **payment** is CP.""",
  diagram={"rows": [["u:Client"], ["db:Node A", "db:Node B"]], "edges": [["Client", "Node A", "write x=2"], ["Node A", "Node B", "✕ partition"]]},
  see=("pacelc", "consistency-models")),

C("pacelc", "PACELC theorem", "Advanced",
  "Extends CAP: if there is a Partition choose A or C; Else (normal operation) choose between Latency and Consistency.",
  """Even with no partition, keeping replicas consistent means waiting for them, which adds latency.

|System|If partition (P)|Else (E)|
|DynamoDB, Cassandra, Riak|A (available)|L (low latency)|
|BigTable, HBase, Spanner|C|C|
|MongoDB (typical)|A or C (configurable)|C|
|PNUTS (Yahoo)|C|L|

Use PACELC when the interviewer pushes past CAP: 'normally we trade a few ms of latency for consistency on payments, but feeds favour latency'.""",
  see=("cap",)),

C("consistency-models", "Consistency models: strong, eventual, causal and more", "Advanced",
  "Promises a system makes about what a read can return after writes, from strongest (linearizable) to weakest (eventual).",
  """|Model|Guarantee|Example|
|**Linearizable (strong)**|Every read sees the latest completed write, as if there were one copy|Spanner, etcd, ZooKeeper writes, a single Postgres primary|
|**Sequential**|All nodes see operations in the same order (not necessarily real-time order)|—|
|**Causal**|If A caused B (reply after a post), everyone sees A before B; unrelated writes may appear in any order|Comments under posts, COPS, MongoDB causal sessions|
|**Read-your-writes**|You always see your own writes|Updating your profile then viewing it|
|**Monotonic reads**|You never see time go backwards (newer then older)|Pin a session to one replica|
|**Eventual**|If writes stop, all replicas converge eventually|DNS, likes counters, Cassandra at ONE|

### Strong vs eventual in one picture
Strong: after 'write x=2' returns, every reader everywhere sees 2. Eventual: some readers may see 1 for a while (replication lag), but all reach 2.

### Picking a model per data type
- Money, inventory counts, unique usernames, locks → **strong**.
- Feeds, likes, view counts, recommendations, search indexes → **eventual**.
- Chat/comments → **causal** at least (replies after the message).""",
  see=("replication", "quorum")),

C("quorum", "Quorums: N, R, W", "Advanced",
  "With N replicas, write to W of them and read from R. If R + W > N, every read overlaps at least one replica that has the latest write.",
  """### Example: N = 3
- `W = 2, R = 2` (QUORUM/QUORUM): 2 + 2 > 3, strong-ish reads, tolerates 1 node down.
- `W = 1, R = 1`: fastest, but reads can be stale (eventual).
- `W = 3, R = 1`: fast reads, but writes fail if any replica is down.
- `W = 1, R = 3`: fast writes, slow reads.

### How the reader picks the latest
Each value carries a **version** (timestamp or vector clock); the reader takes the newest and repairs stale replicas (**read repair**).

### Sloppy quorum and hinted handoff
If some of the N 'home' replicas are down, write to other healthy nodes temporarily with a **hint**; they hand the data back when the home node recovers. Keeps writes available (AP) at the cost of weaker guarantees.

### Edge cases
Even with R + W > N, concurrent writes, failed partial writes and clock-based last-write-wins can still produce anomalies; true linearizability needs consensus.""",
  lab="quorum", see=("replication", "vector-clocks")),

C("time-clocks", "Time in distributed systems: clock skew, NTP, Lamport and vector clocks, HLC, TrueTime", "Advanced",
  "Machine clocks drift and disagree, so 'which write happened last?' can't safely use wall-clock time. Logical clocks order events by causality instead.",
  """### Physical clocks
- Clocks drift; **NTP** keeps them within a few ms, but jumps and skew happen. Never rely on timestamps from two machines to order events exactly.
- **Last-write-wins (LWW)** with skewed clocks can silently drop the truly newer write.

### Lamport clock
Each node keeps a counter: increment on every event; send it with messages; on receive set `counter = max(local, received) + 1`. If A happened-before B then `L(A) < L(B)` (but not the reverse). Gives a total order consistent with causality.

### Vector clock
Each node keeps a vector of counters, one per node. Compare vectors: if every entry of V1 ≤ V2, V1 happened before V2; if neither dominates, the writes are **concurrent → conflict** to resolve (merge, ask the user, CRDT). Used by Dynamo and Riak for detecting conflicts in carts.

### Hybrid logical clocks (HLC)
Physical time + a logical counter: close to wall-clock but still causal. Used by CockroachDB, YugabyteDB.

### Google TrueTime
GPS + atomic clocks give each machine an interval `[earliest, latest]` with ~7 ms uncertainty. Spanner **waits out the uncertainty** before committing ('commit wait'), giving globally consistent timestamps and external consistency.""",
  diagram={"seq": ["Node A", "Node B", "Node C"], "msgs": [["Node A", "Node B", "msg (A:1)"], ["Node B", "Node C", "msg (A:1,B:1)"], ["Node C", "Node A", "msg (A:1,B:1,C:1)"]]},
  see=("vector-clocks",)),

C("vector-clocks", "Conflict resolution: LWW, vector clocks, merges", "Advanced",
  "When two replicas accept different writes to the same key, the system must detect the conflict and pick or merge a winner.",
  """- **Last-write-wins**: keep the value with the highest timestamp. Simple (Cassandra), but loses data under concurrent writes or clock skew.
- **Vector clocks / version vectors**: detect true concurrency; keep both 'siblings' and let the application merge (Amazon cart: union of items).
- **Application merge**: domain rules (max, union, sum).
- **CRDTs**: data types that merge automatically and deterministically.
- **Avoid conflicts**: route all writes for a key to one leader (single-leader per key / partition).""",
  see=("crdt",)),

C("consensus", "Consensus: Paxos and Raft", "Advanced",
  "Consensus lets a group of nodes agree on one value (or one ordered log) even if some crash, as long as a majority is alive. It powers leader election, configuration stores and strongly consistent databases.",
  """### Why majority (quorum)
With 5 nodes, any two majorities (3+) overlap in at least one node, so two different values can't both be chosen. A cluster of **2f + 1** nodes tolerates **f** failures (3 nodes → 1 failure, 5 → 2).

### Raft (designed to be understandable)
1. **Leader election**: nodes start as followers; if a follower hears no heartbeat within a random timeout (150–300 ms) it becomes a **candidate**, increments the **term**, and asks for votes. A majority makes it **leader**. Random timeouts avoid split votes.
2. **Log replication**: clients send commands to the leader; it appends to its log and replicates to followers; once a **majority** has stored the entry it is **committed** and applied to the state machine.
3. **Safety**: a node only votes for candidates whose log is at least as up to date as its own, so a new leader always has all committed entries.

### Paxos
The original (Lamport): proposers, acceptors, learners; two phases (prepare/promise, accept/accepted). **Multi-Paxos** elects a stable leader to skip phase 1. Used in Google Chubby, Spanner. Correct but notoriously hard to implement.

### Where consensus is used
etcd (Kubernetes' brain), ZooKeeper (ZAB protocol), Consul, CockroachDB/TiDB/Spanner (Raft/Paxos groups per data range), Kafka KRaft (controller metadata).

### Cost
Every write needs a majority round trip: higher latency, especially across regions; throughput limited by the leader. Use consensus for **metadata and critical state**, not for every page view.""",
  diagram={"rows": [["u:Client"], ["Leader (term 4)"], ["Follower 1", "Follower 2", "Follower 3", "Follower 4"]],
           "edges": [["Client", "Leader (term 4)", "SET x=5"], ["Leader (term 4)", "Follower 1", "append"], ["Leader (term 4)", "Follower 2", "append"], ["Leader (term 4)", "Follower 3", "append"], ["Leader (term 4)", "Follower 4", "append"]]}),

C("leader-election", "Leader election and coordination services (ZooKeeper, etcd)", "Advanced",
  "Many systems need exactly one node to do a job (the leader). Coordination services provide leader election, locks, configuration and service discovery on top of consensus.",
  """### ZooKeeper / etcd / Consul give you
- A small, strongly consistent key–value tree.
- **Ephemeral nodes / leases**: disappear when the client's session dies → perfect for 'who is alive' and leader election.
- **Watches**: get notified when a key changes.
- **Sequential nodes / revisions**: build fair locks and queues.

### Leader election recipe (ZooKeeper)
Each candidate creates an ephemeral sequential node `/election/n_000012`; the one with the smallest number is leader; each other node watches the node just before it. If the leader dies, its node vanishes and the next one takes over.

### Split brain
Two nodes both believe they are leader (e.g. after a network partition or a long GC pause). Prevent it with **majority quorums**, **leases with expiry**, and **fencing tokens**.""",
  see=("distributed-locks", "consensus")),

C("distributed-locks", "Distributed locks and fencing tokens", "Advanced",
  "A lock that works across machines so only one worker does a job at a time. Hard to get right: locks must expire, and a paused holder must not keep writing after expiry.",
  """### Redis lock (simple)
`SET lock:job42 <random-id> NX PX 30000` (set if not exists, 30 s expiry). Release only if the value is still your id (check-and-delete in a Lua script).

### The danger
Worker A gets the lock, then pauses (GC, network) for 40 s; the lock expires; worker B takes it; A wakes up and writes too. Both 'hold' the lock.

### Fencing tokens
The lock service returns an increasing number with each grant (33, 34, ...). The storage layer rejects writes with a token lower than the highest it has seen. A's late write with token 33 is rejected after B wrote with 34. ZooKeeper's zxid / etcd revisions work as fencing tokens.

### Redlock debate
Redlock acquires the lock on a majority of independent Redis nodes. Fine for efficiency (avoid duplicate work); for correctness-critical locks prefer a consensus system (etcd, ZooKeeper) + fencing.

### Often better: avoid locks
Use DB constraints, optimistic concurrency (version column), single-partition ownership, or idempotent operations.""",
  diagram={"seq": ["Worker A", "Lock service", "Worker B", "Storage"], "msgs": [["Worker A", "Lock service", "acquire"], ["Lock service", "Worker A", "OK token 33"], ["Worker B", "Lock service", "acquire (after A's lease expired)"], ["Lock service", "Worker B", "OK token 34"], ["Worker B", "Storage", "write (token 34) ✓"], ["Worker A", "Storage", "late write (token 33) ✗ rejected"]]}),

C("gossip", "Gossip protocols and failure detection", "Advanced",
  "Nodes periodically exchange state with a few random peers, so information (membership, who is down) spreads through the cluster like a rumour in O(log N) rounds.",
  """### Gossip
- Each second, a node picks 1–3 random peers and swaps its view (member list, heartbeat counters, versions).
- Scales to thousands of nodes with no central server; tolerant of failures.
- Used by Cassandra, DynamoDB, Consul (Serf/SWIM), Redis Cluster, Amazon S3 internals.

### Failure detection
- **Heartbeats**: 'I'm alive' every T; suspect after missing k beats. Trade-off: fast detection vs false alarms.
- **Phi accrual detector** (Cassandra, Akka): outputs a suspicion level based on heartbeat arrival history instead of a fixed timeout.
- **SWIM**: probe a random node; if no ack, ask others to probe it indirectly before declaring it dead.""",
  see=("kvstore-hld",)),

C("merkle-anti-entropy", "Merkle trees, anti-entropy, read repair, hinted handoff", "Advanced",
  "Techniques Dynamo-style stores use to keep replicas in sync after failures.",
  """- **Read repair**: during a quorum read, if a replica returns an older version, write the newest version back to it.
- **Hinted handoff**: when a replica is down, another node stores the write with a hint and forwards it when the replica returns.
- **Anti-entropy with Merkle trees**: each replica builds a hash tree over its key ranges (leaf = hash of a range, parent = hash of children). Two replicas compare root hashes; if they differ, descend only into differing branches. Syncing finds differences by exchanging O(log n) hashes instead of all data.

Merkle trees are also used in Git, Bitcoin/blockchains, Cassandra repair, IPFS and Certificate Transparency.""",
  diagram={"rows": [["root = H(H12 + H34)"], ["H12 = H(H1+H2)", "H34 = H(H3+H4)"], ["H1", "H2", "H3", "H4"]],
           "edges": [["root = H(H12 + H34)", "H12 = H(H1+H2)"], ["root = H(H12 + H34)", "H34 = H(H3+H4)"], ["H12 = H(H1+H2)", "H1"], ["H12 = H(H1+H2)", "H2"], ["H34 = H(H3+H4)", "H3"], ["H34 = H(H3+H4)", "H4"]]}),

C("crdt", "CRDTs (conflict-free replicated data types)", "Advanced",
  "Data structures designed so replicas can be updated independently and always merge to the same result, with no coordination.",
  """### Examples
- **G-Counter** (grow-only): each replica counts its own increments; value = sum; merge = per-replica max.
- **PN-Counter**: two G-Counters (increments, decrements) → likes/dislikes.
- **G-Set / OR-Set** (observed-remove set): add/remove items; adds win over concurrent removes of unseen adds.
- **LWW-Register**, **Multi-value register**.
- **Sequence CRDTs** (RGA, Yjs, Automerge) for collaborative text editing.

### Where used
Redis Enterprise active-active, Riak, Figma-like and Notion-like collaboration, offline-first apps, multiplayer state.

### OT vs CRDT for collaborative editing
**Operational transformation** (Google Docs) transforms concurrent edits against each other on a central server; **CRDTs** merge without a central server but use more metadata.""",
  see=("googledocs-hld",)),

C("byzantine", "Crash faults vs Byzantine faults", "Advanced",
  "Most systems assume nodes either work or crash. Byzantine faults are nodes that lie or act maliciously; tolerating them needs 3f + 1 nodes and is mostly used in blockchains.",
  """- **Crash-stop / crash-recovery**: node stops or restarts. Raft/Paxos handle these with 2f + 1 nodes.
- **Omission / timing faults**: messages lost or very late.
- **Byzantine**: arbitrary, possibly malicious behaviour. **PBFT** and blockchain consensus (Tendermint, proof-of-work/stake) tolerate up to f traitors among 3f + 1.
- Inside a company's data centre you usually assume non-Byzantine nodes but still validate inputs and use checksums to catch corrupted data.""",
  tips=["Mentioning that you assume crash (non-Byzantine) faults shows you know the difference."]),

C("unique-id", "Generating unique IDs at scale (UUID, Snowflake, ticket servers)", "Intermediate",
  "Auto-increment IDs break with many database shards. Distributed systems use UUIDs, Snowflake-style time-ordered 64-bit IDs, or ranges handed out by a ticket server.",
  """|Approach|How|Pros|Cons|
|UUID v4|128-bit random|No coordination|Large, random → poor index locality, not sortable|
|UUID v7 / ULID|Timestamp prefix + random|Sortable by time, no coordination|128 bits|
|DB auto-increment per shard with offset|Shard 1: 1, 3, 5…; shard 2: 2, 4, 6…|Simple|Hard to add shards|
|Ticket server / range allocation|Central service hands out blocks of 1,000 IDs|Compact, nearly sequential|Central dependency (keep it HA)|
|**Twitter Snowflake**|64-bit: 1 sign bit + **41-bit ms timestamp** + **10-bit machine ID** + **12-bit sequence**|Sortable, 4,096 IDs/ms per machine, no coordination|Needs unique machine IDs; clock going backwards must be handled|

### Snowflake layout
`0 | 41 bits: ms since custom epoch (~69 years) | 5 bits datacenter | 5 bits worker | 12 bits sequence`

```java
synchronized long nextId() {
    long now = System.currentTimeMillis();
    if (now < lastMs) throw new IllegalStateException("clock moved backwards");
    if (now == lastMs) { seq = (seq + 1) & 4095; if (seq == 0) now = waitNextMs(lastMs); }
    else seq = 0;
    lastMs = now;
    return ((now - EPOCH) << 22) | (workerId << 12) | seq;
}
```
Used by Twitter, Discord, Instagram (variant), Sony (Sonyflake).""",
  see=("idgen-hld", "urlshortener-hld")),
]

PROBABILISTIC = [
C("bloom-filter", "Bloom filters", "Intermediate",
  "A tiny bit array that answers 'is X in the set?' with either 'definitely not' or 'probably yes'. No false negatives, a small tunable rate of false positives.",
  """### How it works
- A bit array of m bits and k hash functions.
- **Add x**: set bits `h1(x)…hk(x)` to 1.
- **Check y**: if any of its k bits is 0 → definitely not present; if all are 1 → probably present.
- You can't delete (use a **counting Bloom filter** for that).

### Sizing
About **10 bits per element** gives ~1% false positives (with k ≈ 7).

### Uses
- LSM-tree databases skip SSTables that can't contain a key (Cassandra, RocksDB, HBase).
- Cache penetration protection (reject IDs that never existed).
- Web crawlers: 'have I seen this URL?'.
- Chrome's old malicious-URL check, Medium's 'already recommended', username availability pre-check.""",
  example="1 billion URLs in a crawler: a Bloom filter needs ~1.2 GB instead of ~100 GB for storing the URLs.",
  see=("crawler-hld", "cache-problems")),

C("hyperloglog", "HyperLogLog and Count-Min Sketch", "Advanced",
  "HyperLogLog counts distinct items (unique visitors) using ~12 KB with ~1% error. Count-Min Sketch estimates how often each item appears (heavy hitters / top-K) in fixed memory.",
  """### HyperLogLog
- Hash each item; look at the number of leading zeros. Seeing a hash with many leading zeros suggests many distinct items. Average over many buckets for accuracy.
- Redis `PFADD visitors:2026-11-20 user42`, `PFCOUNT`. Mergeable across days/servers (`PFMERGE`).
- Used for unique visitors, distinct search queries, cardinality in analytics (BigQuery `APPROX_COUNT_DISTINCT`).

### Count-Min Sketch
- A d × w grid of counters with d hash functions. Add item: increment one counter per row. Estimate: the **minimum** across rows (never underestimates; may overestimate).
- With a small heap it gives approximate **top-K / trending** items over a stream.

### Other sketches
**t-digest** / HDR histogram for percentiles (p99 latency), **MinHash** for similarity (near-duplicate pages), reservoir sampling for random samples from a stream.""",
  see=("topk-hld",)),

C("geohash-quadtree", "Geospatial indexing: geohash, quadtree, S2, H3", "Intermediate",
  "Ways to find 'things near me' quickly by turning 2-D locations into searchable keys or tree cells.",
  """### Geohash
Recursively split the world into a grid and encode the cell as a base-32 string: `tdr1y` ≈ a 5 km cell in Bengaluru. Longer string = smaller cell; **shared prefix ≈ nearby**. Search the user's cell + its 8 neighbours (edge effects). Easy to store in any DB or Redis (`GEOSEARCH`).

### Quadtree
A tree where each node covers a square; split a node into 4 children when it holds more than k places (e.g. 100). Dense cities get deep, small cells; deserts stay shallow. Built in memory, great for 'find nearest drivers/restaurants'.

### Google S2 and Uber H3
- **S2** maps the sphere to cells on a cube using a Hilbert curve; cell IDs are 64-bit integers; used by Google Maps, Foursquare, MongoDB.
- **H3** uses hexagons (all neighbours equidistant); used by Uber for pricing and dispatch zones.

### Other options
R-trees (PostGIS), Elasticsearch geo queries.""",
  diagram={"rows": [["World"], ["NW", "NE", "SW", "SE"], ["NE.1", "NE.2", "NE.3", "NE.4"]],
           "edges": [["World", "NW"], ["World", "NE"], ["World", "SW"], ["World", "SE"], ["NE", "NE.1"], ["NE", "NE.2"], ["NE", "NE.3"], ["NE", "NE.4"]]},
  see=("proximity-hld", "uber-hld")),

C("trie-structures", "Tries, skip lists and other structures inside systems", "Intermediate",
  "Classic data structures that show up inside real systems: tries for autocomplete, skip lists in Redis sorted sets, heaps for top-K, ring buffers for queues.",
  """- **Trie** (prefix tree): autocomplete, IP routing tables (longest prefix match), spell checkers. Store top-k suggestions at each node for O(prefix length) lookups.
- **Skip list**: sorted structure with O(log n) insert/search using express lanes; Redis sorted sets and LevelDB memtables use them.
- **Heap / priority queue**: top-K, schedulers, Dijkstra in maps.
- **Ring buffer**: fixed-size queues, logging (LMAX Disruptor).
- **Consistent-hash ring**, **Merkle tree**, **Bloom filter**, **LSM tree**, **B+ tree**, **inverted index**, **geohash** — all covered in their own cards.
- **Graph algorithms**: shortest path (maps), PageRank (search), BFS (friend suggestions).""",
  see=("autocomplete-hld", "leaderboard-hld")),
]
