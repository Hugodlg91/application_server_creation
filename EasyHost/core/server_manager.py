import os
import sys
import subprocess
import threading
import re
import time
from .java_manager import JavaManager
from core.i18n import t


def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ServerManager:
    """
    Gère le processus Java du serveur Minecraft et ses dossiers associés,
    en utilisant les runtimes dynamiques de JavaManager.
    """
    def __init__(self, on_log_received=None, on_status_changed=None):
        self.java_manager = JavaManager()
        self.process = None
        self.base_dir = _get_base_dir()
        self.server_dir = self.base_dir
        self.current_version = None
        self.jar_path = ""
        self.eula_path = ""
        self.is_running = False
        
        self.connected_players = set()
        self.on_players_update_callback = None

        self.server_type = "PaperMC"
        self.launch_jar = "server.jar"

        self.on_log_received = on_log_received
        self.on_status_changed = on_status_changed

        self.scheduler_active = False
        self.scheduler_thread = None

    def set_version(self, server_type, version):
        """Met à jour les chemins cibles selon le type et la version sélectionnés."""
        if not version:
            return
        self.server_type = server_type
        self.current_version = version
        self.server_dir = os.path.join(self.base_dir, f"minecraft_server_{server_type}_{version}")

        if server_type == "Fabric":
            self.launch_jar = "fabric-server-launch.jar"
        else:
            self.launch_jar = "server.jar"

        self.jar_path = os.path.join(self.server_dir, self.launch_jar)
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
            SYS = t("sys.prefix_system")
            ERR = t("sys.prefix_error")
            try:
                with open(self.eula_path, "w", encoding="utf-8") as f:
                    f.write("eula=true\n")
                self._notify_log(f"{SYS} {t('sys.eula_created')}")
            except Exception as e:
                self._notify_log(f"{ERR} {t('sys.eula_fail').format(err=e)}")

    def start_server(self, memory_mb=1024, aikar_flags=False):
        SYS  = t("sys.prefix_system")
        ERR  = t("sys.prefix_error")
        if self.is_running:
            self._notify_log(f"{SYS} {t('sys.already_running')}")
            return

        if not self.is_installed():
            self._notify_log(f"{ERR} {t('sys.jar_missing')}")
            return

        self.accept_eula()

        def _startup_sequence():
            SYS   = t("sys.prefix_system")
            ERR   = t("sys.prefix_error")
            FATAL = t("sys.prefix_fatal")

            # 1. Vérifie et installe le JRE si nécessaire
            target_java = self.java_manager.get_required_java_version(self.current_version)

            self._notify_log(f"{SYS} {t('sys.java_checking').format(ver=target_java)}")

            # Cette étape bloque (téléchargement). On est déjà dans un sous-thread.
            success = self.java_manager.ensure_java(target_java, on_log_callback=self._notify_log)
            if not success:
                self._notify_log(f"{ERR} {t('sys.java_missing').format(ver=target_java)}")
                self._notify_status(False)
                return

            java_exe = self.java_manager.get_java_executable(target_java)
            if not java_exe:
                self._notify_log(f"{ERR} {t('sys.java_exe_missing').format(ver=target_java)}")
                self._notify_status(False)
                return

            # 2. Démarrage du subprocess
            try:
                if aikar_flags:
                    java_args = [
                        f"-Xms{memory_mb}M", f"-Xmx{memory_mb}M",
                        "-XX:+UseG1GC", "-XX:+ParallelRefProcEnabled",
                        "-XX:MaxGCPauseMillis=200", "-XX:+UnlockExperimentalVMOptions",
                        "-XX:+DisableExplicitGC", "-XX:+AlwaysPreTouch",
                        "-XX:G1HeapWastePercent=5", "-XX:G1MixedGCCountTarget=4",
                        "-XX:G1MixedGCLiveThresholdPercent=90",
                        "-XX:G1RSetUpdatingPauseTimePercent=5",
                        "-XX:SurvivorRatio=32", "-XX:+PerfDisableSharedMem",
                        "-XX:MaxTenuringThreshold=1"
                    ]
                else:
                    java_args = [f"-Xms{memory_mb}M", f"-Xmx{memory_mb}M"]

                aikar_label = t("sys.start_info_aikar_on") if aikar_flags else t("sys.start_info_aikar_off")
                self._notify_log(f"{SYS} {t('sys.start_info').format(ram=memory_mb, aikar=aikar_label)}")

                self.process = subprocess.Popen(
                    [java_exe] + java_args + ["-jar", self.launch_jar, "nogui"],
                    cwd=self.server_dir,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                self._notify_status(True)
                self._notify_log(f"{SYS} {t('sys.starting_in').format(dir=self.server_dir, ver=target_java)}")

                # Lance la lecture des événements serveurs
                self._read_logs()

            except Exception as e:
                self._notify_log(f"{FATAL} {t('sys.java_launch_fail').format(err=e)}")
                self._notify_status(False)

        # Lancer toute la séquence (incluant le possible téléchargement) en asynchrone
        threading.Thread(target=_startup_sequence, daemon=True).start()

    def _read_logs(self):
        if not self.process: return
        
        # Outil pour nettoyer les codes couleurs invisibles de PaperMC (ANSI)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        for line in iter(self.process.stdout.readline, ''):
            if line:
                # 1. On récupère la ligne et on l'envoie à la console visuelle
                line_clean = line.strip()
                self._notify_log(line_clean)
                
                # 2. On retire les couleurs invisibles pour que notre détecteur ne soit pas aveuglé
                line_analyzed = ansi_escape.sub('', line_clean)
                
                # --- DETECTION DES CONNEXIONS ---
                # On ajoute \. et \* pour supporter les joueurs Bedrock/Geyser
                match_join = re.search(r"\]:\s+([a-zA-Z0-9_\.\*]+)\s+joined the game", line_analyzed)
                if match_join:
                    player_name = match_join.group(1)
                    self.connected_players.add(player_name)
                    if self.on_players_update_callback:
                        self.on_players_update_callback(list(self.connected_players))

                # --- DETECTION DES DECONNEXIONS ---
                match_leave = re.search(r"\]:\s+([a-zA-Z0-9_\.\*]+)\s+left the game", line_analyzed)
                if match_leave:
                    player_name = match_leave.group(1)
                    if player_name in self.connected_players:
                        self.connected_players.remove(player_name)
                        if self.on_players_update_callback:
                            self.on_players_update_callback(list(self.connected_players))

                # --- DETECTION DU BOUTON ACTUALISER (/list) ---
                # Rendu beaucoup plus flexible pour ignorer les mots qui changent selon les versions
                match_list = re.search(r"players online:(.*)", line_analyzed)
                if match_list:
                    players_string = match_list.group(1).strip()
                    self.connected_players.clear()
                    if players_string: # S'il y a des joueurs
                        for p in players_string.split(","):
                            clean_p = p.strip()
                            if clean_p:
                                self.connected_players.add(clean_p)
                    
                    if self.on_players_update_callback:
                        self.on_players_update_callback(list(self.connected_players))

        self.process.stdout.close()
        self.process.wait()
        self._notify_status(False)
        self._notify_log(f"{t('sys.prefix_system')} {t('sys.server_stopped')}")
        # On vide la liste des joueurs quand le serveur s'éteint
        self.connected_players.clear()
        if self.on_players_update_callback:
            self.on_players_update_callback(list(self.connected_players))

    def send_command(self, command):
        if self.is_running and self.process and self.process.stdin:
            try:
                self._notify_log(f"> {command}")
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except Exception as e:
                self._notify_log(
                    f"{t('sys.prefix_error')} {t('sys.command_fail').format(err=e)}")
        else:
            self._notify_log(
                f"{t('sys.prefix_system')} {t('sys.command_ignored')}")
            
    def stop_server(self):
        if self.is_running:
            self.send_command("stop")
        else:
            self._notify_log(
                f"{t('sys.prefix_system')} {t('sys.server_not_running')}")

    def start_scheduler(self, message, interval_minutes):
        """Lance un thread qui envoie périodiquement un message 'say' au serveur."""
        self.stop_scheduler()
        self.scheduler_active = True

        def _loop():
            while self.scheduler_active:
                time.sleep(interval_minutes * 60)
                if self.scheduler_active and self.is_running:
                    self.send_command(f"say {message}")

        self.scheduler_thread = threading.Thread(target=_loop, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """Arrête le planificateur de messages."""
        self.scheduler_active = False
