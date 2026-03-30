"""
src/entrainement/entrainer_modele.py — Pipeline d'entraînement du modèle
OCP Safi — Maintenance Prédictive — AI4I 2020

Ce script entraîne deux modèles sur le jeu de données AI4I 2020 :
  1. Régression Logistique (modèle de référence / baseline)
  2. XGBoostClassifier (modèle principal de production)

Étapes :
    1. Chargement des données nettoyées depuis PostgreSQL
    2. Préparation (split train/test, normalisation)
    3. Entraînement de la régression logistique (baseline)
    4. Entraînement du XGBoost (modèle principal)
    5. Analyse des seuils de risque
    6. Sauvegarde du run dans la table model_runs
"""

import sys
import json
import logging
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import psycopg2

from sklearn.linear_model    import LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing   import StandardScaler
from sklearn.metrics         import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
    confusion_matrix,
)
import xgboost as xgb

# Suppression des avertissements non critiques
warnings.filterwarnings("ignore")

# ── Configuration du chemin d'importation du module de configuration ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from configuration.parametres import (
    CONFIG_BDD, VARIABLES_EXPLICATIVES, VARIABLE_CIBLE, PARAMS_XGB,
    SEUILS_RISQUE, CHEMIN_MODELE, CHEMIN_NORMALISEUR,
    REPERTOIRE_JOURNAUX, FORMAT_LOG, FORMAT_DATE_LOG,
)

# ── Initialisation du journal d'exécution ─────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT_LOG,
    datefmt=FORMAT_DATE_LOG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            REPERTOIRE_JOURNAUX / f"entrainement_{datetime.now():%Y%m%d_%H%M%S}.log",
            encoding="utf-8",
        ),
    ],
)
journal = logging.getLogger("ENTRAINEMENT")


# ══════════════════════════════════════════════════════════════
# ÉTAPE 1 — Chargement des données nettoyées depuis PostgreSQL
# ══════════════════════════════════════════════════════════════
def charger_donnees() -> pd.DataFrame:
    """Charge les données nettoyées depuis la table cleaned_sensor_readings."""
    journal.info("Chargement depuis cleaned_sensor_readings...")
    connexion = psycopg2.connect(**CONFIG_BDD)
    requete = (
        f"SELECT {', '.join(VARIABLES_EXPLICATIVES + [VARIABLE_CIBLE])} "
        f"FROM cleaned_sensor_readings;"
    )
    df = pd.read_sql(requete, connexion)
    connexion.close()
    journal.info(
        "  Lignes chargées : %d | Pannes : %d (%.1f%%)",
        len(df), df[VARIABLE_CIBLE].sum(), df[VARIABLE_CIBLE].mean() * 100,
    )
    return df


# ══════════════════════════════════════════════════════════════
# ÉTAPE 2 — Préparation des données (split + normalisation)
# ══════════════════════════════════════════════════════════════
def preparer_donnees(df: pd.DataFrame):
    """
    Divise les données en ensembles d'entraînement et de test (80/20),
    stratifiés sur la variable cible.
    Crée également une version normalisée pour la régression logistique.

    Retourne :
        X_entrainement, X_test, y_entrainement, y_test,
        X_entrainement_norm, X_test_norm
    """
    X = df[VARIABLES_EXPLICATIVES].copy()
    y = df[VARIABLE_CIBLE].copy()

    X_entrainement, X_test, y_entrainement, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42,
    )
    journal.info("  Split — Entraînement : %d | Test : %d",
                 len(X_entrainement), len(X_test))
    journal.info("  Pannes dans l'ensemble test : %d / %d",
                 y_test.sum(), len(y_test))

    # Normalisation StandardScaler (nécessaire pour la régression logistique)
    normaliseur = StandardScaler()
    X_entrainement_norm = normaliseur.fit_transform(X_entrainement)
    X_test_norm         = normaliseur.transform(X_test)
    joblib.dump(normaliseur, CHEMIN_NORMALISEUR)
    journal.info("  Normaliseur sauvegardé : %s", CHEMIN_NORMALISEUR)

    return X_entrainement, X_test, y_entrainement, y_test, X_entrainement_norm, X_test_norm


