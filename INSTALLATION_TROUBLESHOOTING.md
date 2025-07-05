# Installation Troubleshooting Guide

## Common Installation Issues and Solutions

### 1. "File or folder not found" Error

**Problem**: The install script can't find the executable file.

**Solutions**:
```bash
# Check what files are in your current directory
ls -la

# Make sure you're running install.sh from the correct location:
# Option 1: From release folder (contains OllamaDesktop directly)
cd /path/to/release/folder
./install.sh

# Option 2: From project folder (contains dist/OllamaDesktop)
cd /path/to/project/folder
./install.sh
```

### 2. "Permission denied" Error

**Problem**: Install script or executable doesn't have execute permissions.

**Solutions**:
```bash
# Make install script executable
chmod +x install.sh

# Make executable file executable (if manually copying)
chmod +x OllamaDesktop
chmod +x ~/.local/share/OllamaDesktop/OllamaDesktop
```

### 3. Executable Won't Run After Installation

**Problem**: Application starts but immediately crashes or shows errors.

**Diagnostic Steps**:
```bash
# Test the installation
./test_installation.sh

# Check for missing libraries
ldd ~/.local/share/OllamaDesktop/OllamaDesktop

# Try running manually to see error messages
~/.local/share/OllamaDesktop/OllamaDesktop
```

**Solutions**:
```bash
# Install common missing dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install libc6 libstdc++6 libgcc-s1 libglib2.0-0 libdbus-1-3 libxcb1 libx11-6

# For Qt/GUI issues
sudo apt install libqt6core6 libqt6gui6 libqt6widgets6 qt6-qpa-plugins

# For audio/multimedia (if needed)
sudo apt install libpulse0 libasound2
```

### 4. Application Not Appearing in Menu

**Problem**: Desktop entry not working or not visible in application menu.

**Solutions**:
```bash
# Update desktop database
update-desktop-database ~/.local/share/applications

# Check desktop file
cat ~/.local/share/applications/OllamaDesktop.desktop

# Manually refresh (logout/login or restart desktop environment)
# Or try:
killall nautilus  # For GNOME
# or
kbuildsycoca5     # For KDE
```

### 5. Icon Not Displaying

**Problem**: Application runs but icon is missing.

**Solutions**:
```bash
# Check if icon file exists
ls -la ~/.local/share/OllamaDesktop/OllDesk_icon.png

# Copy icon manually if missing
cp OllDesk_icon.png ~/.local/share/OllamaDesktop/

# Update icon cache
gtk-update-icon-cache ~/.local/share/icons/ 2>/dev/null || true
```

### 6. "No such file or directory" for Working Executable

**Problem**: File exists but system says it doesn't (usually architecture mismatch).

**Diagnostic**:
```bash
# Check file architecture
file ~/.local/share/OllamaDesktop/OllamaDesktop

# Check system architecture
uname -m

# Check if it's a 32-bit vs 64-bit issue
readelf -h ~/.local/share/OllamaDesktop/OllamaDesktop | grep Machine
```

**Solutions**:
```bash
# For 64-bit executable on 64-bit system needing 32-bit libraries
sudo apt install lib32z1 lib32ncurses6

# Ensure you have the right architecture build
# The executable should show: ELF 64-bit LSB executable, x86-64
```

### 7. Installation Script Fails

**Problem**: Install script encounters errors during execution.

**Solutions**:
```bash
# Run with debug output
bash -x install.sh

# Check permissions on target directories
ls -la ~/.local/share/
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/OllamaDesktop

# Run with verbose output
./install.sh 2>&1 | tee install.log
```

### 8. Cannot Create Directory

**Problem**: Permission issues creating installation directories.

**Solutions**:
```bash
# Fix home directory permissions
chmod 755 ~
chmod 755 ~/.local
chmod 755 ~/.local/share

# Create directories manually
mkdir -p ~/.local/share/OllamaDesktop
mkdir -p ~/.local/share/applications

# Check disk space
df -h ~
```

## Quick Diagnostic Commands

```bash
# Complete system check
./test_installation.sh

# Manual verification
ls -la ~/.local/share/OllamaDesktop/
ls -la ~/.local/share/applications/OllamaDesktop.desktop
file ~/.local/share/OllamaDesktop/OllamaDesktop
ldd ~/.local/share/OllamaDesktop/OllamaDesktop | head -5

# Test execution
timeout 10s ~/.local/share/OllamaDesktop/OllamaDesktop --version 2>&1 || echo "Test failed"
```

## Getting Help

If you continue to have issues:

1. **Run the diagnostic**: `./test_installation.sh`
2. **Check system compatibility**: Ensure you're on a supported Linux distribution
3. **Verify dependencies**: Use `ldd` to check for missing libraries
4. **Manual installation**: Try copying files manually instead of using the script
5. **Check logs**: Look for error messages in terminal output

## Manual Installation (Fallback)

If the automatic installation fails completely:

```bash
# Create directories
mkdir -p ~/.local/share/OllamaDesktop
mkdir -p ~/.local/share/applications

# Copy files manually
cp OllamaDesktop ~/.local/share/OllamaDesktop/
cp OllDesk_icon.png ~/.local/share/OllamaDesktop/
cp uninstall.sh ~/.local/share/OllamaDesktop/

# Set permissions
chmod +x ~/.local/share/OllamaDesktop/OllamaDesktop
chmod +x ~/.local/share/OllamaDesktop/uninstall.sh

# Create desktop entry manually
cat > ~/.local/share/applications/OllamaDesktop.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ollama Desktop
Comment=Chat with local LLM models using Ollama
Exec=$HOME/.local/share/OllamaDesktop/OllamaDesktop
Icon=$HOME/.local/share/OllamaDesktop/OllDesk_icon.png
Terminal=false
Categories=Office;Chat;Development;
StartupWMClass=OllamaDesktop
Keywords=AI;LLM;Chat;Ollama;Assistant;
EOF

chmod +x ~/.local/share/applications/OllamaDesktop.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications
```
