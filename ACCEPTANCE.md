# ACCEPTANCE CRITERIA

Chaque item doit être vérifiable par une commande ou un test.

## A1 — Missions JSON
- [ ] `missions/romy/` contient exactement 30 fichiers (mission_01 → mission_30)
- [ ] `missions/oscar/` contient exactement 34 fichiers (mission_01 → mission_34)
- [ ] `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('missions/**/*.json', recursive=True)]"` → no error
- [ ] Chaque JSON a les champs : id, level, title, description, hint, check, success_message, points
- [ ] Les champs `level` vont de 1 à 4 sans trous
- [ ] Les missions de niveau 1 sont inchangées (ids mission_01–mission_08 pour Romy)

## A2 — Config
- [ ] `config/romy.json` contient `"total_missions": 30` et un champ `"levels"` (liste de 4 niveaux)
- [ ] `config/oscar.json` contient `"total_missions": 34` et un champ `"levels"`
- [ ] Chaque niveau dans `"levels"` a : id, name, reward, missions_count

## A3 — Illustrations
- [ ] `python3 generate_assets.py` s'exécute sans erreur
- [ ] Après exécution, `ls assets/illustrations/romy/ | wc -l` ≥ 22 (levels 2-4)
- [ ] Après exécution, `ls assets/illustrations/oscar/ | wc -l` ≥ 25
- [ ] Chaque image PNG est valide : `python3 -c "from PIL import Image; Image.open('...').verify()"`
- [ ] Chaque mission de niveau 2-4 a un champ `"image"` pointant vers son illustration

## A4 — GUI multi-niveau
- [ ] `python3 -m py_compile engine/gui.py` → no error
- [ ] La GUI charge l'image PIL et l'affiche si `mission["image"]` existe
- [ ] Un écran "Niveau X terminé !" s'affiche entre les niveaux
- [ ] Le score par niveau est conservé
- [ ] `python3 game.py romy --status` affiche le niveau actuel

## A5 — StateManager
- [ ] `python3 -m py_compile engine/state.py` → no error
- [ ] L'état initial contient `current_level: 1`
- [ ] Après complétion du niveau 1 (mocked), `current_level` passe à 2
- [ ] `level_rewards` liste les récompenses débloquées par niveau

## A6 — Smoke tests
- [ ] `python3 game.py romy --status` → exit 0, affiche "Niveau 1"
- [ ] `python3 game.py oscar --status` → exit 0
- [ ] `python3 parent/status.py` → exit 0, affiche les deux joueurs
- [ ] `python3 tests/test_checks.py` → all pass
- [ ] `python3 tests/test_missions.py` → all mission JSONs valid + levels coherent

## A7 — Curriculum
- [ ] Les missions de maths Romy couvrent : additions/soustractions ≤100, tables ×2 ×3 ×5, formes géométriques
- [ ] Les missions de maths Oscar couvrent : multiplication posée, division, fractions, décimaux, périmètre/aire
- [ ] Les missions de français couvrent : conjugaison présent (Romy), passé composé/futur (Oscar)
- [ ] Les missions d'anglais couvrent : couleurs/chiffres (Romy), phrases complètes (Oscar)
- [ ] Les missions de sciences couvrent ≥ 3 thèmes distincts pour chaque joueur
