#!/bin/bash
# =============================================================================
# setup/install.sh — Installateur principal du jeu Mission Espace
# Usage: sudo bash setup/install.sh   (depuis le répertoire du projet)
# =============================================================================
set -e

# ---------------------------------------------------------------------------
# Couleurs terminal
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERREUR]${RESET} $*" >&2; }
step()    { echo -e "\n${CYAN}${BOLD}▶ $*${RESET}"; }
banner()  { echo -e "${BOLD}${CYAN}$*${RESET}"; }

# ---------------------------------------------------------------------------
# Vérification de l'environnement
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

banner "
╔══════════════════════════════════════════════════╗
║        🚀  MISSION ESPACE — INSTALLATION        ║
╚══════════════════════════════════════════════════╝
"

info "Répertoire du projet : $PROJECT_ROOT"

# Doit être lancé en root (ou avec sudo)
if [[ $EUID -ne 0 ]]; then
    error "Ce script doit être lancé avec sudo."
    error "Exemple : sudo bash setup/install.sh"
    exit 1
fi

# ---------------------------------------------------------------------------
# Étape 1 : Vérification des dépendances
# ---------------------------------------------------------------------------
step "Vérification des dépendances"

MISSING_DEPS=()

check_dep() {
    local cmd="$1"
    local pkg="${2:-$1}"
    if command -v "$cmd" &>/dev/null; then
        success "$cmd trouvé : $(command -v "$cmd")"
    else
        warn "$cmd introuvable (paquet suggéré : $pkg)"
        MISSING_DEPS+=("$pkg")
    fi
}

check_dep python3       python3
check_dep notify-send   libnotify-bin
check_dep xfconf-query  xfconf
check_dep paplay        pulseaudio-utils

# Vérifier python3-tk spécifiquement (indispensable pour l'interface graphique)
if ! python3 -c "import tkinter" &>/dev/null; then
    warn "python3-tk introuvable — REQUIS pour l'interface graphique"
    MISSING_DEPS+=("python3-tk")
fi

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    warn "Dépendances manquantes : ${MISSING_DEPS[*]}"
    warn "Installation automatique..."
    apt-get install -y "${MISSING_DEPS[@]}" || warn "Certaines dépendances n'ont pas pu être installées — le jeu fonctionnera quand même."
fi

# Vérification finale de tkinter (critique)
if ! python3 -c "import tkinter" &>/dev/null; then
    error "python3-tk n'a pas pu être installé. Installez-le manuellement :"
    error "  sudo apt-get install python3-tk"
    error "Le jeu NE FONCTIONNERA PAS sans ce paquet."
fi

# ---------------------------------------------------------------------------
# Étape 2 : Permissions sur les sources du projet
# ---------------------------------------------------------------------------
step "Mise à jour des permissions sur les sources"

# Rendre le répertoire source lisible par tous les utilisateurs
# (Cherche le propriétaire réel du projet pour ne pas hardcoder "lion")
PROJECT_OWNER=$(stat -c '%U' "$PROJECT_ROOT")
PROJECT_OWNER_HOME=$(eval echo "~$PROJECT_OWNER" 2>/dev/null || echo "/home/$PROJECT_OWNER")
chmod o+rx "$PROJECT_OWNER_HOME" 2>/dev/null || warn "Impossible de chmod $PROJECT_OWNER_HOME"
# Remonter jusqu'à Documents si nécessaire
DOCS_DIR="$(dirname "$PROJECT_ROOT")"
if [[ "$DOCS_DIR" != "$PROJECT_OWNER_HOME" && "$DOCS_DIR" != "/" ]]; then
    chmod o+rx "$DOCS_DIR" 2>/dev/null || warn "Impossible de chmod $DOCS_DIR"
fi
chmod o+rx "$PROJECT_ROOT"
chmod -R o+r "$PROJECT_ROOT"
find "$PROJECT_ROOT" -type d -exec chmod o+rx {} \;

