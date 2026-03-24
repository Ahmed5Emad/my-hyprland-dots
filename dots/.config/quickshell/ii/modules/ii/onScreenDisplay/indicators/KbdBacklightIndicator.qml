import qs.services
import QtQuick
import Quickshell
import Quickshell.Hyprland
import qs.modules.ii.onScreenDisplay

OsdValueIndicator {
    id: root
    icon: "keyboard"
    rotateIcon: false
    scaleIcon: false
    name: Translation.tr("Keyboard")
    value: 0
}
