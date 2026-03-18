pragma Singleton

import qs.modules.common
import qs.modules.common.functions
import QtQuick
import Quickshell
import Quickshell.Io

Singleton {
    id: root

    property list<var> games: []
    property bool loading: false

    function refresh() {
        if (loading) return;
        loading = true;
        console.log("[GameLauncher] Refreshing games...");
        let cmd = ["python3", Quickshell.shellPath("scripts/gamelauncher/catalog.py"), "--json"];
        if (Config.options.games.steam) {
            cmd.push("--steam");
        }
        catalogProc.command = cmd;
        catalogProc.running = true;
    }

    Component.onCompleted: {
        refresh();
    }

    Connections {
        target: GlobalStates
        function onGameLauncherOpenChanged() {
            if (GlobalStates.gameLauncherOpen) {
                root.refresh();
            }
        }
    }

    Process {
        id: catalogProc
        command: ["python3", Quickshell.shellPath("scripts/gamelauncher/catalog.py"), "--json"]
        stdout: StdioCollector {
            onStreamFinished: {
                console.log("[GameLauncher] Catalog process finished. Text length:", text.length);
                try {
                    const data = JSON.parse(text);
                    root.games = data;
                    console.log("[GameLauncher] Successfully parsed", data.length, "games.");
                } catch (e) {
                    console.error("[GameLauncher] Failed to parse games JSON:", e);
                    console.error("[GameLauncher] Raw text:", text);
                }
                root.loading = false;
            }
        }
        onExited: (exitCode, exitStatus) => {
            if (exitCode !== 0) {
                console.error("[GameLauncher] Process exited with code", exitCode, "and status", exitStatus);
            }
        }
    }
}
