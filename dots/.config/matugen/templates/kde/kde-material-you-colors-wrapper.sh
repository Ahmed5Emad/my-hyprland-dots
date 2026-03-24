#!/usr/bin/env bash

XDG_STATE_HOME="${XDG_STATE_HOME:-$HOME/.local/state}"

color=$(tr -d '\n' < "$XDG_STATE_HOME/quickshell/user/generated/color.txt")
icon_color=$color
if [ -f "$XDG_STATE_HOME/quickshell/user/generated/icon_color.txt" ]; then
    icon_color=$(tr -d '\n' < "$XDG_STATE_HOME/quickshell/user/generated/icon_color.txt")
elif [ -f "$XDG_STATE_HOME/quickshell/user/generated/primary_color.txt" ]; then
    icon_color=$(tr -d '\n' < "$XDG_STATE_HOME/quickshell/user/generated/primary_color.txt")
fi

# Parse --scheme-variant flag first so we know what scheme we are dealing with
scheme_variant_str=""
args=("$@")
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scheme-variant)
            scheme_variant_str="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done
# Restore arguments for the final command
set -- "${args[@]}"

# Dynamically pick the closest Tela-circle icon theme based on the generated vibrant color
tela_variant=$(python3 "$HOME/.config/quickshell/ii/scripts/colors/get_closest_tela.py" "$icon_color")

# User strictly requested icons NOT to be grey. Fall back to raw wallpaper color if it evaluates to grey!
if [[ "$tela_variant" == "grey" ]]; then
    tela_variant=$(python3 "$HOME/.config/quickshell/ii/scripts/colors/get_closest_tela.py" "$color")
    # If the raw wallpaper is ALSO grey, pick a generic vibrant color to guarantee no grey icons
    if [[ "$tela_variant" == "grey" ]]; then
        tela_variant="blue"
    fi
fi
sed -i "s/^iconslight = .*/iconslight = Tela-circle-$tela_variant-light/" "$HOME/.config/kde-material-you-colors/config.conf"
sed -i "s/^iconsdark = .*/iconsdark = Tela-circle-$tela_variant-dark/" "$HOME/.config/kde-material-you-colors/config.conf"

current_mode=$(gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null | tr -d "'")
if [[ "$current_mode" == "prefer-dark" ]]; then
    mode_flag="-d"
else
    mode_flag="-l"
fi

# Parse --scheme-variant flag
scheme_variant_str=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scheme-variant)
            scheme_variant_str="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Map string variant to integer
case "$scheme_variant_str" in
    scheme-content) sv_num=0 ;;
    scheme-expressive) sv_num=1 ;;
    scheme-fidelity) sv_num=2 ;;
    scheme-monochrome) sv_num=3 ;;
    scheme-neutral) sv_num=4 ;;
    scheme-tonal-spot) sv_num=5 ;;
    scheme-vibrant) sv_num=6 ;;
    scheme-rainbow) sv_num=7 ;;
    scheme-fruit-salad) sv_num=8 ;;
    "") sv_num=5 ;;
    *)
        echo "Unknown scheme variant: $scheme_variant_str" >&2
        exit 1
        ;;
esac

source "$(eval echo $ILLOGICAL_IMPULSE_VIRTUAL_ENV)/bin/activate"
kde-material-you-colors "$mode_flag" --color "$color" -sv "$sv_num"
deactivate
