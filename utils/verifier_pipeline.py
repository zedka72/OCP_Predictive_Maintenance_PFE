"""
utils/verifier_pipeline.py — Vérification rapide de la base de données
OCP Safi — Maintenance Prédictive — AI4I 2020

Ce script interroge la base PostgreSQL et affiche un résumé des résultats
du pipeline : dernier run d'entraînement, distribution des prédictions,
KPIs globaux et machines à risque élevé.

Usage :
    python utils/verifier_pipeline.py
"""

import sys
from pathlib import Path

import pandas as pd
import psycopg2

# ── Configuration du chemin d'importation du module de configuration ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from configuration.parametres import CONFIG_BDD


def obtenir_connexion():
    """Retourne une connexion active à PostgreSQL."""
    return psycopg2.connect(**CONFIG_BDD)


def verifier_dernier_run(connexion) -> None:
    """Affiche les métriques du dernier run d'entraînement."""
    print("=" * 55)
    print("  DERNIER RUN D'ENTRAÎNEMENT (model_runs)")
    print("=" * 55)
    df = pd.read_sql(
        """
        SELECT model_name, roc_auc, f1_score, recall, n_train, n_test
        FROM model_runs
        ORDER BY run_date DESC
        LIMIT 1
        """,
        connexion,
    )
    if df.empty:
        print("  Aucun run trouvé. Exécuter d'abord entrainer_modele.py")
    else:
        print(df.to_string(index=False))


def verifier_distribution_risque(connexion) -> None:
    """Affiche la distribution des niveaux de risque dans les prédictions."""
    print()
    print("=" * 55)
    print("  DISTRIBUTION DES PRÉDICTIONS (predictions)")
    print("=" * 55)
    df = pd.read_sql(
        """
        SELECT
            risk_level                              AS niveau_risque,
            COUNT(pred_id)                          AS nb_predictions,
            ROUND(AVG(risk_score)::NUMERIC, 4)      AS score_moyen
        FROM predictions
        GROUP BY risk_level
        ORDER BY risk_level
        """,
        connexion,
    )
    if df.empty:
        print("  Aucune prédiction. Exécuter d'abord calcul_risque.py")
    else:
        print(df.to_string(index=False))


def verifier_kpi_globaux(connexion) -> None:
    """Affiche les KPIs globaux depuis la vue v_global_kpi."""
    print()
    print("=" * 55)
    print("  KPIs GLOBAUX (vue v_global_kpi)")
    print("=" * 55)
    df = pd.read_sql(
        """
        SELECT
            model_name, total_scored,
            nb_high, nb_medium, nb_low,
            avg_risk_score, pct_high_risk,
            roc_auc
        FROM v_global_kpi
        """,
        connexion,
    )
    if df.empty:
        print("  Vue vide. Vérifier que le pipeline complet a été exécuté.")
    else:
        print(df.to_string(index=False))


def verifier_machines_risque_eleve(connexion) -> None:
    """Affiche le top 5 des machines à risque élevé."""
    print()
    print("=" * 55)
    print("  TOP 5 MACHINES À RISQUE ÉLEVÉ (vue v_high_risk_machines)")
    print("=" * 55)
    df = pd.read_sql(
        """
        SELECT
            udi, product_id, type,
            risk_score, tool_wear_min,
            actual_failure
        FROM v_high_risk_machines
        LIMIT 5
        """,
        connexion,
    )
    if df.empty:
        print("  Aucune machine à risque élevé trouvée.")
    else:
        print(df.to_string(index=False))


def main():
    """Exécute toutes les vérifications du pipeline."""
    print("═" * 55)
    print("  VÉRIFICATION DU PIPELINE — OCP Safi")
    print("═" * 55)

    try:
        connexion = obtenir_connexion()
    except Exception as erreur:
        print(f"  ✗ Connexion PostgreSQL impossible : {erreur}")
        print("    → Vérifier que le service PostgreSQL est actif")
        sys.exit(1)

    try:
        verifier_dernier_run(connexion)
        verifier_distribution_risque(connexion)
        verifier_kpi_globaux(connexion)
        verifier_machines_risque_eleve(connexion)
    finally:
        connexion.close()

    print()
    print("═" * 55)
    print("  ✅  VÉRIFICATION TERMINÉE")
    print("═" * 55)


if __name__ == "__main__":
    main()
