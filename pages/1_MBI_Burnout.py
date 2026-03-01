# ============================================================
# YODAN ANALYTICS — 1_MBI_Burnout.py
# ============================================================
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from io import BytesIO

st.set_page_config(
    page_title="MBI Burnout - YODAN Analytics",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
    '<style>'
    'html,body,[class*="css"]{font-family:Inter,sans-serif!important}'
    '.main{background:#f1f4f9!important}'
    '.block-container{padding:1.5rem 2rem!important;max-width:1300px!important}'
    '#MainMenu,footer,header{visibility:hidden}'
    # Tabs
    '.stTabs [data-baseweb="tab-list"]{gap:8px;background:transparent;padding:4px 0 12px 0;border-bottom:none!important}'
    '.stTabs [data-baseweb="tab"]{'
    'height:44px;padding:0 24px;background:#f8fafc!important;border-radius:9px;'
    'border:1.5px solid #e2e8f0!important;color:#475569!important;font-weight:600;font-size:13px;'
    'box-shadow:none;transition:all 0.2s}'
    '.stTabs [data-baseweb="tab"] p{color:#475569!important}'
    '.stTabs [data-baseweb="tab"]:hover{border-color:#3b82f6!important;color:#1e40af!important}'
    '.stTabs [data-baseweb="tab"]:hover p{color:#1e40af!important}'
    '.stTabs [aria-selected="true"]{'
    'background:linear-gradient(135deg,#1e40af,#3b82f6)!important;'
    'color:white!important;border-color:#1e40af!important;'
    'box-shadow:0 3px 10px rgba(30,64,175,0.25)!important}'
    '.stTabs [aria-selected="true"] p{color:white!important}'
    '.stTabs [data-baseweb="tab-highlight"]{display:none!important}'
    '.stTabs [data-baseweb="tab-border"]{display:none!important}'
    # Buttons
    '.stButton>button{background:white!important;color:#1e40af!important;'
    'border:1.5px solid #bfdbfe!important;border-radius:10px!important;'
    'font-weight:600!important;font-size:13px!important;height:42px!important;'
    'transition:all 0.2s!important}'
    '.stButton>button:hover{background:#1e40af!important;color:white!important;'
    'border-color:#1e40af!important}'
    # Download button
    '.stDownloadButton>button{background:white!important;color:#1e40af!important;'
    'border:1.5px solid #bfdbfe!important;border-radius:10px!important;'
    'font-weight:600!important;font-size:13px!important;'
    'transition:all 0.2s!important}'
    '.stDownloadButton>button:hover{background:#1e40af!important;color:white!important}'
    # Select
    'div[data-baseweb="select"]>div{background:white!important;'
    'border:1.5px solid #cbd5e1!important;border-radius:9px!important;color:#1e293b!important}'
    'div[data-baseweb="select"] span{color:#1e293b!important}'
    'div[data-baseweb="select"] input{color:#1e293b!important}'
    'div[data-baseweb="select"] *{color:#1e293b!important}'
    # Label du selectbox
    '.stSelectbox label{color:#1e293b!important;font-weight:600!important;font-size:13px!important}'
    '.stSelectbox p{color:#1e293b!important}'
    # Valeur affichée dans le champ
    '[data-baseweb="select"] [data-testid="stMarkdownContainer"] p{color:#1e293b!important}'
    'div[data-baseweb="select"] div{color:#1e293b!important}'
    'ul[role="listbox"]{background:white!important;border:1px solid #e2e8f0!important;'
    'border-radius:10px!important;box-shadow:0 8px 24px rgba(0,0,0,0.11)!important}'
    'li[role="option"]{background:white!important;color:#1e293b!important;font-size:13px!important}'
    'li[role="option"] *{color:#1e293b!important}'
    'li[role="option"]:hover{background:#eff6ff!important;color:#1e40af!important}'
    'li[role="option"]:hover *{color:#1e40af!important}'
    'li[role="option"][aria-selected="true"]{background:#1e40af!important;color:white!important}'
    'li[role="option"][aria-selected="true"] *{color:white!important}'
    '[data-testid="collapsedControl"]{background:#1e40af!important;border-radius:0 8px 8px 0!important}'
    '[data-testid="collapsedControl"] svg{fill:white!important}'
    '</style>',
    unsafe_allow_html=True
)

