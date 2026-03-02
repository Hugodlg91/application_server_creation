import sys
import os

# Optionnel : S'assurer que le dossier parent est dans le PYTHONPATH si besoin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from core.server_manager import ServerManager
from core.downloader import Downloader
from core.config_manager import ConfigManager
from core.system_monitor import SystemMonitor
from core.plugin_manager import PluginManager
from core.playit_manager import PlayitManager
from ui.main_window import MainWindow


def main():
    # Définition du thème UI
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    # 1. Initialisation des composants "Core" (Backend)
    server_manager = ServerManager()
    downloader = Downloader()
    config_manager = ConfigManager()
    system_monitor = SystemMonitor(on_update_callback=None) # Le callback est attaché plus tard par la fenêtre
    plugin_manager = PluginManager()
    playit_manager = PlayitManager()
    
    # 2. Création de l'interface graphique (Frontend), en injectant les dépendances
    app = MainWindow(
        server_manager=server_manager,
        config_manager=config_manager,
        downloader=downloader,
        system_monitor=system_monitor,
        plugin_manager=plugin_manager,
        playit_manager=playit_manager
    )
    
    server_manager.on_players_update_callback = lambda players: app.after(0, app.tab_players.update_player_list, players)
    
    # 3. Fonction pour gérer la fermeture propre
    def on_closing():
        # Arrêt immédiat de playit et autres services non-process
        playit_manager.stop()
        
        if server_manager.is_running:
            server_manager.on_log_received("[Système] Arrêt automatique du serveur avant la fermeture...")
            server_manager.stop_server()
            # Attendre un peu pour que le stop s'envoie
            app.after(3000, lambda: _final_close(app, system_monitor, server_manager))
        else:
            _final_close(app, system_monitor, server_manager)
            
    app.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 4. Lancement de la boucle principale
    app.mainloop()
    
def _final_close(app, monitor, manager):
    monitor.stop()
    if manager.process:
        try:
            manager.process.kill() # Security si toujours vivant
        except:
            pass
    app.destroy()

if __name__ == "__main__":
    main()
