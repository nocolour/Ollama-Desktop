# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs
import os

# Collect Qt input method plugins and platform plugins
qt_binaries = []
qt_datas = []

# Try to find Qt plugins directory
try:
    import PySide6
    qt_plugins_dir = os.path.join(os.path.dirname(PySide6.__file__), 'Qt', 'plugins')
    
    # Add input method plugins for Chinese and other international input
    if os.path.exists(os.path.join(qt_plugins_dir, 'platforminputcontexts')):
        for file in os.listdir(os.path.join(qt_plugins_dir, 'platforminputcontexts')):
            if file.endswith('.so'):
                qt_binaries.append((
                    os.path.join(qt_plugins_dir, 'platforminputcontexts', file),
                    'PySide6/Qt/plugins/platforminputcontexts'
                ))
    
    # Add platform plugins
    if os.path.exists(os.path.join(qt_plugins_dir, 'platforms')):
        for file in os.listdir(os.path.join(qt_plugins_dir, 'platforms')):
            if file.endswith('.so'):
                qt_binaries.append((
                    os.path.join(qt_plugins_dir, 'platforms', file),
                    'PySide6/Qt/plugins/platforms'
                ))
                
    # Add imageformats plugins
    if os.path.exists(os.path.join(qt_plugins_dir, 'imageformats')):
        for file in os.listdir(os.path.join(qt_plugins_dir, 'imageformats')):
            if file.endswith('.so'):
                qt_binaries.append((
                    os.path.join(qt_plugins_dir, 'imageformats', file),
                    'PySide6/Qt/plugins/imageformats'
                ))
except ImportError:
    pass

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=qt_binaries,
    datas=qt_datas,
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_qt_input.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OllamaDesktop-debug',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['OllDesk_icon.png'],
)
