#!/usr/bin/env python3
import sys
import colorsys

def get_tela_variant(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    
    hue_deg = h * 360
    
    # 1. Grayscale / Muted detection
    if s < 0.12:
        if l < 0.25: return "black"
        return "grey"

    # 2. Specific "Vibe" themes based on saturation/lightness
    # Nord: Cold, muted blue
    if 190 < hue_deg < 225 and s < 0.4:
        return "nord"
    # Dracula: Dark, saturated purple
    if 240 < hue_deg < 285 and l < 0.5:
        return "dracula"
    # Brown: Dark orange/yellow
    if 15 < hue_deg < 45 and l < 0.4:
        return "brown"

    # 3. Main Hue Mapping (More balanced)
    # Red: 345 - 15
    if hue_deg >= 345 or hue_deg < 15:
        return "red"
    # Orange: 15 - 45
    if 15 <= hue_deg < 45:
        return "orange"
    # Yellow: 45 - 65
    if 45 <= hue_deg < 65:
        return "yellow"
    # Green: 65 - 140
    if 65 <= hue_deg < 140:
        # Manjaro: Teal/Sea-green
        if hue_deg > 125: return "manjaro"
        return "green"
    # Manjaro/Teal extension: 140 - 170
    if 140 <= hue_deg < 170:
        return "manjaro"
    # Blue: 170 - 250
    if 170 <= hue_deg < 250:
        return "blue"
    # Purple: 250 - 295
    if 250 <= hue_deg < 295:
        return "purple"
    # Pink: 295 - 345
    if 295 <= hue_deg < 345:
        return "pink"
    
    return "standard" # Better default than hardcoded blue

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("standard")
        sys.exit(0)
    
    color = sys.argv[1]
    print(get_tela_variant(color))
