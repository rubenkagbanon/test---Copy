# ============================================================
# YODAN ANALYTICS — app.py
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="YODAN Analytics - Dashboard RPS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
    '<style>'
    'html,body,[class*="css"]{font-family:Inter,sans-serif!important}'
    '.main{background:#f1f4f9!important}'
    '.block-container{padding:1.5rem 2rem!important;max-width:1300px!important}'
    '#MainMenu,footer,header{visibility:hidden}'
    '.stButton>button{background:white!important;color:#1e40af!important;'
    'border:1.5px solid #bfdbfe!important;border-radius:10px!important;'
    'font-weight:600!important;font-size:13px!important;height:62px!important;'
    'width:100%!important;transition:all 0.2s!important}'
    '.stButton>button:hover{background:#1e40af!important;color:white!important;'
    'border-color:#1e40af!important;transform:translateY(-2px)!important}'
    '[data-testid="collapsedControl"]{background:#1e40af!important;border-radius:0 8px 8px 0!important}'
    '[data-testid="collapsedControl"] svg{fill:white!important}'
    '</style>',
    unsafe_allow_html=True
)

# ── Données ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    fp = os.path.join(base_path, 'data', 'mbi_donnees_fictives_600_sans_imc.csv')
    if not os.path.exists(fp):
        st.error(f"Fichier introuvable : {fp}")
        return pd.DataFrame()
    df = pd.read_csv(fp)
    if 'imc' not in df.columns:
        df['imc'] = (df['poids'] / ((df['taille']/100)**2)) if 'poids' in df.columns else 22.0
    return df

df = load_data()
if df.empty:
    st.stop()

total   = len(df)
nb_h    = (df['genre'] == 'Homme').sum()
nb_f    = (df['genre'] == 'Femme').sum()
pct_h   = nb_h / total * 100
pct_f   = nb_f / total * 100
age_moy = int(round(df['age'].mean()))

# ════════════════════════════════════════════════════════════
# TOPBAR
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;justify-content:space-between;'
    'background:white;border-radius:12px;padding:16px 24px;margin-bottom:20px;'
    'box-shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 12px rgba(30,64,175,0.08);'
    'border:1px solid #e8edf5;">'
    '<div style="display:flex;align-items:center;gap:14px;">'
    '<div style="width:40px;height:40px;background:linear-gradient(135deg,#1e40af,#3b82f6);'
    'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
    '<i class="fas fa-chart-line" style="color:white;font-size:16px;"></i></div>'
    '<div>'
    '<div style="font-size:18px;font-weight:700;color:#1e293b;">YODAN Analytics</div>'
    '<div style="font-size:12px;color:#64748b;margin-top:1px;">Dashboard Risques Psychosociaux</div>'
    '</div></div>'
    '<div style="text-align:right;line-height:1.9;">'
    '<div style="font-size:12px;color:#94a3b8;"><i class="fas fa-building" style="color:#cbd5e1;"></i>&nbsp;Pahaliah &amp; Fils</div>'
    '<div style="font-size:12px;color:#94a3b8;"><i class="far fa-calendar-alt" style="color:#cbd5e1;"></i>&nbsp;19 F\u00e9vrier 2026</div>'
    '</div></div>',
    unsafe_allow_html=True
)

# ════════════════════════════════════════════════════════════
# VUE D'ENSEMBLE
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin:20px 0 14px;">'
    '<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
    '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">Vue d\'ensemble</span>'
    '</div>',
    unsafe_allow_html=True
)

def kpi_card(icon, icon_color, icon_bg, bar_color, value, unit, sub, label):
    sub_html = f'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">{sub}</div>' if sub else ''
    return (
        f'<div style="background:white;border-radius:12px;padding:18px 16px 14px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.05),0 4px 12px rgba(0,0,0,0.06);'
        f'border:1px solid #e8edf5;border-top:3px solid {bar_color};height:148px;">'
        f'<div style="width:34px;height:34px;background:{icon_bg};border-radius:8px;'
        f'display:flex;align-items:center;justify-content:center;margin-bottom:10px;">'
        f'<i class="{icon}" style="color:{icon_color};font-size:14px;"></i></div>'
        f'<div style="font-size:32px;font-weight:700;color:#1e293b;line-height:1;letter-spacing:-0.5px;">'
        f'{value}<span style="font-size:14px;font-weight:400;color:#64748b;">{unit}</span></div>'
        f'{sub_html}'
        f'<div style="font-size:11px;font-weight:600;color:#64748b;letter-spacing:0.7px;'
        f'text-transform:uppercase;margin-top:8px;">{label}</div>'
        f'</div>'
    )

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card("fas fa-users","#1e40af","#eff6ff","#3b82f6",total,"","","Effectif total"), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card("fas fa-male","#0369a1","#f0f9ff","#38bdf8",f"{pct_h:.1f}","%",f"{nb_h} collaborateurs","Hommes"), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card("fas fa-female","#7c3aed","#f5f3ff","#a78bfa",f"{pct_f:.1f}","%",f"{nb_f} collaboratrices","Femmes"), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card("far fa-calendar-alt","#0f766e","#f0fdfa","#2dd4bf",age_moy," ans","","Âge moyen"), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# JAUGE
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin:28px 0 16px;">'
    '<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
    '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">Indice de performance globale RPS</span>'
    '</div>',
    unsafe_allow_html=True
)

