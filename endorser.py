# This file is part of Batch Endorser.
# Copyright (C) 2025 Harry Joseph King
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import requests
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import threading
import json
import base64
import time
from cryptography.fernet import Fernet, InvalidToken

CONFIG_FILE = "config.json"
FERNET_KEY_FILE = "config.key"

GAMES = {
    "Skyrim Special Edition": "skyrimspecialedition",
    "Fallout 4": "fallout4",
    "Skyrim Legendary Edition": "skyrim",
    "Fallout New Vegas": "falloutnv",
    "Witcher 3": "witcher3"
}

def get_fernet():
    if not os.path.exists(FERNET_KEY_FILE):
        key = Fernet.generate_key()
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(FERNET_KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

def endorse_mod(api_key, game_domain, mod_id):
    url = f"https://api.nexusmods.com/v1/games/{game_domain}/mods/{mod_id}/endorse.json"
    headers = {"apikey": api_key, "accept": "application/json"}
    response = requests.post(url, headers=headers)
    return response.status_code == 200, response.status_code, response.text

def get_mod_file_id(api_key, game_domain, mod_id):
    """Fetches the primary file ID from the Nexus files endpoint so MO2 can fully verify the mod."""
    try:
        headers = {"apikey": api_key, "accept": "application/json"}
        
        # Try primary/endorsement from main endpoint first
        url_main = f"https://api.nexusmods.com/v1/games/{game_domain}/mods/{mod_id}.json"
        resp = requests.get(url_main, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            fid = data.get("endorsement_file_id") or data.get("primary_file_id")
            if fid:
                return fid
                
        # Fallback to files endpoint if main endpoint didn't provide it
        url_files = f"https://api.nexusmods.com/v1/games/{game_domain}/mods/{mod_id}/files.json"
        resp_files = requests.get(url_files, headers=headers)
        if resp_files.status_code == 200:
            files_data = resp_files.json()
            files_list = files_data.get("files", [])
            if files_list:
                return files_list[0].get("file_id") or files_list[0].get("id")
    except Exception:
        pass
    return None

def process_mods(api_key, game_domain, mods_folder, output_box, status_var, progress_var, root):
    if not os.path.isdir(mods_folder):
        output_box.insert(tk.END, f"❌ Mods folder not found: {mods_folder}\n")
        status_var.set("Mods folder not found!")
        return

    count_endorsed = 0
    count_total = 0
    mods = [mod_name for mod_name in os.listdir(mods_folder)]
    output_box.insert(tk.END, f"Found mods: {len(mods)} items\n")
    
    for idx, mod_name in enumerate(mods, 1):
        mod_folder = os.path.join(mods_folder, mod_name)
        meta_ini = os.path.join(mod_folder, "meta.ini")
        if not os.path.isfile(meta_ini):
            continue

        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve exact case formatting for MO2 config files
        try:
            with open(meta_ini, encoding="utf-8-sig") as f:
                content = f.read()
                while content.startswith('\ufeff'):
                    content = content[1:]
                from io import StringIO
                config.read_file(StringIO(content))
        except (configparser.MissingSectionHeaderError, UnicodeDecodeError) as e:
            output_box.insert(tk.END, f"⚠️ Skipped '{mod_name}': Invalid meta.ini ({e})\n")
            continue

        try:
            mod_id = config.getint('General', 'modid')
        except (configparser.NoOptionError, configparser.NoSectionError, ValueError):
            output_box.insert(tk.END, f"⚠️ Skipped '{mod_name}': No mod ID\n")
            continue

        success, code, text = endorse_mod(api_key, game_domain, mod_id)
        time.sleep(0.25)  # Rate limiting to prevent API blocks during large runs
        
        # Accept successful endorsement (200) or already endorsed response (400)
        if success or code == 400:
            if success:
                output_box.insert(tk.END, f"✅ Endorsed '{mod_name}' (ID: {mod_id})\n")
                count_endorsed += 1
            else:
                output_box.insert(tk.END, f"ℹ️ Syncing flag for '{mod_name}' (ID: {mod_id})\n")
            
            # Ensure General section exists, update endorsed flag and game name
            if not config.has_section('General'):
                config.add_section('General')
            config['General']['endorsed'] = 'true'
            config['General']['gameName'] = game_domain

            # Ensure [installedFiles] section and file ID exist so MO2 clears the '?' icon
            if not config.has_section('installedFiles'):
                config.add_section('installedFiles')
            
            if not config.has_option('installedFiles', '1\\fileid'):
                file_id = get_mod_file_id(api_key, game_domain, mod_id)
                if file_id:
                    config['installedFiles']['size'] = '1'
                    config['installedFiles']['1\\modid'] = str(mod_id)
                    config['installedFiles']['1\\fileid'] = str(file_id)

            # Write changes back with encoding safety
            with open(meta_ini, 'w', encoding='utf-8-sig') as configfile:
                config.write(configfile)
        else:
            output_box.insert(tk.END, f"❌ Failed to endorse '{mod_name}' (ID: {mod_id}): {code} {text}\n")

        count_total += 1
        output_box.see(tk.END)
        percent = (idx / len(mods)) * 100
        root.after(0, progress_var.set, percent)
        root.after(0, status_var.set, f"Processing {idx}/{len(mods)}: {mod_name}")

    output_box.insert(tk.END, f"\nFinished: {count_endorsed} endorsed / processed out of {count_total} total mods.\n")
    root.after(0, status_var.set, "Done.")
    root.after(0, progress_var.set, 100)

def load_config():
    if os.path.exists(CONFIG_FILE):
        fernet = get_fernet()
        try:
            with open(CONFIG_FILE, "rb") as f:
                encrypted = f.read()
                try:
                    decrypted = fernet.decrypt(encrypted)
                    data = json.loads(decrypted.decode("utf-8"))
                except InvalidToken:
                    data = json.loads(encrypted.decode("utf-8"))
                    save_config(
                        data.get("api_key", ""),
                        data.get("last_game", ""),
                        data.get("profiles_folder", ""),
                        data.get("mods_folder", ""),
                        data.get("last_profile", ""),
                        data.get("tracked_mods", {}),
                        data.get("mo2_install_path", "")
                    )
                if "api_key" in data and data["api_key"]:
                    data["api_key"] = base64.b64decode(data["api_key"]).decode()
                if "tracked_mods" not in data:
                    data["tracked_mods"] = {}
                if "mo2_install_path" not in data:
                    data["mo2_install_path"] = ""
                return data
        except Exception:
            return {"tracked_mods": {}, "mo2_install_path": ""}
    return {"tracked_mods": {}, "mo2_install_path": ""}

def save_config(api_key, game, profiles_folder, mods_folder, profile, tracked_mods=None, mo2_install_path=""):
    data = {
        "api_key": base64.b64encode(api_key.encode()).decode() if api
