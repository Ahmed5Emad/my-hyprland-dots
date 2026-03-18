# Custom Hyprland Dots

This repository is a customized fork of the excellent [end-4/dots-hyprland](https://github.com/end-4/dots-hyprland) configuration. All credit for the original core setup, architecture, and beautiful Material You-based scripts goes to **end-4** and the illogical-impulse community.

## Customizations
The following local changes have been made to tailor this rice to my preferences:

- **Game Launcher:** Added and integrated a custom Game Launcher script.
- **UI Modifications:** Adjusted the UI roundness modifiers across the system.
- **Icon Theming:** Added new custom icon theming configurations to match the setup.
- **Tela Circle Icons:** Modified the installation script (`sdata/subcmd-install/3.files.sh`) to automatically clone and install the [Tela Circle Standard icon theme](https://github.com/vinceliuice/Tela-circle-icon-theme) directly from its source repository during a fresh install.
- **Synced Local Files:** Saved custom `.qml` components and configurations from `~/.config/quickshell/` and `~/.config/hypr/` into the `dots/` directory for safe version control.

## Installation
You can follow the standard installation process. The installer will pull in these customized scripts and automatically configure the Tela icons for you:

```bash
git clone https://github.com/Ahmed5Emad/my-hyprland-dots.git
cd my-hyprland-dots
./setup install
```
