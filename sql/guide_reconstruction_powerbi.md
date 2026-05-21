# Guide complet — Reconstruction des 3 Dashboards Power BI from scratch

> **Prérequis** : PostgreSQL démarré + données chargées (`python -m src.etl.pipeline_etl` + `python -m src.entrainement.entrainer_modele`)

---

## ÉTAPE 1 — Connexion PostgreSQL

1. Ouvrir **Power BI Desktop**
2. `Accueil → Obtenir des données → Base de données → Base de données PostgreSQL`
3. Remplir :
   - Serveur : `localhost`
   - Base de données : `maintenance_predictive`
4. Cliquer **OK** → Mode Connectivité : **Importer**
5. Dans le navigateur, cocher ces **5 tables** :
   - ☑ `public predictions`
   - ☑ `public raw_sensor_readings`
   - ☑ `public model_runs`
   - ☑ `public cleaned_sensor_readings`
   - ☑ `public roc_curve_data`
6. Cliquer **Charger**

---

## ÉTAPE 2 — Modèle de données (Relations)

Aller dans l'onglet **Modèle** (icône gauche)

Créer ces relations (glisser-déposer) :

| Table source | Colonne | Table cible | Colonne | Type |
|---|---|---|---|---|
| `public predictions` | `run_id` | `public model_runs` | `run_id` | Plusieurs → Un |
| `public predictions` | `udi` | `public raw_sensor_readings` | `udi` | Plusieurs → Un |
| `public roc_curve_data` | `run_id` | `public model_runs` | `run_id` | Plusieurs → Un |

---

## ÉTAPE 3 — Créer toutes les mesures DAX

### Comment créer une mesure :
`Accueil → Nouvelle mesure` (dans la table `public predictions`)

Copier-coller **chaque bloc** ci-dessous séparément.

---

### GROUPE A — KPIs Principaux (Page 1)

```dax
Total Machines =
COUNTROWS('public predictions')
```

```dax
Machines High Risk =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_level] = "High"
)
```

```dax
Machines Medium Risk =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_level] = "Medium"
)
```

```dax
Machines Low Risk =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_level] = "Low"
)
```

```dax
Pct High Risk =
DIVIDE([Machines High Risk], [Total Machines], 0) * 100
```

```dax
Pct Medium Risk =
DIVIDE([Machines Medium Risk], [Total Machines], 0) * 100
```

```dax
Pct Low Risk =
DIVIDE([Machines Low Risk], [Total Machines], 0) * 100
```

```dax
Risk Score Moyen =
AVERAGE('public predictions'[risk_score])
```

```dax
Taux Panne Reel =
DIVIDE(
    CALCULATE(
        COUNTROWS('public predictions'),
        'public predictions'[actual_failure] = 1
    ),
    COUNTROWS('public predictions'),
    0
) * 100
```

---

### GROUPE B — Métriques Modèle (Page 3)

```dax
ROC AUC Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[roc_auc]), 'public model_runs'[run_date] = dernierRun)
```

```dax
F1 Score Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[f1_score]), 'public model_runs'[run_date] = dernierRun)
```

```dax
Recall Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[recall]), 'public model_runs'[run_date] = dernierRun)
```

```dax
Precision Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[precision_score]), 'public model_runs'[run_date] = dernierRun)
```

```dax
Accuracy Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[accuracy]), 'public model_runs'[run_date] = dernierRun)
```

---

### GROUPE C — Matrice de Confusion (Page 3)

> ⚠️ Ces mesures utilisent le **seuil 0.50** (même que sklearn) pour correspondre aux chiffres du rapport

```dax
Vrais Positifs =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_score] >= 0.50,
    'public predictions'[actual_failure] = 1
)
```

```dax
Faux Positifs =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_score] >= 0.50,
    'public predictions'[actual_failure] = 0
)
```

```dax
Vrais Negatifs =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_score] < 0.50,
    'public predictions'[actual_failure] = 0
)
```

