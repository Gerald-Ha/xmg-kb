# ⌨️ XMG-KB

**RGB Keyboard Controller for Linux**

A user-friendly tool to control RGB keyboard backlighting on laptops with ITE 8291 controller.

---

## ✨ Features

- 🎨 **18 Colors** - From cyan to violet to coral
- 🌈 **12 Light Effects** - Rainbow, Breathing, Wave, Fireworks and more
- 💡 **4 Brightness Levels** - From subtle to full power
- 🖥️ **Interactive Menu** - Easy to use without memorizing commands
- ⚡ **Quick Commands** - For power users via command line
- 💾 **Save Settings** - Automatically restored on reboot
- 🚀 **Autostart** - systemd service for automatic restoration
- 🐧 **Native Linux Support** - Ubuntu, Fedora, Arch and more

---

## 🖥️ Supported Systems

### Operating Systems

| Distribution | Supported |
|--------------|-----------|
| **Ubuntu / Debian** | ✅ |
| **Fedora / RHEL** | ✅ |
| **Arch Linux / Manjaro** | ✅ |
| **openSUSE** | ✅ |
| **Linux Mint / Pop!_OS** | ✅ |

### Supported Devices

Works with laptops using the **ITE Device(8291) Rev 0.03** keyboard controller:

| Manufacturer | Models |
|--------------|--------|
| **XMG / Schenker** | XMG Fusion E24 (Self-tested) |


### Check Your Controller

```bash
sudo hwinfo --short
```

Expected output:
```
keyboard:
                       Integrated Technology Express ITE Device(8291)
```

---

## 📦 Installation

### Automatic Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/Gerald-Ha/xmg-kb.git
cd xmg-kb

# Run installer
sudo ./install.sh
```

The install script will:
- ✅ Automatically detect your system (Ubuntu/Fedora/Arch)
- ✅ Install all dependencies
- ✅ Set up the systemd service
- ✅ Enable autostart on boot

### Manual Installation

```bash
# Dependencies (Ubuntu/Debian)
sudo apt install python3 python3-pip libusb-1.0-0

# Dependencies (Fedora)
sudo dnf install python3 python3-pip libusb

# Install package
sudo pip3 install . --break-system-packages
```

### Uninstallation

```bash
sudo ./uninstall.sh
```

---

## 🚀 Usage

### Interactive Menu

Simply run without arguments:

```bash
sudo xmg-kb
```

The menu will guide you step by step:

1. **Choose a color** (including rainbow and special combos)
2. **Choose an effect** (optional, with info about color support)
3. **Choose speed** (1-10, only if effect selected)
4. **Choose brightness** (1-4)

```
╔════════════════════════════════════════════════════════════╗
║            XMG KEYBOARD RGB CONTROL                        ║
╚════════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════════
  STEP 1: Choose a color
════════════════════════════════════════════════════════════════
    1. red              2. green          3. blue           4. cyan
    ...
   19. h-pink-cyan      20. v-red-blue    (special combos)

➤ Choose color (number/name, q = quit): 
```

**Settings are automatically saved** and restored on next system boot! 💾

### Quick Commands

**Set color:**
```bash
sudo xmg-kb -c cyan -b 4
```

**Activate effect:**
```bash
sudo xmg-kb -s rainbow -b 4
```

**Effect with speed:**
```bash
sudo xmg-kb -s wave -b 4 --speed 3
```

**Alternating colors:**
```bash
sudo xmg-kb -H pink cyan -b 4    # Horizontal
sudo xmg-kb -V red blue -b 4     # Vertical
```

**Turn off backlight:**
```bash
sudo xmg-kb -d
```

**Show saved settings:**
```bash
sudo xmg-kb --status
```

---

## 🔄 Autostart & Service

After installation, the keyboard backlight automatically starts with your last used settings.

### Manage Service

```bash
# Show status
sudo systemctl status xmg-kb

# Manually restart
sudo systemctl restart xmg-kb

