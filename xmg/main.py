# ------------------------------------------------------------------------------
# XMG-KB - RGB Keyboard Controller
# Version: 2.1.1
# Author: Gerald Hasani
# Email: contact@gerald-hasani.com
# GitHub: https://github.com/Gerald-Ha
# ------------------------------------------------------------------------------

import argparse
import textwrap
import sys
import os
import re
import json

from xmg.core.handler import KeyboardController
from xmg.core.colors import (
    COLORS,
    get_mono_color_vector,
    get_h_alt_color_vector,
    get_v_alt_color_vector
)

CONFIG_DIR = "/etc/xmg-kb"
CONFIG_FILE = f"{CONFIG_DIR}/config.json"

BRIGHTNESS_LEVELS = {
    1: 0x08,
    2: 0x16,
    3: 0x24,
    4: 0x32
}

EFFECTS = {
    "breathing":      0x02,
    "wave":           0x03,
    "random":         0x04,
    "reactive":       0x04,
    "rainbow":        0x05,
    "ripple":         0x06,
    "reactiveripple": 0x07,
    "marquee":        0x09,
    "raindrop":       0x0A,
    "aurora":         0x0E,
    "reactiveaurora": 0x0E,
    "fireworks":      0x11,
}

EFFECT_COLOR_CODES = {
    "r": 0x01,
    "o": 0x02,
    "y": 0x03,
    "g": 0x04,
    "t": 0x05,
    "b": 0x06,
    "p": 0x07,
    "k": 0x09,
    "v": 0x0E,
}

EFFECTS_WITH_COLORS = [
    'breathing', 'raindrop', 'aurora', 'random', 'reactive',
    'ripple', 'reactiveripple', 'reactiveaurora', 'fireworks'
]

EFFECTS_NO_COLORS = ['rainbow', 'wave', 'marquee']

COLORS_NO_EFFECT_SUPPORT = [
    'red',
    'white',
    'turquoise',
    'lavender',
    'coral',
    'salmon',
]

COLOR_TO_EFFECT_CODE = {
    'red': 'r',
    'orange': 'o',
    'yellow': 'y',
    'green': 'g',
    'darkgreen': 'g',
    'cyan': 't',
    'turquoise': 't',
    'blue': 'b',
    'purple': 'p',
    'magenta': 'p',
    'violet': 'v',
    'pink': 'k',
    'hotpink': 'k',
    'lavender': 'v',
    'coral': 'o',
    'salmon': 'o',
    'white': '',
    'rainbow': '',
}


def save_config(config):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
    return None


def apply_config(keyboard, config):
    if not config:
        return False
    
    try:
        mode = config.get('mode', 'color')
        brightness = config.get('brightness', 4)
        
        if mode == 'off':
            keyboard.turn_off()
        elif mode == 'effect':
            effect = config.get('effect', 'rainbow')
            speed = config.get('speed', 5)
            keyboard.set_effect(effect, brightness, speed=speed)
        elif mode == 'h_alt':
            colors = config.get('colors', ['red', 'blue'])
            keyboard.set_brightness(brightness)
            keyboard.set_h_colors(colors[0], colors[1])
        elif mode == 'v_alt':
            colors = config.get('colors', ['red', 'blue'])
            keyboard.set_brightness(brightness)
            keyboard.set_v_colors(colors[0], colors[1])
        else:  # mode == 'color'
            color = config.get('color', 'white')
            keyboard.set_brightness(brightness)
            keyboard.set_color(color)
        
        return True
    except Exception as e:
        print(f"Error applying configuration: {e}")
        return False


class Term:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


_effect_pattern = re.compile(
    "^({})({})?$".format(
        '|'.join(EFFECTS.keys()),
        '|'.join(EFFECT_COLOR_CODES.keys())
    )
)


