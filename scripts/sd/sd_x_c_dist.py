"""Detailed explanations with diagrams: Distributed Systems tab."""
from sd_x_util import X, P, H, AN, KEY, FLOW, SEQ, NOTE, ER, TABLE, CALC, BARS, CODE, UML, STATE

X("fallacies",
  TABLE("The 8 fallacies and what they break", ["False assumption", "Reality", "Design response"],
        [["the network is reliable", "packets drop, links partition", "timeouts, retries, idempotency"], ["latency is zero", "0.5 ms in-DC, 150+ ms cross-continent", "batch calls, cache, keep chatty calls local"], ["bandwidth is infinite", "large payloads saturate links", "compress, paginate, stream"],
         ["the network is secure", "anyone can sniff/spoof", "TLS/mTLS, zero trust"], ["topology doesn't change", "IPs and nodes come and go", "service discovery, DNS, health checks"], ["there is one administrator", "many teams/providers", "contracts, observability, runbooks"],
         ["transport cost is zero", "serialisation CPU + cloud egress fees", "efficient formats, keep traffic in-region"], ["the network is homogeneous", "mixed hardware, protocols, versions", "standard protocols, backward-compatible APIs"]]),
  SEQ("Why a timeout tells you almost nothing", ["Client", "Server"],
      [["Client", "Server", "charge ₹500"], NOTE(["Client", "Server"], "no reply within 2 s"),
       ["Client", "Client", "was the request lost? the server slow? the reply lost?", "", "All three look identical to the client. The charge may or may not have happened, so a retry must be idempotent (same Idempotency-Key)."]]))

X("cap",
  P("CAP: during a network **P**artition, a distributed store must give up either **C**onsistency (every read sees the latest write) or **A**vailability (every request gets a non-error answer). Without a partition, you can have both."),
  SEQ("CP system (e.g. ZooKeeper, etcd, HBase) during a partition", ["Client", "Node A (minority side)", "Node B + C (majority side)"],
      [NOTE(["Node A (minority side)", "Node B + C (majority side)"], "✂ A is cut off"), ["Client", "Node A (minority side)", "write x = 2"], ["Node A (minority side)", "Client", "error: no quorum", "r", "Refuses rather than risk divergence: consistent, not available."],
       ["Client", "Node B + C (majority side)", "write x = 2"], ["Node B + C (majority side)", "Client", "OK (2 of 3 = majority)", "r"]]),
  SEQ("AP system (e.g. Cassandra, DynamoDB default) during a partition", ["Client 1", "Node A", "Node B", "Client 2"],
      [NOTE(["Node A", "Node B"], "✂ partition"), ["Client 1", "Node A", "write cart += shoes"], ["Node A", "Client 1", "OK", "r"], ["Client 2", "Node B", "read cart"], ["Node B", "Client 2", "old cart (no shoes)", "r", "Available but stale. After healing, replicas reconcile (last-write-wins, vector clocks, CRDTs)."]]),
  TABLE("Examples", ["System", "Leans", "Why"], [["bank ledger, seat booking", "CP", "double-spend/double-book is unacceptable"], ["shopping cart, likes, feeds", "AP", "always accept user actions"], ["DNS", "AP", "stale records are tolerable"], ["etcd / ZooKeeper", "CP", "they hold locks and leader info"]]))

X("pacelc",
  P("PACELC extends CAP: **if Partition** → choose **A**vailability or **C**onsistency; **Else** (normal operation) → choose **L**atency or **C**onsistency. The 'else' part matters every day, because strong consistency means waiting for replicas."),
  TABLE("Systems classified", ["System", "During partition (PA / PC)", "Normally (EL / EC)", "Meaning"], [["DynamoDB / Cassandra", "PA", "EL", "fast, eventually consistent (tunable)"], ["MongoDB (default)", "PC", "EC", "primary handles writes/reads"],
        ["Spanner / CockroachDB", "PC", "EC", "consistent; pays commit latency"], ["PNUTS (Yahoo)", "PC", "EL", "per-record master; local reads fast"]]),
  CALC("Cost of 'EC' across regions", [("Round trip Mumbai ↔ Singapore", "rtt = 60", "ms"), ("Quorum write needing 1 remote ack", "rtt", "ms"), ("Same write, local ack only (EL)", "1", "ms"), ("Penalty factor", "rtt / 1", "×")]))