score = 72

if   score >= 75: statut, sc, sc_bg, sc_bd = "EXCELLENT", "#15803d", "#f0fdf4", "#86efac"
elif score >= 50: statut, sc, sc_bg, sc_bd = "BON",       "#1e40af", "#eff6ff", "#bfdbfe"
elif score >= 25: statut, sc, sc_bg, sc_bd = "VIGILANCE", "#d97706", "#fffbeb", "#fde68a"
else:             statut, sc, sc_bg, sc_bd = "CRITIQUE",  "#dc2626", "#fef2f2", "#fca5a5"

msgs = {
    "EXCELLENT": ("fas fa-shield-alt",          "Environnement de travail sain",
                  "Les indicateurs psychosociaux sont au vert. Les pratiques de pr\u00e9vention sont bien ancr\u00e9es. "
                  "Maintenez cette dynamique par des \u00e9valuations r\u00e9guli\u00e8res et continuez \u00e0 impliquer les collaborateurs."),
    "BON":       ("fas fa-chart-line",           "Situation globalement favorable",
                  "Le niveau de risques psychosociaux est ma\u00eetris\u00e9 dans l\u2019ensemble. Quelques axes d\u2019am\u00e9lioration "
                  "restent \u00e0 explorer, notamment sur les dimensions stress et \u00e9puisement professionnel. "
                  "Une attention particuli\u00e8re aux r\u00e9sultats MBI et COPSOQ permettra d\u2019affiner les actions prioritaires."),
    "VIGILANCE": ("fas fa-exclamation-triangle", "Des signaux \u00e0 ne pas n\u00e9gliger",
                  "Plusieurs indicateurs r\u00e9v\u00e8lent une exposition mod\u00e9r\u00e9e aux risques psychosociaux. "
                  "Il est recommand\u00e9 d\u2019engager rapidement une analyse approfondie par dimension et de mettre "
                  "en place un plan d\u2019action cibl\u00e9 avec un suivi mensuel."),
    "CRITIQUE":  ("fas fa-exclamation-circle",   "Situation n\u00e9cessitant une intervention urgente",
                  "Les indicateurs sont en zone critique. Une intervention imm\u00e9diate est n\u00e9cessaire : audit RPS complet, "
                  "entretiens individuels et collectifs, et mise en place d\u2019un comit\u00e9 de suivi d\u00e9di\u00e9."),
}
m_icon, m_title, m_body = msgs[statut]

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score,
    domain={'x':[0,1],'y':[0,1]},
    number={
        'font':{'size':60,'color':sc,'family':'Inter'},
        'valueformat':'.0f',
        'suffix':'<span style="font-size:22px;color:#94a3b8;"> / 100</span>'
    },
    gauge={
        'axis':{
            'range':[0,100],
            'tickvals':[0,25,50,75,100],
            'ticktext':['0','25','50','75','100'],
            'tickfont':{'size':12,'color':'#94a3b8','family':'Inter'},
            'tickwidth':1,'tickcolor':'#e2e8f0'
        },
        'bar':{'color':sc,'thickness':0.04},
        'bgcolor':'white','borderwidth':0,
        'steps':[
            {'range':[0,  25],'color':'#ef4444'},
            {'range':[25, 50],'color':'#fb923c'},
            {'range':[50, 75],'color':'#4ade80'},
            {'range':[75,100],'color':'#16a34a'},
        ],
        'threshold':{'line':{'color':sc,'width':5},'thickness':0.85,'value':score}
    }
))
fig.update_layout(
    height=300,
    margin=dict(l=60,r=60,t=20,b=10),
    paper_bgcolor='white',
    font={'family':'Inter'}
)



col_gauge, col_msg = st.columns([3, 2])

with col_gauge:
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:center;gap:10px;'
        f'padding:10px 20px;background:{sc_bg};border-radius:10px;'
        f'border:1.5px solid {sc_bd};margin-top:-8px;">'
        f'<div style="width:8px;height:8px;border-radius:50%;background:{sc};"></div>'
        f'<span style="font-size:14px;font-weight:700;color:{sc};letter-spacing:1.2px;">{statut}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

