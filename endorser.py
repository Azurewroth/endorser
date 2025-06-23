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
    headers = {"apikey": api_key}
    response = requests.post(url, headers=headers)
    return response.status_code == 200, response.status_code, response.text

def process_mods(api_key, game_domain, mods_folder, output_box, status_var, progress_var, root):
    if not os.path.isdir(mods_folder):
        output_box.insert(tk.END, f"❌ Mods folder not found: {mods_folder}\n")
        status_var.set("Mods folder not found!")
        return

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
        fernet = get_fernet()
        try:
            with open(CONFIG_FILE, "rb") as f:
                encrypted = f.read()
                try:
                    # Try to decrypt as Fernet
                    decrypted = fernet.decrypt(encrypted)
                    data = json.loads(decrypted.decode("utf-8"))
                except InvalidToken:
                    # If decryption fails, try to load as plain JSON and then encrypt it
                    data = json.loads(encrypted.decode("utf-8"))
                    # Immediately encrypt and save
                    save_config(
                        data.get("api_key", ""),
                        data.get("last_game", ""),
                        data.get("profiles_folder", ""),
                        data.get("mods_folder", ""),
                        data.get("last_profile", ""),
                        data.get("tracked_mods", {}),
                        data.get("mo2_install_path", "")
                    )
                # Decode API key if present
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
        "api_key": base64.b64encode(api_key.encode()).decode() if api_key else "",
        "last_game": game,
        "profiles_folder": profiles_folder,
        "mods_folder": mods_folder,
        "last_profile": profile,
        "tracked_mods": tracked_mods if tracked_mods is not None else {},
        "mo2_install_path": mo2_install_path
    }
    fernet = get_fernet()
    json_bytes = json.dumps(data, indent=2).encode("utf-8")
    encrypted = fernet.encrypt(json_bytes)
    with open(CONFIG_FILE, "wb") as f:
        f.write(encrypted)

def add_tracked_mod(config, game, mod_id, author):
    tracked = config.get("tracked_mods", {})
    if game not in tracked:
        tracked[game] = []
    # Add meta_mtime with the current timestamp
    tracked[game].append({"mod_id": mod_id, "author": author, "meta_mtime": int(os.path.getmtime(os.path.join(config.get('mods_folder', ''), f"{mod_id}.esp"))) if os.path.isfile(os.path.join(config.get('mods_folder', ''), f"{mod_id}.esp")) else 0})
    config["tracked_mods"] = tracked
    save_config(
        config.get("api_key", ""),
        config.get("last_game", ""),
        config.get("profiles_folder", ""),
        config.get("mods_folder", ""),
        config.get("last_profile", ""),
        tracked,
        config.get("mo2_install_path", "")
    )

def get_tracked_mods(config, game):
    return config.get("tracked_mods", {}).get(game, [])

def auto_track_mods(config, mods_folder, game):
    if not mods_folder or not os.path.isdir(mods_folder):
        return  # Do nothing if the folder is not set or doesn't exist
    tracked = config.get("tracked_mods", {})
    if game not in tracked:
        tracked[game] = []
    tracked_mods = {entry["mod_id"]: entry for entry in tracked[game]}
    updated = False

    for mod_name in os.listdir(mods_folder):
        mod_folder = os.path.join(mods_folder, mod_name)
        meta_ini = os.path.join(mod_folder, "meta.ini")
        if not os.path.isfile(meta_ini):
            continue
        config_parser = configparser.ConfigParser()
        try:
            with open(meta_ini, encoding="utf-8-sig") as f:
                content = f.read()
                while content.startswith('\ufeff'):
                    content = content[1:]
                from io import StringIO
                config_parser.read_file(StringIO(content))
        except Exception:
            continue
        try:
            mod_id = str(config_parser.getint('General', 'modid'))
            author = config_parser.get('General', 'author', fallback="Unknown")
        except Exception:
            continue
        mtime = os.path.getmtime(meta_ini)
        if mod_id not in tracked_mods or tracked_mods[mod_id]["meta_mtime"] != mtime:
            tracked_mods[mod_id] = {
                "mod_id": mod_id,
                "author": author,
                "meta_mtime": mtime,
                "changed": mod_id in tracked_mods and tracked_mods[mod_id]["meta_mtime"] != mtime
            }
            updated = True

    # Convert back to list
    config["tracked_mods"][game] = list(tracked_mods.values())
    if updated:
        save_config(
            config.get("api_key", ""),
            config.get("last_game", ""),
            config.get("profiles_folder", ""),
            config.get("mods_folder", ""),
            config.get("last_profile", ""),
            config.get("tracked_mods", {}),
            config.get("mo2_install_path", "")
        )

