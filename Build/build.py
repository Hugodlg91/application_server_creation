#!/usr/bin/env python3
"""
build.py — Script de packaging EasyHost MC avec PyInstaller.
Usage : python build.py
"""

import os
import sys
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIDDEN_IMPORTS = [
    "customtkinter",
    "PIL",
    "PIL._tkinter_finder",
    "psutil",
    "requests",
]


def run(cmd, **kwargs):
    print(f"\n>>> {' '.join(str(c) for c in cmd)}\n")
    return subprocess.run(cmd, **kwargs)


def ensure_package(package):
    """Installe le package via pip s'il n'est pas importable."""
    try:
        __import__(package)
    except ImportError:
        print(f"[build] '{package}' non trouvé — installation…")
        run([sys.executable, "-m", "pip", "install", package], check=True)


def main():
    # ── Prérequis ───────────────────────────────────────────────────────────
    print("[build] Vérification des dépendances…")
    ensure_package("PyInstaller")
    ensure_package("customtkinter")

    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)

    # ── Détection OS ────────────────────────────────────────────────────────
    platform = sys.platform
    sep = ";" if platform == "win32" else ":"

    if platform == "win32":
        target_desc = "dist/EasyHost/EasyHost.exe"
    elif platform == "darwin":
        target_desc = "dist/EasyHost.app"
    else:
        target_desc = "dist/EasyHost/EasyHost"

    print(f"\n[build] Plateforme : {platform}")
    print(f"[build] Résultat attendu : {target_desc}")

    # ── Commande PyInstaller ─────────────────────────────────────────────────
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--windowed",
        "--onedir",
        "--name", "EasyHost",
        "--add-data", f"{ctk_path}{sep}customtkinter",
    ]

    for imp in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", imp]

    # Icône (optionnelle)
    icon_win = os.path.join(BASE_DIR, "assets", "icon.ico")
    icon_mac = os.path.join(BASE_DIR, "assets", "icon.icns")
    if platform == "win32" and os.path.exists(icon_win):
        cmd += ["--icon", icon_win]
    elif platform == "darwin" and os.path.exists(icon_mac):
        cmd += ["--icon", icon_mac]

    cmd.append(os.path.join(BASE_DIR, "../EasyHost/main.py"))

    # ── Build ────────────────────────────────────────────────────────────────
    print("\n[build] Lancement du build…")
    result = run(cmd, cwd=BASE_DIR)

    # ── Résultat ─────────────────────────────────────────────────────────────
    if result.returncode == 0:
        print(f"\n[build] Build réussi.")
        print(f"[build] Livrable : {os.path.join(BASE_DIR, target_desc)}")
    else:
        print("\n[build] ECHEC du build. Causes communes :")
        print("  - CustomTkinter mal installé → pip install customtkinter")
        print("  - tkinter absent sur Linux   → sudo apt install python3-tk")
        print("  - Sur macOS, utiliser Python officiel python.org (pas Homebrew)")
        print("  - Lancer depuis le dossier MonPanelLocal/ avec le bon venv activé")
        sys.exit(1)


if __name__ == "__main__":
    main()
