# Changelog

## [1.2.0] - 2025-06-22
### Added
- Encrypted config.json using Fernet symmetric encryption; config.key is now required to decrypt settings
- Tracked mods system: automatically tracks all mods in the selected MO2 mods folder
- "Show Tracked Mods" button displays tracked mods and checks for updates on Nexus Mods
- Marks mods as `[Update Available]` if a newer version is found on Nexus Mods
- Marks mods as `(Changed)` if the local meta.ini has changed since last scan
- Both "Start Endorsement" and "Show Tracked Mods" buttons are disabled while processing
- Output for tracked mods now appears in a scrollable text box instead of a popup

### Changed
- Improved config saving/loading to ensure settings persist between runs
- Enhanced error handling for missing or corrupted config/key files

### Fixed
- Fixed issues with config/key file recognition and persistence
- Fixed UI freezing during long update checks

---

## [1.1.0] - 2025-06-19
### Added
- Remembers API key, game, and folder paths in a local config.json file
- Hides API key entry after first successful save (unless config is missing)
- Added a checkbox to show/hide the output text box
- Improved output box padding for better appearance

## [1.0.0] - 2025-06-19
### Added
- Initial release of Batch Endorser for MO2
- Simple graphical interface (Tkinter)
- Supports Skyrim SE, Fallout 4, Skyrim LE, Fallout NV, Witcher 3
- Batch endorsement of all mods in a selected MO2 mods folder
- Progress bar and status updates
- Error handling for missing or invalid `meta.ini` files