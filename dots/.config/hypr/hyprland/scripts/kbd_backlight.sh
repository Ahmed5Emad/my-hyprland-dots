#!/usr/bin/env bash

# Find the keyboard backlight device
DEVICE=$(brightnessctl --list | grep -oP "Device '\K[^']*(?=')" | grep "kbd_backlight" | head -n 1)

if [[ -z "$DEVICE" ]]; then
    exit 1
fi

case "$1" in
    increase)
        brightnessctl -d "$DEVICE" s +1
        ;;
    decrease)
        brightnessctl -d "$DEVICE" s 1-
        ;;
    *)
        echo "Usage: $0 {increase|decrease}"
        exit 1
        ;;
esac

# Get new brightness level
CURRENT=$(brightnessctl -d "$DEVICE" g)
MAX=$(brightnessctl -d "$DEVICE" m)

# Calculate fraction (0 to 1) for Quickshell OSD
FRACTION=$(awk "BEGIN {print $CURRENT / $MAX}")

# Trigger Quickshell OSD
qs -c ii ipc call osdKbd trigger "$FRACTION"
