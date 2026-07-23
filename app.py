"""
================================================================================
APPLICATION DE PRÉDICTION DES INDEMNISATIONS AGRICOLES
Déployée sur Streamlit Cloud
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import statsmodels.api as sm
import warnings
import os

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================

st.set_page_config(
    page_title="Prédiction des Indemnisations Agricoles",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Prédiction des Indemnisations Agricoles")
st.markdown("*Application basée sur les modèles économétriques et actuariels*")
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
        st.sidebar.success("✅ Binomial Négatif chargé")
    except:
        st.sidebar.error("❌ Binomial Négatif non trouvé")
        modeles['binomial_negatif'] = None
    
    try:
        with open('modeles/model_log_gamma.pkl', 'rb') as f:
            modeles['log_gamma'] = pickle.load(f)
        st.sidebar.success("✅ Log-Gamma chargé")
    except:
        st.sidebar.error("❌ Log-Gamma non trouvé")
        modeles['log_gamma'] = None
    
    try:
        with open('modeles/model_regression_logistique.pkl', 'rb') as f:
            modeles['regression_logistique'] = pickle.load(f)
        st.sidebar.success("✅ Régression Logistique chargé")
    except:
        st.sidebar.error("❌ Régression Logistique non trouvé")
        modeles['regression_logistique'] = None
    
    return modeles

# Chargement
with st.spinner("Chargement des modèles..."):
    modeles = charger_modeles()

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

# ============================================================================
# INTERFACE UTILISATEUR
# ============================================================================

# Barre latérale
with st.sidebar:
    st.header("📋 Caractéristiques du ménage")
    
    st.subheader("👨‍👩‍👧‍👦 Démographie")
    taille = st.number_input("Taille du ménage", min_value=1, max_value=50, value=15)
    age = st.number_input("Âge du chef", min_value=18, max_value=100, value=45)
    sexe = st.selectbox("Sexe du chef", ["Masculin", "Féminin"])
    
    st.subheader("💰 Économie")
    revenu = st.number_input(
        "Revenu (FCFA)", 
        min_value=100000, 
        max_value=50000000, 
        value=1000000, 
        step=100000,
        format="%d"
    )
    depalim = st.number_input(
        "Dépenses alimentaires (FCFA)", 
        min_value=50000, 
        max_value=1000000, 
        value=250000, 
        step=10000,
        format="%d"
    )
    
    st.subheader("🍽️ Alimentation")
    sca = st.number_input("Score de consommation (SCA)", min_value=0, max_value=120, value=60)
    sci = st.number_input("Stratégies de survie (SCI)", min_value=0, max_value=50, value=8)
    
    st.subheader("🌦️ Chocs climatiques")
    inondation = st.selectbox("Inondation", ["Non", "Oui"])
    pluies_insuf = st.selectbox("Pluies insuffisantes", ["Non", "Oui"])
    pluies_hs = st.selectbox("Pluies hors saison", ["Non", "Oui"])

# Conversion des variables
sexe_encoded = 0 if sexe == "Masculin" else 1
inondation_val = 1 if inondation == "Oui" else 0
pluies_insuf_val = 1 if pluies_insuf == "Oui" else 0
pluies_hs_val = 1 if pluies_hs == "Oui" else 0

# ============================================================================
# BOUTON DE PRÉDICTION
# ============================================================================

if st.sidebar.button("🔮 Prédire", type="primary", use_container_width=True):
    
    # Vérification des modèles
    if modeles['binomial_negatif'] is None or modeles['log_gamma'] is None or modeles['regression_logistique'] is None:
        st.error("❌ Certains modèles ne sont pas disponibles. Veuillez vérifier les fichiers.")
        st.stop()
    
    # Préparation des données
    data = pd.DataFrame([{
        'taille_numeric': taille,
        'age_numeric': age,
        'revenu': revenu,
        'sca': sca,
        'depalim': depalim,
        'sci': sci,
        'Inondation': inondation_val,
        'pluies_insuffisantes': pluies_insuf_val,
        'pluies_hors_saison': pluies_hs_val,
        'sexe_encoded': sexe_encoded
    }])
    
    # Prédictions
    with st.spinner("Calcul des prédictions..."):
        freq = predict_frequence(modeles['binomial_negatif'], data)
        cout = predict_cout(modeles['log_gamma'], data)
        proba, classe = predict_vulnerabilite(modeles['regression_logistique'], data)
    
    # ========================================================================
    # AFFICHAGE DES RÉSULTATS
    # ========================================================================
    
    st.markdown("## 📊 Résultats des prédictions")
    st.markdown("---")
    
    # 3 colonnes pour les métriques principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📈 Fréquence d'indemnisation",
            value=f"{freq:.1f}",
            delta=f"{int(freq)} indemnisation(s) attendue(s)"
        )
        st.caption(f"📌 Modèle : Binomial Négatif")
    
    with col2:
        st.metric(
            label="💰 Coût moyen par indemnisation",
            value=f"{cout:,.0f} FCFA"
        )
        st.caption(f"📌 Modèle : Log-Gamma")
    
    with col3:
        st.metric(
            label="⚠️ Statut de vulnérabilité",
            value=classe,
            delta=f"Probabilité: {proba*100:.1f}%",
            delta_color="inverse" if proba >= 0.5 else "normal"
        )
        st.caption(f"📌 Modèle : Régression Logistique")
    
    # Détails des prédictions
    st.markdown("---")
    st.subheader("📋 Détails des prédictions")
    
    # Création du tableau de détails
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
    
    df_details = pd.DataFrame(details)
    st.dataframe(df_details, use_container_width=True, hide_index=True)
    
    # ========================================================================
    # INTERPRÉTATION
    # ========================================================================
    
    st.markdown("---")
    st.subheader("📝 Interprétation des résultats")
    
    # Interprétation personnalisée
    interpretation = []
    
    # Fréquence
    if freq < 5:
        interpretation.append("✅ **Faible fréquence** : Le ménage devrait recevoir peu d'indemnisations.")
    elif freq < 15:
        interpretation.append("⚠️ **Fréquence modérée** : Le ménage devrait recevoir plusieurs indemnisations.")
    else:
        interpretation.append("🔴 **Fréquence élevée** : Le ménage est très exposé et devrait recevoir de nombreuses indemnisations.")
    
    # Coût
    if cout < 50000:
        interpretation.append("✅ **Faible coût** : Le coût moyen par indemnisation est relativement faible.")
    elif cout < 200000:
        interpretation.append("⚠️ **Coût modéré** : Le coût moyen par indemnisation est dans la moyenne.")
    else:
        interpretation.append("🔴 **Coût élevé** : Le coût moyen par indemnisation est très élevé.")
    
    # Vulnérabilité
    if proba >= 0.7:
        interpretation.append("🔴 **Risque élevé** : Le ménage présente un risque élevé de vulnérabilité.")
    elif proba >= 0.4:
        interpretation.append("⚠️ **Risque modéré** : Le ménage présente un risque modéré de vulnérabilité.")
    else:
        interpretation.append("✅ **Risque faible** : Le ménage présente un faible risque de vulnérabilité.")
    
    # Affichage
    for line in interpretation:
        st.write(line)
    
    # ========================================================================
    # RECOMMANDATIONS
    # ========================================================================
    
    st.markdown("---")
    st.subheader("💡 Recommandations")
    
    if proba >= 0.5:
        st.warning("""
        **🚨 Recommandations pour les ménages vulnérables :**
        - Envisager une assurance agricole adaptée
        - Diversifier les sources de revenus
        - Adopter des techniques agricoles résilientes
        - Créer des systèmes d'épargne pour les périodes de soudure
        """)
    else:
        st.success("""
        **✅ Recommandations pour les ménages non vulnérables :**
        - Maintenir les bonnes pratiques agricoles
        - Continuer à diversifier les activités
        - Partager les bonnes pratiques avec d'autres ménages
        """)

else:
    # Message d'accueil
    st.info("👈 **Bienvenue !** Remplissez les caractéristiques du ménage dans le panneau de gauche et cliquez sur **'Prédire'** pour obtenir les résultats.")
    
    # Présentation des modèles
    st.markdown("---")
    st.subheader("📊 Modèles utilisés")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📈 Fréquence d'indemnisation**
        - Modèle : **Binomial Négatif**
        - AIC : 549,54
        - Meilleur modèle pour la fréquence
        """)
    
    with col2:
        st.markdown("""
        **💰 Coût moyen d'indemnisation**
        - Modèle : **Log-Gamma**
        - AIC : 2046,67
        - Meilleur modèle pour le coût
        """)
    
    with col3:
        st.markdown("""
        **⚠️ Vulnérabilité**
        - Modèle : **Régression Logistique**
        - Précision : 66,25%
        - AUC : 0,649
        """)

# ============================================================================
# PIED DE PAGE
# ============================================================================

st.markdown("---")
st.caption("""
**Projet d'Économétrie et d'Actuariat** | UADB | Année 2024-2025

*Les prédictions sont basées sur des modèles statistiques entraînés sur des données de l'enquête ERASAN 2024.*
""")