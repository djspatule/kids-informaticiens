#!/bin/bash
# =============================================================================
# setup/install_oscar.sh — Installateur du contenu de jeu pour Oscar
# Appelé par install.sh (doit être lancé en root / avec sudo)
# =============================================================================
set -e

# ---------------------------------------------------------------------------
# Couleurs terminal
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${BLUE}  [oscar]${RESET} $*"; }
success() { echo -e "${GREEN}  [oscar]${RESET} $*"; }

# Doit être lancé en root
if [[ $EUID -ne 0 ]]; then
    echo "install_oscar.sh doit être lancé en root (via install.sh avec sudo)." >&2
    exit 1
fi

HOME_OSCAR="/home/oscar"
GAME_DIR="$HOME_OSCAR/game"

# Vérifier que le compte oscar existe
if ! id oscar &>/dev/null; then
    echo "ERREUR : le compte 'oscar' n'existe pas." >&2
    exit 1
fi

# Desktop folder — always English name (XFCE on this machine uses LANG=en_US)
BUREAU="$HOME_OSCAR/Desktop"
mkdir -p "$BUREAU"
info "Bureau détecté : $BUREAU"

# ---------------------------------------------------------------------------
# Création de l'arborescence
# ---------------------------------------------------------------------------
info "Création des dossiers..."

mkdir -p "$GAME_DIR/saves"
mkdir -p "$GAME_DIR/wallpapers"
mkdir -p "$HOME_OSCAR/.config/autostart"

success "Dossiers créés"

# ---------------------------------------------------------------------------
# Fichiers de contenu du jeu (message de bienvenue seulement)
# ---------------------------------------------------------------------------
info "Création du message de bienvenue..."

# --- game/message_bienvenue.txt ---
cat > "$GAME_DIR/message_bienvenue.txt" <<'EOF'
📡 BIENVENUE, COMMANDANT OSCAR! 📡
====================================

Tu es maintenant Commandant du Centre de Contrôle Spatial !

Pour commencer ta mission, lance le jeu depuis le raccourci sur ton Bureau,
ou demande à Papa de le lancer pour toi.

Bonne chance, Commandant ! 🚀
EOF

success "Créé : game/message_bienvenue.txt"

# --- game/start.sh ---
# Injecter le vrai chemin du projet au moment de l'installation
INSTALL_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cat > "$GAME_DIR/start.sh" <<STARTEOF
#!/bin/bash
# Lance le jeu Mission Espace pour Oscar
# Installé depuis : $INSTALL_PROJECT_ROOT
cd "$INSTALL_PROJECT_ROOT"
exec python3 game.py oscar
STARTEOF

chmod +x "$GAME_DIR/start.sh"
success "Créé : game/start.sh (exécutable)"

# --- Raccourci Bureau / Desktop ---
DESKTOP_SHORTCUT="$BUREAU/Mission Espace.desktop"
cat > "$DESKTOP_SHORTCUT" <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Mission Espace 🚀
Comment=Ta mission spatiale, Commandant Oscar!
Exec=/home/oscar/game/start.sh
Icon=starred
Terminal=false
StartupNotify=true
Categories=Game;Education;
EOF

chmod +x "$DESKTOP_SHORTCUT"
success "Créé : raccourci Bureau '$DESKTOP_SHORTCUT'"

# --- .config/autostart/mission-espace.desktop ---
cat > "$HOME_OSCAR/.config/autostart/mission-espace.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Mission Espace
Comment=Le jeu d'exploration spatiale d'Oscar
Exec=/home/oscar/game/start.sh
Icon=starred
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

success "Créé : .config/autostart/mission-espace.desktop"

# ---------------------------------------------------------------------------
# Wallpapers — copie depuis /usr/share/backgrounds
# ---------------------------------------------------------------------------
info "Recherche de fonds d'écran..."

WALLPAPER_DST="$GAME_DIR/wallpapers"
WALLPAPER_COUNT=0

for SEARCH_DIR in \
    /usr/share/backgrounds/linuxmint \
    /usr/share/backgrounds \
    /usr/share/pixmaps; do

    if [[ -d "$SEARCH_DIR" ]]; then
        while IFS= read -r -d '' img; do
            if [[ $WALLPAPER_COUNT -ge 6 ]]; then break 2; fi
            BASENAME=$(basename "$img")
            if [[ ! -f "$WALLPAPER_DST/$BASENAME" ]]; then
                cp "$img" "$WALLPAPER_DST/$BASENAME" 2>/dev/null && {
                    info "  Fond d'écran copié : $BASENAME"
                    WALLPAPER_COUNT=$((WALLPAPER_COUNT + 1))
                }
            fi
        done < <(find "$SEARCH_DIR" -maxdepth 2 \( -name "*.jpg" -o -name "*.png" \) -print0 2>/dev/null)
    fi
done

# Si aucun fond d'écran trouvé, générer un placeholder avec Python
if [[ $WALLPAPER_COUNT -eq 0 ]]; then
    info "Aucun fond d'écran système trouvé — génération d'un placeholder..."
    /usr/bin/python3 - "$WALLPAPER_DST/espace_bleu.png" <<'PYEOF'
import sys, struct, zlib

def make_png(path, width=1920, height=1080, r=0, g=20, b=60):
    """PNG minimaliste: fond uni, sans dépendances externes."""
    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    row = bytes([0] + [r, g, b] * width)
    compressed = zlib.compress(row * height, 9)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)
    print(f"PNG généré : {path}")

make_png(sys.argv[1])
PYEOF
    success "Fond d'écran placeholder généré"
fi

# ---------------------------------------------------------------------------
# Propriété et permissions
# ---------------------------------------------------------------------------
info "Mise à jour de la propriété (chown oscar:oscar)..."

chown -R oscar:oscar "$GAME_DIR"
chown oscar:oscar "$HOME_OSCAR/.config/autostart/mission-espace.desktop"
[[ -f "$DESKTOP_SHORTCUT" ]] && chown oscar:oscar "$DESKTOP_SHORTCUT"

success "Propriété mise à jour pour tous les fichiers d'Oscar"
echo -e "${GREEN}  [oscar]${RESET} ${BOLD}Installation d'Oscar terminée ✓${RESET}"
