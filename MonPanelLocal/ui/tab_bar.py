import customtkinter as ctk

BG       = "#0f172a"
SURFACE  = "#1e293b"
BORDER   = "#334155"
MUTED    = "#475569"
TEXT     = "#e2e8f0"
SUB      = "#94a3b8"
ACCENT   = "#6366f1"


class TabBar(ctk.CTkFrame):
    """
    Barre d'onglets custom — CTkLabel + bindings souris (pas de CTkButton,
    évite le segfault canvas Linux avant mapping fenêtre WM).
    """

    TABS = [
        ("console",    "Console"),
        ("joueurs",    "Joueurs"),
        ("plugins",    "Plugins"),
        ("parametres", "Paramètres"),
    ]

    def __init__(self, master, on_tab_change, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self.on_tab_change = on_tab_change
        self.active_tab = "console"
        self._labels     = {}   # tab_id → CTkLabel
        self._indicators = {}   # tab_id → CTkFrame (barre 2px)
        self._badge_label = None

        for tab_id, label in self.TABS:
            # Conteneur vertical par onglet
            col = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
            col.pack(side="left")

            # Label cliquable (pas de canvas → pas de segfault)
            lbl = ctk.CTkLabel(
                col,
                text=label,
                font=ctk.CTkFont(size=13),
                padx=16, pady=10,
                cursor="hand2"
            )
            lbl.pack()
            self._labels[tab_id] = lbl

            # Barre indicatrice 2px en bas
            indicator = ctk.CTkFrame(col, height=2, fg_color="transparent",
                                     corner_radius=0)
            indicator.pack(fill="x")
            self._indicators[tab_id] = indicator

            # Bindings hover / clic sur le conteneur ET le label
            for w in (col, lbl):
                w.bind("<Button-1>", lambda e, t=tab_id: self._on_click(t))
                w.bind("<Enter>",    lambda e, t=tab_id: self._on_hover(t, True))
                w.bind("<Leave>",    lambda e, t=tab_id: self._on_hover(t, False))

            # Badge joueurs (overlay via place, caché par défaut)
            if tab_id == "joueurs":
                self._badge_label = ctk.CTkLabel(
                    col,
                    text="0",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    fg_color=ACCENT,
                    text_color="#ffffff",
                    corner_radius=8,
                    width=18, height=18
                )

        self._refresh_styles()
        self.after(0, self._place_badge)

    # ── Badge ────────────────────────────────────────────────────────────────

    def _place_badge(self):
        """Place le badge en overlay sur le label Joueurs puis le cache (caché par défaut)."""
        if self._badge_label:
            lbl = self._labels["joueurs"]
            lbl.update_idletasks()
            self._badge_label.place(
                in_=lbl, relx=1.0, rely=0.0, anchor="ne", x=-4, y=4)
            self._badge_label.place_forget()  # caché au démarrage

    # ── Logique interne ──────────────────────────────────────────────────────

    def _on_click(self, tab_id):
        self.active_tab = tab_id
        self._refresh_styles()
        self.on_tab_change(tab_id)

    def _on_hover(self, tab_id, entering):
        if tab_id == self.active_tab:
            return
        self._labels[tab_id].configure(
            text_color=TEXT if entering else MUTED)

    def _refresh_styles(self):
        for tab_id, lbl in self._labels.items():
            is_active = (tab_id == self.active_tab)
            lbl.configure(
                text_color=TEXT if is_active else MUTED,
                fg_color=SURFACE if is_active else "transparent"
            )
            self._indicators[tab_id].configure(
                fg_color=ACCENT if is_active else "transparent")

    # ── API publique ─────────────────────────────────────────────────────────

    def update_badge(self, count: int):
        if self._badge_label:
            if count > 0:
                self._badge_label.configure(text=str(count))
                lbl = self._labels["joueurs"]
                self._badge_label.place(
                    in_=lbl, relx=1.0, rely=0.0, anchor="ne", x=-4, y=4)
            else:
                self._badge_label.place_forget()
