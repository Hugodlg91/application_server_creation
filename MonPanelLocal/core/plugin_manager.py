import os
import requests
import threading

class PluginManager:
    def __init__(self):
        self.base_url = "https://api.modrinth.com/v2"
        self.headers = {"User-Agent": "MonPanelLocal/1.0 (contact@example.com)"}

    def search_plugins(self, query, callback_success, callback_error):
        def _search():
            try:
                url = f"{self.base_url}/search"
                params = {
                    "query": query,
                    "facets": '[["categories:paper"]]',
                    "limit": 20
                }
                response = requests.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for hit in data.get("hits", []):
                    results.append({
                        "title": hit.get("title", "Unknown"),
                        "description": hit.get("description", ""),
                        "project_id": hit.get("project_id")
                    })
                
                if callback_success:
                    callback_success(results)
                    
            except Exception as e:
                print(f"[PluginManager] Search error: {e}")
                if callback_error:
                    callback_error(str(e))
                    
        threading.Thread(target=_search, daemon=True).start()

    def download_plugin(self, project_id, server_version, server_dir, progress_callback, finish_callback):
        def _download():
            try:
                # 1. Trouver la version compatible
                url = f"{self.base_url}/project/{project_id}/version"
                params = {
                    "loaders": '["paper"]',
                    "game_versions": f'["{server_version}"]'
                }
                
                response = requests.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                versions = response.json()
                
                if not versions:
                    if finish_callback: finish_callback(False)
                    return
                
                # Prendre la version la plus récente compatible
                latest_version = versions[0]
                files = latest_version.get("files", [])
                
                jar_file = None
                for f in files:
                    if f["filename"].endswith(".jar") and f.get("primary"):
                        jar_file = f
                        break
                
                if not jar_file:
                    for f in files:
                        if f["filename"].endswith(".jar"):
                            jar_file = f
                            break
                            
                if not jar_file:
                    if finish_callback: finish_callback(False)
                    return
                
                download_url = jar_file["url"]
                filename = jar_file["filename"]
                
                # 2. Créer le dossier plugins/
                plugins_dir = os.path.join(server_dir, "plugins")
                os.makedirs(plugins_dir, exist_ok=True)
                
                filepath = os.path.join(plugins_dir, filename)
                
                # 3. Télécharger le fichier
                dl_response = requests.get(download_url, stream=True, headers=self.headers)
                dl_response.raise_for_status()
                
                total_size = int(dl_response.headers.get("content-length", 0))
                downloaded_size = 0
                
                with open(filepath, "wb") as f:
                    for chunk in dl_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            if total_size > 0 and progress_callback:
                                percent = downloaded_size / total_size
                                progress_callback(percent)
                                
                if finish_callback:
                    finish_callback(True)
                    
            except Exception as e:
                print(f"[PluginManager] Download error: {e}")
                if finish_callback:
                    finish_callback(False)
                    
        threading.Thread(target=_download, daemon=True).start()
