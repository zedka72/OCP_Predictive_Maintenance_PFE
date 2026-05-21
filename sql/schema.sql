-- ==========================================================
-- sql/schema.sql — Schéma PostgreSQL PFE Maintenance OCP Safi
-- ==========================================================

-- ──────────────────────────────────────────────────────────
-- 1. RAW SENSOR READINGS
--    Données brutes importées depuis CSV — jamais modifiées
-- ──────────────────────────────────────────────────────────
DROP TABLE IF EXISTS raw_sensor_readings CASCADE;

CREATE TABLE raw_sensor_readings (
    id                     SERIAL          PRIMARY KEY,
    udi                    INTEGER         NOT NULL UNIQUE,
    product_id             VARCHAR(10),
    type                   CHAR(1),
    air_temperature_k      NUMERIC(7,3),
    process_temperature_k  NUMERIC(7,3),
    rotational_speed_rpm   INTEGER,
    torque_nm              NUMERIC(7,3),
    tool_wear_min          INTEGER,
    machine_failure        SMALLINT        CHECK (machine_failure IN (0,1)),
    twf                    SMALLINT        CHECK (twf IN (0,1)),
    hdf                    SMALLINT        CHECK (hdf IN (0,1)),
    pwf                    SMALLINT        CHECK (pwf IN (0,1)),
    osf                    SMALLINT        CHECK (osf IN (0,1)),
    rnf                    SMALLINT        CHECK (rnf IN (0,1)),
    ingested_at            TIMESTAMP       DEFAULT NOW()
);

-- Index
CREATE INDEX idx_raw_type           ON raw_sensor_readings (type);
CREATE INDEX idx_raw_failure        ON raw_sensor_readings (machine_failure);
CREATE INDEX idx_raw_ingested       ON raw_sensor_readings (ingested_at DESC);
CREATE INDEX idx_raw_tool_wear      ON raw_sensor_readings (tool_wear_min);

-- ──────────────────────────────────────────────────────────
-- 2. CLEANED SENSOR READINGS
--    Données nettoyées + features engineerées prêtes pour ML
-- ──────────────────────────────────────────────────────────
DROP TABLE IF EXISTS cleaned_sensor_readings CASCADE;

CREATE TABLE cleaned_sensor_readings (
    id                     SERIAL          PRIMARY KEY,
    udi                    INTEGER         NOT NULL UNIQUE REFERENCES raw_sensor_readings(udi),
    product_id             VARCHAR(10),
    type                   CHAR(1),
    type_encoded           SMALLINT,        -- L=0, M=1, H=2
    air_temperature_k      NUMERIC(7,3),
    process_temperature_k  NUMERIC(7,3),
    temp_diff              NUMERIC(7,3),    -- process_temp - air_temp
    rotational_speed_rpm   INTEGER,
    torque_nm              NUMERIC(7,3),
    power                  NUMERIC(10,3),  -- rpm * torque
    tool_wear_min          INTEGER,
    machine_failure        SMALLINT,
    cleaned_at             TIMESTAMP       DEFAULT NOW()
);

-- Index
CREATE INDEX idx_clean_type         ON cleaned_sensor_readings (type);
CREATE INDEX idx_clean_failure      ON cleaned_sensor_readings (machine_failure);
CREATE INDEX idx_clean_tool_wear    ON cleaned_sensor_readings (tool_wear_min);
CREATE INDEX idx_clean_power        ON cleaned_sensor_readings (power DESC);

-- ──────────────────────────────────────────────────────────
-- 3. MODEL RUNS
--    Historique de chaque exécution d'entraînement
-- ──────────────────────────────────────────────────────────
DROP TABLE IF EXISTS model_runs CASCADE;

CREATE TABLE model_runs (
    run_id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name      VARCHAR(50)     NOT NULL,
    run_date        TIMESTAMP       DEFAULT NOW(),
    n_train         INTEGER,
    n_test          INTEGER,
    accuracy        NUMERIC(6,4),
    precision_score NUMERIC(6,4),
    recall          NUMERIC(6,4),
    f1_score        NUMERIC(6,4),
    roc_auc         NUMERIC(6,4),
    threshold_low   NUMERIC(5,3),
    threshold_high  NUMERIC(5,3),
    model_path      TEXT,
    params          JSONB,
    notes           TEXT
);

-- Index
CREATE INDEX idx_runs_model         ON model_runs (model_name);
CREATE INDEX idx_runs_date          ON model_runs (run_date DESC);
CREATE INDEX idx_runs_auc           ON model_runs (roc_auc DESC);

-- ──────────────────────────────────────────────────────────
-- 3.bis ROC CURVE DATA
--    Points (FPR, TPR) pour la courbe ROC du dernier run
-- ──────────────────────────────────────────────────────────
DROP TABLE IF EXISTS roc_curve_data CASCADE;

