import os
import sys
import subprocess
import threading
import platform
import requests
import re
import zipfile
import tarfile
from core.i18n import t


def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class BoreManager:
    """
    Gère le tunneling avec l'outil léger Bore (en Rust).
    """
    def __init__(self):
        self.base_dir = _get_base_dir()
        self.runtimes_dir = os.path.join(self.base_dir, "runtimes", "bore")
        self.process = None
        self.is_running = False

    def get_executable_path(self):
        exe_name = "bore.exe" if platform.system().lower() == "windows" else "bore"
        return os.path.join(self.runtimes_dir, exe_name)

    def ensure_downloaded(self, on_log=None, on_progress=None):
        if os.path.exists(self.get_executable_path()):
            if on_progress: on_progress(1.0)
            return True

        BORE = t("sys.prefix_bore")
        if on_log: on_log(f"{BORE} {t('sys.bore_checking')}")

        try:
            os.makedirs(self.runtimes_dir, exist_ok=True)
            response = requests.get("https://api.github.com/repos/ekzhang/bore/releases/latest", timeout=5)
            response.raise_for_status()
            release_data = response.json()

            os_name = platform.system().lower()
            machine = platform.machine().lower()

            target_os = ""
            if "win" in os_name:
                target_os = "windows"
            elif "darwin" in os_name or "mac" in os_name:
                target_os = "apple-darwin"
            else:
                target_os = "linux"

            target_arch = "x86_64"
            if "aarch64" in machine or "arm64" in machine:
                target_arch = "aarch64"

            download_url = None
            extension = ""
            for asset in release_data.get("assets", []):
                name = asset.get("name", "").lower()
                if target_os in name and target_arch in name:
                    download_url = asset.get("browser_download_url")
                    extension = "zip" if name.endswith(".zip") else "tar.gz"
                    break

            if not download_url:
                if on_log: on_log(f"{BORE} {t('sys.bore_no_release').format(os=target_os, arch=target_arch)}")
                return False

            archive_path = os.path.join(self.runtimes_dir, f"bore_temp.{extension}")
            if on_log: on_log(f"{BORE} {t('sys.bore_downloading')}")

            with requests.get(download_url, stream=True, timeout=10) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(archive_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and on_progress:
                            on_progress(downloaded / total_size)

            if on_log: on_log(f"{BORE} {t('sys.bore_extracting')}")
            if extension == "zip":
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.runtimes_dir)
            else:
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.runtimes_dir)

            os.remove(archive_path)

            exe_path = self.get_executable_path()
            if "win" not in os_name and os.path.exists(exe_path):
                os.chmod(exe_path, 0o755)

            if on_log: on_log(f"{BORE} {t('sys.bore_installed')}")
            return True

        except Exception as e:
            if on_log: on_log(f"{BORE} {t('sys.bore_install_error').format(err=e)}")
            return False

    def start(self, port, on_log, on_ip_allocated):
        if self.is_running:
            return

        exe_path = self.get_executable_path()
        BORE = t("sys.prefix_bore")
        if not os.path.exists(exe_path):
            if on_log: on_log(f"{BORE} {t('sys.bore_missing_exe')}")
            return

        self.is_running = True

        def _run():
            BORE = t("sys.prefix_bore")
            try:
                self.process = subprocess.Popen(
                    [exe_path, "local", str(port), "--to", "bore.pub"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1
                )

                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        clean_line = line.strip()
                        if on_log: on_log(f"{BORE} {clean_line}")

                        match = re.search(r"listening at (bore\.pub:\d+)", clean_line)
                        if match:
                            on_ip_allocated(match.group(1))

                self.process.wait()
            except Exception as e:
                if on_log: on_log(f"{BORE} {t('sys.bore_crash').format(err=e)}")
            finally:
                self.is_running = False
                if on_log: on_log(f"{BORE} {t('sys.bore_disabled')}")
                on_ip_allocated("")

        threading.Thread(target=_run, daemon=True).start()

    def stop(self):
        if self.process and self.is_running:
            try:
                self.process.terminate()
            except:
                pass
        self.is_running = False
