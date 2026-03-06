# EasyHost MC

> Host a Minecraft server on your own PC in minutes — no command line, no technical knowledge required.

![Version](https://img.shields.io/badge/version-1.0.0-6366f1)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-informational)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Proprietary-red)

---

## What is EasyHost?

EasyHost is a desktop application that lets you launch and manage a Minecraft server without ever opening a terminal. It handles everything automatically — downloading the right Java version, installing the server, and even making it publicly accessible without touching your router.

**Built for people who just want to play with friends, not deal with infrastructure.**

---

## Features

- **One-click install & launch** — select a server type, pick a version, click Install. Done.
- **Multi-server support** — PaperMC, Vanilla and Fabric out of the box
- **Automatic Java management** — downloads the correct JRE for each Minecraft version (Java 8, 16, 17 or 21)
- **Built-in tunneling** — make your server public instantly via [Bore](https://github.com/ekzhang/bore), no port forwarding needed
- **Plugin manager** — search and install plugins from Modrinth directly from the UI
- **Player management** — see who's online, kick, ban or op players in one click
- **Performance settings** — configure RAM allocation and Aikar JVM flags
- **Auto-broadcast scheduler** — send automatic messages to players at set intervals
- **Live console** — color-coded server output with command history (↑/↓)
- **FR / EN interface** — switch language from the Settings tab

---

## Screenshots

> *(coming soon)*

---

## Download

Head to the [Releases](../../releases) page and download the zip for your platform:

| Platform | File |
|----------|------|
| Windows  | `EasyHost-Windows.zip` |
| macOS    | `EasyHost-macOS.zip` |
| Linux    | `EasyHost-Linux.zip` |

**No installation required** — just unzip and run.

---

## Getting Started

### Windows
1. Download and unzip `EasyHost-Windows.zip`
2. Run `EasyHost.exe`
3. Select a server type (PaperMC recommended) and a Minecraft version
4. Click **Install** — EasyHost handles the rest
5. Click **Start** once the installation is complete

### macOS
1. Download and unzip `EasyHost-macOS.zip`
2. Double-click `EasyHost.app`
3. If macOS blocks the app: right-click → Open → Open anyway
4. Follow the same steps as Windows

### Linux
1. Download and unzip `EasyHost-Linux.tar.gz`
2. Make the binary executable: `chmod +x EasyHost/EasyHost`
3. Run: `./EasyHost/EasyHost`
4. If tkinter is missing: `sudo apt install python3-tk`

---

## Making Your Server Public

1. Start your server
2. Click **Make Public** in the console bar
3. EasyHost downloads Bore automatically and generates a public address (e.g. `bore.pub:12345`)
4. Share that address with your friends — they connect using it as the server IP

No router configuration, no static IP, no DynDNS needed.

---

## System Requirements

| | Minimum |
|---|---|
| OS | Windows 10, macOS 11, Ubuntu 20.04 |
| RAM | 2 GB (4 GB recommended for the server itself) |
| Storage | 500 MB free (+ server files) |
| Internet | Required for first install |

Java is downloaded and managed automatically — you don't need to install it manually.

---

## Supported Server Types

| Type | Description |
|------|-------------|
| **PaperMC** | Recommended — best performance, plugin support, all versions |
| **Vanilla** | Official Mojang server — no plugins |
| **Fabric** | Mod support via Fabric loader |

---

## Building from Source

If you want to run EasyHost from source:

```bash
git clone https://github.com/yourname/easyhost
cd easyhost/MonPanelLocal
pip install -r requirements.txt
python main.py
```

To create a distributable build:

```bash
python build.py
```

See `BUILD.md` for full build instructions and platform-specific notes.

---

## Roadmap

- [ ] Automatic server backups
- [ ] Multi-instance management (run several servers at once)
- [ ] Other games (Valheim, Terraria, Palworld...)

Support development on [Ko-fi](https://ko-fi.com/vladimirwrld) or [Patreon](https://www.patreon.com/cw/VladimirWRLD) to help prioritize these features.

---

## License

EasyHost MC is proprietary software. You may use it for personal use.
Redistribution, modification or resale is not permitted without explicit written permission.

© 2026 EasyHost — All rights reserved.
