"""
src/etl/pipeline_etl.py — Pipeline ETL : CSV → PostgreSQL
OCP Safi — Maintenance Prédictive — AI4I 2020

Ce script importe le jeu de données AI4I 2020 depuis un fichier CSV,
effectue le nettoyage et l'enrichissement des données (feature engineering),
puis insère les résultats dans la base de données PostgreSQL.

Étapes :
    1. Lecture du CSV brut
    2. Nettoyage et enrichissement des variables
    3. Sauvegarde du CSV nettoyé
    4. Insertion dans PostgreSQL (tables brutes et nettoyées)
"""

import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values

# ── Configuration du chemin d'importation du module de configuration ──
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from configuration.parametres import (
    CONFIG_BDD, CSV_BRUT, CSV_PROPRE,
    REPERTOIRE_BRUT, REPERTOIRE_JOURNAUX,
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
            REPERTOIRE_JOURNAUX / f"etl_{datetime.now():%Y%m%d_%H%M%S}.log",
            encoding="utf-8",
        ),
    ],
)
journal = logging.getLogger("ETL")


# ══════════════════════════════════════════════════════════════
# ÉTAPE 1 — Lecture du CSV brut
# ══════════════════════════════════════════════════════════════
def charger_csv_brut(chemin_csv: Path) -> pd.DataFrame:
    """Charge le fichier CSV brut et standardise les noms de colonnes."""
    journal.info("Lecture du fichier CSV : %s", chemin_csv)
    df = pd.read_csv(chemin_csv)
    journal.info("  Lignes chargées : %d | Colonnes : %d", len(df), df.shape[1])

    # Normalisation des noms de colonnes (suppression des espaces et majuscules)
    df.columns = [
        "udi", "product_id", "type",
        "air_temperature_k", "process_temperature_k",
        "rotational_speed_rpm", "torque_nm", "tool_wear_min",
        "machine_failure", "twf", "hdf", "pwf", "osf", "rnf",
    ]
    return df


