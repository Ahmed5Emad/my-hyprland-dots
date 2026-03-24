# Custom Hyprland Dots

This repository is a customized fork of the excellent [end-4/dots-hyprland](https://github.com/end-4/dots-hyprland) configuration. All credit for the original core setup, architecture, and beautiful Material You-based scripts goes to **end-4** and the illogical-impulse community.

## Customizations
The following local changes have been made to tailor this rice to my preferences:

- **Keyboard Backlight Control:** Added a custom script (`kbd_backlight.sh`) to control keyboard brightness with `FN+F2` (decrease) and `FN+F3` (increase).
- **Native OSD Integration:** Integrated the keyboard backlight into the Quickshell On-Screen Display (OSD), matching the design of the system volume and brightness indicators.
- **Game Launcher:** Added and integrated a custom Game Launcher script.
- **UI Modifications:** Adjusted the UI roundness modifiers across the system.
- **Icon Theming:** Added new custom icon theming configurations to match the setup.
- **Tela Circle Icons:** Modified the installation script (`sdata/subcmd-install/3.files.sh`) to automatically clone and install the [Tela Circle Standard icon theme](https://github.com/vinceliuice/Tela-circle-icon-theme) directly from its source repository during a fresh install.
- **Improved Synchronization:** Added a `sync.sh` script to safely sync your active configurations from `~/.config` into the repository for easy backup.

## Installation
You can follow the standard installation process. The installer will pull in these customized scripts and automatically configure the Tela icons for you:

```bash
git clone https://github.com/Ahmed5Emad/my-hyprland-dots.git
cd my-hyprland-dots
./setup install
```

## Maintenance
To keep your repository updated with your local changes, run the sync script:

```bash
./sync.sh
```
This script only syncs folders that already exist in the repository's `dots/` directory, ensuring your backup stays clean and focused on your configurations.
