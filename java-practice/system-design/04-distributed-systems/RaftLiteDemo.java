import java.util.*;

public class RaftLiteDemo {
    // Simplified Raft: leader election by majority vote with terms, and log replication committed on a majority.
    static class Node {
        final int id; int term = 0; Integer votedFor = null; String role = "follower"; boolean up = true; final List<String> log = new ArrayList<>(); int commitIndex = 0;
        Node(int id) { this.id = id; }
        boolean requestVote(int t, int candidate, int candidateLogLen) {
            if (!up || t < term) return false;
            if (t > term) { term = t; votedFor = null; role = "follower"; }
            if ((votedFor == null || votedFor == candidate) && candidateLogLen >= log.size()) { votedFor = candidate; return true; }
            return false;
        }
        boolean appendEntries(int t, List<String> leaderLog) {
            if (!up || t < term) return false;
            term = t; role = "follower"; log.clear(); log.addAll(leaderLog); return true;
        }
    }
    static final List<Node> cluster = new ArrayList<>();

    static Node elect(Node candidate) {
        candidate.term++; candidate.role = "candidate"; candidate.votedFor = candidate.id; int votes = 1;
        for (Node n : cluster) if (n != candidate && n.requestVote(candidate.term, candidate.id, candidate.log.size())) votes++;
        boolean won = votes > cluster.size() / 2;
        if (won) candidate.role = "leader";
        System.out.println("node " + candidate.id + " runs in term " + candidate.term + ": " + votes + " votes -> " + (won ? "LEADER" : "lost"));
        return won ? candidate : null;
    }

    static void replicate(Node leader, String cmd) {
        leader.log.add(cmd); int acks = 1;
        for (Node n : cluster) if (n != leader && n.appendEntries(leader.term, leader.log)) acks++;
        boolean committed = acks > cluster.size() / 2;
        if (committed) leader.commitIndex = leader.log.size();
        System.out.println("  " + cmd + ": " + acks + "/" + cluster.size() + " acks -> " + (committed ? "COMMITTED" : "not committed (no majority)"));
    }

    public static void main(String[] args) {
        for (int i = 1; i <= 5; i++) cluster.add(new Node(i));
        Node leader = elect(cluster.get(0));
        replicate(leader, "SET x=1"); replicate(leader, "SET y=2");
        leader.up = false; System.out.println("node 1 (leader) crashes");
        Node newLeader = elect(cluster.get(2));
        replicate(newLeader, "SET x=3");
        cluster.get(3).up = false; cluster.get(4).up = false; System.out.println("nodes 4 and 5 crash too (3 of 5 down)");
        replicate(newLeader, "SET z=9");
        System.out.println("node 3 log: " + newLeader.log + ", committed up to index " + newLeader.commitIndex);
        cluster.get(0).up = true; System.out.println("old leader 1 comes back in term " + cluster.get(0).term + " and steps down on seeing term " + newLeader.term);
        cluster.get(0).appendEntries(newLeader.term, newLeader.log.subList(0, newLeader.commitIndex));
        System.out.println("node 1 now: role=" + cluster.get(0).role + " term=" + cluster.get(0).term + " log=" + cluster.get(0).log);
    }
}
