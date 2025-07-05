#!/usr/bin/env python3
"""
Ollama Desktop - A Modern Chat Interface
A comprehensive desktop application for interacting with Ollama models
Built with PySide6 for a native, responsive experience

This is the main entry point that coordinates all the modular components.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon

from main_window import OllamaDesktopApp


def setup_input_methods():
    """Setup input method support for international text input"""
    # Set environment variables for better input method support
    if 'QT_IM_MODULE' not in os.environ:
        # Try common input methods
        if os.system('which ibus-daemon > /dev/null 2>&1') == 0:
            os.environ['QT_IM_MODULE'] = 'ibus'
        elif os.system('which fcitx > /dev/null 2>&1') == 0:
            os.environ['QT_IM_MODULE'] = 'fcitx'
        elif os.system('which fcitx5 > /dev/null 2>&1') == 0:
            os.environ['QT_IM_MODULE'] = 'fcitx5'
    
    # Ensure UTF-8 locale support
    if 'LC_CTYPE' not in os.environ:
        os.environ['LC_CTYPE'] = 'en_US.UTF-8'


def setup_application():
    """Setup the QApplication with proper configuration"""
    # Setup input methods before creating QApplication
    setup_input_methods()
    
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Ollama Desktop")
    app.setApplicationDisplayName("Ollama Desktop Chat")
    app.setOrganizationName("Ollama Desktop")
    app.setOrganizationDomain("ollama-desktop.local")
    app.setApplicationVersion("2.0.0")

    # Quit when the last window is closed
    app.setQuitOnLastWindowClosed(True)

    # Set application icon (if available)
    try:
        app.setWindowIcon(QIcon("icon.png"))  # Add your icon file here
    except:
        pass  # Icon not available, continue without it

    return app


def main():
    """Main entry point for the application"""
    try:
        # Create application
        app = setup_application()

        # Create and show main window
        window = OllamaDesktopApp()
        window.show()

        # Start event loop
        return app.exec()

    except Exception as e:
        print(f"Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
