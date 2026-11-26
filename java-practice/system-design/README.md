# System Design in Java: practice programs

One runnable program for every System Design concept card and HLD question on the board. Each file is self-contained (no libraries).

Run any of them with Java 17 or newer:

```
java 03-databases-storage/ConsistentHashingDemo.java
```

Each card on the board shows the same code, its real output, and 3 practice exercises. Change the code, predict the output, then run it.

## Fundamentals

- [SystemGrowthDemo.java](01-fundamentals/SystemGrowthDemo.java): What is system design?
- [ClientServerDemo.java](01-fundamentals/ClientServerDemo.java): Client–server model
- [UrlJourneyDemo.java](01-fundamentals/UrlJourneyDemo.java): What happens when you type a URL and press Enter
- [LatencyThroughputDemo.java](01-fundamentals/LatencyThroughputDemo.java): Latency, throughput and bandwidth
- [ScalabilityDemo.java](01-fundamentals/ScalabilityDemo.java): Scalability: vertical vs horizontal
- [AvailabilityDemo.java](01-fundamentals/AvailabilityDemo.java): Availability, the 'nines' and SLAs
- [ReliabilityDemo.java](01-fundamentals/ReliabilityDemo.java): Reliability, durability, fault tolerance, resilience
- [EstimationDemo.java](01-fundamentals/EstimationDemo.java): Back-of-the-envelope estimation
- [LatencyNumbersDemo.java](01-fundamentals/LatencyNumbersDemo.java): Latency numbers every engineer should know
- [QueueingDemo.java](01-fundamentals/QueueingDemo.java): Performance vs scalability, and how systems fail under load
- [CapDemo.java](01-fundamentals/CapDemo.java): Consistency vs availability: a first look
- [EncapsulationDemo.java](01-fundamentals/EncapsulationDemo.java): Network layers: OSI and TCP/IP models
- [DnsResolverDemo.java](01-fundamentals/DnsResolverDemo.java): IP addresses and DNS
- [TcpUdpDemo.java](01-fundamentals/TcpUdpDemo.java): TCP vs UDP
- [HttpDemo.java](01-fundamentals/HttpDemo.java): HTTP: methods, status codes, headers, versions
- [TlsHandshakeDemo.java](01-fundamentals/TlsHandshakeDemo.java): HTTPS and TLS: how encryption on the web works
- [RestApiDemo.java](01-fundamentals/RestApiDemo.java): REST API design
- [RpcDemo.java](01-fundamentals/RpcDemo.java): RPC and gRPC
- [GraphQlDemo.java](01-fundamentals/GraphQlDemo.java): GraphQL
- [RealtimeDemo.java](01-fundamentals/RealtimeDemo.java): Real-time communication: polling, long polling, WebSockets, SSE, webhooks
- [ApiGatewayDemo.java](01-fundamentals/ApiGatewayDemo.java): API gateway
- [ProxyDemo.java](01-fundamentals/ProxyDemo.java): Forward proxy vs reverse proxy
- [RateLimiterAlgorithmsDemo.java](01-fundamentals/RateLimiterAlgorithmsDemo.java): Rate limiting algorithms

## Building blocks

- [LoadBalancerDemo.java](02-building-blocks/LoadBalancerDemo.java): Load balancers
- [LbAlgorithmsDemo.java](02-building-blocks/LbAlgorithmsDemo.java): Load-balancing algorithms
- [CdnDemo.java](02-building-blocks/CdnDemo.java): CDN (Content Delivery Network)
- [CachingDemo.java](02-building-blocks/CachingDemo.java): Caching: the basics
- [CacheStrategiesDemo.java](02-building-blocks/CacheStrategiesDemo.java): Cache read/write strategies
- [CacheEvictionDemo.java](02-building-blocks/CacheEvictionDemo.java): Cache eviction policies
- [CacheProblemsDemo.java](02-building-blocks/CacheProblemsDemo.java): Cache problems: stampede, penetration, avalanche, hot keys, consistency
- [MiniRedisDemo.java](02-building-blocks/MiniRedisDemo.java): Redis vs Memcached, and distributed caches
- [MessageQueueDemo.java](02-building-blocks/MessageQueueDemo.java): Message queues
- [MiniKafkaDemo.java](02-building-blocks/MiniKafkaDemo.java): Kafka and log-based streaming
- [DeliverySemanticsDemo.java](02-building-blocks/DeliverySemanticsDemo.java): Delivery guarantees: at-most-once, at-least-once, exactly-once
- [BackpressureDemo.java](02-building-blocks/BackpressureDemo.java): Backpressure, load shedding and dead-letter queues
- [StreamWindowsDemo.java](02-building-blocks/StreamWindowsDemo.java): Batch vs stream processing (MapReduce, Spark, Flink)
- [SchedulerDemo.java](02-building-blocks/SchedulerDemo.java): Job schedulers, cron and delayed tasks
- [ObjectStoreDemo.java](02-building-blocks/ObjectStoreDemo.java): Block, file and object storage
- [InvertedIndexDemo.java](02-building-blocks/InvertedIndexDemo.java): Search systems and inverted indexes (Elasticsearch)
- [ColumnStoreDemo.java](02-building-blocks/ColumnStoreDemo.java): Time-series databases, data warehouses and OLAP

