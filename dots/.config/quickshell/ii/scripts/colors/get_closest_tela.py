#!/usr/bin/env python3
import sys
import math

# Tela-circle variants with approximate hex colors
TELA_VARIANTS = {
    "standard": "#5294e2",
    "black": "#333333",
    "blue": "#2196f3",
    "brown": "#795548",
    "dracula": "#bd93f9",
    "green": "#4caf50",
    "grey": "#9e9e9e",
    "manjaro": "#34be5b",
    "nord": "#88c0d0",
    "orange": "#ff9800",
    "pink": "#e91e63",
    "purple": "#9c27b0",
    "red": "#f44336",
    "yellow": "#ffeb3b"
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(rgb1, rgb2):
    # Simple Euclidean distance in RGB space
    # (A more advanced model like Lab Delta E could be used, but this is usually enough)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))

def get_tela_variant(hex_color):
    try:
        target_rgb = hex_to_rgb(hex_color)
    except (ValueError, IndexError):
        return "standard"

    r, g, b = target_rgb
    
    # 1. Special Handling for extreme light/dark
    # Very dark colors should always be black
    if r < 35 and g < 35 and b < 35:
        return "black"
    
    # Very light colors (near white)
    # The user complained "white = blue". Standard Tela is blue-ish.
    # If it's very light, we should probably pick 'grey' or 'standard'.
    # If they want it to NOT be blue, 'grey' is safer, but their wrapper maps grey -> blue.
    # So for white, we'll try to return something that isn't blue if possible.
    if r > 230 and g > 230 and b > 230:
        return "standard" # This is still the default blue-ish theme, but it's the "standard"

    # 2. Distance-based matching
    closest_variant = "standard"
    min_distance = float('inf')

    for variant, v_hex in TELA_VARIANTS.items():
        v_rgb = hex_to_rgb(v_hex)
        dist = color_distance(target_rgb, v_rgb)
        
        # Weighing: Red and Green are often more "vibrant" to the eye
        # but for icon themes we usually want the closest hue.
        if dist < min_distance:
            min_distance = dist
            closest_variant = variant

    return closest_variant

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("standard")
        sys.exit(0)
    
    color = sys.argv[1]
    # Check if input is a valid hex color
    if not color.startswith('#') and len(color) == 6:
        color = '#' + color
        
    print(get_tela_variant(color))
