# EasyHost MC — Guide de build et distribution

## Prérequis

- Python 3.10+
- Dépendances installées :
  ```bash
  pip install -r requirements.txt
  ```
- **Linux uniquement** — tkinter doit être présent :
  ```bash
  sudo apt install python3-tk
  ```
- **macOS uniquement** — utiliser Python officiel [python.org](https://www.python.org/downloads/)
  (le Python Homebrew n'inclut pas tkinter et fera échouer le build)

## Builder

```bash
cd MonPanelLocal
python build.py
```

Le script vérifie les dépendances, construit et indique le chemin du livrable.

## Ce que ça produit

| OS | Livrable |
|----|----------|
| Windows | `dist/EasyHost/` (dossier complet) → zipper en `.zip` |
| macOS | `dist/EasyHost.app` → zipper en `.zip` |
| Linux | `dist/EasyHost/` (dossier complet) → archiver en `.tar.gz` |

## Notes importantes

- **Ne pas utiliser `--onefile`** : CustomTkinter ne trouve pas ses thèmes
  dans un exécutable monofichier.
- **Distribuer le dossier entier** `dist/EasyHost/` — extraire uniquement
  le `.exe` ne fonctionnera pas.
- Les dossiers serveur Minecraft (`minecraft_server_*/`) sont créés à côté
  de l'exécutable au premier lancement, pas dans un dossier système.

## Distribuer sur Gumroad

1. Builder sur chaque OS cible (Windows, macOS, Linux)
2. Compresser chaque livrable :
   - Windows/macOS : zipper le dossier/`.app` en `.zip`
   - Linux : `tar -czf EasyHost-linux.tar.gz dist/EasyHost/`
3. Sur Gumroad, uploader les 3 archives comme fichiers du même produit
   avec les labels **Windows**, **macOS**, **Linux**
