# Real-Time Emergency Task Scheduler

A dual-tier discrete-time task scheduling platform featuring a hand-built **Indexed Binary Min-Heap in C++17** and an interactive **Streamlit & Plotly Control Room Dashboard**.

Built to satisfy coursework constraints: **no `std::priority_queue` in product code**, discrete integer-time simulation, preemption across $k$ workers, dynamic priority shifts, starvation prevention via aging, and multi-policy comparison.

---

## 🌟 Key Features

1. **Hand-Built Indexed Binary Min-Heap (`engine/src/IndexedHeap.h`)**:
   - $O(1)$ lookup and $O(\log n)$ priority updates and removals via reverse position mapping `pos[id]`.
   - Templated comparator allowing dynamic switching between scheduling policies without modifying heap code.
   - Rigorously tested against a brute-force oracle across 15,000+ randomized operations.

2. **Simulation Engine (`engine/src/Scheduler.cpp`)**:
   - Discrete tick-by-tick simulation ($t = 0, 1, 2, \dots$).
   - Multiple scheduling policies: **PRIORITY**, **EDF** (Earliest Deadline First), **HYBRID**, and **LST** (Least Slack Time).
   - Preemption across $k$ workers (with tiebreakers to prevent ping-pong).
   - Aging mechanism that periodically elevates waiting tasks to prevent starvation.
   - Deadline enforcement supporting both `DROP` (cancel overdue tasks) and `CONTINUE` (late completion) modes.
   - Emits structured JSON-Lines events (`ARRIVE`, `START`, `PREEMPT`, `MISS`, `TICK`, `FINISH`) and summary `METRICS`.

3. **Streamlit Control Room Dashboard (`ui/app.py`)**:
   - **Tab 1 · Setup**: Dynamic spreadsheet editor (`st.data_editor`), preset scenarios, and seeded random task generator.
   - **Tab 2 · Replay**: Interactive time slider, step forward/backward buttons, active worker progress lanes, and urgency queue cards with red countdown borders for near-deadline tasks.
   - **Tab 3 · Results**: Plotly integer-tick horizontal Gantt chart, queue length over time, and per-priority miss rate breakdown.
   - **Tab 4 · Compare**: One-click benchmark comparing all 4 policies on the same workload with automated winner recommendations.
   - **Themes**: Switchable UI skins (**Generic**, **Emergency Dispatch**, **Personal Productivity**, and **OS CPU Scheduler**).

---

## 📁 Repository Structure

```
ds project/
├── README.md
├── plan.md
├── requirements.txt             # streamlit, plotly, pandas
├── engine/                      # C++17 Simulation Engine
│   ├── Makefile                 # Linux/macOS build
│   ├── build.bat                # Windows MinGW build script
│   ├── src/
│   │   ├── IndexedHeap.h        # Hand-built indexed min-heap
│   │   ├── Task.h               # Task data model & status enum
│   │   ├── Worker.h             # Worker state & busy tracking
│   │   ├── Policy.h             # Comparators (PRIORITY, EDF, HYBRID, LST)
│   │   ├── Scenario.h/.cpp      # File & string scenario parser
│   │   ├── Logger.h/.cpp        # JSON-lines event & metric logging
│   │   ├── Scheduler.h/.cpp     # Discrete-time simulation loop
│   │   └── main.cpp             # CLI entrypoint
│   └── tests/
│       ├── test_heap.cpp        # Randomized heap stress tests
│       └── test_scheduler.cpp   # Hand-checked scenario tests
├── scenarios/                   # Sample test scenarios
│   ├── basic.txt                # Sanity check: all tasks meet deadlines
│   ├── overload.txt             # Bottleneck workload causing misses
│   ├── priority_change.txt      # Mid-run priority shift & preemption
│   └── starvation.txt           # Demonstrates aging preventing starvation
├── ui/                          # Python / Streamlit Dashboard
│   ├── app.py                   # Main Streamlit application
│   ├── labels.py                # UI label mappings for themes
│   ├── engine_bridge.py         # Subprocess bridge to scheduler.exe
│   ├── generator.py             # Seeded random scenario generator
│   ├── charts.py                # Plotly Gantt, queue & comparison charts
│   ├── components.py            # KPI cards, queue cards & worker lanes
│   ├── styles.css               # Control-room dark theme stylesheet
│   └── .streamlit/
│       └── config.toml          # Streamlit theme configuration
└── docs/
    └── report-outline.md        # Detailed academic report & analysis
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **C++ Compiler**: `g++` with C++17 support (MinGW on Windows or GCC/Clang on Linux/macOS).
- **Python**: Python 3.9+ with `pip`.

### 1. Build the Engine

**On Windows:**
```cmd
cd engine
build.bat
```
*Or manually:*
```cmd
g++ -std=c++17 -O2 -Iengine/src engine/src/Scenario.cpp engine/src/Logger.cpp engine/src/Scheduler.cpp engine/src/main.cpp -o C:\MinGW\bin\scheduler.exe
```

**On Linux / macOS:**
```bash
cd engine
make
```

### 2. Run the C++ Test Suites
Verify heap invariants and scenario logic:
```cmd
REM Run heap unit tests (15,000 randomized operations against oracle)
g++ -std=c++17 -O2 -Iengine/src engine/tests/test_heap.cpp -o C:\MinGW\bin\test_heap_run.exe
C:\MinGW\bin\test_heap_run.exe

REM Run scenario integration tests
g++ -std=c++17 -O2 -Iengine/src engine/src/Scenario.cpp engine/src/Logger.cpp engine/src/Scheduler.cpp engine/tests/test_scheduler.cpp -o C:\MinGW\bin\test_scheduler_run.exe
C:\MinGW\bin\test_scheduler_run.exe
```

### 3. Launch the Streamlit Dashboard
From the project root:
```cmd
python -m streamlit run ui/app.py
```
Open `http://localhost:8501` in your browser.

---

## 🎬 Demo Script (3-Minute Walkthrough)

1. **Basic Sanity Check**:
   - In the sidebar, select preset `Basic (Sanity Check)` and click **Apply Preset**.
   - Click **Run Simulation**.
   - Navigate to **Tab 3 · Results**: Observe that all 4 tasks finish on time with $0\%$ miss rate and inspect the Gantt chart.
2. **Overload & Miss Detection**:
   - Select preset `Overload (Forces Misses)` and click **Apply Preset**.
   - Click **Run Simulation**.
   - Navigate to **Tab 2 · Replay**: Scrub through time ticks $t = 0 \dots 10$. Notice how cards turn red as their deadlines near, and overdue tasks trigger `MISS` notifications.
3. **Dynamic Priority Shift & Preemption**:
   - Select preset `Priority Change & Preemption` and click **Apply Preset**.
   - Click **Run Simulation**.
   - Observe in the replay that Task 3 is initially at the back of the queue (P5), but at tick $t = 4$, a `PRIORITY_CHANGE` boosts it to P1, triggering a `PREEMPT` event that immediately displaces the running task.
4. **Multi-Policy Benchmark**:
   - Navigate to **Tab 4 · Policy Comparison**.
   - Click **Benchmark All Policies**.
   - Compare miss rates and average wait times between `PRIORITY`, `EDF`, `HYBRID`, and `LST` on the same workload.