X("consistency-models",
  P("Asha posts a comment. Who sees it, and when? Each model promises something different:"),
  TABLE("From strongest to weakest", ["Model", "Promise", "What Ravi (another user) might see", "Cost"],
        [["Linearizable (strong)", "acts like one copy; reads see the latest completed write", "comment as soon as Asha's write returns", "highest latency, coordination"], ["Sequential", "everyone sees writes in the same order", "same order, maybe later", "high"],
         ["Causal", "cause before effect (reply after the comment it answers)", "never a reply before its comment", "medium"], ["Read-your-writes", "Asha always sees her own writes", "(Ravi: no promise)", "low: sticky reads"],
         ["Monotonic reads", "you never go back in time", "doesn't see the comment and then lose it", "low"], ["Eventual", "replicas converge if writes stop", "may see it late, possibly out of order", "lowest"]]),
  SEQ("Read-your-writes violation and fix", ["Asha", "Leader", "Lagging replica"],
      [["Asha", "Leader", "post comment"], ["Leader", "Asha", "OK", "r"], ["Asha", "Lagging replica", "reload page"], ["Lagging replica", "Asha", "no comment!", "r", "She thinks it failed and posts again."],
       NOTE(["Asha", "Lagging replica"], "Fix: route Asha's reads to the leader for ~10 s after a write, or wait until the replica reaches her write's log position")]))

X("quorum",
  P("With **N** replicas, a write waits for **W** acks and a read asks **R** replicas. If **R + W > N**, every read set overlaps every write set in at least one replica, so the read sees the latest value (by version)."),
  TABLE("N = 3: choosing R and W", ["W", "R", "R + W > N?", "Behaviour"], [["2", "2", "✔ (4 > 3)", "balanced; tolerates 1 node down for both"], ["3", "1", "✔", "fast reads, writes fail if any node down"], ["1", "3", "✔", "fast writes, slow reads"], ["1", "1", "✘", "fastest, may read stale data"]]),
  SEQ("Overlap in action (N = 3, W = 2, R = 2)", ["Client", "Replica 1", "Replica 2", "Replica 3"],
      [["Client", "Replica 1", "write x = 7 (v2)"], ["Client", "Replica 2", "write x = 7 (v2)"], NOTE(["Replica 3"], "missed the write: still x = 5 (v1)"),
       ["Client", "Replica 2", "read x"], ["Client", "Replica 3", "read x"], ["Replica 3", "Client", "x = 5 (v1)", "r"], ["Replica 2", "Client", "x = 7 (v2) → newest wins", "r", "Read repair: the client/coordinator also writes v2 back to Replica 3."]]))

X("time-clocks",
  P("Machines' clocks drift and NTP corrections can move them backwards, so wall-clock timestamps can't reliably order events across machines. **Lamport clocks** give a consistent order using counters:"),
  TABLE("Lamport clock rules", ["Event", "Rule"], [["local event", "counter += 1"], ["send message", "counter += 1; attach counter"], ["receive message with t", "counter = max(counter, t) + 1"]]),
  SEQ("Three processes with Lamport timestamps", ["P1", "P2", "P3"],
      [["P1", "P1", "event a (L=1)"], ["P1", "P2", "send m1 (L=2)"], ["P2", "P2", "receive m1: max(0, 2) + 1 = 3"], ["P2", "P3", "send m2 (L=4)"], ["P3", "P3", "local event (L=1)"], ["P3", "P3", "receive m2: max(1, 4) + 1 = 5", "", "If a → b causally then L(a) < L(b). The reverse isn't guaranteed: L alone can't detect concurrency (vector clocks can)."]]),
  KEY("Google Spanner's TrueTime exposes clock uncertainty as an interval [earliest, latest] and waits out the uncertainty (~7 ms) before committing, giving globally ordered timestamps.", "Real-world trick"))

