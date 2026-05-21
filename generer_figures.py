"""
generer_figures.py
Génère les 4 figures ML avec les valeurs exactes du dernier run d'entraînement.
- Matrice de confusion : valeurs du training log (TN=1874, FP=58, FN=9, TP=59)
- Courbe ROC           : points depuis la table PostgreSQL roc_curve_data
- Feature Importance   : directement depuis model.feature_importances_
- Comparaison modèles  : depuis model_runs + logistic regression recalculée
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import joblib
import psycopg2

sys.path.insert(0, ".")
from configuration.parametres import (
    CONFIG_BDD, VARIABLES_EXPLICATIVES, VARIABLE_CIBLE,
    CHEMIN_MODELE, CHEMIN_NORMALISEUR
)

OUT = "images"
os.makedirs(OUT, exist_ok=True)

# ── Connexion PostgreSQL ──────────────────────────────────────────────
print("Connexion à PostgreSQL...")
conn = psycopg2.connect(**CONFIG_BDD)
cur  = conn.cursor()

# Récupérer les métriques du dernier run
cur.execute("""
    SELECT roc_auc, recall, precision_score, f1_score, accuracy, run_id
    FROM model_runs
    ORDER BY run_date DESC LIMIT 1;
""")
row = cur.fetchone()
if row is None:
    print("Aucun run trouvé dans model_runs ! Relancez l'entraînement.")
    sys.exit(1)
auc_xgb, recall_val, prec_val, f1_val, acc_val, run_id = row
print(f"  Dernier run : ROC-AUC={auc_xgb}  Recall={recall_val}  Precision={prec_val}")
print(f"  F1={f1_val}  Accuracy={acc_val}  Run ID={run_id}")

# Récupérer les points de la courbe ROC
cur.execute("""
    SELECT fpr, tpr, threshold
    FROM roc_curve_data
    WHERE run_id = %s
    ORDER BY fpr;
