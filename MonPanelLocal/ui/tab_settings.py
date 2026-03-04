import customtkinter as ctk

class TabSettings(ctk.CTkFrame):
    """
    Onglet de configuration pour modifier server.properties de la version active.
    """
    def __init__(self, master, on_save_callback, on_load_perf_callback, on_save_perf_callback,
                 on_start_scheduler=None, on_stop_scheduler=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_save_callback = on_save_callback
        self.on_load_perf_callback = on_load_perf_callback
        self.on_save_perf_callback = on_save_perf_callback
        self.on_start_scheduler = on_start_scheduler
        self.on_stop_scheduler = on_stop_scheduler

        self.scroll_container = ctk.CTkScrollableFrame(self)
        self.scroll_container.pack(fill="both", expand=True)
        self.scroll_container.grid_columnconfigure(1, weight=1)

        self.lbl_title = ctk.CTkLabel(self.scroll_container, text="Paramètres du Serveur (server.properties)", font=("Arial", 16, "bold"))
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
            lbl = ctk.CTkLabel(self.scroll_container, text=label_text)
            lbl.grid(row=self.row_idx, column=0, padx=10, pady=5, sticky="w")

            entry = ctk.CTkEntry(self.scroll_container)
            entry.grid(row=self.row_idx, column=1, padx=10, pady=5, sticky="ew")
            self.entries[key] = entry
            self.row_idx += 1

        self.btn_save = ctk.CTkButton(self.scroll_container, text="Sauvegarder", command=self._on_save_clicked)
        self.btn_save.grid(row=self.row_idx, column=0, columnspan=2, pady=20)

        self.lbl_status = ctk.CTkLabel(self.scroll_container, text="")
        self.lbl_status.grid(row=self.row_idx + 1, column=0, columnspan=2)

        # === Section Performances ===
        self.frm_perf = ctk.CTkFrame(self.scroll_container, corner_radius=8)
        self.frm_perf.grid(row=self.row_idx + 2, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="ew")
        self.frm_perf.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frm_perf, text="⚙️ Performances du Serveur", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w"
        )

        ctk.CTkLabel(self.frm_perf, text="RAM allouée :").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.option_ram = ctk.CTkOptionMenu(
            self.frm_perf,
            values=["512 Mo", "1024 Mo", "2048 Mo", "4096 Mo", "6144 Mo", "8192 Mo"]
        )
        self.option_ram.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.switch_aikar = ctk.CTkSwitch(self.frm_perf, text="Activer les optimisations Aikar Flags")
        self.switch_aikar.grid(row=2, column=0, columnspan=2, padx=10, pady=(5, 0), sticky="w")

        ctk.CTkLabel(
            self.frm_perf,
            text="Réduit les lags et optimise le garbage collector Java",
            text_color="gray"
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

        self.btn_save_perf = ctk.CTkButton(
            self.frm_perf, text="💾 Sauvegarder les performances", command=self._on_save_perf_clicked
        )
        self.btn_save_perf.grid(row=4, column=0, columnspan=2, padx=10, pady=(5, 5))

        self.lbl_perf_status = ctk.CTkLabel(self.frm_perf, text="")
        self.lbl_perf_status.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # === Section Planificateur ===
        self.frm_scheduler = ctk.CTkFrame(self.scroll_container, corner_radius=8)
        self.frm_scheduler.grid(row=self.row_idx + 3, column=0, columnspan=2, padx=10, pady=(10, 10), sticky="ew")
        self.frm_scheduler.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frm_scheduler, text="📢 Planificateur de Messages", font=("Arial", 14, "bold")).grid(
            row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w"
        )

        ctk.CTkLabel(self.frm_scheduler, text="Message :").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_scheduler_msg = ctk.CTkEntry(self.frm_scheduler, placeholder_text="Bienvenue sur le serveur !")
        self.entry_scheduler_msg.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.frm_scheduler, text="Intervalle :").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.option_scheduler_interval = ctk.CTkOptionMenu(
            self.frm_scheduler,
            values=["5 min", "10 min", "15 min", "30 min", "60 min"]
        )
        self.option_scheduler_interval.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.switch_scheduler = ctk.CTkSwitch(
            self.frm_scheduler, text="Activer le planificateur", command=self._on_scheduler_toggled
        )
        self.switch_scheduler.grid(row=3, column=0, columnspan=2, padx=10, pady=(5, 10), sticky="w")

        # Pré-remplissage avec la config sauvegardée
        perf = self.on_load_perf_callback()
        self.option_ram.set(f"{perf['ram_mb']} Mo")
        if perf["aikar_flags"]:
            self.switch_aikar.select()
        else:
            self.switch_aikar.deselect()

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

    def _on_scheduler_toggled(self):
        if self.switch_scheduler.get() == 1:
            if self.on_start_scheduler:
                msg = self.entry_scheduler_msg.get().strip() or "Bienvenue sur le serveur !"
                interval_str = self.option_scheduler_interval.get()  # ex: "15 min"
                interval = int(interval_str.split()[0])
                self.on_start_scheduler(msg, interval)
        else:
            if self.on_stop_scheduler:
                self.on_stop_scheduler()

    def _on_save_perf_clicked(self):
        ram_str = self.option_ram.get()  # ex: "2048 Mo"
        ram_mb = int(ram_str.split()[0])
        aikar = self.switch_aikar.get() == 1
        success = self.on_save_perf_callback(ram_mb, aikar)
        if success:
            self.lbl_perf_status.configure(text="Performances sauvegardées !", text_color="green")
            self.after(3000, lambda: self.lbl_perf_status.configure(text=""))
        else:
            self.lbl_perf_status.configure(text="Erreur lors de la sauvegarde.", text_color="red")
            self.after(3000, lambda: self.lbl_perf_status.configure(text=""))
