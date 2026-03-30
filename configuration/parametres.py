"""
configuration/parametres.py — Configuration centrale du projet PFE
OCP Safi — Maintenance Prédictive — AI4I 2020

Ce fichier centralise tous les paramètres du projet :
  - Chemins des répertoires et fichiers
  - Connexion PostgreSQL
  - Paramètres du modèle XGBoost
  - Variables explicatives et variable cible
  - Seuils de classification du risque
  - Format de journalisation
"""

import os
from pathlib import Path

# ══════════════════════════════════════════════════════════════
# CHEMINS — Répertoires principaux
# ══════════════════════════════════════════════════════════════

# Répertoire racine du projet (deux niveaux au-dessus de ce fichier)
REPERTOIRE_BASE      = Path(__file__).resolve().parent.parent

# Répertoires de données
REPERTOIRE_DONNEES   = REPERTOIRE_BASE / "donnees"
REPERTOIRE_BRUT      = REPERTOIRE_DONNEES / "brutes"
REPERTOIRE_TRAITE    = REPERTOIRE_DONNEES / "traitees"

# Répertoire des modèles entraînés
REPERTOIRE_MODELES   = REPERTOIRE_BASE / "modeles"

# Répertoire des journaux d'exécution
REPERTOIRE_JOURNAUX  = REPERTOIRE_BASE / "journaux"

# Création automatique des répertoires manquants au démarrage
for _dossier in [REPERTOIRE_BRUT, REPERTOIRE_TRAITE, REPERTOIRE_MODELES, REPERTOIRE_JOURNAUX]:
    _dossier.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════
# FICHIERS — Chemins des fichiers de données et modèles
# ══════════════════════════════════════════════════════════════

# Données brutes (CSV original AI4I 2020)
CSV_BRUT         = REPERTOIRE_BRUT    / "ai4i2020.csv"

# Données nettoyées et enrichies (features engineerées)
CSV_PROPRE       = REPERTOIRE_TRAITE  / "ai4i2020_propre.csv"

# Modèle XGBoost entraîné
CHEMIN_MODELE    = REPERTOIRE_MODELES / "xgb_maintenance.joblib"

# Normaliseur StandardScaler (utilisé pour la régression logistique)
CHEMIN_NORMALISEUR = REPERTOIRE_MODELES / "normaliseur.joblib"


# ══════════════════════════════════════════════════════════════
# BASE DE DONNÉES — Configuration PostgreSQL
# Les valeurs sont lues depuis les variables d'environnement
# si disponibles, sinon les valeurs par défaut sont utilisées.
# ══════════════════════════════════════════════════════════════

CONFIG_BDD = {
    "host":     os.getenv("PG_HOTE",      "localhost"),
    "port":     int(os.getenv("PG_PORT",  "5432")),
    "dbname":   os.getenv("PG_BASE",      "maintenance_pfe"),
    "user":     os.getenv("PG_UTILISATEUR", "pfe_user"),
    "password": os.getenv("PG_MOT_PASSE", "pfe_password123"),
}


# ══════════════════════════════════════════════════════════════
# MODÈLE — Variables explicatives et variable cible
# ══════════════════════════════════════════════════════════════

# Colonnes utilisées comme entrées du modèle XGBoost
VARIABLES_EXPLICATIVES = [
    "air_temperature_k",        # Température de l'air (en Kelvin)
    "process_temperature_k",    # Température du processus (en Kelvin)
    "rotational_speed_rpm",     # Vitesse de rotation (en tours/min)
    "torque_nm",                # Couple (en Newton-mètre)
    "tool_wear_min",            # Usure de l'outil (en minutes)
    "temp_diff",                # Écart thermique (process - air), feature calculée
    "power",                    # Puissance (rpm × couple), feature calculée
    "type_encoded",             # Type machine encodé : L=0, M=1, H=2
]

# Colonne cible : 1 = panne, 0 = pas de panne
VARIABLE_CIBLE = "machine_failure"


# ══════════════════════════════════════════════════════════════
# SEUILS DE RISQUE — Classification probabiliste
# Ces seuils définissent les bornes des 3 niveaux de risque.
# ══════════════════════════════════════════════════════════════

SEUILS_RISQUE = {
    "faible":  0.30,   # p < 0.30           → Risque Faible  (Low)
    "moyen":   0.60,   # 0.30 ≤ p < 0.60   → Risque Moyen   (Medium)
    # p ≥ 0.60         → Risque Élevé  (High)
}


# ══════════════════════════════════════════════════════════════
# HYPERPARAMÈTRES XGBOOST
# Configurés pour le déséquilibre de classe (339 pannes / 10000)
# ══════════════════════════════════════════════════════════════

PARAMS_XGB = {
    "n_estimators":     300,      # Nombre d'arbres de décision
    "max_depth":        6,         # Profondeur maximale d'un arbre
    "learning_rate":    0.05,      # Taux d'apprentissage
    "subsample":        0.8,       # Fraction des échantillons par arbre
    "colsample_bytree": 0.8,       # Fraction des colonnes par arbre
    "reg_alpha":        0.1,       # Régularisation L1
    "reg_lambda":       1.0,       # Régularisation L2
    "min_child_weight": 5,         # Poids minimal d'une feuille
    "scale_pos_weight": 29,        # Ratio déséquilibre ≈ (10000-339)/339
    "tree_method":      "hist",    # Méthode rapide pour grandes données
    "n_jobs":           -1,        # Utiliser tous les cœurs CPU
    "eval_metric":      "auc",     # Métrique d'évaluation : aire sous la courbe ROC
    "early_stopping_rounds": 30,   # Arrêt anticipé si pas d'amélioration
    "random_state":     42,        # Graine aléatoire pour reproductibilité
    "verbosity":        1,         # Niveau de verbosité XGBoost
}


# ══════════════════════════════════════════════════════════════
# JOURNALISATION — Format des logs
# ══════════════════════════════════════════════════════════════

FORMAT_LOG      = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
FORMAT_DATE_LOG = "%Y-%m-%d %H:%M:%S"
