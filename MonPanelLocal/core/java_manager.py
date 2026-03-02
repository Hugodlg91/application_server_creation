import os
import requests
import tarfile
import zipfile
import platform
import shutil

class JavaManager:
    """
    Gère le téléchargement, l'extraction et l'utilisation de runtimes Java portables
    via l'API Adoptium v3 (Temurin).
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.runtimes_dir = os.path.join(self.base_dir, "runtimes")
        os.makedirs(self.runtimes_dir, exist_ok=True)

    def get_required_java_version(self, minecraft_version):
        """Retourne la version de Java requise selon la version de Minecraft."""
        if not minecraft_version:
            return 21 # Par défaut
            
        try:
            # Format standard "1.19.4"
            parts = minecraft_version.split('.')
            minor = int(parts[1])
            patch = int(parts[2]) if len(parts) > 2 else 0
            
            if minor <= 16:
                return 8
            elif minor == 17:
                return 16
            elif minor >= 18 and minor <= 20 and patch < 5:
                # 1.18, 1.19, 1.20.0 to 1.20.4
                return 17
            else:
                return 21
        except Exception:
            # Fallback en cas de snapshot ou format étrange
            return 21

    def _get_os_and_arch_for_adoptium(self):
        """Mappe la plateforme courante aux identifiants de l'API Adoptium."""
        os_name = platform.system().lower()
        if os_name == "darwin":
            os_name = "mac"
        elif "win" in os_name:
            os_name = "windows"
            
        machine = platform.machine().lower()
        arch = "x64"
        if "aarch64" in machine or "arm64" in machine:
            arch = "aarch64"
        elif "arm" in machine:
            arch = "arm"
        elif "86" in machine and not "64" in machine:
            arch = "x32"
            
        return os_name, arch

    def get_java_executable(self, java_version):
        """Retourne le chemin absolu vers l'exécutable java portable local s'il est validé."""
        target_dir = os.path.join(self.runtimes_dir, f"java_{java_version}")
        
        # Le contenu téléchargé d'Adoptium a souvent un dosser racine (ex: jdk-17.0.2+8-jre/)
        # On doit chercher récursivement "bin/java" ou "bin/java.exe"
        exe_name = "java.exe" if platform.system().lower() == "windows" else "java"
        
        if not os.path.exists(target_dir):
            return None
            
        for root, dirs, files in os.walk(target_dir):
            if exe_name in files and os.path.basename(root) == "bin":
                return os.path.join(root, exe_name)
                
        return None

    def ensure_java(self, java_version, on_log_callback=None):
        """
        Vérifie si Java est présent, sinon le télécharge et l'extrait.
        Retourne True en cas de succès, False sinon.
        Note: Le téléchargement de Java est bloquant pour le démarrage serveur (doit s'exécuter dans le thread).
        """
        # Vérification si l'exécutable existe déjà
        if self.get_java_executable(java_version):
            return True

        # Si introuvable, il faut le télécharger
        if on_log_callback:
            on_log_callback(f"[Java] Téléchargement du JRE (Java {java_version}) requis...")

        os_name, arch = self._get_os_and_arch_for_adoptium()
        asset_url = f"https://api.adoptium.net/v3/binary/latest/{java_version}/ga/{os_name}/{arch}/jre/hotspot/normal/eclipse"
        
        # Le nom du fichier téléchargé dépend de l'OS (tar.gz sous linux/mac, zip sous windows)
        extension = "zip" if os_name == "windows" else "tar.gz"
        archive_path = os.path.join(self.runtimes_dir, f"temp_java_{java_version}.{extension}")
        target_dir = os.path.join(self.runtimes_dir, f"java_{java_version}")
        
        try:
            # 1. Téléchargement streaming (bloque dans le thread courant de démarrage)
            with requests.get(asset_url, stream=True, timeout=20) as r:
                r.raise_for_status()
                with open(archive_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            if on_log_callback:
                on_log_callback(f"[Java] Extraction du JRE en cours...")

            # 2. Extraction
            os.makedirs(target_dir, exist_ok=True)
            if extension == "zip":
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
            else:
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(target_dir)

            # 3. Nettoyage et permissions
            os.remove(archive_path)
            
            # Sous linux/mac on s'assure que le binaire a les droits d'exécution
            if os_name != "windows":
                exe_path = self.get_java_executable(java_version)
                if exe_path:
                    os.chmod(exe_path, 0o755)

            if on_log_callback:
                on_log_callback(f"[Java] Runtime installé avec succès ! ({target_dir})")
            return True
            
        except Exception as e:
            if on_log_callback:
                on_log_callback(f"[Java] Erreur lors de l'acquisition du JRE {java_version} : {e}")
            # Nettoyage en cas de fail
            if os.path.exists(archive_path):
                try: os.remove(archive_path)
                except: pass
            return False
