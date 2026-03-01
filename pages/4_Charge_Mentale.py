# ============================================================
# YODAN ANALYTICS — 4_Charge_Mentale.py
# Charge Mentale & Stress
# Style : YODAN / Pahaliah & Fils
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Charge Mentale - YODAN Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS YODAN ─────────────────────────────────────────────────
st.markdown(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">'
    '<style>'
    'html,body,[class*="css"]{font-family:Inter,sans-serif!important;color:#0F172A}'
    '.main{background:#f1f4f9!important}'
    '.block-container{padding:1.5rem 2rem!important;max-width:1300px!important}'
    '#MainMenu,footer,header{visibility:hidden}'
    '[data-testid="metric-container"]{'
    'background:white;border-radius:12px;padding:1.1rem 1.3rem;'
    'border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(15,23,42,0.06);transition:all 0.2s}'
    '[data-testid="metric-container"]:hover{'
    'transform:translateY(-2px);border-color:#93c5fd;box-shadow:0 4px 16px rgba(37,99,235,0.12)}'
    '[data-testid="stMetricLabel"] p{font-size:0.72rem!important;color:#64748b!important;'
    'text-transform:uppercase;letter-spacing:0.06em;font-weight:600!important}'
    '[data-testid="stMetricValue"]{font-family:Sora,sans-serif!important;font-size:1.7rem!important;'
    'font-weight:700!important;color:#0f172a!important}'
    'div[data-baseweb="select"]>div{background:white!important;border:1.5px solid #cbd5e1!important;'
    'border-radius:9px!important;color:#1e293b!important}'
    'div[data-baseweb="select"] *{color:#1e293b!important}'
    '.stSelectbox label,.stSelectbox p{color:#1e293b!important;font-weight:600!important;font-size:13px!important}'
    'ul[role="listbox"]{background:white!important;border:1px solid #e2e8f0!important;border-radius:10px!important}'
    'li[role="option"]{background:white!important;color:#1e293b!important;font-size:13px!important}'
    'li[role="option"] *{color:#1e293b!important}'
    'li[role="option"]:hover{background:#eff6ff!important}'
    'li[role="option"][aria-selected="true"]{background:#1e40af!important;color:white!important}'
    'li[role="option"][aria-selected="true"] *{color:white!important}'
    '.stButton>button{background:white!important;color:#1e40af!important;'
    'border:1.5px solid #bfdbfe!important;border-radius:10px!important;'
    'font-weight:600!important;font-size:13px!important;transition:all 0.2s!important}'
    '.stButton>button:hover{background:#1e40af!important;color:white!important}'
    '</style>',
    unsafe_allow_html=True
)

# ============================================================
# CONSTANTES (identiques au code ami)
# ============================================================
COMPANY          = "Pahaliah & Fils"
SCORE_STRESS_MAX = 40   

# Colonnes brutes du CSV -> on les renomme Stress_Q1..Q10 
CSV_Q_COLS = [
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_ete_contrarie_par_un_evenement_inattendu",
    "au_cours_du_dernier_mois_a_quelle_frequence_vous_etes_vous_senti_incable_de_controler_les_choses_importantes_dans_votre_vie",
    "au_cours_du_dernier_mois_a_quelle_frequence_vous_etes_vous_senti_nerveux_ou_stresse",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_eu_le_sentiment_de_bien_maitriser_les_choses",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_senti_que_les_difficultes_s_accumulaient_au_point_de_ne_plus_pouvoir_les_surmonter",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_eu_confiance_en_votre_capacite_a_resoudre_vos_problemes_personnels",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_estime_que_les_choses_allaient_comme_vous_le_vouliez",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_eu_le_sentiment_que_vous_ne_pouviez_pas_maitriser_toutes_les_choses_que_vous_aviez_a_faire",
    "au_cours_du_dernier_mois_a_quelle_frequence_avez_vous_pu_controler_vos_difficultes",
    "au_cours_du_dernier_mois_a_quelle_frequence_vous_etes_vous_senti_depasse_par_les_evenements",
]
Q_COLS = [f"Stress_Q{i+1}" for i in range(10)]  

