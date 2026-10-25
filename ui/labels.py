# labels.py - Humanized Theme definitions, dynamic CSS generation, and label mappings

THEMES = {
    "Serenity": {
        "icon": "🌿",
        "name": "Serenity & Balance",
        "tagline": "Calm, Restorative Discrete-Event Dispatcher",
        "task": "Care Request",
        "tasks": "Care Requests",
        "worker": "Caregiver Unit",
        "workers": "Caregiver Units",
        "priority": "Attention Need",
        "deadline": "Fulfillment Window",
        "burst": "Care Time Needed",
        "arrive": "Received At",
        "missed": "Delayed Attention",
        "done": "Gently Fulfilled",
        "running": "Active in Care",
        "waiting": "Caring Queue",
        "accent": "#4A7C59",       # Calming Forest Sage
        "accent_light": "#72A280", # Soft Fern
        "accent_glow": "rgba(74, 124, 89, 0.24)",
        # Dark mode styling (Warm olive cedar - no pitch black)
        "bg_gradient": "linear-gradient(150deg, #1C221A 0%, #262D23 50%, #1A2018 100%)",
        "card_bg": "#2B3428",
        "card_border": "#414E3C",
        "banner_bg": "linear-gradient(135deg, rgba(74, 124, 89, 0.22) 0%, rgba(43, 52, 40, 0.9) 100%)",
        "banner_border": "#4A7C59",
        "btn_gradient": "linear-gradient(135deg, #4A7C59, #365B41)",
        "btn_hover": "linear-gradient(135deg, #578F67, #3F6A4C)",
        "tab_active_bg": "#4A7C59",
        # Bright mode styling (Artisanal warm linen & oat)
        "bright_bg_gradient": "linear-gradient(180deg, #FAF8F5 0%, #F1ECE2 100%)",
        "bright_card_bg": "#FFFFFF",
        "bright_card_border": "#DFD7CB",
        "bright_banner_bg": "linear-gradient(135deg, #EFF4EE 0%, #E2ECE1 100%)",
        "bright_banner_border": "#5E8F6C",
        "description": "Harmonious human-paced scheduling minimizing waiting fatigue with natural organic balance."
    },
    "Emergency": {
        "icon": "🚑",
        "name": "Lifeline Dispatch",
        "tagline": "Compassionate 911 Triage & Critical Care",
        "task": "Incident / Call",
        "tasks": "Incidents",
        "worker": "Response Unit",
        "workers": "Response Units",
        "priority": "Triage Urgency",
        "deadline": "Commitment Horizon",
        "burst": "Care Duration",
        "arrive": "Call Received",
        "missed": "Delayed Care",
        "done": "Safely Resolved",
        "running": "En Route & Caring",
        "waiting": "Triage Priority",
        "accent": "#C54E44",       # Terracotta Carmine
        "accent_light": "#E0766C", # Warm Coral Blush
        "accent_glow": "rgba(197, 78, 68, 0.24)",
        # Dark mode styling (Warm merlot umber - no pitch black)
        "bg_gradient": "linear-gradient(150deg, #241A1A 0%, #2E2222 50%, #201717 100%)",
        "card_bg": "#352727",
        "card_border": "#533D3D",
        "banner_bg": "linear-gradient(135deg, rgba(197, 78, 68, 0.22) 0%, rgba(53, 39, 39, 0.9) 100%)",
        "banner_border": "#C54E44",
        "btn_gradient": "linear-gradient(135deg, #C54E44, #99372F)",
        "btn_hover": "linear-gradient(135deg, #D45D55, #AB3E35)",
        "tab_active_bg": "#C54E44",
        # Bright mode styling (Warm almond rose)
        "bright_bg_gradient": "linear-gradient(180deg, #FDF9F7 0%, #F7ECE8 100%)",
        "bright_card_bg": "#FFFFFF",
        "bright_card_border": "#E8D5D0",
        "bright_banner_bg": "linear-gradient(135deg, #FBEEEB 0%, #F6DFD9 100%)",
        "bright_banner_border": "#D45D55",
        "description": "Patient-first emergency triage: critical calls gently preempt standard units."
    },
    "Personal": {
        "icon": "☕",
        "name": "Mindful Flow",
        "tagline": "Intentional Human Focus & Well-being Planner",
        "task": "Intent / Ritual",
        "tasks": "Intents",
        "worker": "Focus Window",
        "workers": "Focus Windows",
        "priority": "Life Value",
        "deadline": "Meaningful Deadline",
        "burst": "Estimated Focus",
        "arrive": "Added Today",
        "missed": "Gentle Horizon Shift",
        "done": "Accomplished",
        "running": "Deep Flow",
        "waiting": "Calm Backlog",
        "accent": "#C27D26",       # Spiced Warm Ochre
        "accent_light": "#DEA354", # Golden Flax
        "accent_glow": "rgba(194, 125, 38, 0.24)",
        # Dark mode styling (Warm roasted chestnut - no pitch black)
        "bg_gradient": "linear-gradient(150deg, #241E18 0%, #2F271F 50%, #1F1914 100%)",
        "card_bg": "#372D24",
        "card_border": "#584839",
        "banner_bg": "linear-gradient(135deg, rgba(194, 125, 38, 0.22) 0%, rgba(55, 45, 36, 0.9) 100%)",
        "banner_border": "#C27D26",
        "btn_gradient": "linear-gradient(135deg, #C27D26, #965F1B)",
        "btn_hover": "linear-gradient(135deg, #D48C31, #A96B20)",
        "tab_active_bg": "#C27D26",
        # Bright mode styling (Sunlit warm parchment)
        "bright_bg_gradient": "linear-gradient(180deg, #FCFAF6 0%, #F5EFE3 100%)",
        "bright_card_bg": "#FFFFFF",
        "bright_card_border": "#E7DDCF",
        "bright_banner_bg": "linear-gradient(135deg, #FAF2E4 0%, #F4E5CC 100%)",
        "bright_banner_border": "#D08E39",
        "description": "Mindful human productivity maximizing genuine impact with serene pacing."
    },
    "Studio": {
        "icon": "🎨",
        "name": "Studio Craft",
        "tagline": "Artisan Engineering & Algorithmic Workshop",
        "task": "Craft Routine",
        "tasks": "Routines",
        "worker": "Artisan Lane",
        "workers": "Artisan Lanes",
        "priority": "Craft Priority",
        "deadline": "Excellence Target",
        "burst": "Craft Duration",
        "arrive": "Commenced",
        "missed": "Target Extended",
        "done": "Masterfully Crafted",
        "running": "Active Crafting",
        "waiting": "Artisan Queue",
        "accent": "#3B7E85",       # Oceanic Slate Teal
        "accent_light": "#64A3AA", # Muted Sea-Glass
        "accent_glow": "rgba(59, 126, 133, 0.24)",
        # Dark mode styling (Deep abyssal slate - no pitch black)
        "bg_gradient": "linear-gradient(150deg, #182326 0%, #202F33 50%, #151D20 100%)",
        "card_bg": "#26373B",
        "card_border": "#3D555A",
        "banner_bg": "linear-gradient(135deg, rgba(59, 126, 133, 0.22) 0%, rgba(38, 55, 59, 0.9) 100%)",
        "banner_border": "#3B7E85",
        "btn_gradient": "linear-gradient(135deg, #3B7E85, #28595F)",
        "btn_hover": "linear-gradient(135deg, #48929A, #2F6970)",
        "tab_active_bg": "#3B7E85",
        # Bright mode styling (Sea-salt travertine)
        "bright_bg_gradient": "linear-gradient(180deg, #F8FAFA 0%, #ECF2F2 100%)",
        "bright_card_bg": "#FFFFFF",
        "bright_card_border": "#D2E0E2",
        "bright_banner_bg": "linear-gradient(135deg, #EAF2F3 0%, #D8E7E9 100%)",
        "bright_banner_border": "#4A9098",
        "description": "High-craft precision scheduling combining core affinity with serene flow."
    },
    "Overload": {
        "icon": "⚠️",
        "name": "Surge Control",
        "tagline": "Peak Capacity & Overload Pressure Operations",
        "task": "Surge Incident",
        "tasks": "Surge Incidents",
        "worker": "Surge Lane",
        "workers": "Surge Lanes",
        "priority": "Criticality",
        "deadline": "Hard Cutoff",
        "burst": "Processing Time",
        "arrive": "Surge Influx",
        "missed": "Dropped Past Cutoff",
        "done": "Safely Preserved",
        "running": "Active in Surge",
        "waiting": "Backlog Queue",
        "accent": "#D2691E",       # Warning Burnt Sienna
        "accent_light": "#E58A4E", # Warm Amber Glow
        "accent_glow": "rgba(210, 105, 30, 0.28)",
        # Dark mode styling (Warm volcanic iron & umber - no pitch black)
        "bg_gradient": "linear-gradient(150deg, #241A17 0%, #2F211D 50%, #1D1513 100%)",
        "card_bg": "#362622",
        "card_border": "#543C35",
        "banner_bg": "linear-gradient(135deg, rgba(210, 105, 30, 0.22) 0%, rgba(54, 38, 34, 0.9) 100%)",
        "banner_border": "#D2691E",
        "btn_gradient": "linear-gradient(135deg, #D2691E, #A44C0E)",
        "btn_hover": "linear-gradient(135deg, #E2792D, #B75713)",
        "tab_active_bg": "#D2691E",
        # Bright mode styling (Warm sunlit terracotta & cream)
        "bright_bg_gradient": "linear-gradient(180deg, #FDF9F6 0%, #F6EDE5 100%)",
        "bright_card_bg": "#FFFFFF",
        "bright_card_border": "#E8D8CC",
        "bright_banner_bg": "linear-gradient(135deg, #FBEEE4 0%, #F3DFD1 100%)",
        "bright_banner_border": "#D2691E",
        "description": "Peak system saturation: heavy work surges exceed worker limits, demonstrating hard deadline drops."
    }
}

