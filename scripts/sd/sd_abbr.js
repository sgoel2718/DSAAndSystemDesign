/* ================= Abbreviations: first use in each card/section shows "Full form (ABBR)" ================= */
const ABBR = {
  // web & networking
  API: "Application Programming Interface", CDN: "Content Delivery Network", URL: "Uniform Resource Locator", HTTP: "HyperText Transfer Protocol",
  HTTPS: "HyperText Transfer Protocol Secure", DNS: "Domain Name System", TLS: "Transport Layer Security", TCP: "Transmission Control Protocol",
  UDP: "User Datagram Protocol", IP: "Internet Protocol", QUIC: "Quick UDP Internet Connections", REST: "Representational State Transfer",
  RPC: "Remote Procedure Call", gRPC: "Google Remote Procedure Call", JSON: "JavaScript Object Notation", HTML: "HyperText Markup Language", CSS: "Cascading Style Sheets",
  JS: "JavaScript", XML: "Extensible Markup Language", YAML: "YAML Ain't Markup Language", SSE: "Server-Sent Events", WS: "WebSocket",
  TLD: "Top-Level Domain", ISP: "Internet Service Provider", NAT: "Network Address Translation", CIDR: "Classless Inter-Domain Routing",
  OSI: "Open Systems Interconnection", ICMP: "Internet Control Message Protocol", MAC: "Media Access Control", VPN: "Virtual Private Network",
  RTT: "Round-Trip Time", SYN: "Synchronize", ACK: "Acknowledgement", FIN: "Finish", SMTP: "Simple Mail Transfer Protocol",
  IMAP: "Internet Message Access Protocol", MX: "Mail Exchange", NS: "Name Server", CNAME: "Canonical Name", SRV: "Service record",
  TXT: "Text record", SSH: "Secure Shell", RTP: "Real-time Transport Protocol", SRTP: "Secure Real-time Transport Protocol", HPACK: "HTTP/2 header compression",
  WebRTC: "Web Real-Time Communication", SDP: "Session Description Protocol", ICE: "Interactive Connectivity Establishment",
  STUN: "Session Traversal Utilities for NAT", TURN: "Traversal Using Relays around NAT", SFU: "Selective Forwarding Unit", MCU: "Multipoint Control Unit",
  FEC: "Forward Error Correction", HLS: "HTTP Live Streaming", DASH: "Dynamic Adaptive Streaming over HTTP", ABR: "Adaptive Bitrate",
  MPEG: "Moving Picture Experts Group", RSS: "Really Simple Syndication", NTP: "Network Time Protocol", GPS: "Global Positioning System",
  GSLB: "Global Server Load Balancing", VRRP: "Virtual Router Redundancy Protocol", LVS: "Linux Virtual Server", NGINX: "Engine X web server",
  BFF: "Backend for Frontend", SDK: "Software Development Kit", CLI: "Command-Line Interface", UI: "User Interface", OTLP: "OpenTelemetry Protocol",
  // scale & reliability
  QPS: "Queries Per Second", RPS: "Requests Per Second", DAU: "Daily Active Users", MAU: "Monthly Active Users", SLA: "Service Level Agreement",
  SLO: "Service Level Objective", SLI: "Service Level Indicator", SRE: "Site Reliability Engineering", MTBF: "Mean Time Between Failures",
  MTTR: "Mean Time To Recovery", RPO: "Recovery Point Objective", RTO: "Recovery Time Objective", DR: "Disaster Recovery", SPOF: "Single Point Of Failure",
  HA: "High Availability", AZ: "Availability Zone", LB: "Load Balancer", ALB: "Application Load Balancer", NLB: "Network Load Balancer",
  ASG: "Auto Scaling Group", HPA: "Horizontal Pod Autoscaler", RED: "Rate, Errors, Duration", USE: "Utilisation, Saturation, Errors",
  ETA: "Estimated Time of Arrival", TTL: "Time To Live", P2P: "Peer-to-Peer", L1: "Level 1", L2: "Level 2", L3: "Layer 3", L4: "Layer 4", L7: "Layer 7",
  // hardware
  CPU: "Central Processing Unit", GPU: "Graphics Processing Unit", RAM: "Random-Access Memory", SSD: "Solid-State Drive", HDD: "Hard Disk Drive",
  IO: "Input/Output", OS: "Operating System", VM: "Virtual Machine", JVM: "Java Virtual Machine", GC: "Garbage Collection", ZGC: "Z Garbage Collector",
  NIO: "New Input/Output", KB: "Kilobyte", MB: "Megabyte", GB: "Gigabyte", TB: "Terabyte", PB: "Petabyte",
  // data
  DB: "Database", SQL: "Structured Query Language", NoSQL: "Not only SQL", KV: "Key–Value", ACID: "Atomicity, Consistency, Isolation, Durability",
  BASE: "Basically Available, Soft state, Eventually consistent", CAP: "Consistency, Availability, Partition tolerance",
  CP: "Consistent and Partition-tolerant", AP: "Available and Partition-tolerant", PACELC: "Partition: Availability or Consistency, Else: Latency or Consistency", OLTP: "Online Transaction Processing", OLAP: "Online Analytical Processing",
  ETL: "Extract, Transform, Load", ELT: "Extract, Load, Transform", CDC: "Change Data Capture", WAL: "Write-Ahead Log", LSM: "Log-Structured Merge",
  MVCC: "Multi-Version Concurrency Control", SSI: "Serializable Snapshot Isolation", ORM: "Object-Relational Mapping", CRUD: "Create, Read, Update, Delete",
  RDS: "Relational Database Service", RDB: "Redis Database snapshot", AOF: "Append-Only File", TSDB: "Time-Series Database",
  GSI: "Global Secondary Index", PK: "Primary Key", ID: "Identifier", UUID: "Universally Unique Identifier", ULID: "Universally Unique Lexicographically Sortable Identifier",
  CQRS: "Command Query Responsibility Segregation", CRDT: "Conflict-free Replicated Data Type", LWW: "Last-Write-Wins", HLC: "Hybrid Logical Clock",
  ISR: "In-Sync Replicas", DLQ: "Dead-Letter Queue", SQS: "Simple Queue Service", SNS: "Simple Notification Service", ZSET: "Sorted Set",
  BM25: "Best Matching 25", TF: "Term Frequency", IDF: "Inverse Document Frequency", HDFS: "Hadoop Distributed File System", GFS: "Google File System",
  S3: "Simple Storage Service", GCS: "Google Cloud Storage", EBS: "Elastic Block Store", EFS: "Elastic File System", NFS: "Network File System",
  DAG: "Directed Acyclic Graph", DTO: "Data Transfer Object", "2PC": "Two-Phase Commit", "3PC": "Three-Phase Commit", XA: "eXtended Architecture (distributed transactions)",
  FLP: "Fischer–Lynch–Paterson", PBFT: "Practical Byzantine Fault Tolerance", ZAB: "ZooKeeper Atomic Broadcast", SWIM: "Scalable Weakly-consistent Infection-style Membership",
  RGA: "Replicated Growable Array", HNSW: "Hierarchical Navigable Small World", IVF: "Inverted File index", ANN: "Approximate Nearest Neighbour",
  PN: "Positive–Negative", OT: "Operational Transformation", MD5: "Message Digest 5", SHA: "Secure Hash Algorithm", XOR: "Exclusive OR",
  // architecture & ops
  SOA: "Service-Oriented Architecture", ESB: "Enterprise Service Bus", CI: "Continuous Integration", CD: "Continuous Delivery", IAM: "Identity and Access Management",
  AWS: "Amazon Web Services", GCP: "Google Cloud Platform", ELK: "Elasticsearch, Logstash, Kibana", LMAX: "London Multi-Asset Exchange",
  STONITH: "Shoot The Other Node In The Head", MDC: "Mapped Diagnostic Context", E2E: "End-to-End", EV: "Electric Vehicle",
  // security
  JWT: "JSON Web Token", SSO: "Single Sign-On", OIDC: "OpenID Connect", SAML: "Security Assertion Markup Language", PKCE: "Proof Key for Code Exchange",
  MFA: "Multi-Factor Authentication", OTP: "One-Time Password", RBAC: "Role-Based Access Control", ABAC: "Attribute-Based Access Control",
  ACL: "Access Control List", KMS: "Key Management Service", AES: "Advanced Encryption Standard", RSA: "Rivest–Shamir–Adleman", ECC: "Elliptic-Curve Cryptography",
  ACM: "AWS Certificate Manager", GCM: "Galois/Counter Mode", WAF: "Web Application Firewall", DDoS: "Distributed Denial of Service",
  CSRF: "Cross-Site Request Forgery", XSS: "Cross-Site Scripting", CORS: "Cross-Origin Resource Sharing", CSP: "Content Security Policy",
  SSRF: "Server-Side Request Forgery", IDOR: "Insecure Direct Object Reference", OWASP: "Open Worldwide Application Security Project",
  PII: "Personally Identifiable Information", PCI: "Payment Card Industry", DSS: "Data Security Standard", GDPR: "General Data Protection Regulation",
  DPDP: "Digital Personal Data Protection", HIPAA: "Health Insurance Portability and Accountability Act", CAPTCHA: "Completely Automated Public Turing test to tell Computers and Humans Apart",
  SPF: "Sender Policy Framework", DKIM: "DomainKeys Identified Mail", DMARC: "Domain-based Message Authentication, Reporting and Conformance",
  DRM: "Digital Rights Management", X3DH: "Extended Triple Diffie–Hellman", PIN: "Personal Identification Number", PAN: "Primary Account Number",
  // payments & product
  PSP: "Payment Service Provider", UPI: "Unified Payments Interface", NPCI: "National Payments Corporation of India", VPA: "Virtual Payment Address",
  SMS: "Short Message Service", APNs: "Apple Push Notification service", FCM: "Firebase Cloud Messaging", SES: "Simple Email Service", ATM: "Automated Teller Machine",
  RSVP: "Répondez s'il vous plaît (please reply)", UTC: "Coordinated Universal Time", DST: "Daylight Saving Time", RRULE: "Recurrence Rule",
  // AI
  ML: "Machine Learning", AI: "Artificial Intelligence", LLM: "Large Language Model", RAG: "Retrieval-Augmented Generation",
  // interviews & code
  HLD: "High-Level Design", LLD: "Low-Level Design", OOP: "Object-Oriented Programming", UML: "Unified Modeling Language", DSA: "Data Structures and Algorithms",
  SOLID: "Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion", DRY: "Don't Repeat Yourself",
  KISS: "Keep It Simple, Stupid", YAGNI: "You Aren't Gonna Need It", FIFO: "First In, First Out", LRU: "Least Recently Used", LFU: "Least Frequently Used",
  CAS: "Compare-And-Swap", SDE: "Software Development Engineer", TC: "Time Complexity", SC: "Space Complexity",
  BFS: "Breadth-First Search", DFS: "Depth-First Search", DP: "Dynamic Programming", BST: "Binary Search Tree", MST: "Minimum Spanning Tree",
  DSU: "Disjoint Set Union", LCA: "Lowest Common Ancestor", LIS: "Longest Increasing Subsequence", LCS: "Longest Common Subsequence",
  KMP: "Knuth–Morris–Pratt", AVL: "Adelson-Velsky and Landis", GCD: "Greatest Common Divisor", LCM: "Least Common Multiple", DLL: "Doubly Linked List",
  PQ: "Priority Queue", LPS: "Longest Prefix Suffix", JMH: "Java Microbenchmark Harness", TCO: "Tail Call Optimisation", STAR: "Situation, Task, Action, Result",
};
const ABBR_RE = new RegExp("(?<![\\w/.-])(" + Object.keys(ABBR).sort((a, b) => b.length - a.length).map(k => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")(s?)(?![\\w/-])", "g");
const ABBR_UNIT = ".sdc, .sdq, .sdstage, .lab, .sheet, .note, .pcard, .box, .nvitem, .sdbox, .qday, .ppsolwrap, .kit, .sdx > p, .sdx > h2, .trcard";
const ABBR_SKIP = ".pptable tr:not(.ppsolrow), nav, .groups, .today, header, .tmacts, pre, code, textarea, input, select, script, style, svg, abbr, .tag, .sdlv, .sdfq, .sdqt, .nvkind, .sdrt, .codebar, .lgd";
const abbrSeen = new WeakMap(), abbrDone = new WeakSet();
const T = t => { const x = document.createTextNode(t); abbrDone.add(x); return x; };
function expandAbbr(root){
  if (!root || root.nodeType !== 1) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {acceptNode: n => {
    if (abbrDone.has(n) || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
    const p = n.parentElement; if (!p || p.closest(ABBR_SKIP)) return NodeFilter.FILTER_REJECT;
    return NodeFilter.FILTER_ACCEPT; }});
  const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(n => {
    ABBR_RE.lastIndex = 0; const text = n.nodeValue;
    if (!ABBR_RE.test(text)) { abbrDone.add(n); return; }
    ABBR_RE.lastIndex = 0;
    const unit = n.parentElement.closest(ABBR_UNIT) || n.parentElement.closest("section, main, aside, article, details, footer");
    if (!unit) { abbrDone.add(n); return; }
    let seen = abbrSeen.get(unit); if (!seen) { seen = new Set(); abbrSeen.set(unit, seen); }
    const unitText = unit.textContent.toLowerCase();
    const frag = document.createDocumentFragment(); let last = 0, m;
    while ((m = ABBR_RE.exec(text))) {
      const [all, k, s] = m, full = ABBR[k] + (s && !/s$/.test(ABBR[k]) ? "s" : "");
      frag.append(T(text.slice(last, m.index)));
      const before = text.slice(Math.max(0, m.index - full.length - 3), m.index).toLowerCase(), after = text.slice(m.index + all.length, m.index + all.length + full.length + 3).toLowerCase();
      const alreadyExplained = before.includes(ABBR[k].toLowerCase()) || after.includes(ABBR[k].toLowerCase()) || unitText.includes(ABBR[k].toLowerCase() + " (" + k.toLowerCase());
      if (!seen.has(k) && !alreadyExplained) { frag.append(T(full + " (")); }
      const ab = document.createElement("abbr"); ab.title = ABBR[k]; ab.textContent = all; frag.append(ab);
      if (!seen.has(k) && !alreadyExplained) frag.append(T(")"));
      seen.add(k); last = m.index + all.length;
    }
    frag.append(T(text.slice(last)));
    const parent = n.parentNode; parent.replaceChild(frag, n);
  });
}
const abbrObs = new MutationObserver(ms => { ms.forEach(m => m.addedNodes.forEach(n => { if (n.nodeType === 1) expandAbbr(n); else if (n.nodeType === 3 && n.parentElement) expandAbbr(n.parentElement); })); });
function startAbbr(){ expandAbbr(document.querySelector(".wrap")); expandAbbr(document.getElementById("sheet")); abbrObs.observe(document.body, {childList: true, subtree: true}); }
