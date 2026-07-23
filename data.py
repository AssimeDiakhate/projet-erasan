import pandas as pd
import numpy as np

def get_sample_data():
    return pd.DataFrame({
        'taille_numeric': [15, 20, 10],
        'age_numeric': [45, 55, 35],
        'revenu': [1000000, 2000000, 500000],
        'sca': [60, 70, 50],
        'depalim': [250000, 300000, 200000],
        'sci': [8, 5, 12],
        'Inondation': [1, 0, 1],
        'pluies_insuffisantes': [0, 1, 0],
        'pluies_hors_saison': [1, 0, 1],
        'sexe_encoded': [0, 0, 1]
    })
