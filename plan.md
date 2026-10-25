# Real-Time Emergency Task Scheduler — Project Plan

> **Assignment:** Design a task scheduling system using priority queues to manage tasks according to urgency and deadlines. Simulate task arrivals, priority changes, and missed deadlines under limited processing capacity.
>
> **Constraint:** The priority queue must be built by hand in **C++**. The rest (UI/UX) is built in a separate language. Recommended: **Python + Streamlit**.

---

## 1. Vision in One Paragraph

A generic scheduling simulator. Tasks arrive over time, each with a priority, a time needed, and a deadline. A limited number of workers can process tasks at once. A hand-built priority queue decides who goes next. The simulation handles arrivals, mid-run priority changes, preemption, and missed deadlines, then produces a full event log and metrics. A dashboard replays the run visually and lets the user compare scheduling policies. The engine knows nothing about themes. "Emergency", "Personal", or "Computer" are UI skins applied later.

---

## 2. Key Decisions (Locked In)

| # | Decision | Reason |
|---|----------|--------|
| 1 | Engine is **generic** (task, worker, priority, deadline) | Themes can be added later without touching C++ |
| 2 | Priority queue is a **hand-built indexed binary heap** | Assignment requirement, and priority changes need update/remove |
| 3 | **Discrete time ticks** (integers) | Easy to reason about, debug, and test |
| 4 | **Run to completion, then replay** | Engine writes an event log; UI replays it. No live C++/UI streaming needed |
| 5 | C++ ↔ UI bridge = **scenario file in, JSON-lines event log out** | Simple, language-independent, no bindings |
| 6 | UI = **Python + Streamlit** with Plotly | Fastest path to a polished dashboard |
| 7 | **Lower priority number = more urgent** (1 = critical) | Matches min-heap convention |
| 8 | All UI labels routed through one `LABELS` dictionary | Makes the theme switcher trivial later |

---

## 3. Scope

### Must Have (Core)
- Hand-built indexed min-heap: `push`, `pop`, `peek`, `updatePriority`, `remove`
- Tick-based simulation with task arrivals
- Priority changes at scheduled times
- Missed-deadline detection and logging
- Limited capacity (1 to k workers)
- Event log + summary metrics
- Streamlit dashboard: setup, replay, results

### Should Have
- Preemption (toggle)
- Multiple policies: Priority, EDF, Hybrid, Least Slack
- Aging (prevents starvation)
- Side-by-side policy comparison
- Random scenario generator (seeded)

### Nice to Have
- Theme presets (Emergency / Personal / Computer)
- Live-feel replay with toasts and animations
- Export results (CSV/PNG)
- Scenario save/load

### Out of Scope
- Real-time wall-clock scheduling
- Network/distributed execution
- Native C++/Python bindings

---

## 4. System Architecture

```
┌────────────────────┐     scenario.txt      ┌────────────────────┐
│   Streamlit UI     │ ───────────────────▶  │   C++ Engine       │
│  (Python)          │                       │  (scheduler.exe)   │
│                    │ ◀───────────────────  │                    │
│  setup / replay /  │    events.jsonl       │  IndexedHeap +     │
│  results           │    + metrics          │  Scheduler loop    │
└────────────────────┘                       └────────────────────┘
```

**Flow:**
1. User configures tasks and options in the UI.
2. UI writes a `scenario.txt`.
3. UI runs `scheduler scenario.txt` as a subprocess.
4. Engine prints one JSON event per line, then a final metrics line.
5. UI parses output and drives replay, charts, and metrics.

---

## 5. Folder Structure

