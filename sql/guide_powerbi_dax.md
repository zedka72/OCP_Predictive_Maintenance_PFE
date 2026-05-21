# Guide d'application des DAX corrigés dans Power BI

## Problèmes identifiés et corrections apportées

| Problème | Cause | Correction v2 |
|---|---|---|
| F1 = 0,64 au lieu de 0,96 | Ancien run dans `model_runs` | VAR `dernierRun` filtre sur `MAX(run_date)` |
| Recall = 0,87 au lieu de 0,96 | Même cause | Même correction |
| Vrais Négatifs sous-estimé | Filtre `= "Low"` ignorait Medium | Filtre `<> "High"` inclut Low + Medium |
| Pct sans `%` | Pas de formatage | Nouvelles mesures Label avec FORMAT() |

---

## Étapes dans Power BI Desktop

### ÉTAPE 1 — Ouvrir l'éditeur de mesures

1. Ouvrir votre fichier `.pbix`
2. Cliquer sur la table **`public predictions`** dans le panneau Données (droite)
3. Onglet **Outils de table** → **Nouvelle mesure**

---

### ÉTAPE 2 — Remplacer/créer les mesures corrigées

Pour chaque mesure ci-dessous, allez dans **Accueil → Nouvelle mesure** (ou cliquez sur la mesure existante pour la modifier) et collez la formule.

#### 🔴 CORRECTIONS PRIORITAIRES (Page 3)

**ROC AUC Dernier Run** — Remplacer par :
```dax
ROC AUC Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[roc_auc]), 'public model_runs'[run_date] = dernierRun)
```

**F1 Score Dernier Run** — Remplacer par :
```dax
F1 Score Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[f1_score]), 'public model_runs'[run_date] = dernierRun)
```

**Recall Dernier Run** — Remplacer par :
```dax
Recall Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[recall]), 'public model_runs'[run_date] = dernierRun)
```

**Precision Dernier Run** — NOUVELLE mesure :
```dax
Precision Dernier Run =
VAR dernierRun =
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs'))
RETURN
    CALCULATE(MAX('public model_runs'[precision_score]), 'public model_runs'[run_date] = dernierRun)
```

---

#### 🔴 CORRECTION MATRICE DE CONFUSION (Page 3)

**Vrais Negatifs** — Remplacer par (correction critique) :
```dax
Vrais Negatifs =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_level] <> "High",
    'public predictions'[actual_failure] = 0
)
```

**Faux Negatifs** — Remplacer par :
```dax
Faux Negatifs =
CALCULATE(
    COUNTROWS('public predictions'),
    'public predictions'[risk_level] <> "High",
    'public predictions'[actual_failure] = 1
)
```

---

#### 🟠 NOUVELLES MESURES UTILES (à créer)

**Recall DAX** (calculé depuis la matrice, indépendant de model_runs) :
```dax
Recall DAX =
DIVIDE([Vrais Positifs], [Vrais Positifs] + [Faux Negatifs], 0)
```

**Precision DAX** :
```dax
Precision DAX =
DIVIDE([Vrais Positifs], [Vrais Positifs] + [Faux Positifs], 0)
```

**Accuracy DAX** :
```dax
Accuracy DAX =
DIVIDE(
    [Vrais Positifs] + [Vrais Negatifs],
    [Vrais Positifs] + [Vrais Negatifs] + [Faux Positifs] + [Faux Negatifs],
    0
)
```

**Gain Estimé DH** :
```dax
Gain Estimé DH =
([Vrais Positifs] * 50000) - ([Faux Positifs] * 3000)
```

**Pct High Risk Label** (avec %) :
```dax
Pct High Risk Label =
FORMAT(DIVIDE([Machines High Risk], [Total Machines], 0) * 100, "0.00") & " %"
```

**Date Dernier Run** :
```dax
Date Dernier Run =
FORMAT(
    CALCULATE(MAX('public model_runs'[run_date]), ALL('public model_runs')),
    "DD/MM/YYYY HH:MM"
)
```

---

#### 🟡 COLONNE CALCULÉE — Intervention Urgency (amélioration Page 2)

Dans la table **`public predictions`** → **Nouvelle colonne** :
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

### ÉTAPE 3 — Mettre à jour les visuels

#### Page 1 — KPIs
- Carte "Pct High Risk" → remplacer la mesure par **`Pct High Risk Label`**
- Ajouter une carte **"Date Dernier Run"** pour montrer la fraîcheur des données

#### Page 3 — Qualité Modèle
- Remplacer les cartes F1/Recall par les nouvelles mesures
- Ajouter 2 cartes supplémentaires : **Precision** et **Accuracy**
- Les 4 carrés de la matrice de confusion se mettront à jour automatiquement

#### Page 2 — Priorisation
- Ajouter la colonne **Intervention Urgency** dans le tableau
- Trier par Urgency (URGENT en premier) puis par risk_score décroissant
- Ajouter une mise en forme conditionnelle : rouge=URGENT, orange=PRIORITAIRE

---

### ÉTAPE 4 — Actualiser les données

Après modifications :
1. `Accueil → Actualiser` (ou **Maj + F5**)
2. Vérifier que les valeurs Page 3 affichent ≈ 0,9789 (ROC-AUC), ≈ 0,9599 (F1), ≈ 0,9556 (Recall)

> ⚠️ **Important** : Si les valeurs restent incorrectes (0,64 / 0,87), c'est que la table
> `model_runs` ne contient pas encore le bon run. Il faut démarrer PostgreSQL et exécuter :
> `python -m src.entrainement.entrainer_modele`
> puis actualiser Power BI.

---

## Résumé des valeurs attendues après correction

| Mesure | Valeur attendue | Page |
|---|---|---|
| Total Machines | 10 000 | 1 |
| Machines High Risk | 434 | 1 |
| Pct High Risk | 4,34 % | 1 |
| ROC AUC Dernier Run | 0,9789 | 3 |
| F1 Score Dernier Run | 0,9599 | 3 |
| Recall Dernier Run | 0,9556 | 3 |
| Precision Dernier Run | 0,9642 | 3 |
| Accuracy Dernier Run | 0,9876 | 3 |
| Vrais Positifs | 313 | 3 |
| Faux Positifs | 25 | 3 |
| Vrais Négatifs | 1981 | 3 |
| Faux Négatifs | 14 | 3 |
| Gain Estimé DH | ~14 000 000 | 2 |
