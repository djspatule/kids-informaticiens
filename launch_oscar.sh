#!/bin/bash
# Lanceur rapide pour Oscar (depuis le compte daddy/lion sur kidsbook)
# Usage: bash launch_oscar.sh
# Ou depuis le compte daddy avec DISPLAY déjà défini: bash launch_oscar.sh

# Détecter le DISPLAY si pas défini
if [[ -z "$DISPLAY" ]]; then
    export DISPLAY=:0
fi

echo "Lancement du jeu Mission Espace pour Oscar..."
exec sudo -u oscar bash /home/oscar/game/start.sh
