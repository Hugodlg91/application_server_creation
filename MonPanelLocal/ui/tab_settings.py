import customtkinter as ctk

BG       = "#0f172a"
SURFACE  = "#1e293b"
BORDER   = "#334155"
MUTED    = "#475569"
TEXT     = "#e2e8f0"
SUB      = "#94a3b8"
ACCENT   = "#6366f1"
ACCENT2  = "#8b5cf6"
GREEN    = "#4ade80"
RED      = "#ef4444"

ACCENT_TINT = "#1e2256"


class TabSettings(ctk.CTkFrame):
    """
    Onglet de configuration — server.properties + performances + planificateur.
    """

    def __init__(self, master, on_save_callback, on_load_perf_callback,
                 on_save_perf_callback, on_start_scheduler=None,
                 on_stop_scheduler=None, **kwargs):
        super().__init__(master, fg_color=BG, **kwargs)
        self.on_save_callback = on_save_callback
        self.on_load_perf_callback = on_load_perf_callback
        self.on_save_perf_callback = on_save_perf_callback
        self.on_start_scheduler = on_start_scheduler
        self.on_stop_scheduler = on_stop_scheduler

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(
            self, fg_color=BG,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=MUTED)
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        # ── Section : Paramètres du serveur ──────────────────────────────────
        self._build_properties_section()

        # ── Section : Performances ───────────────────────────────────────────
        self._build_perf_section()

        # ── Section : Planificateur ──────────────────────────────────────────
        self._build_scheduler_section()

        # Pré-remplissage config perf
        perf = self.on_load_perf_callback()
        self.option_ram.set(f"{perf['ram_mb']} Mo")
        if perf["aikar_flags"]:
            self.switch_aikar.select()
        else:
            self.switch_aikar.deselect()

        self.after(200, lambda: self._bind_mousewheel(self.scroll_container))

    # ── Constructeurs de sections ─────────────────────────────────────────────

    def _make_section_card(self, title, icon=""):
        """Crée un cadre SURFACE avec titre de section et badge icône optionnel."""
        card = ctk.CTkFrame(self.scroll_container, fg_color=SURFACE,
                            border_color=BORDER, border_width=1,
                            corner_radius=10)
        card.grid(sticky="ew", padx=10, pady=(10, 4))
        card.grid_columnconfigure(1, weight=1)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=2, padx=14, pady=(12, 6), sticky="w")

        if icon:
            ctk.CTkLabel(hdr, text=icon,
                         font=ctk.CTkFont(size=14), text_color=ACCENT
                         ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(hdr, text=title.upper(),
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=SUB
                     ).pack(side="left")

        return card

    def _build_properties_section(self):
        card = self._make_section_card("Paramètres du serveur")

        self.entries = {}
        properties = {
            "server-port":  "Port du serveur",
            "max-players":  "Joueurs maximum",
            "motd":         "Message du jour (MOTD)",
            "difficulty":   "Difficulté",
            "gamemode":     "Mode de jeu",
        }

        for row_i, (key, label_text) in enumerate(properties.items(), start=1):
            ctk.CTkLabel(card, text=label_text, text_color=SUB,
                         font=ctk.CTkFont(size=12), width=210, anchor="w"
                         ).grid(row=row_i, column=0, padx=(14, 6),
                                pady=5, sticky="w")
            entry = ctk.CTkEntry(card, fg_color=BG, border_color=BORDER,
                                 text_color=TEXT)
            entry.grid(row=row_i, column=1, padx=(0, 14), pady=5, sticky="ew")
            self.entries[key] = entry

        # Bouton + statut
        row_save = len(properties) + 1
        self.btn_save = ctk.CTkButton(
            card, text="Sauvegarder",
            fg_color=ACCENT, hover_color=ACCENT2,
            command=self._on_save_clicked)
        self.btn_save.grid(row=row_save, column=0, columnspan=2,
                           padx=14, pady=(10, 6), sticky="e")

        self.lbl_status = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=11))
        self.lbl_status.grid(row=row_save + 1, column=0, columnspan=2,
                             padx=14, pady=(0, 12))

    def _build_perf_section(self):
        self.frm_perf = self._make_section_card("Performances du serveur")
        self.frm_perf.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frm_perf, text="RAM allouée",
                     text_color=SUB, font=ctk.CTkFont(size=12)
                     ).grid(row=1, column=0, padx=14, pady=5, sticky="w")
        self.option_ram = ctk.CTkOptionMenu(
            self.frm_perf,
            values=["512 Mo", "1024 Mo", "2048 Mo", "4096 Mo", "6144 Mo", "8192 Mo"],
            fg_color=BG, button_color=ACCENT,
            button_hover_color=ACCENT2, text_color=TEXT,
            dropdown_fg_color=SURFACE, dropdown_text_color=TEXT,
            dropdown_hover_color=BORDER)
        self.option_ram.grid(row=1, column=1, padx=(0, 14), pady=5, sticky="w")

        self.switch_aikar = ctk.CTkSwitch(
            self.frm_perf,
            text="Activer les optimisations Aikar Flags",
            text_color=TEXT, progress_color=ACCENT, button_color=TEXT)
        self.switch_aikar.grid(row=2, column=0, columnspan=2,
                               padx=14, pady=(6, 2), sticky="w")

        ctk.CTkLabel(self.frm_perf,
                     text="Réduit les lags et optimise le garbage collector Java",
                     text_color=SUB, font=ctk.CTkFont(size=11)
                     ).grid(row=3, column=0, columnspan=2,
                            padx=14, pady=(0, 6), sticky="w")

        self.btn_save_perf = ctk.CTkButton(
            self.frm_perf, text="Sauvegarder les performances",
            fg_color=ACCENT, hover_color=ACCENT2,
            command=self._on_save_perf_clicked)
        self.btn_save_perf.grid(row=4, column=0, columnspan=2,
                                padx=14, pady=(6, 6), sticky="e")

        self.lbl_perf_status = ctk.CTkLabel(self.frm_perf, text="",
                                            font=ctk.CTkFont(size=11))
        self.lbl_perf_status.grid(row=5, column=0, columnspan=2,
                                  padx=14, pady=(0, 12))

    def _build_scheduler_section(self):
        self.frm_scheduler = self._make_section_card("Planificateur de messages")
        self.frm_scheduler.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frm_scheduler, text="Message",
                     text_color=SUB, font=ctk.CTkFont(size=12)
                     ).grid(row=1, column=0, padx=14, pady=5, sticky="w")
        self.entry_scheduler_msg = ctk.CTkEntry(
            self.frm_scheduler,
            placeholder_text="Bienvenue sur le serveur !",
            fg_color=BG, border_color=BORDER, text_color=TEXT,
            placeholder_text_color=MUTED)
        self.entry_scheduler_msg.grid(row=1, column=1, padx=(0, 14),
                                      pady=5, sticky="ew")

        ctk.CTkLabel(self.frm_scheduler, text="Intervalle",
                     text_color=SUB, font=ctk.CTkFont(size=12)
                     ).grid(row=2, column=0, padx=14, pady=5, sticky="w")
        self.option_scheduler_interval = ctk.CTkOptionMenu(
            self.frm_scheduler,
            values=["5 min", "10 min", "15 min", "30 min", "60 min"],
            fg_color=BG, button_color=ACCENT,
            button_hover_color=ACCENT2, text_color=TEXT,
            dropdown_fg_color=SURFACE, dropdown_text_color=TEXT,
            dropdown_hover_color=BORDER)
        self.option_scheduler_interval.grid(row=2, column=1, padx=(0, 14),
                                            pady=5, sticky="w")

        self.switch_scheduler = ctk.CTkSwitch(
            self.frm_scheduler,
            text="Activer le planificateur",
            text_color=TEXT, progress_color=ACCENT, button_color=TEXT,
            command=self._on_scheduler_toggled)
        self.switch_scheduler.grid(row=3, column=0, columnspan=2,
                                   padx=14, pady=(6, 14), sticky="w")

    # ── Scroll molette ───────────────────────────────────────────────────────

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>",   self._on_mousewheel)
        widget.bind("<Button-5>",   self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.scroll_container._parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.scroll_container._parent_canvas.yview_scroll(1, "units")
        else:
            self.scroll_container._parent_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units")

    # ── API publique ─────────────────────────────────────────────────────────

    def update_form(self, current_config):
        for key, entry in self.entries.items():
            entry.delete(0, "end")
            if key in current_config:
                entry.insert(0, current_config[key])

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _on_save_clicked(self):
        new_config = {k: e.get().strip()
                      for k, e in self.entries.items() if e.get().strip()}
        success = self.on_save_callback(new_config)
        if success:
            self.lbl_status.configure(
                text="Configuration sauvegardée !", text_color=GREEN)
        else:
            self.lbl_status.configure(
                text="Veuillez d'abord initialiser le serveur.", text_color=RED)
        self.after(3000, lambda: self.lbl_status.configure(text=""))

    def _on_save_perf_clicked(self):
        ram_str = self.option_ram.get()
        ram_mb = int(ram_str.split()[0])
        aikar = self.switch_aikar.get() == 1
        success = self.on_save_perf_callback(ram_mb, aikar)
        if success:
            self.lbl_perf_status.configure(
                text="Performances sauvegardées !", text_color=GREEN)
        else:
            self.lbl_perf_status.configure(
                text="Erreur lors de la sauvegarde.", text_color=RED)
        self.after(3000, lambda: self.lbl_perf_status.configure(text=""))

    def _on_scheduler_toggled(self):
        if self.switch_scheduler.get() == 1:
            if self.on_start_scheduler:
                msg = self.entry_scheduler_msg.get().strip() or "Bienvenue sur le serveur !"
                interval = int(self.option_scheduler_interval.get().split()[0])
                self.on_start_scheduler(msg, interval)
        else:
            if self.on_stop_scheduler:
                self.on_stop_scheduler()