X("vector-clocks",
  P("A vector clock keeps one counter **per node**. Comparing two vectors tells you whether one event happened before another, or whether they're **concurrent** (a conflict to resolve)."),
  TABLE("Cart edited on two replicas", ["Step", "Replica A clock", "Replica B clock", "Value"],
        [["start, synced", "[A:1, B:0]", "[A:1, B:0]", "{milk}"], ["Asha adds eggs on A", "[A:2, B:0]", "", "{milk, eggs}"], ["Ravi adds bread on B (partition)", "", "[A:1, B:1]", "{milk, bread}"],
         ["compare [2,0] vs [1,1]", "", "", "neither ≥ the other in every slot → concurrent"], ["merge (union for carts)", "[A:2, B:1]", "[A:2, B:1]", "{milk, eggs, bread}"]]),
  TABLE("Comparison rule", ["Relation", "Condition"], [["V1 happened before V2", "every V1[i] ≤ V2[i] and at least one <"], ["concurrent", "some V1[i] > V2[i] and some V1[j] < V2[j]"]]),
  KEY("Amazon's original Dynamo used vector clocks and returned conflicting versions to the app to merge. Many systems choose last-write-wins instead (simpler, but silently drops one update).", "In practice"))

X("consensus",
  P("Consensus lets a group of nodes agree on a sequence of values (a replicated log) even if some crash. **Raft** does it with a leader, terms and majorities."),
  STATE("Raft node roles", [["[*]"], ["Follower"], ["Candidate"], ["Leader"]],
        [["[*]", "Follower", "start"], ["Follower", "Candidate", "election timeout (no heartbeat)"], ["Candidate", "Leader", "votes from majority"], ["Candidate", "Follower", "sees higher term / another leader"], ["Candidate", "Candidate", "split vote → new term"], ["Leader", "Follower", "sees higher term"]]),
  SEQ("Replicating one log entry (5 nodes)", ["Client", "Leader (term 3)", "F1", "F2", "F3"],
      [["Client", "Leader (term 3)", "SET x = 5"], ["Leader (term 3)", "F1", "AppendEntries(index 8, x = 5)"], ["Leader (term 3)", "F2", "AppendEntries"], ["Leader (term 3)", "F3", "AppendEntries"], ["F1", "Leader (term 3)", "ack", "r"], ["F2", "Leader (term 3)", "ack", "r", "Leader + 2 followers = 3 of 5, a majority: the entry is committed."],
       ["Leader (term 3)", "Client", "OK", "r"], ["Leader (term 3)", "F3", "commit index = 8 (next heartbeat)"]]),
  CALC("Fault tolerance", [("Nodes", "n = 5", ""), ("Majority needed", "n // 2 + 1", ""), ("Crashes tolerated", "n - (n // 2 + 1)", "", "3 nodes tolerate 1; 5 tolerate 2; even numbers add no tolerance")]))

X("leader-election",
  SEQ("Lease-based election with etcd", ["Node A", "etcd", "Node B"],
      [["Node A", "etcd", "create /leader = A with lease 10 s (if absent)"], ["etcd", "Node A", "success → A is leader", "r"], ["Node B", "etcd", "create /leader = B"], ["etcd", "Node B", "exists → B watches the key", "r"],
       ["Node A", "etcd", "keep-alive every 3 s"], NOTE(["Node A"], "A freezes (GC pause) for 15 s"), ["etcd", "Node B", "lease expired: key deleted", "a"], ["Node B", "etcd", "create /leader = B → leader"],
       ["Node A", "Node A", "wakes up still thinking it's leader!", "", "Split brain risk. Fix: fencing tokens (next card) and A checking its lease before acting."]]),
  TABLE("Approaches", ["Method", "How", "Example"], [["Consensus algorithm", "Raft/Paxos built into the system", "etcd, Kafka KRaft"], ["Coordination service", "ephemeral node / lease", "ZooKeeper, etcd, Consul"], ["Database lock", "row with expiry / advisory lock", "small systems"], ["Bully / ring", "highest id wins (classic)", "textbooks"]]))

