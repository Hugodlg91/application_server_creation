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

ACCENT_TINT = "#1e2256"
GREEN_TINT  = "#0d2a1a"


class TabPlugins(ctk.CTkFrame):
    def __init__(self, master, on_search_callback, on_install_callback, **kwargs):
        super().__init__(master, fg_color=BG, **kwargs)

        self.on_search_callback = on_search_callback
        self.on_install_callback = on_install_callback

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # === Barre de recherche ===
        self.frame_search = ctk.CTkFrame(self, fg_color=SURFACE,
                                         border_color=BORDER, border_width=1,
                                         corner_radius=8)
        self.frame_search.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self.frame_search.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_search, text="🔍",
                     font=ctk.CTkFont(size=15)
                     ).grid(row=0, column=0, padx=(14, 0), pady=10)

        self.entry_search = ctk.CTkEntry(
            self.frame_search,
            placeholder_text="Rechercher un plugin Modrinth...",
            fg_color=BG, border_color=BORDER,
            text_color=TEXT, placeholder_text_color=MUTED,
            height=36, border_width=0)
        self.entry_search.grid(row=0, column=1, padx=(6, 6), pady=10, sticky="ew")
        self.entry_search.bind("<Return>", lambda e: self._on_search_click())

        self.btn_search = ctk.CTkButton(
            self.frame_search, text="Rechercher", width=120, height=36,
            fg_color=ACCENT, hover_color=ACCENT2,
            command=self._on_search_click)
        self.btn_search.grid(row=0, column=2, padx=(0, 10), pady=10)

        # === Résultats ===
        self.scroll_results = ctk.CTkScrollableFrame(
            self, fg_color=BG,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=MUTED)
        self.scroll_results.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")
        self.scroll_results.grid_columnconfigure(0, weight=1)

        # === Barre de progression ===
        self.progress_bar = ctk.CTkProgressBar(
            self, height=4, corner_radius=0, border_width=0,
            progress_color=ACCENT, fg_color=BORDER)
        self.progress_bar.set(0)

        self._show_prompt_state()
        self.after(200, lambda: self._bind_mousewheel(self.scroll_results))

    # ── États illustrés ───────────────────────────────────────────────────────

    def _show_prompt_state(self):
        for w in self.scroll_results.winfo_children():
            w.destroy()
        frame = ctk.CTkFrame(self.scroll_results, fg_color="transparent")
        frame.grid(row=0, column=0, pady=60, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text="🧩",
                     font=ctk.CTkFont(size=48)
                     ).grid(row=0, column=0, pady=(0, 10))
        ctk.CTkLabel(frame, text="Trouver des plugins",
                     font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT
                     ).grid(row=1, column=0)
        ctk.CTkLabel(frame,
                     text="Recherchez sur Modrinth pour découvrir et installer des plugins.",
                     font=ctk.CTkFont(size=12), text_color=MUTED
                     ).grid(row=2, column=0, pady=(4, 0))

    def _show_no_results(self, query=""):
        frame = ctk.CTkFrame(self.scroll_results, fg_color="transparent")
        frame.grid(row=0, column=0, pady=60, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text="🔍",
                     font=ctk.CTkFont(size=40)
                     ).grid(row=0, column=0, pady=(0, 10))
        ctk.CTkLabel(frame, text="Aucun résultat",
                     font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT
                     ).grid(row=1, column=0)
        hint = f"Aucun plugin trouvé pour « {query} »." if query else "Essayez avec d'autres mots-clés."
        ctk.CTkLabel(frame, text=hint,
                     font=ctk.CTkFont(size=12), text_color=MUTED
                     ).grid(row=2, column=0, pady=(4, 0))

    # ── Scroll molette ────────────────────────────────────────────────────────

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>",   self._on_mousewheel)
        widget.bind("<Button-5>",   self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.scroll_results._parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.scroll_results._parent_canvas.yview_scroll(1, "units")
        else:
            self.scroll_results._parent_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units")

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_search_click(self):
        query = self.entry_search.get().strip()
        if query:
            self.btn_search.configure(state="disabled", text="Recherche…")
            self.on_search_callback(query)

    def reset_search_state(self):
        self.btn_search.configure(state="normal", text="Rechercher")

    # ── Rendu des résultats ──────────────────────────────────────────────────

    def display_results(self, results):
        self.reset_search_state()
        query = self.entry_search.get().strip()
        for widget in self.scroll_results.winfo_children():
            widget.destroy()

        if not results:
            self._show_no_results(query)
            return

        for i, res in enumerate(results):
            title      = res.get("title", "Unknown")
            desc       = res.get("description", "")
            project_id = res.get("project_id", "")
            downloads  = res.get("downloads", 0)

            if len(desc) > 120:
                desc = desc[:117] + "..."

            card = ctk.CTkFrame(self.scroll_results, fg_color=SURFACE,
                                border_color=BORDER, border_width=1,
                                corner_radius=10)
            card.grid(row=i, column=0, padx=4, pady=4, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # Icône placeholder
            icon_frame = ctk.CTkFrame(card, fg_color=ACCENT_TINT,
                                      width=44, height=44, corner_radius=10)
            icon_frame.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=12)
            icon_frame.grid_propagate(False)
            ctk.CTkLabel(icon_frame, text="🧩", font=ctk.CTkFont(size=20)
                         ).place(relx=0.5, rely=0.5, anchor="center")

            # Titre
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT,
                         anchor="w"
                         ).grid(row=0, column=1, padx=(0, 8), pady=(12, 2), sticky="w")

            # Description + téléchargements
            info_row = ctk.CTkFrame(card, fg_color="transparent")
            info_row.grid(row=1, column=1, padx=(0, 8), pady=(0, 12), sticky="w")
            ctk.CTkLabel(info_row, text=desc,
                         font=ctk.CTkFont(size=11), text_color=SUB,
                         anchor="w", justify="left", wraplength=380
                         ).pack(anchor="w")
            if downloads:
                dl_str = f"⬇ {downloads:,}".replace(",", "\u202f")
                ctk.CTkLabel(info_row, text=dl_str,
                             font=ctk.CTkFont(size=10), text_color=MUTED
                             ).pack(anchor="w", pady=(2, 0))

            # Bouton installer
            ctk.CTkButton(
                card, text="⬇  Installer", width=110,
                fg_color=ACCENT, hover_color=ACCENT2,
                command=lambda pid=project_id: self._on_install_click(pid)
            ).grid(row=0, column=2, rowspan=2, padx=12, pady=12)

        self._bind_mousewheel(self.scroll_results)

    def _on_install_click(self, project_id):
        self.on_install_callback(project_id)

    def show_progress(self, show: bool):
        if show:
            self.progress_bar.grid(row=2, column=0, padx=0, pady=0, sticky="ew")
            self.progress_bar.set(0)
        else:
            self.progress_bar.grid_forget()

    def update_progress(self, pct: float):
        self.progress_bar.set(pct)
