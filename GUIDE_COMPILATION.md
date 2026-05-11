# Guide de Compilation LaTeX — Rapport PFE

**Rapport :** Maintenance Prédictive — OCP Safi  
**Format :** LaTeX (rapport.tex)  
**Sortie attendue :** PDF haute qualité (rapport.pdf)

---

## Prérequis

- ✅ LaTeX installé (TeXLive, MiKTeX, ou MacTeX)
- ✅ `rapport.tex` dans le dossier principal
- ✅ Dossier `images/` avec les 8 images PNG
- ✅ Terminal ou invite de commande

---

## Méthode 1 : Compilation Locale (Recommandée)

### Pour Windows

#### Option A : Command Prompt (cmd.exe)
```cmd
cd "C:\chemin\vers\Modèle Rapport"
pdflatex rapport.tex
bibtex rapport
pdflatex rapport.tex
pdflatex rapport.tex
```

#### Option B : PowerShell
```powershell
cd "C:\chemin\vers\Modèle Rapport"
pdflatex rapport.tex; bibtex rapport; pdflatex rapport.tex; pdflatex rapport.tex
```

#### Option C : Git Bash (si installé)
```bash
cd /c/chemin/vers/Modèle\ Rapport
pdflatex rapport.tex && bibtex rapport && pdflatex rapport.tex && pdflatex rapport.tex
```

---

### Pour macOS & Linux

```bash
# Naviguer vers le dossier
cd ~/chemin/vers/Modèle\ Rapport

# Compiler
pdflatex rapport.tex
bibtex rapport
pdflatex rapport.tex
pdflatex rapport.tex
```

Ou en une seule ligne :
```bash
pdflatex rapport.tex && bibtex rapport && pdflatex rapport.tex && pdflatex rapport.tex
```

---

### Résultat Attendu

```
This is pdfTeX, Version 3.141592653-2.6-1.40.25 (TeX Live 2024)
...
Output written on rapport.pdf (XX pages, XXX bytes).
Transcript written on rapport.log.
```

✅ Le fichier **rapport.pdf** est généré dans le même dossier

---

## Méthode 2 : Compilation via Overleaf (En Ligne - Recommandée)

Overleaf est un éditeur LaTeX en ligne qui élimine les problèmes d'installation locales.

### Étape 1 : Créer un compte Overleaf
1. Aller sur **www.overleaf.com**
2. Cliquer "Sign up" (gratuit)
3. Entrer email et créer mot de passe

### Étape 2 : Créer un nouveau projet
1. Cliquer "New Project"
2. Sélectionner "Blank Project"
3. Nommer le projet : "PFE_Maintenance_Predictive"

### Étape 3 : Upload du fichier rapport
1. Cliquer sur l'icône **📎 Upload**
2. Sélectionner `rapport.tex`
3. Attendre l'upload (quelques secondes)

### Étape 4 : Upload du dossier images
#### Option A : Upload via ZIP
1. Compresser le dossier `images/` en ZIP
   - Windows : Clic droit > Envoyer vers > Dossier compressé
   - macOS : Clic droit > Compresser
   - Linux : `zip -r images.zip images/`
2. Upload le fichier ZIP via **📎 Upload** d'Overleaf
3. Overleaf extrait automatiquement les fichiers

#### Option B : Upload fichier par fichier
1. Cliquer **📎 Upload** → "Files"
2. Sélectionner tous les fichiers PNG de `images/`
3. Créer un dossier "images" dans Overleaf si nécessaire (via "New Folder")

### Étape 5 : Compiler
1. Cliquer le grand bouton **"Recompile"** en haut à droite
2. Attendre la compilation (généralement 10-30 sec)
3. Cliquer sur l'icône **🔍 PDF** pour voir le résultat

### Résultat
✅ PDF généré automatiquement, téléchargeable via l'icône **⬇️ Download**

---

## Méthode 3 : Utiliser un Makefile

Si vous compilez souvent, créez un fichier `Makefile` pour automatiser :

### Créer le fichier Makefile

**Fichier :** `Makefile` (dans le même dossier que `rapport.tex`)

