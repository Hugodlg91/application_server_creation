import threading
import customtkinter as ctk

from .header_bar import HeaderBar
from .tab_bar import TabBar
from .tab_console import TabConsole
from .tab_settings import TabSettings
from .tab_players import TabPlayers
from .tab_plugins import TabPlugins

BG      = "#0f172a"
SURFACE = "#1e293b"
BORDER  = "#334155"


class MainWindow(ctk.CTk):
    def __init__(self, server_manager, config_manager, downloader,
                 system_monitor, plugin_manager, bore_manager):
        super().__init__()
        self.update()   # Force le mapping de la fenêtre avant les rendus CTk (Linux)

        self.server_manager = server_manager
        self.config_manager = config_manager
        self.downloader = downloader
        self.system_monitor = system_monitor
        self.plugin_manager = plugin_manager
        self.bore_manager = bore_manager

        self.configure(fg_color=BG)
        self.title("MonPanelLocal - Minecraft Server Dashboard")
        self.geometry("950x680")
        self.minsize(700, 500)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── HeaderBar (row 0) ─────────────────────────────────────────────
        self.header_bar = HeaderBar(
            self, server_type="PaperMC", version="—", is_running=False)
        self.header_bar.grid(row=0, column=0, sticky="ew")

        # ── TabBar (row 1) ────────────────────────────────────────────────
        self.tab_bar = TabBar(self, on_tab_change=self._show_tab)
        self.tab_bar.grid(row=1, column=0, sticky="ew")

        # ── Contenu (row 2) — tous les onglets empilés via .place() ───────
        self.frame_content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.frame_content.grid(row=2, column=0, sticky="nsew")

        # === Onglet Console ===
        self.tab_console = TabConsole(
            self.frame_content,
            on_start=self._action_start,
            on_stop=self._action_stop,
            on_send_command=self._action_send_command,
            on_download=self._action_download,
            on_version_change=self._action_version_change,
            on_type_change=self._action_type_change,
            on_bore_toggle=self._action_toggle_bore
        )

        # === Onglet Joueurs ===
        self.tab_players = TabPlayers(
            self.frame_content,
            send_command_callback=self._action_send_command
        )

        # === Onglet Paramètres ===
        self.tab_settings = TabSettings(
            self.frame_content,
            on_save_callback=self.config_manager.save_config,
            on_load_perf_callback=self.config_manager.load_performance_config,
            on_save_perf_callback=self.config_manager.save_performance_config,
            on_start_scheduler=lambda msg, interval: self.server_manager.start_scheduler(msg, interval),
            on_stop_scheduler=lambda: self.server_manager.stop_scheduler()
        )

        # === Onglet Plugins ===
        self.tab_plugins = TabPlugins(
            self.frame_content,
            on_search_callback=self._action_search_plugins,
            on_install_callback=self._action_install_plugin
        )

        # Empiler tous les onglets dans frame_content
        for tab in [self.tab_console, self.tab_players,
                    self.tab_settings, self.tab_plugins]:
            tab.place(x=0, y=0, relwidth=1, relheight=1)

        # Onglet affiché par défaut
        self._show_tab("console")

        # ── Callbacks ─────────────────────────────────────────────────────
        self.server_manager.on_log_received = (
            lambda msg: self.after(0, self.tab_console.append_log, msg))
        self.server_manager.on_status_changed = (
            lambda is_run: self.after(0, self._update_ui_status, is_run))
        self.system_monitor.on_update_callback = (
            lambda cpu, ram: self.after(0, self.header_bar.update_metrics, cpu, ram))

        # Début
        self.system_monitor.start()
        self._initialize_app()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _show_tab(self, tab_id):
        # tab_id = clé minuscule envoyée par TabBar ("console", "joueurs", …)
        tabs = {
            "console":    self.tab_console,
            "joueurs":    self.tab_players,
            "plugins":    self.tab_plugins,
            "parametres": self.tab_settings,
        }
        if tab_id in tabs:
            tabs[tab_id].lift()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _initialize_app(self):
        saved_type = self.config_manager.load_server_type()
        self.current_server_type = saved_type
        self.tab_console.option_type.set(saved_type)
        self.after(0, self.tab_console.append_log,
                   f"[Système] Récupération des versions {saved_type} depuis l'API...")

        def fetch():
            versions = self.downloader.get_versions(saved_type)
            self.after(0, self._on_versions_fetched, versions)

        threading.Thread(target=fetch, daemon=True).start()

    def _on_versions_fetched(self, versions):
        self.tab_console.set_loading_state(False)
        if not versions:
            self.tab_console.append_log(
                "[Erreur] Impossible de charger les versions (Pas d'internet ?).")
        else:
            server_type = getattr(self, "current_server_type", "PaperMC")
            self.tab_console.append_log(
                f"[Système] {len(versions)} versions {server_type} disponibles.")
        self.tab_console.set_versions(versions)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _action_type_change(self, server_type):
        self.current_server_type = server_type
        self.config_manager.save_server_type(server_type)
        self.tab_console.set_loading_state(True)

        def fetch():
            versions = self.downloader.get_versions(server_type)
            self.after(0, self._on_versions_fetched, versions)

        threading.Thread(target=fetch, daemon=True).start()

    def _action_version_change(self, version):
        self.current_version = version
        server_type = getattr(self, "current_server_type", "PaperMC")
        self.server_manager.set_version(server_type, version)
        self.config_manager.set_version(server_type, version)
        self.header_bar.set_server_info(server_type, version)

        is_inst = self.server_manager.is_installed()
        self.tab_console.update_install_state(is_inst)

        config_dict = self.config_manager.read_config()
        self.tab_settings.update_form(config_dict)

    def _update_ui_status(self, is_running):
        self.tab_console.set_running_state(is_running)
        self.header_bar.update_status(is_running, 0)

    def _on_players_update(self, players):
        self.tab_players.update_player_list(players)
        count = len(players)
        self.tab_bar.update_badge(count)
        self.header_bar.update_status(self.server_manager.is_running, count)

    def _action_start(self):
        perf = self.config_manager.load_performance_config()
        self.server_manager.start_server(
            memory_mb=perf["ram_mb"], aikar_flags=perf["aikar_flags"])

    def _action_stop(self):
        self.server_manager.stop_server()

    def _action_send_command(self, cmd):
        self.server_manager.send_command(cmd)

    def _action_download(self):
        if not hasattr(self, "current_version") or not self.current_version:
            return
        server_type = getattr(self, "current_server_type", "PaperMC")

        self.tab_console.show_progress(True)
        self.tab_console.btn_install.configure(state="disabled")

        def on_log(msg):
            self.after(0, self.tab_console.append_log, msg)

        def on_progress(pct):
            self.after(0, self.tab_console.update_progress, pct)

        def on_finish(success):
            def finalize():
                self.tab_console.show_progress(False)
                self.tab_console.btn_install.configure(state="normal")
                self.tab_console.option_version.configure(state="normal")
                self.tab_console.option_type.configure(state="normal")
                if success:
                    self.server_manager.accept_eula()
                    self._action_version_change(self.current_version)
                    self.tab_console.append_log(
                        f"[Système] Installation {server_type} {self.current_version} terminée !")
            self.after(0, finalize)

        def prepare_and_download():
            java_path = None
            if server_type == "Fabric":
                java_ver = self.server_manager.java_manager.get_required_java_version(
                    self.current_version)
                on_log(f"[Système] Vérification de Java {java_ver} pour l'installateur Fabric...")
                ok = self.server_manager.java_manager.ensure_java(java_ver, on_log)
                if ok:
                    java_path = self.server_manager.java_manager.get_java_executable(java_ver)

            self.downloader.download_version(
                server_type=server_type,
                version=self.current_version,
                java_exe_path=java_path,
                on_log_callback=on_log,
                on_progress_callback=on_progress,
                on_finish_callback=on_finish
            )

        threading.Thread(target=prepare_and_download, daemon=True).start()

    def _action_search_plugins(self, query):
        def on_success(results):
            self.after(0, self.tab_plugins.display_results, results)

        def on_error(err):
            self.after(0, self.tab_plugins.reset_search_state)
            self.after(0, self.tab_console.append_log,
                       f"[Erreur] Recherche plugins: {err}")

        self.plugin_manager.search_plugins(query, on_success, on_error)

    def _action_install_plugin(self, project_id):
        if not self.server_manager.server_dir or not self.current_version:
            self.tab_console.append_log(
                "[Erreur] Impossible d'installer : Serveur non sélectionné ou installé.")
            return

        self.tab_plugins.show_progress(True)

        def on_progress(pct):
            self.after(0, self.tab_plugins.update_progress, pct)

        def on_finish(success):
            def finalize():
                self.tab_plugins.show_progress(False)
                if success:
                    self.tab_console.append_log("[Système] Plugin installé avec succès !")
                else:
                    self.tab_console.append_log(
                        "[Erreur] Echec du téléchargement du plugin. Vérifiez la compatibilité.")
            self.after(0, finalize)

        self.plugin_manager.download_plugin(
            project_id=project_id,
            server_version=self.current_version,
            server_dir=self.server_manager.server_dir,
            progress_callback=on_progress,
            finish_callback=on_finish
        )

    def _action_toggle_bore(self):
        if self.bore_manager.is_running:
            self.tab_console.btn_bore.configure(state="disabled")
            self.bore_manager.stop()
            self.tab_console.set_bore_state(False)
            self.tab_console.btn_bore.configure(state="normal")
            self.tab_console.append_log("[Système] Tunnel Bore arrêté.")
        else:
            self.tab_console.btn_bore.configure(state="disabled")

            def start_process():
                def on_log_prep(msg):
                    self.after(0, self.tab_console.append_log, msg)

                if not self.bore_manager.ensure_downloaded(on_log=on_log_prep):
                    self.after(0, lambda: self.tab_console.btn_bore.configure(state="normal"))
                    self.after(0, self.tab_console.append_log,
                               "[Erreur] Impossible de préparer l'exécutable Bore.")
                    return

                self.after(0, lambda: self.tab_console.set_bore_state(True))
                self.after(0, lambda: self.tab_console.btn_bore.configure(state="normal"))
                self.after(0, self.tab_console.append_log,
                           "[Système] Démarrage de Bore sur le port 25565...")

                port = 25565
                try:
                    props = self.config_manager.read_config()
                    if "server-port" in props:
                        port = int(props["server-port"])
                except Exception:
                    pass

                def on_log(msg):
                    self.after(0, self.tab_console.append_log, msg)

                def on_ip(ip):
                    if ip:
                        self.after(0, lambda: self.tab_console.set_bore_state(True, ip))
                        self.after(0, self.tab_console.append_log,
                                   f"[Bore] IP publique allouée: {ip}")

                self.bore_manager.start(port, on_log, on_ip)

            import threading
            threading.Thread(target=start_process, daemon=True).start()
