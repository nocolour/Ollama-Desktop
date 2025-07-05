# Ollama Desktop - Release Package

A modern, feature-rich desktop application for chatting with local LLM models via Ollama.

## 📦 Package Contents

- `OllamaDesktop` - Main executable (71MB, standalone)
- `install.sh` - Automatic installation script
- `uninstall.sh` - Automatic uninstallation script
- `test_installation.sh` - Installation verification script
- `OllamaDesktop.desktop` - Desktop integration file
- `OllDesk_icon.png` - Application icon
- `README.md` - This documentation
- `CHINESE_INPUT_GUIDE.md` - Guide for Chinese input support
- `INSTALLATION_TROUBLESHOOTING.md` - Troubleshooting guide

## 🚀 Quick Installation

### Automatic Installation (Recommended)
```bash
# Make install script executable and run it
chmod +x install.sh
./install.sh
```

### Verify Installation
```bash
# Test that everything works correctly
./test_installation.sh
```

## ✨ Features

- **Local AI Chat**: Works with any Ollama model
- **Chinese Input Support**: Full international text input
- **Modern UI**: Dark/light themes with excellent readability
- **Real-time Streaming**: See responses as they're generated
- **Model Management**: Easy model downloads and switching
- **Default Model**: Set preferred models for quick access
- **Rich Text Display**: Markdown rendering for formatted content
- **Settings Persistence**: Remembers your preferences
- **Desktop Integration**: Appears in application menu with icon

## 📋 Requirements

- **Operating System**: Linux (64-bit)
- **Ollama Server**: Must be installed and running
- **Libraries**: Standard Linux libraries (automatically checked)

### Install Ollama Server
```bash
# Install Ollama if you haven't already
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Download a model
ollama pull llama3.2:1b
```

## 🔧 Usage

### Starting the Application
```bash
# After installation, run from anywhere:
~/.local/share/OllamaDesktop/OllamaDesktop

# Or find "Ollama Desktop" in your application menu
```

### Basic Usage
1. **Start Ollama**: Ensure `ollama serve` is running
2. **Open Application**: Launch Ollama Desktop
3. **Select Model**: Choose from available models
4. **Chat**: Type messages and get AI responses
5. **Configure**: Access settings for customization

## 🗑️ Uninstallation

```bash
# Automatic uninstallation
~/.local/share/OllamaDesktop/uninstall.sh

# Manual uninstallation (if needed)
rm -rf ~/.local/share/OllamaDesktop
rm -f ~/.local/share/applications/OllamaDesktop.desktop
```

## 🔍 Troubleshooting

### If Installation Fails
1. **Check Requirements**: Ensure you're on a 64-bit Linux system
2. **Run Diagnostics**: `./test_installation.sh`
3. **Check Permissions**: Make sure you can write to `~/.local/share/`
4. **See Troubleshooting Guide**: `INSTALLATION_TROUBLESHOOTING.md`

### If Application Won't Start
```bash
# Check for missing libraries
ldd ~/.local/share/OllamaDesktop/OllamaDesktop

# Install common dependencies (Ubuntu/Debian)
sudo apt update
sudo apt install libc6 libstdc++6 libgcc-s1 libglib2.0-0 libdbus-1-3

# Try running from terminal to see error messages
~/.local/share/OllamaDesktop/OllamaDesktop
```

### If Chinese Input Doesn't Work
See `CHINESE_INPUT_GUIDE.md` for detailed setup instructions.

## 🌟 What's New in This Release

- ✅ **Standalone Executable**: No Python installation required
- ✅ **Chinese Input Support**: Full international text input
- ✅ **Improved UI**: Better contrast and readability
- ✅ **Default Model Feature**: Set and remember preferred models
- ✅ **Automatic Installation**: Easy setup and removal scripts
- ✅ **Desktop Integration**: Proper Linux desktop environment support
- ✅ **Comprehensive Documentation**: Guides for all features

## 📁 File Locations After Installation

- **Executable**: `~/.local/share/OllamaDesktop/OllamaDesktop`
- **Icon**: `~/.local/share/OllamaDesktop/OllDesk_icon.png`
- **Uninstaller**: `~/.local/share/OllamaDesktop/uninstall.sh`
- **Desktop Entry**: `~/.local/share/applications/OllamaDesktop.desktop`
- **Settings**: `~/.config/OllamaDesktop/` (created when app runs)

## 🤝 Support

- **Installation Issues**: See `INSTALLATION_TROUBLESHOOTING.md`
- **Chinese Input**: See `CHINESE_INPUT_GUIDE.md`
- **General Usage**: See main `README.md`
- **Verification**: Run `./test_installation.sh`

## 📜 License

MIT License - Free to use, modify, and distribute.

---

**Enjoy chatting with your local AI models! 🤖**