# ══════════════════════════════════════════════════════════════
# ÉTAPE 3 — Calcul des métriques de performance
# ══════════════════════════════════════════════════════════════
def evaluer_modele(nom: str, y_test, y_pred, y_proba) -> dict:
    """
    Calcule et journalise les métriques de performance d'un modèle.

    Arguments :
        nom     : Nom du modèle (pour l'affichage dans les journaux)
        y_test  : Vraies étiquettes de l'ensemble test
        y_pred  : Prédictions binaires du modèle
        y_proba : Probabilités estimées de la classe positive

    Retourne un dictionnaire des métriques arrondies.
    """
    exactitude  = accuracy_score(y_test, y_pred)
    precision   = precision_score(y_test, y_pred, zero_division=0)
    rappel      = recall_score(y_test, y_pred, zero_division=0)
    score_f1    = f1_score(y_test, y_pred, zero_division=0)
    aire_roc    = roc_auc_score(y_test, y_proba)

    journal.info("── %s ──────────────────────────────", nom)
    journal.info("  Exactitude  : %.4f", exactitude)
    journal.info("  Précision   : %.4f", precision)
    journal.info("  Rappel      : %.4f", rappel)
    journal.info("  F1-Score    : %.4f", score_f1)
    journal.info("  ROC-AUC     : %.4f", aire_roc)
    journal.info("  Matrice de confusion :\n%s",
                 confusion_matrix(y_test, y_pred))
    journal.info("  Rapport de classification :\n%s",
                 classification_report(y_test, y_pred,
                                       target_names=["Pas de panne", "Panne"],
                                       zero_division=0))

    return {
        "exactitude": round(exactitude, 4),
        "precision":  round(precision, 4),
        "rappel":     round(rappel, 4),
        "f1":         round(score_f1, 4),
        "roc_auc":    round(aire_roc, 4),
    }


# ══════════════════════════════════════════════════════════════
# ÉTAPE 4 — Régression Logistique (modèle de référence)
# ══════════════════════════════════════════════════════════════
def entrainer_regression_logistique(X_entr_norm, y_entr, X_test_norm, y_test) -> dict:
    """
    Entraîne une régression logistique avec rééquilibrage des classes.
    Effectue une validation croisée (5 plis) pour estimer la stabilité.

    Retourne les métriques de performance.
    """
    journal.info("Entraînement Régression Logistique (modèle de référence)...")
    modele_lr = LogisticRegression(
        class_weight="balanced",  # Gestion du déséquilibre de classes
        max_iter=1000,
        random_state=42,
    )
    modele_lr.fit(X_entr_norm, y_entr)

    y_pred  = modele_lr.predict(X_test_norm)
    y_proba = modele_lr.predict_proba(X_test_norm)[:, 1]

    metriques = evaluer_modele("Régression Logistique", y_test, y_pred, y_proba)

    # Validation croisée stratifiée (5 plis) pour estimer la robustesse
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores_cv = cross_val_score(
        modele_lr, X_entr_norm, y_entr,
        cv=cv, scoring="roc_auc", n_jobs=-1,
    )
    journal.info("  Validation croisée ROC-AUC (5 plis) : %.4f ± %.4f",
                 scores_cv.mean(), scores_cv.std())

    return metriques


# ══════════════════════════════════════════════════════════════
# ÉTAPE 5 — XGBoost (modèle principal)
# ══════════════════════════════════════════════════════════════
def entrainer_xgboost(X_entr, y_entr, X_test, y_test) -> tuple:
    """
    Entraîne le modèle XGBoost principal avec arrêt anticipé.
    Sauvegarde le modèle entraîné dans le répertoire modeles/.

    Retourne :
        modele      : Le modèle XGBoost entraîné
        metriques   : Dictionnaire des performances
        y_proba     : Probabilités sur l'ensemble test
    """
    journal.info("Entraînement XGBoostClassifier (modèle principal)...")

    # Extraction du paramètre d'arrêt anticipé (géré séparément)
    params = PARAMS_XGB.copy()
    arret_anticipe = params.pop("early_stopping_rounds", 30)

    modele = xgb.XGBClassifier(**params, early_stopping_rounds=arret_anticipe)

    modele.fit(
        X_entr, y_entr,
        eval_set=[(X_test, y_test)],
        verbose=50,  # Afficher les métriques tous les 50 arbres
    )

    y_pred  = modele.predict(X_test)
    y_proba = modele.predict_proba(X_test)[:, 1]

    metriques = evaluer_modele("XGBoost", y_test, y_pred, y_proba)

    # Importance des variables explicatives (top 5)
    importances = pd.Series(
        modele.feature_importances_,
        index=VARIABLES_EXPLICATIVES,
    ).sort_values(ascending=False)
    journal.info("  Importance des variables (top 5) :\n%s",
                 importances.head(5).to_string())

    # Sauvegarde du modèle entraîné
    joblib.dump(modele, CHEMIN_MODELE)
    journal.info("  Modèle sauvegardé : %s", CHEMIN_MODELE)

    return modele, metriques, y_proba


