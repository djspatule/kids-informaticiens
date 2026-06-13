# PLAN — Mission Espace Levels 2-4

## Task Graph

```
[A] Add level:1 to existing missions + write ALL new missions L2-L4
[B] generate_assets.py — Pillow illustrations for every new mission
[C] Update engine/state.py + engine/gui.py for multi-level + image display
[D] Update config/romy.json + config/oscar.json + fix tests

A, B, C, D are INDEPENDENT — run in parallel
```

## Interface contracts

### Mission JSON schema (all fields)
```json
{
  "id": "mission_NN",
  "level": 1,
  "title": "emoji + Title",
  "description": "Short (2-4 lines). Minimal text, big visuals.",
  "hint": "Very specific help.",
  "check": { "type": "...", ... },
  "success_message": "Celebratory French. 🚀",
  "next": "mission_NN+1",
  "points": 10,
  "image": "assets/illustrations/romy/romy_l2_m09.png"
}
```

### New state fields (additions to existing state.json)
```json
{
  "current_level": 1,
  "completed_levels": [],
  "level_rewards": {}
}
```

### Level config structure (addition to romy.json / oscar.json)
```json
"levels": [
  {"id": 1, "name": "L'Exploration Informatique", "missions_count": 8,  "reward": "ETOILE-ROMY-2026",  "color": "#CE93D8"},
  {"id": 2, "name": "La Station Mathématique",    "missions_count": 8,  "reward": "PLANETE-ROMY-2026", "color": "#FFD700"},
  {"id": 3, "name": "Le Vaisseau du Langage",     "missions_count": 8,  "reward": "GALAXIE-ROMY-2026", "color": "#80CBC4"},
  {"id": 4, "name": "La Planète des Sciences",    "missions_count": 6,  "reward": "UNIVERS-ROMY-2026", "color": "#FF8C42"}
]
```

## Task A — Missions content

### Existing missions: add "level": 1
All 17 existing files in missions/romy/ and missions/oscar/ need "level": 1 added.

### Mission numbering
- Romy: existing mission_01–08 → L1. New: mission_09–16 (L2), mission_17–24 (L3), mission_25–30 (L4)
- Oscar: existing mission_01–09 → L1. New: mission_10–18 (L2), mission_19–27 (L3), mission_28–34 (L4)

### Working folders per level (all on Desktop = {desktop})
ROMY:
- L1 (done): {desktop}/Mission-Spatiale/
- L2 (math): first mission creates {desktop}/Station-Maths/, work there
- L3 (lang): first mission creates {desktop}/Vaisseau-Langage/, work there
- L4 (sci):  first mission creates {desktop}/Planete-Sciences/, work there

OSCAR:
- L1 (done): {desktop}/Base-Spatiale/
- L2 (math): {desktop}/Module-Mathematiques/
- L3 (lang): {desktop}/Centre-Communication/
- L4 (sci):  {desktop}/Laboratoire-Spatial/

## Task B — Illustrations

File naming: assets/illustrations/romy/romy_l2_m09.png (level 2, mission 09)
Image size: 460×280 px
Design language: dark space background, bright colors, minimal text, large visuals

## Task C — Engine changes

### state.py additions
- _create_fresh adds: current_level=1, completed_levels=[], level_rewards={}
- migrate_state(state): if keys missing, add defaults (backward-compat)

### gui.py additions
1. Image panel: above mission title, load from PIL ImageTk, resize to 460×200
2. Level complete screen: new Toplevel, shows level name + reward code
3. On mission complete: if next mission has different level → trigger level complete screen
4. Progress: show "Level X — Mission Y/Z" 

## Task D — Config + tests

### romy.json changes
- total_missions: 30
- Add levels array (4 items)
- secret_code: becomes the FINAL reward "UNIVERS-ROMY-2026"

### oscar.json changes
- total_missions: 34
- Add levels array
- secret_code: "QUASAR-OSCAR-2026"

### tests/test_checks.py fix
- StateManager test: use cfg["game_dir"] = str(tmpdir) instead of cfg["save_file"]