# ============================================================
# CHARGEMENT & PIPELINE 
# ============================================================
@st.cache_data
def load_and_process(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8-sig", sep=None, engine="python")
    except Exception:
        df = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")

    # Renommer les colonnes Q → Stress_Q1..Q10 
    rename_map = {csv: q for csv, q in zip(CSV_Q_COLS, Q_COLS) if csv in df.columns}
    df = df.rename(columns=rename_map)

    # ── Score stress : SOMME BRUTE Q1..Q10, aucune inversion ──
    df["score_stress"]        = df[Q_COLS].sum(axis=1)
    df["Score_Stress_Total"]  = df["score_stress"]

    # ICM et TP 
    df["ICM_i"] = (df["score_stress"] / SCORE_STRESS_MAX) * 100
    df["TP_i"]  = (1 - (df["score_stress"] / SCORE_STRESS_MAX)) * 100

    # Catégories d'âge 
    df["Tranche_Age"] = np.select(
        [
            df["Age"] <= 20,
            (df["Age"] >= 21) & (df["Age"] < 30),
            (df["Age"] >= 30) & (df["Age"] < 40),
            (df["Age"] >= 40) & (df["Age"] < 50),
            (df["Age"] >= 50) & (df["Age"] < 60),
            df["Age"] >= 60,
        ],
        ["20 ans et moins","21-29 ans","30-39 ans","40-49 ans","50-59 ans","60 ans et plus"],
        default=np.nan,
    )

    # Catégories taille / poids 
    df["taille_cat"] = pd.cut(
        df["Taille_cm"],
        bins=[0, 159.9, 169.9, 179.9, 1000],
        labels=["<160 cm","160-169 cm","170-179 cm","180 cm et plus"],
        include_lowest=True,
    )
    df["poids_cat"] = pd.cut(
        df["Poids_kg"],
        bins=[0, 59.9, 74.9, 89.9, 1000],
        labels=["<60 kg","60-74 kg","75-89 kg","90 kg et plus"],
        include_lowest=True,
    )

    # Catégories ancienneté 
    df["anciennete_cat"] = np.select(
        [
            df["Anciennete"] <= 2,
            df["Anciennete"] <= 5,
            df["Anciennete"] <= 10,
            df["Anciennete"] <= 20,
        ],
        ["0-2 ans","3-5 ans","6-10 ans","11-20 ans"],
        default="20 ans et plus",
    )

    # Niveau de stress 
    df["niveau"] = np.select(
        [
            df["score_stress"] <= 13,
            (df["score_stress"] > 13) & (df["score_stress"] <= 26),
            (df["score_stress"] > 26) & (df["score_stress"] <= 40),
        ],
        ["Niveau de stress faible","Niveau de stress modere","Niveau de stress eleve"],
        default=np.nan,
    )

    return df

# ============================================================
# JAUGE 
# ============================================================
def construire_psy_gauge(valeur: float, titre: str, mode: str = "stress") -> go.Figure:
    if mode == "stress":
        steps = [
            {"range": [0,  35], "color": "#4CAF50"},
            {"range": [35, 65], "color": "#FFC107"},
            {"range": [65,100], "color": "#F44336"},
        ]
        bar_color = "#F44336" if valeur >= 65 else ("#FFC107" if valeur >= 35 else "#4CAF50")
    else:  # productivité
        steps = [
            {"range": [0,  35], "color": "#F44336"},
            {"range": [35, 65], "color": "#FFC107"},
            {"range": [65,100], "color": "#4CAF50"},
        ]
        bar_color = "#4CAF50" if valeur >= 65 else ("#FFC107" if valeur >= 35 else "#F44336")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(valeur, 1),
        number={"suffix": "%", "font": {"size": 32, "family": "Sora", "color": "#0f172a"}},
        title={"text": titre, "font": {"size": 14, "family": "Sora", "color": "#0f172a"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#64748b", "size": 10}},
            "bar":  {"color": bar_color, "thickness": 0.72},
            "bgcolor": "#f8fafc",
            "bordercolor": "#e2e8f0",
            "borderwidth": 1,
            "steps": steps,
            "threshold": {
                "line": {"color": "#64748b", "width": 2},
                "thickness": 0.8,
                "value": 50,
            },
        },
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#0f172a"),
    )
    return fig

# ============================================================
# HELPERS
# ============================================================
def sec(text: str):
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin:22px 0 12px;">'
        f'<div style="width:4px;height:18px;background:linear-gradient(180deg,#1e40af,#60a5fa);border-radius:4px;"></div>'
        f'<span style="font-family:Sora,sans-serif;font-size:11px;font-weight:700;color:#64748b;'
        f'letter-spacing:1.2px;text-transform:uppercase;">{text}</span></div>',
        unsafe_allow_html=True
    )

def find_csv() -> str | None:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in [
        os.path.join(base, "data", "Charge_mentale_2.csv"),
        "data/Charge_mentale_2.csv",
        "Charge_mentale_2.csv",
    ]:
        if os.path.exists(p): return p
    return None

