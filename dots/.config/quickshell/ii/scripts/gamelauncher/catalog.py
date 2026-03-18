#!/usr/bin/env python3
"""
Merged catalog for gamelauncher: combine Steam and Lutris entries into one JSON/rofi stream.

Outputs:
  --json : prints array of {backend, id, name, display_name, header, install_dir}
  --rofi-string : prints rofi-ready lines: display_name\0icon\u001f<header>\x1e<backend>:<id>

The script probes for Lutris (flatpak or native) and calls the existing
`gamelauncher/steam.py --json` to get Steam entries.
"""

import json
import subprocess
import os
import sys
from collections import defaultdict


def fetch_entries(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        sys.stderr.write(f"Error fetching entries with {command}: {e}\n")
        return []


def merge_entries(steam_entries, lutris_entries):
    merged = []
    # Create a set of lowercased names from lutris for quick lookup
    lutris_names = {entry["name"].lower() for entry in lutris_entries}

    # Add all Lutris entries
    for entry in lutris_entries:
        entry["backend"] = "lutris"
        entry["display_name"] = entry["name"]
        merged.append(entry)

    # Add Steam entries only if they don't exist in Lutris
    for entry in steam_entries:
        if entry["name"].lower() in lutris_names:
            # Skip steam entry if a lutris entry with the same name exists
            continue
        entry["backend"] = "steam"
        entry["display_name"] = entry["name"]
        merged.append(entry)

    return merged


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output merged JSON")
    parser.add_argument("--rofi-string", action="store_true", help="Output merged rofi strings")
    parser.add_argument("--steam", action="store_true", help="Include Steam entries")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    steam_entries = []
    if args.steam:
        steam_entries = fetch_entries(["python3", os.path.join(script_dir, "steam.py"), "--json"])
    lutris_entries = fetch_entries(["python3", os.path.join(script_dir, "lutris.py"), "--json"])

    merged = merge_entries(steam_entries, lutris_entries)

    if args.json:
        print(json.dumps(merged, indent=4))
        return

    if args.rofi_string:
        for entry in merged:
            rofi_string = f"{entry['display_name']}\t{entry['run_command']}"
            if entry.get("cover"):
                rofi_string += f"\t\x00icon\x1f{entry['cover']}"
            elif entry.get("icon"):
                rofi_string += f"\t\x00icon\x1f{entry['icon']}"
            elif entry.get("header"):
                rofi_string += f"\t\x00icon\x1f{entry['header']}"
            print(rofi_string)


if __name__ == "__main__":
    main()
