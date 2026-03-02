import os
import subprocess
import threading
from .java_manager import JavaManager

class ServerManager:
    """
    Gère le processus Java du serveur Minecraft et ses dossiers associés,
    en utilisant les runtimes dynamiques de JavaManager.
    """
    def __init__(self, on_log_received=None, on_status_changed=None):
        self.java_manager = JavaManager()
        self.process = None
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.server_dir = self.base_dir
        self.current_version = None
        self.jar_path = ""
        self.eula_path = ""
        self.is_running = False
        
        self.on_log_received = on_log_received
        self.on_status_changed = on_status_changed

    def set_version(self, version):
        """Met à jour les chemins cibles selon la version de minecraft sélectionnée."""
        if not version:
            return
        self.current_version = version
        self.server_dir = os.path.join(self.base_dir, f"minecraft_server_{version}")
        self.jar_path = os.path.join(self.server_dir, "server.jar")
        self.eula_path = os.path.join(self.server_dir, "eula.txt")

    def is_installed(self):
        """Vérifie si le jar de la version courante est installé."""
        if not self.jar_path: return False
        return os.path.exists(self.jar_path)

    def _notify_status(self, is_running):
        self.is_running = is_running
        if self.on_status_changed:
            self.on_status_changed(self.is_running)

    def _notify_log(self, message):
        if self.on_log_received:
            self.on_log_received(message)

    def accept_eula(self):
        """Vérifie si l'EULA existe, sinon le crée avec eula=true."""
        if not self.eula_path: return
        os.makedirs(self.server_dir, exist_ok=True)
        if not os.path.exists(self.eula_path):
            try:
                with open(self.eula_path, "w", encoding="utf-8") as f:
                    f.write("eula=true\n")
                self._notify_log("[Système] eula.txt généré avec succès (eula=true).")
            except Exception as e:
                self._notify_log(f"[Erreur] Impossible de créer eula.txt: {e}")

    def start_server(self, memory_mb=1024):
        if self.is_running:
            self._notify_log("[Système] Le serveur est déjà en cours d'exécution.")
            return

        if not self.is_installed():
            self._notify_log("[Erreur] server.jar introuvable pour cette version.")
            return

        self.accept_eula()

        def _startup_sequence():
            # 1. Vérifie et installe le JRE si nécessaire
            target_java = self.java_manager.get_required_java_version(self.current_version)
            
            self._notify_log(f"[Système] Vérification du runtime Java (Version requise: {target_java})...")
            
            # Cette étape bloque (téléchargement). On est déjà dans un sous-thread.
            success = self.java_manager.ensure_java(target_java, on_log_callback=self._notify_log)
            if not success:
                self._notify_log(f"[Erreur] Impossible d'acquérir Java {target_java}. Abandon du démarrage.")
                self._notify_status(False)
                return
                
            java_exe = self.java_manager.get_java_executable(target_java)
            if not java_exe:
                self._notify_log(f"[Erreur] Exécutable Java {target_java} introuvable après installation.")
                self._notify_status(False)
                return

            # 2. Démarrage du subprocess
            try:
                self.process = subprocess.Popen(
                    [java_exe, f"-Xms{memory_mb}M", f"-Xmx{memory_mb}M", "-jar", self.jar_path, "nogui"],
                    cwd=self.server_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                self._notify_status(True)
                self._notify_log(f"[Système] Démarrage du serveur dans {self.server_dir} avec Java {target_java}...")

                # Lance la lecture des événements serveurs
                self._read_logs()

            except Exception as e:
                self._notify_log(f"[Erreur fatale] Impossible de lancer Java: {e}")
                self._notify_status(False)

        # Lancer toute la séquence (incluant le possible téléchargement) en asynchrone
        threading.Thread(target=_startup_sequence, daemon=True).start()

    def _read_logs(self):
        if not self.process: return
        for line in iter(self.process.stdout.readline, ''):
            if line:
                self._notify_log(line.strip())
        self.process.stdout.close()
        self.process.wait()
        self._notify_status(False)
        self._notify_log("[Système] Le serveur est arrêté.")

    def send_command(self, command):
        if self.is_running and self.process and self.process.stdin:
            try:
                self._notify_log(f"> {command}")
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                self._notify_log(f"[Erreur] Échec de l'envoi de la commande: {e}")
        else:
            self._notify_log("[Système] Serveur éteint, commande ignorée.")
            
    def stop_server(self):
        if self.is_running:
            self.send_command("stop")
        else:
            self._notify_log("[Système] Le serveur n'est pas en marche.")
