#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
import requests
import re

# Set Heroic config path
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
XDG_CACHE_HOME = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
HEROIC_CONFIG_PATH = Path(XDG_CONFIG_HOME) / "heroic"
HEROIC_COVER_CACHE = Path(XDG_CACHE_HOME) / "quickshell" / "heroic_covers"

def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

def download_cover(name, url):
    if not url or not url.startswith('http'):
        return url
        
    ext = url.split('.')[-1].split('?')[0]
    if len(ext) > 4 or len(ext) < 2: ext = 'jpg' # fallback
    filename = f"{sanitize_filename(name)}.{ext}"
    local_path = HEROIC_COVER_CACHE / filename
    
    if local_path.exists():
        return str(local_path)
        
    try:
        HEROIC_COVER_CACHE.mkdir(parents=True, exist_ok=True)
        # Use a real user agent to avoid 403s
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(response.content)
            return str(local_path)
    except Exception as e:
        sys.stderr.write(f"Error downloading cover for {name}: {e}\n")
        
    return url # Return original URL if download fails

def get_heroic_games():
    games = []
    
    # 0. Load installation status
    installed_ids = set()
    for inst_file in ["legendary_install_info.json", "gog_install_info.json", "nile_install_info.json"]:
        inst_path = HEROIC_CONFIG_PATH / "store_cache" / inst_file
        if inst_path.exists():
            try:
                with open(inst_path, 'r') as f:
                    inst_data = json.load(f)
                    for app_id, data in inst_data.items():
                        if app_id == "__timestamp": continue
                        if isinstance(data, dict) and data.get("install") is not None:
                            installed_ids.add(app_id)
            except Exception:
                pass

    # 1. Sideloaded games
    sideload_path = HEROIC_CONFIG_PATH / "sideload_apps" / "library.json"
    if sideload_path.exists():
        try:
            with open(sideload_path, 'r') as f:
                data = json.load(f)
                for g in data.get("games", []):
                    if not g.get("is_installed", True): continue
                    
                    app_id = g.get("app_name")
                    title = g.get("title")
                    art_url = g.get("art_cover")
                    
                    cover = download_cover(title, art_url)
                    
                    games.append({
                        "id": app_id,
                        "name": title,
                        "runner": "heroic",
                        "cover": cover,
                        "run_command": f"xdg-open heroic://launch/sideload/{app_id}"
                    })
        except Exception:
            pass

    # 2. Titles and Covers map for other games
    titles_map = {}
    covers_map = {}
    for lib_file in ["legendary_library.json", "gog_library.json", "nile_library.json"]:
        lib_path = HEROIC_CONFIG_PATH / "store_cache" / lib_file
        if lib_path.exists():
            try:
                with open(lib_path, 'r') as f:
                    data = json.load(f)
                    items = data.get("library", []) if isinstance(data, dict) and "library" in data else data
                    
                    if isinstance(items, list):
                        for item in items:
                            if not isinstance(item, dict): continue
                            app_id = item.get("app_name") or item.get("appId")
                            if not app_id: continue
                            
                            if item.get("is_installed"):
                                installed_ids.add(app_id)
                            
                            title = item.get("title") or item.get("appName")
                            if not title:
                                about = item.get("extra", {}).get("about", {})
                                title = about.get("title") or about.get("description")
                                if title and len(title) > 100: title = None
                            
                            if title: titles_map[app_id] = title
                            if item.get("art_cover"): covers_map[app_id] = item.get("art_cover")
                                
                    elif isinstance(items, dict):
                        for app_id, item in items.items():
                            if isinstance(item, dict):
                                if item.get("is_installed"): installed_ids.add(app_id)
                                titles_map[app_id] = item.get("title", app_id)
                                if item.get("art_cover"): covers_map[app_id] = item.get("art_cover")
                            else:
                                titles_map[app_id] = item
            except Exception:
                pass

    # 3. Epic/GOG games (from GamesConfig) - ONLY if installed
    games_config_dir = HEROIC_CONFIG_PATH / "GamesConfig"
    if games_config_dir.exists():
        for p in games_config_dir.glob("*.json"):
            app_id = p.stem
            if app_id not in installed_ids: continue
            
            if not any(g["id"] == app_id for g in games):
                title = titles_map.get(app_id, app_id)
                
                cover = None
                icon_path = HEROIC_CONFIG_PATH / "icons" / f"{app_id}.jpg"
                if icon_path.exists():
                    cover = str(icon_path)
                else:
                    for candidate in (HEROIC_CONFIG_PATH / "icons").glob(f"{app_id}*"):
                        if not candidate.name.endswith('$PART'):
                            cover = str(candidate)
                            break
                
                if not cover and app_id in covers_map:
                    cover = download_cover(title, covers_map[app_id])

                games.append({
                    "id": app_id,
                    "name": title,
                    "runner": "heroic",
                    "cover": cover,
                    "run_command": f"xdg-open heroic://launch/{app_id}"
                })

    return games

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    games = get_heroic_games()
    
    result = []
    for g in games:
        result.append({
            "id": g["id"],
            "name": g["name"],
            "runner": "heroic",
            "cover": g["cover"],
            "run_command": g["run_command"]
        })

    if args.json:
        print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
