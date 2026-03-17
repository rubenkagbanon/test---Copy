# =============================================================================
# DASHBOARD QVT — Qualité de Vie au Travail
# Inspiré du modèle Karasek · 2 onglets
# Lancer avec : streamlit run dashboard_qvt.py
# Dépendances  : pip install streamlit plotly pandas numpy openpyxl
# =============================================================================

import io
import re
import unicodedata

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG PAGE
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="QVT Dashboard",
    page_icon="❤️",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE & CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
C = {
    "bg":        "#F0F7FF",
    "card":      "#FFFFFF",
    "text":      "#0F2340",
    "muted":     "#6B88A8",
    "border":    "#D6E8F7",
    "blue":      "#38A3E8",
    "orange":    "#F97316",
    "green":     "#22C55E",
    "red":       "#EF4444",
    "purple":    "#A78BFA",
    "dark_red":  "#FD0000",
    "light_red": "#E85D35",
    "light_grn": "#6DCF7A",
    "dark_grn":  "#1B7A32",
}

RESPONSE_ORDER  = ["Très insatisfait", "Insatisfait", "Satisfait", "Très satisfait"]
RESPONSE_COLORS = {
    "Très insatisfait": C["dark_red"],
    "Insatisfait":      C["light_red"],
    "Satisfait":        C["light_grn"],
    "Très satisfait":   C["dark_grn"],
}

QUESTIONS = [
    "Je comprends clairement mes missions.",
    "Je dispose des moyens nécessaires pour faire mon travail.",
    "Je peux exprimer mon point de vue au travail.",
    "Je suis reconnu(e) pour le travail bien fait.",
    "Mon travail a du sens pour moi.",
    "Je suis écouté(e) par ma hiérarchie.",
    "J'ai un bon équilibre entre vie privée et professionnelle.",
    "J'ai des relations de qualité avec mes collègues.",
    "Je peux évoluer dans mon poste.",
    "Mon environnement de travail est sain et sécurisé.",
    "J'ai des pauses suffisantes pendant ma journée.",
    "Je reçois des informations utiles pour bien travailler.",
    "Je participe aux décisions qui concernent mon travail.",
    "Mon travail est compatible avec mes valeurs.",
    "Je ressens de la fierté dans ce que je fais.",
    "Mon travail est stimulant.",
    "Les horaires sont compatibles avec ma vie personnelle.",
    "Mon manager me soutient en cas de difficulté.",
    "Je me sens à l'aise dans mon équipe.",
    "Je me sens utile dans mon organisation.",
]

SCORE_GROUPS = {
    "Sens du Travail": [
        "Mon travail a du sens pour moi.",
        "Mon travail est compatible avec mes valeurs.",
        "Je ressens de la fierté dans ce que je fais.",
        "Mon travail est stimulant.",
        "Je me sens utile dans mon organisation.",
    ],
    "Relations Interpersonnelles": [
        "Je peux exprimer mon point de vue au travail.",
        "Je suis écouté(e) par ma hiérarchie.",
        "J'ai des relations de qualité avec mes collègues.",
        "Mon manager me soutient en cas de difficulté.",
        "Je me sens à l'aise dans mon équipe.",
    ],
    "Santé & Environnement": [
        "Je comprends clairement mes missions.",
        "Je dispose des moyens nécessaires pour faire mon travail.",
        "Mon environnement de travail est sain et sécurisé.",
        "Je reçois des informations utiles pour bien travailler.",
    ],
    "Reconnaissance & Évolution": [
        "Je suis reconnu(e) pour le travail bien fait.",
        "Je peux évoluer dans mon poste.",
        "Je participe aux décisions qui concernent mon travail.",
    ],
    "Équilibre de Vie": [
        "J'ai un bon équilibre entre vie privée et professionnelle.",
        "J'ai des pauses suffisantes pendant ma journée.",
        "Les horaires sont compatibles avec ma vie personnelle.",
    ],
}

SCORE_COLORS = {
    "Sens du Travail":             C["purple"],
    "Relations Interpersonnelles": C["blue"],
    "Santé & Environnement":       C["green"],
    "Reconnaissance & Évolution":  C["orange"],
    "Équilibre de Vie":            "#F59E0B",
}

SOCIO_CANDIDATES = [
    "Departement", "Département", "Direction",
    "Poste de travail", "Fonction",
    "Genre",
    "Categorie_IMC", "Classe_Anciennete", "TrancheAge",
]

# ─────────────────────────────────────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fraunces:ital,opsz,wght@0,9..144,300;1,9..144,400;1,9..144,600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #0F2340; }

