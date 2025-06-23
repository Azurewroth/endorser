# Batch Endorser for MO2

Batch Endorser is a Python utility that helps you quickly endorse all your installed mods on Nexus Mods for games managed by Mod Organizer 2 (MO2).  
It features a simple graphical interface and supports Skyrim SE, Fallout 4, and more.

## Features

- Endorse all mods in a selected MO2 mods folder with one click
- Supports multiple games (Skyrim SE, Fallout 4, Skyrim LE, Fallout NV, Witcher 3)
- Progress bar and status updates
- Open source (GPL v3)

## Requirements

- Python 3.8 or newer
- [requests](https://pypi.org/project/requests/)
- [tkinter](https://docs.python.org/3/library/tkinter.html) (usually included with Python)
- [Nexus Mods API key](https://www.nexusmods.com/users/myaccount?tab=api%20access)

## Installation

1. **Clone or download this repository:**
    ```sh
    git clone https://github.com/Azurewroth/endorser.git
    cd endorser
    ```

2. **Install dependencies:**
    ```sh
    pip install requests cryptography
    ```

## Usage

1. **Get your Nexus Mods API key:**  
   [Get your API key here](https://www.nexusmods.com/users/myaccount?tab=api%20access)

2. **Run the script:**
    ```sh
    python endorser.py
    ```

3. **In the GUI:**
    - Paste your Nexus API key.
    - Select your game.
    - Browse to your MO2 profiles folder and select a profile.
    - Browse to your MO2 mods folder.
    - Click **Start Endorsement**.
    - Watch the progress bar and status updates as your mods are endorsed!

## Tracked Mods & Update Checking

- **Automatic Tracking:**  
  All mods in your selected MO2 mods folder are automatically tracked by the program—no manual entry needed.

- **Show Tracked Mods:**  
  Click the **"Show Tracked Mods"** button to view a list of all tracked mods for the selected game.

- **Update Detection:**  
  The program checks Nexus Mods for each tracked mod.  
  - If a mod has a newer version available on Nexus Mods, it will display `[Update Available]` next to that mod.
  - If the local mod’s `meta.ini` has changed since the last scan, it will display `(Changed)`.

- **Performance:**  
  For large mod lists, update checking may take some time. The button will be disabled while checking to prevent duplicate requests.

---

**Tip:**  
Make sure your Nexus Mods API key is set and your MO2 mods folder path is correct in the config or GUI for best results.

## Notes

- Only mods with a valid `meta.ini` and `modid` will be endorsed.
- Your Nexus API key and settings are encrypted in `config.json` using a key stored in `config.key`.
- Keep `config.key` safe! If you lose it, you cannot recover your settings.

## License

This project is licensed under the [GNU GPL v3](LICENSE).

---

*Created by Harry Joseph King, 2025.*