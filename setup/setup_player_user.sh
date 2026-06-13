#!/bin/bash
# =============================================================================
# setup/setup_player_user.sh — Installation en mode utilisateur (sans sudo)
#
# Ce script peut être exécuté par le joueur lui-même (romy ou oscar).
# Il crée uniquement les dossiers et fichiers dans son propre compte.
#
# Usage (exemple, lancé en SSH ou dans le terminal du joueur) :
#   bash /home/lion/Documents/kids-informaticiens/setup/setup_player_user.sh
#
# Le nom du joueur est détecté automatiquement depuis $USER.
# =============================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${BLUE}[setup]${RESET} $*"; }
success() { echo -e "${GREEN}[ok]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[warn]${RESET}  $*"; }

PLAYER="${USER:-$(id -un)}"
HOME_DIR="${HOME:-/home/$PLAYER}"
GAME_DIR="$HOME_DIR/game"
SOURCE_DIR="/home/lion/Documents/kids-informaticiens"

echo ""
echo -e "${BOLD}🚀 Mission Espace — Installation pour $PLAYER${RESET}"
echo "────────────────────────────────────────────"

# ── 1. Dossiers de base ──────────────────────────────────────────────────────
info "Création des dossiers de jeu..."
mkdir -p "$GAME_DIR/saves"
mkdir -p "$GAME_DIR/wallpapers"
mkdir -p "$HOME_DIR/.config/autostart"
success "Dossiers ~/game/ créés"

# ── 2. Wallpapers — copie depuis /usr/share/backgrounds ─────────────────────
info "Copie des fonds d'écran..."
WP_COUNT=0
for SEARCH_DIR in /usr/share/backgrounds/linuxmint /usr/share/backgrounds; do
    [[ -d "$SEARCH_DIR" ]] || continue
    while IFS= read -r -d '' img; do
        [[ $WP_COUNT -ge 5 ]] && break 2
        BASENAME=$(basename "$img")
        [[ -f "$GAME_DIR/wallpapers/$BASENAME" ]] && continue
        cp "$img" "$GAME_DIR/wallpapers/$BASENAME" 2>/dev/null && {
            info "  Copié : $BASENAME"
            (( WP_COUNT++ )) || true
        }
    done < <(find "$SEARCH_DIR" -maxdepth 2 \( -name "*.jpg" -o -name "*.png" \) -print0 2>/dev/null)
done

if [[ $WP_COUNT -eq 0 ]]; then
    warn "Aucun fond système trouvé — génération d'un fond de couleur..."
    python3 - "$GAME_DIR/wallpapers/espace.png" <<'PYEOF'
import sys, struct, zlib
def make_png(path, w=1920, h=1080, r=10, g=0, b=40):
    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)
    row = bytes([0] + [r, g, b] * w)
    compressed = zlib.compress(row * h, 6)
    png = b"\x89PNG\r\n\x1a\n" \
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) \
        + chunk(b"IDAT", compressed) \
        + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
PYEOF
    success "Fond d'écran généré : ~/game/wallpapers/espace.png"
else
    success "$WP_COUNT fond(s) d'écran copié(s)"
fi

# ── 3. Lanceur start.sh ──────────────────────────────────────────────────────
info "Création du lanceur..."
cat > "$GAME_DIR/start.sh" <<EOF
#!/bin/bash
# Lanceur Mission Espace pour $PLAYER
export PYTHONPATH="$SOURCE_DIR"
cd "$SOURCE_DIR"
exec python3 game.py $PLAYER "\$@"
EOF
chmod +x "$GAME_DIR/start.sh"
success "Lanceur créé : ~/game/start.sh"

# ── 4. Raccourci sur le Bureau ───────────────────────────────────────────────
info "Création du raccourci sur le Bureau..."
BUREAU=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME_DIR/Bureau")
[[ -d "$BUREAU" ]] || mkdir -p "$BUREAU"

cat > "$BUREAU/Mission Espace.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Mission Espace 🚀
Comment=Ta mission spatiale, $(id -un) !
Exec=$GAME_DIR/start.sh
Icon=starred
Terminal=false
StartupNotify=true
Categories=Game;Education;
EOF
chmod +x "$BUREAU/Mission Espace.desktop"
success "Raccourci créé sur le Bureau"

# ── 5. Autostart XFCE ────────────────────────────────────────────────────────
info "Configuration de l'autostart XFCE..."
cat > "$HOME_DIR/.config/autostart/mission-espace.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Mission Espace
Comment=Le jeu d'exploration spatiale de $PLAYER
Exec=$GAME_DIR/start.sh
Icon=starred
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
success "Autostart configuré"

# ── 6. Vérification Python ───────────────────────────────────────────────────
info "Vérification Python..."
if python3 -c "
import sys
sys.path.insert(0, '$SOURCE_DIR')
from engine.state import StateManager
from engine.missions import MissionLoader
from engine.checker import CheckRunner
import json
config = json.load(open('$SOURCE_DIR/config/$PLAYER.json'))
sm = StateManager('$PLAYER', config)
state = sm.load()
print('  Mission actuelle:', state['current_mission'])
print('  Score:', state['score'])
" 2>&1; then
    success "Python et moteur de jeu : OK"
else
    warn "Problème détecté avec Python — vérifie les logs"
fi

# ── Résumé ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}✅ Installation terminée pour $PLAYER !${RESET}"
echo ""
echo "Pour lancer le jeu :"
echo -e "  ${BLUE}$GAME_DIR/start.sh${RESET}"
echo ""
echo "Pour voir le statut :"
echo -e "  ${BLUE}python3 $SOURCE_DIR/game.py $PLAYER --status${RESET}"
echo ""
