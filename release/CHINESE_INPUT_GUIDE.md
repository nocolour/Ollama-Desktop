# Chinese Input Support for Ollama Desktop

The Ollama Desktop application now includes enhanced support for Chinese and other international text input methods.

## What's Included

- ✅ Qt input method plugins bundled in the executable
- ✅ Automatic detection of common input methods (ibus, fcitx, fcitx5)
- ✅ UTF-8 locale support
- ✅ Runtime configuration for optimal input method performance

## Setup Instructions

### For Ubuntu/Debian Systems:

1. **Install an Input Method Engine:**
   ```bash
   # Option 1: IBus (recommended)
   sudo apt install ibus ibus-pinyin ibus-libpinyin
   
   # Option 2: Fcitx5 (modern alternative)
   sudo apt install fcitx5 fcitx5-chinese-addons
   
   # Option 3: Fcitx (legacy)
   sudo apt install fcitx fcitx-pinyin
   ```

2. **Configure Input Method:**
   ```bash
   # For IBus:
   ibus-setup
   
   # For Fcitx5:
   fcitx5-configtool
   
   # For Fcitx:
   fcitx-configtool
   ```

3. **Set Environment Variables (if needed):**
   ```bash
   # Add to ~/.bashrc or ~/.profile
   export GTK_IM_MODULE=ibus
   export QT_IM_MODULE=ibus
   export XMODIFIERS=@im=ibus
   ```

4. **Start Input Method Service:**
   ```bash
   # IBus:
   ibus-daemon -drx
   
   # Fcitx5:
   fcitx5 -d
   
   # Fcitx:
   fcitx -d
   ```

### Usage:

1. **Start Ollama Desktop**
2. **Switch to Chinese Input:**
   - Press `Ctrl + Space` or configured hotkey
   - Look for input method indicator in system tray
3. **Type Chinese:**
   - Input will appear in the text field
   - Use number keys to select characters from candidates

## Troubleshooting

### If Chinese input doesn't work:

1. **Check Input Method Status:**
   ```bash
   echo $QT_IM_MODULE
   ps aux | grep -E "(ibus|fcitx)"
   ```

2. **Restart Input Method:**
   ```bash
   # Kill existing processes
   killall ibus-daemon fcitx fcitx5
   
   # Start again
   ibus-daemon -drx
   # or
   fcitx5 -d
   ```

3. **Manual Environment Setup:**
   ```bash
   # Run with explicit environment
   QT_IM_MODULE=ibus ./OllamaDesktop
   ```

4. **Check System Locale:**
   ```bash
   locale
   # Should show UTF-8 encoding
   ```

### For Other Linux Distributions:

- **Fedora/CentOS:** `dnf install ibus ibus-pinyin`
- **Arch Linux:** `pacman -S ibus ibus-pinyin`
- **openSUSE:** `zypper install ibus ibus-pinyin`

## Supported Input Methods

- ✅ **Pinyin** (Simplified Chinese)
- ✅ **Bopomofo** (Traditional Chinese)
- ✅ **Cangjie** (Traditional Chinese)
- ✅ **Japanese** (Hiragana, Katakana, Kanji)
- ✅ **Korean** (Hangul)
- ✅ **Other international layouts**

## Notes

- The application automatically detects and configures available input methods
- Qt plugins for input methods are bundled in the executable
- No additional Qt installation required
- Works with both Wayland and X11 desktop sessions

If you continue to experience issues, please check your system's input method configuration and ensure the input method service is running.
