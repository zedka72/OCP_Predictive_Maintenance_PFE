# Guide de Création des 8 Images pour le Rapport

## Préface

Les 8 images suivantes sont **placeholders intégrés** dans le LaTeX. Vous devez les créer et les placer dans un dossier `images/` pour que le PDF final soit complet.

---

## 📋 Liste des 8 Images à Créer

### 1️⃣ Architecture Système (Chapitre 4)

**Fichier** : `images/01_architecture_systeme.png`

**Dimensions** : 1000px × 600px (landscape)

**Contenu** : Diagramme montrant 3 couches :
- **Couche 1 (Ingestion/ML)** : Extraction CSV → Nettoyage → Feature Engineering → Modèle XGBoost
- **Couche 2 (PostgreSQL)** : 4 tables relationnelles + 3 vues SQL + indexation
- **Couche 3 (Power BI)** : Dashboard 3 pages + 20+ mesures DAX

**Flèches** : Flux de données descendant entre couches

**Style** :
- Couleurs professionnelles : bleu (couche 1), vert (couche 2), orange (couche 3)
- Boîtes arrondies
- Texte blanc sur fond coloré
- Font sans-serif (Arial, Helvetica)

**Outil** : Draw.io, Lucidchart, PowerPoint

---

### 2️⃣ Pipeline ETL (Chapitre 5 - Étape 1)

**Fichier** : `images/02_pipeline_etl_flux.png`

**Dimensions** : 1100px × 500px (landscape)

**Contenu** : Flux horizontal du pipeline :

```
[CSV Input] → [Lecture] → [Exploration] → [Imputation] → 
[Détection Outliers] → [Normalisation] → [Feature Eng] → [PostgreSQL]
```

**Étapes** :
1. Lecture données brutes (10k lignes)
2. Exploration (statistics, null check)
3. Imputation (valeurs manquantes)
4. Détection/écrêtage outliers
5. Normalisation (StandardScaler)
6. Feature Engineering (temp_diff, power)
7. Chargement PostgreSQL (cleaned_sensor_readings)

**Style** :
- Boîtes sequentielles reliées par flèches
- Couleur dégradée (bleu clair → bleu foncé)
- Chiffres étapes en cercles (1, 2, 3...)
- 2-3 lignes descriptif par étape

**Outil** : Draw.io, Lucidchart, Google Slides

---

### 3️⃣ Power BI Dashboard - Page 1 : KPI (Chapitre 5)

**Fichier** : `images/03_powerbi_page1_kpi.png`

**Dimensions** : 1400px × 800px (landscape, portrait possible)

**Contenu** : Capture d'écran ou mockup Power BI page 1 :

**Éléments clés** :
- Titre page : "KPIs Stratégiques"
- Card 1 : Total Machines (9999)
- Card 2 : Machines à Risque Élevé (170)
- Card 3 : % Risque Élevé (1.70%)
- Card 4 : Taux Panne Réel (3.39%)
- Graphique 1 : Distribution des risques (pie chart : Low 91%, Medium 7%, High 2%)
- Graphique 2 : KPIs Modèle (ROC-AUC: 0.9789, F1: 0.9599, Recall: 0.9556)
- Slicers/filtres : Machine Type (L, M, H), Date range

**Style** :
- Fond blanc avec thème bleu
- Cards avec nombres en gros caractères
- Graphiques colorés (bleu, orange, vert)
- Design clean et professionnel

**Outil** : Power BI Desktop (screenshot) ou Figma mockup

---

### 4️⃣ Power BI Dashboard - Page 2 : Maintenance (Chapitre 5)

**Fichier** : `images/04_powerbi_page2_maintenance.png`

**Dimensions** : 1400px × 800px (landscape)

**Contenu** : Capture d'écran ou mockup Power BI page 2 :

**Éléments clés** :
- Titre page : "Priorisation Top 50 - Machines à Intervenir"
- Table/Matrix : 
  - Colonnes : UDI, Product ID, Type, Torque, Tool Wear, Process Temp, Risk Score, Risk Level, Urgency
  - 20-30 rows visibles
  - Tri : Risk Score décroissant (0.9987 → 0.85...)
  - Coloration conditionnelle : RED pour High, ORANGE pour Medium
- Graphique : Distribution tool wear pour machines High Risk
- Slicer : Risk Level filter