# ══════════════════════════════════════════════════════════════
# ÉTAPE 6 — Analyse des seuils de classification du risque
# ══════════════════════════════════════════════════════════════
def analyser_seuils_risque(y_test, y_proba) -> dict:
    """
    Affiche la distribution des niveaux de risque selon les seuils configurés.
    Les seuils sont définis dans configuration/parametres.py : SEUILS_RISQUE.

    Retourne les seuils utilisés pour l'enregistrement du run.
    """
    seuil_faible = SEUILS_RISQUE["faible"]
    seuil_moyen  = SEUILS_RISQUE["moyen"]

    niveaux = pd.cut(
        y_proba,
        bins=[-np.inf, seuil_faible, seuil_moyen, np.inf],
        labels=["Faible", "Moyen", "Élevé"],
    )
    distribution = niveaux.value_counts().sort_index()
    journal.info("  Distribution des niveaux de risque (ensemble test) :")
    for niveau, nb in distribution.items():
        journal.info("    %-8s : %d (%.1f%%)",
                     niveau, nb, 100 * nb / len(y_proba))

    return {"seuil_faible": seuil_faible, "seuil_moyen": seuil_moyen}


# ══════════════════════════════════════════════════════════════
# ÉTAPE 7 — Enregistrement du run dans model_runs
# ══════════════════════════════════════════════════════════════
def sauvegarder_execution(metriques: dict, seuils: dict,
                          nb_entrainement: int, nb_test: int) -> str:
    """
    Insère les résultats du run d'entraînement dans la table model_runs.
    Retourne l'identifiant unique du run (UUID).
    """
    journal.info("Enregistrement du run dans model_runs...")
    connexion = psycopg2.connect(**CONFIG_BDD)
    curseur   = connexion.cursor()

    curseur.execute("""
        INSERT INTO model_runs (
            model_name, n_train, n_test,
            accuracy, precision_score, recall, f1_score, roc_auc,
            threshold_low, threshold_high,
            model_path, params
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING run_id;
    """, (
        "XGBoostClassifier",
        nb_entrainement, nb_test,
        metriques["exactitude"], metriques["precision"],
        metriques["rappel"],     metriques["f1"],
        metriques["roc_auc"],
        seuils["seuil_faible"],  seuils["seuil_moyen"],
        str(CHEMIN_MODELE),
        json.dumps(PARAMS_XGB),
    ))

    id_run = str(curseur.fetchone()[0])
    connexion.commit()
    curseur.close()
    connexion.close()

    journal.info("  Run enregistré — ID : %s", id_run)
    return id_run


# ══════════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ══════════════════════════════════════════════════════════════
def main():
    journal.info("═" * 55)
    journal.info("  ENTRAÎNEMENT — Maintenance Prédictive OCP Safi")
    journal.info("═" * 55)

    # Chargement et préparation des données
    df = charger_donnees()
    (X_entr, X_test, y_entr, y_test,
     X_entr_norm, X_test_norm) = preparer_donnees(df)

    # Modèle de référence : Régression Logistique
    journal.info("")
    journal.info("── RÉFÉRENCE : Régression Logistique ──────────────────")
    metriques_lr = entrainer_regression_logistique(
        X_entr_norm, y_entr, X_test_norm, y_test
    )

    # Modèle principal : XGBoost
    journal.info("")
    journal.info("── MODÈLE PRINCIPAL : XGBoost ──────────────────────────")
    modele, metriques_xgb, y_proba = entrainer_xgboost(
        X_entr, y_entr, X_test, y_test
    )

    # Analyse des seuils de risque
    journal.info("")
    journal.info("── SEUILS DE RISQUE ────────────────────────────────────")
    seuils = analyser_seuils_risque(y_test, y_proba)

    # Sauvegarde du run
    id_run = sauvegarder_execution(
        metriques_xgb, seuils,
        nb_entrainement=len(X_entr),
        nb_test=len(X_test),
    )

    # Résumé final
    journal.info("")
    journal.info("═" * 55)
    journal.info("  ENTRAÎNEMENT TERMINÉ")
    journal.info("  Modèle  : %s", CHEMIN_MODELE)
    journal.info("  Run ID  : %s", id_run)
    journal.info("  ROC-AUC : %.4f", metriques_xgb["roc_auc"])
    journal.info("  F1      : %.4f", metriques_xgb["f1"])
    journal.info("  Rappel  : %.4f", metriques_xgb["rappel"])
    journal.info("═" * 55)

    return id_run


if __name__ == "__main__":
    main()
