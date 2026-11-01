# NexusKV

A distributed, fault-tolerant key-value store built from scratch in Java 21, as the flagship project of my 30-day DSA and System Design plan.

**Status:** Day 1 - Maven multi-module skeleton, `KeyValueStore` interface, HashMap-backed `InMemoryStore`, JUnit 5 tests.

## Modules
| Module | Purpose |
|---|---|
| `nexuskv-core` | Storage engine: in-memory store now; LRU cache, skip-list memtable, WAL, SSTables, Bloom filters, compaction later |
| `nexuskv-server` | Networking (Java NIO TCP server from Day 21), replication and clustering |

## Build and test
```bash
cd nexuskv
mvn test                                     # runs JUnit 5 tests
mvn -q package && java -cp nexuskv-server/target/classes:nexuskv-core/target/classes io.nexuskv.server.NexusKvApp
```
Needs JDK 21 and Maven 3.9+.

## Roadmap
Day 6 LRU cache · Day 7 skip-list memtable · Day 10 K-way merge · Day 11 Bloom filter · Day 14 WAL + SSTables · Day 18 compaction · Day 21 NIO server · Day 22 Command/Strategy refactor · Day 23 thread safety + JMH · Day 25 consistent hashing · Day 26 replication + leader election · Day 28 Docker, CI, dashboard