# ── Chargement données ────────────────────────────────────────
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.dirname(__file__))
    fp = os.path.join(base_path, 'data', 'mbi_donnees_fictives_600_sans_imc.csv')
    if not os.path.exists(fp):
        fp = 'mbi_donnees_fictives_600_sans_imc.csv'
    if not os.path.exists(fp):
        return pd.DataFrame()
    df = pd.read_csv(fp)

    # Scores MBI
    q_ee = ['mbi_q1','mbi_q2','mbi_q3','mbi_q6','mbi_q8','mbi_q13','mbi_q14','mbi_q16','mbi_q20']
    q_dp = ['mbi_q5','mbi_q10','mbi_q11','mbi_q15','mbi_q22']
    q_pa = ['mbi_q4','mbi_q7','mbi_q9','mbi_q12','mbi_q17','mbi_q18','mbi_q19','mbi_q21']
    df['ee_score'] = df[q_ee].sum(axis=1)
    df['dp_score'] = df[q_dp].sum(axis=1)
    df['pa_score'] = df[q_pa].sum(axis=1)

    def cat_ee(s): return 'Faible' if s<=16 else ('Modéré' if s<=26 else 'Élevé')
    def cat_dp(s): return 'Faible' if s<=6  else ('Modéré' if s<=12 else 'Élevé')
    def cat_pa(s): return 'Élevé'  if s>=39 else ('Modéré' if s>=32 else 'Faible')
    df['ee_categorie'] = df['ee_score'].apply(cat_ee)
    df['dp_categorie'] = df['dp_score'].apply(cat_dp)
    df['pa_categorie'] = df['pa_score'].apply(cat_pa)

    def cls_burnout(r):
        ee, dp, pa = r['ee_categorie'], r['dp_categorie'], r['pa_categorie']
        if ee=='Faible' and dp=='Faible' and pa=='Élevé': return 'Pas de burnout'
        if (ee=='Élevé' and dp=='Élevé') or (ee=='Élevé' and pa=='Faible'): return 'Burnout avéré'
        return 'Pré-burnout'
    df['niveau_burnout'] = df.apply(cls_burnout, axis=1)

    # Tranches
    if 'age' in df.columns:
        df['tranche_age'] = pd.Categorical(
            pd.cut(df['age'], bins=[16,31,41,51,71],
                   labels=['16-30 ans','31-40 ans','41-50 ans','51-70 ans'], right=False),
            categories=['16-30 ans','31-40 ans','41-50 ans','51-70 ans'], ordered=True)
    if 'anciennete' in df.columns:
        df['tranche_anciennete'] = pd.Categorical(
            pd.cut(df['anciennete'], bins=[0,3,6,11,100],
                   labels=['0-2 ans','3-5 ans','6-10 ans','11 ans et plus'], right=False),
            categories=['0-2 ans','3-5 ans','6-10 ans','11 ans et plus'], ordered=True)
    if 'poids' in df.columns and 'taille' in df.columns:
        df['imc'] = (df['poids'] / ((df['taille']/100)**2)).round(1)
        def cat_imc(v):
            if v<18.5: return 'Maigreur'
            if v<25:   return 'Normal'
            if v<30:   return 'Surpoids'
            return 'Obésité'
        df['imc_categorie'] = df['imc'].apply(cat_imc)
    return df

df = load_data()
if df.empty:
    st.error("❌ Fichier de données introuvable.")
    st.stop()

total_analyses = len(df)
nb_f   = (df['genre']=='Femme').sum()
nb_h   = (df['genre']=='Homme').sum()
pct_f  = nb_f / total_analyses * 100
pct_h  = nb_h / total_analyses * 100
age_moy = int(round(df['age'].mean()))

bc = df['niveau_burnout'].value_counts()
nb_pas   = bc.get('Pas de burnout', 0);  pct_pas   = nb_pas   / total_analyses * 100
nb_pre   = bc.get('Pré-burnout',    0);  pct_pre   = nb_pre   / total_analyses * 100
nb_avere = bc.get('Burnout avéré',  0);  pct_avere = nb_avere / total_analyses * 100

# total_entreprise : dans la vraie app ce sera une donnée saisie ; fictif = 600
total_entreprise = st.session_state.get('total_entreprise', total_analyses)
pct_analyses = total_analyses / total_entreprise * 100

# ════════════════════════════════════════════════════════════
# TOPBAR
# ════════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;align-items:center;justify-content:space-between;'
    'background:white;border-radius:12px;padding:14px 24px;margin-bottom:20px;'
    'box-shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 12px rgba(30,64,175,0.08);'
    'border:1px solid #e8edf5;">'
    '<div style="display:flex;align-items:center;gap:14px;flex:1;justify-content:center;">'
    '<div style="width:48px;height:48px;background:linear-gradient(135deg,#dc2626,#ef4444);'
    'border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">'
    '<i class="fas fa-fire" style="color:white;font-size:20px;"></i></div>'
    '<div style="text-align:center;">'
    '<div style="font-size:26px;font-weight:700;color:#1e293b;letter-spacing:-0.5px;">MBI — Maslach Burnout Inventory</div>'
    '<div style="font-size:15px;font-weight:600;color:#334866;margin-top:5px;letter-spacing:0.2px;">Analyse du burnout professionnel · Pahaliah &amp; Fils</div>'
    '</div></div>'
    '<a href="/" target="_self" style="text-decoration:none;">'
    '<div style="display:flex;align-items:center;gap:8px;padding:7px 14px;'
    'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;">'
    '<i class="fas fa-arrow-left" style="color:#64748b;font-size:12px;"></i>'
    '<span style="font-size:12px;font-weight:600;color:#64748b;">Accueil</span>'
    '</div></a>'
    '</div>',
    unsafe_allow_html=True
)

# ── Helper section header ─────────────────────────────────────
def sec(label):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin:22px 0 14px;">'
        f'<div style="width:4px;height:20px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
        f'<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.3px;text-transform:uppercase;">{label}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── Helper KPI card ───────────────────────────────────────────
def kpi(icon, icon_color, icon_bg, bar_color, value, unit, sub, label):
    sub_html = f'<div style="font-size:11px;color:#94a3b8;margin-top:2px;">{sub}</div>' if sub else ''
    return (
        f'<div style="background:white;border-radius:12px;padding:16px 14px 12px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.05),0 4px 12px rgba(0,0,0,0.06);'
        f'border:1px solid #e8edf5;border-top:3px solid {bar_color};height:140px;">'
        f'<div style="width:32px;height:32px;background:{icon_bg};border-radius:8px;'
        f'display:flex;align-items:center;justify-content:center;margin-bottom:8px;">'
        f'<i class="{icon}" style="color:{icon_color};font-size:13px;"></i></div>'
        f'<div style="font-size:28px;font-weight:700;color:#1e293b;line-height:1;letter-spacing:-0.5px;">'
        f'{value}<span style="font-size:13px;font-weight:400;color:#64748b;">{unit}</span></div>'
        f'{sub_html}'
        f'<div style="font-size:10px;font-weight:600;color:#64748b;letter-spacing:0.7px;'
        f'text-transform:uppercase;margin-top:6px;">{label}</div>'
        f'</div>'
    )

