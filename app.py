print("Démarrage de l'application...")

import streamlit as st

print("Streamlit importé avec succès")

st.set_page_config(
    page_title="Test",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Application fonctionne !")

st.write("Si vous voyez ce message, le déploiement est réussi.")

# Test simple
if st.button("Cliquez ici"):
    st.success("Le bouton fonctionne !")
