# Maintenance Prédictive — OCP Safi | PFE 2025–2026

**Jeu de données** : AI4I 2020  
**Stack technique** : Python 3.11 · XGBoost · PostgreSQL 16 · Power BI  
**Objectif** : Prédire le score de risque de panne des machines industrielles et le classifier en 3 niveaux (Faible / Moyen / Élevé)

---

## Structure du Projet

```
Projet PFE/
├── configuration/
│   ├── __init__.py
│   └── parametres.py              # Configuration centrale (BDD, variables, seuils)
├── donnees/
│   ├── brutes/                    # CSV brut AI4I 2020 (données sources)
│   └── traitees/                  # CSV nettoyé + variables enrichies
├── journaux/                      # Fichiers de log horodatés (ETL, entraînement, scoring)
├── modeles/
│   ├── xgb_maintenance.joblib     # Modèle XGBoost entraîné
│   └── normaliseur.joblib         # Normaliseur StandardScaler
├── sql/
│   ├── schema.sql                 # Schéma PostgreSQL : 4 tables + 3 vues BI
│   ├── acces_bi.sql               # Rôle lecture seule pour Power BI
│   └── mesures_dax.txt            # Mesures DAX pour Power BI Desktop
├── src/
│   ├── etl/
│   │   └── pipeline_etl.py        # Pipeline ETL : CSV → PostgreSQL
│   ├── entrainement/
│   │   └── entrainer_modele.py    # Entraînement : Régression Logistique + XGBoost
│   └── prediction/
│       └── calcul_risque.py       # Scoring batch : prédictions → PostgreSQL
├── utils/
│   └── verifier_pipeline.py       # Vérification rapide de la BDD et des résultats
├── README.md                      # Ce fichier
└── requirements.txt               # Dépendances Python
```

---

## Prérequis

