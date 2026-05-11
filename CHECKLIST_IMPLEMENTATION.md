# Checklist — Implémentation des Améliorations du Rapport PFE

**Rapport :** Maintenance Prédictive pour OCP Safi  
**Statut :** Améliorations apportées, prêt pour finalisation  
**Date :** 2024

---

## Phase 1 : Vérification des Modifications ✓

- [x] Introduction générale remaniée (contexte mondial → marocain → industriel → projet)
- [x] Section "Contraintes du projet" ajoutée
- [x] Impact financier documenté (coûts arrêts non planifiés)
- [x] Aspect MGSI renforcé (gouvernance, BI, KPI, transformation digitale)
- [x] 8 placeholders pour images intégrés
- [x] Ton naturel & académique appliqué partout
- [x] Section "Note sur les améliorations" ajoutée
- [x] Dossier `/images/` créé avec README.md

---

## Phase 2 : Création des Images (À FAIRE) 🎨

### Image 1 : Architecture Système
- [ ] Créer `architecture_systeme.png`
- [ ] Montrer : Couche Ingestion/ML → PostgreSQL → Power BI
- [ ] Format : PNG, 1200×800px, 300 DPI
- [ ] Placer dans : `/images/`

**Description pour créateurs (Canva, Draw.io, PowerPoint) :**
```
┌──────────────────────┐
│   Couche Ingestion   │
│   Python + XGBoost   │───────┐
└──────────────────────┘       │
                               ↓
                    ┌──────────────────────┐
                    │  PostgreSQL (DB)     │
                    │  • Raw Readings      │
                    │  • Cleaned Data      │
                    │  • Model Runs        │
                    │  • Predictions       │
                    │  • Vues SQL          │
                    └──────────────────────┘
                               │
                               ↓
                    ┌──────────────────────┐
                    │    Power BI (BI)     │
                    │  Dashboard 3 pages   │
                    │  • KPIs              │
                    │  • Maintenance Top50 │
                    │  • Qualité Modèle    │
                    └──────────────────────┘
```

---

### Image 2 : Pipeline ETL
- [ ] Créer `pipeline_etl.png`
- [ ] Montrer flux : Données Brutes → Imputation → Écrêtage → Features → Entraînement
- [ ] Format : PNG, 1000×600px, 300 DPI
- [ ] Placer dans : `/images/`

**Description (flux horizontal) :**
```
Données Brutes (CSV) 
    ↓
[Imputation NaN] 
    ↓
[Écrêtage ±3σ] 
    ↓
[Feature Engineering] 
    ↓
[Normalisation] 
    ↓
[Train/Test Split 80/20] 
    ↓
Données Prêtes pour ML
```

---

### Image 3 : Matrice de Confusion
- [ ] Créer `confusion_matrix.png`
- [ ] Format : Heatmap avec couleurs (rouge/vert pour FP/TP)
- [ ] Montrer : TN=1981, FP=25, FN=14, TP=313
- [ ] Format : PNG, 800×800px, 300 DPI
- [ ] Placer dans : `/images/`

**Valeurs à intégrer :**
| | Panne (Pred) | Sain (Pred) |
|---|---|---|
| **Panne (Réel)** | 313 (TP) | 14 (FN) |
| **Sain (Réel)** | 25 (FP) | 1981 (TN) |

---

### Image 4 : Feature Importance
- [ ] Créer `feature_importance.png`
- [ ] Format : Graphique en barres horizontales
- [ ] Montrer : tool_wear (0.453), torque (0.216), process_temp (0.183), power (0.065), etc.
- [ ] Format : PNG, 1000×600px, 300 DPI
- [ ] Placer dans : `/images/`

**Valeurs à intégrer :**
```
tool_wear_min        ████████████████████░ 0.453
torque_nm            ██████████░░░░░░░░░░░ 0.216
process_temperature  █████████░░░░░░░░░░░░ 0.183
power                ██░░░░░░░░░░░░░░░░░░░ 0.065
rotational_speed     █░░░░░░░░░░░░░░░░░░░░ 0.051
temp_diff            ░░░░░░░░░░░░░░░░░░░░░ 0.020
air_temperature      ░░░░░░░░░░░░░░░░░░░░░ 0.009
type_encoded         ░░░░░░░░░░░░░░░░░░░░░ 0.003
```

