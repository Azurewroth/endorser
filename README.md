swUtLapvFPt+cllGNuDKL7g30fIxDk9GJoIDU54Ze3OYE8yz--XPH72h/oOZ/hq4iX--+ovy4303ODI/ITUYkiq5Xw==
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
    pip install requests
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

## Notes

- Only mods with a valid `meta.ini` and `modid` will be endorsed.
- Your Nexus API key is never saved.
- This tool does not upload or modify your mods, only sends endorsements.

## License

This project is licensed under the [GNU GPL v3](LICENSE).

---

*Created by Harry Joseph King, 2025.*