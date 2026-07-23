import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Prédiction des Indemnisations Agricoles",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Prédiction des Indemnisations Agricoles")
st.markdown("*Application de démonstration*")
st.markdown("---")

st.info("""
**📌 Application en cours de déploiement**

Les modèles sont en cours d'installation. 
Cette version de démonstration montre l'interface utilisateur.
""")

# Interface utilisateur
with st.sidebar:
    st.header("📋 Caractéristiques du ménage")
    
    st.subheader("👨‍👩‍👧‍👦 Démographie")
    taille = st.number_input("Taille du ménage", min_value=1, max_value=50, value=15)
    age = st.number_input("Âge du chef", min_value=18, max_value=100, value=45)
    sexe = st.selectbox("Sexe du chef", ["Masculin", "Féminin"])
    
    st.subheader("💰 Économie")
    revenu = st.number_input("Revenu (FCFA)", min_value=100000, max_value=50000000, value=1000000, step=100000)
    depalim = st.number_input("Dépenses alimentaires (FCFA)", min_value=50000, max_value=1000000, value=250000, step=10000)
    
    st.subheader("🍽️ Alimentation")
    sca = st.number_input("Score de consommation (SCA)", min_value=0, max_value=120, value=60)
    sci = st.number_input("Stratégies de survie (SCI)", min_value=0, max_value=50, value=8)
    
    st.subheader("🌦️ Chocs climatiques")
    inondation = st.selectbox("Inondation", ["Non", "Oui"])
    pluies_insuf = st.selectbox("Pluies insuffisantes", ["Non", "Oui"])
    pluies_hs = st.selectbox("Pluies hors saison", ["Non", "Oui"])

if st.sidebar.button("🔮 Simuler", type="primary"):
    # Simuler des résultats
    freq = 8 + np.random.rand() * 5
    cout = 150000 + np.random.rand() * 100000
    proba = 0.4 + np.random.rand() * 0.4
    classe = "Vulnérable" if proba >= 0.5 else "Non vulnérable"
    
    st.markdown("## 📊 Résultats (Simulation)")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Fréquence", f"{freq:.1f}")
    
    with col2:
        st.metric("💰 Coût moyen", f"{cout:,.0f} FCFA")
    
    with col3:
        st.metric("⚠️ Vulnérabilité", classe, f"Prob: {proba*100:.1f}%")
    
    st.info("""
    **ℹ️ Version de démonstration**
    
    Les modèles seront chargés prochainement.
    """)

st.markdown("---")
st.caption("Projet d'Économétrie et d'Actuariat - UADB")
