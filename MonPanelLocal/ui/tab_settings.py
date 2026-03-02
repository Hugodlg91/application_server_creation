import customtkinter as ctk

class TabSettings(ctk.CTkFrame):
    """
    Onglet de configuration pour modifier server.properties de la version active.
    """
    def __init__(self, master, on_save_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_save_callback = on_save_callback
        self.grid_columnconfigure(1, weight=1)
        
        self.lbl_title = ctk.CTkLabel(self, text="Paramètres du Serveur (server.properties)", font=("Arial", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.entries = {}
        self.properties_to_show = {
            "server-port": "Port du serveur",
            "max-players": "Joueurs maximum",
            "motd": "Message du jour (MOTD)",
            "difficulty": "Difficulté (peaceful, easy, normal, hard)",
            "gamemode": "Mode de jeu (survival, creative, adventure)"
        }
        
        self.status_lbl_row = len(self.properties_to_show) + 2
        
        # Build UI structure empty first
        self.row_idx = 1
        for key, label_text in self.properties_to_show.items():
            lbl = ctk.CTkLabel(self, text=label_text)
            lbl.grid(row=self.row_idx, column=0, padx=10, pady=5, sticky="w")
            
            entry = ctk.CTkEntry(self)
            entry.grid(row=self.row_idx, column=1, padx=10, pady=5, sticky="ew")
            self.entries[key] = entry
            self.row_idx += 1
            
        self.btn_save = ctk.CTkButton(self, text="Sauvegarder", command=self._on_save_clicked)
        self.btn_save.grid(row=self.row_idx, column=0, columnspan=2, pady=20)
        
        self.lbl_status = ctk.CTkLabel(self, text="")
        self.lbl_status.grid(row=self.row_idx+1, column=0, columnspan=2)

    def update_form(self, current_config):
        """Met à jour les champs du formulaire avec la nouvelle config."""
        for key, entry in self.entries.items():
            entry.delete(0, "end")
            if key in current_config:
                entry.insert(0, current_config[key])

    def _on_save_clicked(self):
        new_config = {}
        for key, entry in self.entries.items():
            val = entry.get().strip()
            if val:
                new_config[key] = val
                
        success = self.on_save_callback(new_config)
        
        if success:
            self.lbl_status.configure(text="Configuration sauvegardée !", text_color="green")
            self.after(3000, lambda: self.lbl_status.configure(text=""))
        else:
            self.lbl_status.configure(text="Veuillez d'abord initialiser le serveur.", text_color="red")
            self.after(3000, lambda: self.lbl_status.configure(text=""))
