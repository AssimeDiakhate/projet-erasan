"""
================================================================================
APPLICATION DE PRÉDICTION DES INDEMNISATIONS AGRICOLES
Projet d'Économétrie et d'Actuariat - UADB
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import statsmodels.api as sm
import warnings
import os
import plotly.express as px
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================

st.set_page_config(
    page_title="Prédiction des Indemnisations Agricoles",
    page_icon="🌾",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        text-align: center;
        padding: 20px;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stButton button {
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #1B5E20;
    }
</style>
""", unsafe_allow_html=True)

# Titre
st.markdown('<p class="main-header">🌾 Prédiction des Indemnisations Agricoles</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Application basée sur les modèles économétriques et actuariels</p>', unsafe_allow_html=True)
st.markdown("---")

# ============================================================================
# CHARGEMENT DES MODÈLES
# ============================================================================

@st.cache_resource
def charger_modeles():
    """Charge les modèles sauvegardés"""
    modeles = {}
    
    try:
        with open('modeles/model_binomial_negatif.pkl', 'rb') as f:
            modeles['binomial_negatif'] = pickle.load(f)
        st.sidebar.success("✅ Binomial Négatif")
    except:
        st.sidebar.error("❌ Binomial Négatif")
        modeles['binomial_negatif'] = None
    
    try:
        with open('modeles/model_log_gamma.pkl', 'rb') as f:
            modeles['log_gamma'] = pickle.load(f)
        st.sidebar.success("✅ Log-Gamma")
    except:
        st.sidebar.error("❌ Log-Gamma")
        modeles['log_gamma'] = None
    
    try:
        with open('modeles/model_regression_logistique.pkl', 'rb') as f:
            modeles['regression_logistique'] = pickle.load(f)
        st.sidebar.success("✅ Régression Logistique")
    except:
        st.sidebar.error("❌ Régression Logistique")
        modeles['regression_logistique'] = None
    
    return modeles

modeles = charger_modeles()
##

# Ajouter en haut du fichier
if 'historique' not in st.session_state:
    st.session_state.historique = []

# Après chaque prédiction
st.session_state.historique.append({
    'Date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
    'Fréquence': freq,
    'Coût': cout,
    'Vulnérabilité': classe
})

# Afficher l'historique
if len(st.session_state.historique) > 0:
    st.subheader("📜 Historique des prédictions")
    st.dataframe(pd.DataFrame(st.session_state.historique))

##
# ============================================================================
# FONCTIONS DE PRÉDICTION
# ============================================================================

def predict_frequence(model, X_new):
    """Prédit la fréquence d'indemnisation"""
    required_cols = ['taille_numeric', 'age_numeric', 'revenu', 'sca', 'depalim',
                     'Inondation', 'pluies_insuffisantes', 'pluies_hors_saison', 'sexe_encoded']
    
    for col in required_cols:
        if col not in X_new.columns:
            X_new[col] = 0
    
    X_pred = X_new[required_cols].fillna(0)
    X_pred = sm.add_constant(X_pred)
    
    return float(model.predict(X_pred)[0])

def predict_cout(model, X_new):
    """Prédit le coût moyen d'indemnisation"""
    required_cols = ['taille_numeric', 'age_numeric', 'revenu', 'depalim', 'sca', 'sci',
                     'Inondation', 'pluies_insuffisantes', 'pluies_hors_saison', 'sexe_encoded']
    
    for col in required_cols:
        if col not in X_new.columns:
            X_new[col] = 0
    
    X_pred = X_new[required_cols].fillna(0)
    X_pred = sm.add_constant(X_pred)
    
    return float(model.predict(X_pred)[0] - 1)

def predict_vulnerabilite(model, X_new):
    """Prédit la vulnérabilité"""
    required_cols = ['Inondation', 'pluies_insuffisantes', 'pluies_hors_saison',
                     'sexe_encoded', 'taille_numeric', 'age_numeric']
    
    for col in required_cols:
        if col not in X_new.columns:
            X_new[col] = 0
    
    X_pred = X_new[required_cols].fillna(0)
    X_pred = sm.add_constant(X_pred)
    
    proba = float(model.predict(X_pred)[0])
    classe = "Vulnérable" if proba >= 0.5 else "Non vulnérable"
    
    return proba, classe