- **Python 3.11** installé (`C:\Program Files\Python311\`)
- **PostgreSQL 16** en cours d'exécution (service `postgresql-x64-16`)
- Base de données `maintenance_pfe` et utilisateur `pfe_user` créés
- Environnement virtuel `.venv` activé et packages installés
- Fichier `ai4i2020.csv` placé dans `donnees/brutes/` ou `archive_extracted/`

---

## Installation

### 0. Activer l'environnement virtuel

À exécuter à chaque nouvelle session PowerShell :

```powershell
cd "C:\Users\ouakr\Desktop\Projet PFE"
$env:Path += ";C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
.\.venv\Scripts\Activate.ps1
# Le prompt doit afficher (.venv)
```

### Installer les dépendances

```powershell
pip install -r requirements.txt
```

---

## Ordre d'Exécution du Pipeline

```
1. psql -U pfe_user -d maintenance_pfe -f sql/schema.sql
2. python src/etl/pipeline_etl.py
3. python src/entrainement/entrainer_modele.py
4. python src/prediction/calcul_risque.py
5. python utils/verifier_pipeline.py
```

---

## Exécution Détaillée

### Étape 1 — Créer le schéma PostgreSQL

```powershell
psql -U pfe_user -d maintenance_pfe -f sql/schema.sql
```

Ce script crée les 4 tables et les 3 vues BI :

| Tables | Description |
|---|---|
| `raw_sensor_readings` | Données brutes importées depuis le CSV |
| `cleaned_sensor_readings` | Données nettoyées + variables enrichies |
| `model_runs` | Historique des runs d'entraînement |
| `predictions` | Résultats du scoring batch |

| Vues BI | Description |
|---|---|
| `v_global_kpi` | KPIs globaux du dernier run (pour Power BI) |
| `v_risk_distribution` | Distribution des risques par type de machine |
| `v_high_risk_machines` | Top 50 machines à risque élevé |

Vérification dans psql :
```sql
\dt   -- Affiche les 4 tables
\dv   -- Affiche les 3 vues
```

---

### Étape 2 — Exécuter le Pipeline ETL

```powershell
python src/etl/pipeline_etl.py
```

Ce script :
- Lit le CSV source (`donnees/brutes/ai4i2020.csv` ou `archive_extracted/`)
- Nettoie les données (imputation des valeurs manquantes, écrêtage ±3σ)
- Encode le type de machine (L=0, M=1, H=2)
- Calcule les variables enrichies : `temp_diff` (écart thermique) et `power` (puissance)
- Insère dans `raw_sensor_readings` (10 000 lignes) et `cleaned_sensor_readings`
- Sauvegarde le CSV nettoyé dans `donnees/traitees/`

Vérification SQL :
```sql
SELECT COUNT(*) FROM raw_sensor_readings;      -- 10 000 lignes attendues
SELECT COUNT(*) FROM cleaned_sensor_readings;  -- 10 000 lignes attendues
SELECT AVG(temp_diff), AVG(power) FROM cleaned_sensor_readings;
```

---

### Étape 3 — Entraîner le Modèle

```powershell
python src/entrainement/entrainer_modele.py
```

Ce script :
- Charge les données depuis `cleaned_sensor_readings`
- Entraîne une **Régression Logistique** (modèle de référence)
- Entraîne un **XGBoostClassifier** (modèle principal)
- Calcule les métriques : Exactitude, Précision, Rappel, F1, ROC-AUC
- Sauvegarde `modeles/xgb_maintenance.joblib` et `modeles/normaliseur.joblib`
- Insère les résultats dans `model_runs`

Vérification SQL :
```sql
SELECT model_name, run_date, accuracy, recall, f1_score, roc_auc
FROM model_runs
ORDER BY run_date DESC
LIMIT 5;
```

---

### Étape 4 — Scoring Batch

```powershell
python src/prediction/calcul_risque.py
```

Ce script :
- Charge `cleaned_sensor_readings` et le modèle XGBoost entraîné
- Calcule les probabilités de panne (`risk_score`) pour chaque machine
- Attribue un niveau de risque : **Low** (< 0,30) | **Medium** (0,30–0,60) | **High** (≥ 0,60)
- Insère les résultats dans `predictions`

Vérification SQL :
```sql
-- Distribution des niveaux de risque
SELECT risk_level, COUNT(*), ROUND(AVG(risk_score)::NUMERIC, 4)
FROM predictions
GROUP BY risk_level
ORDER BY risk_level;

-- KPIs globaux (vue Power BI)
SELECT * FROM v_global_kpi;

-- Top machines à risque élevé
SELECT * FROM v_high_risk_machines LIMIT 10;
```

---

### Étape 5 — Vérification Rapide

```powershell
python utils/verifier_pipeline.py
```

Affiche un résumé complet : métriques du dernier run, distribution des risques, KPIs et top machines.

---

## Connexion Power BI

1. Ouvrir **Power BI Desktop**
2. **Accueil → Obtenir des données → Base de données PostgreSQL**
3. Serveur : `localhost` | Base : `maintenance_pfe`
4. Importer les vues : `v_global_kpi`, `v_risk_distribution`, `v_high_risk_machines`
5. Pour un accès en lecture seule dédié :
   ```powershell
   psql -U postgres -f sql/acces_bi.sql
   # Identifiants Power BI : lecteur_bi / bi_readonly_2026
   ```

---

## Résolution des Erreurs Fréquentes

### `python` non reconnu dans PowerShell
```powershell
$env:Path += ";C:\Program Files\Python311;C:\Program Files\Python311\Scripts"
```

### `psql` non reconnu dans PowerShell
```powershell
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

### Service PostgreSQL arrêté
```powershell
Get-Service postgresql-x64-16     # Vérifier le statut
Start-Service postgresql-x64-16   # Démarrer si arrêté
```

### Erreur d'authentification PostgreSQL
```powershell
psql -U postgres -c "ALTER USER pfe_user WITH PASSWORD 'pfe_password123';"
```

### `ModuleNotFoundError`
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### `Modèle introuvable` lors du scoring
> Le scoring nécessite un modèle entraîné. Exécuter d'abord :
```powershell
python src/entrainement/entrainer_modele.py
```

---

## Requêtes SQL Utiles

```sql
-- Distribution générale des pannes
SELECT machine_failure, COUNT(*) AS nb, ROUND(100.0*COUNT(*)/10000, 2) AS pct
FROM raw_sensor_readings
GROUP BY machine_failure;

-- Pannes par type de machine
SELECT type, SUM(machine_failure) AS pannes, COUNT(*) AS total
FROM raw_sensor_readings
GROUP BY type ORDER BY type;

-- Corrélation entre usure outil et panne
SELECT
    CASE WHEN tool_wear_min < 100 THEN '<100 min'
         WHEN tool_wear_min < 200 THEN '100–200 min'
         ELSE '>200 min' END AS tranche_usure,
    ROUND(AVG(machine_failure::NUMERIC)*100, 1) AS pct_panne
FROM raw_sensor_readings
GROUP BY 1 ORDER BY 1;

-- Performances du dernier run
SELECT model_name, roc_auc, f1_score, recall, n_train, n_test
FROM model_runs ORDER BY run_date DESC LIMIT 1;

-- Distribution risque par type de machine (vue BI)
SELECT * FROM v_risk_distribution;

-- KPIs de monitoring
SELECT * FROM v_global_kpi;
```

---

## Architecture des Données

```
CSV brut (AI4I 2020)
        ↓  pipeline_etl.py
raw_sensor_readings  ──────────────────┐
        ↓                              │
cleaned_sensor_readings                │
        ↓  entrainer_modele.py         │
   model_runs                          │
   modeles/xgb_maintenance.joblib      │
        ↓  calcul_risque.py            │
    predictions ←──────────────────────┘
        ↓
  Vues BI (v_global_kpi, v_risk_distribution, v_high_risk_machines)
        ↓
   Power BI Desktop
```