# ══════════════════════════════════════════════════════════════
# ÉTAPE 2 — Nettoyage et enrichissement des données
# ══════════════════════════════════════════════════════════════
def nettoyer_et_enrichir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Effectue le nettoyage et l'enrichissement des données :
      - Imputation des valeurs manquantes (médiane pour le numérique)
      - Écrêtage des valeurs aberrantes (±3 écarts-types)
      - Encodage du type de machine (L=0, M=1, H=2)
      - Calcul de nouvelles variables : temp_diff et power
    """
    journal.info("Nettoyage et enrichissement des données...")
    nb_lignes_initial = len(df)

    # 2a. Imputation des valeurs manquantes numériques par la médiane
    colonnes_numeriques = df.select_dtypes(include=np.number).columns
    nb_manquants: pd.Series = df[colonnes_numeriques].isna().sum()
    if nb_manquants.sum() > 0:
        journal.warning("  Valeurs manquantes détectées : %s",
                        nb_manquants[nb_manquants > 0].to_dict())
        df[colonnes_numeriques] = df[colonnes_numeriques].fillna(
            df[colonnes_numeriques].median()
        )

    # Imputation des variables catégorielles
    if df["type"].isna().any():
        df["type"] = df["type"].fillna("M")  # Type par défaut : Moyen
    if df["product_id"].isna().any():
        df["product_id"] = df["product_id"].fillna("INCONNU")

    # 2b. Encodage ordinal du type de machine (L=0, M=1, H=2)
    correspondance_type = {"L": 0, "M": 1, "H": 2}
    df["type_encoded"] = df["type"].map(correspondance_type).fillna(1).astype(int)

    # 2c. Écrêtage des valeurs aberrantes à ±3 écarts-types
    colonnes_a_ecreter = [
        "air_temperature_k", "process_temperature_k",
        "rotational_speed_rpm", "torque_nm", "tool_wear_min",
    ]
    for colonne in colonnes_a_ecreter:
        moyenne, ecart_type = df[colonne].mean(), df[colonne].std()
        borne_inf = moyenne - 3 * ecart_type
        borne_sup = moyenne + 3 * ecart_type
        valeurs_ecretes = df[colonne].clip(borne_inf, borne_sup)
        nb_ecretes = (df[colonne] != valeurs_ecretes).sum()
        if nb_ecretes > 0:
            journal.info("  Valeurs aberrantes écrêtées [%s] : %d valeurs",
                         colonne, nb_ecretes)
        df[colonne] = valeurs_ecretes

    # 2d. Feature engineering : création de nouvelles variables
    # Écart thermique : différence entre température processus et température air
    df["temp_diff"] = (
        df["process_temperature_k"] - df["air_temperature_k"]
    ).round(3)

    # Puissance mécanique approximative : vitesse × couple
    df["power"] = (
        df["rotational_speed_rpm"] * df["torque_nm"]
    ).round(3)

    journal.info("  Nouvelles variables créées : temp_diff, power")
    journal.info("  Lignes finales : %d (supprimées : %d)",
                 len(df), nb_lignes_initial - len(df))

    return df


# ══════════════════════════════════════════════════════════════
# ÉTAPE 3 — Sauvegarde du CSV nettoyé
# ══════════════════════════════════════════════════════════════
def sauvegarder_csv_propre(df: pd.DataFrame) -> None:
    """Sauvegarde le DataFrame nettoyé dans le répertoire des données traitées."""
    df.to_csv(CSV_PROPRE, index=False)
    journal.info("CSV nettoyé sauvegardé : %s", CSV_PROPRE)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 4a — Connexion à PostgreSQL
# ══════════════════════════════════════════════════════════════
def obtenir_connexion():
    """Retourne une connexion active à la base de données PostgreSQL."""
    return psycopg2.connect(**CONFIG_BDD)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 4b — Insertion des données brutes
# ══════════════════════════════════════════════════════════════
def inserer_donnees_brutes(df: pd.DataFrame, connexion) -> int:
    """
    Vide et réinsère les données brutes dans la table raw_sensor_readings.
    Retourne le nombre de lignes insérées.
    """
    journal.info("Insertion dans raw_sensor_readings...")
    curseur = connexion.cursor()

    # Troncature de la table pour un réimport propre
    curseur.execute("TRUNCATE TABLE raw_sensor_readings RESTART IDENTITY CASCADE;")

    colonnes_brutes = [
        "udi", "product_id", "type",
        "air_temperature_k", "process_temperature_k",
        "rotational_speed_rpm", "torque_nm", "tool_wear_min",
        "machine_failure", "twf", "hdf", "pwf", "osf", "rnf",
    ]
    lignes = [tuple(r) for r in df[colonnes_brutes].itertuples(index=False)]

    execute_values(
        curseur,
        f"INSERT INTO raw_sensor_readings ({', '.join(colonnes_brutes)}) VALUES %s",
        lignes,
        page_size=500,
    )
    connexion.commit()
    journal.info("  → %d lignes insérées dans raw_sensor_readings", len(lignes))
    curseur.close()
    return len(lignes)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 4c — Insertion des données nettoyées
# ══════════════════════════════════════════════════════════════
def inserer_donnees_nettoyees(df: pd.DataFrame, connexion) -> int:
    """
    Vide et réinsère les données nettoyées dans la table cleaned_sensor_readings.
    Retourne le nombre de lignes insérées.
    """
    journal.info("Insertion dans cleaned_sensor_readings...")
    curseur = connexion.cursor()

    curseur.execute("TRUNCATE TABLE cleaned_sensor_readings RESTART IDENTITY;")

    colonnes_propres = [
        "udi", "product_id", "type", "type_encoded",
        "air_temperature_k", "process_temperature_k", "temp_diff",
        "rotational_speed_rpm", "torque_nm", "power",
        "tool_wear_min", "machine_failure",
    ]
    lignes = [tuple(r) for r in df[colonnes_propres].itertuples(index=False)]

    execute_values(
        curseur,
        f"INSERT INTO cleaned_sensor_readings ({', '.join(colonnes_propres)}) VALUES %s",
        lignes,
        page_size=500,
    )
    connexion.commit()
    journal.info("  → %d lignes insérées dans cleaned_sensor_readings", len(lignes))
    curseur.close()
    return len(lignes)


# ══════════════════════════════════════════════════════════════
# ÉTAPE 5 — Archivage du CSV brut dans donnees/brutes/
# ══════════════════════════════════════════════════════════════
def archiver_csv_brut(source: Path) -> None:
    """Copie le CSV source dans le répertoire des données brutes si absent."""
    destination = REPERTOIRE_BRUT / "ai4i2020.csv"
    if not destination.exists():
        shutil.copy2(source, destination)
        journal.info("CSV brut copié vers : %s", destination)
    else:
        journal.info("CSV brut déjà présent : %s", destination)


# ══════════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL
# ══════════════════════════════════════════════════════════════
def main():
    journal.info("═" * 55)
    journal.info("  ETL — Maintenance Prédictive OCP Safi")
    journal.info("═" * 55)

    # Résolution du chemin source (archive extraite ou dossier brutes/)
    chemin_archive = Path(__file__).resolve().parent.parent.parent / "archive_extracted" / "ai4i2020.csv"
    chemin_source  = chemin_archive if chemin_archive.exists() else CSV_BRUT

    if not chemin_source.exists():
        journal.error("Fichier CSV introuvable : %s", chemin_source)
        journal.error("  → Placer ai4i2020.csv dans donnees/brutes/ ou archive_extracted/")
        sys.exit(1)

    # Exécution séquentielle du pipeline ETL
    df_brut   = charger_csv_brut(chemin_source)
    archiver_csv_brut(chemin_source)
    df_propre = nettoyer_et_enrichir(df_brut)
    sauvegarder_csv_propre(df_propre)

    # Insertion en base de données
    connexion = obtenir_connexion()
    try:
        nb_brut   = inserer_donnees_brutes(df_brut, connexion)
        nb_propre = inserer_donnees_nettoyees(df_propre, connexion)
    finally:
        connexion.close()

    # Résumé final
    journal.info("═" * 55)
    journal.info("  ETL TERMINÉ — brutes: %d | nettoyées: %d", nb_brut, nb_propre)
    journal.info("  Pannes dans le jeu de données : %d (%.1f%%)",
                 df_propre["machine_failure"].sum(),
                 df_propre["machine_failure"].mean() * 100)
    journal.info("═" * 55)


if __name__ == "__main__":
    main()
