import threading
import time
import psutil

class SystemMonitor:
    """
    Surveille l'utilisation du CPU et de la RAM (tête de l'ordinateur hébergeant local).
    Passe les informations au frontend avec un callback.
    """
    def __init__(self, on_update_callback):
        self.on_update_callback = on_update_callback
        self.running = False
        self.thread = None

    def start(self):
        """Lance la boucle de monitoring."""
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Arrête le monitoring proprement."""
        self.running = False
        
    def _monitor_loop(self):
        # Initial call cache init
        psutil.cpu_percent(interval=0.1)
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=None) # pas de délai de thread pour ne pas bloquer
                ram = psutil.virtual_memory().percent
                if self.on_update_callback:
                    self.on_update_callback(cpu, ram)
            except Exception:
                pass
            time.sleep(1) # Mise à jour toutes les secondes