def build_effect_command(effect_name, brightness=3, speed=0x05):
    match = _effect_pattern.match(effect_name)
    
    if not match:
        raise ValueError(f"Unknown effect: {effect_name}")
    
    effect, color_code = match.groups()
    effect_code = EFFECTS[effect]
    color = EFFECT_COLOR_CODES[color_code] if color_code else 0x08
    brightness_code = BRIGHTNESS_LEVELS[brightness]
    extra = 0x00

    if effect == "rainbow":
        color = 0x00
    elif effect == "marquee":
        color = 0x08
    elif effect == "wave":
        color = 0x00
        extra = 0x01
    elif effect in ["reactive", "reactiveaurora", "fireworks"]:
        extra = 0x01

    return (0x08, 0x02, effect_code, speed, brightness_code, color, extra, 0x00)


class XMGKeyboard(KeyboardController):
    def __init__(self, vendor_id=0x048d, product_id=0x600b):
        super().__init__(vendor_id, product_id)
        self._brightness = None

    def turn_off(self):
        self.ctrl_write(0x08, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)

    def set_effect(self, effect_name, brightness=3, speed=5):
        self.ctrl_write(*build_effect_command(effect_name, brightness, speed=speed))

    def set_brightness(self, level=4):
        self._brightness = level
        self.ctrl_write(0x08, 0x02, 0x33, 0x00, BRIGHTNESS_LEVELS[level], 0x00, 0x00, 0x00)

    def _prepare_color_change(self, save=0x01):
        self.ctrl_write(0x12, 0x00, 0x00, 0x08, save, 0x00, 0x00, 0x00)

    def set_color(self, color):
        if not self._brightness:
            self.set_brightness(4)
        self._prepare_color_change()
        self.bulk_write(times=8, payload=get_mono_color_vector(color))

    def set_h_colors(self, color_a, color_b):
        if not self._brightness:
            self.set_brightness(4)
        self._prepare_color_change()
        self.bulk_write(times=8, payload=get_h_alt_color_vector(color_a, color_b))

    def set_v_colors(self, color_a, color_b):
        if not self._brightness:
            self.set_brightness(4)
        self._prepare_color_change()
        self.bulk_write(times=8, payload=get_v_alt_color_vector(color_a, color_b))


def run_auto_test(keyboard):
    import time
    
    known_codes = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0E]
    tested_ranges = list(range(0x00, 0x21)) + [0x29, 0x2E, 0x39, 0x3E, 0x40, 0x80, 0xC0, 0xFF]
    
    test_codes = []
    for code in range(0x21, 0x80):
        if code not in tested_ranges:
            test_codes.append(code)
    
    print(f"\n{Term.CYAN}{Term.BOLD}═══════════════════════════════════════════════════════════════{Term.RESET}")
    print(f"{Term.CYAN}{Term.BOLD}  AUTOMATIC HARDWARE COLOR CODE TEST{Term.RESET}")
    print(f"{Term.CYAN}{Term.BOLD}═══════════════════════════════════════════════════════════════{Term.RESET}")
    print(f"\n{Term.YELLOW}Known working codes:{Term.RESET}")
    print(f"  0x01=Red, 0x02=Orange, 0x03=Yellow, 0x04=Green, 0x05=Cyan")
    print(f"  0x06=Blue, 0x07=Purple, 0x08=Rainbow, 0x09=Pink, 0x0E=Violet")
    print(f"\n{Term.YELLOW}Testing {len(test_codes)} codes from 0x21 to 0x7F{Term.RESET}")
    print(f"{Term.DIM}Press Enter to advance, type 'q' to quit{Term.RESET}")
    print(f"{Term.DIM}Write down the code if you see a color!{Term.RESET}\n")
    
    input(f"{Term.GREEN}Press Enter to start...{Term.RESET}")
    
    keyboard.set_brightness(4)
    
    for code in test_codes:
        print(f"\n{Term.CYAN}{'─' * 50}{Term.RESET}")
        print(f"{Term.BOLD}Testing: 0x{code:02X} (decimal: {code}){Term.RESET}")
        print(f"{Term.CYAN}{'─' * 50}{Term.RESET}")
        
        try:
            effect_code = EFFECTS['breathing']
            effect_param = (effect_code << 24) | (0x00 << 16) | (code << 8) | BRIGHTNESS_LEVELS[4]
            keyboard._controller.set_effect(effect_param)
        except Exception as e:
            print(f"{Term.RED}Error: {e}{Term.RESET}")
        
        user_input = input(f"{Term.YELLOW}Enter = next, 'q' = quit: {Term.RESET}").strip().lower()
        if user_input == 'q':
            break
    
    keyboard.turn_off()
    print(f"\n{Term.GREEN}✓ Test completed!{Term.RESET}")
    print(f"{Term.DIM}If you found new colors, let me know the codes!{Term.RESET}\n")


