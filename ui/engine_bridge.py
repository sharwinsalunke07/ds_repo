import os
import sys
import json
import shutil
import subprocess
import tempfile
from typing import Dict, Any, List, Tuple
import pandas as pd

def find_scheduler_executable() -> str:
    """Finds the compiled scheduler executable or compiles it if necessary."""
    # List of candidate paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        r"C:\MinGW\bin\scheduler.exe",
        os.path.join(project_root, "engine", "scheduler.exe"),
        os.path.join(project_root, "engine", "scheduler"),
        os.path.join(project_root, "scheduler.exe"),
        os.path.join(project_root, "scheduler"),
    ]
    
    which_path = shutil.which("scheduler") or shutil.which("scheduler.exe")
    if which_path:
        candidates.insert(0, which_path)
        
    for p in candidates:
        if os.path.isfile(p) and os.access(p, os.X_OK | os.R_OK):
            return p

    # If not found, attempt automatic build
    compile_cmd = [
        "g++", "-std=c++17", "-O2", "-Wall",
        "-Iengine/src",
        "engine/src/Scenario.cpp",
        "engine/src/Logger.cpp",
        "engine/src/Scheduler.cpp",
        "engine/src/main.cpp",
        "-o", r"C:\MinGW\bin\scheduler.exe" if os.path.isdir(r"C:\MinGW\bin") else "engine/scheduler.exe"
    ]
    try:
        res = subprocess.run(compile_cmd, cwd=project_root, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            target = r"C:\MinGW\bin\scheduler.exe" if os.path.isdir(r"C:\MinGW\bin") else os.path.join(project_root, "engine", "scheduler.exe")
            if os.path.isfile(target):
                return target
    except Exception as e:
        pass

    raise FileNotFoundError(
        "Could not find or automatically compile 'scheduler.exe'. "
        "Please build the engine using 'engine/build.bat' or 'make' in 'engine/'."
    )

def build_scenario_text(config: Dict[str, Any], tasks_df: pd.DataFrame, prio_changes: List[Dict[str, Any]] = None) -> str:
    """Serializes UI configuration and tables into scenario.txt format."""
    lines = []
    
    # CONFIG line
    workers = config.get("workers", 2)
    policy = config.get("policy", "PRIORITY")
    preemptive = 1 if config.get("preemptive", False) else 0
    aging = 1 if config.get("aging", False) else 0
    aging_interval = config.get("aging_interval", 5)
    miss_action = config.get("miss_action", "DROP")
    max_time = config.get("max_time", 50)
    hybrid_weight = config.get("hybrid_weight", 3)

    lines.append(
        f"CONFIG workers={workers} policy={policy} preemptive={preemptive} "
        f"aging={aging} aging_interval={aging_interval} miss_action={miss_action} "
        f"max_time={max_time} hybrid_weight={hybrid_weight}"
    )

    # TASK lines
    for _, row in tasks_df.iterrows():
        t_id = int(row.get("Task ID", row.get("id", 1)))
        arrive = int(row.get("Arrival Time", row.get("arrive", 0)))
        burst = int(row.get("Burst Time", row.get("burst", 1)))
        deadline = int(row.get("Deadline", row.get("deadline", 10)))
        priority = int(row.get("Priority", row.get("priority", 3)))
        lines.append(f"TASK id={t_id} arrive={arrive} burst={burst} deadline={deadline} priority={priority}")

    # PRIORITY_CHANGE lines
    if prio_changes:
        for pc in prio_changes:
            p_time = int(pc.get("Event Tick", pc.get("time", 0)))
            p_id = int(pc.get("Task ID", pc.get("id", 1)))
            p_new = int(pc.get("New Priority", pc.get("new_priority", 1)))
            lines.append(f"PRIORITY_CHANGE time={p_time} id={p_id} new_priority={p_new}")

    return "\n".join(lines) + "\n"

def run_simulation(scenario_text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Runs scheduler with scenario text and returns parsed events and metrics."""
    exe_path = find_scheduler_executable()
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write(scenario_text)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            [exe_path, tmp_path],
            capture_output=True,
            text=True,
            timeout=20
        )
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    if proc.returncode != 0:
        err_msg = proc.stderr.strip() or proc.stdout.strip() or f"Scheduler process failed with code {proc.returncode}"
        raise RuntimeError(f"Engine Execution Error: {err_msg}")

    events = []
    metrics = {}

    for line in proc.stdout.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get("event") == "METRICS":
                metrics = obj
            else:
                events.append(obj)
        except json.JSONDecodeError:
            continue

    if not metrics and not events:
        raise RuntimeError("Engine produced empty or unparseable output.")

    return events, metrics
