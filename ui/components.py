from typing import Dict, Any

# Curated, humanized artisan priority color palette (organic pigments)
PRIORITY_HEX = {
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

def render_theme_banner(theme: Dict[str, Any], is_bright: bool = False) -> str:
    """Renders a warm, human-crafted operational banner."""
    banner_bg = theme.get('bright_banner_bg', '#EFF4EE') if is_bright else theme.get('banner_bg', '#1F231D')
    banner_border = theme.get('bright_banner_border', theme.get('accent', '#4A7C59')) if is_bright else theme.get('banner_border', '#4A7C59')
    heading_color = "#191512" if is_bright else "#FAF6F0"
    desc_color = "#453D35" if is_bright else "#D8CEBE"
    shadow = "0 8px 20px -3px rgba(40, 30, 20, 0.05)" if is_bright else f"0 10px 25px -4px {theme.get('accent_glow', 'rgba(0,0,0,0.3)')}"

    return f"""
    <div style="
        background: {banner_bg};
        border: 1px solid {banner_border};
        border-radius: 14px;
        padding: 18px 24px;
        margin-bottom: 22px;
        box-shadow: {shadow};
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(12px);
    ">
        <div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2.2rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));">{theme.get('icon', '🌿')}</span>
                <div>
                    <span style="
                        background: {theme.get('accent', '#4A7C59')};
                        color: #ffffff;
                        font-size: 0.75rem;
                        font-weight: 700;
                        padding: 3px 12px;
                        border-radius: 9999px;
                        letter-spacing: 0.04em;
                    ">
                        {theme.get('name', 'Serenity & Balance')}
                    </span>
                    <h2 style="margin: 4px 0 0 0; font-size: 1.45rem; font-weight: 800; color: {heading_color}; letter-spacing: -0.02em;">
                        {theme.get('tagline', 'Real-Time Dispatch Simulator')}
                    </h2>
                </div>
            </div>
            <p style="margin: 8px 0 0 0; font-size: 0.92rem; color: {desc_color}; line-height: 1.4;">
                {theme.get('description', '')}
            </p>
        </div>
        <div style="text-align: right; display: none; @media(min-width: 768px) {{ display: block; }}">
            <div style="font-size: 0.8rem; color: {'#6E645A' if is_bright else '#A89C8E'}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Engine Model</div>
            <div style="font-size: 1.15rem; font-weight: 800; color: {theme.get('accent', '#4A7C59')};">
                Indexed Min-Heap
            </div>
        </div>
    </div>
    """

def render_kpi_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color: str = "#4A7C59", card_bg: str = "#1F231D", card_border: str = "#343E31", is_bright: bool = False) -> str:
    """Renders a humanized, warm metric card."""
    title_color = "#554C42" if is_bright else "#A89C8E"
    sub_color = "#6E645A" if is_bright else "#8F8274"
    shadow = "0 6px 16px -2px rgba(40, 30, 20, 0.04)" if is_bright else "0 8px 20px -3px rgba(10, 8, 6, 0.35)"

    return f"""
    <div style="
        background: {card_bg};
        border-radius: 14px;
        border: 1px solid {card_border};
        padding: 18px 22px;
        box-shadow: {shadow};
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(12px);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 0.82rem; color: {title_color}; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;">{title}</span>
            <span style="font-size: 1.3rem;">{icon}</span>
        </div>
        <div style="font-size: 1.85rem; font-weight: 800; color: {color}; line-height: 1.15; letter-spacing: -0.02em;">
            {value}
        </div>
        {f'<div style="font-size: 0.82rem; color: {sub_color}; margin-top: 5px; font-weight: 500;">{subtitle}</div>' if subtitle else ''}
    </div>
    """