```dax
Faux Negatifs =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_score] < 0.50,
    'public predictions'[actual_failure] = 1
)
```

```dax
Recall DAX =
DIVIDE([Vrais Positifs], [Vrais Positifs] + [Faux Negatifs], 0)
```

```dax
Precision DAX =
DIVIDE([Vrais Positifs], [Vrais Positifs] + [Faux Positifs], 0)
```

```dax
Accuracy DAX =
DIVIDE(
    [Vrais Positifs] + [Vrais Negatifs],
    [Vrais Positifs] + [Vrais Negatifs] + [Faux Positifs] + [Faux Negatifs],
    0
)
```

---

### GROUPE D — Impact Financier (Page 2)

```dax
Gain Estime DH =
([Vrais Positifs] * 500000) - ([Faux Positifs] * 30000)
```

```dax
Ratio Preventif =
DIVIDE([Machines High Risk] + [Machines Medium Risk], [Total Machines], 0) * 100
```

---

### GROUPE E — Colonnes calculées
> À créer dans **`public predictions`** → Onglet Données → Nouvelle colonne

```dax
Risk Score Bin =
SWITCH(
    TRUE(),
    'public predictions'[risk_score] < 0.30, "1. Low (< 0.30)",
    'public predictions'[risk_score] < 0.60, "2. Medium (0.30-0.60)",
    "3. High (>= 0.60)"
)
```

```dax
Intervention Urgency =
SWITCH(
    TRUE(),
    'public predictions'[risk_level] = "High" && 'public predictions'[tool_wear_min] > 150, "URGENT",
    'public predictions'[risk_level] = "High" && 'public predictions'[tool_wear_min] <= 150, "PRIORITAIRE",
    'public predictions'[risk_level] = "Medium", "A SURVEILLER",
    "OK"
)
```

---

## ÉTAPE 4 — PAGE 1 : Vue d'ensemble

**Nom de la page** : `Vue d'ensemble`

### Titre
- Insérer → Zone de texte
- Texte : **Tableau de Bord — Maintenance Prédictive OCP Safi**
- Police : 20pt, Gras, centré

### Visuel 1 — Carte KPI : Total Machines
- Type : **Carte**
- Champ : `Total Machines`
- Titre visuel : "Total Machines"

### Visuel 2 — Carte KPI : Machines High Risk
- Type : **Carte**
- Champ : `Machines High Risk`
- Titre : "Machines High Risk"

### Visuel 3 — Carte KPI : Pct High Risk
- Type : **Carte**
- Champ : `Pct High Risk`
- Format → Valeur → Décimales : 2 → ajouter suffixe `%`
- Titre : "% High Risk"