with col_msg:
    st.markdown('<div style="height:36px;"></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:#f8fafc;border-radius:12px;padding:20px;'
        f'border:1px solid #e2e8f0;border-left:4px solid {sc};">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
        f'<div style="width:30px;height:30px;background:{sc_bg};border-radius:8px;'
        f'display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
        f'<i class="{m_icon}" style="color:{sc};font-size:13px;"></i></div>'
        f'<span style="font-size:13px;font-weight:700;color:#1e293b;">{m_title}</span>'
        f'</div>'
        f'<p style="margin:0 0 14px;font-size:12.5px;color:#475569;line-height:1.75;">{m_body}</p>'
        f'<div style="padding-top:12px;border-top:1px solid #e2e8f0;">'
        f'<p style="margin:0;font-size:11px;color:#94a3b8;text-align:center;">'
        f'<i class="fas fa-info-circle"></i>&nbsp;'
        f'Indice fictif \u2014 recalcul\u00e9 \u00e0 l\u2019issue de tous les tests<br>'
        f'MBI \u00b7 COPSOQ \u00b7 Karasek \u00b7 WHO \u00b7 PSS-10 \u00b7 QVT \u00b7 Toile SST'
        f'</p></div></div>',
        unsafe_allow_html=True
    )



# ════════════════════════════════════════════════════════════
# 7 BOUTONS TESTS
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;gap:10px;margin:28px 0 14px;">'
    '<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
    '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">Acc\u00e8s aux tests psychosociaux</span>'
    '</div>',
    unsafe_allow_html=True
)

# ── Ligne 1 : 4 icônes + 4 boutons ──
TESTS1 = [
    ("fas fa-fire",            "#dc2626","#fef2f2"),
    ("fas fa-clipboard-check", "#0369a1","#f0f9ff"),
    ("fas fa-briefcase",       "#7c3aed","#f5f3ff"),
    ("fas fa-heartbeat",       "#d97706","#fffbeb"),
]
ic1, ic2, ic3, ic4 = st.columns(4)
for col, (icon, color, bg) in zip([ic1,ic2,ic3,ic4], TESTS1):
    with col:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:5px;">'
            f'<div style="width:40px;height:40px;border-radius:10px;background:{bg};'
            f'display:inline-flex;align-items:center;justify-content:center;">'
            f'<i class="{icon}" style="color:{color};font-size:16px;"></i></div></div>',
            unsafe_allow_html=True
        )

b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("MBI Burnout",   use_container_width=True, key="mbi"):
        st.switch_page("pages/1_MBI_Burnout.py")
with b2:
    if st.button("COPSOQ Stress", use_container_width=True, key="copsoq"):
        st.switch_page("pages/5_Copsoq.py")
with b3:
    if st.button("Karasek",       use_container_width=True, key="karasek"):
        st.switch_page("pages/2_Karasek.py")
with b4:
    if st.button("WHO Sant\u00e9", use_container_width=True, key="who"):
        st.info("🚧 En construction")

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── Ligne 2 : 4 colonnes alignées, col1 vide, col2-3-4 = PSS / QVT / SST ──
# FIX 2 : Toile SST = vrai st.button aligné, même style, "En construction" au clic

TESTS2_icons = [
    ("fas fa-brain",  "#0891b2","#ecfeff"),
    ("fas fa-star",   "#0f766e","#f0fdfa"),
    ("fas fa-spider", "#7c3aed","#f5f3ff"),   # violet comme les autres
]
ic5, ic6, ic7, _ = st.columns(4)
for col, (icon, color, bg) in zip([ic5, ic6, ic7], TESTS2_icons):
    with col:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:5px;">'
            f'<div style="width:40px;height:40px;border-radius:10px;background:{bg};'
            f'display:inline-flex;align-items:center;justify-content:center;">'
            f'<i class="{icon}" style="color:{color};font-size:16px;"></i></div></div>',
            unsafe_allow_html=True
        )

b5, b6, b7, _ = st.columns(4)
with b5:
    if st.button("PSS-10 Stress", use_container_width=True, key="pss10"):
        st.switch_page("pages/4_Charge_Mentale.py")
with b6:
    if st.button("QVT Qualit\u00e9", use_container_width=True, key="qvt"):
        st.info("🚧 En construction")
with b7:
    if st.button("Toile SST", use_container_width=True, key="sst"):
        st.switch_page("pages/3_SST.py")

# ── FOOTER ────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-top:40px;padding:14px 0;border-top:1px solid #e2e8f0;'
    'display:flex;align-items:center;justify-content:space-between;">'
    '<div style="display:flex;align-items:center;gap:10px;">'
    '<div style="width:24px;height:24px;background:linear-gradient(135deg,#1e40af,#3b82f6);'
    'border-radius:6px;display:flex;align-items:center;justify-content:center;">'
    '<i class="fas fa-chart-line" style="color:white;font-size:10px;"></i></div>'
    '<span style="font-size:13px;font-weight:600;color:#374151;">YODAN Analytics</span>'
    '<span style="font-size:12px;color:#cbd5e1;">\u00b7</span>'
    '<span style="font-size:12px;color:#94a3b8;">Dashboard v2.0 Pro \u00b7 2026</span>'
    '</div>'
    '<span style="font-size:11px;color:#cbd5e1;letter-spacing:0.4px;">'
    'MBI \u00b7 COPSOQ \u00b7 Karasek \u00b7 WHO \u00b7 PSS-10 \u00b7 QVT \u00b7 Toile SST'
    '</span></div>',
    unsafe_allow_html=True
)
