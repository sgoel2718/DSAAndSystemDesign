"""Company tags and 'how often asked' tiers for the conceptual Q&A bank.
Companies: where this kind of question is commonly reported (topic defaults + keyword overrides).
Frequency: 'Very common' = staple questions that appear in almost every prep list and interview report;
'Common' = regularly asked; 'Sometimes' = senior/deep-dive questions asked less often."""

TOPIC_COMPANIES = {
    "Fundamentals": ["Google", "Amazon", "Microsoft", "Meta"],
    "Networking": ["Google", "Microsoft", "Cloudflare"],
    "APIs": ["Stripe", "Amazon", "Microsoft"],
    "Load balancing": ["Google", "Amazon", "Microsoft"],
    "Caching": ["Amazon", "Meta", "Flipkart", "Twitter"],
    "Databases": ["Google", "Uber", "Flipkart", "Microsoft"],
    "Async": ["LinkedIn", "Uber", "Amazon", "Confluent"],
    "Storage": ["Amazon", "Dropbox", "Google"],
    "Security": ["Microsoft", "PayPal", "Google"],
    "Estimation": ["Google", "Meta", "Amazon"],
    "LLD": ["Flipkart", "Amazon", "Microsoft", "Uber", "Swiggy"],
    "Distributed": ["Google", "Microsoft", "Uber", "Netflix"],
    "Architecture": ["Netflix", "Uber", "Amazon", "Microsoft"],
    "Reliability": ["Google", "Netflix", "Microsoft"],
    "Patterns": ["Meta", "Uber", "Twitter", "Google"],
    "Transactions": ["Stripe", "Goldman Sachs", "Razorpay", "Amazon"],
    "Data": ["Google", "Uber", "LinkedIn"],
    "Streaming": ["Meta", "Uber", "LinkedIn", "Google"],
    "Scale": ["Google", "Meta", "Uber"],
    "Search": ["Google", "Microsoft", "LinkedIn"],
    "GenAI": ["OpenAI", "Microsoft", "Google", "Anthropic", "NVIDIA"],
}

KEYWORD_COMPANIES = [
    (("spanner", "truetime"), ["Google"]),
    (("payment", "invoice", "billing"), ["Amazon", "Stripe", "Razorpay", "PayPal"]),
    (("chat", "whatsapp", "read receipt", "end-to-end"), ["Meta", "Microsoft", "Amazon"]),
    (("feed", "celebrity", "social graph", "fan-out"), ["Meta", "Twitter", "LinkedIn", "Google"]),
    (("seat", "booking"), ["Amazon", "BookMyShow", "Microsoft"]),
    (("flash sale",), ["Flipkart", "Amazon", "Walmart"]),
    (("click",), ["Google", "Meta", "Amazon"]),
    (("dropbox",), ["Dropbox", "Google", "Microsoft"]),
    (("bitrate", "video"), ["Netflix", "Google", "Amazon"]),
    (("nearby", "geohash", "quadtree"), ["Uber", "Swiggy", "Google"]),
    (("url shortener", "base62", "301 vs 302"), ["Amazon", "Google", "Microsoft"]),
    (("kafka",), ["LinkedIn", "Uber", "Amazon", "Confluent"]),
    (("trending", "top-k"), ["Twitter", "Google", "Meta"]),
    (("search engine", "shards fast"), ["Google", "Microsoft"]),
    (("mysql", "migration"), ["Uber", "Amazon", "Flipkart"]),
    (("websocket", "polling"), ["Meta", "Microsoft", "Slack"]),
    (("serverless", "cold start"), ["Amazon", "Microsoft"]),
    (("singleton", "parking", "strategy vs state", "builder"), ["Amazon", "Microsoft", "Flipkart", "Uber"]),
]

VERY_COMMON = [
    "horizontal and vertical scaling", "what happens when you type", "tcp vs udp", "sql vs nosql", "what is acid",
    "explain the cap theorem", "strong vs eventual", "consistent hashing", "what is sharding", "how do you choose a shard key",
    "compare cache-aside", "lru eviction", "what does a load balancer do", "l4 vs l7", "why use a message queue",
    "at-least-once vs exactly-once", "kafka guarantee ordering", "what is replication", "unique ids across many servers",
    "rest vs graphql", "monolith vs microservices", "what is a circuit breaker", "sessions vs jwt", "what is dns",
    "what is a cdn", "database index", "2pc vs saga", "fan-out on write", "polling vs long polling", "idempotent http methods",
    "solid", "equals() and hashcode()", "thread-safe in java", "strategy vs state", "concurrenthashmap",
    "cache stampede", "optimistic vs pessimistic", "prevent two users booking", "isolation levels", "rate limiting algorithm",
    "latency vs throughput", "99.99%", "single point of failure", "stateless", "transactional outbox", "idempotency for a payment",
]


def tag(q):
    text = (q["q"] + " " + q["a"]).lower()
    cos = list(TOPIC_COMPANIES.get(q["topic"], ["Amazon", "Google", "Microsoft"]))
    for kws, extra in KEYWORD_COMPANIES:
        if any(k in text for k in kws):
            cos = extra + [c for c in cos if c not in extra]
    qq = q["q"].lower()
    if any(k in qq for k in VERY_COMMON):
        freq = "Very common"
    else:
        freq = "Sometimes" if q["level"] == "Advanced" else "Common"
    return dict(q, companies=cos[:6], freq=freq)