**Style** :
- Couleur danger : rouge pour High, orange pour Medium
- Table bien lisible
- Numéros alignés à droite
- Compact et dense (tout tient en 1 page)

**Outil** : Power BI Desktop (screenshot) ou Figma/Excel mockup

---

### 5️⃣ Power BI Dashboard - Page 3 : Quality (Chapitre 5)

**Fichier** : `images/05_powerbi_page3_quality.png`

**Dimensions** : 1400px × 800px (landscape)

**Contenu** : Capture d'écran ou mockup Power BI page 3 :

**Éléments clés** :
- Titre page : "Qualité du Modèle et Métriques"
- Section 1 : Matrice de Confusion (heatmap 2x2 : TP, FP, FN, TN)
- Section 2 : KPIs Modèle (cartes : Accuracy 0.9876, Precision 0.9642, Recall 0.9556, F1 0.9599, ROC-AUC 0.9789)
- Section 3 : Historique ROC-AUC (courbe line chart au fil des runs)
- Section 4 : Distribution prédictions (histogram : scores [0-1])

**Style** :
- Heatmap rouge → vert (confusion)
- KPI cards en vert (succès)
- Courbe lisse et élégante
- Professionnel et scientifique

**Outil** : Power BI Desktop (screenshot) ou Matplotlib/Seaborn graphique

---

### 6️⃣ Matrice de Confusion (Chapitre 6)

**Fichier** : `images/06_confusion_matrix_xgboost.png`

**Dimensions** : 700px × 700px (carré)

**Contenu** : Heatmap 2×2 matrice de confusion :

```
              Prédit Négatif  Prédit Positif
Réel Négatif      9629              75        (TN=9629, FP=75)
Réel Positif       15              310        (FN=15, TP=310)
```

**Valeurs** :
- TP (True Positive) : 310
- FP (False Positive) : 75
- FN (False Negative) : 15
- TN (True Negative) : 9629

**Couleurs** : Gradient vert clair (bas) → vert foncé (haut)

**Labels** : Valeurs absolues + pourcentages

**Style** :
- Heatmap propre (sklearn.metrics ou seaborn)
- Font lisible
- Axes labellisés clairement
- Titre : "Matrice de Confusion - XGBoost"

**Outil** : Python (matplotlib, seaborn), Tableau Public, Power BI

---

### 7️⃣ Feature Importance (Chapitre 6)

**Fichier** : `images/07_feature_importance_xgboost.png`

**Dimensions** : 900px × 600px (landscape)

**Contenu** : Graphique barres horizontal montrant importance des 8 variables :

**Variables et scores approx** :
1. Tool wear [min] : 0.45
2. Torque [Nm] : 0.25
3. Process temperature [K] : 0.15
4. Rotational speed [rpm] : 0.08
5. Power (feature engineered) : 0.04
6. Air temperature [K] : 0.02
7. Temperature difference (feature eng) : 0.01
8. Product Type : 0.00

**Style** :
- Barres horizontales décroissantes
- Gradient couleur : rouge (haut) → bleu (bas)
- Valeurs en pourcentages affichées
- Titre : "Feature Importance - Modèle XGBoost"
- Axe X : 0 à 0.5 (importance score)

**Outil** : Python (xgboost.plot_importance), R (ggplot2), Tableau

---

### 8️⃣ Schéma PostgreSQL - ER Diagram (Chapitre 6)

**Fichier** : `images/08_postgresql_schema_er.png`

**Dimensions** : 1200px × 800px (landscape)

**Contenu** : Diagramme Entité-Relation montrant 4 tables :

**Table 1 : raw_sensor_readings**
- Colonnes : udi (PK), product_id, type, air_temperature_k, process_temperature_k, rotational_speed_rpm, torque_nm, tool_wear_min, machine_failure, created_at
- Indices : idx_type, idx_machine_failure

**Table 2 : cleaned_sensor_readings**
- Colonnes : clean_id (PK), udi (FK), air_temperature_k, ..., temp_diff, power, type_encoded, machine_failure, processed_at
- Lien FK vers raw_sensor_readings

**Table 3 : model_runs**
- Colonnes : run_id (PK, UUID), model_name, training_date, hyperparameters (JSONB), accuracy, precision, recall, f1_score, roc_auc, notes
- Indice : idx_training_date

