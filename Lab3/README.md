````markdown
# Lab 3 — Raft Lite (Distributed Computing)

This project implements a simplified **Raft (Raft Lite)** consensus protocol to demonstrate leader election, heartbeats, log replication, majority-based commit, and failure handling, as required by the lab criteria.

---

## Contents

- `node.py` — Raft Lite node implementation
- `client.py` — Simple client to submit commands to the leader
- `kill_node.sh` — Helper script to simulate node crashes
- `README.md` — This file

---

## Requirements

- Python **3.8+**
- Python packages:
  ```bash
  pip install flask requests
````

---

## Architecture Overview

* Each node runs an HTTP server and participates in a Raft Lite cluster.
* Nodes can be in one of three states: **Follower**, **Candidate**, **Leader**.
* Implemented RPCs:

  * `RequestVote`
  * `AppendEntries` (used for both heartbeats and log replication)
* Failure model: **crash-stop** (simulated by killing the process).

---

## Running the Cluster (Local Machine)

Open **three terminals**.

### Node A

```bash
python3 node.py --id A --port 8000 --peers B:8001,C:8002
```

### Node B

```bash
python3 node.py --id B --port 8001 --peers A:8000,C:8002
```

### Node C

```bash
python3 node.py --id C --port 8002 --peers A:8000,B:8001
```

Within a short time, one node will become the **leader**.
You will see logs indicating election timeouts and leadership.

---

## Submitting a Client Command

Send a command to the **leader**:

```bash
python3 client.py --leader http://127.0.0.1:8000 --cmd "SET x=5"
```

If the contacted node is not the leader, the request will fail and return a leader hint.

---

## Failure Experiments (Required by Lab)

### 1. Leader Crash and Re-election

1. Identify the current leader from logs.
2. Kill the leader:

   ```bash
   ./kill_node.sh A
   ```
3. Observe logs from remaining nodes — a new leader will be elected automatically.

### 2. Follower Crash and Recovery

1. Kill a follower:

   ```bash
   ./kill_node.sh C
   ```
2. Submit commands to the leader while the follower is down.
3. Restart the follower using its original command.
4. Observe that the follower catches up via log replication.

---

## Example Log Output

```text
[B] Timeout → Candidate (term 3)
[B] Received votes → Leader (term 3)
[A] Append log entry (term=3, cmd=SET x=5)
[C] Append success; appended 1 entries (term=3)
[A] Entry committed (index=0)
```

These logs demonstrate:

* Leader election
* Log replication
* Majority-based commit

---

## EC2 Deployment Notes

* Use **private IP addresses** instead of `127.0.0.1` in `--peers`.
* Ensure all nodes are in the same VPC.
* Open required ports (e.g., `8000–8004`) in the security group.
* Example peer format:

  ```text
  A:10.0.1.12:8000
  ```

---

## Limitations (Explicitly Stated)

* This is a **teaching / lab implementation**, not a production Raft.
* Log persistence is **in-memory only** (no disk recovery).
* Log consistency checks (`prevLogIndex`, `prevLogTerm`) are simplified.
* Designed to meet lab requirements: election, replication, majority commit, and fault tolerance.

