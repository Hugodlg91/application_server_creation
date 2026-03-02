import customtkinter as ctk

class TabConsole(ctk.CTkFrame):
    """
    Onglet contenant la console en direct et les contrôles du serveur pour la version choisie.
    """
    def __init__(self, master, on_start, on_stop, on_send_command, on_download, on_version_change, on_tunnel_toggle=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_send_command = on_send_command
        self.on_download = on_download
        self.on_version_change = on_version_change
        self.on_tunnel_toggle = on_tunnel_toggle
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # === Frame des contrôles haut ===
        self.frame_controls = ctk.CTkFrame(self)
        self.frame_controls.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Choix de la version
        self.lbl_version = ctk.CTkLabel(self.frame_controls, text="Version:")
        self.lbl_version.pack(side="left", padx=(5,2), pady=5)
        
        self.option_version = ctk.CTkOptionMenu(self.frame_controls, values=["Chargement..."], command=self._on_version_selected)
        self.option_version.pack(side="left", padx=(0,5), pady=5)
        
        # Bouton Installer
        self.btn_install = ctk.CTkButton(self.frame_controls, text="Installer", fg_color="#1f538d", command=self._on_download_clicked)
        self.btn_install.pack(side="left", padx=5, pady=5)
        
        # Boutons Démarrer et Arrêter
        self.btn_start = ctk.CTkButton(self.frame_controls, text="Démarrer", fg_color="green", hover_color="darkgreen", command=self._on_start_clicked)
        self.btn_start.pack(side="left", padx=5, pady=5)
        self.btn_start.pack_forget() # Caché par défaut si non installé
        
        self.btn_stop = ctk.CTkButton(self.frame_controls, text="Arrêter", fg_color="red", hover_color="darkred", state="disabled", command=self._on_stop_clicked)
        self.btn_stop.pack(side="left", padx=5, pady=5)
        
        # Bouton Tunnel ngrok
        self.btn_tunnel = ctk.CTkButton(self.frame_controls, text="🌐 Rendre Public", fg_color="#6A0DAD", hover_color="#4B0082", command=self._on_tunnel_clicked)
        self.btn_tunnel.pack(side="right", padx=5, pady=5)
        
        # Tunnel IP (cachée par défaut)
        self.entry_tunnel_ip = ctk.CTkEntry(self.frame_controls, width=180, justify="center")
        
        # Status Label
        self.lbl_state = ctk.CTkLabel(self.frame_controls, text="Statut: Éteint", text_color="gray")
        self.lbl_state.pack(side="right", padx=10, pady=5)
        
        # === ProgressBar (Barre de téléchargement) ===
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid_remove() # Caché par défaut
        
        # === Textbox pour la console ===
        self.console_box = ctk.CTkTextbox(self, state="disabled", font=("Consolas", 12))
        self.console_box.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        # === Frame pour l'envoi de commandes (bas) ===
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.frame_input.grid_columnconfigure(0, weight=1)
        
        self.entry_cmd = ctk.CTkEntry(self.frame_input, placeholder_text="Entrez une commande (ex: say Hello)")
        self.entry_cmd.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="ew")
        self.entry_cmd.bind("<Return>", self._on_send_clicked) 
        
        self.btn_send = ctk.CTkButton(self.frame_input, text="Envoyer", command=self._on_send_clicked, state="disabled")
        self.btn_send.grid(row=0, column=1, padx=5, pady=5)

    def set_versions(self, versions):
        """Remplit le menu déroulant avec les versions récupérées."""
        if versions:
            self.option_version.configure(values=versions)
            self.option_version.set(versions[0])
            self.on_version_change(versions[0]) # Déclencher la sélection au lancement
        else:
            self.option_version.configure(values=["Erreur API"])
            self.option_version.set("Erreur API")
            self.btn_install.configure(state="disabled")

    def _on_version_selected(self, value):
        self.on_version_change(value)

    def update_install_state(self, is_installed):
        """Affiche Installer ou Démarrer selon si la version est déjà téléchargée."""
        if is_installed:
            self.btn_install.pack_forget()
            self.btn_start.pack(side="left", padx=5, pady=5, after=self.option_version)
        else:
            self.btn_start.pack_forget()
            self.btn_install.pack(side="left", padx=5, pady=5, after=self.option_version)

    def show_progress(self, show=True):
        if show:
            self.progress_bar.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")
            self.progress_bar.set(0)
        else:
            self.progress_bar.grid_remove()
            
    def update_progress(self, percent):
        self.progress_bar.set(percent)

    def append_log(self, text):
        self.console_box.configure(state="normal")
        self.console_box.insert("end", text + "\n")
        self.console_box.see("end")
        self.console_box.configure(state="disabled")

    def set_running_state(self, is_running):
        """Désactive la sélection pendant que le serveur tourne."""
        if is_running:
            self.option_version.configure(state="disabled")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.btn_send.configure(state="normal")
            self.lbl_state.configure(text="Statut: En Ligne", text_color="green")
        else:
            self.option_version.configure(state="normal")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_send.configure(state="disabled")
            self.lbl_state.configure(text="Statut: Éteint", text_color="red")
            
    def _on_start_clicked(self):
        self.on_start()
        
    def _on_stop_clicked(self):
        self.on_stop()
        
    def _on_download_clicked(self):
        self.btn_install.configure(state="disabled")
        self.option_version.configure(state="disabled")
        self.on_download()
        
    def _on_send_clicked(self, event=None):
        cmd = self.entry_cmd.get().strip()
        if cmd:
            self.on_send_command(cmd)
            self.entry_cmd.delete(0, "end")
            
    def _on_tunnel_clicked(self):
        if self.on_tunnel_toggle:
            self.on_tunnel_toggle()
            
    def set_tunnel_state(self, active, ip=""):
        if active:
            self.btn_tunnel.configure(text="🔴 Fermer l'accès", fg_color="red", hover_color="darkred")
            self.entry_tunnel_ip.pack(side="right", padx=5, pady=5, before=self.btn_tunnel)
            self.entry_tunnel_ip.configure(state="normal")
            self.entry_tunnel_ip.delete(0, "end")
            self.entry_tunnel_ip.insert(0, ip)
            self.entry_tunnel_ip.configure(state="readonly")
        else:
            self.btn_tunnel.configure(text="🌐 Rendre Public", fg_color="#6A0DAD", hover_color="#4B0082")
            self.entry_tunnel_ip.pack_forget()
