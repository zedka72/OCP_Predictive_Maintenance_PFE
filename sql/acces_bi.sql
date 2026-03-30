-- ==========================================================
-- sql/acces_bi.sql — Rôle lecture seule pour Power BI
-- OCP Safi — Maintenance Prédictive — AI4I 2020
--
-- À exécuter une seule fois en tant que superutilisateur (postgres)
-- ==========================================================

-- 1. Création du rôle en lecture seule dédié à Power BI
DROP ROLE IF EXISTS lecteur_bi;
CREATE ROLE lecteur_bi LOGIN PASSWORD 'bi_readonly_2026'
    NOSUPERUSER NOCREATEDB NOCREATEROLE;

-- 2. Autorisation de connexion à la base maintenance_pfe
GRANT CONNECT ON DATABASE maintenance_pfe TO lecteur_bi;

-- 3. Accès au schéma public
GRANT USAGE ON SCHEMA public TO lecteur_bi;

-- 4. Accès en lecture aux vues BI uniquement (pas aux tables brutes)
GRANT SELECT ON v_global_kpi          TO lecteur_bi;
GRANT SELECT ON v_risk_distribution   TO lecteur_bi;
GRANT SELECT ON v_high_risk_machines  TO lecteur_bi;

-- 5. Accès en lecture aux tables pour les jointures Power BI
GRANT SELECT ON predictions             TO lecteur_bi;
GRANT SELECT ON model_runs              TO lecteur_bi;
GRANT SELECT ON raw_sensor_readings     TO lecteur_bi;
GRANT SELECT ON cleaned_sensor_readings TO lecteur_bi;

-- ==========================================================
-- Commandes de vérification (à exécuter dans psql)
-- ==========================================================
-- \du lecteur_bi
-- \c maintenance_pfe lecteur_bi
-- SELECT COUNT(*) FROM v_global_kpi;          -- doit fonctionner
-- INSERT INTO predictions VALUES (...);       -- doit échouer (lecture seule)