## Databases storage

- [SqlVsNoSqlDemo.java](03-databases-storage/SqlVsNoSqlDemo.java): SQL vs NoSQL
- [AcidDemo.java](03-databases-storage/AcidDemo.java): ACID transactions
- [IsolationDemo.java](03-databases-storage/IsolationDemo.java): Isolation levels and concurrency anomalies
- [IndexDemo.java](03-databases-storage/IndexDemo.java): Database indexes (B-tree, hash, composite, covering)
- [LsmTreeDemo.java](03-databases-storage/LsmTreeDemo.java): Storage engines: B-tree vs LSM tree, WAL
- [NoSqlTypesDemo.java](03-databases-storage/NoSqlTypesDemo.java): NoSQL families: key–value, document, wide-column, graph
- [NormalizationDemo.java](03-databases-storage/NormalizationDemo.java): Normalization vs denormalization
- [ReplicationDemo.java](03-databases-storage/ReplicationDemo.java): Replication: leader–follower, multi-leader, leaderless
- [ShardingDemo.java](03-databases-storage/ShardingDemo.java): Partitioning and sharding
- [ConsistentHashingDemo.java](03-databases-storage/ConsistentHashingDemo.java): Consistent hashing
- [DbScalingPathDemo.java](03-databases-storage/DbScalingPathDemo.java): How to scale a database step by step
- [ConnectionPoolDemo.java](03-databases-storage/ConnectionPoolDemo.java): Connection pooling and N+1 queries
- [SagaDemo.java](03-databases-storage/SagaDemo.java): Distributed transactions: 2PC, 3PC, Saga, outbox
- [CdcDemo.java](03-databases-storage/CdcDemo.java): Change Data Capture (CDC)
- [BlobMetadataDemo.java](03-databases-storage/BlobMetadataDemo.java): Storing files: blob store + metadata DB

## Distributed systems

- [UnreliableNetworkDemo.java](04-distributed-systems/UnreliableNetworkDemo.java): Why distributed systems are hard: the 8 fallacies, two generals
- [CapChoiceDemo.java](04-distributed-systems/CapChoiceDemo.java): CAP theorem
- [PacelcDemo.java](04-distributed-systems/PacelcDemo.java): PACELC theorem
- [ConsistencyModelsDemo.java](04-distributed-systems/ConsistencyModelsDemo.java): Consistency models: strong, eventual, causal and more
- [QuorumDemo.java](04-distributed-systems/QuorumDemo.java): Quorums: N, R, W
- [LamportClockDemo.java](04-distributed-systems/LamportClockDemo.java): Time in distributed systems: clock skew, NTP, Lamport and vector clocks, HLC, TrueTime
- [VectorClockDemo.java](04-distributed-systems/VectorClockDemo.java): Conflict resolution: LWW, vector clocks, merges
- [RaftLiteDemo.java](04-distributed-systems/RaftLiteDemo.java): Consensus: Paxos and Raft
- [LeaseElectionDemo.java](04-distributed-systems/LeaseElectionDemo.java): Leader election and coordination services (ZooKeeper, etcd)
- [DistributedLockDemo.java](04-distributed-systems/DistributedLockDemo.java): Distributed locks and fencing tokens
- [GossipDemo.java](04-distributed-systems/GossipDemo.java): Gossip protocols and failure detection
- [MerkleTreeDemo.java](04-distributed-systems/MerkleTreeDemo.java): Merkle trees, anti-entropy, read repair, hinted handoff
- [CrdtDemo.java](04-distributed-systems/CrdtDemo.java): CRDTs (conflict-free replicated data types)
- [ByzantineDemo.java](04-distributed-systems/ByzantineDemo.java): Crash faults vs Byzantine faults
- [SnowflakeDemo.java](04-distributed-systems/SnowflakeDemo.java): Generating unique IDs at scale (UUID, Snowflake, ticket servers)
- [BloomFilterDemo.java](04-distributed-systems/BloomFilterDemo.java): Bloom filters
- [HyperLogLogDemo.java](04-distributed-systems/HyperLogLogDemo.java): HyperLogLog and Count-Min Sketch
- [GeohashDemo.java](04-distributed-systems/GeohashDemo.java): Geospatial indexing: geohash, quadtree, S2, H3
- [TypeaheadTrieDemo.java](04-distributed-systems/TypeaheadTrieDemo.java): Tries, skip lists and other structures inside systems