```
task-scheduler/
├── README.md
├── plan.md
├── engine/                      # C++ part
│   ├── Makefile
│   ├── src/
│   │   ├── Task.h               # Task struct + status enum
│   │   ├── IndexedHeap.h        # Hand-built priority queue (template/header)
│   │   ├── Policy.h             # Key functions: PRIORITY, EDF, HYBRID, LST
│   │   ├── Worker.h             # Worker state (idle / running task id)
│   │   ├── Scenario.h/.cpp      # Parse scenario file into config + events
│   │   ├── Scheduler.h/.cpp     # Tick loop, preemption, deadline checks
│   │   ├── Logger.h/.cpp        # JSON-lines event output + metrics
│   │   └── main.cpp             # Entry point: read file, run, print
│   └── tests/
│       ├── test_heap.cpp        # Randomized heap tests
│       └── test_scheduler.cpp   # Hand-checked scenario tests
├── scenarios/
│   ├── basic.txt
│   ├── overload.txt             # Too many tasks, forces misses
│   ├── priority_change.txt
│   └── starvation.txt           # Shows aging working
├── ui/
│   ├── app.py                   # Streamlit entry point
│   ├── labels.py                # LABELS dict + theme presets
│   ├── engine_bridge.py         # Write scenario, run exe, parse output
│   ├── generator.py             # Seeded random scenario generator
│   ├── charts.py                # Gantt, queue-over-time, metrics charts
│   ├── components.py            # Cards, badges, KPI row helpers
│   ├── styles.css               # Injected custom CSS
│   └── .streamlit/
│       └── config.toml          # Theme colors
├── docs/
│   ├── report-outline.md
│   └── screenshots/
└── requirements.txt             # streamlit, plotly, pandas
```

---

## 6. Data Model

### Task
| Field | Meaning |
|-------|---------|
| `id` | Unique integer |
| `arrive` | Tick when the task enters the system |
| `burst` | Total ticks of work needed |
| `remaining` | Ticks of work left |
| `deadline` | Tick by which it must be complete |
| `priority` | 1 (most urgent) to 5 (least) |
| `status` | `NOT_ARRIVED`, `WAITING`, `RUNNING`, `DONE`, `MISSED` |
| `startTime`, `finishTime` | For metrics |
| `waitedTicks` | For aging and metrics |

### Worker
`id`, `currentTaskId` (or -1 if idle), `busyTicks` (for utilization).

### Deadline rule (precise)
A task finishing during tick `t` completes at time `t + 1`. It meets its deadline if `completion <= deadline`. At the **start** of tick `t`, if `remaining > 0` and `t >= deadline`, the task is **missed**.

---

## 7. Scenario File Format (UI → Engine)

Line-based, easy to parse in C++ with no libraries:

```
# comments allowed
CONFIG workers=2 policy=HYBRID preemptive=1 aging=1 aging_interval=5 miss_action=DROP max_time=100
TASK id=1 arrive=0 burst=5 deadline=12 priority=3
TASK id=2 arrive=2 burst=3 deadline=6  priority=1
PRIORITY_CHANGE time=4 id=1 new_priority=1
```

**CONFIG options**

| Key | Values | Meaning |
|-----|--------|---------|
| `workers` | 1..N | Processing capacity |
| `policy` | `PRIORITY`, `EDF`, `HYBRID`, `LST` | How urgency is ranked |
| `preemptive` | 0/1 | Can urgent tasks interrupt running ones |
| `aging` | 0/1 | Waiting tasks gain urgency |
| `aging_interval` | ticks | How often aging applies |
| `miss_action` | `DROP`, `CONTINUE` | Remove missed task, or let it finish late |
| `max_time` | ticks | Hard stop for the simulation |

---

## 8. Event Log Format (Engine → UI)

One JSON object per line, in chronological order:

```json
{"t":0,"event":"ARRIVE","id":1,"priority":3,"deadline":12}
{"t":0,"event":"START","id":1,"worker":0}
{"t":2,"event":"ARRIVE","id":2,"priority":1,"deadline":6}
{"t":2,"event":"PREEMPT","id":1,"worker":0,"by":2}
{"t":2,"event":"START","id":2,"worker":0}
{"t":4,"event":"PRIORITY_CHANGE","id":1,"old":3,"new":1}
{"t":5,"event":"FINISH","id":2,"worker":0}
{"t":9,"event":"MISS","id":3,"deadline":8}
{"t":12,"event":"AGING","id":4,"old":5,"new":4}
```

