import os
import requests
import threading

class Downloader:
    """
    Gère la récupération des versions et le téléchargement du .jar de PaperMC via son API v2 (requests).
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.api_url = "https://api.papermc.io/v2/projects/paper"
    
    def get_versions(self):
        """Récupère la liste des versions de Minecraft supportées par PaperMC."""
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            versions = data.get("versions", [])
            return list(reversed(versions)) # Les plus récentes d'abord
        except Exception:
            return []

    def download_version(self, version, on_log_callback=None, on_progress_callback=None, on_finish_callback=None):
        """Télécharge la dernière build PaperMC pour une version donnée avec suivi de progression."""
        if on_log_callback:
            on_log_callback(f"[Téléchargement] Recherche de la dernière build pour la version {version}...")
            
        def _download_task():
            try:
                # 1. Obtenir les builds de la version
                version_url = f"{self.api_url}/versions/{version}"
                resp = requests.get(version_url, timeout=5)
                resp.raise_for_status()
                data = resp.json()
                
                builds = data.get("builds", [])
                if not builds:
                    if on_log_callback: on_log_callback(f"[Téléchargement] Aucune build de PaperMC trouvée pour {version}.")
                    if on_finish_callback: on_finish_callback(False)
                    return
                
                latest_build = builds[-1]
                
                # 2. Obtenir le nom de fichier spécifique pour la build
                build_url = f"{self.api_url}/versions/{version}/builds/{latest_build}"
                resp2 = requests.get(build_url, timeout=5)
                resp2.raise_for_status()
                build_data = resp2.json()
                
                jar_name = build_data.get("downloads", {}).get("application", {}).get("name")
                
                if not jar_name:
                    if on_log_callback: on_log_callback("[Téléchargement] Erreur : Nom du fichier .jar introuvable.")
                    if on_finish_callback: on_finish_callback(False)
                    return
                
                # 3. Construire le chemin du répertoire minecraft_server_[version]
                server_dir = os.path.join(self.base_dir, f"minecraft_server_{version}")
                os.makedirs(server_dir, exist_ok=True)
                jar_path = os.path.join(server_dir, "server.jar")
                
                # 4. Télécharger le fichier par morceaux avec progression
                download_link = f"{self.api_url}/versions/{version}/builds/{latest_build}/downloads/{jar_name}"
                
                if on_log_callback: on_log_callback(f"[Téléchargement] Téléchargement de la version {version} (Build {latest_build}) en cours...")
                
                with requests.get(download_link, stream=True, timeout=10) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(jar_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0 and on_progress_callback:
                                on_progress_callback(downloaded / total_size)
                                
                if on_log_callback: on_log_callback(f"[Téléchargement] Succès ! Enregistré dans : minecraft_server_{version}/server.jar")
                if on_progress_callback: on_progress_callback(1.0)
                
                if on_finish_callback:
                    on_finish_callback(True)
                    
            except Exception as e:
                if on_log_callback: on_log_callback(f"[Téléchargement] Erreur réseau ou écriture : {e}")
                if on_finish_callback: on_finish_callback(False)

        # Lancer la tâche de manière asynchrone
        threading.Thread(target=_download_task, daemon=True).start()