---

### Image 5 : PostgreSQL Schema
- [ ] Créer `postgresql_schema.png`
- [ ] Format : Diagramme entité-relation (ERD)
- [ ] Montrer : 4 tables + clés étrangères
- [ ] Format : PNG, 1200×800px, 300 DPI
- [ ] Placer dans : `/images/`

**Entités à montrer :**
```
┌─ raw_sensor_readings ─┐
│ • udi (PK)            │
│ • product_id          │
│ • type, temps, RPM... │
└───────────────────────┘
       ↓ (FK: udi)
       
┌─ cleaned_sensor_readings ─┐
│ • clean_id (PK)           │
│ • udi (FK)                │
│ • temp_diff, power...     │
└───────────────────────────┘

┌─ model_runs ─┐
│ • run_id (PK)│
│ • métriques  │
└───────────────┘
   ↑ (FK: run_id)
   
┌─ predictions ─────┐
│ • pred_id (PK)    │
│ • udi (FK)        │
│ • run_id (FK)     │
│ • risk_score      │
└───────────────────┘
```

---

### Image 6 : Power BI Dashboard — Page 1 (KPIs)
- [ ] Créer `powerbi_page1_kpi.png`
- [ ] Format : Capture dashboard ou mockup Power BI
- [ ] Montrer : KPIs clés (nombre machines, machines à risque, dispo, taux prédiction)
- [ ] Format : PNG, 1600×900px, 300 DPI
- [ ] Placer dans : `/images/`

**Éléments à inclure :**
```
╔════════════════════════════════════════════════════════════════════╗
║                    TABLEAU DE BORD PRÉDICTIVE MAINTENANCE          ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Total Machines: 10,661     Machines Risque Élevé: 342            ║
║  Disponibilité: 92.3%       Prédictions: 10,000                   ║
║                                                                    ║
║  Taux Panne Réel: 3.19%     Tendance: ↑ (bon)                     ║
║                                                                    ║
║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ ║
║  │ Défaillances/   │  │ Distribution     │  │ Tendance         │ ║
║  │ Mois            │  │ Risques          │  │ Dispo.           │ ║
║  │                │  │                  │  │                 │ ║
║  │ [Chart here]   │  │ H: 342 (3.2%)    │  │ 90→92→94→96%     │ ║
║  │                │  │ M: 1,200 (11.2%) │  │ [Trend up]       │ ║
║  │                │  │ L: 9,119 (85.5%) │  │                 │ ║
║  └──────────────────┘  └──────────────────┘  └──────────────────┘ ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

### Image 7 : Power BI Dashboard — Page 2 (Maintenance Priorities)
- [ ] Créer `powerbi_page2_maintenance.png`
- [ ] Format : Tableau ou liste Top 50 machines
- [ ] Montrer : Machine ID, Risk Score, Dernier arrêt, Actions recommandées
- [ ] Format : PNG, 1600×900px, 300 DPI
- [ ] Placer dans : `/images/`

**Éléments à inclure :**
```
╔════════════════════════════════════════════════════════════════════╗
║           TOP 50 PRIORITÉS MAINTENANCE — ACTIONS RECOMMANDÉES      ║
╠═══════════╦════════════╦═════════╦═══════════════════════════════╣
║ Priorité  ║ Machine ID ║ Score   ║ Action                        ║
╠═══════════╬════════════╬═════════╬═══════════════════════════════╣
║ 1         ║ M-0001     ║ 0.89    ║ ⚠️ URGENCE — Maintenance de suite
║ 2         ║ M-0042     ║ 0.87    ║ ⚠️ URGENCE — Remplacement joint
║ 3         ║ M-0156     ║ 0.85    ║ ⚠️ URGENCE — Révision complète
║ ...       ║ ...        ║ ...     ║ ...
║ 50        ║ M-5234     ║ 0.50    ║ 🔧 Surveillance — Maintenance prévue
╚═══════════╩════════════╩═════════╩═══════════════════════════════╝
```

---

### Image 8 : Power BI Dashboard — Page 3 (Model Quality)
- [ ] Créer `powerbi_page3_quality.png`
- [ ] Format : Métriques de performance + confusion matrix
- [ ] Montrer : ROC-AUC 0.9789, Precision 0.9642, Recall 0.9556, Confusion Matrix
- [ ] Format : PNG, 1600×900px, 300 DPI
- [ ] Placer dans : `/images/`

**Éléments à inclure :**
```
╔════════════════════════════════════════════════════════════════════╗
║          QUALITÉ DU MODÈLE — MÉTRIQUES DE PERFORMANCE              ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ROC-AUC: 0.9789 ✅      Precision: 0.9642 ✅                     ║
║  Recall: 0.9556 ✅        F1-Score: 0.9599 ✅                     ║
║  Accuracy: 0.9876 ✅                                               ║
║                                                                    ║
║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ ║
║  │ Matrice Confusion│  │ Courbe ROC       │  │ Version Modèle   │ ║
║  │                │  │                  │  │                 │ ║
║  │    1981 | 25  │  │ [ROC curve plot]  │  │ XGBoost v1.2    │ ║
║  │     14 | 313 │  │ AUC = 0.9789      │  │ Entraîné: 2024  │ ║
║  │                │  │                  │  │ 10k données     │ ║
║  └──────────────────┘  └──────────────────┘  └──────────────────┘ ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Phase 3 : Intégration des Images (À FAIRE) 📁

