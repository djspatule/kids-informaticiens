# DECISIONS & ASSUMPTIONS

## Architecture

**ASSUMED** — Structure de missions plate (mission_01 → mission_30)
Raison : évite de toucher MissionLoader, le tri naturel des noms de fichiers suffit.
Alternative rejetée : sous-dossiers level_1/, level_2/ (nécessite refactoring majeur).

**ASSUMED** — Champ `"level": N` dans chaque mission JSON
Le GUI et StateManager utilisent ce champ pour détecter les transitions de niveau.

**ASSUMED** — La récompense de fin de niveau est affichée DANS le GUI (pas dans un fichier)
Le code secret de niveau est lu depuis `config["levels"][n]["reward"]`.

**ASSUMED** — Missions de réponse mathématique : l'enfant crée un fichier .txt avec la réponse
Check : `file_contains` sur le chemin attendu, insensible à la casse, accepte espaces.
Ex : réponse attendue "42", le check cherche "42" dans le fichier (partial match OK).

**ASSUMED** — Tolérance orthographique pour les réponses en lettres
"sept" est accepté même si l'enfant écrit "Sept" ou " sept " (case_sensitive: false).
Pour les nombres : on cherche le chiffre exact comme substring → "42" matche "42 cm" aussi.

**ASSUMED** — Illustrations : 460×280 px PNG, fond #0B0B2E (noir espace), texte blanc/doré
Générées par `generate_assets.py` à exécuter une fois avant de jouer.

**ASSUMED** — La GUI affiche l'illustration EN HAUT du panneau de mission (au-dessus du titre)
Si pas d'image pour la mission, la zone est masquée (layout s'adapte).

**ASSUMED** — Chaque niveau a son propre "reward screen" (moins élaboré que le final)
Le reward screen de fin de niveau affiche : nom du niveau, code de niveau, "Niveau X terminé !".
Le reward screen FINAL (fin niveau 4) garde l'animation feux d'artifice existante.

**ASSUMED** — Numérotation des missions continues
Romy : mission_01–08 (L1), mission_09–16 (L2), mission_17–24 (L3), mission_25–30 (L4)
Oscar : mission_01–09 (L1), mission_10–18 (L2), mission_19–27 (L3), mission_28–34 (L4)

**ASSUMED** — Pour les missions de science : l'enfant crée des fichiers de "notes" 
(pas de check de contenu sophistiqué — juste file_exists + optionnellement file_contains)

**ASSUMED** — Les missions de langue demandent d'écrire dans un fichier
Ex : "Écris la couleur en anglais dans couleur.txt" → file_contains("red")

## Content

**ASSUMED** — Réponses mathématiques attendues sous forme de chiffres arabes
Ex : "42" pas "quarante-deux" (sauf missions explicitement sur les nombres en lettres)

**ASSUMED** — Pour les missions où l'enfant doit écrire une phrase complète
Le check vérifie seulement un mot-clé (pas la phrase entière) → tolérant aux erreurs

**ASSUMED** — Codes secrets par niveau :
Romy : L1=ETOILE-ROMY-2026, L2=PLANETE-ROMY-2026, L3=GALAXIE-ROMY-2026, L4=UNIVERS-ROMY-2026
Oscar : L1=COSMOS-OSCAR-2026, L2=NEBULA-OSCAR-2026, L3=PULSAR-OSCAR-2026, L4=QUASAR-OSCAR-2026

## Testing

**ASSUMED** — Tests dans `tests/` directory (nouveau)
`tests/test_checks.py` : unit tests des check functions
`tests/test_missions.py` : validation structure JSON + cohérence niveaux
