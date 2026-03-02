import threading
from pyngrok import ngrok, conf

class TunnelManager:
    """
    Gère la création et la fermeture d'un tunnel TCP via ngrok
    pour rendre le serveur accessible depuis l'extérieur.
    """
    def __init__(self):
        self.active_tunnel = None
        
    def start_tunnel(self, port, callback_success, callback_error):
        def _start():
            try:
                # Ouvrir le tunnel TCP
                self.active_tunnel = ngrok.connect(port, "tcp")
                
                # Récupérer l'URL brute (ex: tcp://0.tcp.ngrok.io:12345)
                public_url = self.active_tunnel.public_url
                
                # Nettoyer l'URL
                if public_url.startswith("tcp://"):
                    public_url = public_url[6:]
                    
                if callback_success:
                    callback_success(public_url)
                    
            except Exception as e:
                print(f"[TunnelManager] Start error: {e}")
                if callback_error:
                    callback_error(str(e))
                    
        threading.Thread(target=_start, daemon=True).start()
        
    def stop_tunnel(self, callback_stopped=None):
        def _stop():
            try:
                if self.active_tunnel:
                    ngrok.disconnect(self.active_tunnel.public_url)
                    self.active_tunnel = None
                ngrok.kill()
                
                if callback_stopped:
                    callback_stopped()
                    
            except Exception as e:
                print(f"[TunnelManager] Stop error: {e}")
                if callback_stopped:
                    callback_stopped()
                    
        threading.Thread(target=_stop, daemon=True).start()
