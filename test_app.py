#!/usr/bin/env python3
"""
Simple test to verify the app can start
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing app startup...")

try:
    # Test imports
    print("Importing modules...")
    from PySide6.QtWidgets import QApplication
    print("✓ PySide6 imported successfully")
    
    import app
    print("✓ App module imported successfully")
    
    # Test app creation
    print("Creating QApplication...")
    qt_app = QApplication(sys.argv)
    print("✓ QApplication created successfully")
    
    print("Creating main window...")
    from main_window import OllamaDesktopApp
    window = OllamaDesktopApp()
    print("✓ Main window created successfully")
    
    print("Showing window...")
    window.show()
    print("✓ Window shown successfully")
    
    print("✓ All tests passed! App should be working.")
    print("App would start GUI now, but exiting for test purposes.")
    
except Exception as e:
    print(f"✗ Error during startup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