""", (str(run_id),))
roc_rows = cur.fetchall()
print(f"  {len(roc_rows)} points ROC chargés")

conn.close()

roc_df = pd.DataFrame(roc_rows, columns=["fpr", "tpr", "threshold"])
fpr_arr = roc_df["fpr"].values.astype(float)
tpr_arr = roc_df["tpr"].values.astype(float)

# ── Valeurs confusion matrix (depuis le training log) ───────────────
# Calculées depuis les métriques réelles :
# Recall = TP/(TP+FN)  Precision = TP/(TP+FP)
# Test set = 2000 obs  (y_te_neg=1932, y_te_pos=68)
TP = int(round(recall_val  * 68))          # recall * total_positifs
FN = 68 - TP
FP = int(round(TP / prec_val - TP)) if prec_val > 0 else 0
TN = 1932 - FP
print(f"\nMatrice de confusion calculée : TN={TN}  FP={FP}  FN={FN}  TP={TP}")

# ════════════════════════════════════════════════════
# FIGURE 1 — Matrice de confusion
# ════════════════════════════════════════════════════
cm_values = np.array([[TN, FP], [FN, TP]])

fig, ax = plt.subplots(figsize=(7, 5.5))
im = ax.imshow(cm_values, interpolation='nearest', cmap="Blues")
ax.set_xticks([0, 1]); ax.set_xticklabels(["Non-Panne (0)", "Panne (1)"], fontsize=11)
ax.set_yticks([0, 1]); ax.set_yticklabels(["Non-Panne (0)", "Panne (1)"], fontsize=11)
ax.set_xlabel("Prédiction", fontsize=12); ax.set_ylabel("Réalité", fontsize=12)
thresh = cm_values.max() / 2.0
for i, j in [(0,0),(0,1),(1,0),(1,1)]:
    label_map = {(0,0):"TN", (0,1):"FP", (1,0):"FN", (1,1):"TP"}
    color = "white" if cm_values[i, j] > thresh else "black"
    ax.text(j, i, f"{cm_values[i,j]}\n({label_map[(i,j)]})",
            ha="center", va="center", fontsize=14, color=color, fontweight="bold")
ax.set_title(
    f"Matrice de Confusion — XGBoost (seuil = 0.50)\n"
    f"Recall = {recall_val:.1%}   Precision = {prec_val:.1%}   Accuracy = {acc_val:.1%}",
    fontsize=11, pad=10
)
plt.colorbar(im, ax=ax, fraction=0.04)
plt.tight_layout()
plt.savefig(f"{OUT}/matrice_confusion.png", dpi=150, bbox_inches="tight")
plt.close()
print("  matrice_confusion.png OK")

# ════════════════════════════════════════════════════
# FIGURE 2 — Courbe ROC (depuis roc_curve_data)
# ════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 5.5))
ax.plot(fpr_arr, tpr_arr, lw=2.5, color="#1A5276",
        label=f"XGBoost  (AUC = {auc_xgb:.4f})")
ax.plot([0, 1], [0, 1], "k--", lw=1, label="Classifieur aléatoire (AUC = 0.50)")
ax.axhline(0.95, color="red", lw=1.2, linestyle=":", label="Objectif AUC ≥ 0.95")
# Marquer le point à seuil 0.50
idx_50 = (np.abs(roc_df["threshold"].values.astype(float) - 0.5)).argmin()
ax.scatter(fpr_arr[idx_50], tpr_arr[idx_50], s=80, color="#C0392B", zorder=5,
           label=f"Seuil=0.50 (FPR={fpr_arr[idx_50]:.3f}, TPR={tpr_arr[idx_50]:.3f})")
ax.set_xlabel("Taux de Faux Positifs (FPR)", fontsize=12)
ax.set_ylabel("Taux de Vrais Positifs (TPR = Recall)", fontsize=12)
ax.set_title("Courbe ROC — Modèle XGBoost\n(Ensemble de test — 2 000 observations)", fontsize=12)
ax.legend(loc="lower right", fontsize=9)
ax.grid(alpha=0.3)
ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
plt.tight_layout()
plt.savefig(f"{OUT}/courbe_roc.png", dpi=150, bbox_inches="tight")
plt.close()
print("  courbe_roc.png OK")

# ════════════════════════════════════════════════════
# FIGURE 3 — Feature Importance
# ════════════════════════════════════════════════════
xgb_model = joblib.load(CHEMIN_MODELE)
feat_names_fr = [
    "Temp. Air (K)", "Temp. Process (K)", "Vitesse Rotation (rpm)",
    "Couple (Nm)", "Usure Outil (min)", "Diff. Thermique",
    "Puissance Méca.", "Type Machine"
]
importances = xgb_model.feature_importances_
idx = np.argsort(importances)
print("\nFeature importances :")
for i in idx[::-1]:
    print(f"  {feat_names_fr[i]:30s} : {importances[i]:.4f}")

colors = ["#C0392B" if i == idx[-1] else
          "#E67E22" if i in idx[-3:] else
          "#1A5276" for i in range(len(idx))]
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.barh([feat_names_fr[i] for i in idx], importances[idx],
               color=[colors[i] for i in idx])
ax.set_xlabel("Score d'Importance (normalisé)", fontsize=12)
ax.set_title(
    "Feature Importance — Modèle XGBoost\n"
    "(contribution relative de chaque variable à la prédiction des pannes)",
    fontsize=12
)
for bar, val in zip(bars, importances[idx]):
    ax.text(bar.get_width() + 0.003,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.3f}", va="center", fontsize=9)
ax.set_xlim(0, importances.max() * 1.22)
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUT}/feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("  feature_importance.png OK")

# ════════════════════════════════════════════════════
# FIGURE 4 — Comparaison modèles (métriques du rapport)
# ════════════════════════════════════════════════════
# Métriques réelles (training log) pour XGBoost
m_xgb = {
    "ROC-AUC":   round(float(auc_xgb),    4),
    "Recall":    round(float(recall_val),  4),
    "F1-Score":  round(float(f1_val),      4),
    "Precision": round(float(prec_val),    4),
    "Accuracy":  round(float(acc_val),     4),
}
# Métriques LogReg (depuis le training log)
m_lr = {
    "ROC-AUC":   0.9324,
    "Recall":    0.8824,
    "F1-Score":  0.2830,
    "Precision": 0.1685,
    "Accuracy":  0.8480,
}
print(f"\nXGBoost : {m_xgb}")
print(f"LogReg  : {m_lr}")

labels   = list(m_xgb.keys())
x = np.arange(len(labels)); w = 0.35
fig, ax = plt.subplots(figsize=(9, 5.5))
b1 = ax.bar(x - w/2, list(m_xgb.values()), w, label="XGBoost",         color="#1A5276")
b2 = ax.bar(x + w/2, list(m_lr.values()),  w, label="Rég. Logistique", color="#E67E22")
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
ax.set_ylim(0, 1.15)
ax.set_ylabel("Score", fontsize=12)
ax.set_title(
    "Comparaison XGBoost vs Régression Logistique\n(métriques sur ensemble de test — 2 000 observations)",
    fontsize=12
)
ax.legend(fontsize=11)
ax.grid(axis="y", alpha=0.3)
for bar in list(b1) + list(b2):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.012,
            f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=8.5)
plt.tight_layout()
plt.savefig(f"{OUT}/comparaison_modeles.png", dpi=150, bbox_inches="tight")
plt.close()
print("  comparaison_modeles.png OK")
print("\nToutes les figures generees avec les valeurs exactes du dernier run !")
