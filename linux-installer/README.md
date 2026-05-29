# Aletheia Desktop - Linux Installation

Welcome to Aletheia Desktop! This package contains everything you need to cleanly install Aletheia on your Linux system.

## Contents
- **Aletheia-1.0.0.AppImage**: The main executable.
- **appicon.png**: The application icon.
- **install.sh**: An automated script to install the app and add it to your application menu.
- **uninstall.sh**: An automated script to remove the app from your system.
- **README.md**: This document.

## How to Install

1. Open your terminal and navigate to the folder where you extracted this zip file.
2. Ensure the installer script is executable:
   ```bash
   chmod +x install.sh
   ```
3. Run the installer:
   ```bash
   ./install.sh
   ```
4. Follow the on-screen prompts. 

The installer will place the AppImage in `~/.local/share/Aletheia/`, copy the icon, and create a standard `.desktop` entry so Aletheia will show up in your desktop environment's application launcher. It also creates a convenient symlink so you can launch it by typing `aletheia` in your terminal!

## Requirements
AppImages typically require FUSE to run. Most Linux distributions have this pre-installed. If not, the installer will warn you.
- **Ubuntu/Debian**: `sudo apt install libfuse2`
- **Fedora**: `sudo dnf install fuse`
- **Arch**: `sudo pacman -S fuse2`

## How to Uninstall

If you ever wish to completely remove Aletheia, run the included uninstaller from this folder:

```bash
chmod +x uninstall.sh
./uninstall.sh
```

## Troubleshooting
- **Cannot run in terminal**: Ensure `~/.local/bin` is in your system's `PATH`.
- **Blurry text on Wayland**: If you are using Wayland, you can force Aletheia to run natively by launching it from the terminal with:
  ```bash
  aletheia --ozone-platform-hint=auto
  ```

Thank you for using Aletheia!