**Table 4 : predictions**
- Colonnes : pred_id (PK), run_id (FK), udi (FK), risk_score, risk_level, predicted_failure, prediction_date
- Liens FK vers model_runs et raw_sensor_readings

**Vues** :
- v_global_kpi
- v_risk_distribution
- v_high_risk_machines

**Style** :
- Boîtes pour tables (blanc fond, bleu bordure)
- Colonnes listées inside
- Clés primaires en gras
- Clés étrangères avec symboles de relation
- Vues en boîtes arrondies (gris)
- Relations avec cardinalités (1, N)

**Outil** : Draw.io, Lucidchart, PostgreSQL pgAdmin (export), DBVisualizer

---

## 🎨 Recommandations de Design Global

### Palette de couleurs suggérée :
- **Primaire** : Bleu professionnel (#0078D4 ou #003366)
- **Accent** : Orange (#FF8C00)
- **Succès** : Vert (#28A745)
- **Alerte** : Rouge (#DC3545)
- **Neutre** : Gris clair (#F0F0F0), Gris foncé (#333333)

### Typographie :
- Font corpo : Arial, Helvetica, Segoe UI
- Taille titre : 18-20px
- Taille contenu : 12-14px
- Bold pour labels importants

### Dimensions conseillées :
- Pour figures portrait (3-7) : 900-1000px × 600-700px
- Pour figures paysage (1-2, 8) : 1000-1200px × 600-800px
- Résolution : 300 dpi si print prévu, 150 dpi si digital suffisant

---

## 📦 Procédure de Placement

### 1. Créer dossier
```bash
mkdir images
```

### 2. Nommer fichiers exactement :
```
images/01_architecture_systeme.png
images/02_pipeline_etl_flux.png
images/03_powerbi_page1_kpi.png
images/04_powerbi_page2_maintenance.png
images/05_powerbi_page3_quality.png
images/06_confusion_matrix_xgboost.png
images/07_feature_importance_xgboost.png
images/08_postgresql_schema_er.png
```

### 3. Compiler LaTeX
```bash
pdflatex rapport_pfe_modifie.tex
bibtex rapport_pfe_modifie
pdflatex rapport_pfe_modifie.tex
pdflatex rapport_pfe_modifie.tex
```

### 4. Vérifier PDF généré
- Pas de "?" ou chemins cassés
- Images bien alignées
- Captions lisibles

---

## ⏰ Temps Estimé par Image

| Image | Outil | Temps |
|-------|-------|-------|
| 01 Architecture | Draw.io | 30-45 min |
| 02 ETL Pipeline | Draw.io ou PowerPoint | 20-30 min |
| 03 Dashboard KPI | Power BI screenshot | 15-20 min |
| 04 Dashboard Maintenance | Power BI screenshot | 15-20 min |
| 05 Dashboard Quality | Power BI screenshot | 15-20 min |
| 06 Confusion Matrix | Python/Seaborn | 10 min |
| 07 Feature Importance | Python/XGBoost | 10 min |
| 08 PostgreSQL ER | Draw.io ou Lucidchart | 30-45 min |
| **Total** | **Mix** | **2-3 heures** |

---

## 💡 Astuces

### Power BI :
- Créer rapport dummy avec données fictives
- Prendre screenshots avec bonne résolution
- Format : Tableau blanc simple, pas trop d'animations
- Exporter en PNG haute résolution (1400+ px)

### Draw.io / Lucidchart :
- Utiliser templates "Database" ou "System Architecture"
- Exporter en PNG 300 dpi
- Vérifier contraste texte/fond
- Grouper éléments bien

### Python (Confusion Matrix, Feature Importance) :
```python
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens')
plt.savefig('06_confusion_matrix_xgboost.png', dpi=300, bbox_inches='tight')

# Feature Importance
xgb_model.plot_importance(importance_type='weight')
plt.savefig('07_feature_importance_xgboost.png', dpi=300, bbox_inches='tight')
```

---

## ✅ Checklist Avant Compilation

- [ ] Dossier `images/` créé
- [ ] Les 8 fichiers PNG/PDF placés avec noms exacts
- [ ] Résolution ≥ 150 dpi
- [ ] Pas d'espaces dans noms de fichiers
- [ ] Formats supportés : .png, .pdf, .jpg
- [ ] LaTeX peut accéder au dossier (permissions OK)

---

**Une fois images en place, compilez et vérifiez le PDF final ! 🎉**
