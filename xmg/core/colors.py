# ------------------------------------------------------------------------------
# XMG-KB - RGB Keyboard Controller
# Version: 2.1.0
# Author: Gerald Hasani
# Email: contact@gerald-hasani.com
# GitHub: https://github.com/Gerald-Ha
# ------------------------------------------------------------------------------



COLORS = {
    # Primary colors
    'red':        [0x00, 0xFF, 0x00, 0x00],
    'green':      [0x00, 0x00, 0xFF, 0x00],
    'blue':       [0x00, 0x00, 0x00, 0xFF],
    'yellow':     [0x00, 0xFF, 0xFF, 0x00],
    'white':      [0x00, 0xFF, 0xFF, 0xFF],
    
    # Cyan
    'cyan':       [0x00, 0x00, 0xFF, 0xFF],
    'turquoise':  [0x00, 0x00, 0xFF, 0xFF],
    
    # Purple/Pink variants
    'purple':     [0x00, 0x80, 0x00, 0x80],
    'magenta':    [0x00, 0xFF, 0x00, 0xFF],
    'violet':     [0x00, 0x4B, 0x00, 0x82],
    'pink':       [0x00, 0xEE, 0x82, 0xEE],
    'hotpink':    [0x00, 0xFF, 0x69, 0xB4],
    'lavender':   [0x00, 0xE6, 0xE6, 0xFA],
    
    # Orange
    'orange':     [0x00, 0xFF, 0xA5, 0x00],
    'coral':      [0x00, 0xFF, 0x7F, 0x50],
    'salmon':     [0x00, 0xFA, 0x80, 0x72],
    
    # Green variants
    'darkgreen':  [0x00, 0x00, 0x64, 0x00],
    
    # Special
    'rainbow':    [0x00, 0xFF, 0xFF, 0xFF],
    
    # Special combos (for interactive menu display)
    'h-pink-cyan':  [0x00, 0x00, 0x00, 0x00],  # Horizontal: pink + cyan
    'v-red-blue':   [0x00, 0x00, 0x00, 0x00],  # Vertical: red + blue
}


def get_mono_color_vector(color_name):
    """Creates a color vector for single-color lighting"""
    return bytearray(16 * COLORS[color_name])


def get_h_alt_color_vector(color_a, color_b):
    """Creates a color vector for horizontally alternating colors"""
    return bytearray(8 * (COLORS[color_a] + COLORS[color_b]))


def get_v_alt_color_vector(color_a, color_b):
    """Creates a color vector for vertically alternating colors"""
    return bytearray(8 * COLORS[color_a] + 8 * COLORS[color_b])
