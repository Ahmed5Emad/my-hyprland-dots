import qs
import qs.services
import qs.modules.common
import qs.modules.common.widgets
import qs.modules.common.functions
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland

Scope {
    id: root

    PanelWindow {
        id: window
        visible: GlobalStates.gameLauncherOpen

        WlrLayershell.namespace: "quickshell:gamelauncher"
        WlrLayershell.layer: WlrLayer.Top
        WlrLayershell.keyboardFocus: GlobalStates.gameLauncherOpen ? WlrKeyboardFocus.OnDemand : WlrKeyboardFocus.None
        color: "transparent"

        anchors {
            top: true
            bottom: true
            left: true
        }
        width: screen.width * 0.25

        // Replicate rofi-like dismiss behavior
        Connections {
            target: GlobalStates
            function onGameLauncherOpenChanged() {
                if (GlobalStates.gameLauncherOpen) {
                    GlobalFocusGrab.addDismissable(window);
                    listView.forceActiveFocus();
                } else {
                    GlobalFocusGrab.dismiss();
                }
            }
        }

        Connections {
            target: GlobalFocusGrab
            function onDismissed() {
                GlobalStates.gameLauncherOpen = false;
            }
        }

        Rectangle {
            anchors.fill: parent
            color: Appearance.colors.colBackgroundSurfaceContainer

            ColumnLayout {
                anchors.fill: parent
                spacing: 0



                ListView {
                    id: listView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: GameLauncher.games
                    spacing: 15
                    clip: true
                    topMargin: 20
                    bottomMargin: 20
                    leftMargin: 20
                    rightMargin: 20
                    
                    
                    highlight: Rectangle {
                        color: Appearance.colors.colPrimaryContainer
                        radius: 10
                    }
                    highlightMoveDuration: 150

                    delegate: RippleButton {
                        width: listView.width - listView.leftMargin - listView.rightMargin
                        height: 160
                        buttonRadius: 10
                        
                        // element selected logic
                        colBackground: (ListView.isCurrentItem || hovered) ? Appearance.colors.colPrimaryContainer : "transparent"
                        
                        onClicked: {
                            Quickshell.execDetached(["bash", "-c", modelData.run_command]);
                            GlobalStates.gameLauncherOpen = false;
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 15
                            anchors.rightMargin: 15
                            spacing: 20

                            // element-icon
                            Rectangle {
                                width: 100
                                height: 140
                                radius: 15 // more modern radius
                                clip: true
                                color: Appearance.colors.colLayer1

                                Image {
                                    anchors.fill: parent
                                    source: {
                                        const path = modelData.cover || modelData.header || modelData.icon || "";
                                        return path.startsWith("/") ? `file://${path}` : path;
                                    }
                                    fillMode: Image.PreserveAspectCrop
                                    asynchronous: true
                                    onStatusChanged: {
                                        if (status === Image.Error) {
                                            console.error("[GameLauncher] Error loading image for", modelData.name, "from path", source);
                                        }
                                    }
                                }
                            }

                            // element-text
                            StyledText {
                                Layout.fillWidth: true
                                text: modelData.name
                                font.pixelSize: Appearance.font.pixelSize.large
                                color: Appearance.colors.colOnSurface
                                elide: Text.ElideRight
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }

                    Keys.onPressed: (event) => {
                        if (event.key === Qt.Key_Escape) {
                            GlobalStates.gameLauncherOpen = false;
                            event.accepted = true;
                        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                            if (currentItem) currentItem.clicked();
                            event.accepted = true;
                        }
                    }

                    // Empty state
                    StyledText {
                        anchors.centerIn: parent
                        text: GameLauncher.loading ? "Searching for games..." : "No games found."
                        visible: listView.count === 0
                        color: Appearance.colors.colOnSurfaceVariant
                        font.pixelSize: Appearance.font.pixelSize.normal
                    }
                }
            }
        }
    }

    IpcHandler {
        target: "gamelauncher"
        function toggle() { GlobalStates.gameLauncherOpen = !GlobalStates.gameLauncherOpen; }
        function open() { GlobalStates.gameLauncherOpen = true; }
        function close() { GlobalStates.gameLauncherOpen = false; }
    }
}
