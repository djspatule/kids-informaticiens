#!/bin/bash
# =============================================================================
# setup/deploy_to_kidsbook.sh — Déploie le jeu sur kidsbook (192.168.1.41)
# Usage: bash setup/deploy_to_kidsbook.sh
# Requires: daddy's SSH access or root SSH access to kidsbook
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEPLOY_TARGET="/opt/mission-espace"
KIDSBOOK="192.168.1.41"

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

echo -e "${CYAN}${BOLD}"
echo "╔══════════════════════════════════════════════════╗"
echo "║    🚀  MISSION ESPACE — DÉPLOIEMENT KIDSBOOK   ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${RESET}"

info "Source : $PROJECT_ROOT"
info "Cible  : $KIDSBOOK:$DEPLOY_TARGET"

# Vérification connectivity
if ! ping -c 1 -W 3 "$KIDSBOOK" &>/dev/null; then
    error "Impossible de joindre $KIDSBOOK — vérifie que kidsbook est allumé."
    exit 1
fi

# Demander identifiants SSH daddy@kidsbook
info "Connexion SSH : daddy@$KIDSBOOK"
info "(Le mot de passe daddy de kidsbook sera demandé)"
echo ""

# Copier les sources vers /tmp/mission-espace sur kidsbook
info "Copie des sources vers kidsbook..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
    "$PROJECT_ROOT/" \
    "daddy@$KIDSBOOK:/tmp/mission-espace/" \
    && success "Sources copiées vers /tmp/mission-espace"

# Exécuter l'installation en root via sudo
info "Installation sur kidsbook (nécessite le mot de passe sudo de daddy)..."
ssh -tt daddy@$KIDSBOOK "sudo bash -lc 'set -e; mkdir -p $DEPLOY_TARGET; rsync -a /tmp/mission-espace/ $DEPLOY_TARGET/; chmod -R o+rX $DEPLOY_TARGET; mkdir -p $DEPLOY_TARGET/logs; chmod 1777 $DEPLOY_TARGET/logs; bash $DEPLOY_TARGET/setup/install.sh; echo Déploiement terminé !'"

success "Jeu déployé sur kidsbook : $DEPLOY_TARGET"
echo ""
echo -e "${BOLD}Prochaines étapes sur kidsbook :${RESET}"
echo -e "  Le jeu démarrera automatiquement au login de Romy et Oscar."
echo -e "  Pour lancer manuellement depuis le compte daddy :"
echo -e "    ${CYAN}bash /home/romy/game/start.sh${RESET}"
echo -e "    ${CYAN}bash /home/oscar/game/start.sh${RESET}"
echo ""
