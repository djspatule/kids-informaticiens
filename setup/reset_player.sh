#!/bin/bash
# =============================================================================
# setup/reset_player.sh — Réinitialisation d'un joueur
# Usage: sudo bash setup/reset_player.sh romy
#        sudo bash setup/reset_player.sh oscar
# =============================================================================
set -e

# ---------------------------------------------------------------------------
# Couleurs terminal
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}   $*"; }
success() { echo -e "${GREEN}[OK]${RESET}     $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}   $*"; }
error()   { echo -e "${RED}[ERREUR]${RESET} $*" >&2; }

# ---------------------------------------------------------------------------
# Vérifications préliminaires
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ $EUID -ne 0 ]]; then
    error "Ce script doit être lancé avec sudo."
    error "Exemple : sudo bash setup/reset_player.sh romy"
    exit 1
fi

PLAYER="${1:-}"
if [[ -z "$PLAYER" ]]; then
    error "Usage : sudo bash setup/reset_player.sh <joueur>"
    error "Joueurs disponibles : romy, oscar"
    exit 1
fi

if [[ "$PLAYER" != "romy" && "$PLAYER" != "oscar" ]]; then
    error "Joueur invalide : '$PLAYER'. Valeurs acceptées : romy, oscar"
    exit 1
fi

if ! id "$PLAYER" &>/dev/null; then
    error "Le compte '$PLAYER' n'existe pas sur ce système."
    exit 1
fi

USER_HOME="/home/$PLAYER"
SAVE_FILE="$USER_HOME/game/saves/state.json"

# ---------------------------------------------------------------------------
# Affichage et confirmation
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}${YELLOW}⚠️  RÉINITIALISATION DU JOUEUR : ${PLAYER^^}${RESET}"
echo ""
echo "Cette opération va :"
echo "  • Supprimer la progression ($SAVE_FILE)"
echo "  • Supprimer les dossiers de jeu créés par le joueur :"

if [[ "$PLAYER" == "romy" ]]; then
    BUREAU=$(sudo -u romy xdg-user-dir DESKTOP 2>/dev/null || echo "$USER_HOME/Bureau")
    echo "      $BUREAU/Fusée/"
    echo "      $USER_HOME/Étoiles/"
    echo "      $USER_HOME/Mission/"
    echo "      $USER_HOME/Trouvailles/"
    echo "      $USER_HOME/Vaisseau/"
else
    BUREAU=$(sudo -u oscar xdg-user-dir DESKTOP 2>/dev/null || echo "$USER_HOME/Bureau")
    echo "      $BUREAU/Mission_Spatiale/"
    echo "      $USER_HOME/Planètes/"
    echo "      $USER_HOME/Base_Spatiale/"
    echo "      $USER_HOME/Mission_Journal/"
    echo "      $USER_HOME/Transmissions/"
fi

echo "  • Recréer tout le contenu de départ"
echo ""
echo -e "${RED}${BOLD}Cette action est irréversible !${RESET}"
echo ""
read -r -p "Continuer ? [oui/NON] : " CONFIRM

if [[ "$CONFIRM" != "oui" && "$CONFIRM" != "OUI" ]]; then
    info "Annulation. Aucun changement effectué."
    exit 0
fi

echo ""
info "Début de la réinitialisation pour $PLAYER..."

# ---------------------------------------------------------------------------
# Suppression de la sauvegarde
# ---------------------------------------------------------------------------
if [[ -f "$SAVE_FILE" ]]; then
    rm -f "$SAVE_FILE"
    success "Sauvegarde supprimée : $SAVE_FILE"
else
    info "Aucune sauvegarde à supprimer."
fi

# Aussi supprimer le log
LOG_FILE="$PROJECT_ROOT/logs/$PLAYER.log"
if [[ -f "$LOG_FILE" ]]; then
    rm -f "$LOG_FILE"
    success "Log supprimé : $LOG_FILE"
fi

# ---------------------------------------------------------------------------
# Suppression des dossiers de contenu
# ---------------------------------------------------------------------------
info "Suppression des dossiers de jeu..."

if [[ "$PLAYER" == "romy" ]]; then
    rm -rf "$BUREAU/Fusée" 2>/dev/null || warn "Impossible de supprimer $BUREAU/Fusée"
    rm -rf "$USER_HOME/Étoiles" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Étoiles"
    rm -rf "$USER_HOME/Mission" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Mission"
    rm -rf "$USER_HOME/Trouvailles" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Trouvailles"
    rm -rf "$USER_HOME/Vaisseau" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Vaisseau"
else
    rm -rf "$BUREAU/Mission_Spatiale" 2>/dev/null || warn "Impossible de supprimer $BUREAU/Mission_Spatiale"
    rm -rf "$USER_HOME/Planètes" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Planètes"
    rm -rf "$USER_HOME/Base_Spatiale" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Base_Spatiale"
    rm -rf "$USER_HOME/Mission_Journal" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Mission_Journal"
    rm -rf "$USER_HOME/Transmissions" 2>/dev/null || warn "Impossible de supprimer $USER_HOME/Transmissions"
fi

success "Dossiers supprimés"

# ---------------------------------------------------------------------------
# Réinstallation du contenu
# ---------------------------------------------------------------------------
info "Réinstallation du contenu initial..."

bash "$SCRIPT_DIR/install_${PLAYER}.sh"

echo ""
success "${PLAYER^} a été réinitialisé avec succès ! 🚀"
echo -e "  Le jeu reprend depuis la ${BOLD}mission 1${RESET}."
echo ""