X("distributed-locks",
  SEQ("Fencing tokens prevent a stale lock holder from doing damage", ["Client 1", "Lock service", "Client 2", "Storage"],
      [["Client 1", "Lock service", "acquire lock"], ["Lock service", "Client 1", "granted, token 33", "r"], NOTE(["Client 1"], "long GC pause; lock expires"), ["Client 2", "Lock service", "acquire lock"], ["Lock service", "Client 2", "granted, token 34", "r"],
       ["Client 2", "Storage", "write (token 34)"], ["Client 1", "Storage", "write (token 33)"], ["Storage", "Client 1", "rejected: 33 < 34 already seen", "r", "Storage only accepts increasing tokens, so the stale holder can't corrupt data."]]),
  CODE("Redis lock: acquire and safe release", """SET lock:order:987 <random-uuid> NX PX 30000      -- only if absent, 30 s expiry

-- release only if we still own it (atomic Lua)
if redis.call("GET", KEYS[1]) == ARGV[1] then
  return redis.call("DEL", KEYS[1])
else
  return 0
end""", "lua"),
  KEY("For efficiency (avoid duplicate work) a Redis lock is fine. For correctness (money, inventory) use a consensus-backed lock (etcd/ZooKeeper) **plus** fencing tokens, or avoid locks with conditional writes (`UPDATE … WHERE version = 7`).", "Efficiency vs correctness"))

X("gossip",
  P("In gossip, every second each node tells a few random peers what it knows (membership, heartbeats, versions). Information spreads like a rumour: exponentially."),
  TABLE("Rumour spread with fan-out 2 (1,000 nodes)", ["Round", "Nodes informed (approx)"], [["0", "1"], ["1", "3"], ["2", "9"], ["3", "27"], ["4", "81"], ["5", "243"], ["6", "729"], ["7", "≈ 1,000 (all)"]], "≈ log₃(1000) ≈ 7 rounds: a few seconds for a whole cluster."),
  TABLE("Failure detection via gossip (heartbeat counters)", ["Node", "Heartbeat counter last seen", "Last updated", "Status"], [["A", "1042", "now", "alive"], ["B", "988", "1 s ago", "alive"], ["C", "731", "12 s ago", "suspect → dead after 30 s"]]),
  KEY("Used by Cassandra, Consul (SWIM), DynamoDB-style stores, Redis Cluster. No central server, robust to failures, but convergence is eventual.", "Where you'll see it"))

X("merkle-anti-entropy",
  P("Two replicas hold millions of keys. Instead of comparing every key, each builds a **Merkle tree**: leaves are hashes of key ranges, parents hash their children. Compare roots; descend only into subtrees that differ."),
  FLOW("Merkle tree comparison", [["Root A = H(H12, H34)  ≠  Root B"], ["H12 equal ✔", "H34 differs ✘"], ["(skip range 1–2)", "H3 equal ✔", "H4 differs ✘ → sync keys in range 4 only"]],
       [["Root A = H(H12, H34)  ≠  Root B", "H12 equal ✔"], ["Root A = H(H12, H34)  ≠  Root B", "H34 differs ✘"], ["H12 equal ✔", "(skip range 1–2)"], ["H34 differs ✘", "H3 equal ✔"], ["H34 differs ✘", "H4 differs ✘ → sync keys in range 4 only"]]),
  CALC("Work saved", [("Keys per replica", "k = 1e8", ""), ("Leaf ranges (tree leaves)", "l = 2**15", ""), ("Keys per leaf range", "k / l", ""), ("Hash comparisons to find 1 differing range (tree depth)", "15 * 2", "", "vs comparing 100 million keys")]),
  KEY("Also used by Git, BitTorrent, blockchains, and Cassandra/Dynamo anti-entropy repair.", "Where else"))

X("crdt",
  P("A CRDT (conflict-free replicated data type) is a data structure designed so that replicas can update independently and **always merge to the same result**, in any order, without coordination."),
  TABLE("G-Counter (grow-only counter): likes on two replicas", ["Step", "Replica A vector", "Replica B vector", "Value"],
        [["start", "{A:0, B:0}", "{A:0, B:0}", "0"], ["3 likes on A", "{A:3, B:0}", "", "3 on A"], ["2 likes on B", "", "{A:0, B:2}", "2 on B"], ["merge = per-slot max", "{A:3, B:2}", "{A:3, B:2}", "5 on both ✔"]],
        "Merging is max per slot, so it's commutative, associative and idempotent: duplicate or reordered syncs are harmless."),
  TABLE("Common CRDTs", ["CRDT", "Supports", "Used for"], [["G-Counter / PN-Counter", "increment / increment + decrement", "likes, inventory estimates"], ["G-Set / OR-Set", "add / add + remove", "shopping carts, tags"], ["LWW-Register", "last write wins by timestamp", "profile fields"], ["RGA / sequence CRDTs", "collaborative text", "Figma-like/Google-Docs-like editors (Yjs, Automerge)"]]))

