#!/usr/bin/env python3
"""
Merged catalog for gamelauncher: combine Steam and Lutris entries into one JSON/rofi stream.
"""

import json
import subprocess
import os
import sys

def fetch_entries(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        sys.stderr.write(f"Error fetching entries with {command}: {e}\n")
        return []

def merge_entries(steam_entries, lutris_entries, heroic_entries):
    merged = []
    seen_names = set()

    # Priority 1: Lutris
    for entry in lutris_entries:
        name = entry["name"].lower()
        if name not in seen_names:
            entry["backend"] = "lutris"
            entry["display_name"] = entry["name"]
            merged.append(entry)
            seen_names.add(name)

    # Priority 2: Steam
    for entry in steam_entries:
        name = entry["name"].lower()
        if name not in seen_names:
            entry["backend"] = "steam"
            entry["display_name"] = entry["name"]
            merged.append(entry)
            seen_names.add(name)

    # Heroic: Always add (allow duplicates as requested)
    for entry in heroic_entries:
        entry["backend"] = "heroic"
        entry["display_name"] = entry["name"]
        merged.append(entry)

    return merged

def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Output merged JSON")
    parser.add_argument("--rofi-string", action="store_true", help="Output merged rofi strings")
    parser.add_argument("--steam", action="store_true", help="Include Steam entries")
    parser.add_argument("--heroic", action="store_true", help="Include Heroic entries")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    steam_entries = []
    if args.steam:
        steam_entries = fetch_entries(["python3", os.path.join(script_dir, "steam.py"), "--json"])
    
    heroic_entries = []
    if args.heroic:
        heroic_entries = fetch_entries(["python3", os.path.join(script_dir, "heroic.py"), "--json"])

    lutris_entries = fetch_entries(["python3", os.path.join(script_dir, "lutris.py"), "--json"])

    merged = merge_entries(steam_entries, lutris_entries, heroic_entries)

    if args.json:
        print(json.dumps(merged, indent=4))
        return

    if args.rofi_string:
        for entry in merged:
            rofi_string = f"{entry['display_name']}\t{entry['run_command']}"
            icon = entry.get("cover") or entry.get("icon") or entry.get("header")
            if icon:
                rofi_string += f"\t\x00icon\x1f{icon}"
            print(rofi_string)

if __name__ == "__main__":
    main()
