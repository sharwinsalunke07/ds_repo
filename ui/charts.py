import plotly.graph_objects as go
from typing import List, Dict, Any
import pandas as pd

# Humanized, artisan priority color palette (natural mineral pigments)
PRIORITY_COLORS = {
    1: "#C54E44",  # Terracotta Carmine (Critical Need)
    2: "#CE6C38",  # Spiced Rust (High Attention)
    3: "#B88728",  # Warm Ochre (Moderate Need)
    4: "#4A7C59",  # Calming Forest Sage (Standard Flow)
    5: "#7C7063"   # Taupe Riverstone (Gentle Horizon)
}

PRIORITY_NAMES = {
    1: "Critical Need",
    2: "High Attention",
    3: "Moderate Need",
    4: "Standard Flow",
    5: "Gentle Horizon"
}

def create_gantt_chart(events: List[Dict[str, Any]], num_workers: int, max_t: int = None, is_bright: bool = False, task_names: Dict[int, str] = None) -> go.Figure:
    """
    Constructs an integer-tick Gantt chart using go.Bar with orientation='h'.
    Satisfies plan.md section 10.4: avoiding px.timeline date requirements.
    Uses humanized tones and rounded borders.
    """
    if task_names is None:
        task_names = {}
    worker_intervals = {w: [] for w in range(num_workers)}
    active_runs = {}
    task_priorities = {}
    task_deadlines = {}
    missed_tasks = set()

    for ev in events:
        e_type = ev.get("event")
        t = ev.get("t", 0)
        t_id = ev.get("id")

        if e_type == "ARRIVE":
            task_priorities[t_id] = ev.get("priority", 3)
            task_deadlines[t_id] = ev.get("deadline", 0)
        elif e_type == "START":
            w = ev.get("worker", 0)
            active_runs[w] = (t_id, t)
        elif e_type in ("FINISH", "PREEMPT"):
            w = ev.get("worker", 0)
            if w in active_runs:
                cur_id, start_t = active_runs.pop(w)
                duration = t - start_t
                if duration > 0:
                    worker_intervals[w].append({
                        "task_id": cur_id,
                        "start": start_t,
                        "duration": duration,
                        "priority": task_priorities.get(cur_id, 3),
                        "deadline": task_deadlines.get(cur_id, 0),
                        "missed": cur_id in missed_tasks
                    })
        elif e_type == "MISS":
            missed_tasks.add(t_id)

    if max_t is not None:
        for w, (cur_id, start_t) in list(active_runs.items()):
            duration = max_t - start_t
            if duration > 0:
                worker_intervals[w].append({
                    "task_id": cur_id,
                    "start": start_t,
                    "duration": duration,
                    "priority": task_priorities.get(cur_id, 3),
                    "deadline": task_deadlines.get(cur_id, 0),
                    "missed": cur_id in missed_tasks
                })

    fig = go.Figure()
    added_legend = set()
    border_color = "#FFFFFF" if is_bright else "#282119"

    for w in range(num_workers):
        for interval in worker_intervals[w]:
            prio = interval["priority"]
            color = "#A63830" if interval["missed"] else PRIORITY_COLORS.get(prio, "#7C7063")
            prio_label = PRIORITY_NAMES.get(prio, f"P{prio}")
            legend_name = f"P{prio} · {prio_label}" + (" (Delayed)" if interval["missed"] else "")
            show_in_legend = legend_name not in added_legend
            if show_in_legend:
                added_legend.add(legend_name)

            t_name = task_names.get(interval['task_id'], "")
            name_str = f": {t_name}" if t_name else ""
            hover_text = (
                f"<b>Task #{interval['task_id']}{name_str}</b><br>"
                f"Worker Lane: Unit {w}<br>"
                f"Timeline: Tick {interval['start']} to {interval['start'] + interval['duration']}<br>"
                f"Duration: {interval['duration']} ticks<br>"
                f"Urgency: P{prio} ({prio_label})<br>"
                f"Commitment Due: Tick {interval['deadline']}"
            )

            bar_label = f"T{interval['task_id']} ({t_name})" if t_name else f"T{interval['task_id']} ({prio_label})"
            fig.add_trace(go.Bar(
                name=legend_name,
                orientation="h",
                y=[f"Worker {w}"],
                x=[interval["duration"]],
                base=[interval["start"]],
                marker=dict(
                    color=color,
                    line=dict(color=border_color, width=1.5)
                ),
                text=bar_label,
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="#ffffff", size=11, family="Outfit, Inter, sans-serif"),
                hoverinfo="text",
                hovertext=hover_text,
                showlegend=show_in_legend
            ))

    plot_bg = "#F6F2EA" if is_bright else "#161311"
    paper_bg = "#FFFFFF" if is_bright else "#201B17"
    text_color = "#282420" if is_bright else "#EDE6DC"
    title_color = "#191512" if is_bright else "#FAF6F0"
    grid_color = "#E5DDD0" if is_bright else "#352D26"
    zeroline_color = "#D2C7B7" if is_bright else "#4A3F36"

    fig.update_layout(
        barmode="stack",
        plot_bgcolor=plot_bg,
        paper_bgcolor=paper_bg,
        font=dict(color=text_color, family="Outfit, Inter, sans-serif"),
        title=dict(
            text="Care Execution Timeline (Gantt Schedule)",
            font=dict(size=16, color=title_color)
        ),
        xaxis=dict(
            title="Discrete Simulation Time (Ticks)",
            dtick=1,
            gridcolor=grid_color,
            zerolinecolor=zeroline_color
        ),
        yaxis=dict(
            title="",
            gridcolor=grid_color,
            autorange="reversed"
        ),
        height=max(260, 100 + num_workers * 70),
        margin=dict(l=85, r=30, t=50, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def create_queue_length_chart(events: List[Dict[str, Any]], is_bright: bool = False) -> go.Figure:
    """Plots queue length over time with warm, calming tones."""
    ticks = []
    lengths = []

    for ev in events:
        if ev.get("event") == "TICK":
            ticks.append(ev.get("t", 0))
            lengths.append(len(ev.get("queue", [])))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ticks,
        y=lengths,
        mode="lines+markers",
        line=dict(color="#4A7C59", width=2.5),
        marker=dict(size=6, color="#72A280"),
        fill="tozeroy",
        fillcolor="rgba(74, 124, 89, 0.16)",
        name="Queued Care Requests"
    ))

    plot_bg = "#F6F2EA" if is_bright else "#161311"
    paper_bg = "#FFFFFF" if is_bright else "#201B17"
    text_color = "#282420" if is_bright else "#EDE6DC"
    title_color = "#191512" if is_bright else "#FAF6F0"
    grid_color = "#E5DDD0" if is_bright else "#352D26"

    fig.update_layout(
        plot_bgcolor=plot_bg,
        paper_bgcolor=paper_bg,
        font=dict(color=text_color, family="Outfit, Inter, sans-serif"),
        title=dict(
            text="Waiting Queue Length Over Time",
            font=dict(size=15, color=title_color)
        ),
        xaxis=dict(
            title="Time (Ticks)",
            dtick=2,
            gridcolor=grid_color
        ),
        yaxis=dict(
            title="Requests in Waiting Queue",
            dtick=1,
            gridcolor=grid_color
        ),
        height=260,
        margin=dict(l=50, r=20, t=40, b=40)
    )
    return fig

