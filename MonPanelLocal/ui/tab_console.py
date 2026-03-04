import customtkinter as ctk

class TabConsole(ctk.CTkFrame):
    """
    Onglet contenant la console en direct et les contrôles du serveur pour la version choisie.
    """
    def __init__(self, master, on_start, on_stop, on_send_command, on_download,
                 on_version_change, on_type_change, on_bore_toggle=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_start = on_start
        self.on_stop = on_stop
        self.on_send_command = on_send_command
        self.on_download = on_download
        self.on_version_change = on_version_change
        self.on_type_change = on_type_change
        self.on_bore_toggle = on_bore_toggle

        self.command_history = []
        self.history_index = -1
        self._tags_ready = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # === Frame des contrôles haut ===
        self.frame_controls = ctk.CTkFrame(self)
        self.frame_controls.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Choix du type de serveur
        self.lbl_type = ctk.CTkLabel(self.frame_controls, text="Type:")
        self.lbl_type.pack(side="left", padx=(5,2), pady=5)

        self.option_type = ctk.CTkOptionMenu(
            self.frame_controls,
            values=["PaperMC", "Vanilla", "Fabric"],
            width=110
        )
        self.option_type.pack(side="left", padx=(0,5), pady=5)

        # Choix de la version
        self.lbl_version = ctk.CTkLabel(self.frame_controls, text="Version:")
        self.lbl_version.pack(side="left", padx=(5,2), pady=5)

        self.option_version = ctk.CTkComboBox(
            self.frame_controls,
            values=["Chargement..."],
            width=120,
            state="readonly",
            command=self._on_version_selected
        )
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

        # Status Label
        self.lbl_state = ctk.CTkLabel(self.frame_controls, text="Statut: Éteint", text_color="gray")
        self.lbl_state.pack(side="right", padx=10, pady=5)

        # Bouton Bore et IP
        self.btn_bore = ctk.CTkButton(self.frame_controls, text="🌐 Rendre Public (Bore)", fg_color="#1f538d", hover_color="#14375e", command=self._on_bore_clicked)
        self.btn_bore.pack(side="right", padx=5, pady=5)

        self.entry_bore_ip = ctk.CTkEntry(self.frame_controls, width=170, state="readonly", justify="center")

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
        self.entry_cmd.bind("<Up>", self._on_history_up)
        self.entry_cmd.bind("<Down>", self._on_history_down)

        self.btn_send = ctk.CTkButton(self.frame_input, text="Envoyer", command=self._on_send_clicked, state="disabled")
        self.btn_send.grid(row=0, column=1, padx=5, pady=5)

        # Câblage du type APRÈS création de tous les widgets (évite le callback prématuré sur Linux)
        self.option_type.configure(command=self._on_type_selected)

        # Configurer les tags couleur après le premier rendu (évite segfault Linux pré-mainloop)
        self.after(100, self._configure_log_tags)

    def _configure_log_tags(self):
        """Configure les tags de couleur sur le widget Text interne, après le démarrage de mainloop."""
        self.console_box._textbox.tag_configure("error", foreground="#f87171")
        self.console_box._textbox.tag_configure("warn", foreground="#fbbf24")
        self.console_box._textbox.tag_configure("system", foreground="#93c5fd")
        self.console_box._textbox.tag_configure("default", foreground="#e2e8f0")
        self._tags_ready = True

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

    def _on_type_selected(self, value):
        self.on_type_change(value)

    def set_loading_state(self, loading: bool):
        """Désactive les contrôles pendant le chargement des versions."""
        self.option_type.configure(state="disabled" if loading else "normal")
        self.option_version.configure(state="disabled" if loading else "readonly")
        if loading:
            self.option_version.configure(values=["Chargement..."])
            self.option_version.set("Chargement...")

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
        if self._tags_ready:
            if "ERROR" in text or "[Erreur]" in text:
                tag = "error"
            elif "WARN" in text or "WARNING" in text:
                tag = "warn"
            elif "[Système]" in text or "[Bore]" in text or "[Java]" in text:
                tag = "system"
            else:
                tag = "default"
            self.console_box.insert("end", text + "\n", tag)
        else:
            self.console_box.insert("end", text + "\n")
        self.console_box.see("end")

    def set_running_state(self, is_running):
        """Désactive la sélection pendant que le serveur tourne."""
        if is_running:
            self.option_version.configure(state="disabled")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.btn_send.configure(state="normal")
            self.lbl_state.configure(text="Statut: En Ligne", text_color="green")
        else:
            self.option_version.configure(state="readonly")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_send.configure(state="disabled")
            self.lbl_state.configure(text="Statut: Éteint", text_color="red")

    def set_bore_state(self, is_running, ip=""):
        """Met à jour l'apparence du bouton Bore et affiche l'IP."""
        if is_running:
            self.btn_bore.configure(text="🔴 Désactiver le tunnel", fg_color="red", hover_color="darkred")
            if ip:
                self.entry_bore_ip.pack(side="right", padx=5, pady=5, before=self.btn_bore)
                self.entry_bore_ip.configure(state="normal")
                self.entry_bore_ip.delete(0, "end")
                self.entry_bore_ip.insert(0, ip)
                self.entry_bore_ip.configure(state="readonly")
        else:
            self.btn_bore.configure(text="🌐 Rendre Public (Bore)", fg_color="#1f538d", hover_color="#14375e")
            self.entry_bore_ip.pack_forget()

    def _on_start_clicked(self):
        self.on_start()

    def _on_stop_clicked(self):
        self.on_stop()

    def _on_download_clicked(self):
        self.btn_install.configure(state="disabled")
        self.option_version.configure(state="disabled")
        self.on_download()

    def _on_bore_clicked(self):
        if self.on_bore_toggle:
            self.on_bore_toggle()

    def _on_send_clicked(self, event=None):
        cmd = self.entry_cmd.get().strip()
        if cmd:
            self.command_history.insert(0, cmd)
            if len(self.command_history) > 50:
                self.command_history.pop()
            self.history_index = -1
            self.on_send_command(cmd)
            self.entry_cmd.delete(0, "end")

    def _on_history_up(self, event=None):
        if not self.command_history:
            return "break"
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
        self.entry_cmd.delete(0, "end")
        self.entry_cmd.insert(0, self.command_history[self.history_index])
        return "break"

    def _on_history_down(self, event=None):
        if self.history_index > 0:
            self.history_index -= 1
            self.entry_cmd.delete(0, "end")
            self.entry_cmd.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = -1
            self.entry_cmd.delete(0, "end")
        return "break"
