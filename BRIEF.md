# BRIEF — Mission Espace : Niveaux 2-4

## Context
Jeu éducatif "Mission Espace" pour deux enfants sur Linux Mint 22.3 XFCE.
- **Romy** — CE1 (7-8 ans), profil easy
- **Oscar** — CM1 (9-10 ans), profil medium

## What exists (Level 1 — DONE)
- 8 missions Romy + 9 missions Oscar
- Thème informatique : créer/déplacer/renommer des fichiers, terminal, fond d'écran
- GUI tkinter animée (fond étoilé, thème spatial)
- Codes secrets : ETOILE-ROMY-2026 / COSMOS-OSCAR-2026
- Checks : file_exists, file_contains, file_moved, file_renamed, folder_exists, wallpaper_changed

## What is requested
**3 levels supplémentaires** (2, 3, 4) avec :
- Minimum de lecture → **maximum d'illustrations**
- Contenu multidisciplinaire : maths, français, anglais, sciences
- Conforme au programme Éducation Nationale CE1/CM1
- Reward (code secret) à la fin de chaque niveau
- Reward final ultime à la fin du niveau 4

## Constraints
- Python stdlib + **Pillow 12.2.0** disponible → illustrations PNG générées par script
- Aucun autre package externe
- Toutes les missions utilisent file_contains ou file_exists ou folder_exists comme check
  (les enfants écrivent la réponse dans un fichier texte)
- Missions indépendantes entre les deux joueurs (aucune progression partagée)
- Fonctionne en tant qu'utilisateur sans sudo
- Temps restant estimé : toute la nuit (~8h)

## Level structure
| Level | Thème | Romy (CE1) | Oscar (CM1) |
|-------|-------|------------|-------------|
| 1 | Informatique | 8 missions ✓ | 9 missions ✓ |
| 2 | Mathématiques | 8 missions | 9 missions |
| 3 | Français + Anglais | 8 missions | 9 missions |
| 4 | Sciences | 6 missions | 7 missions |
| **Total** | | **30 missions** | **34 missions** |

## Illustration system
- Script `generate_assets.py` génère tous les PNG avec Pillow
- Taille : 460×280 px, fond sombre (#0B0B2E), couleurs vives
- Dossier : `assets/illustrations/romy/` et `assets/illustrations/oscar/`
- Convention : `romy_l2_m01.png`, `oscar_l3_m05.png`
- La GUI charge l'image depuis `mission["image"]` si le champ existe
