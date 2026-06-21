"""
StudyAI Enhanced — Premium Study Assistant
Features: Light/Dark mode, multiple tabs, interactive MCQ analysis, improved sidebar
"""

import re
import json
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

st.set_page_config(
    page_title="StudyAI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# CSS — Light/Dark mode with full design system
# ══════════════════════════════════════════════════════════════
def inject_css():
    dark = st.session_state.get("dark_mode", True)

    if dark:
        theme = """
        --bg:           #0D0D0F;
        --bg2:          #111115;
        --bg3:          #17171D;
        --bg4:          #1E1E26;
        --glass:        rgba(255,255,255,0.04);
        --glass-border: rgba(255,255,255,0.08);
        --border:       rgba(255,255,255,0.07);
        --txt:          #F0EEF8;
        --txt2:         #9A97B0;
        --txt3:         #5A5775;
        --card-bg:      #17171D;
        --input-bg:     #1E1E26;
        --hover-bg:     rgba(255,255,255,0.05);
        --shadow:       0 4px 24px rgba(0,0,0,0.5);
        --mode-icon:    "🌙";
        """
    else:
        theme = """
        --bg:           #F5F4F0;
        --bg2:          #FFFFFF;
        --bg3:          #F0EEE8;
        --bg4:          #E8E6DE;
        --glass:        rgba(0,0,0,0.03);
        --glass-border: rgba(0,0,0,0.08);
        --border:       rgba(0,0,0,0.09);
        --txt:          #1A1825;
        --txt2:         #5A5775;
        --txt3:         #9A97B0;
        --card-bg:      #FFFFFF;
        --input-bg:     #FFFFFF;
        --hover-bg:     rgba(0,0,0,0.04);
        --shadow:       0 4px 24px rgba(0,0,0,0.08);
        --mode-icon:    "☀️";
        """

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

    :root {{
        {theme}
        --amber:        #F59E0B;
        --amber-soft:   #FCD34D;
        --amber-dim:    rgba(245,158,11,0.12);
        --amber-glow:   rgba(245,158,11,0.25);
        --green:        #10B981;
        --green-dim:    rgba(16,185,129,0.12);
        --red:          #EF4444;
        --red-dim:      rgba(239,68,68,0.12);
        --blue:         #3B82F6;
        --blue-dim:     rgba(59,130,246,0.12);
        --purple:       #8B5CF6;
        --purple-dim:   rgba(139,92,246,0.12);
        --radius:       10px;
        --radius-lg:    16px;
        --radius-xl:    22px;
        --t:            all 0.2s cubic-bezier(0.4,0,0.2,1);
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        font-family: 'DM Sans', sans-serif !important;
        color: var(--txt) !important;
        transition: background 0.3s, color 0.3s;
    }}

    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    .stDeployButton {{ display: none !important; }}

    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--bg4); border-radius: 99px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--amber); }}

    /* ── SIDEBAR ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: var(--bg2) !important;
        border-right: 1px solid var(--border) !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }}
    [data-testid="stSidebarContent"] {{ padding: 0 !important; }}

    .sb-logo {{
        display: flex; align-items: center; gap: 10px;
        padding: 18px 16px 14px;
        border-bottom: 1px solid var(--border);
    }}
    .sb-logo-icon {{
        width: 34px; height: 34px; border-radius: 9px;
        background: linear-gradient(135deg, #F59E0B, #D97706);
        display: flex; align-items: center; justify-content: center;
        font-size: 17px; flex-shrink: 0;
        box-shadow: 0 4px 12px rgba(245,158,11,0.3);
    }}
    .sb-logo-name {{
        font-family: 'Syne', sans-serif;
        font-size: 15px; font-weight: 800;
        color: var(--txt); letter-spacing: -0.3px; line-height: 1;
    }}
    .sb-logo-name span {{ color: var(--amber); }}
    .sb-logo-sub {{ font-size: 10px; color: var(--txt3); margin-top: 2px; }}
    .sb-badge {{
        font-size: 9px; font-weight: 700; letter-spacing: 0.8px;
        text-transform: uppercase; color: var(--amber);
        border: 1px solid rgba(245,158,11,0.3);
        padding: 2px 7px; border-radius: 99px;
        background: var(--amber-dim); margin-left: auto;
    }}

    .sb-body {{ padding: 10px 12px 20px; }}

    .sb-label {{
        font-size: 9.5px; font-weight: 600; letter-spacing: 1.2px;
        text-transform: uppercase; color: var(--txt3);
        padding: 0 2px; margin: 16px 0 6px;
        display: flex; align-items: center; gap: 6px;
    }}
    .sb-label::after {{
        content: ''; flex: 1; height: 1px; background: var(--border);
    }}

    /* Sidebar nav buttons */
    [data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
        background: transparent !important;
        color: var(--txt2) !important;
        border: 1px solid transparent !important;
        border-radius: var(--radius) !important;
        padding: 8px 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important; font-weight: 500 !important;
        text-align: left !important;
        transition: var(--t) !important;
        margin-bottom: 2px !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: var(--hover-bg) !important;
        border-color: var(--border) !important;
        color: var(--amber) !important;
        transform: translateX(2px) !important;
    }}
    [data-testid="stSidebar"] .stButton > button:focus {{
        box-shadow: none !important; outline: none !important;
    }}

    .sb-active-btn .stButton > button {{
        background: var(--amber-dim) !important;
        border-color: rgba(245,158,11,0.3) !important;
        color: var(--amber) !important;
    }}

    .nav-danger .stButton > button {{ color: #EF4444 !important; }}
    .nav-danger .stButton > button:hover {{
        background: var(--red-dim) !important;
        border-color: rgba(239,68,68,0.25) !important;
        color: #EF4444 !important; transform: none !important;
    }}

    /* PDF pill */
    .pdf-pill {{
        display: flex; align-items: center; gap: 7px;
        padding: 8px 10px; border-radius: var(--radius);
        background: var(--glass); border: 1px solid var(--glass-border);
        font-size: 11.5px; color: var(--txt2); font-weight: 500;
        margin-top: 6px; word-break: break-all;
    }}
    .pdf-pill.loaded {{
        background: var(--green-dim);
        border-color: rgba(16,185,129,0.25);
        color: var(--green);
    }}
    .dot {{
        width: 6px; height: 6px; flex-shrink: 0;
        border-radius: 50%; background: var(--green);
        box-shadow: 0 0 5px var(--green);
        animation: pulse-dot 2s ease infinite;
    }}
    .dot.empty {{ background: var(--txt3); box-shadow: none; animation: none; }}

    /* File uploader */
    [data-testid="stFileUploader"] {{
        background: var(--glass) !important;
        border: 1.5px dashed rgba(245,158,11,0.3) !important;
        border-radius: var(--radius) !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: var(--amber) !important;
        background: var(--amber-dim) !important;
    }}
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzoneInput"] {{
        background: transparent !important; border: none !important;
    }}
    [data-testid="stFileUploader"] section > div {{ padding: 8px !important; }}
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] p {{
        font-size: 11.5px !important; color: var(--txt2) !important;
    }}

    /* Selectbox */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {{
        background: var(--input-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        color: var(--txt) !important; font-size: 12.5px !important;
        font-family: 'DM Sans', sans-serif !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div:focus-within {{
        border-color: var(--amber) !important;
        box-shadow: 0 0 0 3px var(--amber-dim) !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] label {{
        font-size: 9.5px !important; font-weight: 600 !important;
        letter-spacing: 1px !important; text-transform: uppercase !important;
        color: var(--txt3) !important; margin-bottom: 4px !important;
    }}

    /* Slider */
    [data-testid="stSidebar"] [data-testid="stSlider"] label {{
        font-size: 9.5px !important; font-weight: 600 !important;
        letter-spacing: 1px !important; text-transform: uppercase !important;
        color: var(--txt3) !important;
    }}

    /* ── TABS ─────────────────────────────────────────────── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {{
        background: var(--bg3) !important;
        border-radius: var(--radius-lg) !important;
        padding: 4px !important;
        border: 1px solid var(--border) !important;
        gap: 2px !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab"] {{
        background: transparent !important;
        border-radius: var(--radius) !important;
        color: var(--txt2) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important; font-weight: 500 !important;
        padding: 8px 16px !important;
        transition: var(--t) !important;
        border: 1px solid transparent !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab"]:hover {{
        color: var(--amber) !important;
        background: var(--amber-dim) !important;
    }}
    [data-testid="stTabs"] [aria-selected="true"] {{
        background: var(--amber) !important;
        color: #000 !important; font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(245,158,11,0.3) !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    [data-testid="stTabs"] [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* ── MAIN AREA ────────────────────────────────────────── */
    .main .block-container {{
        max-width: 860px !important;
        padding: 0 2rem 140px !important;
        margin: 0 auto !important;
    }}

    /* Top bar */
    .topbar {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 18px 0 14px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 20px;
        animation: fadeDown 0.4s ease both;
    }}
    .topbar-title {{
        font-family: 'Syne', sans-serif;
        font-size: 1rem; font-weight: 700; color: var(--txt);
    }}
    .topbar-title span {{ color: var(--amber); }}
    .badge {{
        display: inline-flex; align-items: center; gap: 5px;
        padding: 4px 10px; border-radius: 99px;
        font-size: 11px; font-weight: 600; letter-spacing: 0.4px;
    }}
    .badge-amber {{
        background: var(--amber-dim); border: 1px solid rgba(245,158,11,0.25);
        color: var(--amber);
    }}
    .badge-green {{
        background: var(--green-dim); border: 1px solid rgba(16,185,129,0.25);
        color: var(--green);
    }}
    .badge-blue {{
        background: var(--blue-dim); border: 1px solid rgba(59,130,246,0.25);
        color: var(--blue);
    }}

    /* ── HERO / WELCOME ───────────────────────────────────── */
    .hero {{
        text-align: center; padding: 40px 0 28px;
        animation: fadeUp 0.5s ease both;
    }}
    .hero-orb {{
        width: 72px; height: 72px; border-radius: 20px;
        background: linear-gradient(135deg, #F59E0B, #B45309);
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; margin: 0 auto 18px;
        box-shadow: 0 8px 28px rgba(245,158,11,0.3), 0 0 0 10px rgba(245,158,11,0.06);
        animation: float 4s ease-in-out infinite;
    }}
    .hero h1 {{
        font-family: 'Syne', sans-serif !important;
        font-size: 2rem !important; font-weight: 800 !important;
        letter-spacing: -0.5px !important; color: var(--txt) !important;
        line-height: 1.15 !important; margin-bottom: 10px !important;
    }}
    .hero h1 em {{ font-style: normal; color: var(--amber); }}
    .hero p {{
        font-size: 14.5px !important; color: var(--txt2) !important;
        line-height: 1.7 !important; max-width: 380px;
        margin: 0 auto 28px !important;
    }}

    .stats-row {{
        display: flex; gap: 10px; justify-content: center;
        margin-bottom: 32px; flex-wrap: wrap;
    }}
    .stat-pill {{
        display: flex; align-items: center; gap: 6px;
        padding: 7px 14px; border-radius: 99px;
        background: var(--glass); border: 1px solid var(--glass-border);
        font-size: 11.5px; color: var(--txt2);
    }}
    .stat-pill strong {{ color: var(--amber); font-weight: 700; }}

    /* Chip grid */
    [data-testid="stHorizontalBlock"] > [data-testid="column"] .stButton > button {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        color: var(--txt) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 12.5px !important; font-weight: 400 !important;
        padding: 14px !important; text-align: left !important;
        width: 100% !important; transition: var(--t) !important;
        box-shadow: none !important; line-height: 1.5 !important;
        height: auto !important; white-space: normal !important;
    }}
    [data-testid="stHorizontalBlock"] > [data-testid="column"] .stButton > button:hover {{
        border-color: var(--amber) !important;
        background: var(--amber-dim) !important;
        color: var(--amber-soft) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(245,158,11,0.12) !important;
    }}

    /* ── CHAT MESSAGES ────────────────────────────────────── */
    [data-testid="stChatMessage"] {{
        background: transparent !important; border: none !important;
        padding: 3px 0 !important; animation: fadeUp 0.3s ease both; gap: 10px !important;
    }}
    [data-testid="stChatMessage"][data-role="user"] > div:last-child {{
        background: linear-gradient(135deg, rgba(245,158,11,0.14), rgba(217,119,6,0.08)) !important;
        border: 1px solid rgba(245,158,11,0.2) !important;
        border-radius: 14px 14px 4px 14px !important;
        padding: 11px 15px !important; max-width: 72% !important;
    }}
    [data-testid="stChatMessage"][data-role="user"] [data-testid="stMarkdownContainer"] p {{
        color: var(--amber-soft) !important; font-size: 13.5px !important; line-height: 1.7 !important;
    }}
    [data-testid="stChatMessage"][data-role="assistant"] > div:last-child {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px 14px 14px 4px !important;
        padding: 13px 17px !important; max-width: 82% !important;
        box-shadow: var(--shadow) !important;
    }}
    [data-testid="stChatMessage"][data-role="assistant"] [data-testid="stMarkdownContainer"] p {{
        color: var(--txt) !important; font-size: 13.5px !important; line-height: 1.8 !important;
    }}
    [data-testid="chatAvatarIcon-user"] {{
        background: linear-gradient(135deg, #F59E0B, #D97706) !important;
        border-radius: 9px !important;
    }}
    [data-testid="chatAvatarIcon-assistant"] {{
        background: var(--bg4) !important;
        border: 1px solid var(--border) !important;
        border-radius: 9px !important;
    }}
    [data-testid="stChatMessage"] code {{
        background: var(--bg4) !important; border: 1px solid var(--border) !important;
        border-radius: 4px !important; padding: 2px 6px !important;
        font-size: 12px !important; color: var(--amber) !important;
    }}

    /* ── CHAT INPUT ───────────────────────────────────────── */
    [data-testid="stBottom"] {{
        background: linear-gradient(to top, var(--bg) 55%, rgba(0,0,0,0) 100%) !important;
        padding: 10px 2rem 18px !important;
    }}
    [data-testid="stChatInputContainer"] {{
        background: var(--card-bg) !important;
        border: 1px solid rgba(245,158,11,0.2) !important;
        border-radius: 14px !important;
        padding: 5px 7px 5px 16px !important;
        box-shadow: 0 0 0 4px rgba(245,158,11,0.04), 0 4px 20px rgba(0,0,0,0.2) !important;
        max-width: 860px !important; margin: 0 auto !important;
    }}
    [data-testid="stChatInputContainer"]:focus-within {{
        border-color: var(--amber) !important;
        box-shadow: 0 0 0 4px rgba(245,158,11,0.1), 0 4px 20px rgba(0,0,0,0.2) !important;
    }}
    [data-testid="stChatInputContainer"] textarea {{
        background: transparent !important; border: none !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13.5px !important; color: var(--txt) !important;
        caret-color: var(--amber) !important; box-shadow: none !important;
    }}
    [data-testid="stChatInputContainer"] textarea::placeholder {{
        color: var(--txt3) !important;
    }}
    [data-testid="stChatInputSubmitButton"] > button {{
        background: linear-gradient(135deg, #F59E0B, #D97706) !important;
        border: none !important; border-radius: 9px !important;
        width: 36px !important; height: 36px !important;
        box-shadow: 0 2px 10px rgba(245,158,11,0.35) !important;
        transition: var(--t) !important;
    }}
    [data-testid="stChatInputSubmitButton"] > button:hover {{
        transform: scale(1.08) !important;
    }}
    [data-testid="stChatInputSubmitButton"] > button svg {{
        color: #000 !important; fill: #000 !important;
    }}

    /* ── QUIZ ─────────────────────────────────────────────── */
    .quiz-card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 22px 24px; margin-bottom: 18px;
        box-shadow: var(--shadow);
        animation: fadeUp 0.3s ease both;
    }}
    .quiz-q-num {{
        font-size: 10px; font-weight: 600; letter-spacing: 1.2px;
        text-transform: uppercase; color: var(--amber); margin-bottom: 8px;
    }}
    .quiz-q-text {{ font-size: 15px; font-weight: 500; color: var(--txt); line-height: 1.6; }}

    .progress-track {{
        height: 5px; background: var(--bg4);
        border-radius: 99px; overflow: hidden; margin-bottom: 22px;
    }}
    .progress-fill {{
        height: 100%; border-radius: 99px;
        background: linear-gradient(90deg, #F59E0B, #FCD34D);
        transition: width 0.4s cubic-bezier(0.4,0,0.2,1);
    }}

    /* Radio options */
    [data-testid="stRadio"] > label {{ display: none !important; }}
    [data-testid="stRadio"] > div {{ gap: 7px !important; display: flex !important; flex-direction: column !important; }}
    [data-testid="stRadio"] label {{
        background: var(--bg4) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 11px 14px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13.5px !important; color: var(--txt2) !important;
        transition: var(--t) !important; cursor: pointer !important;
        display: block !important;
    }}
    [data-testid="stRadio"] label:hover {{
        border-color: var(--amber) !important;
        background: var(--amber-dim) !important;
        color: var(--amber-soft) !important;
    }}

    /* ── ANALYSIS CHARTS ──────────────────────────────────── */
    .analysis-card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 18px 20px; margin-bottom: 14px;
    }}
    .analysis-title {{
        font-size: 11px; font-weight: 600; letter-spacing: 0.9px;
        text-transform: uppercase; color: var(--txt3); margin-bottom: 14px;
    }}
    .bar-row {{
        display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
    }}
    .bar-label {{ font-size: 12px; color: var(--txt2); width: 110px; flex-shrink: 0; }}
    .bar-track {{
        flex: 1; height: 8px; background: var(--bg4);
        border-radius: 99px; overflow: hidden;
    }}
    .bar-fill {{
        height: 100%; border-radius: 99px;
        transition: width 0.6s cubic-bezier(0.4,0,0.2,1);
    }}
    .bar-val {{ font-size: 12px; font-weight: 600; color: var(--txt); width: 36px; text-align: right; }}

    .metric-grid {{
        display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 18px;
    }}
    .metric-box {{
        background: var(--bg3); border: 1px solid var(--border);
        border-radius: var(--radius); padding: 14px;
        text-align: center;
    }}
    .metric-val {{ font-size: 1.8rem; font-weight: 800; font-family: 'Syne', sans-serif; }}
    .metric-lbl {{ font-size: 10px; color: var(--txt3); margin-top: 3px; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; }}

    /* ── MAIN BUTTONS ─────────────────────────────────────── */
    .main .stButton > button {{
        background: linear-gradient(135deg, #F59E0B, #D97706) !important;
        color: #000 !important; border: none !important;
        border-radius: var(--radius) !important;
        padding: 10px 22px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13.5px !important; font-weight: 600 !important;
        box-shadow: 0 3px 14px rgba(245,158,11,0.28) !important;
        transition: var(--t) !important;
    }}
    .main .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 7px 22px rgba(245,158,11,0.42) !important;
    }}

    /* Alerts */
    [data-testid="stAlert"] {{
        border-radius: var(--radius) !important;
        font-size: 13px !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    /* Metrics */
    [data-testid="stMetric"] {{
        background: var(--card-bg) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 11px 13px !important;
    }}
    [data-testid="stMetric"] label {{
        color: var(--txt3) !important; font-size: 9.5px !important;
        font-weight: 600 !important; text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }}
    [data-testid="stMetricValue"] {{ color: var(--amber) !important; font-weight: 800 !important; }}

    /* History card */
    .history-item {{
        background: var(--card-bg); border: 1px solid var(--border);
        border-radius: var(--radius-lg); padding: 14px 16px;
        margin-bottom: 10px; transition: var(--t);
        cursor: default;
    }}
    .history-item:hover {{ border-color: rgba(245,158,11,0.3); }}
    .history-meta {{ font-size: 10.5px; color: var(--txt3); margin-bottom: 5px; }}
    .history-score {{
        font-size: 22px; font-weight: 800; font-family: 'Syne', sans-serif;
        color: var(--amber);
    }}

    /* Typing dots */
    .dots {{ display: flex; gap: 5px; align-items: center; padding: 4px 0; }}
    .dots span {{
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--amber); opacity: 0.4;
        animation: bounce-dot 1.1s ease infinite;
    }}
    .dots span:nth-child(2) {{ animation-delay: 0.16s; }}
    .dots span:nth-child(3) {{ animation-delay: 0.32s; }}

    .history-divider {{
        display: flex; align-items: center; gap: 10px;
        margin: 18px 0 10px; color: var(--txt3);
        font-size: 10.5px; font-weight: 600;
        letter-spacing: 1px; text-transform: uppercase;
    }}
    .history-divider::before, .history-divider::after {{
        content: ''; flex: 1; height: 1px; background: var(--border);
    }}

    /* Notes tab */
    .note-section {{
        background: var(--card-bg); border: 1px solid var(--border);
        border-radius: var(--radius-lg); padding: 20px 22px; margin-bottom: 14px;
    }}
    .note-section h3 {{
        font-family: 'Syne', sans-serif; font-size: 14px;
        font-weight: 700; color: var(--amber); margin-bottom: 10px;
    }}

    /* Flashcard */
    .flashcard {{
        background: var(--card-bg); border: 2px solid var(--amber);
        border-radius: var(--radius-xl); padding: 32px 28px;
        text-align: center; min-height: 180px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        animation: fadeUp 0.3s ease both;
        box-shadow: 0 0 0 4px var(--amber-dim);
    }}
    .flashcard-q {{ font-size: 16px; font-weight: 500; color: var(--txt); line-height: 1.6; }}
    .flashcard-a {{
        font-size: 15px; color: var(--green); margin-top: 16px;
        padding-top: 16px; border-top: 1px solid var(--border);
        font-weight: 500; line-height: 1.6;
    }}
    .flashcard-num {{
        font-size: 10px; font-weight: 600; letter-spacing: 1px;
        text-transform: uppercase; color: var(--txt3); margin-bottom: 14px;
    }}

    /* Mode toggle */
    .mode-toggle {{
        display: inline-flex; align-items: center; gap: 7px;
        padding: 6px 12px; border-radius: 99px;
        background: var(--bg3); border: 1px solid var(--border);
        font-size: 12px; color: var(--txt2); cursor: pointer;
    }}

    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes fadeDown {{
        from {{ opacity: 0; transform: translateY(-8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes float {{
        0%, 100% {{ transform: translateY(0); }}
        50%       {{ transform: translateY(-5px); }}
    }}
    @keyframes bounce-dot {{
        0%, 60%, 100% {{ transform: translateY(0); opacity: 0.4; }}
        30%            {{ transform: translateY(-7px); opacity: 1; }}
    }}
    @keyframes pulse-dot {{
        0%, 100% {{ opacity: 1; }}
        50%       {{ opacity: 0.3; }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
def init_state():
    defaults = dict(
        messages=[],
        pdf_text="", pdf_name=None,
        mode="Chat",
        active_tab="chat",
        dark_mode=True,
        quiz_q=[], quiz_idx=0, quiz_score=0,
        quiz_submitted=False, quiz_chosen=None,
        quiz_history=[],          # list of {score, total, date, answers}
        quiz_answers=[],          # per-question records [{q, chosen, correct, ans}]
        flashcards=[],            # [{q, a}]
        flash_idx=0, flash_revealed=False,
        notes_content="",
        model="meta-llama/llama-3-8b-instruct",
        temperature=0.7,
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


# ══════════════════════════════════════════════════════════════
# CLIENT
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def get_client():
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="sk-or-v1-xxxxxxxxxxxxxxxx",
    )


# ══════════════════════════════════════════════════════════════
# PDF HELPERS
# ══════════════════════════════════════════════════════════════
def load_pdf(file) -> str:
    reader = PdfReader(file)
    raw = "".join(p.extract_text() or "" for p in reader.pages)
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_text(raw)
    return "\n".join(chunks)

def ctx(n: int = 6000) -> str:
    return st.session_state.pdf_text[:n]


# ══════════════════════════════════════════════════════════════
# LLM WRAPPER
# ══════════════════════════════════════════════════════════════
def llm(prompt: str, system: str = "", max_tokens: int = 1400) -> str:
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    r = get_client().chat.completions.create(
        model=st.session_state.model,
        messages=msgs,
        max_tokens=max_tokens,
        temperature=st.session_state.temperature,
    )
    return r.choices[0].message.content


# ══════════════════════════════════════════════════════════════
# GENERATORS
# ══════════════════════════════════════════════════════════════
def gen_mcqs() -> str:
    return llm(
        "Generate exactly 10 MCQs from these notes.\n"
        "Format strictly:\nQ1. <question>\nA) ... B) ... C) ... D) ...\n✅ Answer: <letter>\n\n"
        f"Notes:\n{ctx()}", max_tokens=2000)

def gen_summary() -> str:
    return llm(
        "Summarize for exam prep with ## headings, bullet points, **bold** key terms.\n\n"
        f"Notes:\n{ctx()}")

def gen_notes() -> str:
    return llm(
        "Create revision notes with # headings, ## sub-headings, bullets, "
        "**bold** terms, `definitions`.\n\nNotes:\n" + ctx())

def gen_flashcards() -> list:
    raw = llm(
        "Create 10 flashcards from these notes.\n"
        "Format exactly:\nQ: <question>\nA: <answer>\n\n"
        f"Notes:\n{ctx()}", max_tokens=1600)
    cards = []
    for block in raw.strip().split("\n\n"):
        lines = block.strip().splitlines()
        q, a = "", ""
        for l in lines:
            if l.startswith("Q:"):
                q = l[2:].strip()
            elif l.startswith("A:"):
                a = l[2:].strip()
        if q and a:
            cards.append({"q": q, "a": a})
    return cards

def answer(q: str) -> str:
    context = f"Study notes:\n{ctx()}\n\n" if st.session_state.pdf_text else ""
    return llm(
        f"{context}Question: {q}",
        system="You are a clear, expert AI tutor. Be concise, educational, and structured.",
        max_tokens=900)


# ══════════════════════════════════════════════════════════════
# QUIZ PARSER
# ══════════════════════════════════════════════════════════════
def parse_quiz(text: str):
    questions = []
    for block in re.split(r"\n(?=Q\d+\.)", text.strip()):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        q_text = re.sub(r"^Q\d+\.\s*", "", lines[0])
        opts, ans = [], None
        for ln in lines[1:]:
            if re.match(r"^[A-D]\)", ln):
                opts.append(ln)
            if re.search(r"Answer", ln, re.I):
                m = re.search(r"[A-D]", ln)
                if m:
                    ans = m.group()
        if q_text and len(opts) == 4 and ans:
            questions.append({"q": q_text, "opts": opts, "ans": ans})
    return questions


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        dark = st.session_state.dark_mode
        mode_label = "☀️ Light Mode" if dark else "🌙 Dark Mode"

        st.markdown(f"""
        <div class="sb-logo">
            <div class="sb-logo-icon">⚡</div>
            <div>
                <div class="sb-logo-name">Study<span>AI</span></div>
                <div class="sb-logo-sub">AI-Powered Learning</div>
            </div>
            <div class="sb-badge">Beta</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-body">', unsafe_allow_html=True)

        # ── Theme Toggle ───────────────────────────────────
        if st.button(mode_label, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        # ── Upload ─────────────────────────────────────────
        st.markdown('<div class="sb-label">📁 Upload Notes</div>', unsafe_allow_html=True)
        f = st.file_uploader("PDF", type=["pdf"], label_visibility="collapsed")
        if f and f.name != st.session_state.pdf_name:
            with st.spinner("Reading PDF…"):
                st.session_state.pdf_text = load_pdf(f)
                st.session_state.pdf_name = f.name

        if st.session_state.pdf_name:
            nm = st.session_state.pdf_name
            disp = nm if len(nm) <= 26 else nm[:23] + "…"
            st.markdown(
                f'<div class="pdf-pill loaded"><div class="dot"></div>{disp}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="pdf-pill"><div class="dot empty"></div>No PDF loaded</div>',
                unsafe_allow_html=True)

        # ── Navigation ─────────────────────────────────────
        st.markdown('<div class="sb-label">🗂️ Navigation</div>', unsafe_allow_html=True)

        nav_items = [
            ("💬  Chat", "chat"),
            ("🎯  Quiz", "quiz"),
            ("📊  Analysis", "analysis"),
            ("🃏  Flashcards", "flashcards"),
            ("📒  Notes", "notes"),
        ]
        for label, tab_id in nav_items:
            is_active = st.session_state.active_tab == tab_id
            css_class = "sb-active-btn" if is_active else ""
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"nav_{tab_id}"):
                st.session_state.active_tab = tab_id
                if tab_id == "quiz":
                    if st.session_state.pdf_text:
                        st.session_state.update(
                            quiz_q=[], quiz_idx=0, quiz_score=0,
                            quiz_submitted=False, quiz_chosen=None,
                            quiz_answers=[]
                        )
                    else:
                        st.session_state.active_tab = "chat"
                        st.warning("Upload a PDF first.")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Quick Actions ──────────────────────────────────
        st.markdown('<div class="sb-label">⚡ Quick Actions</div>', unsafe_allow_html=True)

        def action(label, key, fn, tag):
            if st.button(label, key=key):
                if st.session_state.pdf_text:
                    with st.spinner("Generating…"):
                        result = fn()
                    st.session_state.messages.append(
                        {"role": "assistant", "content": f"**{tag}**\n\n{result}"}
                    )
                    st.session_state.active_tab = "chat"
                    st.rerun()
                else:
                    st.warning("Upload a PDF first.")

        action("🧩  Generate MCQs",    "mcq",  gen_mcqs,    "📋 MCQ Practice Set")
        action("📝  Summarize",         "sum",  gen_summary, "📝 Chapter Summary")

        # ── Settings ───────────────────────────────────────
        st.markdown('<div class="sb-label">⚙️ Settings</div>', unsafe_allow_html=True)
        st.session_state.model = st.selectbox(
            "Model",
            options=[
                "meta-llama/llama-3-8b-instruct",
                "meta-llama/llama-3-70b-instruct",
                "mistralai/mistral-7b-instruct",
                "google/gemma-2-9b-it",
            ],
        )
        st.session_state.temperature = st.slider(
            "Creativity", 0.0, 1.0,
            value=st.session_state.temperature, step=0.05,
        )

        # ── Danger ─────────────────────────────────────────
        st.markdown('<div class="sb-label">⚠️ Danger Zone</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-danger">', unsafe_allow_html=True)
        if st.button("🗑  Clear Chat", key="clear_btn"):
            st.session_state.messages = []
            st.session_state.active_tab = "chat"
            st.rerun()
        if st.button("🔄  Reset All", key="reset_all"):
            keys_to_keep = {"dark_mode", "model", "temperature"}
            for k in list(st.session_state.keys()):
                if k not in keys_to_keep:
                    del st.session_state[k]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Stats ──────────────────────────────────────────
        if st.session_state.messages or st.session_state.quiz_history:
            st.markdown('<div class="sb-label">📊 Session</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.metric("Msgs", len(st.session_state.messages))
            c2.metric("Quizzes", len(st.session_state.quiz_history))

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# WELCOME
# ══════════════════════════════════════════════════════════════
CHIPS = [
    ("📖", "Explain a Concept", "Explain Newton's laws of motion in simple terms with examples"),
    ("🔍", "Compare Topics",    "Compare mitosis vs meiosis — key differences in a table"),
    ("📊", "Summarize Notes",   "Summarize the main topics from my uploaded notes"),
    ("🗺️", "Study Plan",       "Create a structured 7-day study plan for my upcoming exam"),
]

def welcome():
    pdf_stat = f"<strong>{st.session_state.pdf_name}</strong>" if st.session_state.pdf_text else "None"
    quiz_count = len(st.session_state.quiz_history)

    st.markdown(f"""
    <div class="hero">
        <div class="hero-orb">⚡</div>
        <h1>Study smarter with <em>AI</em></h1>
        <p>Upload your notes and ask anything — summaries, MCQs, quizzes, flashcards, and expert answers.</p>
        <div class="stats-row">
            <div class="stat-pill">📄 PDF: {pdf_stat}</div>
            <div class="stat-pill">💬 <strong>{len(st.session_state.messages)}</strong> messages</div>
            <div class="stat-pill">🎯 <strong>{quiz_count}</strong> quizzes taken</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="small")
    for i, (icon, title, prompt) in enumerate(CHIPS):
        col = c1 if i % 2 == 0 else c2
        with col:
            label = f"{icon} **{title}**\n_{prompt[:52]}…_" if len(prompt) > 52 else f"{icon} **{title}**\n_{prompt}_"
            if st.button(label, key=f"chip_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.spinner("Thinking…"):
                    rep = answer(prompt)
                st.session_state.messages.append({"role": "assistant", "content": rep})
                st.rerun()


# ══════════════════════════════════════════════════════════════
# CHAT TAB
# ══════════════════════════════════════════════════════════════
def chat_tab():
    pdf_info = f"📄 {st.session_state.pdf_name}" if st.session_state.pdf_name else "📄 No PDF"
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-title">Study<span>AI</span> — Chat</div>
        <div style="display:flex;gap:8px;align-items:center">
            <div class="badge badge-green">{pdf_info}</div>
            <div class="badge badge-amber">💬 Chat</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.messages:
        welcome()
    else:
        st.markdown('<div class="history-divider">Chat History</div>', unsafe_allow_html=True)
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    if prompt := st.chat_input("Ask anything from your notes…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            ph = st.empty()
            ph.markdown('<div class="dots"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
            rep = answer(prompt)
            ph.markdown(rep)
        st.session_state.messages.append({"role": "assistant", "content": rep})
        st.rerun()


# ══════════════════════════════════════════════════════════════
# QUIZ TAB
# ══════════════════════════════════════════════════════════════
def quiz_tab():
    st.markdown("""
    <div class="topbar">
        <div class="topbar-title">Study<span style="color:var(--amber)">AI</span> — Quiz</div>
        <div class="badge badge-amber">🎯 Quiz Mode</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.pdf_text:
        st.warning("Please upload a PDF from the sidebar to start a quiz.")
        return

    if not st.session_state.quiz_q:
        with st.spinner("Building your quiz…"):
            raw = gen_mcqs()
            st.session_state.quiz_q = parse_quiz(raw)
            st.session_state.quiz_chosen = [None] * len(st.session_state.quiz_q)
            st.session_state.quiz_answers = []
            st.session_state.quiz_submitted = False
        if not st.session_state.quiz_q:
            st.error("Couldn't parse questions — try re-uploading your PDF.")
            return

    total = len(st.session_state.quiz_q)
    idx   = st.session_state.quiz_idx

    # ── Finished ─────────────────────────────────────────
    if idx >= total:
        score = st.session_state.quiz_score
        pct   = round(score / total * 100)
        emoji = "🏆" if pct >= 80 else "📚" if pct >= 50 else "💪"
        color = "var(--green)" if pct >= 80 else "var(--amber)" if pct >= 50 else "var(--red)"

        # Save to history
        record = {
            "score": score, "total": total, "pct": pct,
            "answers": list(st.session_state.quiz_answers)
        }
        if not st.session_state.quiz_history or st.session_state.quiz_history[-1] != record:
            st.session_state.quiz_history.append(record)

        st.markdown(f"""
        <div style="text-align:center;padding:40px 0 20px;animation:fadeUp .5s ease both">
            <div style="font-size:3.5rem;margin-bottom:14px;animation:float 3s ease infinite;display:block">{emoji}</div>
            <h2 style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:var(--txt);margin-bottom:8px">
                Quiz Complete!
            </h2>
            <div style="font-size:2.8rem;font-weight:800;color:{color};font-family:'Syne',sans-serif;margin:6px 0">
                {score}/{total}
            </div>
            <p style="font-size:14px;color:var(--txt2);margin-bottom:28px">
                {pct}% — {"Excellent!" if pct>=80 else "Good effort!" if pct>=50 else "Keep studying!"}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick review
        if st.session_state.quiz_answers:
            st.markdown("#### 📋 Quick Review")
            for i, a in enumerate(st.session_state.quiz_answers):
                icon = "✅" if a["correct"] else "❌"
                with st.expander(f"{icon} Q{i+1}: {a['q'][:70]}…" if len(a['q']) > 70 else f"{icon} Q{i+1}: {a['q']}"):
                    st.markdown(f"**Your answer:** {a['chosen']}")
                    if not a["correct"]:
                        st.markdown(f"**Correct answer:** {a['ans']}")

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("🔄  Restart Quiz", use_container_width=True):
                st.session_state.update(
                    quiz_idx=0, quiz_score=0, quiz_q=[],
                    quiz_submitted=False, quiz_chosen=None, quiz_answers=[]
                )
                st.rerun()
        with c2:
            if st.button("📊  View Analysis", use_container_width=True):
                st.session_state.active_tab = "analysis"
                st.rerun()
        return

    # ── Progress ─────────────────────────────────────────
    prog = idx / total
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:11.5px;color:var(--txt3);margin-bottom:6px">
        <span>Question {idx + 1} of {total}</span>
        <span>✅ Score: {st.session_state.quiz_score}</span>
    </div>
    <div class="progress-track">
        <div class="progress-fill" style="width:{prog*100:.0f}%"></div>
    </div>
    """, unsafe_allow_html=True)

    q = st.session_state.quiz_q[idx]

    st.markdown(f"""
    <div class="quiz-card">
        <div class="quiz-q-num">Question {idx + 1}</div>
        <div class="quiz-q-text">{q['q']}</div>
    </div>
    """, unsafe_allow_html=True)

    radio_key = f"quiz_radio_{idx}"

    if not st.session_state.quiz_submitted:
        chosen = st.radio("Choose:", q["opts"], key=radio_key, index=None, label_visibility="collapsed")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Submit Answer ✔", key=f"submit_{idx}", use_container_width=True):
                if chosen is None:
                    st.warning("Please select an answer first.")
                else:
                    correct = chosen[0] == q["ans"]
                    if correct:
                        st.session_state.quiz_score += 1
                    st.session_state.quiz_answers.append({
                        "q": q["q"], "chosen": chosen,
                        "correct": correct, "ans": q["ans"]
                    })
                    st.session_state["_last_chosen"]  = chosen
                    st.session_state["_last_correct"] = correct
                    st.session_state.quiz_submitted   = True
                    st.rerun()
    else:
        last_chosen  = st.session_state.get("_last_chosen", "")
        last_correct = st.session_state.get("_last_correct", False)

        for opt in q["opts"]:
            if opt[0] == q["ans"]:
                st.success(f"✅ {opt} — Correct Answer")
            elif opt == last_chosen and not last_correct:
                st.error(f"❌ {opt} — Your Answer")
            else:
                st.markdown(f"""
                <div style="padding:11px 14px;border-radius:var(--radius);
                            background:var(--bg4);border:1px solid var(--border);
                            color:var(--txt3);font-size:13.5px;margin-bottom:7px">
                    {opt}
                </div>
                """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Next Question →", key=f"next_{idx}", use_container_width=True):
                st.session_state.quiz_idx     += 1
                st.session_state.quiz_submitted = False
                st.session_state.pop("_last_chosen", None)
                st.session_state.pop("_last_correct", None)
                st.rerun()


# ══════════════════════════════════════════════════════════════
# ANALYSIS TAB
# ══════════════════════════════════════════════════════════════
def analysis_tab():
    st.markdown("""
    <div class="topbar">
        <div class="topbar-title">Study<span style="color:var(--amber)">AI</span> — Analysis</div>
        <div class="badge badge-blue">📊 Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.quiz_history

    if not history:
        st.markdown("""
        <div style="text-align:center;padding:60px 0;color:var(--txt3)">
            <div style="font-size:3rem;margin-bottom:16px">📊</div>
            <p style="font-size:15px">No quiz data yet.<br>Complete a quiz to see your analysis here.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Overall metrics
    all_scores  = [h["pct"] for h in history]
    avg_score   = round(sum(all_scores) / len(all_scores))
    best_score  = max(all_scores)
    total_q     = sum(h["total"] for h in history)
    total_right = sum(h["score"] for h in history)

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-box">
            <div class="metric-val" style="color:var(--amber)">{len(history)}</div>
            <div class="metric-lbl">Quizzes Taken</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="color:var(--green)">{avg_score}%</div>
            <div class="metric-lbl">Avg Score</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="color:var(--blue)">{best_score}%</div>
            <div class="metric-lbl">Best Score</div>
        </div>
        <div class="metric-box">
            <div class="metric-val" style="color:var(--purple)">{total_right}/{total_q}</div>
            <div class="metric-lbl">Total Correct</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score history bar chart
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    st.markdown('<div class="analysis-title">📈 Score History</div>', unsafe_allow_html=True)

    for i, h in enumerate(history):
        pct = h["pct"]
        color = "#10B981" if pct >= 80 else "#F59E0B" if pct >= 50 else "#EF4444"
        st.markdown(f"""
        <div class="bar-row">
            <div class="bar-label">Quiz {i+1}</div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%;background:{color}"></div>
            </div>
            <div class="bar-val" style="color:{color}">{pct}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Latest quiz question breakdown
    if history:
        latest = history[-1]
        if latest.get("answers"):
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown('<div class="analysis-title">🔍 Latest Quiz — Question Breakdown</div>', unsafe_allow_html=True)

            correct_count   = sum(1 for a in latest["answers"] if a["correct"])
            incorrect_count = len(latest["answers"]) - correct_count

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div style="text-align:center;padding:16px;background:var(--green-dim);
                            border:1px solid rgba(16,185,129,0.2);border-radius:var(--radius)">
                    <div style="font-size:2rem;font-weight:800;color:var(--green)">{correct_count}</div>
                    <div style="font-size:11px;color:var(--txt3);margin-top:4px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px">Correct</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style="text-align:center;padding:16px;background:var(--red-dim);
                            border:1px solid rgba(239,68,68,0.2);border-radius:var(--radius)">
                    <div style="font-size:2rem;font-weight:800;color:var(--red)">{incorrect_count}</div>
                    <div style="font-size:11px;color:var(--txt3);margin-top:4px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px">Incorrect</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            for i, a in enumerate(latest["answers"]):
                icon  = "✅" if a["correct"] else "❌"
                color = "var(--green)" if a["correct"] else "var(--red)"
                short = a["q"][:65] + "…" if len(a["q"]) > 65 else a["q"]
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:10px 0;
                            border-bottom:1px solid var(--border)">
                    <span style="font-size:15px">{icon}</span>
                    <div style="flex:1;font-size:13px;color:var(--txt2)">{short}</div>
                    <div style="font-size:11px;font-weight:600;color:{color}">
                        {"Correct" if a["correct"] else "Wrong"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Improvement trend
    if len(history) >= 2:
        trend = all_scores[-1] - all_scores[-2]
        trend_color = "var(--green)" if trend > 0 else "var(--red)" if trend < 0 else "var(--txt2)"
        trend_icon  = "↑" if trend > 0 else "↓" if trend < 0 else "→"
        st.markdown(f"""
        <div class="analysis-card" style="display:flex;align-items:center;gap:14px">
            <div style="font-size:2rem">{trend_icon}</div>
            <div>
                <div style="font-size:13.5px;color:var(--txt);font-weight:500">Score Trend</div>
                <div style="font-size:22px;font-weight:800;color:{trend_color}">
                    {'+' if trend > 0 else ''}{trend}% vs last quiz
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# FLASHCARDS TAB
# ══════════════════════════════════════════════════════════════
def flashcards_tab():
    st.markdown("""
    <div class="topbar">
        <div class="topbar-title">Study<span style="color:var(--amber)">AI</span> — Flashcards</div>
        <div class="badge badge-blue">🃏 Flashcards</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.pdf_text:
        st.warning("Upload a PDF first to generate flashcards.")
        return

    if not st.session_state.flashcards:
        if st.button("✨ Generate Flashcards", use_container_width=False):
            with st.spinner("Creating flashcards…"):
                st.session_state.flashcards  = gen_flashcards()
                st.session_state.flash_idx   = 0
                st.session_state.flash_revealed = False
            st.rerun()
        st.markdown("""
        <div style="text-align:center;padding:40px 0;color:var(--txt3)">
            <div style="font-size:2.5rem;margin-bottom:12px">🃏</div>
            <p>Generate AI flashcards from your notes for quick revision.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    cards = st.session_state.flashcards
    idx   = st.session_state.flash_idx % len(cards)
    card  = cards[idx]

    st.markdown(f"""
    <div class="flashcard">
        <div class="flashcard-num">Card {idx + 1} of {len(cards)}</div>
        <div class="flashcard-q">{card['q']}</div>
        {"<div class='flashcard-a'>" + card['a'] + "</div>" if st.session_state.flash_revealed else ""}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("← Prev", use_container_width=True):
            st.session_state.flash_idx = (idx - 1) % len(cards)
            st.session_state.flash_revealed = False
            st.rerun()
    with c2:
        label = "Hide Answer" if st.session_state.flash_revealed else "Reveal Answer"
        if st.button(label, use_container_width=True):
            st.session_state.flash_revealed = not st.session_state.flash_revealed
            st.rerun()
    with c3:
        if st.button("Next →", use_container_width=True):
            st.session_state.flash_idx = (idx + 1) % len(cards)
            st.session_state.flash_revealed = False
            st.rerun()
    with c4:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.flashcards = []
            st.rerun()

    # Progress dots
    dots_html = ""
    for i in range(len(cards)):
        color = "var(--amber)" if i == idx else "var(--bg4)"
        dots_html += f'<div style="width:7px;height:7px;border-radius:50%;background:{color};transition:background 0.2s"></div>'
    st.markdown(f"""
    <div style="display:flex;gap:6px;justify-content:center;margin-top:20px">{dots_html}</div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# NOTES TAB
# ══════════════════════════════════════════════════════════════
def notes_tab():
    st.markdown("""
    <div class="topbar">
        <div class="topbar-title">Study<span style="color:var(--amber)">AI</span> — Notes</div>
        <div class="badge badge-amber">📒 Notes</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.pdf_text:
        st.warning("Upload a PDF first to generate notes.")
        return

    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("📝 Generate Summary", use_container_width=True):
            with st.spinner("Summarizing…"):
                st.session_state.notes_content = gen_summary()
            st.rerun()
    with c2:
        if st.button("📒 Generate Full Notes", use_container_width=True):
            with st.spinner("Building notes…"):
                st.session_state.notes_content = gen_notes()
            st.rerun()

    if st.session_state.notes_content:
        st.markdown('<div class="note-section">', unsafe_allow_html=True)
        st.markdown(st.session_state.notes_content)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("📋 Send to Chat", use_container_width=False):
            st.session_state.messages.append({
                "role": "assistant",
                "content": st.session_state.notes_content
            })
            st.session_state.active_tab = "chat"
            st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px 0;color:var(--txt3)">
            <div style="font-size:2.5rem;margin-bottom:12px">📒</div>
            <p>Generate a summary or detailed notes from your uploaded PDF.</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    init_state()
    inject_css()
    sidebar()

    tab = st.session_state.active_tab
    if tab == "chat":
        chat_tab()
    elif tab == "quiz":
        quiz_tab()
    elif tab == "analysis":
        analysis_tab()
    elif tab == "flashcards":
        flashcards_tab()
    elif tab == "notes":
        notes_tab()


if __name__ == "__main__":
    main()