Plus a per-tick **snapshot** line (needed for the replay queue view):

```json
{"t":3,"event":"TICK","queue":[2,5,7],"running":[1,-1],"missed":0,"done":1}
```

Final line:

```json
{"event":"METRICS","total":10,"done":8,"missed":2,"miss_rate":0.2,"avg_wait":3.4,"avg_turnaround":7.1,"utilization":[0.92,0.85],"per_priority_miss":{"1":0,"2":0.1,"3":0.3,"4":0.5,"5":0.5}}
```

---

## 9. C++ Engine Design

### 9.1 IndexedHeap (the core deliverable)

- Array-based binary min-heap storing task ids (or pointers).
- A `pos[id]` array maps each task to its current heap index.
- Comparator is injected, so policies swap without touching heap code.

| Operation | Behavior | Complexity |
|-----------|----------|------------|
| `push(id)` | Append, sift up, record position | O(log n) |
| `pop()` | Swap root with last, shrink, sift down | O(log n) |
| `peek()` | Return root | O(1) |
| `update(id)` | Key changed: sift up or sift down from `pos[id]` | O(log n) |
| `remove(id)` | Swap with last, shrink, then sift up/down | O(log n) |
| `contains(id)`, `size()`, `empty()` | Via `pos[]` | O(1) |

**Invariant to protect:** every swap updates `pos[]` for both items. Most bugs live here.

### 9.2 Policy keys (lower key = more urgent)

All keys are chosen so they **do not change while a task is waiting**. Otherwise the heap order would silently break.

| Policy | Key | Notes |
|--------|-----|-------|
| `PRIORITY` | `(priority, arrive)` | Ties broken by earlier arrival |
| `EDF` | `(deadline, priority)` | Classic real-time scheduling |
| `HYBRID` | `deadline - W * (6 - priority)` | Priority-adjusted deadline; `W` tunable (default 3) |
| `LST` | `deadline - remaining` | Least slack. For waiting tasks, `now` shifts all slacks equally, so ordering is static |

Always add the task id as a final tiebreaker so results are deterministic.

### 9.3 Aging

Every `aging_interval` ticks, each waiting task's priority improves by 1 (down to a floor of 1). Each change calls `heap.update(id)` and logs an `AGING` event. Cost is O(n log n) every N ticks, which is fine.

### 9.4 Tick loop (order matters)

```
for t = 0 .. max_time:
  1. Add tasks with arrive == t to the heap          (log ARRIVE)
  2. Apply PRIORITY_CHANGE events at t               (heap.update, log)
  3. Apply aging if t % aging_interval == 0
  4. Deadline check: any waiting or running task with
     remaining > 0 and t >= deadline -> MISS
        DROP: remove from heap / free worker
        CONTINUE: mark late, keep going
  5. Preemption (if enabled): while heap.peek() is more urgent than the
     least urgent running task, swap them (push preempted task back, log PREEMPT)
  6. Assign: for each idle worker, pop heap and START the task
  7. Execute: each running task remaining--, worker busyTicks++
        if remaining == 0 -> FINISH (completion = t + 1), free worker
  8. Log TICK snapshot
  9. Stop early if no tasks remain and no future arrivals/events
```

### 9.5 Metrics
- Miss rate (overall and per priority level)
- Average waiting time, average turnaround time
- Per-worker utilization
- Throughput (tasks finished per tick)
- Max queue length

### 9.6 Edge cases to handle explicitly
- Multiple arrivals at the same tick
- Priority change for a task not yet arrived, already running, finished, or missed
- Task with `deadline <= arrive`, or `burst` larger than the available time (infeasible)
- Empty scenario, zero workers, duplicate ids (validate and print a clear error)
- Preemption ping-pong (two equal-key tasks): tiebreak so equal keys never preempt

---

## 10. UI/UX Design (Streamlit)

