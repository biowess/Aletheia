#!/usr/bin/env bash
# Aletheia Linux Installer
# Automatically detects the AppImage and installs it to the user's home directory.

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}      Aletheia Linux Installer         ${NC}"
echo -e "${BLUE}=======================================${NC}\n"

# 1. Dependency checks
echo -e "${YELLOW}[1/6] Checking system dependencies...${NC}"

# Check for FUSE (required for AppImages)
if ! command -v fusermount >/dev/null 2>&1 && ! command -v fusermount3 >/dev/null 2>&1; then
    echo -e "${RED}Warning: FUSE does not appear to be installed.${NC}"
    echo -e "AppImages typically require FUSE/libfuse2 to run on Linux."
    echo -e "On Ubuntu/Debian: sudo apt install libfuse2"
    echo -e "On Fedora: sudo dnf install fuse"
    echo -e "On Arch: sudo pacman -S fuse2\n"
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}FUSE is installed.${NC}"
fi

# 2. Locate AppImage
echo -e "\n${YELLOW}[2/6] Locating Aletheia AppImage...${NC}"
# Look in current dir and dist/ directory
APPIMAGE_PATH=$(find . dist -maxdepth 2 -name "Aletheia-*.AppImage" -print -quit 2>/dev/null)

if [ -z "$APPIMAGE_PATH" ]; then
    echo -e "${RED}Error: Could not find Aletheia-*.AppImage.${NC}"
    echo -e "Please run this script from the project root or ensure the AppImage has been built."
    exit 1
fi

APPIMAGE_FILE=$(basename "$APPIMAGE_PATH")
echo -e "${GREEN}Found: $APPIMAGE_PATH${NC}"

# 3. Setup directories
echo -e "\n${YELLOW}[3/6] Setting up directories...${NC}"
APP_DIR="$HOME/.local/share/Aletheia"
BIN_DIR="$HOME/.local/bin"
APPLICATIONS_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"

mkdir -p "$APP_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$APPLICATIONS_DIR"
mkdir -p "$ICON_DIR"

echo -e "${GREEN}Directories ready.${NC}"

# 4. Install AppImage
echo -e "\n${YELLOW}[4/6] Installing AppImage...${NC}"
# Copying AppImage to application directory
cp "$APPIMAGE_PATH" "$APP_DIR/Aletheia.AppImage"
chmod +x "$APP_DIR/Aletheia.AppImage"

# Create symlink in ~/.local/bin
ln -sf "$APP_DIR/Aletheia.AppImage" "$BIN_DIR/aletheia"

echo -e "${GREEN}Installed to $APP_DIR/Aletheia.AppImage${NC}"
echo -e "${GREEN}Symlink created at $BIN_DIR/aletheia${NC}"

# 5. Install Icon
echo -e "\n${YELLOW}[5/6] Installing icon...${NC}"
ICON_SRC="appicon.png"
if [ ! -f "$ICON_SRC" ]; then
    # Try looking in electron/assets if not in root
    ICON_SRC=$(find . -maxdepth 3 -name "appicon.png" -print -quit 2>/dev/null)
fi

if [ -n "$ICON_SRC" ] && [ -f "$ICON_SRC" ]; then
    cp "$ICON_SRC" "$ICON_DIR/aletheia.png"
    echo -e "${GREEN}Icon installed to $ICON_DIR/aletheia.png${NC}"
else
    echo -e "${RED}Warning: appicon.png not found. Using fallback icon behavior.${NC}"
fi

# 6. Create Desktop Entry
echo -e "\n${YELLOW}[6/6] Creating Desktop entry...${NC}"

cat > "$APPLICATIONS_DIR/aletheia.desktop" << EOF
[Desktop Entry]
Name=Aletheia
Comment=Aletheia Clinical Workstation
Exec=$APP_DIR/Aletheia.AppImage %U
Icon=aletheia
Terminal=false
Type=Application
Categories=Science;MedicalSoftware;Education;
StartupWMClass=aletheia-desktop
EOF

# Make it executable (optional but good practice)
chmod +x "$APPLICATIONS_DIR/aletheia.desktop"

# Refresh desktop databases if tools are available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR"
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo -e "${GREEN}Desktop entry created.${NC}"

echo -e "\n${BLUE}=======================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "You can now launch Aletheia from your application menu,"
echo -e "or by typing '${YELLOW}aletheia${NC}' in your terminal."
echo -e "Note: If your terminal doesn't recognize the command, ensure ${YELLOW}$BIN_DIR${NC} is in your PATH."
echo -e "${BLUE}=======================================${NC}\n"
