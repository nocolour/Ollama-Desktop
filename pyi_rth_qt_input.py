"""
Runtime hook for Qt input methods support
Ensures proper initialization of input method plugins
"""

import os
import sys

def setup_qt_input_methods():
    """Setup Qt input method environment"""
    try:
        # Set Qt plugin path
        if hasattr(sys, '_MEIPASS'):
            # Running from PyInstaller bundle
            qt_plugin_path = os.path.join(sys._MEIPASS, 'PySide6', 'Qt', 'plugins')
            if os.path.exists(qt_plugin_path):
                os.environ['QT_PLUGIN_PATH'] = qt_plugin_path
                
        # Enable input method support
        os.environ['QT_IM_MODULE'] = 'ibus'  # or 'fcitx' depending on system
        
        # Ensure UTF-8 locale
        if 'LC_ALL' not in os.environ:
            os.environ['LC_ALL'] = 'en_US.UTF-8'
        if 'LANG' not in os.environ:
            os.environ['LANG'] = 'en_US.UTF-8'
            
    except Exception:
        # Ignore errors during setup
        pass

# Run setup
setup_qt_input_methods()