def create_per_priority_miss_chart(per_prio_miss: Dict[str, float], is_bright: bool = False) -> go.Figure:
    """Displays miss rate breakdown across priorities P1 through P5 with humanized labels."""
    prios = [f"P{p} ({PRIORITY_NAMES[p]})" for p in range(1, 6)]
    rates = [per_prio_miss.get(str(p), per_prio_miss.get(p, 0.0)) * 100 for p in range(1, 6)]
    colors = [PRIORITY_COLORS[p] for p in range(1, 6)]

    fig = go.Figure(data=[
        go.Bar(
            x=prios,
            y=rates,
            marker=dict(color=colors),
            text=[f"{r:.1f}%" for r in rates],
            textposition="auto",
            textfont=dict(color="#ffffff", size=12, family="Outfit, sans-serif")
        )
    ])

    plot_bg = "#F6F2EA" if is_bright else "#161311"
    paper_bg = "#FFFFFF" if is_bright else "#201B17"
    text_color = "#282420" if is_bright else "#EDE6DC"
    title_color = "#191512" if is_bright else "#FAF6F0"
    grid_color = "#E5DDD0" if is_bright else "#352D26"

    fig.update_layout(
        plot_bgcolor=plot_bg,
        paper_bgcolor=paper_bg,
        font=dict(color=text_color, family="Outfit, Inter, sans-serif"),
        title=dict(
            text="Delayed Rate Breakdown by Urgency Tier",
            font=dict(size=15, color=title_color)
        ),
        xaxis=dict(title="Urgency Tier", gridcolor=grid_color),
        yaxis=dict(title="Delayed Rate (%)", range=[0, 105], gridcolor=grid_color),
        height=260,
        margin=dict(l=50, r=20, t=40, b=40)
    )
    return fig

def create_policy_comparison_chart(comparison_data: List[Dict[str, Any]], is_bright: bool = False) -> go.Figure:
    """Generates grouped bar chart comparing all scheduling policies with humanized tones."""
    policies = [d["policy"] for d in comparison_data]
    miss_rates = [d["miss_rate"] * 100 for d in comparison_data]
    avg_waits = [d["avg_wait"] for d in comparison_data]

    fig = go.Figure(data=[
        go.Bar(
            name="Delayed Rate (%)",
            x=policies,
            y=miss_rates,
            marker_color="#C54E44",
            text=[f"{v:.1f}%" for v in miss_rates],
            textposition="auto"
        ),
        go.Bar(
            name="Avg Wait Time (Ticks)",
            x=policies,
            y=avg_waits,
            marker_color="#4A7C59",
            text=[f"{v:.2f}" for v in avg_waits],
            textposition="auto"
        )
    ])

    plot_bg = "#F6F2EA" if is_bright else "#161311"
    paper_bg = "#FFFFFF" if is_bright else "#201B17"
    text_color = "#282420" if is_bright else "#EDE6DC"
    title_color = "#191512" if is_bright else "#FAF6F0"
    grid_color = "#E5DDD0" if is_bright else "#352D26"

    fig.update_layout(
        barmode="group",
        plot_bgcolor=plot_bg,
        paper_bgcolor=paper_bg,
        font=dict(color=text_color, family="Outfit, Inter, sans-serif"),
        title=dict(
            text="Multi-Policy Benchmark: Delayed Rate vs. Average Waiting Time",
            font=dict(size=16, color=title_color)
        ),
        xaxis=dict(title="Policy", gridcolor=grid_color),
        yaxis=dict(title="Value", gridcolor=grid_color),
        height=320,
        margin=dict(l=50, r=30, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