# ============================================================
# EN-TÊTE YODAN
# ============================================================
col_h1, col_h2 = st.columns([8, 2])
with col_h1:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">'
        f'<div style="width:42px;height:42px;background:linear-gradient(135deg,#1e40af,#3b82f6);'
        f'border-radius:10px;display:flex;align-items:center;justify-content:center;">'
        f'<i class="fas fa-brain" style="color:white;font-size:18px;"></i></div>'
        f'<div>'
        f'<div style="font-family:Sora,sans-serif;font-size:20px;font-weight:800;color:#0f172a;">'
        f'Charge Mentale & Stress</div>'
        f'<div style="font-size:13px;color:#64748b;">'
        f'Suivi de la charge mentale, du risque d\'épuisement et de la capacité productive · {COMPANY}</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )
with col_h2:
    if st.button("← Accueil", key="back_home_cm"):
        st.switch_page("app.py")

st.markdown(
    "<hr style='border:none;border-top:1px solid #e2e8f0;margin:4px 0 16px;'>",
    unsafe_allow_html=True
)

# ============================================================
# CHARGEMENT
# ============================================================
# ── Import fichier via sidebar ────────────────────────────────
with st.sidebar:
    st.header("📂 Données")
    _cm_sidebar_up = st.file_uploader(
        "Charger un fichier Excel ou CSV",
        type=["xlsx", "xls", "csv"],
        help="Glissez-déposez ou cliquez pour sélectionner votre fichier de données.",
        key="cm_sidebar_uploader",
    )
if _cm_sidebar_up is not None:
    _b = _cm_sidebar_up.read()
    if _b:
        st.session_state["cm_file_bytes"] = _b
        st.session_state["cm_file_name"] = _cm_sidebar_up.name

if "cm_file_bytes" in st.session_state:
    import io as _io
    _fn = st.session_state["cm_file_name"]
    _buf = _io.BytesIO(st.session_state["cm_file_bytes"])
    try:
        if _fn.lower().endswith(".csv"):
            df = pd.read_csv(_buf, sep=None, engine="python")
        else:
            df = pd.read_excel(_buf)
        # Appliquer le preprocessing si la fonction existe
        if "load_and_process" in dir() or "load_and_process" in globals():
            pass  # df déjà chargé
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement : {e}")
        st.stop()
else:
    csv_path = find_csv()
    if not csv_path:
        st.info("📂 Veuillez charger un fichier de données (Excel ou CSV) pour démarrer l'analyse.")
        _main_up = st.file_uploader(
            "Ou importez votre fichier ici",
            type=["xlsx", "xls", "csv"],
            key="cm_main_uploader",
        )
        if _main_up is not None:
            _b = _main_up.read()
            if _b:
                st.session_state["cm_file_bytes"] = _b
                st.session_state["cm_file_name"] = _main_up.name
        if "cm_file_bytes" not in st.session_state:
            st.stop()
    else:
        df = load_and_process(csv_path)

# ============================================================
# FILTRES 
# ============================================================
familles = {
    "Variables sociodémographiques": ["Sexe", "Tranche_Age", "Situation_matrimoniale"],
    "Variables anthropométriques":   ["taille_cat", "poids_cat"],
    "Variables de travail":          ["anciennete_cat", "Direction", "Fonction", "Poste"],
}

st.markdown(
    '<div style="background:white;border-radius:14px;padding:16px 20px;'
    'border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(15,23,42,0.06);margin-bottom:20px;">',
    unsafe_allow_html=True
)
st.markdown(
    '<div style="font-family:Sora,sans-serif;font-size:12px;font-weight:700;color:#1e40af;'
    'text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Filtres d\'analyse</div>',
    unsafe_allow_html=True
)

f1, f2, f3 = st.columns(3)
with f1:
    famille_selectionnee = st.selectbox("Famille", options=list(familles.keys()), key="cm_famille")
with f2:
    variables_disponibles = familles[famille_selectionnee]
    variable_selectionnee = st.selectbox("Variable", options=variables_disponibles, key="cm_variable")
with f3:
    modalites = ["Tous"] + sorted(df[variable_selectionnee].dropna().astype(str).unique().tolist())
    modalite_selectionnee = st.selectbox("Modalite", options=modalites, key="cm_modalite")

st.markdown("</div>", unsafe_allow_html=True)

# Application filtre 
df_final = df.copy()
if modalite_selectionnee != "Tous":
    df_final = df_final[df_final[variable_selectionnee].astype(str) == modalite_selectionnee]