def show_menu(keyboard):
    print(f"\n{Term.CYAN}{Term.BOLD}╔════════════════════════════════════════════════════════════╗{Term.RESET}")
    print(f"{Term.CYAN}{Term.BOLD}║                                                            ║{Term.RESET}")
    print(f"{Term.CYAN}{Term.BOLD}║            {Term.WHITE}XMG KEYBOARD RGB CONTROL{Term.CYAN}                        ║{Term.RESET}")
    print(f"{Term.CYAN}{Term.BOLD}║                                                            ║{Term.RESET}")
    print(f"{Term.CYAN}{Term.BOLD}╚════════════════════════════════════════════════════════════╝{Term.RESET}")
    
    # Help
    print(f"\n{Term.GREEN}📖 Quick Commands:{Term.RESET}")
    print(f"   {Term.DIM}Type:{Term.RESET} {Term.YELLOW}sudo xmg-kb -c cyan -b 4{Term.RESET} {Term.DIM}for cyan with max brightness{Term.RESET}")
    print(f"   {Term.DIM}Type:{Term.RESET} {Term.YELLOW}sudo xmg-kb -s rainbow -b 4{Term.RESET} {Term.DIM}for rainbow effect{Term.RESET}")
    
    print(f"\n{Term.MAGENTA}{'═' * 64}{Term.RESET}")
    print(f"{Term.MAGENTA}  STEP 1: Choose a color{Term.RESET}")
    print(f"{Term.MAGENTA}{'═' * 64}{Term.RESET}")
    
    color_list = list(COLORS.keys())
    for i, color in enumerate(color_list, 1):
        print(f"   {Term.CYAN}{i:2}.{Term.RESET} {color:<15}", end="")
        if i % 4 == 0:
            print()
    if len(color_list) % 4 != 0:
        print()
    
    off_num = len(color_list) + 1
    print(f"\n   {Term.RED}{off_num:2}. off{Term.RESET} {Term.DIM}(turn off backlight){Term.RESET}")
    print(f"   {Term.YELLOW}    test{Term.RESET} {Term.DIM}(auto-test all remaining hardware codes){Term.RESET}")
    
    try:
        choice = input(f"\n{Term.CYAN}➤ Choose color (number/name, q = quit): {Term.RESET}").strip().lower()
        
        if choice in ('q', 'quit', 'exit'):
            print(f"{Term.DIM}Goodbye! 👋{Term.RESET}\n")
            return None
        
        if choice == 'off' or (choice.isdigit() and int(choice) == off_num):
            keyboard.turn_off()
            print(f"{Term.GREEN}✓ Keyboard backlight turned off{Term.RESET}\n")
            return {'mode': 'off'}
        
        if choice == 'test' or choice == 'auto_test':
            run_auto_test(keyboard)
            return {'mode': 'test'}
        
        selected_color = None
        if choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(color_list):
                selected_color = color_list[num - 1]
        elif choice in COLORS:
            selected_color = choice
        
        if not selected_color:
            print(f"{Term.RED}❌ Invalid selection!{Term.RESET}")
            return None
        
        print(f"{Term.GREEN}   ✓ Color: {selected_color}{Term.RESET}")
        
        if selected_color == 'h-pink-cyan':
            print(f"\n{Term.YELLOW}⚠ Special combo - horizontal pink/cyan{Term.RESET}")
            
            print(f"\n{Term.YELLOW}{'═' * 64}{Term.RESET}")
            print(f"{Term.YELLOW}  Choose brightness{Term.RESET}")
            print(f"{Term.YELLOW}{'═' * 64}{Term.RESET}")
            print(f"   1 = dark  │  2 = low  │  3 = medium  │  4 = bright")
            
            brightness_input = input(f"\n{Term.CYAN}➤ Brightness (1-4, Enter = 4): {Term.RESET}").strip()
            brightness = int(brightness_input) if brightness_input.isdigit() else 4
            brightness = max(1, min(4, brightness))
            print(f"{Term.GREEN}   ✓ Brightness: {brightness}{Term.RESET}")
            
            print(f"\n{Term.DIM}{'─' * 64}{Term.RESET}")
            keyboard.set_brightness(brightness)
            keyboard.set_h_colors('pink', 'cyan')
            config = {'mode': 'h-alt', 'color_a': 'pink', 'color_b': 'cyan', 'brightness': brightness}
            save_config(config)
            print(f"{Term.GREEN}{Term.BOLD}✓ Done!{Term.RESET} Horizontal pink/cyan with brightness {brightness}")
            print(f"{Term.DIM}💾 Settings saved (will be restored on reboot){Term.RESET}\n")
            return config
        
        elif selected_color == 'v-red-blue':
            print(f"\n{Term.YELLOW}⚠ Special combo - vertical red/blue{Term.RESET}")
            
            print(f"\n{Term.YELLOW}{'═' * 64}{Term.RESET}")
            print(f"{Term.YELLOW}  Choose brightness{Term.RESET}")
            print(f"{Term.YELLOW}{'═' * 64}{Term.RESET}")
            print(f"   1 = dark  │  2 = low  │  3 = medium  │  4 = bright")
            
            brightness_input = input(f"\n{Term.CYAN}➤ Brightness (1-4, Enter = 4): {Term.RESET}").strip()
            brightness = int(brightness_input) if brightness_input.isdigit() else 4
            brightness = max(1, min(4, brightness))
            print(f"{Term.GREEN}   ✓ Brightness: {brightness}{Term.RESET}")
            
            print(f"\n{Term.DIM}{'─' * 64}{Term.RESET}")
            keyboard.set_brightness(brightness)
            keyboard.set_v_colors('red', 'blue')
            config = {'mode': 'v-alt', 'color_a': 'red', 'color_b': 'blue', 'brightness': brightness}
            save_config(config)
            print(f"{Term.GREEN}{Term.BOLD}✓ Done!{Term.RESET} Vertical red/blue with brightness {brightness}")
            print(f"{Term.DIM}💾 Settings saved (will be restored on reboot){Term.RESET}\n")
            return config
        
        elif selected_color in COLORS_NO_EFFECT_SUPPORT:
            print(f"\n{Term.YELLOW}⚠ '{selected_color}' shows wrong colors with effects - skipping effect selection{Term.RESET}")
            selected_effect = None
            
            # Only ask for brightness
            print(f"\n{Term.YELLOW}{'═' * 64}{Term.RESET}")
            print(f"{Term.YELLOW}  Choose brightness{Term.RESET}")
            print(f"{Term.YELLOW}{'═' * 64}{Term.RESET}")
            print(f"   1 = dark  │  2 = low  │  3 = medium  │  4 = bright")
            
            brightness_input = input(f"\n{Term.CYAN}➤ Brightness (1-4, Enter = 4): {Term.RESET}").strip()
            brightness = int(brightness_input) if brightness_input.isdigit() else 4
            brightness = max(1, min(4, brightness))
            print(f"{Term.GREEN}   ✓ Brightness: {brightness}{Term.RESET}")
        
        else:
            print(f"\n{Term.BLUE}{'═' * 64}{Term.RESET}")
            print(f"{Term.BLUE}  STEP 2: Choose an effect (optional){Term.RESET}")
            print(f"{Term.BLUE}{'═' * 64}{Term.RESET}")
            
            color_available_for_effects = COLOR_TO_EFFECT_CODE.get(selected_color, '') != ''
            if not color_available_for_effects:
                print(f"   {Term.YELLOW}⚠ Note: '{selected_color}' uses rainbow for effects{Term.RESET}")
            
            effect_list = list(EFFECTS.keys())
            print(f"   {Term.CYAN} 0.{Term.RESET} {Term.WHITE}No effect{Term.RESET} {Term.DIM}(static color){Term.RESET}")
            
            for i, effect in enumerate(effect_list, 1):
                note = f" {Term.DIM}(ignores color choice){Term.RESET}" if effect in EFFECTS_NO_COLORS else ""
                print(f"   {Term.CYAN}{i:2}.{Term.RESET} {effect:<18}{note}")
            
            effect_choice = input(f"\n{Term.CYAN}➤ Choose effect (0-{len(effect_list)}, Enter = 0): {Term.RESET}").strip().lower()
            
            selected_effect = None
            speed = 5  # Default speed
            
            if effect_choice in ('', '0'):
                print(f"{Term.GREEN}   ✓ No effect (static color){Term.RESET}")
            elif effect_choice.isdigit():
                num = int(effect_choice)
                if 1 <= num <= len(effect_list):
                    selected_effect = effect_list[num - 1]
                    print(f"{Term.GREEN}   ✓ Effect: {selected_effect}{Term.RESET}")
            elif effect_choice in EFFECTS:
                selected_effect = effect_choice
                print(f"{Term.GREEN}   ✓ Effect: {selected_effect}{Term.RESET}")
            
            if selected_effect:
                print(f"\n{Term.MAGENTA}{'═' * 64}{Term.RESET}")
                print(f"{Term.MAGENTA}  STEP 3: Choose speed{Term.RESET}")
                print(f"{Term.MAGENTA}{'═' * 64}{Term.RESET}")
                print(f"   1 = fastest  │  5 = normal  │  10 = slowest")
                
                speed_input = input(f"\n{Term.CYAN}➤ Speed (1-10, Enter = 5): {Term.RESET}").strip()
                speed = int(speed_input) if speed_input.isdigit() else 5
                speed = max(1, min(10, speed))
                print(f"{Term.GREEN}   ✓ Speed: {speed}{Term.RESET}")
            
            print(f"\n{Term.YELLOW}{'═' * 64}{Term.RESET}")
            step_num = "4" if selected_effect else "3"
            print(f"{Term.YELLOW}  STEP {step_num}: Choose brightness{Term.RESET}")
            print(f"{Term.YELLOW}{'═' * 64}{Term.RESET}")
            print(f"   1 = dark  │  2 = low  │  3 = medium  │  4 = bright")
            
            brightness_input = input(f"\n{Term.CYAN}➤ Brightness (1-4, Enter = 4): {Term.RESET}").strip()
            brightness = int(brightness_input) if brightness_input.isdigit() else 4
            brightness = max(1, min(4, brightness))
            print(f"{Term.GREEN}   ✓ Brightness: {brightness}{Term.RESET}")
        
        print(f"\n{Term.DIM}{'─' * 64}{Term.RESET}")
        
        config = {'brightness': brightness}
        
        if selected_effect is None:
            keyboard.set_brightness(brightness)
            keyboard.set_color(selected_color)
            config['mode'] = 'color'
            config['color'] = selected_color
            print(f"{Term.GREEN}{Term.BOLD}✓ Done!{Term.RESET} Color '{selected_color}' set with brightness {brightness}\n")
        else:
            if selected_effect in EFFECTS_WITH_COLORS:
                effect_code = COLOR_TO_EFFECT_CODE.get(selected_color, '')
                full_effect = selected_effect + effect_code
                if effect_code:
                    color_info = f" in '{selected_color}'"
                else:
                    color_info = f" ('{selected_color}' not available for effects, using rainbow)"
            else:
                full_effect = selected_effect
                color_info = ""
            
            keyboard.set_effect(full_effect, brightness, speed)
            config['mode'] = 'effect'
            config['effect'] = full_effect
            config['speed'] = speed
            print(f"{Term.GREEN}{Term.BOLD}✓ Done!{Term.RESET} Effect '{selected_effect}'{color_info} with brightness {brightness}, speed {speed}\n")
        
        # Save settings
        if save_config(config):
            print(f"{Term.DIM}💾 Settings saved (will be restored on reboot){Term.RESET}\n")
        
        return config
            
    except KeyboardInterrupt:
        print(f"\n{Term.DIM}Cancelled. 👋{Term.RESET}\n")
        return None
    except Exception as e:
        print(f"{Term.RED}❌ Error: {e}{Term.RESET}")
        return None


