# Dossier Images — Guide d'intégration

Ce dossier doit contenir toutes les images et figures utilisées dans le rapport LaTeX.

## Images à ajouter

Pour que le rapport compile correctement sans erreurs, placez les images suivantes dans ce dossier :

### Architecture et Vue globale
- **architecture_systeme.png** — Diagramme de l'architecture générale (3 couches : Ingestion/ML, PostgreSQL, Power BI)
  - Recommandation : 1200×800px, format PNG haute qualité

### Pipeline et Traitement des données
- **pipeline_etl.png** — Flux du pipeline ETL montrant : données brutes → nettoyage → features → entraînement
  - Recommandation : 1000×600px

### Machine Learning
- **confusion_matrix.png** — Heatmap de la matrice de confusion (TN, FP, FN, TP)
  - Recommandation : 800×800px ou carré
  
- **feature_importance.png** — Graphique en barres horizontales de l'importance des variables
  - Recommandation : 1000×600px

### Base de données
- **postgresql_schema.png** — Diagramme entité-relation montrant les 4 tables et leurs relations
  - Recommandation : 1200×800px

### Power BI Dashboards
- **powerbi_page1_kpi.png** — Page 1 : KPIs (nombre de machines, machines à risque, indicateurs)
  - Recommandation : 1600×900px (résolution dashboard standard)
  
- **powerbi_page2_maintenance.png** — Page 2 : Top 50 machines prioritaires avec score de risque
  - Recommandation : 1600×900px
  
- **powerbi_page3_quality.png** — Page 3 : Métriques de qualité du modèle et confusion matrix
  - Recommandation : 1600×900px

## Format recommandé

- **Format** : PNG ou PDF (meilleure qualité dans LaTeX)
- **Résolution** : 300 DPI minimum pour impression
- **Compression** : Modérée (pas trop compressé, sinon perte de qualité)

## Alternative pour test rapide

Si vous n'avez pas les images, vous pouvez :

1. **Créer des images vides temporaires** :
   ```bash
   # Créer des PNG vides (1×1 pixel)
   touch architecture_systeme.png
   touch pipeline_etl.png
   # ... etc
   ```

2. **Commenter les `\includegraphics`** dans le LaTeX pour tester le document sans images

3. **Utiliser des placeholders de texte** en remplaçant `\includegraphics` par `\textbf{[IMAGE: architecture\_systeme.png]}`

## Aperçu des sections contenant des images

Le rapport inclut des références aux images suivantes aux emplacements suivants :

1. **Chapitre 4, Section "Architecture globale"** — architecture_systeme.png
2. **Chapitre 5, Section "Nettoyage et prétraitement"** — pipeline_etl.png
3. **Chapitre 5, Section "Matrice de confusion"** — confusion_matrix.png
4. **Chapitre 5, Section "Importance des variables"** — feature_importance.png
5. **Chapitre 5, Section "Modèle de données relationnel"** — postgresql_schema.png
6. **Chapitre 5, Section "Validation du modèle / Pilier 3"** — powerbi_page1_kpi.png, powerbi_page2_maintenance.png, powerbi_page3_quality.png

## Compilation LaTeX

Pour compiler le rapport avec les images :

```bash
# Windows
pdflatex rapport.tex
bibtex rapport
pdflatex rapport.tex
pdflatex rapport.tex

# Linux/Mac
pdflatex rapport.tex && bibtex rapport && pdflatex rapport.tex && pdflatex rapport.tex
```

Si une image est manquante, LaTeX affichera un avertissement mais continuera la compilation.
