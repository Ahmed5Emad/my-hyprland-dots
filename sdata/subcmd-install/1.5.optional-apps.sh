# This script is meant to be sourced.
# It's not for directly running.

printf "${STY_CYAN}[$0]: 1.5. Optional application installation\n${STY_RST}"

if [[ "$SKIP_OPTIONALAPPS" == "true" ]]; then
  echo "Skipping optional apps installation as requested."
  return 0
fi

if [[ "$ask" == "false" ]]; then
  echo "Force mode detected or non-interactive. Skipping optional apps installation."
  return 0
fi

install_selected_apps() {
    local category_name="$1"
    local apps_list=("${@:2}")
    local selected=()
    
    echo -e "\n${STY_PURPLE}=== $category_name ===${STY_RST}"
    echo -e "Choose apps to install by entering their ID numbers (separated by space)."
    echo -e "Enter 'a' to install all, or 'n' to skip.\n"

    for i in "${!apps_list[@]}"; do
        IFS=';' read -r name desc arch_pkg fedora_pkg gentoo_pkg <<< "${apps_list[$i]}"
        printf "  ${STY_CYAN}%2d)${STY_RST} %-12s : %s\n" $((i+1)) "$name" "$desc"
    done
    echo -e "  ${STY_CYAN} a)${STY_RST} All"
    echo -e "  ${STY_CYAN} n)${STY_RST} None / Skip"

    echo -ne "\n${STY_BLUE}Selection: ${STY_RST}"
    read -r choices
    
    if [[ "$choices" =~ ^[nN]$ ]]; then
        return 0
    fi
    
    if [[ "$choices" =~ ^[aA]$ ]]; then
        for i in "${!apps_list[@]}"; do selected+=($i); done
    else
        for choice in $choices; do
            if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -le "${#apps_list[@]}" ] && [ "$choice" -gt 0 ]; then
                selected+=($((choice-1)))
            fi
        done
    fi

    for idx in "${selected[@]}"; do
        IFS=';' read -r name desc arch_pkg fedora_pkg gentoo_pkg <<< "${apps_list[$idx]}"
        
        local pkg=""
        case "$OS_GROUP_ID" in
            arch) pkg="$arch_pkg" ;;
            fedora) pkg="$fedora_pkg" ;;
            gentoo) pkg="$gentoo_pkg" ;;
        esac
        
        if [ -z "$pkg" ]; then
            echo -e "${STY_YELLOW}Package for $name not defined for $OS_GROUP_ID. Skipping...${STY_RST}"
            continue
        fi

        echo -e "${STY_BLUE}Installing $name ($pkg)...${STY_RST}"
        case "$OS_GROUP_ID" in
            arch)
                # Use yay if available, otherwise pacman
                if command -v yay >/dev/null 2>&1; then
                    v yay -S --needed --noconfirm "$pkg"
                else
                    v sudo pacman -S --needed --noconfirm "$pkg"
                fi
                ;;
            fedora)
                v sudo dnf install -y "$pkg"
                ;;
            gentoo)
                v sudo emerge --ask=n "$pkg"
                ;;
        esac
    done
}

# Define apps: name;description;arch_pkg;fedora_pkg;gentoo_pkg
optional_apps=(
    "espanso;Cross-platform text expander;espanso-bin;espanso;"
)

gaming_apps=(
    "steam;Digital distribution platform;steam;steam;games-util/steam-launcher"
    "lutris;Open gaming platform;lutris;lutris;games-util/lutris"
    "protonplus;Wine and Proton manager;protonplus;protonplus;"
)

install_selected_apps "Optional Section" "${optional_apps[@]}"
install_selected_apps "Gaming Section" "${gaming_apps[@]}"
