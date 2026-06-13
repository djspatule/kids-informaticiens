# PROGRESS

## Session démarrée : 23:01 CEST 2026-06-13
## Budget estimé : toute la nuit (~8h)

## Status : PHASE 0 — INTAKE ✓ (en cours)

---

## Phase 0 — Intake
- [x] Scan repo + état initial
- [x] BRIEF.md créé
- [x] ACCEPTANCE.md créé  
- [x] DECISIONS.md créé
- [x] Vérification PIL (v12.2.0 disponible ✓)
- [ ] Curriculum EdNat CE1/CM1 (agent en cours...)

## Phase 1 — Plan
- [ ] PLAN.md
- [ ] Architecture multi-niveau définie
- [ ] Interface missions niveau 2-4 spécifiée

## Phase 2 — Test Harness
- [ ] tests/test_checks.py
- [ ] tests/test_missions.py

## Phase 3 — Build
- [ ] Config romy.json + oscar.json mis à jour (levels)
- [ ] engine/state.py mis à jour (current_level, level_rewards)
- [ ] engine/gui.py mis à jour (image display, level completion screen)
- [ ] generate_assets.py (illustrations Pillow)
- [ ] missions Romy L2 (9 missions maths)
- [ ] missions Romy L3 (8 missions FR/EN)
- [ ] missions Romy L4 (6 missions sciences)
- [ ] missions Oscar L2 (9 missions maths)
- [ ] missions Oscar L3 (9 missions FR/EN)
- [ ] missions Oscar L4 (7 missions sciences)

## Phase 4 — Verify
- [ ] python3 generate_assets.py
- [ ] python3 tests/test_missions.py
- [ ] python3 tests/test_checks.py
- [ ] python3 game.py romy --status
- [ ] python3 game.py oscar --status
- [ ] python3 parent/status.py

---

## Tokens/time notes
- 23:01 — Phase 0 en cours, curriculum agent lancé
