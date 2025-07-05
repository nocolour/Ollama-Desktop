#!/bin/bash
# Ollama Desktop Uninstallation Script

echo "Uninstalling Ollama Desktop..."

# Define application directory
APP_DIR="$HOME/.local/share/OllamaDesktop"
DESKTOP_FILE="$HOME/.local/share/applications/OllamaDesktop.desktop"

# Stop any running instances
echo "Stopping any running instances..."
pkill -f "OllamaDesktop" 2>/dev/null || true

# Remove application directory
if [ -d "$APP_DIR" ]; then
    echo "Removing application files from: $APP_DIR"
    rm -rf "$APP_DIR"
    echo "✓ Application files removed"
else
    echo "! Application directory not found: $APP_DIR"
fi

# Remove desktop file
if [ -f "$DESKTOP_FILE" ]; then
    echo "Removing desktop entry: $DESKTOP_FILE"
    rm -f "$DESKTOP_FILE"
    echo "✓ Desktop entry removed"
else
    echo "! Desktop file not found: $DESKTOP_FILE"
fi

# Update desktop database to refresh application menu
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

# Remove application settings (optional)
read -p "Do you want to remove application settings and data? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Remove Qt settings
    SETTINGS_DIR="$HOME/.config/OllamaDesktop"
    if [ -d "$SETTINGS_DIR" ]; then
        echo "Removing application settings: $SETTINGS_DIR"
        rm -rf "$SETTINGS_DIR"
        echo "✓ Application settings removed"
    fi
    
    # Remove QSettings files
    QT_SETTINGS="$HOME/.config/OllamaDesktop.conf"
    if [ -f "$QT_SETTINGS" ]; then
        echo "Removing Qt settings: $QT_SETTINGS"
        rm -f "$QT_SETTINGS"
        echo "✓ Qt settings removed"
    fi
    
    echo "✓ All application data removed"
else
    echo "Application settings preserved"
fi

echo ""
echo "Uninstallation completed!"
echo ""
echo "What was removed:"
echo "- Application files: $APP_DIR"
echo "- Desktop entry: $DESKTOP_FILE"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "- Application settings and data"
fi
echo ""
echo "Ollama Desktop has been successfully uninstalled."