## Architecture reliability

- [MonolithVsMicroservicesDemo.java](05-architecture-reliability/MonolithVsMicroservicesDemo.java): Monolith vs microservices vs modular monolith
- [ServiceDiscoveryDemo.java](05-architecture-reliability/ServiceDiscoveryDemo.java): Service discovery
- [SidecarDemo.java](05-architecture-reliability/SidecarDemo.java): Service mesh and the sidecar pattern
- [BffDemo.java](05-architecture-reliability/BffDemo.java): Backend for Frontend (BFF) and API composition
- [EventBusDemo.java](05-architecture-reliability/EventBusDemo.java): Event-driven architecture
- [EventSourcingDemo.java](05-architecture-reliability/EventSourcingDemo.java): Event sourcing
- [CqrsDemo.java](05-architecture-reliability/CqrsDemo.java): CQRS (Command Query Responsibility Segregation)
- [ServerlessVsContainersDemo.java](05-architecture-reliability/ServerlessVsContainersDemo.java): Containers, Kubernetes and serverless
- [ResilienceDemo.java](05-architecture-reliability/ResilienceDemo.java): Resilience patterns: timeouts, retries with backoff and jitter, circuit breaker, bulkhead, fallback
- [IdempotencyKeyDemo.java](05-architecture-reliability/IdempotencyKeyDemo.java): Idempotency
- [CanaryDeployDemo.java](05-architecture-reliability/CanaryDeployDemo.java): Deployment strategies: rolling, blue-green, canary, feature flags
- [MultiTenancyDemo.java](05-architecture-reliability/MultiTenancyDemo.java): Configuration, multi-tenancy and data residency
- [FailoverDemo.java](05-architecture-reliability/FailoverDemo.java): Redundancy, failover and multi-region design
- [DisasterRecoveryDemo.java](05-architecture-reliability/DisasterRecoveryDemo.java): Disaster recovery: RPO, RTO and backups
- [MonitoringDemo.java](05-architecture-reliability/MonitoringDemo.java): Observability: metrics, logs, traces and alerting
- [AutoscalerDemo.java](05-architecture-reliability/AutoscalerDemo.java): Autoscaling and capacity planning
- [ChaosDemo.java](05-architecture-reliability/ChaosDemo.java): Chaos engineering and game days
- [CostModelDemo.java](05-architecture-reliability/CostModelDemo.java): Cost awareness in design
- [AuthzDemo.java](05-architecture-reliability/AuthzDemo.java): Authentication vs authorization
- [JwtDemo.java](05-architecture-reliability/JwtDemo.java): Sessions vs tokens (JWT)
- [OAuthPkceDemo.java](05-architecture-reliability/OAuthPkceDemo.java): OAuth 2.0, OpenID Connect and SSO
- [EnvelopeEncryptionDemo.java](05-architecture-reliability/EnvelopeEncryptionDemo.java): Encryption at rest and in transit, hashing, key management
- [WebSecurityDemo.java](05-architecture-reliability/WebSecurityDemo.java): Web and API security: OWASP basics, DDoS, WAF, CORS

## Real world patterns

