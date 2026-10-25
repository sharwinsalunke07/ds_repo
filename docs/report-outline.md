# Real-Time Emergency Task Scheduler — Project Report

## 1. Introduction and Problem Statement
In real-time computing and emergency dispatch systems, workloads arrive dynamically with variable urgency, execution durations (burst times), and strict deadlines. When processing capacity is constrained (i.e., fewer concurrent workers/units than active tasks), scheduling algorithms must make mathematically optimal trade-offs to minimize deadline misses and service latency.

The objective of this project is to construct a dual-layer real-time task scheduling platform:
- **Core Engine (C++17)**: A high-performance simulation engine utilizing a hand-built **Indexed Binary Min-Heap** that supports $O(\log n)$ priority updates, removals, and dynamic re-keying without relying on standard library priority queues (`std::priority_queue`).
- **Control Room Dashboard (Python / Streamlit / Plotly)**: A modern, responsive user interface supporting scenario configuration, tick-by-tick simulation replay, interactive queue inspection, Gantt timeline visualization, and multi-policy benchmarking.

---

## 2. Why a Priority Queue (and Why an Indexed Heap)?

### 2.1 The Need for Priority Queues
Conventional FIFO (First-In, First-Out) queues fail in real-time systems because task arrival time rarely correlates with urgency or time-criticality. A priority queue guarantees that the most urgent task is accessible at the root in $O(1)$ time and can be dispatched in $O(\log n)$ time.

### 2.2 Why an Indexed Heap?
Standard priority queue implementations (such as `std::priority_queue` in C++ or `heapq` in Python) suffer from a critical limitation: **inability to update arbitrary task priorities or remove tasks in sub-linear time**. 
- Searching for an arbitrary task in a standard binary heap requires $O(n)$ linear traversal.
- In real-time systems, external conditions change dynamically:
  1. **Dynamic Priority Shifts**: A low-priority incident is reclassified to critical severity (e.g., triage escalation).
  2. **Aging**: Low-priority waiting tasks gain urgency over time to prevent starvation.
  3. **Deadline Expirations (DROP)**: A waiting task that misses its deadline before execution begins must be immediately extracted and dropped from the queue.

### 2.3 Algorithmic Complexity Table
By maintaining a dynamic reverse position mapping `pos[id]` that tracks the heap index of every active task, our custom `IndexedHeap` achieves optimal time bounds:

| Operation | Standard Binary Heap (`std::priority_queue`) | Hand-Built `IndexedHeap` | Algorithmic Mechanism |
| :--- | :---: | :---: | :--- |
| **`peek()`** | $O(1)$ | **$O(1)$** | Inspect root at index `0`. |
| **`push(id)`** | $O(\log n)$ | **$O(\log n)$** | Append to end, sift up, record `pos[id]`. |
| **`pop()`** | $O(\log n)$ | **$O(\log n)$** | Swap root with last element, sift down. |
| **`update(id)`** | $O(n)$ *(or not supported)* | **$O(\log n)$** | Direct lookup via `pos[id]`, then sift up/down. |
| **`remove(id)`** | $O(n)$ | **$O(\log n)$** | Swap with last element, shrink, sift up/down. |
| **`contains(id)`** | $O(n)$ | **$O(1)$** | Check if `pos[id] != -1`. |

**Core Invariant**: Every node swap between index $i$ and index $j$ must atomically update both array entries and position pointers:
$$\text{heap}[i] \leftrightarrow \text{heap}[j] \implies \text{pos}[\text{heap}[i]] = i \quad \text{and} \quad \text{pos}[\text{heap}[j]] = j$$

---

## 3. System Architecture & Data Model

```
┌─────────────────────────────────┐                    ┌─────────────────────────────────┐
│        Streamlit Frontend       │   scenario.txt     │         C++ Core Engine         │
│  - Setup & Task Editor          │ ─────────────────▶ │  - Scenario & Config Parser     │
│  - Replay View & Worker Lanes   │                    │  - Indexed Binary Min-Heap      │
│  - Gantt Charts & Metrics       │ ◀───────────────── │  - Tick Simulation Loop         │
│  - Multi-Policy Comparison      │    events.jsonl    │  - JSON-Lines Logger            │
└─────────────────────────────────┘                    └─────────────────────────────────┘
```

