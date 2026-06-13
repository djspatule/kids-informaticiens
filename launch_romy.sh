#!/bin/bash
# Lanceur rapide pour Romy (depuis le compte daddy/lion sur kidsbook)
# Usage: bash launch_romy.sh
# Ou depuis le compte daddy avec DISPLAY déjà défini: bash launch_romy.sh

# Détecter le DISPLAY si pas défini
if [[ -z "$DISPLAY" ]]; then
    export DISPLAY=:0
fi

echo "Lancement du jeu Mission Espace pour Romy..."
exec sudo -u romy bash /home/romy/game/start.sh