X("byzantine",
  P("**Crash faults**: a node stops. **Byzantine faults**: a node lies or behaves arbitrarily (bug, hacked, malicious). Tolerating f Byzantine nodes needs **3f + 1** nodes, versus 2f + 1 for crashes."),
  CALC("Nodes needed to tolerate f faulty nodes", [("f", "f = 1", ""), ("Crash-fault tolerant (Raft/Paxos)", "2 * f + 1", ""), ("Byzantine-fault tolerant (PBFT)", "3 * f + 1", ""), ("f = 3: crash vs Byzantine", "2 * 3 + 1", "", "vs 10 for Byzantine")]),
  TABLE("Where each applies", ["Setting", "Fault model", "Why"], [["your company's datacenter", "crash faults", "you trust your own nodes"], ["blockchains (open membership)", "Byzantine (PoW/PoS, PBFT)", "anyone can join and lie"], ["aircraft / spacecraft controllers", "Byzantine", "hardware can send corrupt values"]]))

X("unique-id",
  P("Auto-increment IDs need one central database. Distributed systems generate IDs locally. **Snowflake** packs time, machine and a counter into 64 bits:"),
  TABLE("Snowflake 64-bit layout", ["Bits", "Field", "Capacity"], [["1", "sign (always 0)", ""], ["41", "milliseconds since custom epoch", "~69 years"], ["10", "machine id", "1,024 machines"], ["12", "sequence within the ms", "4,096 ids per ms per machine"]]),
  CALC("Capacity", [("Ids per second per machine", "4096 * 1000", "/s"), ("Ids per second, whole fleet", "4096 * 1000 * 1024", "/s"), ("Years before the timestamp overflows", "2**41 / (1000 * 3600 * 24 * 365)", "years")]),
  TABLE("Options compared", ["Option", "Sortable by time", "Size", "Coordination", "Notes"], [["DB auto-increment", "✔", "8 B", "central DB", "simple, single point"], ["UUID v4", "✘", "16 B", "none", "random → poor B-tree locality"],
        ["UUID v7 / ULID", "✔", "16 B", "none", "time-prefixed random"], ["Snowflake", "✔", "8 B", "assign machine ids", "clock going backwards must be handled"], ["Ticket server / ranges", "≈", "8 B", "hand out blocks of 1,000", "Flickr-style"]]))

X("bloom-filter",
  P("A Bloom filter answers 'have I seen x?' with **no false negatives** and a small chance of false positives, using a bit array and k hash functions, in a tiny fraction of the memory of a set."),
  TABLE("10-bit filter, k = 2 hashes", ["Action", "h1", "h2", "Bits set after (positions)"], [["add 'cat'", "1", "4", "1, 4"], ["add 'dog'", "4", "7", "1, 4, 7"], ["check 'cow'", "1", "7", "both set → 'probably yes' (false positive!)"], ["check 'emu'", "2", "7", "bit 2 is 0 → definitely not"]]),
  CALC("Sizing for 1 billion items at 1% false positives", [("Items", "n = 1e9", ""), ("Target false-positive rate", "p = 0.01", ""), ("Bits needed m = −n·ln p / (ln 2)²", "-n * math.log(p) / (math.log(2) ** 2)", ""), ("Memory", "-n * math.log(p) / (math.log(2) ** 2) / 8", "B", "vs ~tens of GB for a hash set of URLs"),
                                                             ("Optimal hash count k = (m/n)·ln 2", "(-math.log(p) / (math.log(2) ** 2)) * math.log(2)", "")]),
  KEY("Uses: skip disk reads for absent keys (Cassandra/RocksDB SSTables), crawler 'seen URL', username-taken pre-check, malicious-URL lists. You can't delete from a plain Bloom filter (use a counting Bloom filter).", "Where it's used"))

