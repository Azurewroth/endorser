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

CONFIG_FILE = "config.json"

GAMES = {
    "Skyrim Special Edition": "skyrimspecialedition",
    "Fallout 4": "fallout4",
    "Skyrim Legendary Edition": "skyrim",
    "Fallout New Vegas": "falloutnv",
    "Witcher 3": "witcher3"
}

def endorse_mod(api_key, game_domain, mod_id):
    url = f"https://api.nexusmods.com/v1/games/{game_domain}/mods/{mod_id}/endorse.json"
    headers = {"apikey": api_key}
    response = requests.post(url, headers=headers)
    return response.status_code == 200, response.status_code, response.text

def process_mods(api_key, game_domain, mods_folder, output_box, status_var, progress_var, root):
    count_endorsed = 0
    count_total = 0
    mods = [mod_name for mod_name in os.listdir(mods_folder)]
    output_box.insert(tk.END, f"Found mods: {mods}\n")
    for idx, mod_name in enumerate(mods, 1):
        mod_folder = os.path.join(mods_folder, mod_name)
        meta_ini = os.path.join(mod_folder, "meta.ini")
        if not os.path.isfile(meta_ini):
            continue

        config = configparser.ConfigParser()
        try:
            with open(meta_ini, encoding="utf-8-sig") as f:
                content = f.read()
                # Remove all BOMs from the start
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
        if success:
            output_box.insert(tk.END, f"✅ Endorsed '{mod_name}' (ID: {mod_id})\n")
            if 'General' not in config:
                config['General'] = {}
            config['General']['endorsed'] = 'true'
            with open(meta_ini, 'w', encoding='utf-8-sig') as configfile:
                config.write(configfile)
            count_endorsed += 1
        else:
            output_box.insert(tk.END, f"❌ Failed to endorse '{mod_name}' (ID: {mod_id}): {code} {text}\n")

        count_total += 1
        output_box.see(tk.END)
        percent = (idx / len(mods)) * 100
        root.after(0, progress_var.set, percent)
        root.after(0, status_var.set, f"Processing {idx}/{len(mods)}: {mod_name}")

    output_box.insert(tk.END, f"\nFinished: {count_endorsed}/{count_total} endorsed.\n")
    root.after(0, status_var.set, "Done.")
    root.after(0, progress_var.set, 100)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Decode API key if present
                if "api_key" in data and data["api_key"]:
                    data["api_key"] = base64.b64decode(data["api_key"]).decode()
                return data
            except Exception:
                return {}
    return {}

def save_config(api_key, game, profiles_folder, mods_folder, profile):
    data = {
        "api_key": base64.b64encode(api_key.encode()).decode() if api_key else "",
        "last_game": game,
        "profiles_folder": profiles_folder,
        "mods_folder": mods_folder,
        "last_profile": profile
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def start_gui():
    # Load config on startup
    config = load_config()

    root = tk.Tk()
    root.title("Nexus Batch Endorser for MO2")
    root.geometry("600x600")

    api_key_var = tk.StringVar(value=config.get("api_key", ""))
    saved_game = config.get("last_game", list(GAMES.keys())[0])
    if saved_game not in GAMES:
        saved_game = list(GAMES.keys())[0]
    selected_game = tk.StringVar(value=saved_game)
    profiles_folder_var = tk.StringVar(value=config.get("profiles_folder", ""))
    mods_folder_var = tk.StringVar(value=config.get("mods_folder", ""))
    profile_options = tk.StringVar(value=config.get("last_profile", ""))

    def browse_profiles_folder():
        folder = filedialog.askdirectory()
        if folder:
            profiles_folder_var.set(folder)
            update_profiles_dropdown(folder)

    def update_profiles_dropdown(folder):
        try:
            profiles = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
            if profiles:
                profile_options.set(profiles[0])
                menu = profiles_dropdown["menu"]
                menu.delete(0, "end")
                for profile in profiles:
                    menu.add_command(label=profile, command=lambda value=profile: profile_options.set(value))
            else:
                messagebox.showwarning("No Profiles", "No profiles found in the selected folder.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def browse_mods_folder():
        folder = filedialog.askdirectory()
        if folder:
            mods_folder_var.set(folder)

    def start_process():
        api_key = api_key_var.get().strip()
        game = GAMES[selected_game.get()]
        mods_folder = mods_folder_var.get().strip()
        profiles_folder = profiles_folder_var.get().strip()
        profile_selected = profile_options.get()

        if not api_key or not mods_folder or not profiles_folder or not profile_selected:
            messagebox.showerror("Missing Info", "Please fill out all required fields.")
            return

        # Save config on start
        save_config(api_key, selected_game.get(), profiles_folder, mods_folder, profile_selected)

        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, f"Starting batch endorsement for {selected_game.get()}...\n")
        output_box.insert(tk.END, f"Selected Profile: {profile_selected}\n")
        output_box.insert(tk.END, f"Profiles Path: {profiles_folder}\n\n")

        status_var.set("Processing...")
        t = threading.Thread(
            target=process_mods,
            args=(api_key, game, mods_folder, output_box, status_var, progress_var, root),
            daemon=True
        )
        t.start()

    api_key_in_config = bool(config.get("api_key"))

    if not api_key_in_config:
        tk.Label(root, text="Nexus API Key:").pack()
        tk.Entry(root, textvariable=api_key_var, width=80).pack()
    # else: do not show the API key entry

    tk.Label(root, text="Select Game:").pack()
    tk.OptionMenu(root, selected_game, *GAMES.keys()).pack()

    tk.Label(root, text="MO2 Profiles Folder:").pack()
    frame_profiles = tk.Frame(root)
    frame_profiles.pack()
    tk.Entry(frame_profiles, textvariable=profiles_folder_var, width=50).pack(side=tk.LEFT)
    tk.Button(frame_profiles, text="Browse...", command=browse_profiles_folder).pack(side=tk.LEFT)

    tk.Label(root, text="Select Profile:").pack()
    profiles_dropdown = tk.OptionMenu(root, profile_options, "")
    profiles_dropdown.pack()

    tk.Label(root, text="MO2 Mods Folder:").pack()
    frame_mods = tk.Frame(root)
    frame_mods.pack()
    tk.Entry(frame_mods, textvariable=mods_folder_var, width=50).pack(side=tk.LEFT)
    tk.Button(frame_mods, text="Browse...", command=browse_mods_folder).pack(side=tk.LEFT)

    tk.Button(root, text="Start Endorsement", command=start_process, bg="green", fg="white").pack(pady=10)

    status_var = tk.StringVar()
    status_var.set("Ready.")
    status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, mode='determinate')
    progress_bar.pack(side=tk.BOTTOM, fill=tk.X)

    show_output_var = tk.BooleanVar(value=True)

    def toggle_output_box():
        if show_output_var.get():
            output_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        else:
            output_box.pack_forget()

    tk.Checkbutton(
        root,
        text="Show Output Text Box",
        variable=show_output_var,
        command=toggle_output_box
    ).pack()

    output_box = scrolledtext.ScrolledText(root, width=80, height=20)
    if show_output_var.get():
        output_box.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    root.mainloop()

    # Save config on exit
    api_key = api_key_var.get().strip()
    game = selected_game.get()
    profiles_folder = profiles_folder_var.get().strip()
    mods_folder = mods_folder_var.get().strip()
    profile_selected = profile_options.get()
    save_config(api_key, game, profiles_folder, mods_folder, profile_selected)

if __name__ == "__main__":
    start_gui()