### 10.1 Design language
- **Mood:** control room. Dark base, high-contrast urgency colors.
- **Palette:** background `#0e1117`, cards `#1a1f2b`, accent red `#ff4b4b`, amber `#ffa62b`, green `#2ecc71`, blue `#3b82f6`
- **Priority colors:** P1 red, P2 orange, P3 amber, P4 blue, P5 grey
- **Missed = always red.** Done = green. Running = pulsing accent.
- One font family, generous spacing, rounded cards, no clutter.

### 10.2 Layout

**Sidebar (global controls)**
- Theme selector (Generic for now)
- Workers (slider), Policy (select), Preemption (toggle), Aging (toggle + interval), Missed-task action
- Scenario source: Manual / Random / Preset example
- **Run Simulation** button

**Tab 1 · Setup**
- Editable task table (`st.data_editor`): id, arrive, burst, deadline, priority
- Priority-change events table
- Random generator: number of tasks, arrival spread, seed
- Validation messages shown inline (for example "deadline is before arrival")

**Tab 2 · Replay**
- Time slider + Play / Pause / Step buttons
- Top KPI row: Time, Waiting, Running, Done, Missed
- Left: **Queue panel**, tasks as stacked cards sorted by urgency, with priority badge and a deadline countdown. Cards near deadline get a red border.
- Right: **Worker lanes**, one row per worker with the current task and a progress bar
- Event feed: the last 5 events as text, plus `st.toast` for PREEMPT, MISS, PRIORITY_CHANGE

**Tab 3 · Results**
- Metric cards (`st.metric`): miss rate, avg wait, avg turnaround, utilization
- **Gantt chart** (Plotly horizontal bars per worker, colored by priority, missed marked red, deadline markers)
- Queue length over time (line chart)
- Per-priority miss rate (bar chart)

**Tab 4 · Compare**
- Runs the same scenario under all policies
- Table + grouped bar chart: miss rate, avg wait per policy
- Short "winner" callout

### 10.3 Theme system

All visible text comes from `labels.py`:

```python
THEMES = {
  "Generic":   {"task": "Task",  "worker": "Worker",      "priority": "Priority", "deadline": "Deadline", "missed": "Missed"},
  "Emergency": {"task": "Call",  "worker": "Response team","priority": "Severity", "deadline": "Response limit", "missed": "Failed response"},
  "Personal":  {"task": "Task",  "worker": "You",         "priority": "Importance","deadline": "Due",     "missed": "Overdue"},
  "Computer":  {"task": "Job",   "worker": "CPU core",    "priority": "Priority", "deadline": "Deadline", "missed": "Missed"},
}
```

Each preset can also carry an icon, accent color, default scenario, and example data. Ship **Generic only** at first, with the dictionary already in place.

### 10.4 Charts note
`px.timeline` expects dates. Use `plotly.graph_objects.Bar` with `orientation="h"` and `base=start`, `x=duration`, `y=worker`. This keeps ticks as plain integers.

### 10.5 Streamlit specifics
- Store the parsed results in `st.session_state` so replay interactions don't rerun the engine.
- Cache engine runs with `st.cache_data` keyed on the scenario text.
- Handle engine failures (missing exe, non-zero exit, malformed output) with a friendly `st.error`.
- Locate the executable relative to the project root; handle `.exe` on Windows.

### 10.6 Accessibility and polish
- Don't rely on color alone: add icons or text labels for status.
- Readable contrast, tooltips on every chart.
- Empty states ("Add some tasks to begin").
- A clear **Reset** button.

---

## 11. Build Plan (Phases)

### Phase 0 · Setup (0.5 day)
- [ ] Create folder structure, git repo, `.gitignore`
- [ ] `Makefile` that builds `scheduler`; check `g++ -std=c++17` works
- [ ] `requirements.txt`, virtual environment, `streamlit hello` runs

### Phase 1 · IndexedHeap (1–2 days)
- [ ] Implement push / pop / peek / update / remove with `pos[]`
- [ ] Randomized test against a brute-force "find the minimum" oracle
- [ ] Test update and remove heavily (this is where bugs hide)
- [ ] Document complexity of each operation