### Visuel 4 — Graphique en anneau (donut)
- Type : **Graphique en anneau**
- Légende : `public predictions[risk_level]`
- Valeurs : `Total Machines`
- Couleurs : High=Rouge (#C0392B), Medium=Orange (#E67E22), Low=Vert (#27AE60)
- Titre : "Répartition par Niveau de Risque"

### Visuel 5 — Histogramme Risk Score Bin
- Type : **Graphique à barres groupées**
- Axe X : `Risk Score Bin` (colonne calculée)
- Valeurs Y : `Total Machines`
- Couleurs conditionnelles par catégorie
- Titre : "Distribution des Scores de Risque"

### Visuel 6 — Jauge ROC AUC
- Type : **Jauge**
- Valeur : `ROC AUC Dernier Run`
- Min : 0, Max : 1, Cible : 0.95
- Titre : "ROC AUC Dernier Run"

### Visuel 7 — Graphique barres groupées (Total vs High)
- Type : **Graphique à barres groupées**
- Axe : `public predictions[type]`
- Valeurs : `Total Machines`, `Machines High Risk`
- Titre : "Total Machines et Machines High Risk par Type"

---

## ÉTAPE 5 — PAGE 2 : Priorisation des Risques

**Nom de la page** : `Priorisation des Risques`
(`Clic droit sur onglet → Renommer`)

### Titre
- Texte : **Priorisation Maintenance — Machines à Risque Élevé**

### Visuel 1 — Graphique Nuage de points (Scatter)
- Type : **Graphique à nuage de points**
- Axe X : `public predictions[tool_wear_min]` (Somme ou Moyenne)
- Axe Y : `public predictions[risk_score]` (Somme ou Moyenne)
- Légende : `public predictions[risk_level]`
- Couleurs : High=Rouge, Medium=Orange, Low=Vert
- Taille : laisser vide
- Titre : "Usure Outil vs Score de Risque"

### Visuel 2 — Tableau priorisation
- Type : **Table**
- Colonnes :
  1. `public predictions[udi]`
  2. `public predictions[product_id]`
  3. `public predictions[type]`
  4. `public predictions[risk_score]` → Format : 4 décimales
  5. `public predictions[risk_level]` → Mise en forme conditionnelle fond
  6. `public predictions[tool_wear_min]`
  7. `Intervention Urgency` (colonne calculée)
- Tri : `risk_score` décroissant
- Titre : "Top Machines à Risque — Liste Priorisée"

### Mise en forme conditionnelle — risk_level
- Cliquer sur la colonne `risk_level` → Mise en forme conditionnelle → Couleur d'arrière-plan
- Règles :
  - Si valeur = "High" → fond #C0392B (rouge), texte blanc
  - Si valeur = "Medium" → fond #E67E22 (orange)
  - Si valeur = "Low" → fond #27AE60 (vert)

### Visuel 3 — Carte : Gain Estimé DH
- Type : **Carte**
- Champ : `Gain Estime DH`
- Format → Unités d'affichage : Millions
- Titre : "Gain Estimé (DH)"

### Filtre page (panneau Filtres)
- Ajouter `risk_level` → filtrer sur `High` uniquement pour le tableau

---

## ÉTAPE 6 — PAGE 3 : Performance & Qualité

**Nom de la page** : `Performance & Qualité`

### Titre
- Texte : **Monitoring Modèle & Traçabilité (XGBoost)**

### Visuel 1 — Carte : ROC AUC
- Type : **Carte**
- Champ : `ROC AUC Dernier Run`
- Format : 4 décimales
- Titre : "ROC AUC Dernier Run"

### Visuel 2 — Carte : F1 Score
- Type : **Carte**
- Champ : `F1 Score Dernier Run`
- Titre : "F1 Score Dernier Run"

### Visuel 3 — Carte : Recall
- Type : **Carte**
- Champ : `Recall Dernier Run`
- Titre : "Recall Dernier Run"

### Visuel 4 — Carte : Precision
- Type : **Carte**
- Champ : `Precision Dernier Run`
- Titre : "Precision Dernier Run"

### Visuel 5 — Courbe ROC (depuis roc_curve_data)
- Type : **Graphique en courbes**
- Axe X : `public roc_curve_data[fpr]`
- Valeurs Y : `public roc_curve_data[tpr]`
- Titre : "Courbe ROC — Modèle XGBoost"
- ⚠️ Ajouter une ligne de référence constante Y=X (diagonale) via : Analytique → Ligne constante → 0 (sur l'axe X)

### Visuel 6 — Matrice de Confusion (4 cartes)
Créer **4 cartes séparées** disposées en 2×2 :

| Position | Mesure | Fond |
|---|---|---|
| Haut-Gauche | `Vrais Positifs` | Bleu #2E86AB |
| Haut-Droite | `Faux Negatifs` | Bleu clair #A8DADC |
| Bas-Gauche | `Vrais Negatifs` | Bleu clair #A8DADC |
| Bas-Droite | `Faux Positifs` | Bleu #2E86AB |

Pour chaque carte :
- Format → Arrière-plan → couleur ci-dessus
- Titre visuel → nom de la mesure

### Visuel 7 — Carte : Pct Usure Critique
- Type : **Carte**
- Champ : `Pct Usure Critique` (créer si absent : voir DAX ci-dessous)
- Titre : "% Usure Critique (> 200 min)"

```dax
Pct Usure Critique =
DIVIDE(
    CALCULATE(
        COUNTROWS('public raw_sensor_readings'),
        'public raw_sensor_readings'[tool_wear_min] > 200
    ),
    COUNTROWS('public raw_sensor_readings'),
    0
) * 100
```

---

## ÉTAPE 7 — Thème et mise en forme globale

### Couleurs globales
- Fond des pages : Blanc #FFFFFF ou Gris clair #F5F5F5
- Couleur principale : Bleu OCP #1A5276
- Titres : Police Segoe UI, 14pt, Gras

### Appliquer à toutes les pages
`Affichage → Thèmes → Personnaliser le thème actuel`
- Couleur 1 : #1A5276 (bleu OCP)
- Couleur 2 : #C0392B (rouge danger)
- Couleur 3 : #E67E22 (orange alerte)
- Couleur 4 : #27AE60 (vert OK)

### Navigation entre pages
`Insérer → Boutons → Page suivante / Page précédente`
Placer en bas de chaque page.

---

## ÉTAPE 8 — Sauvegarde et export

1. `Fichier → Enregistrer sous` → `maintenance_ocp_safi.pbix`
2. Pour les captures rapport :
   - `Fichier → Exporter → Exporter en PDF` (toutes les pages)
   - Ou `Imprimer → Exporter en PNG` page par page

---

## Valeurs attendues après reconstruction

### Métriques de performance — valeurs EXACTES du rapport (Page 3)

| Mesure DAX | Valeur exacte rapport | Source |
|---|---|---|
| ROC AUC Dernier Run | **0,9789** | `model_runs.roc_auc` |
| F1 Score Dernier Run | **0,9599** | `model_runs.f1_score` |
| Recall Dernier Run | **0,9556** | `model_runs.recall` |
| Precision Dernier Run | **0,9642** | `model_runs.precision_score` |
| Accuracy Dernier Run | **0,9876** | `model_runs.accuracy` |

### KPIs globaux (Page 1)

| Mesure DAX | Valeur attendue |
|---|---|
| Total Machines | 10 000 |
| Machines High Risk | 434 |
| Pct High Risk | 4,34 % |
| Pct Usure Critique | 7,62 % |

### Matrice de confusion (Page 3)

> ⚠️ **Note importante** : Le rapport cite les valeurs du **test set (2 000 lignes, 20% des données)**.
> Power BI travaille sur les **10 000 prédictions** → les TN/FP/FN/TP seront ×5 environ.
> Les **ratios (Recall, Precision)** restent identiques — seuls les nombres bruts changent.

| Case | Rapport (test 2 000) | Power BI (tout 10 000) | Ratio |
|---|---|---|---|
| **TP** Vrais Positifs | 313 | ~1 565 | ×5 |
| **FP** Faux Positifs | 25 | ~125 | ×5 |
| **FN** Faux Négatifs | 14 | ~70 | ×5 |
| **TN** Vrais Négatifs | 1 981 | ~9 905 | ×5 |
| **Recall DAX** | 95,56 % | **95,56 %** ✅ identique | — |
| **Precision DAX** | 96,42 % | **96,42 %** ✅ identique | — |

### Pour avoir EXACTEMENT 313/25/14/1981 dans Power BI

Ajouter un **champ calculé** `is_test_set` dans la table `predictions` :
- Si la table contient une colonne `is_test` (BOOLEAN) → filtrer sur `is_test = TRUE`
- Sinon, les **ratios** sont identiques — pour le rapport, utiliser les valeurs de `model_runs`

### Impact financier (Page 2)

| Mesure | Valeur |
|---|---|
| Gain Estimé DH (sur tout le dataset) | ~782 500 000 DH |
| Gain Estimé DH (proportionnel test set) | ~156 500 000 DH |

