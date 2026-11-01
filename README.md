# 30 Days: Data Structures to System Design (Java)

My 30-day plan to prepare for Google, Microsoft and Amazon interviews, entirely in Java.

**Live sticky-notes board:** https://sgoel2718.github.io/DSAAndSystemDesign/
**Full plan (PDF):** [plan/DSA_30_Day_Java_Plan.pdf](plan/DSA_30_Day_Java_Plan.pdf)

| Week | Focus |
|---|---|
| 1 | Java for DSA, complexity, arrays & strings, matrices, hashing, recursion & backtracking, sorting & binary search, linked lists, stacks & queues |
| 2 | Binary trees, BST/AVL/B-Tree, heaps, tries & string algorithms, graphs (BFS/DFS, topo sort, Dijkstra, MST, Union-Find) |
| 3 | Greedy & intervals, dynamic programming (1D, 2D, interval/tree/bitmask), bits, math & number theory, randomised algorithms, segment & Fenwick trees, advanced graphs |
| 4 | OOP, SOLID & design patterns, Java concurrency, LLD case studies, system design (caching, sharding, replication, Kafka, Raft, rate limiting, API design, security), HLD case studies, behavioural prep, mock interviews |

- 161 linked LeetCode problems, a live Java demo every day, and revision sticky notes
- System Design handbook: 7-step answer framework, 19 building blocks, 12 case studies, LLD patterns, estimation numbers
- Pattern playbook: for each of 20 patterns, when to use it, step-by-step approach, Java template, common mistakes, complexity
- "How to approach questions" for every day's topic
- Every problem taught gets all its approaches (brute force to optimal) with time and space complexity and Java code, compiled and tested by `scripts/check_solutions.py`
- Java DSA syntax cheat sheet
- Flagship project: **NexusKV**, a distributed key-value store in Java (LSM-tree storage, WAL, Bloom filters, consistent hashing, replication, leader election)

## Layout
```
index.html            sticky-notes board (GitHub Pages)
plan/                 downloadable PDF plan
scripts/              plan_data.py is the single source; build_pdf.py and build_board.py regenerate both
days/                 daily lessons: notes (README) + runnable Java demos and solutions
nexuskv/              the NexusKV project (Maven multi-module, Java 21)
```

Progress ticks on the board are saved in your own browser.
