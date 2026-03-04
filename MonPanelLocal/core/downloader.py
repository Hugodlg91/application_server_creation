import os
import subprocess
import requests
import threading

class Downloader:
    """
    Gère la récupération des versions et le téléchargement du serveur
    pour PaperMC, Vanilla et Fabric.
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.paper_api = "https://api.papermc.io/v2/projects/paper"

    def get_versions(self, server_type: str) -> list:
        """Retourne la liste des versions disponibles selon le type."""
        try:
            if server_type == "PaperMC":
                resp = requests.get(self.paper_api, timeout=5)
                resp.raise_for_status()
                versions = resp.json().get("versions", [])
                return list(reversed(versions))

            elif server_type == "Vanilla":
                resp = requests.get(
                    "https://launchermeta.mojang.com/mc/game/version_manifest.json",
                    timeout=5
                )
                resp.raise_for_status()
                entries = resp.json().get("versions", [])
                return [e["id"] for e in entries if e.get("type") == "release"]

            elif server_type == "Fabric":
                resp = requests.get(
                    "https://meta.fabricmc.net/v2/versions/game",
                    timeout=5
                )
                resp.raise_for_status()
                entries = resp.json()
                return [e["version"] for e in entries if e.get("stable") is True]

        except Exception:
            pass
        return []

    def download_version(self, server_type, version, java_exe_path=None,
                         on_log_callback=None, on_progress_callback=None,
                         on_finish_callback=None):
        """Lance le téléchargement dans un thread daemon."""
        def _log(msg):
            if on_log_callback:
                on_log_callback(msg)

        def _progress(pct):
            if on_progress_callback:
                on_progress_callback(pct)

        def _finish(ok):
            if on_finish_callback:
                on_finish_callback(ok)

        def _stream_download(url, dest_path, progress_start=0.0, progress_end=1.0):
            """Télécharge url vers dest_path avec progression entre progress_start et progress_end."""
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            ratio = downloaded / total
                            _progress(progress_start + ratio * (progress_end - progress_start))

        def _download_task():
            server_dir = os.path.join(self.base_dir, f"minecraft_server_{server_type}_{version}")
            os.makedirs(server_dir, exist_ok=True)

            try:
                # ── PaperMC ──────────────────────────────────────────────────
                if server_type == "PaperMC":
                    _log(f"[Téléchargement] Recherche de la dernière build PaperMC {version}...")

                    resp = requests.get(f"{self.paper_api}/versions/{version}", timeout=5)
                    resp.raise_for_status()
                    builds = resp.json().get("builds", [])
                    if not builds:
                        _log(f"[Téléchargement] Aucune build trouvée pour {version}.")
                        _finish(False)
                        return

                    latest_build = builds[-1]
                    resp2 = requests.get(
                        f"{self.paper_api}/versions/{version}/builds/{latest_build}", timeout=5
                    )
                    resp2.raise_for_status()
                    jar_name = resp2.json().get("downloads", {}).get("application", {}).get("name")
                    if not jar_name:
                        _log("[Téléchargement] Erreur : nom du .jar introuvable.")
                        _finish(False)
                        return

                    _log(f"[Téléchargement] Téléchargement PaperMC {version} (build {latest_build})...")
                    url = f"{self.paper_api}/versions/{version}/builds/{latest_build}/downloads/{jar_name}"
                    _stream_download(url, os.path.join(server_dir, "server.jar"))
                    _log(f"[Téléchargement] Succès → minecraft_server_PaperMC_{version}/server.jar")
                    _progress(1.0)
                    _finish(True)

                # ── Vanilla ──────────────────────────────────────────────────
                elif server_type == "Vanilla":
                    _log(f"[Téléchargement] Récupération du manifest Vanilla...")
                    resp = requests.get(
                        "https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=5
                    )
                    resp.raise_for_status()
                    entries = resp.json().get("versions", [])
                    entry = next((e for e in entries if e["id"] == version), None)
                    if not entry:
                        _log(f"[Téléchargement] Version Vanilla {version} introuvable dans le manifest.")
                        _finish(False)
                        return

                    resp2 = requests.get(entry["url"], timeout=5)
                    resp2.raise_for_status()
                    server_url = resp2.json().get("downloads", {}).get("server", {}).get("url")
                    if not server_url:
                        _log(f"[Téléchargement] Pas de serveur disponible pour Vanilla {version}.")
                        _finish(False)
                        return

                    _log(f"[Téléchargement] Téléchargement Vanilla {version}...")
                    _stream_download(server_url, os.path.join(server_dir, "server.jar"))
                    _log(f"[Téléchargement] Succès → minecraft_server_Vanilla_{version}/server.jar")
                    _progress(1.0)
                    _finish(True)

                # ── Fabric ───────────────────────────────────────────────────
                elif server_type == "Fabric":
                    _log(f"[Fabric] Récupération des métadonnées...")

                    # Installateur : prendre le premier (plus récent)
                    resp = requests.get(
                        "https://meta.fabricmc.net/v2/versions/installer", timeout=5
                    )
                    resp.raise_for_status()
                    installer_info = resp.json()[0]
                    installer_url = installer_info["url"]

                    # Loader : prendre le premier (plus récent)
                    resp2 = requests.get(
                        f"https://meta.fabricmc.net/v2/versions/loader/{version}", timeout=5
                    )
                    resp2.raise_for_status()
                    loader_version = resp2.json()[0]["loader"]["version"]

                    _log(f"[Fabric] Loader {loader_version} sélectionné.")

                    # Télécharger fabric-installer.jar (0% → 50%)
                    installer_path = os.path.join(server_dir, "fabric-installer.jar")
                    _log(f"[Fabric] Téléchargement de l'installateur...")
                    _stream_download(installer_url, installer_path, 0.0, 0.5)

                    # Vérifier Java
                    if not java_exe_path or not os.path.exists(java_exe_path):
                        _log("[Erreur] Java introuvable pour lancer l'installateur Fabric.")
                        _finish(False)
                        return

                    # Lancer l'installation via Java
                    _log("[Fabric] Lancement de l'installateur...")
                    result = subprocess.run(
                        [java_exe_path, "-jar", "fabric-installer.jar",
                         "server",
                         "-mcversion", version,
                         "-loader", loader_version,
                         "-downloadMinecraft"],
                        cwd=server_dir,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )

                    if result.returncode != 0:
                        _log(f"[Erreur] Installateur Fabric a échoué :\n{result.stderr}")
                        _finish(False)
                        return

                    _progress(1.0)

                    # Nettoyage
                    try:
                        os.remove(installer_path)
                    except Exception:
                        pass

                    _log("[Fabric] Installation terminée.")
                    _finish(True)

            except Exception as e:
                _log(f"[Téléchargement] Erreur : {e}")
                _finish(False)

        threading.Thread(target=_download_task, daemon=True).start()