def check_mod_updates(api_key, game_domain, tracked_mods):
    """Returns a dict of mod_id -> True if update available, else False."""
    updates = {}
    headers = {"apikey": api_key, "Accept": "application/json"}
    for mod in tracked_mods:
        mod_id = mod["mod_id"]
        local_mtime = int(mod.get("meta_mtime", 0))
        try:
            url = f"https://api.nexusmods.com/v1/games/{game_domain}/mods/{mod_id}.json"
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                # Parse the updated_time from Nexus (format: 2024-06-22T16:39:00+00:00)
                from datetime import datetime
                nexus_updated = int(datetime.strptime(data["updated_time"], "%Y-%m-%dT%H:%M:%S%z").timestamp())
                updates[mod_id] = nexus_updated > local_mtime
            else:
                updates[mod_id] = False
        except Exception:
            updates[mod_id] = False
    return updates

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
    mo2_install_path_var = tk.StringVar(value=config.get("mo2_install_path", ""))

    # Auto-track mods if mods folder is set
    if mods_folder_var.get() and selected_game.get():
        auto_track_mods(config, mods_folder_var.get(), selected_game.get())

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
            auto_track_mods(config, folder, selected_game.get())

    def start_process():
        endorse_btn.config(state=tk.DISABLED)
        show_tracked_btn.config(state=tk.DISABLED)
        api_key = api_key_var.get().strip()
        game = GAMES[selected_game.get()]
        mods_folder = mods_folder_var.get().strip()
        profiles_folder = profiles_folder_var.get().strip()
        profile_selected = profile_options.get()

        if not api_key or not mods_folder or not profiles_folder or not profile_selected:
            messagebox.showerror("Missing Info", "Please fill out all required fields.")
            endorse_btn.config(state=tk.NORMAL)
            show_tracked_btn.config(state=tk.NORMAL)
            return

        # Save config on start
        save_config(api_key, selected_game.get(), profiles_folder, mods_folder, profile_selected, config.get("tracked_mods", {}), mo2_install_path_var.get().strip())

        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, f"Starting batch endorsement for {selected_game.get()}...\n")
        output_box.insert(tk.END, f"Selected Profile: {profile_selected}\n")
        output_box.insert(tk.END, f"Profiles Path: {profiles_folder}\n\n")

        status_var.set("Processing...")

        def on_finish():
            endorse_btn.config(state=tk.NORMAL)
            show_tracked_btn.config(state=tk.NORMAL)

        def run_endorse():
            process_mods(api_key, game, mods_folder, output_box, status_var, progress_var, root)
            root.after(0, on_finish)

        t = threading.Thread(
            target=run_endorse,
            daemon=True
        )
        t.start()

    def gui_add_tracked_mod():
        mod_id = track_mod_id_var.get().strip()
        author = track_author_var.get().strip()
        game = selected_game.get()
        if not mod_id or not author:
            messagebox.showwarning("Missing Info", "Enter both Mod ID and Author.")
            return
        add_tracked_mod(config, game, mod_id, author)
        messagebox.showinfo("Tracked", f"Tracked mod {mod_id} by {author} for {game}.")

    def gui_show_tracked_mods():
        endorse_btn.config(state=tk.DISABLED)
        show_tracked_btn.config(state=tk.DISABLED)
        status_var.set("Checking Nexus Mods for updates...")
        def worker():
            api_key = api_key_var.get().strip()
            game_name = selected_game.get()
            game_domain = GAMES[game_name]
            mods = get_tracked_mods(config, game_name)
            if not mods:
                msg = f"No tracked mods for {game_name}.\n"
            else:
                msg = f"Tracked mods for {game_name}:\n"
                updates = check_mod_updates(api_key, game_domain, mods)
                for entry in mods:
                    changed = " (Changed)" if entry.get("changed") else ""
                    update_str = " [Update Available]" if updates.get(entry["mod_id"]) else ""
                    msg += f"Mod ID: {entry['mod_id']}, Author: {entry['author']}{changed}{update_str}\n"
            def show_result():
                output_box.delete(1.0, tk.END)
                output_box.insert(tk.END, msg)
                endorse_btn.config(state=tk.NORMAL)
                show_tracked_btn.config(state=tk.NORMAL)
                status_var.set("Ready.")
            root.after(0, show_result)
        threading.Thread(target=worker, daemon=True).start()

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

    tk.Label(root, text="MO2 Install Path:").pack()
    frame_mo2 = tk.Frame(root)
    frame_mo2.pack()
    tk.Entry(frame_mo2, textvariable=mo2_install_path_var, width=50).pack(side=tk.LEFT)
    tk.Button(frame_mo2, text="Browse...", command=lambda: mo2_install_path_var.set(filedialog.askdirectory())).pack(side=tk.LEFT)

    endorse_btn = tk.Button(root, text="Start Endorsement", command=start_process, bg="green", fg="white")
    endorse_btn.pack(pady=10)
    show_tracked_btn = tk.Button(root, text="Show Tracked Mods", command=gui_show_tracked_mods)
    show_tracked_btn.pack(pady=2)

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

    def on_game_change(*args):
        if mods_folder_var.get():
            auto_track_mods(config, mods_folder_var.get(), selected_game.get())
    selected_game.trace_add("write", on_game_change)

    root.mainloop()

    # Gather latest values from GUI
    api_key = api_key_var.get().strip()
    game = selected_game.get()
    profiles_folder = profiles_folder_var.get().strip()
    mods_folder = mods_folder_var.get().strip()
    profile_selected = profile_options.get()
    tracked_mods = config.get("tracked_mods", {})
    mo2_install_path = mo2_install_path_var.get().strip()

    # Update config dictionary
    config["api_key"] = api_key
    config["last_game"] = game
    config["profiles_folder"] = profiles_folder
    config["mods_folder"] = mods_folder
    config["last_profile"] = profile_selected
    config["tracked_mods"] = tracked_mods
    config["mo2_install_path"] = mo2_install_path

    # Save config on exit
    save_config(
        api_key,
        game,
        profiles_folder,
        mods_folder,
        profile_selected,
        tracked_mods,
        mo2_install_path
    )

    auto_track_mods(config, mods_folder_var.get(), selected_game.get())

if __name__ == "__main__":
    start_gui()