### Phase 2 · Minimal scheduler (1–2 days)
- [ ] Task struct, scenario parser, logger
- [ ] 1 worker, non-preemptive, PRIORITY policy
- [ ] Arrivals, start, finish events working end to end
- [ ] Verify `basic.txt` by hand

### Phase 3 · Real-time behavior (2 days)
- [ ] Deadline-miss detection (DROP and CONTINUE)
- [ ] Priority changes
- [ ] Preemption
- [ ] TICK snapshots and METRICS output

### Phase 4 · Advanced engine (1–2 days)
- [ ] k workers
- [ ] EDF, HYBRID, LST policies
- [ ] Aging
- [ ] Edge cases and input validation

### Phase 5 · UI foundation (1–2 days)
- [ ] `engine_bridge.py`: write scenario, run exe, parse JSONL
- [ ] Setup tab + Run button + Results tab (metrics + Gantt)
- [ ] Error handling

### Phase 6 · Replay and polish (2 days)
- [ ] Replay tab: slider, play, queue cards, worker lanes, toasts
- [ ] Theme config + CSS
- [ ] Compare tab

### Phase 7 · Themes and wrap-up (1 day)
- [ ] Theme presets via `LABELS`
- [ ] README, screenshots, report, demo script
- [ ] Final test pass on all sample scenarios

> Adjust durations to your submission deadline. If time is short, cut in this order: themes, Compare tab, LST policy, aging. Never cut the heap, deadline misses, or priority changes.

---

## 12. Testing Plan

**Heap**
- Random sequences of operations compared against a brute-force oracle (the C++ test may use `std::vector` or `std::priority_queue` as the oracle; only the product code must be hand-built)
- Check the heap invariant and `pos[]` consistency after every operation

**Scheduler**
- Hand-computed expected logs for small scenarios (3 to 5 tasks)
- Same scenario, different policy: results must differ in the expected way
- Determinism: the same scenario run twice gives byte-identical output

**Scenarios to prepare**
| File | Purpose |
|------|---------|
| `basic.txt` | Everything finishes, sanity check |
| `overload.txt` | More work than capacity, forces misses |
| `priority_change.txt` | Urgent bump mid-run changes the order |
| `starvation.txt` | Low-priority task starves without aging, runs with aging |
| `simultaneous.txt` | Many arrivals at the same tick |

**UI**
- Missing exe, empty task table, invalid inputs, very large scenario (e.g. 500 tasks)

---

## 13. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Heap position bookkeeping bugs | Test `update/remove` first and heavily; assert invariants in debug builds |
| Time-dependent keys breaking heap order | Use only static keys (Section 9.2) |
| Off-by-one on deadlines | Fixed rule in Section 6; test with boundary cases |
| C++ ↔ Python path/OS issues | Resolve paths from project root; handle `.exe` |
| Streamlit rerun flicker during replay | Use `session_state` and placeholders; keep animation modest |
| Scope creep | Follow the Must / Should / Nice split |

---

## 14. Deliverables

- Source code (engine + UI), `README` with build and run steps
- Sample scenarios
- Short report: problem, design, data structure choice and complexity, policy comparison results, screenshots, limitations, future work
- Demo script (2 to 3 minutes): basic → overload → priority change → compare policies

### Report outline (`docs/report-outline.md`)
1. Introduction and problem statement
2. Why a priority queue (and why an indexed heap)
3. Design: architecture, data model, algorithm
4. Policies and their trade-offs
5. Implementation notes
6. Experiments: miss rate and wait time per policy
7. UI overview
8. Limitations and future work

---

## 15. Reusable Prompts (for AI assistance)

Start every prompt with the **context header** so the assistant stays consistent:

```
CONTEXT: I'm building a Real-Time Emergency Task Scheduler (course assignment).
Engine in C++17 (hand-built indexed min-heap, no std::priority_queue in product code),
UI in Python + Streamlit. Time is discrete ticks. Lower priority number = more urgent.
Engine reads scenario.txt and prints JSON-lines events. Follow plan.md.
I want to understand the code, so explain key decisions briefly.
```

