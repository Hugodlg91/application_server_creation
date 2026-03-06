import os
import sys
import subprocess
import requests
import threading
from core.i18n import t


def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Downloader:
    """
    Gère la récupération des versions et le téléchargement du serveur
    pour PaperMC, Vanilla et Fabric.
    """
    def __init__(self):
        self.base_dir = _get_base_dir()
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
            DL  = t("sys.prefix_download")
            ERR = t("sys.prefix_error")
            FAB = t("sys.prefix_fabric")

            server_dir = os.path.join(self.base_dir, f"minecraft_server_{server_type}_{version}")
            os.makedirs(server_dir, exist_ok=True)

            try:
                # ── PaperMC ──────────────────────────────────────────────────
                if server_type == "PaperMC":
                    _log(f"{DL} {t('sys.dl_paper_searching').format(ver=version)}")

                    resp = requests.get(f"{self.paper_api}/versions/{version}", timeout=5)
                    resp.raise_for_status()
                    builds = resp.json().get("builds", [])
                    if not builds:
                        _log(f"{DL} {t('sys.dl_paper_no_build').format(ver=version)}")
                        _finish(False)
                        return

                    latest_build = builds[-1]
                    resp2 = requests.get(
                        f"{self.paper_api}/versions/{version}/builds/{latest_build}", timeout=5
                    )
                    resp2.raise_for_status()
                    jar_name = resp2.json().get("downloads", {}).get("application", {}).get("name")
                    if not jar_name:
                        _log(f"{DL} {t('sys.dl_paper_jar_missing')}")
                        _finish(False)
                        return

                    _log(f"{DL} {t('sys.dl_paper_start').format(ver=version, build=latest_build)}")
                    url = f"{self.paper_api}/versions/{version}/builds/{latest_build}/downloads/{jar_name}"
                    _stream_download(url, os.path.join(server_dir, "server.jar"))
                    _log(f"{DL} {t('sys.dl_paper_done').format(ver=version)}")
                    _progress(1.0)
                    _finish(True)

                # ── Vanilla ──────────────────────────────────────────────────
                elif server_type == "Vanilla":
                    _log(f"{DL} {t('sys.dl_vanilla_fetching')}")
                    resp = requests.get(
                        "https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=5
                    )
                    resp.raise_for_status()
                    entries = resp.json().get("versions", [])
                    entry = next((e for e in entries if e["id"] == version), None)
                    if not entry:
                        _log(f"{DL} {t('sys.dl_vanilla_not_found').format(ver=version)}")
                        _finish(False)
                        return

                    resp2 = requests.get(entry["url"], timeout=5)
                    resp2.raise_for_status()
                    server_url = resp2.json().get("downloads", {}).get("server", {}).get("url")
                    if not server_url:
                        _log(f"{DL} {t('sys.dl_vanilla_no_server').format(ver=version)}")
                        _finish(False)
                        return

                    _log(f"{DL} {t('sys.dl_vanilla_start').format(ver=version)}")
                    _stream_download(server_url, os.path.join(server_dir, "server.jar"))
                    _log(f"{DL} {t('sys.dl_vanilla_done').format(ver=version)}")
                    _progress(1.0)
                    _finish(True)

                # ── Fabric ───────────────────────────────────────────────────
                elif server_type == "Fabric":
                    _log(f"{FAB} {t('sys.dl_fabric_fetching')}")

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

                    _log(f"{FAB} {t('sys.dl_fabric_loader').format(ver=loader_version)}")

                    # Télécharger fabric-installer.jar (0% → 50%)
                    installer_path = os.path.join(server_dir, "fabric-installer.jar")
                    _log(f"{FAB} {t('sys.dl_fabric_installer')}")
                    _stream_download(installer_url, installer_path, 0.0, 0.5)

                    # Vérifier Java
                    if not java_exe_path or not os.path.exists(java_exe_path):
                        _log(f"{ERR} {t('sys.dl_java_missing')}")
                        _finish(False)
                        return

                    # Lancer l'installation via Java
                    _log(f"{FAB} {t('sys.dl_fabric_launching')}")
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
                        _log(f"{ERR} {t('sys.dl_fabric_fail').format(err=result.stderr)}")
                        _finish(False)
                        return

                    _progress(1.0)

                    # Nettoyage
                    try:
                        os.remove(installer_path)
                    except Exception:
                        pass

                    _log(f"{FAB} {t('sys.dl_fabric_done')}")
                    _finish(True)

            except Exception as e:
                _log(f"{DL} {t('sys.dl_error').format(err=e)}")
                _finish(False)

        threading.Thread(target=_download_task, daemon=True).start()
