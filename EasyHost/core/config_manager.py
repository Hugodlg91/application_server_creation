import os
import sys
import json


def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigManager:
    """
    Gère la lecture et modification propre du fichier server.properties.
    """
    def __init__(self):
        self.base_dir = _get_base_dir()
        self.properties_path = None
        
    def set_version(self, server_type, version):
        """Met à jour le chemin de config en fonction du type et de la version sélectionnés."""
        if not version: return
        server_dir = os.path.join(self.base_dir, f"minecraft_server_{server_type}_{version}")
        self.properties_path = os.path.join(server_dir, "server.properties")
        
    def read_config(self):
        """Lit le fichier server.properties de la version active et retourne un dictionnaire."""
        config = {}
        if not self.properties_path or not os.path.exists(self.properties_path):
            return config
            
        try:
            with open(self.properties_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        config[key.strip()] = val.strip()
            return config
        except Exception:
            return {}

    def save_config(self, modified_config):
        """Sauvegarde les propriétés tout en préservant l'ordre original et les commentaires."""
        if not self.properties_path: return False
        
        # S'assurer que le dossier parent existe
        os.makedirs(os.path.dirname(self.properties_path), exist_ok=True)
        
        if not os.path.exists(self.properties_path):
            with open(self.properties_path, "w", encoding="utf-8") as f:
                f.write("#Minecraft server properties\n")
                for k, v in modified_config.items():
                    f.write(f"{k}={v}\n")
            return True
            
        try:
            with open(self.properties_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            new_lines = []
            keys_processed = set()
            
            for line in lines:
                original_line = line.strip()
                if not original_line or original_line.startswith("#"):
                    new_lines.append(line)
                    continue
                    
                if "=" in original_line:
                    key = original_line.split("=", 1)[0].strip()
                    if key in modified_config:
                        new_lines.append(f"{key}={modified_config[key]}\n")
                        keys_processed.add(key)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            for k, v in modified_config.items():
                if k not in keys_processed:
                    new_lines.append(f"{k}={v}\n")
                    
            with open(self.properties_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
            
        except Exception:
            return False

    def load_performance_config(self):
        """Retourne la config de performances depuis panel_config.json."""
        path = os.path.join(self.base_dir, "panel_config.json")
        defaults = {"ram_mb": 1024, "aikar_flags": False}
        if not os.path.exists(path):
            return defaults
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"ram_mb": data.get("ram_mb", 1024), "aikar_flags": data.get("aikar_flags", False)}
        except Exception:
            return defaults

    def save_performance_config(self, ram_mb, aikar_flags):
        """Sauvegarde la config de performances sans écraser les autres clés de panel_config.json."""
        path = os.path.join(self.base_dir, "panel_config.json")
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data["ram_mb"] = ram_mb
        data["aikar_flags"] = aikar_flags
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load_server_type(self) -> str:
        """Retourne le type de serveur sauvegardé (défaut : 'PaperMC')."""
        path = os.path.join(self.base_dir, "panel_config.json")
        if not os.path.exists(path):
            return "PaperMC"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("server_type", "PaperMC")
        except Exception:
            return "PaperMC"

    def save_server_type(self, server_type: str):
        """Sauvegarde le type de serveur sans écraser les autres clés de panel_config.json."""
        path = os.path.join(self.base_dir, "panel_config.json")
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data["server_type"] = server_type
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load_lang(self) -> str:
        """Retourne la langue sauvegardée (défaut : 'fr')."""
        path = os.path.join(self.base_dir, "panel_config.json")
        if not os.path.exists(path):
            return "fr"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("lang", "fr")
        except Exception:
            return "fr"

    def save_lang(self, lang: str):
        """Sauvegarde la langue sans écraser les autres clés de panel_config.json."""
        path = os.path.join(self.base_dir, "panel_config.json")
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data["lang"] = lang
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass
