"""
apercu_dataset.py — Affiche un apercu du dataset AI4I 2020
Executer : python apercu_dataset.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd

CHEMIN_CSV = "donnees/brutes/ai4i2020.csv"

df = pd.read_csv(CHEMIN_CSV)

print("=" * 60)
print(f"Dataset : {CHEMIN_CSV}")
print(f"Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")
print("=" * 60)

print("\n── 10 premières lignes ──")
print(df.head(10).to_string())

print("\n── Statistiques descriptives ──")
print(df.describe().round(3).to_string())

print("\n── Répartition Machine Failure ──")
print(df["Machine failure"].value_counts())
print(f"Taux de panne : {df['Machine failure'].mean()*100:.2f}%")
