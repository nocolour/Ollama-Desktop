#!/bin/bash
# Ollama Desktop Installation Script

echo "Installing Ollama Desktop..."

# Create application directory
APP_DIR="$HOME/.local/share/OllamaDesktop"
mkdir -p "$APP_DIR"

# Copy executable and icon
if [ -f "OllamaDesktop" ]; then
    # Running from release folder - executable is in current directory
    cp OllamaDesktop "$APP_DIR/"
    echo "Copied executable from release folder"
elif [ -f "dist/OllamaDesktop" ]; then
    # Running from project folder - executable is in dist/
    cp dist/OllamaDesktop "$APP_DIR/"
    echo "Copied executable from dist folder"
else
    echo "Error: OllamaDesktop executable not found!"
    echo "Please run this script from either:"
    echo "1. The release folder (containing OllamaDesktop)"
    echo "2. The project folder (containing dist/OllamaDesktop)"
    exit 1
fi

cp OllDesk_icon.png "$APP_DIR/"

# Copy uninstall script if available
if [ -f "uninstall.sh" ]; then
    cp uninstall.sh "$APP_DIR/"
    chmod +x "$APP_DIR/uninstall.sh"
else
    echo "Note: uninstall.sh not found in current directory"
fi

# Update desktop file with correct paths
if [ -f "OllamaDesktop.desktop" ]; then
    sed "s|/home/desmond/CodeProjects/PythonProjects/Ollama/dist/OllamaDesktop|$APP_DIR/OllamaDesktop|g" OllamaDesktop.desktop | \
    sed "s|/home/desmond/CodeProjects/PythonProjects/Ollama/OllDesk_icon.png|$APP_DIR/OllDesk_icon.png|g" > "$HOME/.local/share/applications/OllamaDesktop.desktop"
else
    echo "Warning: OllamaDesktop.desktop not found - creating basic desktop entry"
    cat > "$HOME/.local/share/applications/OllamaDesktop.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ollama Desktop
Comment=Chat with local LLM models using Ollama
Exec=$APP_DIR/OllamaDesktop
Icon=$APP_DIR/OllDesk_icon.png
Terminal=false
Categories=Office;Chat;Development;
StartupWMClass=OllamaDesktop
Keywords=AI;LLM;Chat;Ollama;Assistant;
EOF
fi

# Make files executable
chmod +x "$APP_DIR/OllamaDesktop"
chmod +x "$HOME/.local/share/applications/OllamaDesktop.desktop"

# Test if the executable can run
echo "Testing executable..."
echo "Checking file permissions..."
ls -la "$APP_DIR/OllamaDesktop"

echo "Checking dependencies..."
if ! ldd "$APP_DIR/OllamaDesktop" | grep -q "not found"; then
    echo "✓ All dependencies found"
else
    echo "⚠ Missing dependencies:"
    ldd "$APP_DIR/OllamaDesktop" | grep "not found"
fi

echo "Testing executable execution..."
if timeout 3 "$APP_DIR/OllamaDesktop" --version >/dev/null 2>&1; then
    echo "✓ Executable test passed"
elif timeout 3 "$APP_DIR/OllamaDesktop" --help >/dev/null 2>&1; then
    echo "✓ Executable responds to commands"
else
    echo "⚠ Executable test failed - but this might be normal for GUI apps"
    echo "The application may still work when launched normally"
    echo ""
    echo "If you encounter issues, try:"
    echo "1. Check dependencies: ldd $APP_DIR/OllamaDesktop"
    echo "2. Run with debug: $APP_DIR/OllamaDesktop --debug"
    echo "3. Check if Ollama service is running: ollama --version"
fi

echo "Installation completed!"
echo "Executable location: $APP_DIR/OllamaDesktop"
echo "Desktop file: $HOME/.local/share/applications/OllamaDesktop.desktop"
echo ""
echo "You can now:"
echo "1. Run the app directly: $APP_DIR/OllamaDesktop"
echo "2. Find it in your application menu as 'Ollama Desktop'"
echo "3. Copy the executable to anywhere you like"
echo ""
echo "To uninstall later:"
echo "- Run: $APP_DIR/uninstall.sh"
echo "- Or manually delete: $APP_DIR and $HOME/.local/share/applications/OllamaDesktop.desktop"
