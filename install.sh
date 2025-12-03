#!/bin/bash
# ------------------------------------------------------------------------------
# XMG-KB Installer
# Supports: Ubuntu/Debian, Fedora/RHEL, Arch Linux
# ------------------------------------------------------------------------------

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║              ⌨  XMG-KB INSTALLER  ⌨                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Root check
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo ./install.sh${NC}"
    exit 1
fi

# Detect operating system
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/debian_version ]; then
        OS="debian"
    elif [ -f /etc/fedora-release ]; then
        OS="fedora"
    elif [ -f /etc/arch-release ]; then
        OS="arch"
    else
        OS="unknown"
    fi
    echo $OS
}

OS=$(detect_os)
echo -e "${CYAN}📋 Detected system: ${YELLOW}$OS${NC}"
echo ""

# Install dependencies
echo -e "${CYAN}📦 Installing dependencies...${NC}"

case $OS in
    ubuntu|debian|linuxmint|pop)
        apt-get update -qq
        apt-get install -y python3 python3-pip python3-usb libusb-1.0-0
        ;;
    fedora|rhel|centos|rocky|almalinux)
        dnf install -y python3 python3-pip python3-pyusb libusb
        ;;
    arch|manjaro|endeavouros)
        pacman -Sy --noconfirm python python-pip python-pyusb libusb
        ;;
    opensuse*|suse)
        zypper install -y python3 python3-pip python3-usb libusb-1_0
        ;;
    *)
        echo -e "${YELLOW}⚠ Unknown system. Trying generic installation...${NC}"
        ;;
esac

echo -e "${GREEN}✓ System dependencies installed${NC}"

# Install Python packages
echo -e "${CYAN}🐍 Installing Python packages...${NC}"

# Check if --break-system-packages is needed (Python 3.11+)
PIP_ARGS=""
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    PIP_ARGS="--break-system-packages"
fi

pip3 install pyusb elevate $PIP_ARGS

echo -e "${GREEN}✓ Python packages installed${NC}"

# Install XMG-KB
echo -e "${CYAN}⌨ Installing XMG-KB...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

pip3 install . $PIP_ARGS

echo -e "${GREEN}✓ XMG-KB installed${NC}"

# Create udev rule (for USB access + disable autosuspend)
echo -e "${CYAN}🔧 Creating udev rule...${NC}"

cat > /etc/udev/rules.d/99-xmg-keyboard.rules << 'EOF'
# XMG Keyboard RGB Controller
# Allow user access
SUBSYSTEM=="usb", ATTR{idVendor}=="048d", ATTR{idProduct}=="600b", MODE="0666"
# Disable USB autosuspend to prevent RGB settings from being lost
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="048d", ATTR{idProduct}=="600b", ATTR{power/autosuspend}="-1"
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="048d", ATTR{idProduct}=="600b", ATTR{power/autosuspend_delay_ms}="-1"
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="048d", ATTR{idProduct}=="600b", TEST=="power/control", ATTR{power/control}="on"
EOF

udevadm control --reload-rules
udevadm trigger

echo -e "${GREEN}✓ udev rule created (USB autosuspend disabled)${NC}"

# Create configuration directory
echo -e "${CYAN}📁 Creating configuration directory...${NC}"

mkdir -p /etc/xmg-kb
chmod 755 /etc/xmg-kb

echo -e "${GREEN}✓ Configuration directory created${NC}"

# Install systemd service
echo -e "${CYAN}⚙ Installing systemd service...${NC}"

cp "$SCRIPT_DIR/xmg-kb.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable xmg-kb.service

echo -e "${GREEN}✓ systemd service installed and enabled${NC}"

# Install refresh timer (re-applies settings every 2 minutes for notebooks)
echo -e "${CYAN}⏰ Installing refresh timer...${NC}"

cp "$SCRIPT_DIR/xmg-kb-refresh.service" /etc/systemd/system/
cp "$SCRIPT_DIR/xmg-kb-refresh.timer" /etc/systemd/system/

systemctl daemon-reload
systemctl enable xmg-kb-refresh.timer
systemctl start xmg-kb-refresh.timer

echo -e "${GREEN}✓ Refresh timer installed (re-applies RGB every 2 minutes)${NC}"

# Install resume service (restores RGB after suspend/hibernate)
echo -e "${CYAN}💤 Installing suspend/resume service...${NC}"

cp "$SCRIPT_DIR/xmg-kb-resume.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable xmg-kb-resume.service

echo -e "${GREEN}✓ Resume service installed (restores RGB after sleep)${NC}"

# Done
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║              ✓ INSTALLATION COMPLETE!                        ║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Usage:${NC}"
echo -e "  ${YELLOW}sudo xmg-kb${NC}              - Start interactive menu"
echo -e "  ${YELLOW}sudo xmg-kb -c cyan -b 4${NC} - Set color"
echo -e "  ${YELLOW}sudo xmg-kb -s rainbow${NC}   - Activate effect"
echo -e "  ${YELLOW}sudo xmg-kb --status${NC}    - Show saved settings"
echo ""
echo -e "${CYAN}Autostart:${NC}"
echo -e "  Keyboard backlight will automatically start with your"
echo -e "  last used settings on every system boot."
echo ""
echo -e "${CYAN}Manage service:${NC}"
echo -e "  ${YELLOW}sudo systemctl status xmg-kb${NC}            - Show boot service status"
echo -e "  ${YELLOW}sudo systemctl restart xmg-kb${NC}           - Restart boot service"
echo -e "  ${YELLOW}sudo systemctl list-timers xmg-kb*${NC}      - Show refresh timer status"
echo -e "  ${YELLOW}sudo systemctl disable xmg-kb.service${NC}   - Disable boot autostart"
echo -e "  ${YELLOW}sudo systemctl disable xmg-kb-refresh.timer${NC} - Disable 2-min refresh"
echo ""
