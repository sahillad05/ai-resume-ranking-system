"""
AI ATS — Enterprise Recruiter Dashboard
Liquid Glass aesthetic with Frosted Pearl light theme.
"""

import streamlit as st
import requests
import pandas as pd
import time
import io

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI ATS — Recruiter Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://127.0.0.1:8000"

# ──────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────
for k, v in {
    "total_processed": 0, "scores": [], "categories": [],
    "ranking_history": [], "single_result": None,
    "single_file_name": None, "rank_result": None,
    "screening_history": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────────────────────
# CSS — Liquid Glass / Frosted Pearl
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg:            #F9FAFB;
    --bg2:           #F3F4F6;
    --surface:       rgba(255,255,255,0.72);
    --surface-h:     rgba(255,255,255,0.88);
    --bdr:           rgba(0,0,0,0.06);
    --glow:          rgba(30,58,138,0.06);
    --t1:            #111827;
    --t2:            #6B7280;
    --t3:            #9CA3AF;
    --cobalt:        #1E3A8A;
    --cobalt-l:      #2563EB;
    --lav:           #8B5CF6;
    --lav-bg:        rgba(139,92,246,0.08);
    --em:            #059669;
    --em-bg:         rgba(5,150,105,0.08);
    --am:            #D97706;
    --am-bg:         rgba(217,119,6,0.08);
    --sl:            #64748B;
    --sl-bg:         rgba(100,116,139,0.08);
    --rd:            #DC2626;
    --rd-bg:         rgba(220,38,38,0.06);
    --sh:            0 4px 12px rgba(0,0,0,0.05);
    --sh-h:          0 8px 24px rgba(0,0,0,0.08);
    --r:             14px;
    --rs:            10px;
    --g:             16px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
[data-testid="stMain"], .main, .block-container {
    background-color: var(--bg) !important;
    color: var(--t1) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif !important;
    font-size: 14px;
}

/* Force all text to dark */
p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stText"] {
    color: var(--t1) !important;
}

