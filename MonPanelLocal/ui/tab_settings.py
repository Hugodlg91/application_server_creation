import customtkinter as ctk
from core.i18n import t
from core import i18n

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
                 on_stop_scheduler=None, on_save_lang_callback=None, **kwargs):
        super().__init__(master, fg_color=BG, **kwargs)
        self.on_save_callback = on_save_callback
        self.on_load_perf_callback = on_load_perf_callback
        self.on_save_perf_callback = on_save_perf_callback
        self.on_start_scheduler = on_start_scheduler
        self.on_stop_scheduler = on_stop_scheduler
        self.on_save_lang_callback = on_save_lang_callback

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

        # ── Section : Langue ─────────────────────────────────────────────────
        self._build_lang_section()

        # Pré-remplissage config perf
        perf = self.on_load_perf_callback()
        self.option_ram.set(f"{perf['ram_mb']} Mo")
        if perf["aikar_flags"]:
            self.switch_aikar.select()
        else:
            self.switch_aikar.deselect()

        self.after(200, lambda: self._bind_mousewheel(self.scroll_container))

    # ── Constructeurs de sections ─────────────────────────────────────────────

    def _make_section_card(self, title_key, icon=""):
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

        ctk.CTkLabel(hdr, text=t(title_key).upper(),
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=SUB
                     ).pack(side="left")

        return card

    def _build_properties_section(self):
        card = self._make_section_card("settings.section_server")

        self.entries = {}
        # (config key → i18n key)
        properties = {
            "server-port":  "settings.port",
            "max-players":  "settings.max_players",
            "motd":         "settings.motd",
            "difficulty":   "settings.difficulty",
            "gamemode":     "settings.gamemode",
        }

        for row_i, (key, i18n_key) in enumerate(properties.items(), start=1):
            ctk.CTkLabel(card, text=t(i18n_key), text_color=SUB,
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
            card, text=t("settings.save"),
            fg_color=ACCENT, hover_color=ACCENT2,
            command=self._on_save_clicked)
        self.btn_save.grid(row=row_save, column=0, columnspan=2,
                           padx=14, pady=(10, 6), sticky="e")

        self.lbl_status = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=11))
        self.lbl_status.grid(row=row_save + 1, column=0, columnspan=2,
                             padx=14, pady=(0, 12))

    def _build_perf_section(self):
        self.frm_perf = self._make_section_card("settings.section_perf")
        self.frm_perf.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frm_perf, text=t("settings.ram"),
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
            text=t("settings.aikar"),
            text_color=TEXT, progress_color=ACCENT, button_color=TEXT)
        self.switch_aikar.grid(row=2, column=0, columnspan=2,
                               padx=14, pady=(6, 2), sticky="w")

        ctk.CTkLabel(self.frm_perf, text=t("settings.aikar_desc"),
                     text_color=SUB, font=ctk.CTkFont(size=11)
                     ).grid(row=3, column=0, columnspan=2,
                            padx=14, pady=(0, 6), sticky="w")

        self.btn_save_perf = ctk.CTkButton(
            self.frm_perf, text=t("settings.save_perf"),
            fg_color=ACCENT, hover_color=ACCENT2,
            command=self._on_save_perf_clicked)
        self.btn_save_perf.grid(row=4, column=0, columnspan=2,
                                padx=14, pady=(6, 6), sticky="e")

        self.lbl_perf_status = ctk.CTkLabel(self.frm_perf, text="",
                                            font=ctk.CTkFont(size=11))
        self.lbl_perf_status.grid(row=5, column=0, columnspan=2,
                                  padx=14, pady=(0, 12))

    def _build_scheduler_section(self):
        self.frm_scheduler = self._make_section_card("settings.section_scheduler")
        self.frm_scheduler.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frm_scheduler, text=t("settings.scheduler_msg"),
                     text_color=SUB, font=ctk.CTkFont(size=12)
                     ).grid(row=1, column=0, padx=14, pady=5, sticky="w")
        self.entry_scheduler_msg = ctk.CTkEntry(
            self.frm_scheduler,
            placeholder_text=t("settings.scheduler_msg_placeholder"),
            fg_color=BG, border_color=BORDER, text_color=TEXT,
            placeholder_text_color=MUTED)
        self.entry_scheduler_msg.grid(row=1, column=1, padx=(0, 14),
                                      pady=5, sticky="ew")

        ctk.CTkLabel(self.frm_scheduler, text=t("settings.scheduler_interval"),
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
            text=t("settings.scheduler_enable"),
            text_color=TEXT, progress_color=ACCENT, button_color=TEXT,
            command=self._on_scheduler_toggled)
        self.switch_scheduler.grid(row=3, column=0, columnspan=2,
                                   padx=14, pady=(6, 14), sticky="w")

    def _build_lang_section(self):
        self.frm_lang = self._make_section_card("settings.section_lang")
        self.frm_lang.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frm_lang, text=t("settings.lang_label"),
                     text_color=SUB, font=ctk.CTkFont(size=12)
                     ).grid(row=1, column=0, padx=14, pady=(10, 5), sticky="w")

        # Map display → lang code
        self._lang_map = {"Français": "fr", "English": "en"}
        current_display = "English" if i18n.get_lang() == "en" else "Français"

        self.option_lang = ctk.CTkOptionMenu(
            self.frm_lang,
            values=["Français", "English"],
            fg_color=BG, button_color=ACCENT,
            button_hover_color=ACCENT2, text_color=TEXT,
            dropdown_fg_color=SURFACE, dropdown_text_color=TEXT,
            dropdown_hover_color=BORDER,
            command=self._on_lang_changed)
        self.option_lang.set(current_display)
        self.option_lang.grid(row=1, column=1, padx=(0, 14), pady=(10, 5), sticky="w")

        self.lbl_lang_notice = ctk.CTkLabel(
            self.frm_lang, text="",
            font=ctk.CTkFont(size=11), text_color=MUTED)
        self.lbl_lang_notice.grid(row=2, column=0, columnspan=2,
                                  padx=14, pady=(0, 12))

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
            self.lbl_status.configure(text=t("settings.saved_ok"), text_color=GREEN)
        else:
            self.lbl_status.configure(text=t("settings.save_error"), text_color=RED)
        self.after(3000, lambda: self.lbl_status.configure(text=""))

    def _on_save_perf_clicked(self):
        ram_str = self.option_ram.get()
        ram_mb = int(ram_str.split()[0])
        aikar = self.switch_aikar.get() == 1
        success = self.on_save_perf_callback(ram_mb, aikar)
        if success:
            self.lbl_perf_status.configure(
                text=t("settings.perf_saved_ok"), text_color=GREEN)
        else:
            self.lbl_perf_status.configure(
                text=t("settings.perf_save_error"), text_color=RED)
        self.after(3000, lambda: self.lbl_perf_status.configure(text=""))

    def _on_scheduler_toggled(self):
        if self.switch_scheduler.get() == 1:
            if self.on_start_scheduler:
                msg = self.entry_scheduler_msg.get().strip() or t("settings.scheduler_msg_placeholder")
                interval = int(self.option_scheduler_interval.get().split()[0])
                self.on_start_scheduler(msg, interval)
        else:
            if self.on_stop_scheduler:
                self.on_stop_scheduler()

    def _on_lang_changed(self, display_value):
        lang = self._lang_map.get(display_value, "fr")
        i18n.set_lang(lang)
        if self.on_save_lang_callback:
            self.on_save_lang_callback(lang)
        # Message bilingue — la langue vient juste de changer
        notice_fr = "Redémarrez l'application pour appliquer."
        notice_en = "Restart the application to apply."
        self.lbl_lang_notice.configure(
            text=notice_en if lang == "en" else notice_fr,
            text_color=MUTED)