# ════════════════════════════════════════════════════════════
# 2 ONGLETS PRINCIPAUX
# ════════════════════════════════════════════════════════════
onglet1, onglet2 = st.tabs([
    "  Informations générales",
    "  Résultats MBI Burnout"
])

# ╔══════════════════════════════════════════════════════════╗
# ║  ONGLET 1 — INFORMATIONS GÉNÉRALES                      ║
# ╚══════════════════════════════════════════════════════════╝
with onglet1:

    # ── 3 KPI — Population + genre majoritaire + Âge moyen ───
    sec("Vue d'ensemble de la population analysée")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi("fas fa-users","#1e40af","#eff6ff","#3b82f6",
            f"{pct_analyses:.1f}","%",f"{total_analyses} collaborateurs analysés","Population analysée"),
            unsafe_allow_html=True)
    with c2:
        if nb_f > nb_h:
            st.markdown(kpi("fas fa-female","#7c3aed","#f5f3ff","#a78bfa",
                f"{pct_f:.1f}","%",f"{nb_f} collaboratrices","Femmes"), unsafe_allow_html=True)
        else:
            st.markdown(kpi("fas fa-male","#0369a1","#f0f9ff","#38bdf8",
                f"{pct_h:.1f}","%",f"{nb_h} collaborateurs","Hommes"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("far fa-calendar-alt","#0f766e","#f0fdfa","#2dd4bf",
            age_moy," ans","","Âge moyen"), unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Facteurs de risque santé — style ancien app ────────
    sec("Facteurs de risque santé")

    # Calcul des effectifs (logique identique à l'ancien app)
    def get_risque_n(col, val_risque):
        if col not in df.columns: return 0
        s = df[col]
        # Binaire 0/1
        if s.dtype in [int, float, np.int64, np.float64]:
            return int((s == val_risque).sum())
        # Texte Oui/Non
        return int((s.astype(str).str.strip().str.lower() == str(val_risque).lower()).sum())

    RISQUES_DATA = []
    if 'imc_categorie' in df.columns or ('poids' in df.columns and 'taille' in df.columns):
        if 'imc' not in df.columns:
            df['imc'] = df['poids'] / ((df['taille']/100)**2)
        n = int((df['imc'] >= 25).sum())
        RISQUES_DATA.append(('<i class="fas fa-weight"></i>', "Obésité/Surpoids", n))
    if 'pratique_sport' in df.columns:
        s = df['pratique_sport']
        n = int((s.astype(str).str.lower().isin(['non','0','false'])).sum())
        RISQUES_DATA.append(('<i class="fas fa-couch"></i>', "Sédentarité (pas sport)", n))
    if 'consommation_alcool' in df.columns:
        s = df['consommation_alcool']
        n = int((s.astype(str).str.lower().isin(['oui','1','true'])).sum())
        RISQUES_DATA.append(('<i class="fas fa-wine-glass"></i>', "Consommation alcool", n))
    if 'tabagisme' in df.columns:
        s = df['tabagisme']
        n = int((s.astype(str).str.lower().isin(['oui','1','true'])).sum())
        RISQUES_DATA.append(('<i class="fas fa-smoking"></i>', "Consommation tabac", n))
    if 'maladie_chronique' in df.columns:
        s = df['maladie_chronique']
        n = int((s.astype(str).str.lower().isin(['oui','1','true'])).sum())
        RISQUES_DATA.append(('<i class="fas fa-notes-medical"></i>', "Maladie chronique", n))

    col_risk, _ = st.columns([1.1, 1])
    with col_risk:
        for icon, nom, n_risk in RISQUES_DATA:
            pct_r = n_risk / total_analyses * 100
            # Carte blanche identique ancien app
            st.markdown(
                f'<div style="background:white;padding:12px 15px;border-radius:8px;'
                f'margin-bottom:6px;box-shadow:0 2px 5px rgba(0,0,0,0.08);">'
                f'<div style="color:#1e293b;font-weight:600;font-size:14px;">'
                f'{icon}&nbsp; {nom} : '
                f'<span style="color:#ef4444;">{pct_r:.1f}%</span>'
                f' ({n_risk} pers.)</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            # Barre HTML : rouge = à risque, vert = sain
            st.markdown(
                f'<div style="height:8px;border-radius:4px;background:#16a34a;margin:-2px 0 12px 0;">'
                f'<div style="height:8px;border-radius:4px;background:#ef4444;'
                f'width:{min(pct_r,100):.1f}%;"></div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Analyses univariées — logique exacte ancien app ────
    sec("Analyses univariées")

    BINARY_VARS_UNI = ['pratique_sport','consommation_alcool','tabagisme',
                       'maladie_chronique','handicap_physique','suivi_psychologique']

    VAR_OPTIONS = {
        "Sélectionner une variable": None,
        "Genre":                    "genre",
        "Tranche d'âge":            "tranche_age",
        "Ancienneté":               "tranche_anciennete",
        "Situation matrimoniale":   "situation_matrimoniale",
        "Pratique de sport":        "pratique_sport",
        "Consommation alcool":      "consommation_alcool",
        "Tabagisme":                "tabagisme",
        "Catégorie IMC":            "imc_categorie",
        "Maladie chronique":        "maladie_chronique",
        "Handicap physique":        "handicap_physique",
        "Suivi psychologique":      "suivi_psychologique",
    }
    sel_label = st.selectbox("Choisir une variable à visualiser :", list(VAR_OPTIONS.keys()), key="uni_tab1")
    sel_col   = VAR_OPTIONS[sel_label]

    if sel_col and sel_col in df.columns:
        from matplotlib.patches import Patch
        counts_u = df[sel_col].value_counts()
        total_u  = counts_u.sum()
        pcts_u   = (counts_u / total_u * 100).round(1)

        # ── Genre : pie rose/bleu — label uniquement sur segment majoritaire ──
        if sel_col == 'genre':
            fig, ax = plt.subplots(figsize=(3.8, 3.2))
            fig.patch.set_facecolor('#f1f4f9'); ax.set_facecolor('#f1f4f9')
            color_map = {'Femme':'#a78bfa','femme':'#a78bfa','F':'#a78bfa',
                         'Homme':'#38bdf8','homme':'#38bdf8','H':'#38bdf8'}
            colors_g = [color_map.get(str(k),'#1e40af') for k in pcts_u.index]
            dominant_g = pcts_u.idxmax()
            colors_g2 = [color_map.get(str(k),'#1e40af') if k == dominant_g else '#f1f4f9' for k in pcts_u.index]
            wedges, _ = ax.pie(pcts_u.values, labels=None, colors=colors_g2,
                               startangle=90, wedgeprops=dict(edgecolor='white', linewidth=2))
            for wedge, (k, v) in zip(wedges, pcts_u.items()):
                if k == dominant_g:
                    angle = (wedge.theta1 + wedge.theta2) / 2
                    x = 0.55 * np.cos(np.radians(angle))
                    y = 0.55 * np.sin(np.radians(angle))
                    ax.text(x, y, f"{k}\n{v:.1f}%\n({counts_u[k]})",
                            ha='center', va='center', color='white',
                            fontsize=8, fontweight='bold', linespacing=1.3)
            ax.set_title(f"Répartition des Employés\nde l'Entreprise Pahaliah & Fils\nselon : {sel_label}",
                         fontsize=11, fontweight='bold', color='#1e293b', pad=10)
            plt.tight_layout()
            _, cc, _ = st.columns([1,1,1])
            with cc: st.pyplot(fig, use_container_width=False)

        # ── Variables binaires : pie dominant en bleu YODAN + gris ──
        elif sel_col in BINARY_VARS_UNI:
            fig, ax = plt.subplots(figsize=(3.8, 3.0))
            fig.patch.set_facecolor('#f1f4f9'); ax.set_facecolor('#f1f4f9')
            dominant = pcts_u.idxmax()
            sizes, colors_b, explode = [], [], []
            for k, v in pcts_u.items():
                sizes.append(v)
                colors_b.append('#1e40af' if k == dominant else '#e2e8f0')
                explode.append(0.03 if k == dominant else 0)
            wedges, _ = ax.pie(sizes, labels=None, colors=colors_b, explode=explode,
                               startangle=90, wedgeprops=dict(edgecolor='white', linewidth=2))
            for wedge, (k, v) in zip(wedges, pcts_u.items()):
                if k == dominant:
                    angle = (wedge.theta1 + wedge.theta2) / 2
                    x = 0.55 * np.cos(np.radians(angle))
                    y = 0.55 * np.sin(np.radians(angle))
                    ax.text(x, y, f"{k}\n{v:.1f}%\n({counts_u[k]})",
                            ha='center', va='center', color='white',
                            fontsize=8, fontweight='bold', linespacing=1.3)
            minority = [k for k in pcts_u.index if k != dominant][0]
            legend_el = [Patch(facecolor='#1e40af', edgecolor='white', label=f"{dominant}"),
                         Patch(facecolor='#e2e8f0', edgecolor='#ccc',  label=f"{minority}")]
            ax.legend(handles=legend_el, loc='lower center',
                      bbox_to_anchor=(0.5,-0.12), ncol=2, fontsize=8, frameon=False)
            ax.set_title(f"Répartition des Employés\nde l'Entreprise Pahaliah & Fils\nselon : {sel_label}",
                         fontsize=11, fontweight='bold', color='#1e293b', pad=10)
            plt.tight_layout()
            _, cc, _ = st.columns([1,1,1])
            with cc: st.pyplot(fig, use_container_width=False)

        # ── Bar chart vertical (âge, ancienneté, IMC, matrimoniale…) ──
        else:
            if sel_col == 'tranche_age':
                order = ['16-30 ans','31-40 ans','41-50 ans','51-70 ans']
                counts_u = counts_u.reindex([o for o in order if o in counts_u.index])
                pcts_u   = (counts_u / total_u * 100).round(1)
            elif sel_col == 'tranche_anciennete':
                order = ['0-2 ans','3-5 ans','6-10 ans','11 ans et plus']
                counts_u = counts_u.reindex([o for o in order if o in counts_u.index]).dropna()
                pcts_u   = (counts_u / total_u * 100).round(1)

            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor('#f1f4f9'); ax.set_facecolor('#f1f4f9')
            n_bars = len(counts_u)
            cmap   = plt.cm.get_cmap('tab10', n_bars)
            colors_bar = [cmap(i) for i in range(n_bars)]
            bars = ax.bar(range(n_bars), pcts_u.values, color=colors_bar,
                          edgecolor='white', linewidth=2.5, alpha=0.9, width=0.6)
            max_v = pcts_u.max()
            for bar, lbl, pv, cv in zip(bars, counts_u.index, pcts_u.values, counts_u.values):
                h    = bar.get_height()
                text = f"{pv:.1f}%\n({int(cv)})"
                if h > max_v * 0.15:
                    ax.text(bar.get_x()+bar.get_width()/2, h/2, text,
                            ha='center', va='center', color='white',
                            fontsize=11, fontweight='bold', linespacing=1.2)
                else:
                    ax.text(bar.get_x()+bar.get_width()/2, h + max_v*0.02, text,
                            ha='center', va='bottom', color='#1e293b',
                            fontsize=11, fontweight='bold', linespacing=1.2)
            ax.set_xticks(range(n_bars))
            ax.set_xticklabels(counts_u.index.astype(str), fontsize=12,
                               rotation=0 if n_bars<=3 else 30,
                               ha='right' if n_bars>3 else 'center')
            ax.set_ylabel('Pourcentage (%)', fontsize=14, fontweight='bold', color='#1e293b')
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#cbd5e1'); ax.spines['bottom'].set_color('#cbd5e1')
            ax.set_ylim(0, max_v * 1.25)
            ax.set_title(f"Répartition des Employés\nde l'Entreprise Pahaliah & Fils\nselon : {sel_label}",
                         fontsize=14, fontweight='bold', color='#1e293b', pad=16)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=200, bbox_inches='tight', facecolor='#f1f4f9')
        buf.seek(0)
        st.download_button(
            label="⬇  Télécharger le graphique (PNG)",
            data=buf,
            file_name=f"univarie_{sel_col}.png",
            mime="image/png",
            key="dl_uni"
        )
        plt.close()
    elif sel_col:
        st.warning(f"⚠️ La colonne '{sel_col}' n'existe pas dans les données.")


# ╔══════════════════════════════════════════════════════════╗
# ║  ONGLET 2 — RÉSULTATS MBI                               ║
# ╚══════════════════════════════════════════════════════════╝
with onglet2:

    # ── 3 KPI burnout — sobres, blancs avec accents colorés ──
    sec("Résultats de l'évaluation MBI")

    r1, r2, r3 = st.columns(3)
    kpi_card_s = ("background:white;border-radius:12px;padding:22px 16px;"
                  "box-shadow:0 1px 3px rgba(0,0,0,0.06),0 4px 12px rgba(0,0,0,0.07);"
                  "border:1px solid #e8edf5;height:150px;"
                  "display:flex;flex-direction:column;justify-content:center;align-items:center;gap:5px;text-align:center;")
    with r1:
        st.markdown(
            f'<div style="{kpi_card_s}border-top:4px solid #16a34a;">'
            f'<div style="width:36px;height:36px;background:#f0fdf4;border-radius:9px;'
            f'display:flex;align-items:center;justify-content:center;margin-bottom:2px;">'
            f'<i class="fas fa-smile" style="color:#16a34a;font-size:16px;"></i></div>'
            f'<div style="font-size:36px;font-weight:700;color:#16a34a;line-height:1;">{pct_pas:.1f}'
            f'<span style="font-size:14px;font-weight:400;color:#94a3b8;">%</span></div>'
            f'<div style="font-size:11px;color:#94a3b8;">({nb_pas} pers.)</div>'
            f'<div style="font-size:11px;font-weight:700;color:#475569;letter-spacing:0.6px;text-transform:uppercase;">Pas de burnout</div>'
            f'</div>', unsafe_allow_html=True)
    with r2:
        st.markdown(
            f'<div style="{kpi_card_s}border-top:4px solid #d97706;">'
            f'<div style="width:36px;height:36px;background:#fffbeb;border-radius:9px;'
            f'display:flex;align-items:center;justify-content:center;margin-bottom:2px;">'
            f'<i class="fas fa-meh" style="color:#d97706;font-size:16px;"></i></div>'
            f'<div style="font-size:36px;font-weight:700;color:#d97706;line-height:1;">{pct_pre:.1f}'
            f'<span style="font-size:14px;font-weight:400;color:#94a3b8;">%</span></div>'
            f'<div style="font-size:11px;color:#94a3b8;">({nb_pre} pers.)</div>'
            f'<div style="font-size:11px;font-weight:700;color:#475569;letter-spacing:0.6px;text-transform:uppercase;">Pré-burnout</div>'
            f'</div>', unsafe_allow_html=True)
    with r3:
        st.markdown(
            f'<div style="{kpi_card_s}border-top:4px solid #dc2626;">'
            f'<div style="width:36px;height:36px;background:#fef2f2;border-radius:9px;'
            f'display:flex;align-items:center;justify-content:center;margin-bottom:2px;">'
            f'<i class="fas fa-frown" style="color:#dc2626;font-size:16px;"></i></div>'
            f'<div style="font-size:36px;font-weight:700;color:#dc2626;line-height:1;">{pct_avere:.1f}'
            f'<span style="font-size:14px;font-weight:400;color:#94a3b8;">%</span></div>'
            f'<div style="font-size:11px;color:#94a3b8;">({nb_avere} pers.)</div>'
            f'<div style="font-size:11px;font-weight:700;color:#475569;letter-spacing:0.6px;text-transform:uppercase;">Burnout avéré</div>'
            f'</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)


    score_brut    = (0.5 * pct_avere) + (0.3 * pct_pre) + (0.2 * pct_pas)
    score_risque  = round(100 - score_brut, 1)
    if   score_risque < 26: j_statut, j_couleur, j_icone, j_msg = "Sain",      "#16a34a", '<i class="fas fa-check-circle"></i>', f"L'entreprise Pahaliah &amp; Fils se situe en zone saine. L'exposition des employés au burnout est faible et la santé psychosociale des employés est globalement préservée."
    elif score_risque < 75: j_statut, j_couleur, j_icone, j_msg = "Vigilance", "#d97706", '<i class="fas fa-exclamation-triangle"></i>', f"L'entreprise Pahaliah &amp; Fils se situe en zone de vigilance. L'exposition des employés au burnout est significative et nécessite un suivi actif."
    else:                   j_statut, j_couleur, j_icone, j_msg = "Critique",  "#dc2626", '<i class="fas fa-radiation-alt"></i>', f"L'entreprise Pahaliah &amp; Fils se situe en zone critique. L'exposition des employés au burnout est élevée et requiert des actions immédiates pour protéger la santé des employés."

    col_j, col_dim = st.columns([1, 1])

    with col_j:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;margin:0 0 14px;">'
            '<div style="width:4px;height:18px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
            '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;">Score global d\'exposition</span>'
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="background:white;padding:24px 20px;border-radius:12px;'
            f'box-shadow:0 2px 8px rgba(0,0,0,0.08);border:1px solid #e8edf5;">'
            # Labels SAIN / CRITIQUE
            f'<div style="display:flex;justify-content:space-between;font-size:12px;'
            f'font-weight:700;margin-bottom:10px;">'
            f'<span style="color:#16a34a;">SAIN</span>'
            f'<span style="color:#dc2626;">CRITIQUE</span></div>'
            # Barre dégradée + curseur
            f'<div style="position:relative;height:40px;width:100%;margin-bottom:5px;">'
            f'<div style="position:absolute;top:10px;left:0;width:100%;height:20px;'
            f'background:linear-gradient(90deg,#16a34a 0%,#16a34a 30%,#d97706 30%,'
            f'#d97706 50%,#f97316 50%,#f97316 70%,#dc2626 70%,#dc2626 100%);'
            f'border-radius:10px;z-index:1;"></div>'
            f'<div style="position:absolute;left:{min(score_risque,99)}%;top:0;width:6px;height:40px;'
            f'background:#1e293b;border:1px solid white;border-radius:3px;'
            f'transform:translateX(-50%);z-index:10;'
            f'box-shadow:0 0 5px rgba(0,0,0,0.3);"></div></div>'
            # Ticks
            f'<div style="display:flex;justify-content:space-between;font-size:10px;'
            f'color:#94a3b8;margin-bottom:20px;">'
            f'<span>0</span><span>25</span><span>50</span><span>75</span><span>100</span></div>'
            # Score centré
            f'<div style="text-align:center;margin:12px 0;">'
            f'<div style="font-size:52px;font-weight:700;color:{j_couleur};">'
            f'{score_risque}<span style="font-size:22px;color:#94a3b8;">/100</span></div></div>'
            # Badge statut
            f'<div style="text-align:center;padding:8px;background:{j_couleur}20;'
            f'border-radius:8px;border-left:2px solid {j_couleur};margin-bottom:12px;">'
            f'<span style="font-size:16px;font-weight:700;color:{j_couleur};">{j_statut}</span></div>'
            # Message
            f'<div style="padding:10px 12px;background:#f8fafc;border-radius:8px;'
            f'border-left:4px solid {j_couleur};font-size:11px;color:#1e293b;line-height:1.5;">'
            f'<b>{j_icone} {j_statut.upper()} :</b> {j_msg}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with col_dim:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;margin:0 0 14px;">'
            '<div style="width:4px;height:18px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
            '<span style="font-size:11px;font-weight:700;color:#64748b;letter-spacing:1.2px;text-transform:uppercase;">Détails par dimension</span>'
            '</div>',
            unsafe_allow_html=True
        )

        # ── Classifications correctes ──────────────────────────
        def cat_ee_new(s):
            return 'Faible' if s <= 16 else ('Modéré' if s <= 26 else 'Élevé')
        def cat_dp_new(s):
            return 'Faible' if s <= 6  else ('Modéré' if s <= 12 else 'Élevé')
        def cat_pa_new(s):
            return 'Faible' if s <= 31 else ('Modéré' if s <= 38 else 'Élevé')

        df['ee_cat2'] = df['ee_score'].apply(cat_ee_new)
        df['dp_cat2'] = df['dp_score'].apply(cat_dp_new)
        df['pa_cat2'] = df['pa_score'].apply(cat_pa_new)

        def get_props(col):
            vc = df[col].value_counts()
            n  = len(df)
            f  = vc.get('Faible', 0);  pf = f / n * 100
            m  = vc.get('Modéré', 0);  pm = m / n * 100
            e  = vc.get('Élevé',  0);  pe = e / n * 100
            return (int(f), round(pf,1)), (int(m), round(pm,1)), (int(e), round(pe,1))

        ee_f, ee_m2, ee_e = get_props('ee_cat2')
        dp_f, dp_m2, dp_e = get_props('dp_cat2')
        pa_f, pa_m2, pa_e = get_props('pa_cat2')

        ee_moy = df['ee_score'].mean()
        dp_moy = df['dp_score'].mean()
        pa_moy = df['pa_score'].mean()

        def get_niv_color(niv):
            return '#16a34a' if niv == 'Faible' else '#d97706' if niv == 'Modéré' else '#dc2626'

        def draw_dim_new(title, n_f, pf, n_m, pm, n_e, pe, score_moy, niv_moy):
            niv_color = get_niv_color(niv_moy)

            def segment(pct, bg, label, n):
                if pct < 3:
                    return f'<div style="width:{pct:.1f}%;background:{bg};min-height:36px;"></div>'
                return (
                    f'<div style="width:{pct:.1f}%;background:{bg};min-height:36px;'
                    f'display:flex;flex-direction:column;align-items:center;justify-content:center;">'
                    f'<span style="font-size:12px;font-weight:700;color:white;line-height:1.3;">{pct:.1f}%</span>'
                    f'<span style="font-size:10px;color:rgba(255,255,255,0.85);">{label} ({n})</span>'
                    f'</div>'
                )

            bar = (
                f'<div style="display:flex;border-radius:7px;overflow:hidden;margin:10px 0 14px;">'
                + segment(pf, '#4ade80' if False else '#16a34a', 'Faible', n_f)
                + segment(pm, '#d97706', 'Modéré', n_m)
                + segment(pe, '#dc2626', 'Élevé',  n_e)
                + '</div>'
            )

            msg = (
                f'<div style="font-size:12px;color:#64748b;padding:8px 10px;'
                f'background:#f8fafc;border-radius:6px;border:1px solid #e2e8f0;">'
                f'Score moyen de l\'entreprise : <b style="color:#1e293b;">{score_moy:.1f}</b>'
                f' → niveau <b style="color:{niv_color};">{niv_moy}</b>'
                f'</div>'
            )

            return (
                f'<div style="background:white;padding:14px 16px;border-radius:10px;'
                f'margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,0.06);border:1px solid #e8edf5;">'
                f'<div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:4px;">{title}</div>'
                f'{bar}'
                f'{msg}'
                f'</div>'
            )

        st.markdown(draw_dim_new(
            "Épuisement Émotionnel",
            ee_f[0], ee_f[1], ee_m2[0], ee_m2[1], ee_e[0], ee_e[1],
            ee_moy, cat_ee_new(ee_moy)
        ), unsafe_allow_html=True)

        st.markdown(draw_dim_new(
            "Dépersonnalisation",
            dp_f[0], dp_f[1], dp_m2[0], dp_m2[1], dp_e[0], dp_e[1],
            dp_moy, cat_dp_new(dp_moy)
        ), unsafe_allow_html=True)

        st.markdown(draw_dim_new(
            "Accomplissement Personnel",
            pa_f[0], pa_f[1], pa_m2[0], pa_m2[1], pa_e[0], pa_e[1],
            pa_moy, cat_pa_new(pa_moy)
        ), unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Analyses bivariées — style exact ancien code ───────
    sec("Analyses bivariées détaillées")

    VAR_CROISE = {
        "Sélectionner une variable": None,
        "Tranche d'âge":             "tranche_age",
        "Ancienneté":                "tranche_anciennete",
        "Catégorie IMC":             "imc_categorie",
        "Genre":                     "genre",
        "Situation matrimoniale":    "situation_matrimoniale",
        "Pratique de sport":         "pratique_sport",
        "Maladie chronique":         "maladie_chronique",
        "Handicap physique":         "handicap_physique",
        "Suivi psychologique":       "suivi_psychologique",
    }
    sel_c_label = st.selectbox("Sélectionnez une variable démographique à analyser :",
                               list(VAR_CROISE.keys()), key="croise_tab2")
    sel_c_col   = VAR_CROISE[sel_c_label]

    def render_table_mbi(df_t):
        html = (
            '<div style="overflow-x:auto;border-radius:8px;border:1px solid #dee2e6;">'
            '<table style="width:100%;border-collapse:collapse;background:white;font-size:13px;">'
            '<thead><tr style="background:#1e40af;color:white;">'
        )
        html += f'<th style="padding:10px 12px;text-align:left;font-weight:600;border:1px solid #1e3a8a;">{df_t.index.name or ""}</th>'
        for c in df_t.columns:
            html += f'<th style="padding:10px 12px;text-align:center;font-weight:600;border:1px solid #1e3a8a;">{c}</th>'
        html += '</tr></thead><tbody>'
        for i,(idx,row) in enumerate(df_t.iterrows()):
            bg = "white" if i%2==0 else "#f8fafc"
            html += f'<tr style="background:{bg};">'
            html += f'<td style="padding:9px 12px;font-weight:600;color:#1e293b;border:1px solid #e2e8f0;">{idx}</td>'
            for v in row:
                try:    fmt = f"{float(v):.1f}%"
                except: fmt = str(v)
                html += f'<td style="padding:9px 12px;text-align:center;color:#475569;border:1px solid #e2e8f0;">{fmt}</td>'
            html += '</tr>'
        html += '</tbody></table></div>'
        return html

    def msg_ligne(table, label_var):
        lignes = [idx for idx in table.index if str(idx) not in ('TOTAL','Total')]
        if len(lignes) < 2:
            return "Ce tableau montre la répartition du burnout au sein de chaque catégorie. La somme de chaque ligne fait 100%."
        l1, l2 = lignes[0], lignes[1]
        v1 = table.loc[l1, 'Pas de burnout']
        v2 = table.loc[l2, 'Pas de burnout']
        return (
            f"Sur 100 personnes de la catégorie <b>« {l1} »</b>, <b>{v1:.1f}%</b> ne présentent pas de burnout — "
            f"contre <b>{v2:.1f}%</b> parmi la catégorie <b>« {l2} »</b>. "
            f"Ce tableau compare, ligne par ligne, comment le burnout se distribue au sein de chaque catégorie de {label_var}."
        )

    def msg_colonne(table, label_var):
        lignes = [idx for idx in table.index if str(idx) not in ('TOTAL','Total')]
        if not lignes:
            return "Ce tableau montre la composition de chaque groupe de burnout. La somme de chaque colonne fait 100%."
        l1 = lignes[0]
        v_pas = table.loc[l1, 'Pas de burnout']
        v_pre = table.loc[l1, 'Pré-burnout']
        v_av  = table.loc[l1, 'Burnout avéré']
        return (
            f"Sur 100 personnes <b>sans burnout</b>, <b>{v_pas:.1f}%</b> appartiennent à la catégorie <b>« {l1} »</b> — "
            f"contre <b>{v_pre:.1f}%</b> parmi les personnes en <b>pré-burnout</b> "
            f"et <b>{v_av:.1f}%</b> parmi celles en <b>burnout avéré</b>. "
            f"Ce tableau compare la composition de chaque groupe de burnout selon {label_var}."
        )

    if sel_c_col and sel_c_col in df.columns:
        ORDER = ['Pas de burnout','Pré-burnout','Burnout avéré']
        t_ligne   = pd.crosstab(df[sel_c_col], df['niveau_burnout'], normalize='index')*100
        t_ligne   = t_ligne[[c for c in ORDER if c in t_ligne.columns]]
        t_ligne['TOTAL'] = t_ligne.sum(axis=1)

        t_colonne = pd.crosstab(df[sel_c_col], df['niveau_burnout'], normalize='columns')*100
        t_colonne = t_colonne[[c for c in ORDER if c in t_colonne.columns]]
        t_colonne.loc['TOTAL'] = t_colonne.sum(axis=0)

        viz_tab, lig_tab, col_tab = st.tabs([
            "  Visualisation Graphique",
            "  Tableau Croisé % Ligne",
            "  Tableau Croisé % Colonne"
        ])

        with viz_tab:
            fig2, ax2 = plt.subplots(figsize=(12, 7))
            fig2.patch.set_facecolor('#f1f4f9')
            ax2.set_facecolor('white')
            data_plot = t_ligne[[c for c in ORDER if c in t_ligne.columns]].copy()
            data_plot.plot(kind='barh', stacked=True, ax=ax2,
                           color=['#16a34a','#d97706','#dc2626'],
                           edgecolor='none', linewidth=0)
            for i, idx in enumerate(data_plot.index):
                cumsum = 0
                for cat in data_plot.columns:
                    pv = data_plot.loc[idx, cat]
                    if pv > 5:
                        ax2.text(cumsum + pv/2, i, f'{pv:.1f}%',
                                 ha='center', va='center', color='white',
                                 fontsize=11, fontweight='bold')
                    cumsum += pv
            ax2.set_xlabel('Pourcentage (%)', fontsize=13, fontweight='bold', color='#1e293b')
            ax2.set_ylabel(sel_c_label, fontsize=13, fontweight='bold', color='#1e293b')
            ax2.set_title(
                f"Répartition du Burnout des Employés de l'Entreprise Pahaliah & Fils\nselon : {sel_c_label}",
                fontsize=15, fontweight='bold', pad=20, color='#1e293b')
            ax2.legend(title='Niveau Burnout', loc='upper center',
                       bbox_to_anchor=(0.5,-0.12), ncol=3, frameon=False, fontsize=11)
            ax2.set_xlim(0, 100)
            ax2.grid(axis='x', alpha=0.3, linestyle='--')
            ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig2)
            buf2 = BytesIO()
            fig2.savefig(buf2, format='png', dpi=300, bbox_inches='tight', facecolor='#f1f4f9')
            buf2.seek(0)
            st.download_button("⬇  Télécharger le graphique (PNG)", buf2,
                               f"burnout_{sel_c_col}.png", "image/png", key="dl_viz")
            plt.close()

        with lig_tab:
            st.markdown(f"<p style='font-size:13px;color:#1e293b;font-weight:600;'>Tableau croisé % ligne : {sel_c_label} vs Burnout</p>", unsafe_allow_html=True)
            st.markdown(render_table_mbi(t_ligne), unsafe_allow_html=True)
            st.markdown(
                f'<div style="margin-top:12px;background:#f8fafc;border-radius:8px;'
                f'padding:12px 15px;border-left:4px solid #1e40af;">'
                f'<div style="font-size:11px;font-weight:700;color:#1e293b;'
                f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">'
                f'<i class="fas fa-book-open" style="margin-right:6px;color:#1e40af;"></i>'
                f'Comment lire ce tableau</div>'
                f'<p style="font-size:12px;color:#475569;margin:0;line-height:1.7;">'
                f'{msg_ligne(t_ligne, sel_c_label)}</p></div>',
                unsafe_allow_html=True
            )
            csv = t_ligne.to_csv(index=True).encode('utf-8')
            st.download_button("⬇  Télécharger le tableau (CSV)", csv,
                               f"ligne_{sel_c_col}.csv", "text/csv", key="dl_lig")

        with col_tab:
            st.markdown(f"<p style='font-size:13px;color:#1e293b;font-weight:600;'>Tableau croisé % colonne : {sel_c_label} vs Burnout</p>", unsafe_allow_html=True)
            st.markdown(render_table_mbi(t_colonne), unsafe_allow_html=True)
            st.markdown(
                f'<div style="margin-top:12px;background:#f8fafc;border-radius:8px;'
                f'padding:12px 15px;border-left:4px solid #1e40af;">'
                f'<div style="font-size:11px;font-weight:700;color:#1e293b;'
                f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;">'
                f'<i class="fas fa-book-open" style="margin-right:6px;color:#1e40af;"></i>'
                f'Comment lire ce tableau</div>'
                f'<p style="font-size:12px;color:#475569;margin:0;line-height:1.7;">'
                f'{msg_colonne(t_colonne, sel_c_label)}</p></div>',
                unsafe_allow_html=True
            )
            csv2 = t_colonne.to_csv(index=True).encode('utf-8')
            st.download_button("⬇  Télécharger le tableau (CSV)", csv2,
                               f"colonne_{sel_c_col}.csv", "text/csv", key="dl_col")

    elif sel_c_col:
        st.warning(f"⚠️ La colonne '{sel_c_col}' n'existe pas dans les données.")

# ── Footer ────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-top:40px;padding:14px 0;border-top:1px solid #e2e8f0;'
    'display:flex;align-items:center;justify-content:space-between;">'
    '<div style="display:flex;align-items:center;gap:10px;">'
    '<div style="width:22px;height:22px;background:linear-gradient(135deg,#1e40af,#3b82f6);'
    'border-radius:6px;display:flex;align-items:center;justify-content:center;">'
    '<i class="fas fa-chart-line" style="color:white;font-size:9px;"></i></div>'
    '<span style="font-size:12px;font-weight:600;color:#374151;">YODAN Analytics</span>'
    '<span style="font-size:12px;color:#cbd5e1;">\u00b7</span>'
    '<span style="font-size:12px;color:#94a3b8;">MBI Burnout v2.0 \u00b7 2026</span>'
    '</div>'
    '<span style="font-size:11px;color:#cbd5e1;">Maslach Burnout Inventory</span>'
    '</div>',
    unsafe_allow_html=True
)