# Backward compatibility alias map
THEME_ALIASES = {
    "Generic": "Serenity",
    "Computer": "Studio",
    "Warning": "Overload"
}

def resolve_theme_key(key: str) -> str:
    """Resolves aliases like 'Generic' or 'Computer' to humanized keys."""
    if key in THEMES:
        return key
    return THEME_ALIASES.get(key, "Serenity")

def get_label(theme_name: str, key: str, default: str = "") -> str:
    resolved_key = resolve_theme_key(theme_name)
    theme = THEMES.get(resolved_key, THEMES["Serenity"])
    return theme.get(key, default or key.title())

def generate_theme_css(theme_name: str, is_bright: bool = False) -> str:
    """Generates humanized, warm dynamic CSS rules based on theme and mode."""
    resolved_key = resolve_theme_key(theme_name)
    t = THEMES.get(resolved_key, THEMES["Serenity"])
    accent = t["accent"]
    accent_glow = t["accent_glow"]
    btn_gradient = t["btn_gradient"]
    btn_hover = t["btn_hover"]
    tab_active_bg = t["tab_active_bg"]

    if is_bright:
        bg_gradient = t.get("bright_bg_gradient", "linear-gradient(180deg, #FAF8F5 0%, #F1ECE2 100%)")
        card_bg = t.get("bright_card_bg", "#FFFFFF")
        card_border = t.get("bright_card_border", "#DFD7CB")
        text_color = "#282420"
        heading_color = "#191512"
        subtext_color = "#6E645A"
        sidebar_bg = "#F6F2EA"
        tab_list_bg = "#E9E2D5"
        tab_list_border = "#D8CEBE"
        tab_text = "#554C42"
        shadow = "0 8px 24px -4px rgba(40, 30, 20, 0.06), 0 2px 6px -1px rgba(40, 30, 20, 0.03)"
        input_bg = "#FFFFFF"
        popover_bg = "#FFFFFF"
    else:
        bg_gradient = t["bg_gradient"]
        card_bg = t["card_bg"]
        card_border = t["card_border"]
        text_color = "#EDE6DC"
        heading_color = "#FAF6F0"
        subtext_color = "#B0A496"
        sidebar_bg = "#1A201A" if resolved_key == "Serenity" else ("#201717" if resolved_key == "Emergency" else ("#1F1914" if resolved_key == "Personal" else "#151D20"))
        tab_list_bg = "#232A20" if resolved_key == "Serenity" else ("#2A1D1D" if resolved_key == "Emergency" else ("#2B231B" if resolved_key == "Personal" else "#1D282B"))
        tab_list_border = card_border
        tab_text = "#B0A496"
        shadow = f"0 10px 30px -5px {accent_glow}, 0 4px 12px -2px rgba(10, 8, 6, 0.4)"
        input_bg = card_bg
        popover_bg = card_bg

    return f"""
    <style>
    /* ============================================================ */
    /* ELIMINATE ALL BLACK STRIPS (Header, Toolbars, Decorations)   */
    /* ============================================================ */
    header[data-testid="stHeader"],
    .stAppHeader,
    header {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    div[data-testid="stDecoration"] {{
        display: none !important;
        background: transparent !important;
        height: 0 !important;
    }}

    div[data-testid="stToolbar"] {{
        background: transparent !important;
    }}

    /* Humanized Page Surface */
    .stApp {{
        background: {bg_gradient} !important;
        background-attachment: fixed !important;
        color: {text_color} !important;
    }}
    
    /* Headings with organic human warmth */
    h1, h2, h3, h4, h5, h6 {{
        color: {heading_color} !important;
        letter-spacing: -0.02em !important;
        font-weight: 700 !important;
    }}

    p, span, label, div {{
        color: {text_color};
    }}

    /* Sidebar Surface (No black borders or surfaces) */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {card_border} !important;
    }}
    
    /* ============================================================ */
    /* ELIMINATE BLACK DROPDOWNS & BASEWEB POPOVERS                 */
    /* ============================================================ */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        border: 1px solid {card_border} !important;
        color: {text_color} !important;
        border-radius: 11px !important;
    }}

    div[data-baseweb="select"] svg {{
        fill: {text_color} !important;
    }}

    div[data-baseweb="select"] span {{
        color: {text_color} !important;
    }}

    /* Open Dropdown Popover & Options Menu Container */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[role="listbox"],
    ul[data-testid="stSelectboxVirtualDropdown"] {{
        background-color: {popover_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 12px !important;
        box-shadow: {shadow} !important;
        padding: 6px !important;
    }}

    /* BaseWeb Popover inner text elements */
    div[data-baseweb="popover"] *,
    ul[data-testid="stSelectboxVirtualDropdown"] * {{
        color: {text_color} !important;
    }}

    /* Dropdown Options */
    li[role="option"],
    div[data-baseweb="menu"] li,
    ul[data-testid="stSelectboxVirtualDropdown"] li {{
        background-color: {popover_bg} !important;
        color: {text_color} !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }}

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    div[data-baseweb="menu"] li:hover,
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover {{
        background-color: {tab_active_bg} !important;
        color: #ffffff !important;
    }}

    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"] *,
    div[data-baseweb="menu"] li:hover *,
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover * {{
        color: #ffffff !important;
    }}

    /* Inputs, Number Pickers, Text Areas */
    div[data-baseweb="input"],
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {card_border} !important;
        border-radius: 10px !important;
    }}

    /* Slider track & thumb */
    div[data-baseweb="slider"] div[role="slider"] {{
        background-color: {accent} !important;
        border-color: {accent} !important;
    }}

    /* Expander containers */
    div[data-testid="stExpander"] {{
        background-color: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 12px !important;
    }}

    /* Radio buttons */
    div[data-testid="stRadio"] label span {{
        color: {text_color} !important;
    }}

    /* Humanized Glass Cards */
    div[data-testid="stMetric"] {{
        background-color: {card_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 14px !important;
        box-shadow: {shadow} !important;
    }}
    
    div[data-testid="stMetricValue"] {{
        color: {accent} !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {subtext_color} !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}

    /* Tactile Modern Buttons */
    div.stButton > button:first-child {{
        background: {btn_gradient} !important;
        border: 1px solid {accent} !important;
        box-shadow: 0 4px 14px {accent_glow} !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 11px !important;
    }}
    
    div.stButton > button:first-child:hover {{
        background: {btn_hover} !important;
        transform: translateY(-1.5px) !important;
        box-shadow: 0 6px 18px {accent_glow} !important;
    }}
    
    /* Rounded Pill Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {tab_list_bg} !important;
        border: 1px solid {tab_list_border} !important;
        border-radius: 14px !important;
        padding: 5px !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {tab_text} !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {tab_active_bg} !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px {accent_glow} !important;
    }}
    
    /* Data Editor container */
    div[data-testid="stDataEditor"] {{
        background-color: {card_bg} !important;
        border-radius: 14px !important;
        border: 1px solid {card_border} !important;
        box-shadow: {shadow} !important;
    }}
    </style>
    """
