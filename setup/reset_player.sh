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

# Détecter le desktop
BUREAU=$(sudo -u "$PLAYER" xdg-user-dir DESKTOP 2>/dev/null || echo "$USER_HOME/Desktop")
[[ -z "$BUREAU" || "$BUREAU" == "$USER_HOME" ]] && BUREAU="$USER_HOME/Desktop"

# ---------------------------------------------------------------------------
# Affichage et confirmation
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}${YELLOW}⚠️  RÉINITIALISATION DU JOUEUR : ${PLAYER^^}${RESET}"
echo ""
echo "Cette opération va :"
echo "  • Supprimer la progression ($SAVE_FILE)"
echo "  • Supprimer les dossiers/fichiers créés pendant le jeu"

if [[ "$PLAYER" == "romy" ]]; then
    echo "      $BUREAU/Mission-Spatiale/"
    echo "      $BUREAU/rapport-mission.txt"
    echo "      $BUREAU/rapport-final.txt"
else
    echo "      $BUREAU/Base-Spatiale/"
fi

echo "  • Recréer le raccourci et les fichiers de départ"
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

# Supprimer le log
LOG_FILE="$PROJECT_ROOT/logs/$PLAYER.log"
if [[ -f "$LOG_FILE" ]]; then
    rm -f "$LOG_FILE"
    success "Log supprimé : $LOG_FILE"
fi

# ---------------------------------------------------------------------------
# Suppression des dossiers créés pendant le jeu
# ---------------------------------------------------------------------------
info "Suppression des dossiers de jeu..."

if [[ "$PLAYER" == "romy" ]]; then
    rm -rf "$BUREAU/Mission-Spatiale" 2>/dev/null || warn "Impossible de supprimer Mission-Spatiale"
    rm -f  "$BUREAU/rapport-mission.txt" 2>/dev/null || true
    rm -f  "$BUREAU/rapport-final.txt"   2>/dev/null || true
else
    rm -rf "$BUREAU/Base-Spatiale" 2>/dev/null || warn "Impossible de supprimer Base-Spatiale"
fi

success "Contenu de jeu supprimé"

# ---------------------------------------------------------------------------
# Réinstallation du contenu initial
# ---------------------------------------------------------------------------
info "Réinstallation du contenu initial (raccourci, start.sh)..."
bash "$SCRIPT_DIR/install_${PLAYER}.sh"

echo ""
success "${PLAYER^} a été réinitialisé avec succès ! 🚀"
echo -e "  Le jeu reprend depuis la ${BOLD}mission 1${RESET}."
echo ""
