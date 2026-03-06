# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for EasyHost MC
# Usage: pyinstaller easyhost.spec

import os
import sys
import customtkinter

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))
ctk_path  = os.path.dirname(customtkinter.__file__)

# ---------------------------------------------------------------------------
# Données à embarquer
# ---------------------------------------------------------------------------
datas = [
    (ctk_path, "customtkinter"),
]

# ---------------------------------------------------------------------------
# Hidden imports (modules que PyInstaller ne détecte pas automatiquement)
# ---------------------------------------------------------------------------
hiddenimports = [
    "customtkinter",
    "PIL",
    "PIL._tkinter_finder",
    "psutil",
    "requests",
]

# ---------------------------------------------------------------------------
# Icône (optionnelle — ignorée si le fichier n'existe pas)
# ---------------------------------------------------------------------------
icon_win = os.path.join(BASE_DIR, "assets", "icon.ico")
icon_mac = os.path.join(BASE_DIR, "assets", "icon.icns")
icon_arg = None
if sys.platform == "win32" and os.path.exists(icon_win):
    icon_arg = icon_win
elif sys.platform == "darwin" and os.path.exists(icon_mac):
    icon_arg = icon_mac

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    [os.path.join(BASE_DIR, "main.py")],
    pathex=[BASE_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

# ---------------------------------------------------------------------------
# EXE / bundle
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="EasyHost",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_arg,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="EasyHost",
)

# ---------------------------------------------------------------------------
# macOS App Bundle uniquement
# ---------------------------------------------------------------------------
if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="EasyHost.app",
        icon=icon_arg,
        bundle_identifier="com.easyhost.mc",
        info_plist={
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleName": "EasyHost MC",
            "NSHighResolutionCapable": True,
        },
    )