def render_queue_task_card(task: Dict[str, Any], current_tick: int, theme_task_label: str = "Care Request", card_bg: str = "#1F231D", card_border: str = "#343E31", is_bright: bool = False) -> str:
    """
    Renders an urgency card for the waiting queue with warm, human-friendly indicators.
    """
    t_id = task.get("id", task.get("Task ID", 0))
    t_name = task.get("name", task.get("Task Name", ""))
    priority = task.get("priority", task.get("Priority", 3))
    deadline = task.get("deadline", task.get("Deadline", 0))
    burst_val = task.get("burst", task.get("Burst Time", 0))
    remaining = task.get("remaining", burst_val)
    slack = deadline - current_tick

    is_urgent = (slack <= 2)
    border_color = "#C54E44" if is_urgent else card_border
    prio_bg = PRIORITY_HEX.get(priority, "#7C7063")
    prio_label = PRIORITY_NAMES.get(priority, "Standard Flow")
    box_shadow = "0 0 14px rgba(197, 78, 68, 0.3)" if is_urgent else ("0 4px 10px rgba(40,30,20,0.04)" if is_bright else "none")

    if slack < 0:
        slack_html = "<span style='color: #C54E44; font-weight: 700; font-size: 0.82rem;'>⚠️ Past Fulfillment Window</span>"
    elif is_urgent:
        slack_html = f"<span style='color: #C54E44; font-weight: 700; font-size: 0.82rem;'>⚡ Urgent · {slack}t remaining</span>"
    else:
        slack_color = "#3D6857" if is_bright else "#72A280"
        slack_html = f"<span style='color: {slack_color}; font-weight: 600; font-size: 0.82rem;'>⏱️ {slack}t leeway</span>"

    title_color = "#191512" if is_bright else "#FAF6F0"
    text_color = "#554C42" if is_bright else "#A89C8E"
    bold_color = "#191512" if is_bright else "#EDE6DC"

    name_badge = f"<span style='font-weight: 500; font-size: 0.86rem; opacity: 0.85; margin-left: 6px;'>· {t_name}</span>" if t_name else ""

    return f"""
    <div style="
        background: {card_bg};
        border: 1.5px solid {border_color};
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 11px;
        box-shadow: {box_shadow};
        transition: all 0.2s ease;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-weight: 700; color: {title_color}; font-size: 0.98rem;">
                {theme_task_label} #{t_id}{name_badge}
            </div>
            <span style="
                background: {prio_bg};
                color: #ffffff;
                font-size: 0.73rem;
                font-weight: 700;
                padding: 2px 9px;
                border-radius: 9999px;
            ">
                P{priority} · {prio_label}
            </span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.83rem; color: {text_color};">
            <span>Needed: <b style="color: {bold_color};">{remaining} ticks</b></span>
            <span>Target: <b style="color: {bold_color};">Tick {deadline}</b></span>
        </div>
        <div style="margin-top: 6px; text-align: right;">
            {slack_html}
        </div>
    </div>
    """

def render_worker_lane(worker_id: int, current_task: Dict[str, Any] = None, theme_worker_label: str = "Caregiver Unit", card_bg: str = "#1F231D", accent_color: str = "#4A7C59", accent_light: str = "#72A280", is_bright: bool = False) -> str:
    """Renders a worker lane with organic progress bar."""
    if not current_task:
        idle_bg = "#F3EFE8" if is_bright else "#282119"
        idle_color = "#6E645A" if is_bright else "#A89C8E"
        label_color = "#554C42" if is_bright else "#A89C8E"

        return f"""
        <div style="
            background: {card_bg};
            border: 1px dashed {'#D8CEBE' if is_bright else '#3E342B'};
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <span style="font-weight: 600; color: {label_color}; font-size: 0.92rem;">{theme_worker_label} {worker_id}</span>
            <span style="
                background: {idle_bg};
                color: {idle_color};
                padding: 3px 12px;
                border-radius: 9999px;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.04em;
            ">STANDBY · READY</span>
        </div>
        """

    t_id = current_task.get("id", current_task.get("Task ID"))
    t_name = current_task.get("name", current_task.get("Task Name", ""))
    prio = current_task.get("priority", current_task.get("Priority", 3))
    burst = current_task.get("burst", current_task.get("Burst Time", 1))
    remaining = current_task.get("remaining", 0)
    deadline_val = current_task.get("deadline", current_task.get("Deadline", 0))
    done_ticks = max(0, burst - remaining)
    progress_pct = min(100.0, (done_ticks / burst) * 100.0) if burst > 0 else 100.0

    prio_color = PRIORITY_HEX.get(prio, accent_color)
    prio_name = PRIORITY_NAMES.get(prio, "Standard Flow")
    title_color = "#191512" if is_bright else "#FAF6F0"
    track_bg = "#E9E2D5" if is_bright else "#14110E"
    sub_color = "#554C42" if is_bright else "#A89C8E"

    name_label = f" ({t_name})" if t_name else ""

    return f"""
    <div style="
        background: {card_bg};
        border: 1.5px solid {accent_color};
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 14px rgba(40,30,20,{'0.06' if is_bright else '0.35'});
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-weight: 700; color: {title_color}; font-size: 0.95rem;">
                {theme_worker_label} {worker_id}
                <span style="color: {accent_color}; margin-left: 8px; font-weight: 600;">Caring for #{t_id}{name_label}</span>
            </div>
            <span style="
                background: {prio_color};
                color: #ffffff;
                font-size: 0.73rem;
                font-weight: 700;
                padding: 2px 9px;
                border-radius: 9999px;
            ">
                P{prio} · {prio_name}
            </span>
        </div>
        <div style="background: {track_bg}; border-radius: 9999px; height: 10px; overflow: hidden; margin: 9px 0;">
            <div style="
                background: linear-gradient(90deg, {accent_color}, {accent_light});
                height: 100%;
                width: {progress_pct:.1f}%;
                transition: width 0.35s ease;
                border-radius: 9999px;
            "></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: {sub_color};">
            <span>Progress: <b>{done_ticks}/{burst} ticks</b> ({progress_pct:.0f}%)</span>
            <span>Target Horizon: Tick {deadline_val}</span>
        </div>
    </div>
    """
