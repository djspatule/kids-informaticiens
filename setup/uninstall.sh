#!/bin/bash
# =============================================================================
# setup/uninstall.sh — Désinstallateur complet du jeu Mission Espace
# Usage: sudo bash setup/uninstall.sh
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
if [[ $EUID -ne 0 ]]; then
    error "Ce script doit être lancé avec sudo."
    error "Exemple : sudo bash setup/uninstall.sh"
    exit 1
fi

echo ""
echo -e "${BOLD}${RED}⚠️  DÉSINSTALLATION COMPLÈTE — MISSION ESPACE${RESET}"
echo ""
echo "Cette opération va supprimer DÉFINITIVEMENT :"
echo ""
echo "  Pour Romy (/home/romy/) :"
echo "    • Bureau/Fusée/"
echo "    • Étoiles/"
echo "    • Mission/"
echo "    • Trouvailles/"
echo "    • Vaisseau/"
echo "    • game/ (sauvegardes et wallpapers inclus)"
echo "    • .config/autostart/mission-espace.desktop"
echo ""
echo "  Pour Oscar (/home/oscar/) :"
echo "    • Bureau/Mission_Spatiale/"
echo "    • Planètes/"
echo "    • Base_Spatiale/"
echo "    • Mission_Journal/"
echo "    • Transmissions/"
echo "    • game/ (sauvegardes et wallpapers inclus)"
echo "    • .config/autostart/mission-espace.desktop"
echo ""
echo "  Logs du projet : logs/romy.log, logs/oscar.log"
echo ""
echo -e "${RED}${BOLD}Cette action est irréversible !${RESET}"
echo ""
read -r -p "Taper 'DÉSINSTALLER' pour confirmer (ou Entrée pour annuler) : " CONFIRM

if [[ "$CONFIRM" != "DÉSINSTALLER" ]]; then
    info "Annulation. Aucun changement effectué."
    exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo ""
info "Début de la désinstallation..."

# ---------------------------------------------------------------------------
# Romy
# ---------------------------------------------------------------------------
info "Nettoyage pour Romy..."

if id romy &>/dev/null; then
    BUREAU_ROMY=$(sudo -u romy xdg-user-dir DESKTOP 2>/dev/null || echo "/home/romy/Bureau")

    rm -rf "$BUREAU_ROMY/Fusée" 2>/dev/null && success "Supprimé : Bureau/Fusée" || warn "Bureau/Fusée introuvable"
    rm -rf "/home/romy/Étoiles" 2>/dev/null && success "Supprimé : Étoiles" || warn "Étoiles introuvable"
    rm -rf "/home/romy/Mission" 2>/dev/null && success "Supprimé : Mission" || warn "Mission introuvable"
    rm -rf "/home/romy/Trouvailles" 2>/dev/null && success "Supprimé : Trouvailles" || warn "Trouvailles introuvable"
    rm -rf "/home/romy/Vaisseau" 2>/dev/null && success "Supprimé : Vaisseau" || warn "Vaisseau introuvable"
    rm -rf "/home/romy/game" 2>/dev/null && success "Supprimé : game/" || warn "game/ introuvable"
    rm -f "/home/romy/.config/autostart/mission-espace.desktop" 2>/dev/null \
        && success "Supprimé : autostart/mission-espace.desktop" \
        || warn "Entrée autostart introuvable"
else
    warn "Compte romy introuvable — ignoré"
fi

# ---------------------------------------------------------------------------
# Oscar
# ---------------------------------------------------------------------------
info "Nettoyage pour Oscar..."

if id oscar &>/dev/null; then
    BUREAU_OSCAR=$(sudo -u oscar xdg-user-dir DESKTOP 2>/dev/null || echo "/home/oscar/Bureau")

    rm -rf "$BUREAU_OSCAR/Mission_Spatiale" 2>/dev/null && success "Supprimé : Bureau/Mission_Spatiale" || warn "Bureau/Mission_Spatiale introuvable"
    rm -rf "/home/oscar/Planètes" 2>/dev/null && success "Supprimé : Planètes" || warn "Planètes introuvable"
    rm -rf "/home/oscar/Base_Spatiale" 2>/dev/null && success "Supprimé : Base_Spatiale" || warn "Base_Spatiale introuvable"
    rm -rf "/home/oscar/Mission_Journal" 2>/dev/null && success "Supprimé : Mission_Journal" || warn "Mission_Journal introuvable"
    rm -rf "/home/oscar/Transmissions" 2>/dev/null && success "Supprimé : Transmissions" || warn "Transmissions introuvable"
    rm -rf "/home/oscar/game" 2>/dev/null && success "Supprimé : game/" || warn "game/ introuvable"
    rm -f "/home/oscar/.config/autostart/mission-espace.desktop" 2>/dev/null \
        && success "Supprimé : autostart/mission-espace.desktop" \
        || warn "Entrée autostart introuvable"
else
    warn "Compte oscar introuvable — ignoré"
fi

# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------
info "Nettoyage des logs..."
rm -f "$PROJECT_ROOT/logs/romy.log" 2>/dev/null && success "Log Romy supprimé" || true
rm -f "$PROJECT_ROOT/logs/oscar.log" 2>/dev/null && success "Log Oscar supprimé" || true

# ---------------------------------------------------------------------------
# Résumé
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}${BOLD}✅ Désinstallation terminée.${RESET}"
echo ""
echo "Les sources du jeu dans $PROJECT_ROOT sont conservées."
echo "Pour réinstaller : sudo bash $PROJECT_ROOT/setup/install.sh"
echo ""
