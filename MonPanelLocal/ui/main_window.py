import threading
import customtkinter as ctk
from .tab_console import TabConsole
from .tab_settings import TabSettings
from .tab_players import TabPlayers
from .widget_monitor import WidgetMonitor
from .tab_plugins import TabPlugins

class MainWindow(ctk.CTk):
    def __init__(self, server_manager, config_manager, downloader, system_monitor, plugin_manager, tunnel_manager):
        super().__init__()
        
        self.server_manager = server_manager
        self.config_manager = config_manager
        self.downloader = downloader
        self.system_monitor = system_monitor
        self.plugin_manager = plugin_manager
        self.tunnel_manager = tunnel_manager
        self.current_version = None
        self.tunnel_active = False
        
        self.title("MonPanelLocal - Minecraft Server Dashboard")
        self.geometry("850x600")
        self.minsize(650, 450)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        
        self.tabview.add("Console")
        self.tabview.add("Joueurs")
        self.tabview.add("Paramètres")
        self.tabview.add("Plugins")
        
        # === Onglet Console ===
        self.tab_console = TabConsole(
            self.tabview.tab("Console"),
            on_start=self._action_start,
            on_stop=self._action_stop,
            on_send_command=self._action_send_command,
            on_download=self._action_download,
            on_version_change=self._action_version_change,
            on_tunnel_toggle=self._action_toggle_tunnel
        )
        self.tab_console.pack(fill="both", expand=True)
        
        # === Onglet Joueurs ===
        self.tab_players = TabPlayers(
            self.tabview.tab("Joueurs"),
            send_command_callback=self._action_send_command
        )
        self.tab_players.pack(fill="both", expand=True)
        
        # === Onglet Paramètres ===
        self.tab_settings = TabSettings(
            self.tabview.tab("Paramètres"),
            on_save_callback=self.config_manager.save_config
        )
        self.tab_settings.pack(fill="both", expand=True)
        
        # === Onglet Plugins ===
        self.tab_plugins = TabPlugins(
            self.tabview.tab("Plugins"),
            on_search_callback=self._action_search_plugins,
            on_install_callback=self._action_install_plugin
        )
        self.tab_plugins.pack(fill="both", expand=True)
        
        # === Monitor System Widget ===
        self.widget_monitor = WidgetMonitor(self)
        self.widget_monitor.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Callbacks
        self.server_manager.on_log_received = lambda msg: self.after(0, self.tab_console.append_log, msg)
        self.server_manager.on_status_changed = lambda is_run: self.after(0, self._update_ui_status, is_run)
        self.system_monitor.on_update_callback = lambda cpu, ram: self.after(0, self.widget_monitor.update_metrics, cpu, ram)
        
        # Début
        self.system_monitor.start()
        self._initialize_app()

    def _initialize_app(self):
        """Récupère la liste des versions au démarrage, au format asynchrone pour ne pas freezer."""
        self.tab_console.append_log("[Système] Récupération des versions PaperMC depuis l'API...")
        def fetch():
            versions = self.downloader.get_versions()
            self.after(0, self._on_versions_fetched, versions)
        threading.Thread(target=fetch, daemon=True).start()

    def _on_versions_fetched(self, versions):
        if not versions:
            self.tab_console.append_log("[Erreur] Impossible de charger les versions (Pas d'internet ?).")
        else:
            self.tab_console.append_log(f"[Système] {len(versions)} versions disponibles identifiées au lancement.")
        self.tab_console.set_versions(versions)

    def _action_version_change(self, version):
        """Déclenchée quand l'utilisateur change la version dans le menu déroulant."""
        self.current_version = version
        self.server_manager.set_version(version)
        self.config_manager.set_version(version)
        
        is_inst = self.server_manager.is_installed()
        self.tab_console.update_install_state(is_inst)
        
        # Actualise le formulaire de config si c'est installé
        config_dict = self.config_manager.read_config()
        self.tab_settings.update_form(config_dict)

    def _update_ui_status(self, is_running):
        self.tab_console.set_running_state(is_running)
        
    def _action_start(self):
        self.server_manager.start_server(memory_mb=1024)
        
    def _action_stop(self):
        self.server_manager.stop_server()
        
    def _action_send_command(self, cmd):
        self.server_manager.send_command(cmd)
        
    def _action_download(self):
        if not self.current_version: return
        
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
                if success:
                    self.server_manager.accept_eula()
                    self._action_version_change(self.current_version) # Rafraîchir l'UI
                    self.tab_console.append_log(f"[Système] L'installation de la version {self.current_version} est terminée. Le bouton Démarrer est disponible.")
            self.after(0, finalize)
            
        self.downloader.download_version(
            self.current_version, 
            on_log_callback=on_log, 
            on_progress_callback=on_progress, 
            on_finish_callback=on_finish
        )

    def _action_search_plugins(self, query):
        def on_success(results):
            self.after(0, self.tab_plugins.display_results, results)
        def on_error(err):
            self.after(0, self.tab_plugins.reset_search_state)
            self.after(0, self.tab_console.append_log, f"[Erreur] Recherche plugins: {err}")
            
        self.plugin_manager.search_plugins(query, on_success, on_error)

    def _action_install_plugin(self, project_id):
        if not self.server_manager.server_dir or not self.current_version:
            self.tab_console.append_log("[Erreur] Impossible d'installer : Serveur non sélectionné ou installé.")
            return
            
        self.tab_plugins.show_progress(True)
        
        def on_progress(pct):
            self.after(0, self.tab_plugins.update_progress, pct)
            
        def on_finish(success):
            def finalize():
                self.tab_plugins.show_progress(False)
                if success:
                    self.tab_console.append_log(f"[Système] Plugin installé avec succès !")
                else:
                    self.tab_console.append_log(f"[Erreur] Echec du téléchargement du plugin. Vérifiez la compatibilité.")
            self.after(0, finalize)
            
        self.plugin_manager.download_plugin(
            project_id=project_id,
            server_version=self.current_version,
            server_dir=self.server_manager.server_dir,
            progress_callback=on_progress,
            finish_callback=on_finish
        )

    def _action_toggle_tunnel(self):
        if self.tunnel_active:
            self.tab_console.btn_tunnel.configure(state="disabled")
            def on_stopped():
                self.tunnel_active = False
                self.after(0, lambda: self.tab_console.set_tunnel_state(False))
                self.after(0, lambda: self.tab_console.btn_tunnel.configure(state="normal"))
                self.after(0, self.tab_console.append_log, "[Système] Accès public fermé.")
            self.tunnel_manager.stop_tunnel(callback_stopped=on_stopped)
        else:
            self.tab_console.btn_tunnel.configure(state="disabled")
            
            # Récupération du port depuis server.properties ou port par défaut
            config = self.config_manager.read_config()
            port = int(config.get("server-port", 25565))
            
            def on_success(ip):
                self.tunnel_active = True
                self.after(0, lambda: self.tab_console.set_tunnel_state(True, ip))
                self.after(0, lambda: self.tab_console.btn_tunnel.configure(state="normal"))
                self.after(0, self.tab_console.append_log, f"[Système] Tunnel ouvert ! IP publique : {ip}")
                
            def on_error(err):
                self.after(0, lambda: self.tab_console.btn_tunnel.configure(state="normal"))
                self.after(0, self.tab_console.append_log, f"[Erreur] Tunnel ngrok: {err}")
                
            self.tunnel_manager.start_tunnel(port, on_success, on_error)
