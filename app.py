import streamlit as st
import pickle
import statsmodels.api as sm
import pandas as pd
import numpy as np

st.set_page_config(page_title="Prédiction des Indemnisations", page_icon="🌾", layout="wide")

st.title("🌾 Prédiction des Indemnisations Agricoles")

@st.cache_resource
def charger_modeles():
    modeles = {}
    try:
        with open('modeles/model_binomial_negatif.pkl', 'rb') as f:
            modeles['binomial_negatif'] = pickle.load(f)
    except:
        modeles['binomial_negatif'] = None
    try:
        with open('modeles/model_log_gamma.pkl', 'rb') as f:
            modeles['log_gamma'] = pickle.load(f)
    except:
        modeles['log_gamma'] = None
    try:
        with open('modeles/model_regression_logistique.pkl', 'rb') as f:
            modeles['regression_logistique'] = pickle.load(f)
    except:
        modeles['regression_logistique'] = None
    return modeles

modeles = charger_modeles()

# Interface utilisateur
with st.sidebar:
    st.header("📋 Caractéristiques du ménage")
    taille = st.number_input("Taille", min_value=1, max_value=50, value=15)
    age = st.number_input("Âge", min_value=18, max_value=100, value=45)
    sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])
    revenu = st.number_input("Revenu (FCFA)", value=1000000)
    depalim = st.number_input("Dépenses alimentaires", value=250000)
    sca = st.number_input("SCA", min_value=0, max_value=120, value=60)
    sci = st.number_input("SCI", min_value=0, max_value=50, value=8)
    inondation = st.selectbox("Inondation", ["Non", "Oui"])
    pluies_insuf = st.selectbox("Pluies insuffisantes", ["Non", "Oui"])
    pluies_hs = st.selectbox("Pluies hors saison", ["Non", "Oui"])

# Fonctions de prédiction
def predict_frequence(model, X_new):
    required_cols = ['taille_numeric', 'age_numeric', 'revenu', 'sca', 'depalim',
                     'Inondation', 'pluies_insuffisantes', 'pluies_hors_saison', 'sexe_encoded']
    for col in required_cols:
        if col not in X_new.columns:
            X_new[col] = 0
    X_pred = X_new[required_cols].fillna(0)
    X_pred = sm.add_constant(X_pred)
    return float(model.predict(X_pred)[0])

def predict_cout(model, X_new):
    required_cols = ['taille_numeric', 'age_numeric', 'revenu', 'depalim', 'sca', 'sci',
                     'Inondation', 'pluies_insuffisantes', 'pluies_hors_saison', 'sexe_encoded']
    for col in required_cols:
        if col not in X_new.columns:
            X_new[col] = 0
    X_pred = X_new[required_cols].fillna(0)
    X_pred = sm.add_constant(X_pred)
    return float(model.predict(X_pred)[0] - 1)

def predict_vulnerabilite(model, X_new):
    required_cols = ['Inondation', 'pluies_insuffisantes', 'pluies_hors_saison',
                     'sexe_encoded', 'taille_numeric', 'age_numeric']
    for col in required_cols:
        if col not in X_new.columns:
            X_new[col] = 0
    X_pred = X_new[required_cols].fillna(0)
    X_pred = sm.add_constant(X_pred)
    proba = float(model.predict(X_pred)[0])
    return proba, "Vulnérable" if proba >= 0.5 else "Non vulnérable"

if st.sidebar.button("🔮 Prédire", type="primary"):
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
    
    if modeles['binomial_negatif'] and modeles['log_gamma'] and modeles['regression_logistique']:
        freq = predict_frequence(modeles['binomial_negatif'], data)
        cout = predict_cout(modeles['log_gamma'], data)
        proba, classe = predict_vulnerabilite(modeles['regression_logistique'], data)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📈 Fréquence", f"{freq:.1f}")
        col2.metric("💰 Coût moyen", f"{cout:,.0f} FCFA")
        col3.metric("⚠️ Vulnérabilité", classe, f"Prob: {proba*100:.1f}%")
    else:
        st.error("❌ Modèles non disponibles")
        st.info("ℹ️ Version de démonstration avec simulation")
        # Simulation si les modèles ne sont pas chargés
        import random
        freq = round(5 + random.random() * 10, 1)
        cout = round(100000 + random.random() * 200000, 0)
        proba = round(0.3 + random.random() * 0.5, 2)
        classe = "Vulnérable" if proba >= 0.5 else "Non vulnérable"
        col1, col2, col3 = st.columns(3)
        col1.metric("📈 Fréquence", f"{freq:.1f}")
        col2.metric("💰 Coût moyen", f"{cout:,.0f} FCFA")
        col3.metric("⚠️ Vulnérabilité", classe, f"Prob: {proba*100:.1f}%")

st.caption("Projet d'Économétrie et d'Actuariat - UADB")