[data-testid="stHeader"] {
    background: rgba(249,250,251,0.85) !important;
    backdrop-filter: blur(12px) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: rgba(255,255,255,0.9) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
}
section[data-testid="stSidebar"] {
    border-right: 1px solid var(--bdr) !important;
    box-shadow: 1px 0 12px rgba(0,0,0,0.03) !important;
    width: 260px !important; min-width: 260px !important;
}
section[data-testid="stSidebar"] .stRadio > label {
    color: var(--t2) !important; font-weight: 600 !important;
    font-size: 11px !important; text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
section[data-testid="stSidebar"] .stRadio > div > label {
    background: transparent; border: none; border-radius: 8px;
    padding: 9px 14px !important; margin-bottom: 2px;
    transition: all 0.2s ease;
    color: var(--t2) !important; font-weight: 500 !important; font-size: 13.5px !important;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: var(--lav-bg); color: var(--cobalt) !important;
}
section[data-testid="stSidebar"] .stRadio > div [data-checked="true"] + label,
section[data-testid="stSidebar"] .stRadio > div label[data-baseweb="radio"]:has(input:checked) {
    background: rgba(30,58,138,0.06) !important;
    color: var(--cobalt) !important; font-weight: 600 !important;
    box-shadow: inset 2px 0 0 var(--cobalt);
}

/* ── Glass Card ── */
.g-card {
    background: var(--surface); backdrop-filter: blur(16px) saturate(160%);
    border-radius: var(--r); padding: 22px 24px; margin-bottom: var(--g);
    box-shadow: var(--sh), inset 0 0 0 1px rgba(255,255,255,0.5);
    border: 1px solid var(--bdr); transition: all 0.25s ease;
    animation: cardIn 0.4s ease-out both;
}
.g-card:hover {
    box-shadow: var(--sh-h), inset 0 0 0 2px var(--glow); transform: translateY(-1px);
}

/* ── KPI Card ── */
.kpi-card {
    background: var(--surface); backdrop-filter: blur(20px) saturate(180%);
    border-radius: var(--r); padding: 20px; text-align: center;
    box-shadow: var(--sh), inset 0 0 0 1px rgba(255,255,255,0.6);
    border: 1px solid var(--bdr); transition: all 0.25s ease;
    animation: cardIn 0.4s ease-out both;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    border-radius: var(--r) var(--r) 0 0;
}
.kpi-card.kc::before  { background: linear-gradient(90deg, var(--cobalt), var(--cobalt-l)); }
.kpi-card.kl::before  { background: linear-gradient(90deg, var(--lav), #A78BFA); }
.kpi-card.ke::before  { background: linear-gradient(90deg, var(--em), #34D399); }
.kpi-card.ka::before  { background: linear-gradient(90deg, var(--am), #FBBF24); }
.kpi-card:hover { box-shadow: var(--sh-h), inset 0 0 0 2px var(--glow); transform: translateY(-2px); }
.kpi-icon { font-size: 22px; margin-bottom: 6px; display: block; }
.kpi-val  { font-size: 28px; font-weight: 800; color: var(--t1); margin: 2px 0; letter-spacing: -0.02em; }
.kpi-lbl  { font-size: 11px; color: var(--t3); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.kpi-sub  { font-size: 11px; color: var(--t2); margin-top: 4px; }

/* ── Section Headers ── */
.sh { font-size: 22px; font-weight: 800; color: var(--t1); margin-bottom: 4px; letter-spacing: -0.01em; animation: cardIn 0.35s ease-out both; }
.ss { font-size: 13.5px; color: var(--t2); font-weight: 400; margin-bottom: 20px; animation: cardIn 0.4s ease-out both; }

/* ── Pills ── */
.pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 12px; border-radius: 100px; font-weight: 700; font-size: 12.5px;
}
.pill-lg { padding: 6px 16px; font-size: 14px; }
.pill-em  { background: var(--em-bg); color: var(--em) !important; }
.pill-am  { background: var(--am-bg); color: var(--am) !important; }
.pill-sl  { background: var(--sl-bg); color: var(--sl) !important; }
.pill-co  { background: rgba(30,58,138,0.06); color: var(--cobalt) !important; }
.pill-la  { background: var(--lav-bg); color: var(--lav) !important; }
.pill-rd  { background: var(--rd-bg); color: var(--rd) !important; }

/* ── Result Card ── */
.rc {
    background: var(--surface); backdrop-filter: blur(16px) saturate(160%);
    border: 1px solid var(--bdr); border-radius: var(--r);
    padding: 28px; margin: var(--g) 0;
    box-shadow: var(--sh), inset 0 0 0 1px rgba(255,255,255,0.5);
    animation: cardIn 0.5s ease-out both;
}
.rc-cat { font-size: 24px; font-weight: 800; color: var(--cobalt); letter-spacing: -0.01em; }
.rc-lbl { font-size: 11px; color: var(--t3); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; margin-bottom: 4px; }
.rc-val { font-size: 16px; font-weight: 600; color: var(--t1); }

/* ── Bar ── */
.bo { background: var(--bg2); border-radius: 8px; height: 8px; overflow: hidden; margin: 6px 0 12px; }
.bi { height: 100%; border-radius: 8px; animation: barFill 0.9s ease-out both; }
.bi-em { background: linear-gradient(90deg, var(--em), #34D399); }
.bi-am { background: linear-gradient(90deg, var(--am), #FBBF24); }
.bi-sl { background: linear-gradient(90deg, var(--sl), #94A3B8); }
.bi-co { background: linear-gradient(90deg, var(--cobalt), var(--cobalt-l)); }

/* ── Gauge ── */
.gw { position: relative; width: 72px; height: 72px; flex-shrink: 0; }
.gw svg { transform: rotate(-90deg); }
.g-bg { fill: none; stroke: var(--bg2); stroke-width: 5; }
.g-fl { fill: none; stroke-width: 5; stroke-linecap: round; animation: gaugeIn 1s ease-out both; }
.g-em { stroke: var(--em); }
.g-am { stroke: var(--am); }
.g-sl { stroke: var(--sl); }
.g-lb { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); font-size: 14px; font-weight: 800; color: var(--t1); }

/* ── Rank Badge ── */
.rb { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 8px; font-weight: 800; font-size: 12px; color: #fff; flex-shrink: 0; }
.r1 { background: linear-gradient(135deg, #F59E0B, #F97316); }
.r2 { background: linear-gradient(135deg, #94A3B8, #64748B); }
.r3 { background: linear-gradient(135deg, #B45309, #D97706); }
.rn { background: linear-gradient(135deg, #CBD5E1, #94A3B8); }

/* ── Candidate Row ── */
.cr {
    background: var(--surface); backdrop-filter: blur(12px);
    border: 1px solid var(--bdr); border-radius: var(--rs);
    padding: 14px 18px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 16px;
    transition: all 0.2s ease; animation: cardIn 0.35s ease-out both;
}
.cr:hover { box-shadow: var(--sh-h), inset 0 0 0 2px var(--glow); transform: translateY(-1px); }
.cn { font-weight: 600; color: var(--t1); font-size: 13.5px; min-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cs { font-size: 18px; font-weight: 800; color: var(--cobalt); min-width: 56px; }
.cbo { flex: 1; background: var(--bg2); border-radius: 6px; height: 6px; overflow: hidden; }
.cbi { height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--cobalt), var(--cobalt-l)); animation: barFill 0.8s ease-out both; }
.cd { font-size: 11px; color: var(--t3); text-align: center; min-width: 64px; }
.cd span { display: block; font-size: 13px; font-weight: 700; color: var(--t1); }

/* ── Upload Zone ── */
.uz {
    border: 2px dashed rgba(30,58,138,0.15); border-radius: var(--r);
    padding: 36px; text-align: center; background: rgba(30,58,138,0.02);
    transition: all 0.3s ease; animation: cardIn 0.4s ease-out both;
}
.uz:hover { border-color: rgba(30,58,138,0.3); background: rgba(30,58,138,0.04); }
.uz-ic { font-size: 36px; margin-bottom: 8px; display: block; animation: floatS 3s ease-in-out infinite; }
.uz-tx { font-size: 14px; color: var(--t2); font-weight: 500; }
.uz-ht { font-size: 12px; color: var(--t3); margin-top: 4px; }

/* ── Buttons ── */
.stButton > button {
    background: var(--cobalt) !important; color: #fff !important;
    border: none !important; border-radius: var(--rs) !important;
    padding: 10px 28px !important; font-weight: 700 !important;
    font-size: 13.5px !important; transition: all 0.25s ease !important;
    box-shadow: 0 2px 8px rgba(30,58,138,0.2) !important;
}
.stButton > button:hover {
    background: var(--cobalt-l) !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(30,58,138,0.25) !important;
}
.stDownloadButton > button {
    background: var(--em) !important; color: #fff !important;
    border: none !important; border-radius: var(--rs) !important;
    padding: 9px 24px !important; font-weight: 700 !important;
    font-size: 13px !important; transition: all 0.25s ease !important;
    box-shadow: 0 2px 8px rgba(5,150,105,0.15) !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(5,150,105,0.2) !important;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.6) !important; border: 1.5px dashed rgba(30,58,138,0.12) !important;
    border-radius: var(--rs) !important; padding: 12px !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(30,58,138,0.25) !important; }
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.8) !important; color: var(--t2) !important;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--t2) !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: var(--cobalt) !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
}
[data-testid="stFileUploaderDropzone"] small { color: var(--t3) !important; }

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {
    background: #fff !important; border: 1.5px solid rgba(0,0,0,0.08) !important;
    border-radius: var(--rs) !important; color: var(--t1) !important;
    font-family: 'Inter', sans-serif !important; font-size: 13.5px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--cobalt) !important; box-shadow: 0 0 0 3px rgba(30,58,138,0.06) !important;
}
.stTextArea textarea::placeholder { color: var(--t3) !important; }

/* ── Alerts ── */
.a-ok  { background:var(--em-bg); border:1px solid rgba(5,150,105,0.15); border-radius:var(--rs); padding:14px 18px; color:var(--em); font-weight:500; font-size:13.5px; animation:cardIn 0.35s ease-out both; }
.a-err { background:var(--rd-bg); border:1px solid rgba(220,38,38,0.15); border-radius:var(--rs); padding:14px 18px; color:var(--rd); font-weight:500; font-size:13.5px; animation:cardIn 0.35s ease-out both; }
.a-inf { background:rgba(30,58,138,0.04); border:1px solid rgba(30,58,138,0.1); border-radius:var(--rs); padding:14px 18px; color:var(--cobalt); font-weight:500; font-size:13.5px; animation:cardIn 0.35s ease-out both; }

/* ── Empty State ── */
.es { text-align: center; padding: 48px 20px; animation: cardIn 0.4s ease-out both; }
.es-ic { font-size: 40px; margin-bottom: 12px; display: block; opacity: 0.4; }
.es-tx { font-size: 15px; font-weight: 600; color: var(--t2); }
.es-sb { font-size: 12.5px; color: var(--t3); margin-top: 4px; }

/* ── Divider ── */
.dv { height: 1px; background: linear-gradient(90deg, transparent, var(--bdr), transparent); margin: 24px 0; border: none; }

/* ── Logo ── */
.lw { text-align: center; padding: 20px 12px 14px; }
.lm { font-size: 22px; font-weight: 900; color: var(--cobalt); letter-spacing: -0.02em; }
.ls { font-size: 10px; color: var(--t3); text-transform: uppercase; letter-spacing: 0.12em; margin-top: 2px; font-weight: 600; }

/* ── Sidebar Footer ── */
.sf { margin-top: 32px; padding: 14px 12px; border-top: 1px solid var(--bdr); }
.sfi { display: flex; align-items: center; gap: 6px; font-size: 11px; color: var(--t3); margin-bottom: 6px; }
.dok { width:6px;height:6px;border-radius:50%;background:var(--em);box-shadow:0 0 6px rgba(5,150,105,0.4);display:inline-block;animation:pulse 2s ease-in-out infinite; }
.derr { width:6px;height:6px;border-radius:50%;background:var(--rd);box-shadow:0 0 6px rgba(220,38,38,0.3);display:inline-block; }

/* ── History Item ── */
.hi { background:var(--surface); border:1px solid var(--bdr); border-radius:8px; padding:10px 14px; margin-bottom:6px; display:flex; justify-content:space-between; align-items:center; font-size:13px; animation:cardIn 0.3s ease-out both; }

/* ── Charts ── */
[data-testid="stVegaLiteChart"],
[data-testid="stArrowVegaLiteChart"] {
    background: transparent !important;
}
canvas { background: transparent !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--surface) !important; border: 1px solid var(--bdr) !important;
    border-radius: var(--rs) !important;
}
[data-testid="stExpander"] summary span { color: var(--t1) !important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: #fff !important;
}

/* ── Keyframes ── */
@keyframes cardIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
@keyframes barFill { from { width: 0; } }
@keyframes gaugeIn { from { stroke-dashoffset: 188; } }
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }
@keyframes floatS { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-5px); } }
@keyframes spin { to { transform: rotate(360deg); } }

.spinner { width:36px;height:36px;border:3px solid var(--bg2);border-top:3px solid var(--cobalt);border-radius:50%;animation:spin 0.7s linear infinite;margin:16px auto; }

/* ── Hide chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def api_ok() -> bool:
    try: return requests.get(f"{API_BASE}/", timeout=3).status_code == 200
    except Exception: return False

def predict_single(file):
    try:
        r = requests.post(f"{API_BASE}/predict",
                          files={"file": (file.name, file.getvalue(), "application/pdf")}, timeout=30)
        return r.json() if r.status_code == 200 else {"error": r.json().get("error", f"HTTP {r.status_code}")}
    except requests.ConnectionError:
        return {"error": "Cannot reach API. Ensure FastAPI is running."}
    except Exception as e:
        return {"error": str(e)}

def rank_multiple(jd, files):
    try:
        r = requests.post(f"{API_BASE}/rank",
                          files=[("files", (f.name, f.getvalue(), "application/pdf")) for f in files],
                          data={"job_description": jd}, timeout=60)
        return r.json() if r.status_code == 200 else {"error": r.json().get("error", f"HTTP {r.status_code}")}
    except requests.ConnectionError:
        return {"error": "Cannot reach API. Ensure FastAPI is running."}
    except Exception as e:
        return {"error": str(e)}

def tier(pct):
    if pct >= 75: return "em"
    if pct >= 50: return "am"
    return "sl"

def tier_label(pct):
    if pct >= 85: return "Excellent"
    if pct >= 75: return "Strong"
    if pct >= 60: return "Moderate"
    if pct >= 40: return "Fair"
    return "Low"

def gauge_svg(pct, sz=72):
    r = 30; c = 188.5; off = c * (1 - pct / 100); t = tier(pct)
    return (
        f'<div class="gw" style="width:{sz}px;height:{sz}px;">'
        f'<svg width="{sz}" height="{sz}" viewBox="0 0 {sz} {sz}">'
        f'<circle class="g-bg" cx="{sz//2}" cy="{sz//2}" r="{r}"/>'
        f'<circle class="g-fl g-{t}" cx="{sz//2}" cy="{sz//2}" r="{r}" '
        f'stroke-dasharray="{c}" stroke-dashoffset="{off}"/>'
        f'</svg><div class="g-lb">{pct:.0f}%</div></div>'
    )


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="lw"><div class="lm">⚡ AI ATS</div><div class="ls">Intelligent Talent Screening</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="dv"></div>', unsafe_allow_html=True)

    page = st.radio("NAV", ["🏠  Dashboard", "📄  Resume Screening", "📊  Resume Ranking", "📈  Analytics"], label_visibility="collapsed")

    st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
    on = api_ok()
    st.markdown(f'''
        <div class="sf">
            <div class="sfi">🧠 &nbsp;Model v2.1 · XGBoost</div>
            <div class="sfi"><span class="{"dok" if on else "derr"}"></span>API {"Online" if on else "Offline"}</div>
            <div class="sfi" style="margin-top:8px;font-size:10px;">© 2026 AI ATS Platform</div>
        </div>''', unsafe_allow_html=True)


# ======================================================================
#  DASHBOARD
# ======================================================================

if page == "🏠  Dashboard":
    st.markdown('<div class="sh">Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss">Live AI-driven insights across your recruitment pipeline.</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    avg = round(sum(st.session_state.scores) / len(st.session_state.scores), 1) if st.session_state.scores else 0
    uc = len(set(st.session_state.categories)) if st.session_state.categories else 0
    tc = max(set(st.session_state.categories), key=st.session_state.categories.count) if st.session_state.categories else "—"

    with k1:
        st.markdown(f'<div class="kpi-card kc"><span class="kpi-icon">🎯</span><div class="kpi-val">{avg}%</div><div class="kpi-lbl">AI Match Rate</div><div class="kpi-sub">Avg classification confidence</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card kl"><span class="kpi-icon">🚀</span><div class="kpi-val">{st.session_state.total_processed}</div><div class="kpi-lbl">Pipeline Velocity</div><div class="kpi-sub">Total resumes processed</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card ke"><span class="kpi-icon">🌐</span><div class="kpi-val">{uc}</div><div class="kpi-lbl">Diversity Index</div><div class="kpi-sub">Unique role categories</div></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card ka"><span class="kpi-icon">🏷️</span><div class="kpi-val" style="font-size:16px;">{tc}</div><div class="kpi-lbl">Top Category</div><div class="kpi-sub">Most frequent role match</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="dv"></div>', unsafe_allow_html=True)

    ca, cb = st.columns(2, gap="medium")
    with ca:
        st.markdown('<div class="g-card"><div style="font-size:15px;font-weight:700;margin-bottom:8px;">📄 Single Resume Screening</div><div style="color:var(--t2);font-size:13px;line-height:1.6;">Upload one resume for instant AI classification and confidence scoring.</div></div>', unsafe_allow_html=True)
    with cb:
        st.markdown('<div class="g-card"><div style="font-size:15px;font-weight:700;margin-bottom:8px;">📊 Multi Resume Ranking</div><div style="color:var(--t2);font-size:13px;line-height:1.6;">Rank multiple candidates against a job description. Export results as CSV.</div></div>', unsafe_allow_html=True)

    if st.session_state.ranking_history or st.session_state.screening_history:
        st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sh" style="font-size:18px;">Recent Activity</div>', unsafe_allow_html=True)

    for i, e in enumerate(reversed(st.session_state.ranking_history[-3:])):
        t = tier(e["top_score"])
        st.markdown(f'<div class="hi" style="animation-delay:{i*0.06}s;"><div><span style="font-weight:700;">🏆 {e["top_candidate"]}</span> <span class="pill pill-{t}" style="margin-left:8px;">{e["top_score"]}%</span></div><span style="color:var(--t3);font-size:11px;">{e["candidates"]} candidates</span></div>', unsafe_allow_html=True)

    for i, e in enumerate(reversed(st.session_state.screening_history[-5:])):
        t = tier(e["confidence"])
        st.markdown(f'<div class="hi" style="animation-delay:{i*0.06}s;"><div><span style="font-weight:600;">📄 {e["file_name"]}</span> <span style="color:var(--t3);margin:0 6px;">→</span> <span class="pill pill-co">{e["category"]}</span></div><span class="pill pill-{t}">{e["confidence"]}%</span></div>', unsafe_allow_html=True)


# ======================================================================
#  SINGLE RESUME SCREENING
# ======================================================================

elif page == "📄  Resume Screening":
    st.markdown('<div class="sh">Resume Screening</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss">Upload a resume for instant AI-powered classification and confidence analysis.</div>', unsafe_allow_html=True)

    st.markdown('<div class="uz"><span class="uz-ic">📤</span><div class="uz-tx">Drag & drop your resume below</div><div class="uz-ht">Accepts PDF · Max 200 MB</div></div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"], label_visibility="collapsed", key="single_upload")

    if uploaded_file is not None:
        st.markdown(f'<div class="a-inf" style="margin:12px 0;">📎 &nbsp;<strong>{uploaded_file.name}</strong> <span style="color:var(--t3);margin-left:6px;">({round(uploaded_file.size/1024,1)} KB)</span></div>', unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            run = st.button("🚀  Analyze Resume", use_container_width=True)
        with c2:
            if st.button("✕  Clear", use_container_width=True):
                st.session_state.single_result = None
                st.session_state.single_file_name = None
                st.rerun()

        if run:
            ph = st.empty()
            ph.markdown('<div style="text-align:center;padding:32px;"><div class="spinner"></div><div style="color:var(--t2);font-size:13px;margin-top:12px;">Analyzing resume…</div></div>', unsafe_allow_html=True)
            result = predict_single(uploaded_file)
            time.sleep(0.4)
            ph.empty()
            st.session_state.single_result = result
            st.session_state.single_file_name = uploaded_file.name
            if result and "error" not in result:
                cp = round(result["confidence"] * 100, 1)
                st.session_state.total_processed += 1
                st.session_state.scores.append(cp)
                st.session_state.categories.append(result["predicted_category"])
                st.session_state.screening_history.append({"file_name": uploaded_file.name, "category": result["predicted_category"], "confidence": cp})
            st.rerun()

        # ── Persisted Result — split into small st.markdown calls ──
        if st.session_state.single_result is not None:
            res = st.session_state.single_result
            if "error" not in res:
                cat = res["predicted_category"]
                cp = round(res["confidence"] * 100, 1)
                t = tier(cp)
                lbl = tier_label(cp)
                g = gauge_svg(cp)

                st.markdown(f'<div class="a-ok" style="margin-bottom:16px;">✅ &nbsp;Analysis complete — <strong>{st.session_state.single_file_name}</strong> classified successfully.</div>', unsafe_allow_html=True)

                # Result card: top section (gauge + category + pill)
                st.markdown(f'''<div class="rc">
                    <div style="display:flex;align-items:center;gap:24px;">
                        {g}
                        <div style="flex:1;">
                            <div class="rc-lbl">Predicted Job Category</div>
                            <div class="rc-cat">{cat}</div>
                            <div style="margin-top:12px;display:flex;align-items:center;gap:10px;">
                                <span class="pill pill-lg pill-{t}">{cp}% Match</span>
                                <span style="color:var(--t3);font-size:12px;">{lbl} confidence</span>
                            </div>
                        </div>
                    </div>
                </div>''', unsafe_allow_html=True)

                # Confidence breakdown bar
                st.markdown(f'''<div class="rc" style="padding:20px 24px;margin-top:0;">
                    <div class="rc-lbl">Confidence Breakdown</div>
                    <div class="bo"><div class="bi bi-{t}" style="width:{cp}%;"></div></div>
                </div>''', unsafe_allow_html=True)

                # Experience + AI note
                st.markdown(f'''<div class="rc" style="padding:20px 24px;margin-top:0;">
                    <div class="rc-lbl">Experience Detected</div>
                    <div class="rc-val">Extracted from resume text</div>
                    <div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--bdr);">
                        <span style="color:var(--t3);font-size:12px;line-height:1.6;">
                            <span class="pill pill-la" style="margin-right:6px;">AI</span>
                            NLP feature extraction + XGBoost classification determined the most likely job category.
                        </span>
                    </div>
                </div>''', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="a-err">❌ &nbsp;<strong>Analysis Failed</strong> — {res.get("error","Unknown error")}</div>', unsafe_allow_html=True)
    else:
        if st.session_state.single_result is not None:
            st.session_state.single_result = None
            st.session_state.single_file_name = None
        st.markdown('<div class="es"><span class="es-ic">📋</span><div class="es-tx">No resume uploaded</div><div class="es-sb">Upload a PDF above to begin screening</div></div>', unsafe_allow_html=True)

    if st.session_state.screening_history:
        st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sh" style="font-size:16px;">Screening History</div>', unsafe_allow_html=True)
        for i, e in enumerate(reversed(st.session_state.screening_history[-5:])):
            t = tier(e["confidence"])
            st.markdown(f'<div class="hi" style="animation-delay:{i*0.05}s;"><div><span style="font-weight:600;">{e["file_name"]}</span> <span style="color:var(--t3);margin:0 6px;">→</span> <span class="pill pill-co">{e["category"]}</span></div><span class="pill pill-{t}">{e["confidence"]}% Match</span></div>', unsafe_allow_html=True)


# ======================================================================
#  MULTI RESUME RANKING
# ======================================================================

elif page == "📊  Resume Ranking":
    st.markdown('<div class="sh">Resume Ranking</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss">Compare and rank multiple candidates against a job description using hybrid AI scoring.</div>', unsafe_allow_html=True)

    st.markdown('<div class="g-card" style="padding:16px 20px;"><div style="font-size:13px;font-weight:700;margin-bottom:4px;">📝 Job Description</div></div>', unsafe_allow_html=True)
    job_desc = st.text_area("JD", height=140, placeholder="Paste the full job description here — skills, qualifications, experience…", label_visibility="collapsed", key="job_desc_input")

    st.markdown('<div class="uz" style="padding:28px;"><span class="uz-ic" style="font-size:30px;">📁</span><div class="uz-tx">Upload candidate resumes below</div><div class="uz-ht">Multiple PDF files supported</div></div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Resumes", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed", key="multi_upload")

    if uploaded_files:
        names = ", ".join(f.name for f in uploaded_files[:3]) + ("…" if len(uploaded_files) > 3 else "")
        st.markdown(f'<div class="a-inf" style="margin:10px 0;">📎 &nbsp;<strong>{len(uploaded_files)} file{"s" if len(uploaded_files)>1 else ""}</strong> — <span style="color:var(--t3);">{names}</span></div>', unsafe_allow_html=True)

    can = bool(job_desc and job_desc.strip() and uploaded_files)
    rc1, rc2 = st.columns([3, 1])
    with rc1:
        go = st.button("🚀  Run AI Ranking", use_container_width=True, disabled=not can)
    with rc2:
        if st.button("✕  Clear", use_container_width=True, key="rk_clr"):
            st.session_state.rank_result = None
            st.rerun()

    if go:
        ph = st.empty()
        ph.markdown('<div style="text-align:center;padding:36px;"><div class="spinner"></div><div style="color:var(--t2);font-size:13px;margin-top:12px;">Ranking candidates…</div></div>', unsafe_allow_html=True)
        result = rank_multiple(job_desc, uploaded_files)
        time.sleep(0.4)
        ph.empty()
        st.session_state.rank_result = result
        if result and "error" not in result:
            ranking = result.get("ranking", [])
            if ranking:
                st.session_state.total_processed += len(ranking)
                for r in ranking:
                    st.session_state.scores.append(r["final_score"])
                st.session_state.ranking_history.append({"top_candidate": ranking[0]["file_name"], "top_score": ranking[0]["final_score"], "candidates": len(ranking)})
        st.rerun()

    if st.session_state.rank_result is not None:
        res = st.session_state.rank_result
        if "error" not in res:
            ranking = res.get("ranking", [])
            if ranking:
                st.markdown(f'<div class="a-ok" style="margin-bottom:16px;">✅ &nbsp;Ranking complete — <strong>{len(ranking)} candidates</strong> analyzed.</div>', unsafe_allow_html=True)

                for idx, c in enumerate(ranking):
                    rn = idx + 1
                    rcls = f"r{rn}" if rn <= 3 else "rn"
                    medal = ["🥇","🥈","🥉"][idx] if idx < 3 else ""
                    ts = tier(c["final_score"])
                    tc2 = tier(c["classification_confidence"])
                    d = idx * 0.06
                    st.markdown(
                        f'<div class="cr" style="animation-delay:{d}s;">'
                        f'<div class="rb {rcls}">#{rn}</div>'
                        f'<div class="cn">{medal} {c["file_name"]}</div>'
                        f'<span class="pill pill-lg pill-{ts}">{c["final_score"]}%</span>'
                        f'<div style="flex:1;"><div class="cbo"><div class="cbi" style="width:{c["final_score"]}%;animation-delay:{d+0.2}s;"></div></div></div>'
                        f'<div class="cd"><span>{c["similarity"]}%</span>Similarity</div>'
                        f'<div class="cd"><span class="pill pill-{tc2}" style="font-size:11px;">{c["classification_confidence"]}%</span>Confidence</div>'
                        f'<div class="cd"><span>{c["experience_years"]}y</span>Exp</div>'
                        f'</div>', unsafe_allow_html=True)

                st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
                df = pd.DataFrame(ranking)
                df.insert(0, "rank", range(1, len(df) + 1))
                st.download_button("📥  Download CSV", df.to_csv(index=False).encode("utf-8"), "ai_resume_rankings.csv", "text/csv", use_container_width=True)
                with st.expander("📋  Detailed Results Table"):
                    st.dataframe(df.style.format({"final_score":"{:.2f}","similarity":"{:.2f}","classification_confidence":"{:.2f}"}), use_container_width=True, hide_index=True)
            else:
                st.markdown('<div class="a-err">⚠️ No valid resumes processed.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="a-err">❌ <strong>Failed</strong> — {res.get("error","Unknown")}</div>', unsafe_allow_html=True)
    elif not can and not st.session_state.rank_result:
        st.markdown('<div class="es"><span class="es-ic">🎯</span><div class="es-tx">Ready to rank candidates</div><div class="es-sb">Enter a job description and upload resumes</div></div>', unsafe_allow_html=True)


# ======================================================================
#  ANALYTICS
# ======================================================================

elif page == "📈  Analytics":
    st.markdown('<div class="sh">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="ss">Insights and trends from your AI-powered screening sessions.</div>', unsafe_allow_html=True)

    if st.session_state.total_processed == 0:
        st.markdown('<div class="es"><span class="es-ic">📊</span><div class="es-tx">No data yet</div><div class="es-sb">Process resumes to see analytics</div></div>', unsafe_allow_html=True)
    else:
        a1, a2, a3 = st.columns(3, gap="medium")
        with a1:
            st.markdown(f'<div class="kpi-card kc"><span class="kpi-icon">📄</span><div class="kpi-val">{st.session_state.total_processed}</div><div class="kpi-lbl">Total Processed</div></div>', unsafe_allow_html=True)
        with a2:
            av = round(sum(st.session_state.scores)/len(st.session_state.scores),1) if st.session_state.scores else 0
            st.markdown(f'<div class="kpi-card ke"><span class="kpi-icon">📈</span><div class="kpi-val">{av}%</div><div class="kpi-lbl">Avg Confidence</div></div>', unsafe_allow_html=True)
        with a3:
            uc = len(set(st.session_state.categories)) if st.session_state.categories else 0
            st.markdown(f'<div class="kpi-card kl"><span class="kpi-icon">🏷️</span><div class="kpi-val">{uc}</div><div class="kpi-lbl">Unique Categories</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="dv"></div>', unsafe_allow_html=True)

        if st.session_state.scores:
            st.markdown('<div class="g-card"><div style="font-size:15px;font-weight:700;margin-bottom:12px;">📊 Score Distribution</div></div>', unsafe_allow_html=True)
            st.bar_chart(pd.DataFrame({"Score": st.session_state.scores}), use_container_width=True, color="#1E3A8A")

        if st.session_state.categories:
            st.markdown('<div class="dv"></div>', unsafe_allow_html=True)
            st.markdown('<div class="g-card"><div style="font-size:15px;font-weight:700;margin-bottom:12px;">🏷️ Category Breakdown</div></div>', unsafe_allow_html=True)
            from collections import Counter
            cc = Counter(st.session_state.categories)
            mx = max(cc.values())
            for cat, cnt in cc.most_common():
                pct = round(cnt / mx * 100)
                st.markdown(f'<div class="g-card" style="padding:12px 18px;"><div style="display:flex;align-items:center;gap:14px;"><div style="min-width:140px;font-weight:600;font-size:13px;">{cat}</div><div style="flex:1;"><div class="bo" style="height:6px;margin:0;"><div class="bi bi-co" style="width:{pct}%;height:100%;"></div></div></div><div style="min-width:36px;text-align:right;font-weight:700;color:var(--cobalt);font-size:13px;">{cnt}</div></div></div>', unsafe_allow_html=True)
