#!/usr/bin/env python3
import sys
import math
import colorsys

# Tela-circle variants with their representative HSV values
# Using HSV makes it much easier to match by Hue while handling muted/dark colors.
TELA_VARIANTS = {
    # variant: (hex, hue, sat, val) - Hue is 0-360, Sat/Val are 0-100
    "black":    ("#333333", 0,   0,  20),
    "blue":     ("#2196f3", 207, 86, 95),
    "brown":    ("#795548", 16,  41, 47),
    "dracula":  ("#bd93f9", 265, 41, 98),
    "green":    ("#4caf50", 122, 57, 69),
    "grey":     ("#9e9e9e", 0,   0,  62),
    "manjaro":  ("#34be5b", 137, 73, 75),
    "nord":     ("#88c0d0", 193, 35, 82),
    "orange":   ("#ff9800", 36,  100,100),
    "pink":     ("#e91e63", 340, 87, 91),
    "purple":   ("#9c27b0", 291, 78, 69),
    "red":      ("#f44336", 4,   78, 96),
    "ubuntu":   ("#e95420", 16,  86, 91),
    "yellow":   ("#ffeb3b", 54,  77, 100)
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def get_hue_distance(h1, h2):
    diff = abs(h1 - h2)
    return min(diff, 360 - diff)

def get_tela_variant(hex_color):
    try:
        rgb = hex_to_rgb(hex_color)
    except (ValueError, IndexError):
        return "nord"

    h_raw, s_raw, v_raw = colorsys.rgb_to_hsv(*rgb)
    h, s, v = h_raw * 360, s_raw * 100, v_raw * 100

    # 1. Special Handling for extreme colors
    if v < 15: # Very dark
        return "black"
    
    if s < 12: # Very muted (Grey/Nord territory)
        if v > 75: return "nord"
        return "grey"

    # User requested: standard (blue-ish) colors should be nord
    # Blue hue is around 190-250
    if 190 <= h <= 250:
        return "nord"

    # 2. Match by Hue and other properties
    closest_variant = "nord"
    min_score = float('inf')

    for variant, (v_hex, v_h, v_s, v_v) in TELA_VARIANTS.items():
        # Skip black/grey for hue matching if target is somewhat vibrant
        if variant in ["black", "grey"] and s > 20:
            continue
            
        h_dist = get_hue_distance(h, v_h)
        s_dist = abs(s - v_s)
        v_dist = abs(v - v_v)
        
        # Scoring: Hue is most important for color identity, 
        # but Saturation and Value help distinguish between variants like blue/nord/standard
        # Weighting: Hue=2.0, Sat=0.5, Val=0.3
        score = (h_dist * 2.0) + (s_dist * 0.5) + (v_dist * 0.3)
        
        if score < min_score:
            min_score = score
            closest_variant = variant

    return closest_variant

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("nord")
        sys.exit(0)
    
    color = sys.argv[1]
    if not color.startswith('#') and len(color) == 6:
        color = '#' + color
        
    print(get_tela_variant(color))