X("hyperloglog",
  P("HyperLogLog counts **distinct** items (unique visitors) in ~12 KB with ~0.8% error, however many items there are. Intuition: in random hashes, seeing a hash that starts with many zeros is rare, so the longest run of leading zeros hints at how many distinct values you've seen."),
  TABLE("Intuition with coin flips", ["Longest leading-zero run seen", "Rough distinct count it suggests"], [["1", "~2"], ["5", "~32"], ["10", "~1,000"], ["20", "~1 million"]], "HLL averages this estimate over 16,384 buckets to cut the variance."),
  CALC("Memory: exact set vs HyperLogLog", [("Unique visitors", "u = 50e6", ""), ("Exact set of 16-byte ids", "u * 16", "B"), ("HyperLogLog (Redis PFADD)", "12 * 1024", "B"), ("Standard error 1.04/√m, m = 16384", "1.04 / math.sqrt(16384) * 100", "%")]),
  CODE("Redis", """PFADD visitors:2026-11-26 user42 user77 user42
PFCOUNT visitors:2026-11-26                        -- 2
PFMERGE visitors:week visitors:2026-11-20 … visitors:2026-11-26""", "text"))

X("geohash-quadtree",
  P("To find 'drivers near me' fast, map 2-D locations to something indexable. **Geohash** interleaves latitude/longitude bits into a string; nearby points share prefixes. A **quadtree** splits a region into 4 until each cell has few points."),
  TABLE("Geohash precision", ["Length", "Cell size (approx)", "Use"], [["4", "39 km × 20 km", "city"], ["5", "4.9 km × 4.9 km", "neighbourhood"], ["6", "1.2 km × 0.6 km", "nearby drivers"], ["7", "153 m × 153 m", "street"], ["8", "38 m × 19 m", "building"]]),
  SEQ("Nearby search with geohash", ["Rider app", "Location service", "Redis / DB"],
      [["Rider app", "Location service", "drivers near (18.52, 73.85)?"], ["Location service", "Location service", "geohash6 = 'te7ud2'"], ["Location service", "Redis / DB", "fetch drivers in te7ud2 + its 8 neighbours", "", "Neighbours are needed because a driver 50 m away may sit in the next cell."],
       ["Redis / DB", "Location service", "37 candidates", "r"], ["Location service", "Rider app", "sort by exact distance → nearest 10", "r"]]),
  TABLE("Geohash vs quadtree vs H3", ["", "Geohash", "Quadtree", "H3 (Uber)"], [["structure", "fixed grid, string prefix", "adaptive tree (dense areas split more)", "hexagonal grid"], ["storage", "any DB index", "in-memory tree", "64-bit cell ids"], ["strength", "simple, works in any KV store", "handles uneven density", "uniform neighbour distances"]]))

X("trie-structures",
  P("A trie stores strings by character; all words with the same prefix share a path. Typeahead stores at each node the **top-k completions** so a lookup is just a walk down the prefix."),
  FLOW("Trie for: car, cat, cart, dog (top completions cached per node)", [["root"], ["c (top: car, cat, cart)", "d (top: dog)"], ["a"], ["r ✔ (car)", "t ✔ (cat)"], ["t ✔ (cart)"]],
       [["root", "c (top: car, cat, cart)"], ["root", "d (top: dog)"], ["c (top: car, cat, cart)", "a"], ["a", "r ✔ (car)"], ["a", "t ✔ (cat)"], ["r ✔ (car)", "t ✔ (cart)"]]),
  TABLE("Typing 'ca'", ["Step", "Work"], [["walk root → c → a", "2 steps (length of prefix)"], ["read cached top-k at node 'a'", "O(1): car, cat, cart"], ["without caching", "DFS the whole subtree, which could be millions of words"]]),
  KEY("At scale: build the trie offline from query logs (weekly + hourly deltas), shard by prefix, serve from memory, and cache popular prefixes at the CDN/browser. See the typeahead HLD question.", "Production design"))