**P1 · IndexedHeap**
```
[CONTEXT] Write IndexedHeap.h: a templated binary min-heap of task ids with a pos[] array,
injectable comparator, and operations push, pop, peek, update(id), remove(id), contains,
size, empty. Update pos[] on every swap. Add comments on the invariants.
Then write test_heap.cpp with randomized operations checked against a brute-force oracle.
```

**P2 · Scenario parser**
```
[CONTEXT] Write Scenario.h/.cpp to parse the line-based scenario format from plan.md
(CONFIG, TASK, PRIORITY_CHANGE; # comments). Validate: duplicate ids, deadline <= arrive,
burst <= 0, workers < 1, unknown keys. Return clear error messages with line numbers.
```

**P3 · Scheduler loop**
```
[CONTEXT] Implement Scheduler following the tick-loop order in plan.md section 9.4.
Start with 1 worker, non-preemptive, PRIORITY policy. Emit ARRIVE, START, FINISH, TICK
events through Logger as JSON lines. Show me a hand-traced example for basic.txt.
```

**P4 · Deadlines, preemption, priority changes**
```
[CONTEXT] Extend Scheduler with: deadline-miss detection (DROP and CONTINUE), scheduled
PRIORITY_CHANGE using heap.update, and preemption across k workers (compare heap top with
the least urgent running task; equal keys must not preempt). Explain the edge cases.
```

**P5 · Policies and aging**
```
[CONTEXT] Implement Policy.h with PRIORITY, EDF, HYBRID, LST keys using only static keys
(plan.md 9.2), and aging every aging_interval ticks via heap.update. Explain why a
time-dependent key would break the heap.
```

**P6 · Metrics**
```
[CONTEXT] Add Metrics computation and the final METRICS JSON line: miss rate (overall and
per priority), avg wait, avg turnaround, per-worker utilization, throughput, max queue length.
```

**P7 · Engine bridge**
```
[CONTEXT] Write ui/engine_bridge.py: build scenario text from a config dict and a task
DataFrame, run the engine with subprocess (timeout, cross-platform exe path), parse
JSON-lines into events DataFrame + metrics dict, and raise friendly errors.
```

**P8 · Dashboard**
```
[CONTEXT] Build ui/app.py with tabs Setup, Replay, Results, Compare, following plan.md
section 10. Use session_state, st.data_editor for tasks, Plotly go.Bar for the Gantt chart.
Dark control-room theme (config.toml + styles.css). Route all labels through labels.py.
Start with fake event data so I can see the layout before the engine is done.
```

**P9 · Replay view**
```
[CONTEXT] Build the Replay tab: time slider, Play/Pause/Step, KPI row, queue cards sorted
by urgency with deadline countdown and red border near deadline, worker lanes with
progress bars, and st.toast on PREEMPT/MISS/PRIORITY_CHANGE. Driven by TICK snapshots.
```

**P10 · Debugging**
```
[CONTEXT] Here is a scenario file, the expected behavior, and the actual event log:
[paste]. Find the first tick where they diverge and explain why. Don't rewrite everything;
point to the exact logic that is wrong.
```

**P11 · Report**
```
[CONTEXT] Using these experiment results [paste], draft the Experiments and Discussion
sections of my report. Compare policies honestly, including where each one fails.
```

---

## 16. Definition of Done

- [ ] Hand-built heap passes randomized tests, including update and remove
- [ ] Arrivals, priority changes, and missed deadlines are all visible in the output
- [ ] Capacity is limited (k workers), and the overload scenario causes misses
- [ ] At least 3 policies are comparable in the UI
- [ ] Dashboard shows replay, Gantt chart, and metrics without errors
- [ ] Same input always gives the same output
- [ ] README lets a fresh machine build and run in under 5 minutes
- [ ] Report and demo ready

---

## 17. Open Questions

1. Does the course require a specific UI language or framework? (Plan assumes Python + Streamlit.)
2. Are there required input/output formats or file names in the assignment brief?
3. Is a report or viva expected, and in what format?
4. Submission deadline (to size the phases above)?
5. Is preemption expected, or is non-preemptive enough for your instructor?
