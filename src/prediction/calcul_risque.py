"""
src/prediction/calcul_risque.py — Pipeline de scoring batch
OCP Safi — Maintenance Prédictive — AI4I 2020

Ce script calcule les scores de risque de panne pour toutes les machines
du jeu de données nettoyé, puis insère les prédictions dans PostgreSQL.

Étapes :
    1. Chargement des données nettoyées depuis PostgreSQL
    2. Chargement du modèle XGBoost entraîné
    3. Récupération de l'identifiant du dernier run d'entraînement
    4. Calcul des probabilités et attribution des niveaux de risque
    5. Insertion des prédictions dans la table predictions
    6. Affichage du rapport de scoring
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import psycopg2
from psycopg2.extras import execute_values

# ── Configuration du chemin d'importation du module de configuration ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from configuration.parametres import (
    CONFIG_BDD, VARIABLES_EXPLICATIVES, SEUILS_RISQUE,
    CHEMIN_MODELE, REPERTOIRE_JOURNAUX,
    FORMAT_LOG, FORMAT_DATE_LOG,
)

# ── Initialisation du journal d'exécution ─────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format=FORMAT_LOG,
    datefmt=FORMAT_DATE_LOG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            REPERTOIRE_JOURNAUX / f"scoring_{datetime.now():%Y%m%d_%H%M%S}.log",
            encoding="utf-8",
        ),
    ],
)
journal = logging.getLogger("SCORING")


# ══════════════════════════════════════════════════════════════
# ÉTAPE 1 — Chargement des données nettoyées
# ══════════════════════════════════════════════════════════════
def charger_donnees_nettoyees() -> pd.DataFrame:
    """
    Charge l'ensemble des données nettoyées depuis PostgreSQL
    (table cleaned_sensor_readings), ordonnées par identifiant machine.
    """
    journal.info("Chargement de cleaned_sensor_readings depuis PostgreSQL...")
    connexion = psycopg2.connect(**CONFIG_BDD)
    requete = """
        SELECT
            udi, product_id, type,
            air_temperature_k, process_temperature_k,
            rotational_speed_rpm, torque_nm, tool_wear_min,
            type_encoded, temp_diff, power,
            machine_failure
        FROM cleaned_sensor_readings
        ORDER BY udi;
    """
    df = pd.read_sql(requete, connexion)
    connexion.close()
    journal.info("  Lignes chargées : %d", len(df))
    return df


# ══════════════════════════════════════════════════════════════
# ÉTAPE 2 — Chargement du modèle entraîné
# ══════════════════════════════════════════════════════════════
def charger_modele():
    """
    Charge le modèle XGBoost sauvegardé depuis le répertoire modeles/.
    Interrompt l'exécution si le fichier est introuvable.
    """
    if not CHEMIN_MODELE.exists():
        journal.error("Modèle introuvable : %s", CHEMIN_MODELE)
        journal.error("  → Exécuter d'abord : python src/entrainement/entrainer_modele.py")
        sys.exit(1)
    modele = joblib.load(CHEMIN_MODELE)
    journal.info("Modèle chargé : %s", CHEMIN_MODELE)
    return modele


# ══════════════════════════════════════════════════════════════
# ÉTAPE 3 — Récupération du dernier run d'entraînement
# ══════════════════════════════════════════════════════════════
def obtenir_dernier_run_id() -> str:
    """
    Récupère l'identifiant (UUID) du run d'entraînement le plus récent.
    Interrompt l'exécution si aucun run n'existe en base.
    """
    connexion = psycopg2.connect(**CONFIG_BDD)
    curseur   = connexion.cursor()
    curseur.execute("""
        SELECT run_id
        FROM model_runs
        ORDER BY run_date DESC
        LIMIT 1;
    """)
    ligne = curseur.fetchone()
    curseur.close()
    connexion.close()

    if not ligne:
        journal.error("Aucun run trouvé dans model_runs.")
        journal.error("  → Exécuter d'abord : python src/entrainement/entrainer_modele.py")
        sys.exit(1)

    id_run = str(ligne[0])
    journal.info("  Run ID utilisé : %s", id_run)
    return id_run


# ══════════════════════════════════════════════════════════════
# ÉTAPE 4a — Attribution du niveau de risque
# ══════════════════════════════════════════════════════════════
def attribuer_niveau_risque(probabilite: float) -> str:
    """
    Attribue un niveau de risque textuel selon les seuils configurés
    dans configuration/parametres.py (SEUILS_RISQUE).

    Retourne : 'Low', 'Medium' ou 'High'
    """
    if probabilite < SEUILS_RISQUE["faible"]:
        return "Low"
    elif probabilite < SEUILS_RISQUE["moyen"]:
        return "Medium"
    else:
        return "High"


# ══════════════════════════════════════════════════════════════
# ÉTAPE 4b — Calcul des probabilités de panne
# ══════════════════════════════════════════════════════════════
def calculer_predictions(df: pd.DataFrame, modele) -> pd.DataFrame:
    """
    Applique le modèle XGBoost sur les variables explicatives
    et ajoute les colonnes risk_score et risk_level au DataFrame.
    """
    journal.info("Calcul des probabilités de panne...")
    X = df[VARIABLES_EXPLICATIVES].values
    probabilites = modele.predict_proba(X)[:, 1]

    df = df.copy()
    df["risk_score"] = probabilites.round(4)
    df["risk_level"] = [attribuer_niveau_risque(p) for p in probabilites]

    # Affichage de la distribution des niveaux de risque
    distribution = df["risk_level"].value_counts()
    journal.info("  Distribution des risques :")
    for niveau in ["Low", "Medium", "High"]:
        nb = distribution.get(niveau, 0)
        journal.info("    %-8s : %4d (%.1f%%)", niveau, nb, 100 * nb / len(df))

    return df


# ══════════════════════════════════════════════════════════════
# ÉTAPE 5 — Insertion des prédictions en base
# ══════════════════════════════════════════════════════════════
def inserer_predictions(df: pd.DataFrame, id_run: str) -> int:
    """
    Insère les prédictions calculées dans la table predictions.
    Supprime d'abord les prédictions du même run pour éviter les doublons.

    Retourne le nombre de prédictions insérées.
    """
    journal.info("Insertion dans la table predictions...")
    connexion = psycopg2.connect(**CONFIG_BDD)
    curseur   = connexion.cursor()

    # Suppression des prédictions existantes pour ce run (re-scoring propre)
    curseur.execute("DELETE FROM predictions WHERE run_id = %s;", (id_run,))

    colonnes_pred = [
        "run_id", "udi", "product_id", "type",
        "risk_score", "risk_level",
        "air_temperature_k", "process_temperature_k",
        "rotational_speed_rpm", "torque_nm", "tool_wear_min",
        "actual_failure",
    ]

    # Construction des lignes à insérer
    lignes = []
    for _, ligne in df.iterrows():
        lignes.append((
            id_run,
            int(ligne["udi"]),
            ligne["product_id"],
            ligne["type"],
            float(ligne["risk_score"]),
            ligne["risk_level"],
            float(ligne["air_temperature_k"]),
            float(ligne["process_temperature_k"]),
            int(ligne["rotational_speed_rpm"]),
            float(ligne["torque_nm"]),
            int(ligne["tool_wear_min"]),
            int(ligne["machine_failure"]),
        ))

    execute_values(
        curseur,
        f"INSERT INTO predictions ({', '.join(colonnes_pred)}) VALUES %s",
        lignes,
        page_size=500,
    )
    connexion.commit()
    curseur.close()
    connexion.close()

    journal.info("  → %d prédictions insérées", len(lignes))
    return len(lignes)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 6 — Rapport de scoring
# ══════════════════════════════════════════════════════════════
def afficher_rapport_scoring(df: pd.DataFrame) -> None:
    """
    Affiche un rapport de scoring :
      - Top 10 des machines à risque le plus élevé
      - ROC-AUC du scoring par rapport aux vraies pannes
    """
    from sklearn.metrics import roc_auc_score

    journal.info("── Rapport de scoring ───────────────────────────────")

    # Top 10 des machines présentant le risque le plus élevé
    top10 = df.nlargest(10, "risk_score")[[
        "udi", "product_id", "type",
        "risk_score", "risk_level",
        "tool_wear_min", "machine_failure",
    ]]
    journal.info("  Top 10 machines à risque élevé :\n%s",
                 top10.to_string(index=False))

    # Calcul du ROC-AUC si des pannes réelles existent dans le jeu de données
    if df["machine_failure"].sum() > 0:
        auc = roc_auc_score(df["machine_failure"], df["risk_score"])
        journal.info("  ROC-AUC (scoring vs réel) : %.4f", auc)


# ══════════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ══════════════════════════════════════════════════════════════
def main():
    journal.info("═" * 55)
    journal.info("  SCORING — Maintenance Prédictive OCP Safi")
    journal.info("═" * 55)

    # Chargement des données, du modèle et de l'identifiant du run
    df        = charger_donnees_nettoyees()
    modele    = charger_modele()
    id_run    = obtenir_dernier_run_id()

    # Calcul des prédictions et insertion en base
    df_score  = calculer_predictions(df, modele)
    nb_pred   = inserer_predictions(df_score, id_run)

    # Rapport
    afficher_rapport_scoring(df_score)

    # Résumé final
    journal.info("═" * 55)
    journal.info("  SCORING TERMINÉ")
    journal.info("  Prédictions insérées : %d", nb_pred)
    journal.info("  Risque Élevé  (High)   : %d",
                 (df_score["risk_level"] == "High").sum())
    journal.info("  Risque Moyen  (Medium) : %d",
                 (df_score["risk_level"] == "Medium").sum())
    journal.info("  Risque Faible (Low)    : %d",
                 (df_score["risk_level"] == "Low").sum())
    journal.info("  → Consulter : SELECT * FROM v_global_kpi;")
    journal.info("═" * 55)


if __name__ == "__main__":
    main()
