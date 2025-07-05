#!/bin/bash
# Test script for Ollama Desktop installation

echo "Testing Ollama Desktop Installation..."
echo "======================================"

# Check if executable exists
EXECUTABLE="$HOME/.local/share/OllamaDesktop/OllamaDesktop"
if [ -f "$EXECUTABLE" ]; then
    echo "✓ Executable found: $EXECUTABLE"
    
    # Check permissions
    if [ -x "$EXECUTABLE" ]; then
        echo "✓ Executable has correct permissions"
    else
        echo "✗ Executable is not executable"
        echo "  Fix with: chmod +x $EXECUTABLE"
    fi
    
    # Check file type
    FILE_TYPE=$(file "$EXECUTABLE")
    echo "✓ File type: $FILE_TYPE"
    
    # Check dependencies
    echo ""
    echo "Checking dependencies..."
    if command -v ldd >/dev/null 2>&1; then
        MISSING_LIBS=$(ldd "$EXECUTABLE" 2>/dev/null | grep "not found" || true)
        if [ -z "$MISSING_LIBS" ]; then
            echo "✓ All required libraries found"
        else
            echo "✗ Missing libraries:"
            echo "$MISSING_LIBS"
            echo ""
            echo "Try installing missing packages:"
            echo "sudo apt update"
            echo "sudo apt install libc6 libstdc++6 libgcc-s1 libglib2.0-0 libdbus-1-3"
        fi
    else
        echo "! ldd not available - cannot check dependencies"
    fi
    
    # Test basic execution
    echo ""
    echo "Testing basic execution..."
    if timeout 5s "$EXECUTABLE" --help >/dev/null 2>&1; then
        echo "✓ Executable runs successfully"
    elif timeout 5s "$EXECUTABLE" >/dev/null 2>&1; then
        echo "✓ Executable starts (may need GUI)"
    else
        echo "✗ Executable failed to run"
        echo "  Try running manually: $EXECUTABLE"
    fi
    
else
    echo "✗ Executable not found: $EXECUTABLE"
    echo "  Run the install script first: ./install.sh"
fi

# Check desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/OllamaDesktop.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    echo "✓ Desktop entry found: $DESKTOP_FILE"
else
    echo "✗ Desktop entry not found: $DESKTOP_FILE"
fi

# Check icon
ICON_FILE="$HOME/.local/share/OllamaDesktop/OllDesk_icon.png"
if [ -f "$ICON_FILE" ]; then
    echo "✓ Icon found: $ICON_FILE"
else
    echo "✗ Icon not found: $ICON_FILE"
fi

echo ""
echo "Test completed!"
echo ""
echo "If all tests pass, you can:"
echo "1. Run: $EXECUTABLE"
echo "2. Find 'Ollama Desktop' in your application menu"
echo "3. Create a desktop shortcut from the applications menu"