```makefile
.PHONY: all clean view

all: rapport.pdf

rapport.pdf: rapport.tex
	pdflatex rapport.tex
	bibtex rapport
	pdflatex rapport.tex
	pdflatex rapport.tex

clean:
	rm -f *.aux *.log *.bbl *.blg *.out *.toc *.lof *.lot

view: rapport.pdf
	open rapport.pdf

.DEFAULT_GOAL := all
```

### Utiliser le Makefile

```bash
# Compiler
make

# Voir le PDF (macOS/Linux)
make view

# Nettoyer les fichiers temporaires
make clean
```

---

## Vérification de la Compilation

### Erreurs Courantes & Solutions

#### Erreur : "File 'images/architecture_systeme.png' not found"
**Cause :** Image manquante ou chemin incorrect

**Solutions :**
1. Vérifier que l'image existe : `ls images/architecture_systeme.png`
2. Vérifier l'orthographe du nom (sensible à la casse sur Linux/macOS)
3. Vérifier que le dossier `images/` est au bon niveau
4. Commentez temporairement la ligne `\includegraphics` si l'image n'existe pas

```latex
% \includegraphics[width=0.85\textwidth]{images/architecture_systeme.png}
```

---

#### Erreur : "Citation 'XXX' on page ... undefined"
**Cause :** Références bibliographiques manquantes

**Solution :** Exécuter `bibtex rapport` avant de compiler à nouveau
```bash
pdflatex rapport.tex && bibtex rapport && pdflatex rapport.tex
```

---

#### Erreur : "Undefined control sequence"
**Cause :** Caractère ou commande LaTeX mal échappée

**Solution :** Vérifier que tous les caractères spéciaux sont correctement encodés en UTF-8. Vérifier la section du rapport où l'erreur se produit (indiquée dans le log).

---

#### Erreur : "Too many unmatched \left" ou "Unmatched \begin{}"
**Cause :** Accolades ou environnements mal fermés

**Solution :** Vérifier qu'il y a autant de `\end{...}` que de `\begin{...}`

---

### Avertissements Non-Bloquants

```
Overfull \hbox (15.00102pt too wide) in paragraph
```
= Les images ou texte débordent légèrement. Généralement ignorable.

```
Underfull \hbox (badness 10000) in paragraph
```
= Espacement de remplissage. Aussi généralement ignorable.

---

## Optimisation du Résultat PDF

### Réduire la taille du PDF
Si le PDF est trop volumineux (>20 MB) :

```bash
# Linux/macOS avec ghostscript
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=rapport_compressed.pdf rapport.pdf
```

### Vérifier la structure du PDF
```bash
# Linux/macOS : lister les pages
pdfinfo rapport.pdf

# Afficher les métadonnées
exiftool rapport.pdf
```

---

## Debugging Avancé

### Voir les détails de compilation
```bash
# Mode verbeux (affiche tous les détails)
pdflatex -interaction=nonstopmode rapport.tex

# Continuer même en cas d'erreur
pdflatex -interaction=scrollmode rapport.tex
```

### Vérifier les fichiers temporaires générés
```bash
# Lister tous les fichiers créés
ls -la *.log *.aux *.bbl *.blg *.out 2>/dev/null
```

### Lire le fichier log complet
```bash
# macOS/Linux
cat rapport.log | grep -i "error\|warning" | head -20

# Windows (PowerShell)
Get-Content rapport.log | Select-String -Pattern "error|warning" | Select-Object -First 20
```

---

## Automatisation Complète (Script)

### Script Bash pour Linux/macOS

**Fichier :** `compile.sh`