CREATE TABLE roc_curve_data (
    run_id          UUID            REFERENCES model_runs(run_id) ON DELETE CASCADE,
    fpr             NUMERIC(6,4),
    tpr             NUMERIC(6,4),
    threshold       NUMERIC(6,4)
);

CREATE INDEX idx_roc_run            ON roc_curve_data (run_id);

-- ──────────────────────────────────────────────────────────
-- 4. PREDICTIONS
--    Résultats du batch scoring
-- ──────────────────────────────────────────────────────────
DROP TABLE IF EXISTS predictions CASCADE;

CREATE TABLE predictions (
    pred_id         SERIAL          PRIMARY KEY,
    run_id          UUID            REFERENCES model_runs(run_id),
    udi             INTEGER         REFERENCES raw_sensor_readings(udi),
    product_id      VARCHAR(10),
    type            CHAR(1),
    risk_score      NUMERIC(6,4)    NOT NULL,  -- probabilité [0,1]
    risk_level      VARCHAR(10)     NOT NULL CHECK (risk_level IN ('Low','Medium','High')),
    scored_at       TIMESTAMP       DEFAULT NOW(),

    -- Valeurs au moment du scoring (snapshot)
    air_temperature_k      NUMERIC(7,3),
    process_temperature_k  NUMERIC(7,3),
    rotational_speed_rpm   INTEGER,
    torque_nm              NUMERIC(7,3),
    tool_wear_min          INTEGER,
    actual_failure         SMALLINT
);

-- Index
CREATE INDEX idx_pred_run           ON predictions (run_id);
CREATE INDEX idx_pred_risk_level    ON predictions (risk_level);
CREATE INDEX idx_pred_risk_score    ON predictions (risk_score DESC);
CREATE INDEX idx_pred_scored        ON predictions (scored_at DESC);
CREATE INDEX idx_pred_udi           ON predictions (udi);


-- ==========================================================
-- VUES BI (Power BI / pgAdmin)
-- ==========================================================

-- ── Vue 1 : Distribution des niveaux de risque par type machine
DROP VIEW IF EXISTS v_risk_distribution;
CREATE VIEW v_risk_distribution AS
SELECT
    p.type,
    p.risk_level,
    COUNT(*)                                         AS nb_machines,
    ROUND(AVG(p.risk_score)::NUMERIC, 4)             AS avg_risk_score,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER
        (PARTITION BY p.type), 2)                    AS pct_du_type,
    MAX(p.scored_at)                                 AS derniere_maj
FROM predictions p
JOIN model_runs  r ON p.run_id = r.run_id
WHERE r.run_date = (SELECT MAX(run_date) FROM model_runs)
GROUP BY p.type, p.risk_level
ORDER BY p.type, p.risk_level;

-- ── Vue 2 : Top 50 machines à risque élevé avec détails capteurs
DROP VIEW IF EXISTS v_high_risk_machines;
CREATE VIEW v_high_risk_machines AS
SELECT
    p.udi,
    p.product_id,
    p.type,
    p.risk_score,
    p.risk_level,
    p.air_temperature_k,
    p.process_temperature_k,
    ROUND((p.process_temperature_k - p.air_temperature_k)::NUMERIC, 2)
                                                     AS temp_diff,
    p.rotational_speed_rpm,
    p.torque_nm,
    p.tool_wear_min,
    p.actual_failure,
    p.scored_at
FROM predictions p
JOIN model_runs  r ON p.run_id = r.run_id
WHERE p.risk_level = 'High'
  AND r.run_date = (SELECT MAX(run_date) FROM model_runs)
ORDER BY p.risk_score DESC
LIMIT 50;

-- ── Vue 3 : KPI globaux du dernier run pour Power BI
DROP VIEW IF EXISTS v_global_kpi;
CREATE VIEW v_global_kpi AS
SELECT
    r.run_id,
    r.run_date,
    r.model_name,
    r.roc_auc,
    r.f1_score,
    r.recall,
    COUNT(p.pred_id)                                   AS total_scored,
    SUM(CASE WHEN p.risk_level = 'High'   THEN 1 ELSE 0 END) AS nb_high,
    SUM(CASE WHEN p.risk_level = 'Medium' THEN 1 ELSE 0 END) AS nb_medium,
    SUM(CASE WHEN p.risk_level = 'Low'    THEN 1 ELSE 0 END) AS nb_low,
    ROUND(AVG(p.risk_score)::NUMERIC, 4)               AS avg_risk_score,
    ROUND(100.0 * SUM(CASE WHEN p.risk_level = 'High' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(p.pred_id),0), 2)             AS pct_high_risk
FROM model_runs   r
LEFT JOIN predictions p ON p.run_id = r.run_id
WHERE r.run_date = (SELECT MAX(run_date) FROM model_runs)
GROUP BY r.run_id, r.run_date, r.model_name, r.roc_auc, r.f1_score, r.recall;