def predict_simple(data):
    """Prédiction simplifiée (fallback)"""
    freq = 5 + 0.5 * data['sci'].iloc[0] + 0.1 * (data['revenu'].iloc[0] / 1000000)
    cout = 100000 + 1000 * data['sci'].iloc[0] + 0.5 * data['revenu'].iloc[0]
    proba = 0.3 + 0.2 * data['Inondation'].iloc[0] + 0.1 * (data['age_numeric'].iloc[0] / 100)
    proba = min(max(proba, 0), 1)
    classe = "Vulnérable" if proba >= 0.5 else "Non vulnérable"
    return freq, cout, proba, classe

# ============================================================================
# INTERFACE UTILISATEUR
# ============================================================================

with st.sidebar:
    st.header("📋 Caractéristiques du ménage")
    
    st.subheader("👨‍👩‍👧‍👦 Démographie")
    taille = st.number_input("Taille du ménage", min_value=1, max_value=50, value=15)
    age = st.number_input("Âge du chef", min_value=18, max_value=100, value=45)
    sexe = st.selectbox("Sexe du chef", ["Masculin", "Féminin"])
    
    st.subheader("💰 Économie")
    revenu = st.number_input("Revenu (FCFA)", min_value=0, max_value=50000000, value=1000000, step=100000)
    depalim = st.number_input("Dépenses alimentaires (FCFA)", min_value=0, max_value=1000000, value=250000, step=10000)
    
    st.subheader("🍽️ Alimentation")
    sca = st.number_input("Score de consommation (SCA)", min_value=0, max_value=120, value=60)
    sci = st.number_input("Stratégies de survie (SCI)", min_value=0, max_value=50, value=8)
    
    st.subheader("🌦️ Chocs climatiques")
    inondation = st.selectbox("Inondation", ["Non", "Oui"])
    pluies_insuf = st.selectbox("Pluies insuffisantes", ["Non", "Oui"])
    pluies_hs = st.selectbox("Pluies hors saison", ["Non", "Oui"])
    
    st.markdown("---")
    st.caption("Les champs marqués d'un * sont obligatoires")

# ============================================================================
# PRÉDICTION
# ============================================================================

