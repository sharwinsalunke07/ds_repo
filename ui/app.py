import os
import sys
import time
import json
from typing import Dict, Any, List, Tuple
import pandas as pd
import streamlit as st

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from labels import THEMES, get_label, generate_theme_css, resolve_theme_key
from engine_bridge import build_scenario_text, run_simulation
from generator import generate_random_scenario
from charts import (
    create_gantt_chart,
    create_queue_length_chart,
    create_per_priority_miss_chart,
    create_policy_comparison_chart
)
from components import (
    render_theme_banner,
    render_kpi_card,
    render_queue_task_card,
    render_worker_lane
)

# Page configuration
st.set_page_config(
    page_title="Real-Time Task Scheduler",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom base CSS
css_path = os.path.join(current_dir, "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =============================================================
# SCENARIO PRESETS & EXPLANATIONS (Requirement 1 & 2)
# =============================================================
PRESET_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "🌿 Normal Day — Smooth Task Scheduling": {
        "explanation": "Shows normal priority-based scheduling with two workers. Tasks arrive steadily and complete without missed deadlines.",
        "theme": "Serenity",
        "workers": 2,
        "policy": "PRIORITY",
        "preemptive": False,
        "aging": False,
        "aging_interval": 5,
        "miss_action": "DROP",
        "max_time": 30,
        "tasks": pd.DataFrame([
            {"Task ID": 1, "Task Name": "Morning Triage",       "Arrival Time": 0, "Burst Time": 4, "Deadline": 10, "Priority": 3},
            {"Task ID": 2, "Task Name": "Urgent Medical Check",  "Arrival Time": 1, "Burst Time": 3, "Deadline": 8,  "Priority": 1},
            {"Task ID": 3, "Task Name": "Lab Diagnostics",      "Arrival Time": 2, "Burst Time": 5, "Deadline": 15, "Priority": 2},
            {"Task ID": 4, "Task Name": "Prescription Refill",  "Arrival Time": 4, "Burst Time": 2, "Deadline": 12, "Priority": 4},
        ]),
        "prio_changes": []
    },
    "🚑 Emergency Arrival — Urgent Task Preempts Queue": {
        "explanation": "Shows how a task that becomes P1 at tick 4 can interrupt a lower-priority running task.",
        "theme": "Emergency",
        "workers": 2,
        "policy": "PRIORITY",
        "preemptive": True,
        "aging": False,
        "aging_interval": 5,
        "miss_action": "DROP",
        "max_time": 30,
        "tasks": pd.DataFrame([
            {"Task ID": 1, "Task Name": "Routine Check",       "Arrival Time": 0, "Burst Time": 6, "Deadline": 12, "Priority": 3},
            {"Task ID": 2, "Task Name": "High Attention Case", "Arrival Time": 1, "Burst Time": 4, "Deadline": 10, "Priority": 2},
            {"Task ID": 3, "Task Name": "Standard Request",    "Arrival Time": 2, "Burst Time": 5, "Deadline": 14, "Priority": 4},
            {"Task ID": 4, "Task Name": "Escalated Emergency", "Arrival Time": 0, "Burst Time": 5, "Deadline": 15, "Priority": 3},
        ]),
        "prio_changes": [
            {"Event Tick": 4, "Task ID": 4, "New Priority": 1}
        ]
    },
    "☕ Busy Day — Prevent Low-Priority Starvation": {
        "explanation": "Shows aging: a low-priority waiting task gradually gains priority so it eventually gets executed.",
        "theme": "Personal",
        "workers": 1,
        "policy": "HYBRID",
        "preemptive": True,
        "aging": True,
        "aging_interval": 3,
        "miss_action": "DROP",
        "max_time": 35,
        "tasks": pd.DataFrame([
            {"Task ID": 1, "Task Name": "Client Briefing",      "Arrival Time": 0, "Burst Time": 3, "Deadline": 6,  "Priority": 1},
            {"Task ID": 2, "Task Name": "Production Hotfix",    "Arrival Time": 1, "Burst Time": 4, "Deadline": 10, "Priority": 1},
            {"Task ID": 3, "Task Name": "Code Review",          "Arrival Time": 2, "Burst Time": 2, "Deadline": 12, "Priority": 2},
            {"Task ID": 4, "Task Name": "Sprint Documentation", "Arrival Time": 3, "Burst Time": 3, "Deadline": 16, "Priority": 3},
            {"Task ID": 5, "Task Name": "Long-Term Backlog",    "Arrival Time": 5, "Burst Time": 4, "Deadline": 24, "Priority": 5},
        ]),
        "prio_changes": []
    },
    "🎨 Deadline Rush — Earliest Deadline First": {
        "explanation": "Shows EDF scheduling with three workers. Tasks with the earliest deadlines run first, even if their priority is low.",
        "theme": "Studio",
        "workers": 3,
        "policy": "EDF",
        "preemptive": True,
        "aging": False,
        "aging_interval": 5,
        "miss_action": "DROP",
        "max_time": 35,
        "tasks": pd.DataFrame([
            {"Task ID": 1, "Task Name": "Urgent Render Job",  "Arrival Time": 0, "Burst Time": 2, "Deadline": 5,  "Priority": 1},
            {"Task ID": 2, "Task Name": "Short SLA Sync",     "Arrival Time": 0, "Burst Time": 3, "Deadline": 7,  "Priority": 1},
            {"Task ID": 3, "Task Name": "Audio Production",   "Arrival Time": 1, "Burst Time": 5, "Deadline": 12, "Priority": 2},
            {"Task ID": 4, "Task Name": "Asset Compression",  "Arrival Time": 2, "Burst Time": 6, "Deadline": 18, "Priority": 3},
            {"Task ID": 5, "Task Name": "Background Archive", "Arrival Time": 4, "Burst Time": 7, "Deadline": 28, "Priority": 5},
        ]),
        "prio_changes": []
    },
    "⚠️ Overloaded System — Handle Missed Deadlines": {
        "explanation": "Shows an overloaded system with multiple workers where more work arrives than can be completed before the deadlines.",
        "theme": "Overload",
        "workers": 2,
        "policy": "EDF",
        "preemptive": True,
        "aging": False,
        "aging_interval": 5,
        "miss_action": "DROP",
        "max_time": 40,
        "tasks": pd.DataFrame([
            {"Task ID": 1, "Task Name": "Priority Service Order", "Arrival Time": 0, "Burst Time": 8, "Deadline": 10, "Priority": 2},
            {"Task ID": 2, "Task Name": "Emergency Escalation",   "Arrival Time": 0, "Burst Time": 8, "Deadline": 9,  "Priority": 1},
            {"Task ID": 3, "Task Name": "Database Migration",     "Arrival Time": 1, "Burst Time": 7, "Deadline": 11, "Priority": 3},
            {"Task ID": 4, "Task Name": "Critical Patch Deploy",  "Arrival Time": 2, "Burst Time": 6, "Deadline": 8,  "Priority": 1},
            {"Task ID": 5, "Task Name": "Core Gateway Failure",   "Arrival Time": 3, "Burst Time": 7, "Deadline": 10, "Priority": 1},
            {"Task ID": 6, "Task Name": "Full Server Backup",     "Arrival Time": 4, "Burst Time": 9, "Deadline": 14, "Priority": 4},
        ]),
        "prio_changes": []
    }
}

PRESET_KEYS = list(PRESET_SCENARIOS.keys())

# =============================================================
# HELPER FUNCTIONS & VALIDATION (Requirement 8)
# =============================================================
def load_preset_into_state(preset_name: str):
    """Loads a preset's full configuration and data into session_state."""
    p = PRESET_SCENARIOS[preset_name]
    st.session_state.tasks_df = p["tasks"].copy()
    st.session_state.prio_changes = [dict(x) for x in p["prio_changes"]]
    st.session_state.workers_val = int(p["workers"])
    st.session_state.policy_val = str(p["policy"])
    st.session_state.preemptive_val = bool(p["preemptive"])
    st.session_state.aging_val = bool(p["aging"])
    st.session_state.aging_interval_val = int(p["aging_interval"])
    st.session_state.miss_action_val = str(p["miss_action"])
    st.session_state.max_time_val = int(p["max_time"])

    # Synchronize widget state keys so controls on Setup screen reflect the preset
    st.session_state["setup_workers_val"] = int(p["workers"])
    st.session_state["setup_policy_val"] = str(p["policy"])
    st.session_state["setup_preempt_val"] = bool(p["preemptive"])
    st.session_state["setup_aging_val"] = bool(p["aging"])
    st.session_state["setup_aging_int_val"] = int(p["aging_interval"])
    st.session_state["setup_miss_act_val"] = str(p["miss_action"])
    st.session_state["setup_max_time_val"] = int(p["max_time"])

    # Increment editor nonce to reload fresh preset data into dynamic data editors
    st.session_state.editor_nonce = st.session_state.get("editor_nonce", 0) + 1

    if "theme" in p:
        st.session_state.theme_name = p["theme"]
    st.session_state.simulation_results = None
    st.session_state.replay_tick = 0
    st.session_state.last_loaded_preset = preset_name

def validate_scenario(tasks_df: pd.DataFrame, prio_changes: List[Dict[str, Any]], workers: int, max_time: int) -> Tuple[List[str], List[str]]:
    """Performs validation checks per requirement 8."""
    errors = []
    warnings = []

    if tasks_df.empty:
        errors.append("Task table cannot be empty. Please add at least one task.")
        return errors, warnings

    task_ids = []
    latest_arrive = 0
    latest_deadline = 0
    total_burst = 0

    for idx, row in tasks_df.iterrows():
        t_id = row.get("Task ID", row.get("id"))
        t_name = str(row.get("Task Name", row.get("name", f"Task {t_id}")))
        arrive = row.get("Arrival Time", row.get("arrive"))
        burst = row.get("Burst Time", row.get("burst"))
        deadline = row.get("Deadline", row.get("deadline"))
        priority = row.get("Priority", row.get("priority"))

        if any(v is None or pd.isna(v) for v in [t_id, arrive, burst, deadline, priority]):
            errors.append(f"Row {idx + 1}: Contains empty or invalid non-numeric values.")
            continue

        try:
            t_id = int(t_id)
            arrive = int(arrive)
            burst = int(burst)
            deadline = int(deadline)
            priority = int(priority)
        except (ValueError, TypeError):
            errors.append(f"Row {idx + 1}: Values must be integers.")
            continue

        task_ids.append(t_id)
        total_burst += burst
        latest_arrive = max(latest_arrive, arrive)
        latest_deadline = max(latest_deadline, deadline)

        if arrive < 0:
            errors.append(f"Task #{t_id} ('{t_name}'): Arrival time ({arrive}) must be 0 or greater.")
        if burst <= 0:
            errors.append(f"Task #{t_id} ('{t_name}'): Burst time ({burst}) must be strictly greater than 0.")
        if deadline <= arrive:
            errors.append(f"Task #{t_id} ('{t_name}'): Deadline ({deadline}) must be strictly greater than arrival time ({arrive}).")
        if not (1 <= priority <= 5):
            errors.append(f"Task #{t_id} ('{t_name}'): Priority ({priority}) must be between 1 and 5.")

    # Unique Task IDs
    if len(task_ids) != len(set(task_ids)):
        dups = [item for item in set(task_ids) if task_ids.count(item) > 1]
        errors.append(f"Duplicate Task ID(s) detected: {dups}. Every Task ID must be strictly unique.")

    # Validate Priority Changes
    valid_ids = set(task_ids)
    for p_idx, pc in enumerate(prio_changes):
        pc_id = pc.get("Task ID", pc.get("id"))
        pc_tick = pc.get("Event Tick", pc.get("time"))
        pc_prio = pc.get("New Priority", pc.get("new_priority"))

        if pc_id is None or pc_tick is None or pc_prio is None:
            errors.append(f"Priority Change Row {p_idx + 1}: Contains empty fields.")
            continue

        try:
            pc_id = int(pc_id)
            pc_tick = int(pc_tick)
            pc_prio = int(pc_prio)
        except (ValueError, TypeError):
            errors.append(f"Priority Change Row {p_idx + 1}: Values must be integers.")
            continue

        if pc_id not in valid_ids:
            errors.append(f"Priority Change for Task ID {pc_id}: Task ID does not match any existing task in the task table.")
        if pc_tick < 0:
            errors.append(f"Priority Change for Task ID {pc_id}: Event tick ({pc_tick}) must be 0 or greater.")
        if not (1 <= pc_prio <= 5):
            errors.append(f"Priority Change for Task ID {pc_id}: New Priority ({pc_prio}) must be between 1 and 5.")

    # Max Simulation Time validation
    if max_time <= latest_arrive:
        errors.append(f"Maximum Simulation Time ({max_time}) must be strictly greater than the latest task arrival time ({latest_arrive}).")

    # Capacity Warning Check (Total burst vs worker capacity before latest deadline)
    available_capacity = workers * latest_deadline
    if total_burst > available_capacity and not errors:
        warnings.append(
            "Warning: Total burst demand exceeds available worker capacity before the deadlines. Some tasks may miss their deadlines."
        )

    return errors, warnings

# =============================================================
# INITIALIZE SESSION STATE (Requirement 6)
# =============================================================
if "selected_preset" not in st.session_state or st.session_state.selected_preset not in PRESET_KEYS:
    st.session_state.selected_preset = PRESET_KEYS[0]

if "editor_nonce" not in st.session_state:
    st.session_state.editor_nonce = 1

if "last_loaded_preset" not in st.session_state or st.session_state.last_loaded_preset != st.session_state.selected_preset:
    load_preset_into_state(st.session_state.selected_preset)

if "theme_name" not in st.session_state:
    st.session_state["theme_name"] = "Serenity"
if "is_bright" not in st.session_state:
    st.session_state["is_bright"] = False
if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None
if "replay_tick" not in st.session_state:
    st.session_state.replay_tick = 0

# Resolve active theme and mode
theme_name = resolve_theme_key(st.session_state.get("theme_name", "Serenity"))
st.session_state["theme_name"] = theme_name
current_theme = THEMES.get(theme_name, THEMES["Serenity"])
is_bright = st.session_state.get("is_bright", False)

card_bg = current_theme["bright_card_bg"] if is_bright else current_theme["card_bg"]
card_border = current_theme["bright_card_border"] if is_bright else current_theme["card_border"]

# Inject dynamic CSS rules
st.markdown(generate_theme_css(theme_name, is_bright=is_bright), unsafe_allow_html=True)

# Preset change handlers to synchronize sidebar and setup tab dropdowns
def on_sidebar_preset_change():
    sel = st.session_state.sidebar_preset_select
    st.session_state.selected_preset = sel
    st.session_state.setup_preset_select = sel
    load_preset_into_state(sel)

def on_setup_preset_change():
    sel = st.session_state.setup_preset_select
    st.session_state.selected_preset = sel
    st.session_state.sidebar_preset_select = sel
    load_preset_into_state(sel)

# =============================================================
# SIDEBAR CONTROLS & PRESET SELECTOR (Requirement 1 & 2)
# =============================================================
with st.sidebar:
    st.title("🌿 Control Room")

    # Bright Mode Toggle
    bright_toggle = st.toggle("☀️ Bright Mode", value=is_bright)
    if bright_toggle != is_bright:
        st.session_state["is_bright"] = bright_toggle
        st.rerun()

    # Aesthetic Theme Selector
    theme_keys = list(THEMES.keys())
    theme_idx = theme_keys.index(theme_name) if theme_name in theme_keys else 0
    sidebar_theme = st.selectbox(
        "Aesthetic Theme",
        theme_keys,
        index=theme_idx,
        format_func=lambda k: f"{THEMES[k]['icon']} {THEMES[k]['name']}"
    )
    if sidebar_theme != theme_name:
        st.session_state["theme_name"] = sidebar_theme
        st.rerun()

    st.caption(f"{current_theme['icon']} *{current_theme['description']}*")

    st.markdown("---")
    st.subheader("Load Preset Scenario")

    # Instant preset selection dropdown in sidebar (Requirement 1 & 6)
    st.selectbox(
        "Load Preset Scenario",
        PRESET_KEYS,
        index=PRESET_KEYS.index(st.session_state.selected_preset),
        key="sidebar_preset_select",
        on_change=on_sidebar_preset_change,
        label_visibility="collapsed"
    )

    # Immediate preset explanation (Requirement 2)
    st.info(PRESET_SCENARIOS[st.session_state.selected_preset]["explanation"])

    st.markdown("---")
    st.subheader("Active Configuration")

    # Live configuration summary badge in sidebar
    cur_p = PRESET_SCENARIOS[st.session_state.selected_preset]
    w_disp = st.session_state.get("setup_workers_val", st.session_state.get("workers_val", cur_p["workers"]))
    pol_disp = st.session_state.get("setup_policy_val", st.session_state.get("policy_val", cur_p["policy"]))
    pre_disp = "Enabled" if st.session_state.get("setup_preempt_val", st.session_state.get("preemptive_val", cur_p["preemptive"])) else "Disabled"
    ag_bool = st.session_state.get("setup_aging_val", st.session_state.get("aging_val", cur_p["aging"]))
    ag_int = st.session_state.get("setup_aging_int_val", st.session_state.get("aging_interval_val", cur_p["aging_interval"]))
    ag_disp = f"Every {ag_int}t" if ag_bool else "Disabled"
    miss_disp = st.session_state.get("setup_miss_act_val", st.session_state.get("miss_action_val", cur_p["miss_action"]))
    max_disp = st.session_state.get("setup_max_time_val", st.session_state.get("max_time_val", cur_p["max_time"]))

    st.markdown(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 12px 14px; font-size: 0.88rem; line-height: 1.6;">
        <b>👷 Workers:</b> {w_disp}<br>
        <b>⚖️ Policy:</b> {pol_disp}<br>
        <b>🔄 Preemption:</b> {pre_disp}<br>
        <b>⏳ Aging:</b> {ag_disp}<br>
        <b>⚡ Miss Action:</b> {miss_disp}<br>
        <b>⏱️ Max Horizon:</b> {max_disp} ticks
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    sidebar_run_btn = st.button("🚀 Run Simulation", key="sidebar_run_sim_btn", use_container_width=True)

# Active configuration dictionary
config = {
    "workers": int(st.session_state.get("setup_workers_val", st.session_state.get("workers_val", 2))),
    "policy": str(st.session_state.get("setup_policy_val", st.session_state.get("policy_val", "PRIORITY"))),
    "preemptive": bool(st.session_state.get("setup_preempt_val", st.session_state.get("preemptive_val", False))),
    "aging": bool(st.session_state.get("setup_aging_val", st.session_state.get("aging_val", False))),
    "aging_interval": int(st.session_state.get("setup_aging_int_val", st.session_state.get("aging_interval_val", 5))),
    "miss_action": str(st.session_state.get("setup_miss_act_val", st.session_state.get("miss_action_val", "DROP"))),
    "max_time": int(st.session_state.get("setup_max_time_val", st.session_state.get("max_time_val", 30))),
    "hybrid_weight": 3
}

# =============================================================
# MAIN UI: THEME SWITCHER & HEADER BANNER
# =============================================================
row_switch_header, row_mode_toggle = st.columns([4, 1])
with row_switch_header:
    st.markdown("<div style='margin-bottom: 8px; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;'>🎨 Human-Crafted Aesthetic Themes</div>", unsafe_allow_html=True)
with row_mode_toggle:
    btn_mode_label = "🌙 Dark Mode" if is_bright else "☀️ Bright Mode"
    if st.button(btn_mode_label, key="main_bright_mode_toggle_btn", use_container_width=True):
        st.session_state["is_bright"] = not is_bright
        st.rerun()

theme_btn_cols = st.columns(len(THEMES))
for idx, (t_key, t_data) in enumerate(THEMES.items()):
    with theme_btn_cols[idx]:
        is_active = (theme_name == t_key)
        btn_label = f"{t_data['icon']} {t_data['name'].split('&')[0].strip()}" + (" ⭐️" if is_active else "")
        btn_type = "primary" if is_active else "secondary"
        if st.button(btn_label, key=f"main_theme_btn_{t_key}", use_container_width=True, type=btn_type):
            st.session_state["theme_name"] = t_key
            st.rerun()

# Prominent Themed Header Banner
st.markdown(render_theme_banner(current_theme, is_bright=is_bright), unsafe_allow_html=True)

# =============================================================
# VALIDATION EXECUTION HELPER
# =============================================================
def trigger_run_simulation():
    errors, warnings = validate_scenario(
        st.session_state.tasks_df,
        st.session_state.prio_changes,
        config["workers"],
        config["max_time"]
    )
    if errors:
        for err in errors:
            st.error(f"❌ {err}")
        return False
    try:
        scenario_text = build_scenario_text(config, st.session_state.tasks_df, st.session_state.prio_changes)
        events, metrics = run_simulation(scenario_text)
        st.session_state.simulation_results = {
            "events": events,
            "metrics": metrics,
            "scenario_text": scenario_text,
            "config": config
        }
        st.session_state.replay_tick = 0
        st.toast("Simulation completed successfully!", icon="✅")
        return True
    except Exception as e:
        st.error(f"Error running simulation: {str(e)}")
        return False

if sidebar_run_btn:
    trigger_run_simulation()

# =============================================================
# MAIN NAVIGATION TABS
# =============================================================
tab_setup, tab_replay, tab_results, tab_compare = st.tabs([
    f"📋 Tab 1 · Setup & Presets",
    "▶️ Tab 2 · Replay Dashboard",
    "📊 Tab 3 · Results & Gantt",
    "⚖️ Tab 4 · Policy Comparison"
])

# -------------------------------------------------------------
# TAB 1: SETUP SCREEN (Requirements 1, 2, 3, 4, 5, 6, 7, 8)
# -------------------------------------------------------------
with tab_setup:
    st.markdown("### 🎯 Scenario Preset Selection")
    
    # Preset Selector Dropdown directly on Setup Screen (Requirement 1 & 6)
    c_pre1, c_pre2 = st.columns([4, 1])
    with c_pre1:
        st.selectbox(
            "Load Preset Scenario",
            PRESET_KEYS,
            index=PRESET_KEYS.index(st.session_state.selected_preset),
            key="setup_preset_select",
            on_change=on_setup_preset_change,
            label_visibility="collapsed"
        )
    with c_pre2:
        if st.button("🔄 Reset Preset", use_container_width=True, help="Revert edits back to this preset's original values"):
            load_preset_into_state(st.session_state.selected_preset)
            st.toast("Preset reset to default values", icon="🔄")
            st.rerun()

    # Immediate preset explanation (Requirement 2)
    selected_explanation = PRESET_SCENARIOS[st.session_state.selected_preset]["explanation"]
    st.info(f"💡 **Preset Focus:** {selected_explanation}")

    st.markdown("---")

    # Editable Task Table (Requirement 3)
    st.markdown("### 📋 Editable Tasks Table")
    st.caption("Edit existing tasks, add new rows at the bottom, or select rows and press Delete.")

    # Ensure canonical columns exist in DataFrame
    required_cols = ["Task ID", "Task Name", "Arrival Time", "Burst Time", "Deadline", "Priority"]
    tasks_df_display = st.session_state.tasks_df.copy()

    # Normalize column names if needed
    col_mapping = {
        "id": "Task ID", "name": "Task Name", "arrive": "Arrival Time",
        "burst": "Burst Time", "deadline": "Deadline", "priority": "Priority"
    }
    for old_c, new_c in col_mapping.items():
        if old_c in tasks_df_display.columns and new_c not in tasks_df_display.columns:
            tasks_df_display[new_c] = tasks_df_display[old_c]

    # Ensure all required columns are present
    for rc in required_cols:
        if rc not in tasks_df_display.columns:
            if rc == "Task Name":
                tasks_df_display[rc] = [f"Task {row.get('Task ID', idx+1)}" for idx, row in tasks_df_display.iterrows()]
            else:
                tasks_df_display[rc] = 0

    tasks_df_display = tasks_df_display[required_cols]

    editor_key = f"task_editor_{st.session_state.get('editor_nonce', 0)}"
    edited_tasks = st.data_editor(
        tasks_df_display,
        num_rows="dynamic",
        use_container_width=True,
        key=editor_key,
        column_config={
            "Task ID": st.column_config.NumberColumn("Task ID", min_value=1, step=1, required=True),
            "Task Name": st.column_config.TextColumn("Task Name", required=True),
            "Arrival Time": st.column_config.NumberColumn("Arrival Time", min_value=0, step=1, required=True),
            "Burst Time": st.column_config.NumberColumn("Burst Time", min_value=1, step=1, required=True),
            "Deadline": st.column_config.NumberColumn("Deadline", min_value=1, step=1, required=True),
            "Priority": st.column_config.NumberColumn("Priority (1=Highest, 5=Lowest)", min_value=1, max_value=5, step=1, required=True)
        }
    )
    # Persist user edits in session state (Requirement 6)
    st.session_state.tasks_df = edited_tasks

    st.markdown("---")

    # Priority-Change Events Table (Requirement 5)
    st.markdown("### ⚡ Scheduled Priority-Change Events")
    prio_list = st.session_state.prio_changes
    prio_df_display = pd.DataFrame(prio_list) if prio_list else pd.DataFrame(columns=["Event Tick", "Task ID", "New Priority"])

    # Normalize column names for priority changes
    pc_mapping = {"time": "Event Tick", "id": "Task ID", "new_priority": "New Priority"}
    for old_k, new_k in pc_mapping.items():
        if old_k in prio_df_display.columns and new_k not in prio_df_display.columns:
            prio_df_display[new_k] = prio_df_display[old_k]

    for req_pc in ["Event Tick", "Task ID", "New Priority"]:
        if req_pc not in prio_df_display.columns:
            prio_df_display[req_pc] = pd.Series(dtype="int64")

    prio_df_display = prio_df_display[["Event Tick", "Task ID", "New Priority"]]

    if prio_df_display.empty:
        st.caption("ℹ️ *No priority-change events in this preset.* (You can add dynamic events below if desired)")

    prio_editor_key = f"prio_editor_{st.session_state.get('editor_nonce', 0)}"
    edited_prio = st.data_editor(
        prio_df_display,
        num_rows="dynamic",
        use_container_width=True,
        key=prio_editor_key,
        column_config={
            "Event Tick": st.column_config.NumberColumn("Event Tick", min_value=0, step=1, required=True),
            "Task ID": st.column_config.NumberColumn("Task ID", min_value=1, step=1, required=True),
            "New Priority": st.column_config.NumberColumn("New Priority (1-5)", min_value=1, max_value=5, step=1, required=True)
        }
    )
    
    clean_prio_changes = []
    for r in edited_prio.to_dict(orient="records"):
        if pd.notna(r.get("Event Tick")) and pd.notna(r.get("Task ID")) and pd.notna(r.get("New Priority")):
            try:
                clean_prio_changes.append({
                    "Event Tick": int(r["Event Tick"]),
                    "Task ID": int(r["Task ID"]),
                    "New Priority": int(r["New Priority"])
                })
            except (ValueError, TypeError):
                continue
    st.session_state.prio_changes = clean_prio_changes

    st.markdown("---")

    # Scheduler Settings (Requirement 4)
    st.markdown("### ⚙️ Scheduler Settings")
    st.caption("These controls are pre-filled from the selected preset and remain fully editable.")

    c_set1, c_set2, c_set3, c_set4 = st.columns(4)
    with c_set1:
        s_workers = st.number_input(
            "Number of Workers",
            min_value=1, max_value=8,
            value=int(st.session_state.get("workers_val", 2)),
            key="setup_workers_val"
        )
        st.session_state.workers_val = int(s_workers)

        s_policy = st.selectbox(
            "Scheduling Policy",
            ["PRIORITY", "EDF", "HYBRID", "LST"],
            index=["PRIORITY", "EDF", "HYBRID", "LST"].index(st.session_state.get("policy_val", "PRIORITY")),
            key="setup_policy_val"
        )
        st.session_state.policy_val = str(s_policy)

    with c_set2:
        s_preempt = st.toggle(
            "Preemption: Enabled",
            value=bool(st.session_state.get("preemptive_val", False)),
            key="setup_preempt_val"
        )
        st.session_state.preemptive_val = bool(s_preempt)

        s_aging = st.toggle(
            "Aging: Enabled",
            value=bool(st.session_state.get("aging_val", False)),
            key="setup_aging_val"
        )
        st.session_state.aging_val = bool(s_aging)

    with c_set3:
        s_aging_int = 5
        if s_aging:
            s_aging_int = st.number_input(
                "Aging Interval (Ticks)",
                min_value=1, max_value=20,
                value=int(st.session_state.get("aging_interval_val", 5)),
                key="setup_aging_int_val"
            )
        st.session_state.aging_interval_val = int(s_aging_int)

        s_miss_act = st.radio(
            "Missed-Deadline Action",
            ["DROP", "CONTINUE"],
            index=0 if st.session_state.get("miss_action_val", "DROP") == "DROP" else 1,
            key="setup_miss_act_val",
            horizontal=True
        )
        st.session_state.miss_action_val = str(s_miss_act)

    with c_set4:
        s_max_time = st.number_input(
            "Maximum Simulation Time",
            min_value=10, max_value=200,
            value=int(st.session_state.get("max_time_val", 30)),
            key="setup_max_time_val"
        )
        st.session_state.max_time_val = int(s_max_time)

    # Keep config synced with current settings
    config["workers"] = st.session_state.workers_val
    config["policy"] = st.session_state.policy_val
    config["preemptive"] = st.session_state.preemptive_val
    config["aging"] = st.session_state.aging_val
    config["aging_interval"] = st.session_state.aging_interval_val
    config["miss_action"] = st.session_state.miss_action_val
    config["max_time"] = st.session_state.max_time_val

    st.markdown("---")

    # Scenario Summary (Requirement 7)
    st.markdown("### 📊 Scenario Summary")

    total_tasks_count = len(st.session_state.tasks_df)
    burst_numeric = pd.to_numeric(st.session_state.tasks_df.get("Burst Time", st.session_state.tasks_df.get("burst", pd.Series([0]))), errors='coerce').fillna(0)
    arrive_numeric = pd.to_numeric(st.session_state.tasks_df.get("Arrival Time", st.session_state.tasks_df.get("arrive", pd.Series([0]))), errors='coerce').fillna(0)
    dl_numeric = pd.to_numeric(st.session_state.tasks_df.get("Deadline", st.session_state.tasks_df.get("deadline", pd.Series([0]))), errors='coerce').fillna(0)

    total_burst_val = int(burst_numeric.sum()) if not burst_numeric.empty else 0
    earliest_arr_val = int(arrive_numeric.min()) if not arrive_numeric.empty else 0
    latest_dl_val = int(dl_numeric.max()) if not dl_numeric.empty else 0
    num_prio_events = len(st.session_state.prio_changes)

    preempt_text = "Enabled" if config["preemptive"] else "Disabled"
    aging_text = f"Enabled (interval: {config['aging_interval']} ticks)" if config["aging"] else "Disabled"

    # Display clean scenario summary items
    sum_c1, sum_c2, sum_c3, sum_c4 = st.columns(4)
    with sum_c1:
        st.markdown(render_kpi_card("Selected Preset", st.session_state.selected_preset.split("—")[0].strip(), "Active scenario", "🔖", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(render_kpi_card("Total Tasks", str(total_tasks_count), f"Total burst: {total_burst_val} ticks", "📋", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)

    with sum_c2:
        st.markdown(render_kpi_card("Workers Assigned", f"{config['workers']} Worker(s)", "Parallel execution", "👷", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(render_kpi_card("Scheduling Policy", config["policy"], f"Miss Action: {config['miss_action']}", "⚖️", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)

    with sum_c3:
        st.markdown(render_kpi_card("Preemption", preempt_text, f"Aging: {aging_text}", "🔄", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(render_kpi_card("Arrival Window", f"Earliest: t = {earliest_arr_val}", f"Latest Deadline: {latest_dl_val} ticks", "⏱️", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)

    with sum_c4:
        st.markdown(render_kpi_card("Priority Shifts", f"{num_prio_events} Event(s)", "Dynamic escalations", "⚡", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(render_kpi_card("Max Horizon", f"{config['max_time']} Ticks", "Simulation limit", "🏁", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)

    # Detailed structured summary table
    st.markdown(f"""
    <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 14px 18px; margin-top: 14px; font-size: 0.92rem; line-height: 1.7;">
        <b>📌 Scenario Summary Checklist:</b><br>
        • <b>Selected Preset Name:</b> {st.session_state.selected_preset}<br>
        • <b>Number of Workers:</b> {config['workers']}<br>
        • <b>Scheduling Policy:</b> {config['policy']}<br>
        • <b>Preemption Status:</b> {preempt_text}<br>
        • <b>Aging Status:</b> {aging_text}<br>
        • <b>Missed-Deadline Action:</b> {config['miss_action']}<br>
        • <b>Total Tasks:</b> {total_tasks_count}<br>
        • <b>Total Burst Time:</b> {total_burst_val} ticks<br>
        • <b>Earliest Arrival Time:</b> tick {earliest_arr_val}<br>
        • <b>Latest Deadline:</b> tick {latest_dl_val}<br>
        • <b>Number of Priority-Change Events:</b> {num_prio_events}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Validation & Execution (Requirement 8)
    val_errors, val_warnings = validate_scenario(
        st.session_state.tasks_df,
        st.session_state.prio_changes,
        config["workers"],
        config["max_time"]
    )

    if val_errors:
        for err in val_errors:
            st.error(f"❌ {err}")
    elif val_warnings:
        for wrn in val_warnings:
            st.warning(f"⚠️ {wrn}")

    # Main Run Simulation Button
    run_disabled = bool(val_errors)
    c_btn1, c_btn2 = st.columns([3, 1])
    with c_btn1:
        if run_disabled:
            st.button("🚫 Fix Validation Errors to Run Simulation", disabled=True, use_container_width=True)
        else:
            if st.button("🚀 Run Simulation Now", use_container_width=True, key="setup_tab_run_btn"):
                if trigger_run_simulation():
                    st.info("Simulation completed! Head over to **▶️ Tab 2 · Replay Dashboard** or **📊 Tab 3 · Results & Gantt** to explore the execution.")

# -------------------------------------------------------------
# TAB 2: REPLAY DASHBOARD
# -------------------------------------------------------------
with tab_replay:
    if not st.session_state.simulation_results:
        st.info("👈 Please click **🚀 Run Simulation** in the Setup screen or sidebar to view the interactive replay.")
    else:
        events = st.session_state.simulation_results["events"]
        metrics = st.session_state.simulation_results["metrics"]

        # Collect all TICK snapshots
        tick_snapshots = {ev["t"]: ev for ev in events if ev.get("event") == "TICK"}
        max_sim_t = max(tick_snapshots.keys()) if tick_snapshots else 0

        # Synchronize target tick requested by buttons
        if "target_tick" in st.session_state:
            st.session_state["replay_tick"] = min(max_sim_t, max(0, st.session_state.pop("target_tick")))

        # Time slider and controls
        c_ctrl1, c_ctrl2, c_ctrl3, c_ctrl4, c_ctrl5 = st.columns([5, 1, 1, 1, 1])
        with c_ctrl1:
            current_tick = st.slider(
                "Simulation Time Scrubber",
                min_value=0,
                max_value=max_sim_t,
                key="replay_tick"
            )
        with c_ctrl2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("⏮️ Reset"):
                st.session_state["target_tick"] = 0
                st.rerun()
        with c_ctrl3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("◀️ Prev"):
                cur_t = st.session_state.get("replay_tick", 0)
                if cur_t > 0:
                    st.session_state["target_tick"] = cur_t - 1
                    st.rerun()
        with c_ctrl4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("▶️ Next"):
                cur_t = st.session_state.get("replay_tick", 0)
                if cur_t < max_sim_t:
                    nxt = cur_t + 1
                    st.session_state["target_tick"] = nxt
                    cur_events = [e for e in events if e.get("t") == nxt]
                    for ce in cur_events:
                        if ce.get("event") == "MISS":
                            st.toast(f"⏳ Task #{ce.get('id')} delayed past deadline!", icon="⚠️")
                        elif ce.get("event") == "PREEMPT":
                            st.toast(f"⚡ Task #{ce.get('id')} preempted by #{ce.get('by')}", icon="🔄")
                        elif ce.get("event") == "PRIORITY_CHANGE":
                            st.toast(f"🔼 Task #{ce.get('id')} urgency adjusted to P{ce.get('new')}", icon="📈")
                    st.rerun()
        with c_ctrl5:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("⏭️ End"):
                st.session_state["target_tick"] = max_sim_t
                st.rerun()

        cur_snapshot = tick_snapshots.get(current_tick, {"queue": [], "running": [], "missed": 0, "done": 0})

        # Top KPI Row for current tick with warm humanized cards
        kpi_cols = st.columns(5)
        with kpi_cols[0]:
            st.markdown(render_kpi_card("Current Tick", f"t = {current_tick}", f"Horizon: {max_sim_t} ticks", "⏱️", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(render_kpi_card(get_label(theme_name, "waiting"), f"{len(cur_snapshot['queue'])}", f"Queued {get_label(theme_name, 'tasks')}", "📥", current_theme["accent_light"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        with kpi_cols[2]:
            active_count = sum(1 for tid in cur_snapshot['running'] if tid != -1)
            st.markdown(render_kpi_card(f"Active {get_label(theme_name, 'workers')}", f"{active_count} / {config['workers']}", "Processing in care", "⚙️", current_theme["accent"], card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(render_kpi_card(get_label(theme_name, "done"), f"{cur_snapshot['done']}", "Gently completed on time", "✨", "#4A7C59", card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)
        with kpi_cols[4]:
            st.markdown(render_kpi_card(get_label(theme_name, "missed"), f"{cur_snapshot['missed']}", "Commitments delayed", "⏳", "#C54E44", card_bg, card_border, is_bright=is_bright), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Replay Dual Panels: Queue Panel vs Worker Lanes
        col_queue, col_lanes = st.columns([1, 1])

        # Task lookup dictionary from tasks_df
        task_lookup = {}
        for _, row in st.session_state.tasks_df.iterrows():
            t_id = int(row.get("Task ID", row.get("id", 0)))
            task_lookup[t_id] = dict(row)

        with col_queue:
            st.subheader(f"📥 {get_label(theme_name, 'waiting')} ({len(cur_snapshot['queue'])})")
            st.caption("Ordered by hand-built indexed binary min-heap urgency (root at top)")

            if not cur_snapshot["queue"]:
                st.markdown(f"<div style='color: {'#554C42' if is_bright else '#A89C8E'}; padding: 20px; text-align: center; border: 1px dashed {card_border}; border-radius: 8px;'>Queue is currently empty.</div>", unsafe_allow_html=True)
            else:
                for q_id in cur_snapshot["queue"]:
                    t_info = task_lookup.get(q_id, {"Task ID": q_id, "id": q_id, "Priority": 3, "Deadline": 0, "Burst Time": 0})
                    st.markdown(render_queue_task_card(t_info, current_tick, get_label(theme_name, "task"), card_bg=card_bg, card_border=card_border, is_bright=is_bright), unsafe_allow_html=True)

        with col_lanes:
            st.subheader(f"👷 {get_label(theme_name, 'workers')} Lanes")
            st.caption(f"Active status and execution progress across all {config['workers']} processing units")

            running_ids = cur_snapshot.get("running", [-1] * config["workers"])
            for w_idx in range(config["workers"]):
                active_id = running_ids[w_idx] if w_idx < len(running_ids) else -1
                if active_id == -1:
                    st.markdown(render_worker_lane(w_idx, None, get_label(theme_name, "worker"), card_bg=card_bg, accent_color=current_theme["accent"], accent_light=current_theme["accent_light"], is_bright=is_bright), unsafe_allow_html=True)
                else:
                    t_info = task_lookup.get(active_id, {"Task ID": active_id, "id": active_id, "Priority": 3, "Burst Time": 1, "Deadline": 0})
                    st.markdown(render_worker_lane(w_idx, t_info, get_label(theme_name, "worker"), card_bg=card_bg, accent_color=current_theme["accent"], accent_light=current_theme["accent_light"], is_bright=is_bright), unsafe_allow_html=True)

        # Event ticker at bottom of replay
        st.markdown("---")
        st.subheader("📜 Event Log at Current Tick")
        tick_events = [e for e in events if e.get("t") == current_tick and e.get("event") != "TICK"]
        if not tick_events:
            st.caption(f"No discrete transition events at tick {current_tick} (continuous execution).")
        else:
            for te in tick_events:
                ev_type = te.get("event")
                if ev_type == "ARRIVE":
                    st.info(f"🟢 **ARRIVE**: Task #{te.get('id')} entered system with Priority P{te.get('priority')}, Deadline {te.get('deadline')}")
                elif ev_type == "START":
                    st.success(f"🚀 **START**: Worker {te.get('worker')} started Task #{te.get('id')}")
                elif ev_type == "PREEMPT":
                    st.warning(f"⚡ **PREEMPT**: Task #{te.get('id')} preempted on Worker {te.get('worker')} by urgent Task #{te.get('by')}")
                elif ev_type == "PRIORITY_CHANGE":
                    st.info(f"📈 **PRIORITY_CHANGE**: Task #{te.get('id')} urgency shifted from P{te.get('old')} to P{te.get('new')}")
                elif ev_type == "AGING":
                    st.caption(f"⏳ **AGING**: Task #{te.get('id')} priority gently upgraded from P{te.get('old')} to P{te.get('new')}")
                elif ev_type == "MISS":
                    st.error(f"⏳ **MISS**: Task #{te.get('id')} delayed past deadline {te.get('deadline')}!")
                elif ev_type == "FINISH":
                    st.success(f"🏁 **FINISH**: Worker {te.get('worker')} completed Task #{te.get('id')}")

# -------------------------------------------------------------
# TAB 3: RESULTS & GANTT
# -------------------------------------------------------------
with tab_results:
    if not st.session_state.simulation_results:
        st.info("👈 Please click **🚀 Run Simulation** in the Setup screen or sidebar to compute full summary metrics and Gantt charts.")
    else:
        events = st.session_state.simulation_results["events"]
        m = st.session_state.simulation_results["metrics"]
        cfg = st.session_state.simulation_results["config"]

        st.subheader("📊 Performance Metrics Summary")
        m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)
        with m_col1:
            st.metric(f"Missed Rate", f"{m.get('miss_rate', 0.0) * 100:.1f}%")
        with m_col2:
            st.metric("Avg Waiting Time", f"{m.get('avg_wait', 0.0):.2f} ticks")
        with m_col3:
            st.metric("Avg Turnaround", f"{m.get('avg_turnaround', 0.0):.2f} ticks")
        with m_col4:
            st.metric("Throughput", f"{m.get('throughput', 0.0):.2f} / tick")
        with m_col5:
            st.metric("Max Queue Length", f"{m.get('max_queue', 0)} tasks")
        with m_col6:
            util_list = m.get("utilization", [])
            avg_util = (sum(util_list) / len(util_list)) * 100 if util_list else 0.0
            st.metric("Avg Utilization", f"{avg_util:.1f}%")

        st.markdown("---")
        # Build task names dictionary for the Gantt chart
        task_names_dict = {}
        for _, row in st.session_state.tasks_df.iterrows():
            t_id = int(row.get("Task ID", row.get("id", 0)))
            t_name = str(row.get("Task Name", row.get("name", "")))
            if t_name:
                task_names_dict[t_id] = t_name

        # Gantt Chart with bright mode support and task names
        gantt_fig = create_gantt_chart(events, cfg["workers"], is_bright=is_bright, task_names=task_names_dict)
        st.plotly_chart(gantt_fig, use_container_width=True)

        # Queue Length and Priority Breakdown
        c_ch1, c_ch2 = st.columns(2)
        with c_ch1:
            q_fig = create_queue_length_chart(events, is_bright=is_bright)
            st.plotly_chart(q_fig, use_container_width=True)
        with c_ch2:
            miss_fig = create_per_priority_miss_chart(m.get("per_priority_miss", {}), is_bright=is_bright)
            st.plotly_chart(miss_fig, use_container_width=True)

        # Raw Event Log Export
        with st.expander("📥 Raw JSON-Lines Event Log (Engine Output)"):
            jsonl_str = "\n".join([json.dumps(e) for e in events] + [json.dumps(m)])
            st.download_button(
                "Download Event Log (events.jsonl)",
                data=jsonl_str,
                file_name="events.jsonl",
                mime="text/plain"
            )
            st.code(jsonl_str[:2500] + ("\n... (truncated)" if len(jsonl_str) > 2500 else ""), language="json")

# -------------------------------------------------------------
# TAB 4: POLICY COMPARISON
# -------------------------------------------------------------
with tab_compare:
    st.subheader("⚖️ Multi-Policy Benchmark Evaluation")
    st.caption("Runs this identical scenario configuration through all 4 scheduling policies to compare performance.")

    if st.button("🔄 Benchmark All Policies", use_container_width=True):
        with st.spinner("Executing simulation runs across PRIORITY, EDF, HYBRID, and LST..."):
            policies = ["PRIORITY", "EDF", "HYBRID", "LST"]
            comp_results = []

            for pol in policies:
                test_cfg = dict(config)
                test_cfg["policy"] = pol
                sc_text = build_scenario_text(test_cfg, st.session_state.tasks_df, st.session_state.prio_changes)
                try:
                    _, p_metrics = run_simulation(sc_text)
                    comp_results.append({
                        "policy": pol,
                        "miss_rate": p_metrics.get("miss_rate", 0.0),
                        "missed": p_metrics.get("missed", 0),
                        "done": p_metrics.get("done", 0),
                        "avg_wait": p_metrics.get("avg_wait", 0.0),
                        "avg_turnaround": p_metrics.get("avg_turnaround", 0.0),
                        "throughput": p_metrics.get("throughput", 0.0)
                    })
                except Exception as e:
                    st.error(f"Error evaluating policy {pol}: {e}")

            st.session_state.policy_comparison = comp_results

    if "policy_comparison" in st.session_state and st.session_state.policy_comparison:
        c_data = st.session_state.policy_comparison
        c_df = pd.DataFrame(c_data)

        # Comparison chart with bright mode support
        comp_fig = create_policy_comparison_chart(c_data, is_bright=is_bright)
        st.plotly_chart(comp_fig, use_container_width=True)

        # Comparison table
        st.markdown("**Benchmark Scorecard:**")
        display_df = c_df.copy()
        display_df["miss_rate"] = display_df["miss_rate"].apply(lambda v: f"{v*100:.1f}%")
        display_df["avg_wait"] = display_df["avg_wait"].apply(lambda v: f"{v:.2f}")
        display_df["avg_turnaround"] = display_df["avg_turnaround"].apply(lambda v: f"{v:.2f}")
        display_df["throughput"] = display_df["throughput"].apply(lambda v: f"{v:.2f}")
        st.dataframe(display_df, use_container_width=True)

        # Winner callout
        best_miss = min(c_data, key=lambda x: x["miss_rate"])
        best_wait = min(c_data, key=lambda x: x["avg_wait"])

        st.markdown(f"""
        <div style="background: {card_bg}; border-left: 4px solid {current_theme['accent']}; border: 1px solid {card_border}; border-left-width: 4px; border-radius: 8px; padding: 14px 18px; margin-top: 15px; box-shadow: 0 4px 12px {current_theme['accent_glow']};">
            <b style="color: {current_theme['accent']}; font-size: 1.05rem;">🏆 Policy Analysis & Recommendation:</b><br>
            • <b>Lowest Miss Rate:</b> <span style="color: #4A7C59; font-weight: 700;">{best_miss['policy']}</span> ({best_miss['miss_rate']*100:.1f}% misses)<br>
            • <b>Shortest Average Wait:</b> <span style="color: {current_theme['accent']}; font-weight: 700;">{best_wait['policy']}</span> ({best_wait['avg_wait']:.2f} ticks)<br>
            <i>Insight: EDF prioritizes impending deadlines to minimize missed deadlines under heavy workloads, while HYBRID balances urgent severity with deadline constraints.</i>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Click **Benchmark All Policies** above to evaluate and compare PRIORITY, EDF, HYBRID, and LST on this scenario.")
