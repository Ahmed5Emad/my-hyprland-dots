#!/usr/bin/env python3
import os
import sqlite3
import yaml
from pathlib import Path
import time

def parse_bin_vdf(f):
    def read_string(f):
        res = bytearray()
        while True:
            c = f.read(1)
            if not c or c == b'\x00': break
            res += c
        return res.decode('utf-8', 'ignore')

    def parse_node(f):
        node = {}
        while True:
            type_byte = f.read(1)
            if not type_byte or type_byte == b'\x08':
                break
            name = read_string(f)
            if type_byte == b'\x00':
                node[name] = parse_node(f)
            elif type_byte == b'\x01':
                node[name] = read_string(f)
            elif type_byte == b'\x02':
                node[name] = int.from_bytes(f.read(4), 'little', signed=True)
            else:
                pass 
        return node

    b = f.read(1)
    if b != b'\x00': return {}
    name = read_string(f)
    if name.lower() != 'shortcuts': return {}
    return parse_node(f)

def slugify(text):
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")

def get_steam_shortcuts():
    bases = [
        Path.home() / ".local/share/Steam/userdata",
        Path.home() / ".steam/root/userdata",
        Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/userdata"
    ]
    
    shortcuts_data = {}
    
    for base in bases:
        if base.exists():
            for config_dir in base.glob("*/config"):
                vdf_path = config_dir / "shortcuts.vdf"
                if vdf_path.exists():
                    try:
                        with open(vdf_path, "rb") as f:
                            data = parse_bin_vdf(f)
                            for k, v in data.items():
                                if isinstance(v, dict) and 'AppName' in v and 'appid' in v:
                                    shortcuts_data[v['AppName']] = v['appid']
                    except Exception as e:
                        print(f"Error parsing {vdf_path}: {e}")
    return shortcuts_data

def sync_to_lutris():
    shortcuts = get_steam_shortcuts()
    if not shortcuts:
        print("No Steam shortcuts found.")
        return

    lutris_db = Path.home() / ".local/share/lutris/pga.db"
    lutris_games_dir = Path.home() / ".local/share/lutris/games"
    
    if not lutris_db.exists():
        print(f"Lutris DB not found at {lutris_db}")
        return

    conn = sqlite3.connect(lutris_db)
    cur = conn.cursor()
    
    added_count = 0
    
    for app_name, appid in shortcuts.items():
        unsigned_short = appid & 0xFFFFFFFF
        long_id = (unsigned_short << 32) | 0x02000000
        
        slug = slugify(app_name)
        
        cur.execute("SELECT id FROM games WHERE name = ?", (app_name,))
        row = cur.fetchone()
        if row:
            print(f"Skipping '{app_name}' - already in Lutris.")
            continue
            
        cur.execute('''
            INSERT INTO games (name, slug, installer_slug, runner, installed, installed_at)
            VALUES (?, ?, 'steam-shortcut-sync', 'linux', 1, ?)
        ''', (app_name, slug, int(time.time())))
        
        game_id = cur.lastrowid
        configpath = f"{slug}-{game_id}"
        
        cur.execute("UPDATE games SET configpath = ? WHERE id = ?", (configpath, game_id))
        
        lutris_games_dir.mkdir(parents=True, exist_ok=True)
        yml_path = lutris_games_dir / f"{configpath}.yml"
        
        config = {
            "game": {
                "args": f"steam://rungameid/{long_id}",
                "exe": "/usr/bin/steam"
            }
        }
        
        with open(yml_path, "w") as f:
            yaml.dump(config, f)
            
        print(f"Added '{app_name}' to Lutris (Launch ID: {long_id})")
        added_count += 1
        
    conn.commit()
    conn.close()
    
    print(f"\nSync complete! Added {added_count} games.")
    print("Open Lutris to automatically fetch their covers from IGDB.")

if __name__ == '__main__':
    sync_to_lutris()