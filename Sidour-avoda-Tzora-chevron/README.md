# Sidour Avoda V2

Application de gestion de planning (Hebdo) avec configuration par site.

## Fonctionnalités clés
- Sites multiples avec réglages dédiés:
  - Jours actifs (cases à cocher)
  - Shifts dynamiques (Morning / Afternoon / Night) avec heures personnalisables
  - Validation anti-chevauchement entre shifts (ex: Afternoon 14–22 ⇒ Night start ≥ 22; Night end ≤ Morning start)
- Grille Week Planning et Availabilities qui s’adaptent automatiquement aux réglages du site
- Génération de planning équitable (prise en compte des souhaits, distribution des nuits, trous répartis par jour)
- Alternatives de planning au même score (Next/Previous alternative)
- Gestion et suppression de site, ajout de site avec configuration initiale

## Démarrage (dev)
1. Python 3.10+ recommandé
2. Requirement already satisfied: contourpy==1.3.1 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 1)) (1.3.1)
Requirement already satisfied: cycler==0.12.1 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 2)) (0.12.1)
Requirement already satisfied: fonttools==4.55.2 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 3)) (4.55.2)
Requirement already satisfied: joblib==1.4.2 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 4)) (1.4.2)
Requirement already satisfied: kiwisolver==1.4.7 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 5)) (1.4.7)
Requirement already satisfied: matplotlib==3.9.3 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 6)) (3.9.3)
Requirement already satisfied: numpy==2.0.0 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 7)) (2.0.0)
Requirement already satisfied: packaging==24.2 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 8)) (24.2)
Requirement already satisfied: pandas==2.2.3 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 9)) (2.2.3)
Requirement already satisfied: pillow==11.0.0 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 10)) (11.0.0)
Requirement already satisfied: pyparsing==3.2.0 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 11)) (3.2.0)
Requirement already satisfied: python-dateutil==2.9.0.post0 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 12)) (2.9.0.post0)
Requirement already satisfied: pytz==2024.2 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 13)) (2024.2)
Requirement already satisfied: scikit-learn==1.5.2 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 14)) (1.5.2)
Requirement already satisfied: scipy==1.14.1 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 15)) (1.14.1)
Requirement already satisfied: seaborn==0.13.2 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 16)) (0.13.2)
Requirement already satisfied: setuptools==70.1.1 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 17)) (70.1.1)
Requirement already satisfied: six==1.17.0 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 18)) (1.17.0)
Requirement already satisfied: threadpoolctl==3.5.0 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 19)) (3.5.0)
Requirement already satisfied: tzdata==2024.2 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 20)) (2024.2)
Requirement already satisfied: wheel==0.43.0 in /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages (from -r Sidour-avoda-Tzora-chevron/requirements.txt (line 21)) (0.43.0)
3. 

## Utilisation
- Choisir le site en haut (combobox)
- “Add Site” pour créer un nouveau site (jours + shifts avant création)
- “Manage Site” pour modifier les réglages du site courant, puis “Save settings”
- “Planning creation” pour générer; “Next/Previous alternative” pour parcourir les variantes
- “Fill holes” pour tenter de combler les trous restants

## Notes techniques
- Les jours/shifts sont dynamiques et propagés à:
  - l’UI (grilles)
  - l’algorithme (score, redistribution des trous, limites de nuits, etc.)
- La nuit (22–06) est optionnelle; tout le code évite les KeyError si absente

## Repo
Origin: https://github.com/joey603/Sidour_Avoda_V2.git