- [FeedFanoutDemo.java](06-real-world-patterns/FeedFanoutDemo.java): News feed: fan-out on write vs fan-out on read
- [CountersDemo.java](06-real-world-patterns/CountersDemo.java): Counting at scale: likes, views, followers
- [NotificationPipelineDemo.java](06-real-world-patterns/NotificationPipelineDemo.java): Notifications: push, SMS, email at scale
- [ChatDeliveryDemo.java](06-real-world-patterns/ChatDeliveryDemo.java): Chat delivery, presence and read receipts
- [AdaptiveBitrateDemo.java](06-real-world-patterns/AdaptiveBitrateDemo.java): Video upload and streaming: transcoding, adaptive bitrate, HLS/DASH
- [FileSyncDemo.java](06-real-world-patterns/FileSyncDemo.java): File sync: chunking, deduplication, delta sync
- [LedgerDemo.java](06-real-world-patterns/LedgerDemo.java): Payments: idempotency, double-entry ledgers, reconciliation
- [OversellingDemo.java](06-real-world-patterns/OversellingDemo.java): Inventory, flash sales and avoiding overselling
- [LeaderboardDemo.java](06-real-world-patterns/LeaderboardDemo.java): Leaderboards and ranking
- [PoliteCrawlerDemo.java](06-real-world-patterns/PoliteCrawlerDemo.java): Web crawling patterns
- [TwoStageRecsDemo.java](06-real-world-patterns/TwoStageRecsDemo.java): Recommendation and ML system design basics
- [RagPipelineDemo.java](06-real-world-patterns/RagPipelineDemo.java): Designing LLM / GenAI systems: RAG, vector databases, serving
- [ReadWriteHeavyDemo.java](06-real-world-patterns/ReadWriteHeavyDemo.java): Patterns for read-heavy vs write-heavy systems
- [HotspotDemo.java](06-real-world-patterns/HotspotDemo.java): Hot spots and the celebrity problem

## Lld oop

- [OopPillarsDemo.java](07-lld-oop/OopPillarsDemo.java): OOP: the four pillars
- [SolidDemo.java](07-lld-oop/SolidDemo.java): SOLID principles
- [UmlRelationshipsDemo.java](07-lld-oop/UmlRelationshipsDemo.java): UML class diagrams and relationships
- [CreationalPatternsDemo.java](07-lld-oop/CreationalPatternsDemo.java): Creational patterns: Singleton, Factory, Abstract Factory, Builder, Prototype
- [StructuralPatternsDemo.java](07-lld-oop/StructuralPatternsDemo.java): Structural patterns: Adapter, Decorator, Facade, Proxy, Composite, Bridge, Flyweight
- [BehavioralPatternsDemo.java](07-lld-oop/BehavioralPatternsDemo.java): Behavioural patterns: Strategy, Observer, Command, State, Template, Chain of Responsibility, Iterator, Mediator, Memento, Visitor
- [ConcurrencyDemo.java](07-lld-oop/ConcurrencyDemo.java): Concurrency in Java for LLD
- [LldApproachDemo.java](07-lld-oop/LldApproachDemo.java): How to answer a low-level design (machine coding) round
- [ApiContractDemo.java](07-lld-oop/ApiContractDemo.java): Designing clean APIs and models inside a service

## Hld questions