- [ ] Créer un dossier `/images/` s'il n'existe pas
- [ ] Copier les 8 images PNG dans ce dossier
- [ ] Vérifier les noms exactement : 
  - [ ] architecture_systeme.png
  - [ ] pipeline_etl.png
  - [ ] confusion_matrix.png
  - [ ] feature_importance.png
  - [ ] postgresql_schema.png
  - [ ] powerbi_page1_kpi.png
  - [ ] powerbi_page2_maintenance.png
  - [ ] powerbi_page3_quality.png
- [ ] Structure finale :
  ```
  ENSAO_Template/
  └── Modèle Rapport/
      ├── rapport.tex
      ├── images/
      │   ├── README.md (guide)
      │   ├── architecture_systeme.png
      │   ├── pipeline_etl.png
      │   ├── confusion_matrix.png
      │   ├── feature_importance.png
      │   ├── postgresql_schema.png
      │   ├── powerbi_page1_kpi.png
      │   ├── powerbi_page2_maintenance.png
      │   └── powerbi_page3_quality.png
      └── ...
  ```

---

## Phase 4 : Compilation LaTeX (À FAIRE) 🔨

### Option 1 : Compilation locale
- [ ] Ouvrir terminal dans le dossier `/Modèle Rapport/`
- [ ] Exécuter :
  ```bash
  pdflatex rapport.tex
  ```
- [ ] Exécuter :
  ```bash
  bibtex rapport
  ```
- [ ] Exécuter (2x) :
  ```bash
  pdflatex rapport.tex
  pdflatex rapport.tex
  ```
- [ ] Vérifier : `rapport.pdf` créé avec succès

### Option 2 : Overleaf (recommandé)
- [ ] Aller sur Overleaf.com
- [ ] Créer un nouveau projet (Blank Project)
- [ ] Upload `rapport.tex`
- [ ] Upload dossier `images/` (zip puis extract, ou file-by-file)
- [ ] Cliquer "Recompile"
- [ ] Vérifier le PDF généré

---

## Phase 5 : Vérification du PDF (À FAIRE) ✅

