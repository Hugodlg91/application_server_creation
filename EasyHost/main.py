import sys
import os
import threading

# Optionnel : S'assurer que le dossier parent est dans le PYTHONPATH si besoin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from core.server_manager import ServerManager
from core.downloader import Downloader
from core.config_manager import ConfigManager
from core.system_monitor import SystemMonitor
from core.plugin_manager import PluginManager
from core.bore_manager import BoreManager
from core import i18n
from core.i18n import t
from ui.main_window import MainWindow


def main():
    # Définition du thème UI
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    
    # 1. Initialisation des composants "Core" (Backend)
    server_manager = ServerManager()
    downloader = Downloader()
    config_manager = ConfigManager()
    system_monitor = SystemMonitor(on_update_callback=None) # Le callback est attaché plus tard par la fenêtre
    plugin_manager = PluginManager()
    bore_manager = BoreManager()

    # 1b. Appliquer la langue sauvegardée avant toute création de widget
    i18n.set_lang(config_manager.load_lang())
    
    # 2. Création de l'interface graphique (Frontend), en injectant les dépendances
    app = MainWindow(
        server_manager=server_manager,
        config_manager=config_manager,
        downloader=downloader,
        system_monitor=system_monitor,
        plugin_manager=plugin_manager,
        bore_manager=bore_manager
    )
    
    server_manager.on_players_update_callback = lambda players: app.after(0, app._on_players_update, players)
    
    # 3. Fonction pour gérer la fermeture propre
    def on_closing():
        bore_manager.stop()

        if server_manager.is_running:
            # Bloquer les clics supplémentaires sur la croix
            app.protocol("WM_DELETE_WINDOW", lambda: None)
            app.title(t("app.closing_title"))
            app.tab_console.append_log(
                f"[Système] {t('app.closing_log')}")
            server_manager.stop_server()

            def _wait_and_close():
                if server_manager.process:
                    try:
                        server_manager.process.wait(timeout=30)
                    except Exception:
                        pass
                app.after(0, _final_close, app, system_monitor, server_manager)

            threading.Thread(target=_wait_and_close, daemon=True).start()
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