- [UrlShortenerSystem.java](08-hld-questions/UrlShortenerSystem.java): Design a URL shortener (TinyURL / bit.ly)
- [PastebinSystem.java](08-hld-questions/PastebinSystem.java): Design Pastebin / GitHub Gist
- [DistributedRateLimiterSystem.java](08-hld-questions/DistributedRateLimiterSystem.java): Design a distributed rate limiter
- [IdGeneratorSystem.java](08-hld-questions/IdGeneratorSystem.java): Design a unique ID generator for a distributed system
- [KeyValueStoreSystem.java](08-hld-questions/KeyValueStoreSystem.java): Design a distributed key–value store (like DynamoDB / Cassandra)
- [DistributedCacheSystem.java](08-hld-questions/DistributedCacheSystem.java): Design a distributed cache (like Redis Cluster / Memcached)
- [WebCrawlerSystem.java](08-hld-questions/WebCrawlerSystem.java): Design a web crawler
- [NotificationSystem.java](08-hld-questions/NotificationSystem.java): Design a notification system (push, SMS, email)
- [NewsFeedSystem.java](08-hld-questions/NewsFeedSystem.java): Design a news feed (Facebook / LinkedIn)
- [TwitterSystem.java](08-hld-questions/TwitterSystem.java): Design Twitter / X
- [InstagramSystem.java](08-hld-questions/InstagramSystem.java): Design Instagram
- [ChatSystem.java](08-hld-questions/ChatSystem.java): Design a chat system (WhatsApp / Messenger / Slack)
- [AutocompleteSystem.java](08-hld-questions/AutocompleteSystem.java): Design search autocomplete / typeahead
- [VideoPlatformSystem.java](08-hld-questions/VideoPlatformSystem.java): Design YouTube / Netflix (video streaming)
- [FileStorageSyncSystem.java](08-hld-questions/FileStorageSyncSystem.java): Design Google Drive / Dropbox (file storage and sync)
- [ProximityServiceSystem.java](08-hld-questions/ProximityServiceSystem.java): Design a proximity service (Yelp / nearby restaurants)
- [RideHailingSystem.java](08-hld-questions/RideHailingSystem.java): Design Uber / Ola (ride hailing)
- [SeatBookingSystem.java](08-hld-questions/SeatBookingSystem.java): Design BookMyShow / Ticketmaster (seat booking)
- [EcommerceCheckoutSystem.java](08-hld-questions/EcommerceCheckoutSystem.java): Design Amazon / Flipkart (e-commerce checkout)
- [PaymentSystem.java](08-hld-questions/PaymentSystem.java): Design a payment system (Stripe / Razorpay / Amazon Pay)
- [HotelReservationSystem.java](08-hld-questions/HotelReservationSystem.java): Design a hotel / Airbnb reservation system
- [MetricsMonitoringSystem.java](08-hld-questions/MetricsMonitoringSystem.java): Design a metrics monitoring and alerting system (Datadog / Prometheus)
- [LoggingSystem.java](08-hld-questions/LoggingSystem.java): Design a distributed logging system (ELK / Splunk)
- [TopKTrendingSystem.java](08-hld-questions/TopKTrendingSystem.java): Design top-K / trending (most viewed videos, trending hashtags)
- [AdClickAggregationSystem.java](08-hld-questions/AdClickAggregationSystem.java): Design an ad click aggregation system
- [DistributedJobSchedulerSystem.java](08-hld-questions/DistributedJobSchedulerSystem.java): Design a distributed job scheduler (cron at scale)
- [EmailServiceSystem.java](08-hld-questions/EmailServiceSystem.java): Design an email service (Gmail)
- [ObjectStorageSystem.java](08-hld-questions/ObjectStorageSystem.java): Design an object storage system (Amazon S3)
- [FoodDeliverySystem.java](08-hld-questions/FoodDeliverySystem.java): Design Swiggy / Zomato / DoorDash (food delivery)
- [OnlineJudgeSystem.java](08-hld-questions/OnlineJudgeSystem.java): Design LeetCode / an online judge
- [GamingLeaderboardSystem.java](08-hld-questions/GamingLeaderboardSystem.java): Design a real-time gaming leaderboard
- [CollaborativeEditingSystem.java](08-hld-questions/CollaborativeEditingSystem.java): Design Google Docs (collaborative editing)
- [SearchEngineSystem.java](08-hld-questions/SearchEngineSystem.java): Design a web search engine (Google Search)
- [MatchingEngineSystem.java](08-hld-questions/MatchingEngineSystem.java): Design a stock exchange / trading order matching system
- [DistributedLogQueueSystem.java](08-hld-questions/DistributedLogQueueSystem.java): Design a distributed message queue (like Kafka)
- [MapsRoutingSystem.java](08-hld-questions/MapsRoutingSystem.java): Design Google Maps (routing and navigation)
- [VideoConferencingSystem.java](08-hld-questions/VideoConferencingSystem.java): Design a video conferencing system (Zoom / Google Meet)
- [MusicStreamingSystem.java](08-hld-questions/MusicStreamingSystem.java): Design Spotify (music streaming)
- [MatchingSwipeSystem.java](08-hld-questions/MatchingSwipeSystem.java): Design Tinder (matching and swiping)
- [DistributedTracingSystem.java](08-hld-questions/DistributedTracingSystem.java): Design a distributed tracing system (Jaeger / Zipkin)
- [LlmServingSystem.java](08-hld-questions/LlmServingSystem.java): Design ChatGPT / an LLM chat service
- [DistributedFileSystemSystem.java](08-hld-questions/DistributedFileSystemSystem.java): Design a distributed file system (GFS / HDFS)
- [VotingRankingSystem.java](08-hld-questions/VotingRankingSystem.java): Design Reddit / Quora / Hacker News (posts, votes, ranking)
- [NewsAggregatorSystem.java](08-hld-questions/NewsAggregatorSystem.java): Design Google News (news aggregator)
- [DigitalWalletSystem.java](08-hld-questions/DigitalWalletSystem.java): Design a digital wallet / UPI payments app (PhonePe / Paytm / Google Pay)
- [AuctionSystem.java](08-hld-questions/AuctionSystem.java): Design an online auction system (eBay)
- [CalendarSchedulingSystem.java](08-hld-questions/CalendarSchedulingSystem.java): Design Google Calendar / Outlook meeting scheduling
- [CdnSystem.java](08-hld-questions/CdnSystem.java): Design a CDN (content delivery network)
- [PriceAlertSystem.java](08-hld-questions/PriceAlertSystem.java): Design a price tracker / price-drop alert system (stocks, flights, products)
