#!/usr/bin/env bash
# Aletheia Linux Uninstaller

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}=======================================${NC}"
echo -e "${RED}      Aletheia Linux Uninstaller       ${NC}"
echo -e "${RED}=======================================${NC}\n"

read -p "Are you sure you want to completely remove Aletheia? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstallation cancelled."
    exit 0
fi

APP_DIR="$HOME/.local/share/Aletheia"
BIN_DIR="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"

echo -e "\n${YELLOW}Removing files...${NC}"

# Remove App Directory
if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
    echo -e "${GREEN}Removed: $APP_DIR${NC}"
fi

# Remove Bin Symlink
if [ -L "$BIN_DIR/aletheia" ] || [ -f "$BIN_DIR/aletheia" ]; then
    rm "$BIN_DIR/aletheia"
    echo -e "${GREEN}Removed: $BIN_DIR/aletheia${NC}"
fi

# Remove Desktop Entry
if [ -f "$APPLICATIONS_DIR/aletheia.desktop" ]; then
    rm "$APPLICATIONS_DIR/aletheia.desktop"
    echo -e "${GREEN}Removed: $APPLICATIONS_DIR/aletheia.desktop${NC}"
fi

# Remove Icon
if [ -f "$ICON_DIR/aletheia.png" ]; then
    rm "$ICON_DIR/aletheia.png"
    echo -e "${GREEN}Removed: $ICON_DIR/aletheia.png${NC}"
fi

# Refresh desktop databases
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR"
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo -e "\n${GREEN}Uninstallation Complete!${NC}"