# ============================================================
# CALCULS 
# ============================================================
nb_repondants = len(df_final)
age_moyen     = float(df_final["Age"].mean())                            if nb_repondants > 0 else 0.0
pct_hommes    = float((df_final["Sexe"] == "Homme").mean() * 100)        if nb_repondants > 0 else 0.0
pct_femmes    = float((df_final["Sexe"] == "Femme").mean() * 100)        if nb_repondants > 0 else 0.0
icm_n         = float(df_final["ICM_i"].mean())                          if nb_repondants > 0 else 0.0
tp_n          = float(df_final["TP_i"].mean())                           if nb_repondants > 0 else 0.0

total_v     = len(df_final.dropna(subset=["niveau"]))
pct_faible  = float((df_final["niveau"] == "Niveau de stress faible").sum() / total_v * 100) if total_v > 0 else 0.0
pct_modere  = float((df_final["niveau"] == "Niveau de stress modere").sum() / total_v * 100) if total_v > 0 else 0.0
pct_eleve   = float((df_final["niveau"] == "Niveau de stress eleve").sum()  / total_v * 100) if total_v > 0 else 0.0

# ============================================================
# KPI CARDS 
# ============================================================
sec("Indicateurs clés")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#1e40af,#3b82f6);border-radius:12px;'
        f'padding:1.1rem 1.3rem;box-shadow:0 2px 8px rgba(30,64,175,0.2);">'
        f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.8);text-transform:uppercase;'
        f'letter-spacing:0.06em;font-weight:600;margin-bottom:4px;">Effectif analysé</div>'
        f'<div style="font-family:Sora,sans-serif;font-size:1.9rem;font-weight:700;color:white;">'
        f'{nb_repondants}</div></div>',
        unsafe_allow_html=True
    )
with k2:
    st.metric("Proportion hommes", f"{pct_hommes:.1f}%")
with k3:
    st.metric("Proportion femmes", f"{pct_femmes:.1f}%")
with k4:
    st.metric("Âge moyen", f"{age_moyen:.1f} ans")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# JAUGES ICM + TP 
# ============================================================
sec("Indice de charge mentale (ICM) et Taux de productivité (TP)")

g1, g2 = st.columns(2)
with g1:
    st.markdown(
        '<div style="background:white;border-radius:14px;padding:12px 16px;'
        'border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(15,23,42,0.06);">',
        unsafe_allow_html=True
    )
    fig_icm = construire_psy_gauge(icm_n, "ICM — Indice de Charge Mentale", mode="stress")
    st.plotly_chart(fig_icm, use_container_width=True, key="cm_gauge_icm")
    st.markdown('</div>', unsafe_allow_html=True)

with g2:
    st.markdown(
        '<div style="background:white;border-radius:14px;padding:12px 16px;'
        'border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(15,23,42,0.06);">',
        unsafe_allow_html=True
    )
    fig_tp = construire_psy_gauge(tp_n, "TP — Taux de Productivité", mode="productivite")
    st.plotly_chart(fig_tp, use_container_width=True, key="cm_gauge_tp")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# GRILLE NIVEAUX DE STRESS 
# ============================================================
sec("Distribution des niveaux de stress")

s1, s2, s3 = st.columns(3)

for col_s, label, pct, color, bg, border in [
    (s1, "Niveau de stress faible",  pct_faible, "#16a34a", "#f0fdf4", "#bbf7d0"),
    (s2, "Niveau de stress modéré",  pct_modere, "#d97706", "#fffbeb", "#fde68a"),
    (s3, "Niveau de stress élevé",   pct_eleve,  "#dc2626", "#fff5f5", "#fecaca"),
]:
    n_abs = round(pct / 100 * total_v) if total_v > 0 else 0
    with col_s:
        st.markdown(
            f'<div style="background:{bg};border:2px solid {border};border-radius:14px;'
            f'text-align:center;padding:20px 12px;">'
            f'<div style="font-family:Sora,sans-serif;font-size:36px;font-weight:800;'
            f'color:{color};line-height:1;">{pct:.1f}%</div>'
            f'<div style="font-size:12px;color:{color};font-weight:600;margin-top:4px;">'
            f'n = {n_abs}</div>'
            f'<div style="font-size:12px;color:#475569;text-transform:uppercase;'
            f'letter-spacing:0.5px;margin-top:8px;font-weight:600;">{label}</div>'
            f'</div>',
            unsafe_allow_html=True
        )