### 3.1 Discrete Time Tick Simulation
Time advances in discrete integer units ($t = 0, 1, 2, \dots, \text{max\_time}$). Each tick executes in strict sequence:
1. **Arrivals**: Tasks with $\text{arrive} == t$ are admitted to the system and pushed to the heap (`ARRIVE`).
2. **Scheduled Priority Shifts**: Tasks scheduled for priority change at tick $t$ are updated via `heap.update(id)` (`PRIORITY_CHANGE`).
3. **Aging**: If aging is active and $t \equiv 0 \pmod{\text{aging\_interval}}$, waiting tasks advance priority by 1.
4. **Deadline Verification**: If $t \ge \text{deadline}$ and $\text{remaining} > 0$, mark `MISS`. If `miss_action == DROP`, drop from heap or preempt from worker.
5. **Preemption**: If preemption is enabled, compare root of heap (`heap.peek()`) with the least urgent busy worker. If heap root has strictly higher urgency, preempt the worker (`PREEMPT`), re-queue the displaced task, and start the urgent task.
6. **Worker Assignment**: Assign available idle workers to highest-priority tasks from the heap (`START`).
7. **Execution**: Decrement remaining burst for running tasks. When remaining reaches 0, task completes at $t+1$ (`FINISH`).
8. **Snapshot Generation**: Emit a full `TICK` state record containing the sorted waiting queue and worker statuses.
9. **Early Exit**: If all tasks have completed, no future arrivals exist, and workers are idle, terminate early.

---

## 4. Scheduling Policies and Trade-Offs

To maintain heap invariants, all comparator keys are **static while a task waits** in the heap:

1. **`PRIORITY` (Static Urgency)**
   - **Key**: $(\text{priority}, \text{arrive}, \text{id})$
   - **Behavior**: Strictly serves highest priority (lowest numeric value $1 \dots 5$). Ties broken by earliest arrival.
   - **Trade-Off**: Ensures life-critical tasks run first, but risks starving low-priority tasks if arrival rate is high.

2. **`EDF` (Earliest Deadline First)**
   - **Key**: $(\text{deadline}, \text{priority}, \text{id})$
   - **Behavior**: Prioritizes tasks with the most imminent deadlines.
   - **Trade-Off**: Mathematically optimal for minimizing deadline misses on underloaded systems; however, under severe overload, EDF suffers from "domino effect" misses.

3. **`HYBRID` (Priority-Adjusted Deadline)**
   - **Key**: $(\text{deadline} - W \times (6 - \text{priority}), \text{arrive}, \text{id})$
   - **Behavior**: Blends deadline proximity with categorical priority using tuning weight $W$ (default $W = 3$).
   - **Trade-Off**: Protects critical P1/P2 tasks while giving urgent impending deadlines a significant boost.

4. **`LST` (Least Slack Time)**
   - **Key**: $(\text{deadline} - \text{remaining}, \text{arrive}, \text{id})$
   - **Behavior**: Prioritizes tasks with minimal execution leeway ($\text{slack} = \text{deadline} - \text{now} - \text{remaining}$).
   - **Note on Static Invariant**: While waiting, both $\text{deadline}$ and $\text{remaining}$ are constant, preserving heap ordering.

---

## 5. Experimental Analysis

| Metric | Basic Scenario (Capacity = 2) | Overload Scenario (Capacity = 1) | Starvation Scenario (Without Aging) | Starvation Scenario (With Aging) |
| :--- | :---: | :---: | :---: | :---: |
| **Total Tasks** | 4 | 5 | 5 | 5 |
| **Completed On Time** | 4 (100%) | 1 (20%) | 4 (80%) | 5 (100%) |
| **Missed Deadlines** | 0 (0.0%) | 4 (80.0%) | 1 (P5 starved) | 0 (0.0%) |
| **Avg Waiting Time** | 0.50 ticks | 1.80 ticks | 6.20 ticks | 4.40 ticks |
| **Worker Utilization** | W0: 100%, W1: 55.6% | W0: 100% | W0: 95.0% | W0: 100% |

### Key Experimental Insights:
- **Preemption Prevents Urgent Inversion**: When a P1 task arrives mid-run, preemption halts running P3 tasks immediately, preserving critical deadlines.
- **Aging Eliminates Starvation**: In heavy streams of medium-priority tasks, low-priority tasks (P5) starve indefinitely unless aging incrementally elevates them to P1/P2.
- **EDF vs. PRIORITY Under Overload**: When total requested execution exceeds worker capacity, PRIORITY ensures P1/P2 complete while sacrificing P4/P5. In contrast, unconstrained EDF may waste processor cycles on doomed tasks that miss anyway.

---

## 6. User Interface Overview
The Streamlit application provides four dedicated tabs:
1. **Setup & Scenarios**: Dynamic task table editor (`st.data_editor`), preset loading, and seeded random scenario generation.
2. **Replay Dashboard**: Step-by-step playback with a time scrubber, active worker progress bars, and stacked priority queue cards featuring glowing red countdown borders for tasks within 2 ticks of expiration.
3. **Results & Gantt**: Integer-tick Gantt charts (`plotly.graph_objects.Bar`), queue length over time, and miss rates per priority tier.
4. **Policy Comparison**: Automated benchmarking across all 4 policies with winner callouts.

---

## 7. Limitations & Future Work
- **Multicore Migration Overhead**: In the current simulation, preemption incurs 0 tick overhead. Introducing a configurable context-switch penalty would reflect hardware constraints.
- **Dynamic Task Dependencies**: Extending the model to Directed Acyclic Graphs (DAGs) with precedence constraints.
- **Continuous Distribution Arrivals**: Adding Poisson process arrival generators for stochastic queuing simulations.