success "Permissions sources configurées"

# ---------------------------------------------------------------------------
# Étape 3 : Création des répertoires de jeu
# ---------------------------------------------------------------------------
step "Création des répertoires /home/romy/game/ et /home/oscar/game/"

for USER_HOME in /home/romy /home/oscar; do
    USERNAME=$(basename "$USER_HOME")
    GAME_DIR="$USER_HOME/game"
    mkdir -p "$GAME_DIR/saves" "$GAME_DIR/wallpapers"
    chown -R "$USERNAME:$USERNAME" "$GAME_DIR"
    success "Répertoire jeu créé : $GAME_DIR"
done

# ---------------------------------------------------------------------------
# Étape 4 : Installation du contenu pour chaque joueur
# ---------------------------------------------------------------------------
step "Installation du contenu pour Romy"
bash "$SCRIPT_DIR/install_romy.sh"

step "Installation du contenu pour Oscar"
bash "$SCRIPT_DIR/install_oscar.sh"

# ---------------------------------------------------------------------------
# Étape 5 : Autostart XFCE
# ---------------------------------------------------------------------------
step "Configuration de l'autostart XFCE"

setup_autostart() {
    local username="$1"
    local user_home="/home/$username"
    local autostart_dir="$user_home/.config/autostart"
    local desktop_file="$autostart_dir/mission-espace.desktop"

    mkdir -p "$autostart_dir"
    chown "$username:$username" "$autostart_dir"

    cat > "$desktop_file" <<EOF
[Desktop Entry]
Type=Application
Name=Mission Espace
Comment=Le jeu d'exploration spatiale de $username
Exec=/home/$username/game/start.sh
Icon=rocket
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

    chown "$username:$username" "$desktop_file"
    chmod 644 "$desktop_file"
    success "Autostart configuré pour $username : $desktop_file"
}

setup_autostart romy
setup_autostart oscar

# ---------------------------------------------------------------------------
# Étape 6 : Permissions sur les logs du projet
# ---------------------------------------------------------------------------
step "Initialisation du répertoire de logs"

LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
chmod o+rwx "$LOG_DIR"
# Les enfants doivent pouvoir écrire dans les logs
chmod o+rw "$LOG_DIR"/*.log 2>/dev/null || true
# S'assurer que les futurs fichiers log seront créables
chmod 1777 "$LOG_DIR" 2>/dev/null || chmod 777 "$LOG_DIR"
success "Répertoire logs prêt : $LOG_DIR"

# ---------------------------------------------------------------------------
# Résumé final
# ---------------------------------------------------------------------------
echo ""
banner "╔══════════════════════════════════════════════════╗"
banner "║       ✅  INSTALLATION TERMINÉE AVEC SUCCÈS     ║"
banner "╚══════════════════════════════════════════════════╝"
echo ""
echo -e "${BOLD}Prochaines étapes :${RESET}"
echo -e "  ${GREEN}1.${RESET} Demande à ${BOLD}Romy${RESET} de se connecter — le jeu démarrera automatiquement"
echo -e "  ${GREEN}2.${RESET} Demande à ${BOLD}Oscar${RESET} de se connecter — idem"
echo -e "  ${GREEN}3.${RESET} Pour lancer manuellement :"
echo -e "       ${CYAN}python3 $PROJECT_ROOT/game.py romy${RESET}"
echo -e "       ${CYAN}python3 $PROJECT_ROOT/game.py oscar${RESET}"
echo -e "  ${GREEN}4.${RESET} Tableau de bord parents :"
echo -e "       ${CYAN}python3 $PROJECT_ROOT/parent/status.py${RESET}"
echo -e "  ${GREEN}5.${RESET} Réinitialiser un joueur :"
echo -e "       ${CYAN}bash $PROJECT_ROOT/setup/reset_player.sh romy${RESET}"
echo ""
