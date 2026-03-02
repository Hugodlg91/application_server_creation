import os
import subprocess
import threading
import platform
import requests
import re
import stat

class PlayitManager:
    """
    Gère le téléchargement et l'exécution du daemon playit.gg en local
    pour ouvrir le serveur sur internet sans configuration de routeur.
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.playit_dir = os.path.join(self.base_dir, "runtimes", "playit")
        self.process = None
        self.is_running = False
        self.executable_path = None
        
    def _get_download_url(self):
        """Détermine la bonne release GitHub selon l'OS et l'architecture."""
        sys_os = platform.system().lower()
        arch = platform.machine().lower()
        
        # Basé sur playit-cloud/playit-agent releases
        base_url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/"
        
        if sys_os == "windows":
            return base_url + "playit-windows-x86_64.exe", "playit.exe"
        elif sys_os == "linux":
            if "aarch64" in arch or "arm64" in arch:
                return base_url + "playit-linux-aarch64", "playit"
            else:
                return base_url + "playit-linux-x86_64", "playit"
        elif sys_os == "darwin": # Mac
            if "arm64" in arch:
                return base_url + "playit-macos-aarch64", "playit"
            else:
                return base_url + "playit-macos-x86_64", "playit"
        else:
            raise Exception(f"OS non supporté: {sys_os} {arch}")

    def ensure_downloaded(self, progress_callback=None):
        """Vérifie si le binaire playit existe, sinon le télécharge."""
        url, filename = self._get_download_url()
        self.executable_path = os.path.join(self.playit_dir, filename)
        
        if os.path.exists(self.executable_path):
            return True
            
        os.makedirs(self.playit_dir, exist_ok=True)
        
        try:
            print(f"[PlayitManager] Téléchargement depuis {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.executable_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0 and progress_callback:
                            progress_callback(downloaded / total_size)
                            
            # Rendre exécutable sous Linux/Mac
            if platform.system().lower() != "windows":
                st = os.stat(self.executable_path)
                os.chmod(self.executable_path, st.st_mode | stat.S_IEXEC)
                
            return True
        except Exception as e:
            print(f"[PlayitManager] Erreur de téléchargement: {e}")
            if os.path.exists(self.executable_path):
                os.remove(self.executable_path)
            return False

    def start(self, on_log=None, on_claim_link=None, on_ip_allocated=None):
        """Lance playit.gg et parse sa sortie console pour récupérer le statut."""
        if self.is_running:
            return
            
        if not self.executable_path or not os.path.exists(self.executable_path):
            if on_log: on_log("[Erreur] Exécutable playit introuvable.")
            return

        def _run():
            self.is_running = True
            try:
                # Lance dans runtimes/playit/ pour y sauvegarder le playit.toml
                self.process = subprocess.Popen(
                    [self.executable_path],
                    cwd=self.playit_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    bufsize=1,
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == "windows" else 0
                )

                for line in iter(self.process.stdout.readline, ''):
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                        
                    if on_log:
                        on_log(f"[Playit] {line}")
                        
                    claim_match = re.search(r"(https://playit\.gg/claim/[a-zA-Z0-9]+)", line)
                    if claim_match and on_claim_link:
                        on_claim_link(claim_match.group(1))
                        
                    ip_match = re.search(r"([a-zA-Z0-9\-]+\.(auto|tcp)\.playit\.gg:\d+)", line)
                    if ip_match and on_ip_allocated:
                        on_ip_allocated(ip_match.group(1).strip())

            except Exception as e:
                print(f"[PlayitManager] Process error: {e}")
                if on_log: on_log(f"[Playit] Erreur: {e}")
            finally:
                self.is_running = False
                self.process = None

        threading.Thread(target=_run, daemon=True).start()

    def stop(self):
        """Arrête le tunnel playit.gg."""
        if self.process:
            try:
                self.process.terminate()
            except:
                pass
        self.is_running = False