```bash
#!/bin/bash

echo "📚 Compilation du Rapport PFE — Maintenance Prédictive"
echo "=================================================="
echo ""

# Vérifier les préalables
if ! command -v pdflatex &> /dev/null; then
    echo "❌ LaTeX n'est pas installé. Installez TeXLive ou MacTeX."
    exit 1
fi

echo "✅ LaTeX détecté"
echo ""

# Compiler
echo "🔨 Étape 1/4 : pdflatex..."
pdflatex rapport.tex > /dev/null 2>&1

echo "🔨 Étape 2/4 : bibtex..."
bibtex rapport > /dev/null 2>&1

echo "🔨 Étape 3/4 : pdflatex (2e pass)..."
pdflatex rapport.tex > /dev/null 2>&1

echo "🔨 Étape 4/4 : pdflatex (3e pass)..."
pdflatex rapport.tex > /dev/null 2>&1

# Vérifier le résultat
if [ -f rapport.pdf ]; then
    echo ""
    echo "✅ Compilation réussie !"
    echo "📄 Fichier généré : rapport.pdf"
    echo ""
    
    # Afficher taille du PDF
    SIZE=$(du -h rapport.pdf | cut -f1)
    PAGES=$(pdfinfo rapport.pdf 2>/dev/null | grep "Pages" | awk '{print $2}')
    echo "📊 Taille : $SIZE | Pages : $PAGES"
else
    echo ""
    echo "❌ Erreur de compilation"
    echo "💾 Voir rapport.log pour les détails"
    exit 1
fi

# Optionnel : ouvrir le PDF
# open rapport.pdf  # macOS
# xdg-open rapport.pdf  # Linux
```

**Utilisation :**
```bash
chmod +x compile.sh
./compile.sh
```

---

### Script Batch pour Windows

**Fichier :** `compile.bat`

```batch
@echo off
setlocal enabledelayedexpansion

echo.
echo Compilation du Rapport PFE - Maintenance Predictive
echo ================================================
echo.

REM Verifier que pdflatex existe
where pdflatex >nul 2>nul
if %errorlevel% neq 0 (
    echo Erreur: pdflatex non trouve. Installez MiKTeX ou TeXLive.
    pause
    exit /b 1
)

echo Etape 1/4: pdflatex...
pdflatex rapport.tex > nul

echo Etape 2/4: bibtex...
bibtex rapport > nul

echo Etape 3/4: pdflatex ^(2e pass^)...
pdflatex rapport.tex > nul

echo Etape 4/4: pdflatex ^(3e pass^)...
pdflatex rapport.tex > nul

REM Verifier le resultat
if exist rapport.pdf (
    echo.
    echo OK: Compilation reussie!
    echo Fichier: rapport.pdf
    
    REM Optionnel: ouvrir le PDF
    REM start rapport.pdf
) else (
    echo.
    echo Erreur de compilation - voir rapport.log
    pause
    exit /b 1
)

pause
```

**Utilisation :** Double-cliquer sur `compile.bat`

---

## Checklist Pré-Compilation

Avant de compiler, vérifier :

- [ ] Le fichier `rapport.tex` existe et est accessible
- [ ] Le dossier `images/` existe et contient 8 images PNG
- [ ] Les noms d'images sont exactement : 
  - [ ] architecture_systeme.png
  - [ ] pipeline_etl.png
  - [ ] confusion_matrix.png
  - [ ] feature_importance.png
  - [ ] postgresql_schema.png
  - [ ] powerbi_page1_kpi.png
  - [ ] powerbi_page2_maintenance.png
  - [ ] powerbi_page3_quality.png
- [ ] LaTeX est installé : `pdflatex --version` fonctionne
- [ ] Au moins 500 MB d'espace disque libre
- [ ] Pas de fichiers `*.aux` ou `*.log` problématiques (nettoyer si erreurs)

---

## Performance & Optimisation

### Temps de compilation typique
- 1ère compilation : 20-40 sec (crée fichiers auxiliaires)
- Recompilations : 10-20 sec (mise à jour)
- Overleaf : 5-15 sec (serveurs puissants)

### Réduire le temps
1. Utiliser Overleaf plutôt que local (plus rapide)
2. Désactiver les images temporairement pendant l'édition
3. Utiliser `pdftex` au lieu de `xelatex` (plus rapide)

---

## Troubleshooting Final

**Si rien ne fonctionne :**

1. Nettoyer tous les fichiers temporaires :
   ```bash
   rm -f *.aux *.log *.bbl *.blg *.out *.toc
   ```

2. Recompiler à partir de zéro :
   ```bash
   pdflatex -interaction=nonstopmode rapport.tex
   ```

3. Si erreur persiste, ouvrir Overleaf et y upload directement

4. Contacter support LaTeX : https://www.overleaf.com/help

---

**✅ Vous êtes prêt à compiler !**

Exécutez simplement :
```bash
pdflatex rapport.tex && bibtex rapport && pdflatex rapport.tex && pdflatex rapport.tex
```

Et votre PDF professionnel sera généré ! 🎉