# Disable autostart
sudo systemctl disable xmg-kb

# Enable autostart
sudo systemctl enable xmg-kb
```

### Where Are Settings Stored?

Configuration is saved in `/etc/xmg-kb/config.json`.

---

## 🎨 Available Colors

| Basic Colors | Cyan/Turquoise | Purple/Pink | Orange/Coral |
|--------------|----------------|-------------|--------------|
| red | cyan | purple | orange |
| green | turquoise | magenta | coral |
| blue | | violet | salmon |
| yellow | | pink | |
| white | | hotpink | |
| | | lavender | |

| Green Shades | Special |
|--------------|---------|
| darkgreen | rainbow |
| | h-pink-cyan (horizontal combo) |
| | v-red-blue (vertical combo) |

### ⚠️ Effect Color Limitations

Due to hardware limitations by XMG, some colors do **not** have matching effect codes. When you select these colors with an effect, the closest available effect color is used:

| Color | Effect shows | Reason |
|-------|--------------|--------|
| red | magenta | No red effect code found |
| white | rainbow | No white effect code found |
| turquoise | cyan | No turquoise effect code |
| lavender | violet | Close match |
| coral | orange | Close match |
| salmon | orange | Close match |

**Colors with full effect support:** green, blue, yellow, cyan, purple, magenta, violet, pink, hotpink, orange, darkgreen

---

## ✨ Available Effects

| Effect | Description | Color Choice |
|--------|-------------|--------------|
| `breathing` | Pulsing fade in/out | ✅ |
| `wave` | Wave movement | ❌ |
| `random` | Random keys light up | ✅ |
| `reactive` | Reacts to key press | ✅ |
| `ripple` | Wave effect on key press | ✅ |
| `reactiveripple` | Reactive waves | ✅ |
| `marquee` | Marquee effect | ❌ |
| `raindrop` | Raindrop animation | ✅ |
| `aurora` | Northern lights effect | ✅ |
| `reactiveaurora` | Reactive northern lights | ✅ |
| `fireworks` | Fireworks animation | ✅ |

> **Note:** `rainbow` is now selectable as a color (cycles through all colors automatically).

---

## ⚙️ All Options

| Option | Short | Description |
|--------|-------|-------------|
| `--color` | `-c` | Single color for all keys |
| `--brightness` | `-b` | Brightness (1=dark to 4=bright) |
| `--style` | `-s` | Activate light effect |
| `--h-alt` | `-H` | Two horizontally alternating colors |
| `--v-alt` | `-V` | Two vertically alternating colors |
| `--speed` | | Effect speed (1=fast to 10=slow) |
| `--disable` | `-d` | Turn off backlight completely |
| `--restore` | | Restore saved settings |
| `--status` | | Show current configuration |

---

## 🔧 Troubleshooting

### "Keyboard not found"

1. Check if the keyboard is detected:
   ```bash
   lsusb | grep 048d
   ```

2. Make sure you have root privileges:
   ```bash
   sudo xmg-kb
   ```

### Service doesn't start

```bash
# Check logs
sudo journalctl -u xmg-kb

# Test service manually
sudo xmg-kb --restore
```

### Settings not saving

Check if the configuration directory exists:
```bash
ls -la /etc/xmg-kb/
```

---

## 📁 Project Structure

```
xmg-kb/
├── xmg/
│   ├── __init__.py
│   ├── main.py          # Main program
│   └── core/
│       ├── colors.py    # Color definitions
│       └── handler.py   # USB controller
├── install.sh           # Installer
├── uninstall.sh         # Uninstaller
├── xmg-kb.service       # systemd service
├── setup.py
├── requirements.txt
└── README.md
```

---

## 📄 License

MIT License

---

## 👤 Author

**Gerald Hasani**

- GitHub: [@Gerald-Ha](https://github.com/Gerald-Ha)
- Email: contact@gerald-hasani.com

---

<p align="center">
  Made with ❤️ for the Linux Gaming Community
</p>
