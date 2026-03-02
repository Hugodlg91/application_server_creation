import os

class ConfigManager:
    """
    Gère la lecture et modification propre du fichier server.properties.
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.properties_path = None
        
    def set_version(self, version):
        """Met à jour le chemin de config en fonction de la version sélectionnée."""
        if not version: return
        server_dir = os.path.join(self.base_dir, f"minecraft_server_{version}")
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
