#!/bin/bash
# ------------------------------------------------------------------------------
# XMG-KB Uninstaller
# ------------------------------------------------------------------------------

set -e


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              ⌨  XMG-KB UNINSTALLER  ⌨                       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Root check
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo ./uninstall.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠ This will completely uninstall XMG-KB.${NC}"
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}Cancelled.${NC}"
    exit 0
fi

echo ""

# Stop and remove systemd service
echo -e "${CYAN}⚙ Removing systemd service...${NC}"
systemctl stop xmg-kb.service 2>/dev/null || true
systemctl disable xmg-kb.service 2>/dev/null || true
rm -f /etc/systemd/system/xmg-kb.service
systemctl daemon-reload
echo -e "${GREEN}✓ Service removed${NC}"

# Remove udev rule
echo -e "${CYAN}🔧 Removing udev rule...${NC}"
rm -f /etc/udev/rules.d/99-xmg-keyboard.rules
udevadm control --reload-rules 2>/dev/null || true
echo -e "${GREEN}✓ udev rule removed${NC}"

# Uninstall Python package
echo -e "${CYAN}🐍 Uninstalling Python package...${NC}"

PIP_ARGS=""
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    PIP_ARGS="--break-system-packages"
fi

pip3 uninstall -y xmg-kb $PIP_ARGS 2>/dev/null || true
echo -e "${GREEN}✓ Python package uninstalled${NC}"

# Remove configuration (optional)
echo ""
read -p "Also delete saved settings? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf /etc/xmg-kb
    echo -e "${GREEN}✓ Configuration deleted${NC}"
else
    echo -e "${CYAN}Configuration kept in /etc/xmg-kb${NC}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║              ✓ UNINSTALLATION COMPLETE!                      ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