if st.sidebar.button("🔮 Prédire", type="primary", width='stretch'):
    
    # Préparation des données
    sexe_encoded = 0 if sexe == "Masculin" else 1
    data = pd.DataFrame([{
        'taille_numeric': taille,
        'age_numeric': age,
        'revenu': revenu,
        'sca': sca,
        'depalim': depalim,
        'sci': sci,
        'Inondation': 1 if inondation == "Oui" else 0,
        'pluies_insuffisantes': 1 if pluies_insuf == "Oui" else 0,
        'pluies_hors_saison': 1 if pluies_hs == "Oui" else 0,
        'sexe_encoded': sexe_encoded
    }])
    
    with st.spinner("Calcul des prédictions..."):
        # Tentative avec les vrais modèles
        if modeles['binomial_negatif'] is not None and modeles['log_gamma'] is not None:
            try:
                freq = predict_frequence(modeles['binomial_negatif'], data)
                cout = predict_cout(modeles['log_gamma'], data)
                proba, classe = predict_vulnerabilite(modeles['regression_logistique'], data)
                modele_utilise = "Modèles réels entraînés"
            except:
                freq, cout, proba, classe = predict_simple(data)
                modele_utilise = "⚠️ Modèles simplifiés (fallback)"
        else:
            freq, cout, proba, classe = predict_simple(data)
            modele_utilise = "⚠️ Modèles simplifiés (fallback)"
    
    # ========================================================================
    # AFFICHAGE DES RÉSULTATS
    # ========================================================================
    
    st.markdown("## 📊 Résultats des prédictions")
    st.markdown(f"*{modele_utilise}*")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Fréquence d'indemnisation</h3>
            <h1 style="color:#2E7D32;">{:.1f}</h1>
            <p><small>{} indemnisation(s) attendue(s)</small></p>
        </div>
        """.format(freq, int(freq)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Coût moyen</h3>
            <h1 style="color:#1565C0;">{:,.0f} FCFA</h1>
            <p><small>Coût par indemnisation</small></p>
        </div>
        """.format(cout), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ Vulnérabilité</h3>
            <h1 style="color:{};">{}</h1>
            <p><small>Probabilité: {:.1f}%</small></p>
        </div>
        """.format("#D32F2F" if proba >= 0.5 else "#2E7D32", classe, proba*100), unsafe_allow_html=True)
    
    # Détails
    st.markdown("---")
    st.subheader("📋 Détails des prédictions")
    
    details = {
        "Indicateur": [
            "Fréquence d'indemnisation",
            "Coût moyen d'indemnisation",
            "Probabilité de vulnérabilité",
            "Statut de vulnérabilité"
        ],
        "Valeur": [
            f"{freq:.2f} indemnisations",
            f"{cout:,.0f} FCFA",
            f"{proba*100:.1f}%",
            classe
        ],
        "Interprétation": [
            f"Le ménage devrait recevoir environ {int(freq)} indemnisation(s)",
            f"Coût moyen par indemnisation d'environ {cout:,.0f} FCFA",
            f"Risque de vulnérabilité de {proba*100:.1f}%",
            f"Ménage classé comme '{classe}'"
        ]
    }
    
    st.dataframe(pd.DataFrame(details), width='stretch', hide_index=True)
    
    # Graphique de risque
    st.subheader("📊 Niveau de risque")
    
    fig, ax = plt.subplots(figsize=(10, 2))
    colors = ['#4CAF50', '#FFC107', '#F44336']
    
    # Barre de risque
    ax.barh(['Risque'], [proba*100], color='#2E7D32', height=0.3)
    ax.barh(['Risque'], [100 - proba*100], left=[proba*100], color='#E0E0E0', height=0.3)
    
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_yticks([])
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    st.pyplot(fig)
    
    # Recommandations
    st.markdown("---")
    st.subheader("💡 Recommandations")
    
    if proba >= 0.5:
        st.warning("""
        **🚨 Recommandations pour les ménages vulnérables :**
        - ✅ Envisager une assurance agricole adaptée
        - ✅ Diversifier les sources de revenus
        - ✅ Adopter des techniques agricoles résilientes
        - ✅ Créer des systèmes d'épargne pour les périodes de soudure
        - ✅ Participer aux programmes d'adaptation climatique
        """)
    else:
        st.success("""
        **✅ Recommandations pour les ménages non vulnérables :**
        - ✅ Maintenir les bonnes pratiques agricoles
        - ✅ Continuer à diversifier les activités
        - ✅ Partager les bonnes pratiques avec d'autres ménages
        - ✅ Renforcer les capacités de résilience
        """)

else:
    # Message d'accueil
    st.info("👈 **Bienvenue !** Remplissez les caractéristiques du ménage dans le panneau de gauche et cliquez sur **'Prédire'**.")
    
    # Présentation
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align:center;">
            <h2>📈</h2>
            <h3>Fréquence</h3>
            <p>Modèle Binomial Négatif<br>AIC: 549,54</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align:center;">
            <h2>💰</h2>
            <h3>Coût</h3>
            <p>Modèle Log-Gamma<br>AIC: 2046,67</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align:center;">
            <h2>⚠️</h2>
            <h3>Vulnérabilité</h3>
            <p>Régression Logistique<br>Précision: 66,25%</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PIED DE PAGE
# ============================================================================

st.markdown("---")
st.caption("""
**Projet d'Économétrie et d'Actuariat** | UADB | 2024-2025

*Application développée dans le cadre du projet de fin de module.*
""")
