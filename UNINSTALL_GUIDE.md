# Uninstalling Ollama Desktop

There are several ways to uninstall Ollama Desktop depending on how it was installed.

## Method 1: Automatic Uninstallation (Recommended)

If you installed using the `install.sh` script:

```bash
# Run the uninstall script
~/.local/share/OllamaDesktop/uninstall.sh
```

Or if you have the uninstall script in your current directory:
```bash
./uninstall.sh
```

This will:
- ✅ Stop any running instances
- ✅ Remove application files
- ✅ Remove desktop entry
- ✅ Update application menu
- ✅ Optionally remove settings and data

## Method 2: Manual Uninstallation

If you don't have the uninstall script or prefer manual removal:

### 1. Stop Running Application
```bash
pkill -f "OllamaDesktop"
```

### 2. Remove Application Files
```bash
# Remove main application directory
rm -rf ~/.local/share/OllamaDesktop

# Remove desktop entry
rm -f ~/.local/share/applications/OllamaDesktop.desktop
```

### 3. Remove Settings (Optional)
```bash
# Remove application settings
rm -rf ~/.config/OllamaDesktop
rm -f ~/.config/OllamaDesktop.conf
```

### 4. Update Desktop Database
```bash
update-desktop-database ~/.local/share/applications
```

## Method 3: Portable Installation Cleanup

If you copied the executable to a custom location:

### 1. Stop the Application
```bash
pkill -f "OllamaDesktop"
```

### 2. Remove Files
```bash
# Delete the executable from wherever you put it
rm /path/to/your/OllamaDesktop

# If you created a desktop entry manually
rm -f ~/.local/share/applications/OllamaDesktop.desktop
```

### 3. Clean Settings (Optional)
```bash
rm -rf ~/.config/OllamaDesktop
rm -f ~/.config/OllamaDesktop.conf
```

## What Gets Removed

### Application Files:
- `~/.local/share/OllamaDesktop/` - Main application directory
  - `OllamaDesktop` - The executable
  - `OllDesk_icon.png` - Application icon
  - `uninstall.sh` - Uninstall script

### Desktop Integration:
- `~/.local/share/applications/OllamaDesktop.desktop` - Desktop entry file

### Settings and Data (Optional):
- `~/.config/OllamaDesktop/` - Application configuration directory
- `~/.config/OllamaDesktop.conf` - Qt settings file
- Chat history and user preferences

## Verification

After uninstallation, verify removal by:

```bash
# Check if application files are gone
ls ~/.local/share/OllamaDesktop

# Check if desktop entry is removed
ls ~/.local/share/applications/OllamaDesktop.desktop

# Check if still appears in application menu
# (May need to log out/in or restart desktop environment)
```

## Troubleshooting

### Application Won't Stop
```bash
# Force kill if needed
pkill -9 -f "OllamaDesktop"
```

### Permission Issues
```bash
# If you get permission errors, check ownership
ls -la ~/.local/share/OllamaDesktop
ls -la ~/.local/share/applications/OllamaDesktop.desktop

# Fix ownership if needed
chown -R $USER:$USER ~/.local/share/OllamaDesktop
```

### Desktop Entry Still Shows
- Log out and log back in
- Or restart your desktop environment
- Or run: `update-desktop-database ~/.local/share/applications`

## Reinstallation

To reinstall after uninstalling:
1. Run the `install.sh` script again
2. Or copy the executable to your desired location

The uninstallation process is completely reversible and won't affect other applications.