def main():
    from elevate import elevate
    
    if '--help' not in sys.argv and '-h' not in sys.argv:
        if os.geteuid() != 0:
            elevate()
    
    parser = argparse.ArgumentParser(
        prog='xmg-kb',
        description=textwrap.dedent(f'''
            XMG Keyboard - RGB Keyboard Control
            
            Run without arguments for the interactive menu!
            
            Available colors:
            [{"|".join(COLORS.keys())}]
            
            Available effects:
            [{"|".join(EFFECTS.keys())}]
        '''),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-c', '--color', help='Single color for all keys')
    parser.add_argument('-b', '--brightness', type=int, choices=range(1, 5),
                        help='Brightness (1-4)')
    parser.add_argument('-H', '--h-alt', nargs=2, help='Horizontally alternating colors')
    parser.add_argument('-V', '--v-alt', nargs=2, help='Vertically alternating colors')
    parser.add_argument('-s', '--style', help='Activate light effect')
    parser.add_argument('-d', '--disable', action='store_true', help='Turn off backlight')
    parser.add_argument('--speed', type=int, choices=range(1, 11),
                        help='Effect speed (1=fast, 10=slow)')
    parser.add_argument('--restore', action='store_true', 
                        help='Restore last saved settings (for autostart)')
    parser.add_argument('--status', action='store_true',
                        help='Show currently saved configuration')
    
    args = parser.parse_args()
    
    if args.status:
        config = load_config()
        if config:
            print(f"Saved configuration: {json.dumps(config, indent=2)}")
        else:
            print("No configuration saved.")
        return
    
    try:
        keyboard = XMGKeyboard()
    except Exception as e:
        print(f"Error: Keyboard not found! ({e})")
        sys.exit(1)
    
    if args.restore:
        config = load_config()
        if config:
            if apply_config(keyboard, config):
                print("Configuration restored.")
            else:
                print("Error restoring configuration.")
        else:
            print("No saved configuration found.")
        return
    
    if len(sys.argv) == 1:
        show_menu(keyboard)
        return
    
    config = {}
    
    if args.disable:
        keyboard.turn_off()
        config = {'mode': 'off'}
    elif args.style:
        speed = args.speed or 5
        brightness = args.brightness or 3
        keyboard.set_effect(args.style, brightness, speed=speed)
        config = {'mode': 'effect', 'effect': args.style, 'brightness': brightness, 'speed': speed}
    else:
        brightness = args.brightness or 4
        if args.brightness:
            keyboard.set_brightness(args.brightness)
        
        if args.color:
            keyboard.set_color(args.color)
            config = {'mode': 'color', 'color': args.color, 'brightness': brightness}
        elif args.h_alt:
            keyboard.set_h_colors(*args.h_alt)
            config = {'mode': 'h_alt', 'colors': args.h_alt, 'brightness': brightness}
        elif args.v_alt:
            keyboard.set_v_colors(*args.v_alt)
            config = {'mode': 'v_alt', 'colors': args.v_alt, 'brightness': brightness}
        else:
            print("Run 'xmg-kb' without arguments for the interactive menu.")
            return
    
    if config:
        save_config(config)


if __name__ == "__main__":
    main()