.stApp {
    background-color: #F0F7FF;
    background-image:
        radial-gradient(ellipse 1000px 500px at 10% -5%, rgba(56,163,232,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 600px 400px at 90% 105%, rgba(249,115,22,0.08) 0%, transparent 50%);
}
.main .block-container { padding-top: 0.75rem; padding-left: 2rem; padding-right: 2rem; max-width: 1500px; }

/* SIDEBAR */
[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #D0E8F8 !important; }

/* HERO */
.hero-band {
    background: linear-gradient(135deg, #FFFFFF 0%, #F5F9FF 100%);
    border: 1px solid #D0E8F8; border-radius: 20px; padding: 1.4rem 2rem 1.3rem;
    margin-bottom: 0.9rem; position: relative; overflow: hidden;
    box-shadow: 0 4px 24px rgba(56,163,232,0.08), 0 1px 0 rgba(255,255,255,0.9) inset;
}
.hero-band::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #38A3E8, #F97316, #38A3E8);
    background-size: 200% 100%; animation: shimmer 4s linear infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.hero-inner { display: flex; align-items: center; justify-content: space-between; }
.hero-wordmark h1 {
    font-family: 'Fraunces', Georgia, serif; font-size: 2rem; font-weight: 600;
    font-style: italic; color: #0F2340; letter-spacing: -0.02em; margin: 0; line-height: 1;
}
.hero-wordmark h1 span { color: #38A3E8; }
.hero-subtitle { font-size: 0.86rem; color: #4E6A88; letter-spacing: 0.05em; text-transform: uppercase; font-weight: 600; margin-top: 0.4rem; }
.hero-chip {
    display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.65rem;
    font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #F97316;
    background: rgba(249,115,22,0.08); border: 1px solid rgba(249,115,22,0.25);
    border-radius: 999px; padding: 0.3rem 0.8rem;
}
.hero-chip::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #F97316; animation: blink 2s ease-in-out infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* SECTION TITLE */
.section-title {
    display: flex; align-items: center; gap: 0.7rem; font-family: 'Fraunces', serif;
    font-size: 1.2rem; font-style: italic; font-weight: 400; color: #0F2340;
    margin: 1.8rem 0 1rem; padding-bottom: 0.65rem; border-bottom: 2px solid #E4F0FB;
}
.section-title::before {
    content: ''; display: inline-block; width: 4px; height: 20px;
    background: linear-gradient(180deg, #38A3E8 0%, #F97316 100%); border-radius: 2px; flex-shrink: 0;
}

/* KPI CARD */
.kpi-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 16px;
    padding: 1.3rem 1.2rem 1.1rem; text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06); position: relative; overflow: hidden;
}
.kpi-card::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #38A3E8, #F97316); opacity: 0; transition: opacity 0.22s;
}
.kpi-card:hover { transform: translateY(-4px); border-color: #AAD5F5; box-shadow: 0 10px 32px rgba(56,163,232,0.15); }
.kpi-card:hover::after { opacity: 1; }
.kpi-label { font-size: 0.8rem; color: #4E6A88 !important; text-transform: uppercase; letter-spacing: 0.09em; font-weight: 700; margin-bottom: 0.55rem; display: block; }
.kpi-icon { width: 38px; height: 38px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.55rem; }
.kpi-value { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.35rem; font-weight: 800; color: #0F2340 !important; line-height: 1; letter-spacing: -0.04em; }
@keyframes slideUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }

/* GAUGE CARD */
.gauge-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 18px;
    padding: 1.6rem 1.2rem 1.3rem; text-align: center;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 8px rgba(56,163,232,0.06); height: 100%; position: relative; overflow: hidden;
}
.gauge-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #38A3E8, #F97316); opacity: 0; transition: opacity 0.22s; }
.gauge-card:hover { transform: translateY(-4px); border-color: #AAD5F5; box-shadow: 0 12px 36px rgba(56,163,232,0.15); }
.gauge-card:hover::before { opacity: 1; }
.gauge-semi-wrap { position: relative; width: 180px; height: 90px; margin: 0 auto 0.7rem; overflow: hidden; }
.gauge-semi-bg   { position: absolute; width: 180px; height: 180px; border-radius: 50%; background: #EDF5FD; top: 0; left: 0; }
.gauge-semi-fill {
    position: absolute; width: 180px; height: 180px; border-radius: 50%; top: 0; left: 0;
    background: conic-gradient(from 270deg, var(--gauge-color,#38A3E8) 0deg, var(--gauge-color,#38A3E8) calc(var(--g,0deg)), transparent calc(var(--g,0deg)));
}
.gauge-semi-inner { position: absolute; width: 112px; height: 112px; background: #FFFFFF; border-radius: 50%; top: 34px; left: 34px; box-shadow: inset 0 2px 8px rgba(56,163,232,0.06); }
.gauge-value    { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.9rem; font-weight: 800; color: #0F2340; line-height: 1; letter-spacing: -0.04em; }
.gauge-pct      { font-size: 1rem; font-weight: 500; color: #6B88A8; }
.gauge-label    { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.96rem; font-weight: 700; color: #0F2340; margin-top: 0.55rem; }
.gauge-sublabel { font-size: 0.84rem; color: #4E6A88; margin-top: 0.25rem; line-height: 1.5; }
.gauge-badge    { display: inline-block; margin-top: 0.7rem; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; padding: 0.22rem 0.85rem; border-radius: 999px; }
.gauge-badge.good  { background: #DCFCE7; color: #15803D; }
.gauge-badge.alert { background: #FEE2E2; color: #B91C1C; }

/* PROGRESS */
.prog-track { background: #EDF5FD; border-radius: 999px; height: 7px; overflow: hidden; margin-top: 5px; }
.prog-fill  { height: 7px; border-radius: 999px; width: 0%; transition: width 1.1s cubic-bezier(0.4,0,0.2,1); }
.panel-relief { background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 16px; padding: 0.9rem 1rem 0.6rem; box-shadow: 0 3px 14px rgba(56,163,232,0.08); }

/* WORKZONE / LS CARDS */
.workzone-card, .ls-card {
    background: #FFFFFF; border: 1px solid #D6E8F7; border-radius: 14px;
    padding: 1.1rem 1rem; text-align: center; transition: transform 0.2s, box-shadow 0.2s;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
    box-shadow: 0 2px 6px rgba(56,163,232,0.05);
}
.workzone-card:hover, .ls-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(56,163,232,0.12); }

/* TABS */
[data-baseweb="tab-list"] { background: #FFFFFF !important; border-radius: 12px; padding: 4px; gap: 3px; border: 1px solid #D0E8F8; box-shadow: 0 2px 8px rgba(56,163,232,0.07); }
[data-baseweb="tab"] { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.88rem !important; color: #6B88A8 !important; border-radius: 9px !important; padding: 0.5rem 1.4rem !important; transition: all 0.2s !important; }
[aria-selected="true"][data-baseweb="tab"] { background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important; color: #FFFFFF !important; font-weight: 700 !important; box-shadow: 0 3px 12px rgba(56,163,232,0.3) !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none !important; }

/* SELECTS & BUTTONS */
[data-baseweb="select"] > div { background-color: #FFFFFF !important; border-color: #C8DFF2 !important; border-radius: 10px !important; color: #0F2340 !important; }
.stButton > button { background: linear-gradient(135deg, #38A3E8, #2B8FD0) !important; border: none !important; color: #FFFFFF !important; border-radius: 10px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; font-size: 0.8rem !important; letter-spacing: 0.02em !important; box-shadow: 0 3px 10px rgba(56,163,232,0.25) !important; transition: all 0.18s !important; }
.stButton > button:hover { background: linear-gradient(135deg, #F97316, #EA6A0A) !important; box-shadow: 0 4px 16px rgba(249,115,22,0.3) !important; transform: translateY(-1px) !important; }

/* PLOTLY */
div[data-testid="stPlotlyChart"] { border: 1px solid #D6E8F7; border-radius: 12px; background: #FFFFFF; box-shadow: 0 4px 16px rgba(56,163,232,0.06); padding: 4px; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #EDF5FD; }
::-webkit-scrollbar-thumb { background: #AAD5F5; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38A3E8; }

hr { border: none; border-top: 1px solid #E4F0FB; margin: 1rem 0; }
@property --g { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — NORMALISATION COLONNES
# ─────────────────────────────────────────────────────────────────────────────
def normalize(text):
    t = str(text).strip().lower()
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", t)


def find_col(df, target):
    nt = normalize(target)
    for col in df.columns:
        if normalize(col) == nt:
            return col
    return None


def recode_response(series):
    out = pd.Series(pd.NA, index=series.index, dtype="object")
    num = pd.to_numeric(series, errors="coerce")
    out.loc[num == 1] = "Très insatisfait"
    out.loc[num == 2] = "Insatisfait"
    out.loc[num == 3] = "Satisfait"
    out.loc[num == 4] = "Très satisfait"
    text_map = {
        "tresinsatisfait": "Très insatisfait",
        "insatisfait":     "Insatisfait",
        "satisfait":       "Satisfait",
        "tressatisfait":   "Très satisfait",
    }
    normed = series.astype(str).map(normalize)
    for k, v in text_map.items():
        out.loc[normed == k] = v
    return out


def add_derived_columns(df):
    out = df.copy()
    age_col  = find_col(out, "Age")
    anc_col  = find_col(out, "Anciennete")
    poids_col = find_col(out, "Poids")
    taille_col = find_col(out, "Taille")
    imc_col  = find_col(out, "IMC")

    if age_col and "TrancheAge" not in out.columns:
        age = pd.to_numeric(out[age_col], errors="coerce")
        out["TrancheAge"] = pd.cut(
            age, bins=[0, 20, 30, 40, 50, 60, np.inf],
            labels=["<20", "20-30", "31-40", "41-50", "51-60", "60+"], right=False,
        )
    if anc_col and "Classe_Anciennete" not in out.columns:
        anc = pd.to_numeric(out[anc_col], errors="coerce")
        out["Classe_Anciennete"] = pd.cut(
            anc, bins=[0, 2, 5, 10, 20, np.inf],
            labels=["0-2 ans", "3-5 ans", "6-10 ans", "11-20 ans", "21+ ans"],
            include_lowest=True,
        )
    if poids_col and taille_col and "IMC" not in out.columns:
        p = pd.to_numeric(out[poids_col], errors="coerce")
        t = pd.to_numeric(out[taille_col], errors="coerce")
        out["IMC"] = np.round(p / (t / 100) ** 2, 1)
        imc_col = "IMC"
    if imc_col and "Categorie_IMC" not in out.columns:
        imc_vals = pd.to_numeric(out.get(imc_col, pd.Series(dtype=float)), errors="coerce")
        out["Categorie_IMC"] = pd.cut(
            imc_vals, bins=[-np.inf, 18.5, 24.9, 29.9, np.inf],
            labels=["Sous-poids", "Normal", "Surpoids", "Obésité"],
        )
    return out


def resolve_questions(df):
    return {q: find_col(df, q) for q in QUESTIONS if find_col(df, q)}


# ─────────────────────────────────────────────────────────────────────────────
# COMPOSANTS HTML
# ─────────────────────────────────────────────────────────────────────────────
def sec_title(text):
    st.markdown(f'<div class="sec-title">{text}</div>', unsafe_allow_html=True)


def kpi_card(label, value, color=C["blue"], suffix="", decimals=0, sub=""):
    disp = f"{value:.{decimals}f}{suffix}"
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{color};">{disp}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def semi_gauge(pct, color, label, sublabel, key=""):
    """Rendu SVG d'une jauge semi-circulaire."""
    pct = max(0.0, min(100.0, float(pct)))
    angle = pct / 100 * 180
    r, cx, cy = 68, 88, 78
    ex = cx + r * np.cos(np.radians(180 - angle))
    ey = cy - r * np.sin(np.radians(180 - angle))
    arc = f'M {cx-r} {cy} A {r} {r} 0 0 1 {ex:.2f} {ey:.2f}' if angle > 1 else ""
    badge_bg, badge_c, badge_t = (
        ("#DCFCE7", "#15803D", "Élevé")  if pct > 65 else
        ("#FEF3C7", "#B45309", "Moyen")  if pct > 40 else
        ("#FEE2E2", "#B91C1C", "Faible")
    )
    st.markdown(f"""
    <div class="gauge-card">
        <svg width="176" height="96" style="display:block;margin:0 auto;">
            <path d="M {cx-r} {cy} A {r} {r} 0 0 1 {cx+r} {cy}"
                  fill="none" stroke="#EDF5FD" stroke-width="12" stroke-linecap="round"/>
            {'<path d="' + arc + '" fill="none" stroke="' + color + '" stroke-width="12" stroke-linecap="round"/>' if arc else ''}
            <text x="{cx}" y="76" text-anchor="middle" font-size="23" font-weight="800"
                  fill="{color}" font-family="DM Serif Display, serif">{pct:.0f}</text>
            <text x="{cx}" y="92" text-anchor="middle" font-size="10" fill="#6B88A8"
                  font-family="Plus Jakarta Sans">%</text>
        </svg>
        <div style="font-weight:700;font-size:0.82rem;color:{C['text']};line-height:1.35;
                    text-align:center;margin-top:0.15rem;">{label}</div>
        <div style="font-size:0.7rem;color:{C['muted']};text-align:center;
                    margin:0.15rem 0 0.45rem;line-height:1.4;">{sublabel}</div>
        <div style="text-align:center;">
            <span class="badge" style="background:{badge_bg};color:{badge_c};">{badge_t}</span>
        </div>
    </div>""", unsafe_allow_html=True)


def dual_status_bar(neg_pct, pos_pct, neg_color, pos_color):
    """Barre compacte montrant l'équilibre insatisfaits / satisfaits."""
    neg = max(0.0, neg_pct)
    pos = max(0.0, pos_pct)
    if neg + pos == 0:
        return '<div style="height:6px;border-radius:999px;background:#E0E7EF;margin-top:0.4rem;"></div>'
    return f"""
    <div style="display:flex;height:6px;border-radius:999px;overflow:hidden;margin-top:0.4rem;">
        <div style="flex:{neg:.2f};background:{neg_color};"></div>
        <div style="flex:{pos:.2f};background:{pos_color};"></div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# GRAPHIQUES PLOTLY
# ─────────────────────────────────────────────────────────────────────────────
LAYOUT_BASE = dict(
    plot_bgcolor="#FAFCFF",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color=C["text"], size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(showgrid=True, gridcolor="#EDF5FD", zeroline=False,
               showline=True, linecolor=C["border"],
               tickfont=dict(color=C["muted"], size=11)),
    yaxis=dict(showgrid=True, gridcolor="#EDF5FD", zeroline=False,
               showline=False, tickfont=dict(color=C["muted"], size=11)),
)


def apply_layout(fig, title="", height=None):
    upd = dict(**LAYOUT_BASE, title=dict(text=title, font=dict(family="DM Serif Display, serif", size=14, color=C["text"]), x=0.02))
    if height:
        upd["height"] = height
    fig.update_layout(**upd)
    return fig


def radar_chart(score_means: dict) -> go.Figure:
    dims  = list(score_means.keys())
    vals  = list(score_means.values())
    dims_ = dims + [dims[0]]
    vals_ = vals + [vals[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[2.5]*len(dims_), theta=dims_, fill="toself",
        fillcolor="rgba(249,115,22,0.05)",
        line=dict(color="rgba(249,115,22,0.35)", dash="dot", width=1.5),
        name="Référence 2.5", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=vals_, theta=dims_, fill="toself",
        fillcolor="rgba(56,163,232,0.13)",
        line=dict(color=C["blue"], width=2.5),
        marker=dict(color=C["blue"], size=7, line=dict(color="white", width=2)),
        name="Score moyen",
        hovertemplate="<b>%{theta}</b><br>%{r:.2f}/4<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#FAFCFF",
            angularaxis=dict(tickfont=dict(color=C["text"], size=10, family="Plus Jakarta Sans"), linecolor=C["border"], gridcolor="#EDF5FD"),
            radialaxis=dict(visible=True, range=[1, 4], tickfont=dict(color=C["muted"], size=9), gridcolor="#EDF5FD", linecolor=C["border"]),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color=C["text"]),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=C["border"], borderwidth=1, font=dict(size=11)),
        height=380, margin=dict(l=60, r=60, t=40, b=40),
    )
    return fig


def stacked_pct_chart(crosstab: pd.DataFrame, title: str, y_title: str) -> go.Figure:
    fig = go.Figure()
    for label in RESPONSE_ORDER:
        if label not in crosstab.columns:
            continue
        fig.add_trace(go.Bar(
            x=crosstab[label], y=crosstab.index, orientation="h",
            name=label, marker_color=RESPONSE_COLORS[label],
            text=[f"{v:.1f}%" for v in crosstab[label]], textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=11, family="Plus Jakarta Sans"),
        ))
    fig.update_layout(
        barmode="stack",
        title=dict(text=title, font=dict(family="DM Serif Display, serif", size=13, color=C["text"]), x=0.01),
        xaxis=dict(range=[0, 100], title="Pourcentage (%)", ticksuffix="%",
                   showgrid=True, gridcolor="#EDF5FD", zeroline=False,
                   tickfont=dict(color=C["muted"], size=11)),
        yaxis=dict(title=y_title, tickfont=dict(color=C["text"], size=11), showgrid=False),
        legend_title="Réponses",
        plot_bgcolor="#FAFCFF", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color=C["text"], size=11),
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor=C["border"], borderwidth=1),
    )
    return fig


def bar_univarie(series: pd.Series, var_label: str) -> go.Figure:
    counts = series.value_counts().reset_index()
    counts.columns = [var_label, "n"]
    total = counts["n"].sum()
    counts["pct"] = counts["n"] / total * 100
    palette = [C["blue"], C["orange"], C["purple"], C["green"], "#F59E0B",
               "#06B6D4", "#FB923C", "#84CC16"]
    fig = go.Figure()
    for i, row in counts.iterrows():
        fig.add_trace(go.Bar(
            y=[str(row[var_label])], x=[row["pct"]], orientation="h",
            marker_color=palette[i % len(palette)], opacity=0.88,
            text=f"  {row['pct']:.1f}%  (n={row['n']})",
            textposition="outside",
            textfont=dict(color=C["muted"], size=11, family="Plus Jakarta Sans"),
            showlegend=False, name=str(row[var_label]),
        ))
    height = max(260, len(counts) * 52 + 80)
    fig = apply_layout(fig, f"Distribution — {var_label}", height)
    fig.update_xaxes(range=[0, 130], title_text="Pourcentage (%)", ticksuffix="%")
    fig.update_yaxes(title_text=var_label)
    return fig


def bar_bivarie(df_sub: pd.DataFrame, x_col: str, y_col: str, y_label: str) -> go.Figure:
    """Score moyen d'une dimension QVT par catégorie d'une variable socio."""
    groups = df_sub.groupby(x_col)[y_col].agg(["mean", "count"]).reset_index()
    groups.columns = [x_col, "mean", "n"]
    groups = groups.sort_values("mean", ascending=True)

    colors_list = [
        C["green"] if v >= 3 else C["orange"] if v >= 2.5 else C["red"]
        for v in groups["mean"]
    ]
    fig = go.Figure(go.Bar(
        y=groups[x_col].astype(str),
        x=groups["mean"],
        orientation="h",
        marker_color=colors_list,
        opacity=0.88,
        text=[f"{v:.2f}  (n={n})" for v, n in zip(groups["mean"], groups["n"])],
        textposition="outside",
        textfont=dict(color=C["muted"], size=11, family="Plus Jakarta Sans"),
    ))
    height = max(260, len(groups) * 52 + 80)
    fig = apply_layout(fig, f"{y_label} selon {x_col}", height)
    fig.update_xaxes(range=[1, 4.5], title_text="Score moyen (/4)")
    fig.update_yaxes(title_text=x_col)
    # Ligne de référence à 2.5
    fig.add_vline(x=2.5, line_dash="dot", line_color=C["orange"],
                  line_width=1.5, annotation_text="Seuil 2.5",
                  annotation_font=dict(color=C["orange"], size=10))
    return fig


def stacked_bivarie(df_sub: pd.DataFrame, x_col: str, q_col: str, q_label: str) -> go.Figure:
    """Répartition des réponses à une question selon une variable socio."""
    tmp = df_sub.copy()
    tmp["Reponse"] = recode_response(tmp[q_col])
    ct = pd.crosstab(tmp[x_col], tmp["Reponse"], normalize="index") * 100
    ct = ct.reindex(columns=RESPONSE_ORDER, fill_value=0)
    return stacked_pct_chart(ct, f"Réponses à « {q_label[:55]}… » selon {x_col}", x_col)


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DONNÉES
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_excel(file) -> pd.DataFrame:
    return pd.read_excel(file)


def compute_scores(df: pd.DataFrame, question_map: dict) -> pd.DataFrame:
    out = df.copy()
    for score_name, qs in SCORE_GROUPS.items():
        cols = [question_map[q] for q in qs if q in question_map]
        if cols:
            raw = out[cols].apply(pd.to_numeric, errors="coerce")
            out[score_name] = raw.mean(axis=1)
    q_cols = list(question_map.values())
    if q_cols:
        out["Score_Global"] = out[q_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    return out


def question_stats(df: pd.DataFrame, question_map: dict) -> pd.DataFrame:
    rows = []
    n = len(df)
    for q, col in question_map.items():
        recoded = recode_response(df[col])
        counts  = recoded.value_counts()
        total   = counts.sum()
        pct_neg = (counts.get("Très insatisfait", 0) + counts.get("Insatisfait", 0)) / total * 100
        pct_pos = (counts.get("Satisfait", 0)        + counts.get("Très satisfait", 0)) / total * 100
        avg     = pd.to_numeric(df[col], errors="coerce").mean()
        rows.append({"question": q, "col": col, "pct_neg": pct_neg, "pct_pos": pct_pos, "avg": avg, "n_valid": int(total)})
    return pd.DataFrame(rows).sort_values("avg")


# ─────────────────────────────────────────────────────────────────────────────
# APP PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
def main():
    inject_css()

    # ── TOPBAR YODAN ──────────────────────────────────────────────────────────
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    _col_top, _col_back = st.columns([9, 1])
    with _col_top:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:12px;background:white;border-radius:12px;'
            'padding:14px 24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,0.06),'
            '0 4px 12px rgba(30,64,175,0.08);border:1px solid #e8edf5;">'
            '<div style="width:38px;height:38px;background:linear-gradient(135deg,#22c55e,#16a34a);'
            'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
            '<i class="fas fa-heart" style="color:white;font-size:15px;"></i></div>'
            '<div>'
            '<div style="font-size:16px;font-weight:700;color:#1e293b;">QVT — Qualité de Vie au Travail</div>'
            '<div style="font-size:11px;color:#64748b;margin-top:1px;">Analyse de la satisfaction et du bien-être · YODAN Analytics</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
    with _col_back:
        st.write("")
        st.write("")
        if st.button("← Accueil", key="back_home_qvt", use_container_width=True):
            st.switch_page("app.py")

    # ── SIDEBAR IMPORT ────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("📂 Données")
        _qvt_sidebar_up = st.file_uploader(
            "Charger un fichier Excel ou CSV",
            type=["xlsx", "xls", "csv"],
            help="Glissez-déposez ou cliquez pour sélectionner votre fichier QVT.",
            key="qvt_sidebar_uploader",
        )
    if _qvt_sidebar_up is not None:
        _b = _qvt_sidebar_up.read()
        if _b:
            st.session_state["qvt_file_bytes"] = _b
            st.session_state["qvt_file_name"]  = _qvt_sidebar_up.name

    # ── CHARGEMENT ────────────────────────────────────────────────────────────
    if "qvt_file_bytes" in st.session_state:
        _qfn  = st.session_state["qvt_file_name"]
        _qbuf = io.BytesIO(st.session_state["qvt_file_bytes"])
        try:
            if _qfn.lower().endswith((".xlsx", ".xls")):
                uploaded_data = _qbuf
            else:
                uploaded_data = _qbuf
            df_raw = load_excel(uploaded_data)
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement : {e}")
            st.stop()
    else:
        # Fallback : uploader dans la zone principale
        st.info("📂 Chargez votre fichier de données dans la **barre latérale** ou ici pour démarrer l'analyse.")
        uploaded = st.file_uploader(
            "Importer un fichier Excel ou CSV",
            type=["xlsx", "xls", "csv"],
            key="qvt_main_uploader",
        )
        if uploaded is not None:
            _b = uploaded.read()
            if _b:
                st.session_state["qvt_file_bytes"] = _b
                st.session_state["qvt_file_name"]  = uploaded.name
                st.rerun()
        st.stop()
    df_raw = add_derived_columns(df_raw)
    question_map = resolve_questions(df_raw)

    if not question_map:
        st.error("Aucune colonne de question reconnue dans le fichier.")
        st.stop()

    df = compute_scores(df_raw, question_map)

    available_questions = list(question_map.keys())
    score_cols = [s for s in SCORE_GROUPS if s in df.columns]
    socio_cols = [c for c in SOCIO_CANDIDATES if c in df.columns]

    # ── FILTRES ──
    with st.container(border=True):
        f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
        genre_col = find_col(df, "Genre")
        dir_col   = find_col(df, "Direction") or find_col(df, "Departement") or find_col(df, "Département")

        with f1:
            if dir_col:
                opts_dir = ["Tous"] + sorted(df[dir_col].dropna().astype(str).unique().tolist())
                sel_dir  = st.selectbox("Département / Direction", opts_dir, key="fil_dir")
            else:
                sel_dir = "Tous"
                st.selectbox("Département / Direction", ["—"], disabled=True)
        with f2:
            if genre_col:
                opts_genre = ["Tous"] + sorted(df[genre_col].dropna().astype(str).unique().tolist())
                sel_genre  = st.selectbox("Genre", opts_genre, key="fil_genre")
            else:
                sel_genre = "Tous"
                st.selectbox("Genre", ["—"], disabled=True)
        with f3:
            age_col = find_col(df, "Age")
            if age_col:
                ages = pd.to_numeric(df[age_col], errors="coerce").dropna()
                if not ages.empty:
                    age_rng = st.slider("Âge", int(ages.min()), int(ages.max()),
                                        (int(ages.min()), int(ages.max())), key="fil_age")
                else:
                    age_rng = None
            else:
                age_rng = None
                st.slider("Âge", 18, 65, (18, 65), disabled=True)
        with f4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Réinitialiser", use_container_width=True):
                for k in ["fil_dir", "fil_genre", "fil_age"]:
                    st.session_state.pop(k, None)
                st.rerun()

    # Appliquer filtres
    mask = pd.Series(True, index=df.index)
    if dir_col and sel_dir != "Tous":
        mask &= df[dir_col].astype(str) == sel_dir
    if genre_col and sel_genre != "Tous":
        mask &= df[genre_col].astype(str) == sel_genre
    if age_rng and age_col:
        ages_s = pd.to_numeric(df[age_col], errors="coerce")
        mask &= ages_s.between(age_rng[0], age_rng[1])
    df_f = df[mask].copy()
    n = len(df_f)

    if n == 0:
        st.warning("Aucun répondant ne correspond aux filtres sélectionnés.")
        st.stop()

    # Badge effectif filtré
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.5rem;margin:0.3rem 0 0.8rem auto;width:fit-content;">
        <span style="font-size:0.68rem;color:{C['muted']};text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Effectif filtré</span>
        <span class="badge badge-blue" style="font-size:0.8rem;padding:0.2rem 0.7rem;">{n}</span>
    </div>
    """, unsafe_allow_html=True)

    avg_global = df_f["Score_Global"].mean() if "Score_Global" in df_f else 0.0
    q_stats = question_stats(df_f, question_map)
    top_risks     = q_stats.nsmallest(5, "avg")
    top_strengths = q_stats.nlargest(5, "avg")

    score_means = {
        s: df_f[s].mean()
        for s in score_cols
    }

    available_questions = list(question_map.keys())
    score_cols = [s for s in SCORE_GROUPS if s in df.columns]
    socio_cols = [c for c in SOCIO_CANDIDATES if c in df.columns]

    # ═════════════════════════════════════════════════════════════════════════
    # ONGLETS
    # ═════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3 = st.tabs(["Vue d'ensemble", "Analyses détaillées", "Analyse finales"])
    # ─────────────────────────────────────────────────────────────────────────
    # ONGLET 1 — VUE D'ENSEMBLE
    # ─────────────────────────────────────────────────────────────────────────
    with tab1:
        sec_title("Indicateurs clés")
        pct_sat      = (df_f["Score_Global"] >= 3).mean() * 100 if "Score_Global" in df_f else 0
        pct_meaning  = (df_f["Sens du Travail"] >= 3).mean()       * 100 if "Sens du Travail"       in df_f else 0
        pct_balance  = (df_f["Équilibre de Vie"] >= 3).mean()      * 100 if "Équilibre de Vie"       in df_f else 0
        pct_rel      = (df_f["Relations Interpersonnelles"] >= 3).mean() * 100 if "Relations Interpersonnelles" in df_f else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: kpi_card("Répondants", n, C["blue"])
        with c2: kpi_card("Score Global Moyen", avg_global, C["green"] if avg_global >= 3 else C["orange"], "/4", 2)
        with c3: kpi_card("Satisfaction élevée", pct_sat, C["green"], "%", 1, sub=f"{int(n*pct_sat/100)} personnes")
        with c4: kpi_card("Sens du Travail", pct_meaning, C["purple"], "%", 1)
        with c5: kpi_card("Équilibre de Vie", pct_balance, "#F59E0B", "%", 1)

        # Jauges normalisées par dimension
        sec_title("Scores par dimension (normalisé 0–100 %)")
        gauge_cols = st.columns(len(score_cols))
        for i, sc in enumerate(score_cols):
            avg = df_f[sc].mean()
            pct = (avg - 1) / 3 * 100
            color = C["green"] if pct > 65 else C["orange"] if pct > 45 else C["red"]
            with gauge_cols[i]:
                semi_gauge(pct, color, sc, "Score normalisé", key=f"g_{sc}")

        # Radar + Pie genre
        col_radar, col_pie = st.columns([1.4, 1])
        with col_radar:
            sec_title("Profil QVT — Radar des dimensions")
            st.plotly_chart(radar_chart(score_means), use_container_width=True)
        with col_pie:
            if genre_col:
                sec_title("Répartition par genre")
                gcounts = df_f[genre_col].value_counts().reset_index()
                gcounts.columns = ["Genre", "n"]
                fig_pie = px.pie(gcounts, names="Genre", values="n", hole=0.45,
                                  color_discrete_sequence=[C["blue"], C["orange"]])
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20), height=320)
                st.plotly_chart(fig_pie, use_container_width=True)

        # Scores moyens par dimension — barre horizontale
        sec_title("Scores moyens par dimension")
        means_df = pd.DataFrame([{"Dimension": k, "Score": v} for k, v in score_means.items()]).sort_values("Score")
        colors_bar = [
            SCORE_COLORS.get(d, C["blue"]) for d in means_df["Dimension"]
        ]
        fig_bars = go.Figure(go.Bar(
            y=means_df["Dimension"], x=means_df["Score"], orientation="h",
            marker_color=colors_bar, opacity=0.88,
            text=[f"{v:.2f}/4" for v in means_df["Score"]], textposition="outside",
            textfont=dict(color=C["muted"], size=11),
        ))
        fig_bars = apply_layout(fig_bars, height=320)
        fig_bars.update_xaxes(range=[1, 4.5], title_text="Score moyen")
        fig_bars.add_vline(x=2.5, line_dash="dot", line_color=C["orange"], line_width=1.5,
                           annotation_text="Seuil 2.5", annotation_font=dict(color=C["orange"], size=10))
        st.plotly_chart(fig_bars, use_container_width=True)

        # Distribution globale des réponses
        sec_title("Distribution globale des réponses")
        all_reps = []
        for q, col in question_map.items():
            all_reps.append(recode_response(df_f[col]))
        all_reps_s = pd.concat(all_reps)
        dist = all_reps_s.value_counts(normalize=True).reindex(RESPONSE_ORDER) * 100
        fig_dist = go.Figure()
        for label in RESPONSE_ORDER:
            fig_dist.add_trace(go.Bar(
                x=[label], y=[dist.get(label, 0)],
                marker_color=RESPONSE_COLORS[label], opacity=0.88,
                text=[f"{dist.get(label,0):.1f}%"], textposition="outside",
                name=label, showlegend=False,
            ))
        fig_dist = apply_layout(fig_dist, f"Toutes questions confondues · {n * len(question_map):,} réponses totales", height=280)
        fig_dist.update_yaxes(title_text="%", range=[0, 60])
        st.plotly_chart(fig_dist, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    # ONGLET 2 — ANALYSE DÉTAILLÉE
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:

        # ── JAUGES RISQUES / FORCES ──────────────────────────────────────────
        sec_title("Questions les plus critiques & points forts")
        col_risk, col_str = st.columns(2)

        with col_risk:
            st.markdown("""
            <div class="risk-card">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
                    <span class="badge badge-red">RISQUES</span>
                    <span style="font-family:'DM Serif Display',serif;font-style:italic;font-size:1rem;color:#0F2340;">Questions les plus critiques</span>
                </div>
                <p style="font-size:0.74rem;color:#6B88A8;margin:0 0 0.8rem;">
                    % cumulé <strong>Insatisfait + Très insatisfait</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top:0.7rem;'>", unsafe_allow_html=True)
            for _, row in top_risks.iterrows():
                bar = dual_status_bar(row["pct_neg"], row["pct_pos"], C["dark_red"], C["dark_grn"])
                st.markdown(f"""
                <div class="item-row" style="border-left:3px solid {C['red']};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
                        <span style="font-size:0.79rem;color:#3B5878;font-weight:600;line-height:1.4;">{row['question']}</span>
                        <div style="text-align:right;line-height:1.1;">
                            <div style="font-size:0.9rem;font-weight:800;color:{C['dark_red']};">{row['pct_neg']:.1f}% insatisfaits</div>
                            <div style="font-size:0.75rem;color:{C['dark_grn']};margin-top:0.1rem;">{row['pct_pos']:.1f}% satisfaits</div>
                        </div>
                    </div>
                    {bar}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_str:
            st.markdown("""
            <div class="strength-card">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.3rem;">
                    <span class="badge badge-green">FORCES</span>
                    <span style="font-family:'DM Serif Display',serif;font-style:italic;font-size:1rem;color:#0F2340;">Points forts à valoriser</span>
                </div>
                <p style="font-size:0.74rem;color:#6B88A8;margin:0 0 0.8rem;">
                    % cumulé <strong>Satisfait + Très satisfait</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top:0.7rem;'>", unsafe_allow_html=True)
            for _, row in top_strengths.iterrows():
                bar = dual_status_bar(row["pct_neg"], row["pct_pos"], C["dark_red"], C["dark_grn"])
                st.markdown(f"""
                <div class="item-row" style="border-left:3px solid {C['green']};">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:0.5rem;">
                        <span style="font-size:0.79rem;color:#3B5878;font-weight:600;line-height:1.4;">{row['question']}</span>
                        <div style="text-align:right;line-height:1.1;">
                            <div style="font-size:0.9rem;font-weight:800;color:{C['dark_grn']};">{row['pct_pos']:.1f}% satisfaits</div>
                            <div style="font-size:0.75rem;color:{C['dark_red']};margin-top:0.1rem;">{row['pct_neg']:.1f}% insatisfaits</div>
                        </div>
                    </div>
                    {bar}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

                # ── ANALYSES UNIVARIÉES ──────────────────────────────────────────────
        sec_title("Analyse univariée — variables sociodémographiques")

        if not socio_cols:
            st.warning("Aucune variable sociodémographique reconnue dans le fichier.")
        else:
            # Sélecteur de variable
            sel_uni = st.selectbox("Variable à analyser", socio_cols, key="uni_var")

            # Graphique
            st.plotly_chart(
                bar_univarie(df_f[sel_uni].astype(str), sel_uni),
                use_container_width=True
            )

            # Tableau de fréquences
            with st.expander("Tableau de fréquences", expanded=False):
                freq = df_f[sel_uni].astype(str).value_counts(normalize=False).reset_index()
                freq.columns = [sel_uni, "Effectif"]
                freq["Pourcentage (%)"] = (freq["Effectif"] / freq["Effectif"].sum() * 100).round(1)
                st.dataframe(freq, use_container_width=True, hide_index=True)

        # ── ANALYSES BIVARIÉES ───────────────────────────────────────────────
        sec_title("Analyse bivariée — score QVT selon variable sociodémographique")
        if not socio_cols or not score_cols:
            st.warning("Données insuffisantes pour l'analyse bivariée.")
        else:
            b1, b2, b3 = st.columns(3)
            with b1:
                sel_socio = st.selectbox("Variable sociodémographique", socio_cols, key="bi_socio")
            with b2:
                score_options = score_cols + (["Score_Global"] if "Score_Global" in df_f else [])
                sel_score = st.selectbox("Dimension QVT", score_options, key="bi_score")
            with b3:
                bi_type = st.radio("Type de visualisation", ["Scores moyens", "Répartition réponses"], key="bi_type", horizontal=True)

            if bi_type == "Scores moyens":
                st.plotly_chart(bar_bivarie(df_f[[sel_socio, sel_score]].dropna(), sel_socio, sel_score, sel_score), use_container_width=True)
            else:
                # Choisir une question dans le groupe de la dimension sélectionnée
                if sel_score in SCORE_GROUPS:
                    qs_in_group = [q for q in SCORE_GROUPS[sel_score] if q in question_map]
                else:
                    qs_in_group = available_questions
                if qs_in_group:
                    sel_q_bi = st.selectbox("Question", qs_in_group, key="bi_question")
                    st.plotly_chart(
                        stacked_bivarie(df_f, sel_socio, question_map[sel_q_bi], sel_q_bi),
                        use_container_width=True,
                    )

            # Tableau croisé
            with st.expander("Tableau croisé détaillé", expanded=False):
                ct = df_f.groupby(sel_socio)[sel_score].agg(["mean", "count"]).reset_index()
                ct.columns = [sel_socio, "Score moyen", "N"]
                ct["Score moyen"] = ct["Score moyen"].round(2)
                ct = ct.sort_values("Score moyen", ascending=False)
                st.dataframe(ct, use_container_width=True, hide_index=True)

                ####################### Onglet : Analyse finale ########################
        with tab3: 
            st.header("Analyse finale")
            st.write("Résumé global, jauge Score Global")

            # --- Score final normalisé ---
            df["Score_final_normalise"] = (
                df[list(question_map.values())]
                .apply(pd.to_numeric, errors="coerce")
                .apply(lambda x: ((x - 1) / 3) * 100)
                .mean(axis=1)
            )

            # Classification Bon/Mauvais
            df["Categorie_Global"] = np.where(df["Score_final_normalise"] < 50, "Mauvais", "Bon")

            # --- Graphique Score Global ---
            counts_global = df["Categorie_Global"].value_counts()
            fig_global = px.pie(
                names=counts_global.index,
                values=counts_global.values,
                title="Répartition des participants selon le Score final normalisé",
                color=counts_global.index,
                color_discrete_map={"Mauvais": "#8B0000", "Bon": "#006400"}
            )
            fig_global.update_traces(textinfo="percent+label")
            st.plotly_chart(fig_global, use_container_width=True, key="fig_global_tab3")

            
if __name__ == "__main__":
    main()
