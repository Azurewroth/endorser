# Batch Endorser for MO2

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)  
[![Issues](https://img.shields.io/github/issues/Azurewroth/endorser)](https://github.com/Azurewroth/endorser/issues)  
[![Pull Requests](https://img.shields.io/github/issues-pr/Azurewroth/endorser)](https://github.com/Azurewroth/endorser/pulls)  
[![Wiki](https://img.shields.io/badge/docs-wiki-blue.svg)](https://github.com/Azurewroth/endorser/wiki)  
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/Azurewroth/endorser/blob/main/CONTRIBUTING.md)

---

Batch Endorser is a Python utility designed to help you quickly endorse all your installed mods on Nexus Mods for games managed via Mod Organizer 2 (MO2).  
It features a simple graphical interface and supports multiple games, including Skyrim SE, Fallout 4, and more.

---

## Features

- Endorse all mods in a selected MO2 mods folder with a single click  
- Supports multiple games: Skyrim SE, Fallout 4, Skyrim LE, Fallout NV, Witcher 3  
- Real-time progress bar and status updates  
- Open source and licensed under GPL v3

---

## Requirements

- Python 3.8 or newer  
- [requests](https://pypi.org/project/requests/) Python package  
- [tkinter](https://docs.python.org/3/library/tkinter.html) (usually included with Python)  
- A valid [Nexus Mods API key](https://www.nexusmods.com/users/myaccount?tab=api%20access)

---

## Installation

1. **Clone or download this repository:**  
    ```bash
    git clone https://github.com/Azurewroth/endorser.git
    cd endorser
    ```

2. **Install dependencies:**  
    ```bash
    pip install requests cryptography
    ```

---

## Usage

1. **Obtain your Nexus Mods API key:**  
   [Get your API key here](https://www.nexusmods.com/users/myaccount?tab=api%20access)

2. **Run the script:**  
    ```bash
    python endorser.py
    ```

3. **Using the GUI:**  
    - Paste your Nexus API key.  
    - Select your game.  
    - Browse to your MO2 profiles folder and select a profile.  
    - Browse to your MO2 mods folder.  
    - Click **Start Endorsement**.  
    - Monitor the progress bar and status updates as your mods are endorsed.

---

## Tracked Mods & Update Checking

- **Automatic tracking:**  
  All mods within your selected MO2 mods folder are tracked automatically — no manual input required.

- **Show tracked mods:**  
  Click the **"Show Tracked Mods"** button to display all tracked mods for the selected game.

- **Update detection:**  
  The tool checks Nexus Mods for newer versions of each tracked mod.  
  - Mods with updates available will display `[Update Available]`.  
  - Mods with changed local `meta.ini` files will show `(Changed)`.

- **Performance note:**  
  For large mod collections, update checking may take some time. The **Show Tracked Mods** button disables during this process to avoid duplicate requests.

---

## Tips & Notes

- Only mods with a valid `meta.ini` and associated Nexus `modid` will be endorsed.  
- Your Nexus API key and settings are encrypted locally in `config.json` using a key stored in `config.key`.  
- Keep `config.key` safe — if lost, your encrypted settings cannot be recovered.

---

## License

This project is licensed under the [GNU GPL v3](LICENSE).

---

*Created by Harry Joseph King, 2025.*

