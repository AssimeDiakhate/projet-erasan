import streamlit as st

st.set_page_config(page_title="Prédiction des Indemnisations", page_icon="🌾", layout="wide")

st.title("🌾 Prédiction des Indemnisations Agricoles")
st.markdown("---")

st.success("✅ Application déployée avec succès !")

st.info("""
**📌 Version de démonstration**

Les modèles sont en cours d'installation.
Cette interface vous permet de simuler des prédictions.
""")

# Interface utilisateur
with st.sidebar:
    st.header("📋 Caractéristiques du ménage")
    
    taille = st.number_input("Taille du ménage", min_value=1, max_value=50, value=15)
    age = st.number_input("Âge du chef", min_value=18, max_value=100, value=45)
    sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])
    revenu = st.number_input("Revenu (FCFA)", value=1000000, step=100000)
    depalim = st.number_input("Dépenses alimentaires", value=250000, step=10000)
    sca = st.number_input("SCA", min_value=0, max_value=120, value=60)
    sci = st.number_input("SCI", min_value=0, max_value=50, value=8)
    inondation = st.selectbox("Inondation", ["Non", "Oui"])
    pluies_insuf = st.selectbox("Pluies insuffisantes", ["Non", "Oui"])
    pluies_hs = st.selectbox("Pluies hors saison", ["Non", "Oui"])

if st.sidebar.button("🔮 Simuler", type="primary"):
    import random
    
    # Simulation de résultats
    freq = round(5 + random.random() * 10, 1)
    cout = round(100000 + random.random() * 200000, 0)
    proba = round(0.3 + random.random() * 0.5, 2)
    classe = "Vulnérable" if proba >= 0.5 else "Non vulnérable"
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Fréquence", f"{freq:.1f}")
    col2.metric("💰 Coût moyen", f"{cout:,.0f} FCFA")
    col3.metric("⚠️ Vulnérabilité", classe, f"Prob: {proba*100:.1f}%")
    
    st.caption("ℹ️ Version de démonstration - Modèles en cours d'installation")

st.markdown("---")
st.caption("Projet d'Économétrie et d'Actuariat - UADB")