- [ ] Ouvrir `rapport.pdf`
- [ ] Vérifier que les 8 images apparaissent aux bons emplacements
- [ ] Chapitre 4 : architecture_systeme.png présente
- [ ] Chapitre 5 (Nettoyage) : pipeline_etl.png présente
- [ ] Chapitre 5 (ML - Confusion) : confusion_matrix.png présente
- [ ] Chapitre 5 (ML - Features) : feature_importance.png présente
- [ ] Chapitre 5 (PostgreSQL) : postgresql_schema.png présente
- [ ] Chapitre 6 (Résultats) : 3 dashboards Power BI présents
- [ ] Vérifier aucune erreur LaTeX
- [ ] Vérifier tous les liens fonctionnent (\ref, \cite)
- [ ] Table des matières correcte
- [ ] Pages numérotées correctement

---

## Phase 6 : Finalisations (À FAIRE) 📝

- [ ] Lire la section "Note sur les améliorations" (fin du rapport)
- [ ] Personnaliser si nécessaire (noms d'encadrants, dates, etc.)
- [ ] Ajouter votre nom dans la page de titre
- [ ] Vérifier tous les détails spécifiques (noms, entreprises, dates)
- [ ] Imprimer ou préparer pour soutenance
- [ ] Faire relire par encadrant si possible

---

## Phase 7 : Présentation & Soutenance (À FAIRE) 🎯

- [ ] Préparer diapos PowerPoint/Keynote basées sur les figures
- [ ] Mémoriser les points clés de chaque chapitre
- [ ] S'entraîner à la présentation (10-15 min)
- [ ] Imprimer copies du rapport pour le jury (4-5 copies)
- [ ] Préparer démo Power BI si possible (live ou screenshot)
- [ ] Mettre en avant :
  - Rigueur méthodologique (contraintes documentées)
  - Aspect MGSI (gouvernance, KPI, BI)
  - Performance ML (ROC-AUC 0.9789)
  - Impact opérationnel et financier

---

## Ressources Additionnelles

### Documentation du Projet
- ✅ `RAPPORT_MODIFICATIONS.md` — Détail complet des modifications
- ✅ `MODIFICATIONS_VISUELLES.txt` — Résumé visuel
- ✅ `SYNTHESE_AMELIORATIONS.txt` — Vue d'ensemble rapide
- ✅ `images/README.md` — Guide pour intégrer les images

### Outils Recommandés pour Créer les Images
- **Canva Pro** (facile, templates modernes)
- **Draw.io** / **Diagrams.net** (diagrammes techniques, gratuit)
- **Microsoft PowerPoint** (captures et mockups)
- **Python matplotlib/seaborn** (graphiques ML authentiques)
- **Figma** (design professionnel)

### Ressources LaTeX
- Overleaf.com — Éditeur en ligne, compilation instant
- TeXLive / MiKTeX — Distribution locale LaTeX
- LaTeX Documentation — documentation officielle

---

## Statut de Complétion

**Avant améliorations :** ████░░░░░░ 40% (structure de base)  
**Après améliorations :** ████████░░ 80% (contenu enrichi)  
**Après images :** ██████████ 100% (complet et professionnel)

**Vous êtes ici →** Phase 1 ✅ Phase 2 ⏳ Phase 3 ⏳ Phase 4 ⏳ Phase 5 ⏳ Phase 6 ⏳ Phase 7 ⏳

---

## Questions Fréquentes

**Q : Les images sont obligatoires ?**  
A : Fortement recommandées pour crédibilité professionnelle, mais le rapport compile sans elles (avec avertissements).

**Q : Peux-je utiliser d'autres outils pour les images ?**  
A : Oui ! Canva, Draw.io, PowerPoint, Figma, Python (matplotlib)... tous les outils qui produisent PNG/PDF conviennent.

**Q : Peut-on compiler sur Overleaf ?**  
A : Oui, c'est même recommandé. Upload rapport.tex + dossier images/, Overleaf compile automatiquement.

**Q : Peut-on utiliser des images générées par IA (Midjourney, DALL-E) ?**  
A : Possible, mais les diagrammes techniques (architecture, pipeline, schema DB) sont mieux créés avec des outils dédiés pour l'authenticité.

**Q : Combien de temps pour compléter tout ?**  
A : ~2-4 heures (dépend de la qualité des images et votre expérience LaTeX/design)

---

**✨ Bon courage pour finir votre rapport PFE ! ✨**
