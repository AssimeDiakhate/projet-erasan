# 🌾 Prédiction des Indemnisations Agricoles

## Description
Application de prédiction des indemnisations agricoles basée sur les modèles économétriques et actuariels.

## Modèles utilisés
- **Fréquence** : Binomial Négatif (AIC = 549.54)
- **Coût** : Log-Gamma (AIC = 2046.67)  
- **Vulnérabilité** : Régression Logistique (Précision = 66.25%)

## Installation locale
```bash
pip install -r requirements.txt
streamlit run app.py