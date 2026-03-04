import customtkinter as ctk
from core.i18n import t

BG       = "#0f172a"
SURFACE  = "#1e293b"
BORDER   = "#334155"
MUTED    = "#475569"
TEXT     = "#e2e8f0"
SUB      = "#94a3b8"
ACCENT   = "#6366f1"
GREEN    = "#4ade80"
ORANGE   = "#fb923c"
RED      = "#ef4444"

GREEN_TINT  = "#0d2a1a"
RED_TINT    = "#3d1a1a"
RED_BORDER  = "#6b2d2d"
ORANGE_TINT = "#2d1c06"
ORANGE_BDR  = "#5a3810"

# Palette d'avatars (8 couleurs solides)
AVATAR_PALETTE = [
    "#6366f1", "#8b5cf6", "#06b6d4",
    "#10b981", "#f59e0b", "#ef4444",
    "#ec4899", "#3b82f6",
]


def _avatar_color(name: str) -> str:
    return AVATAR_PALETTE[sum(ord(c) for c in name) % len(AVATAR_PALETTE)]


class TabPlayers(ctk.CTkFrame):
    """Onglet affichant la liste des joueurs connectés avec modération."""

    def __init__(self, master, send_command_callback, **kwargs):
        super().__init__(master, fg_color=BG, **kwargs)
        self.send_command_callback = send_command_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === Header ===
        self.frame_top = ctk.CTkFrame(self, fg_color=SURFACE,
                                      border_color=BORDER, border_width=1,
                                      corner_radius=8)
        self.frame_top.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self.frame_top.grid_columnconfigure(1, weight=1)

        frame_titles = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        frame_titles.grid(row=0, column=0, padx=12, pady=10, sticky="w")
        ctk.CTkLabel(frame_titles, text=t("players.title"),
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT
                     ).pack(anchor="w")
        ctk.CTkLabel(frame_titles, text=t("players.subtitle"),
                     font=ctk.CTkFont(size=11), text_color=SUB
                     ).pack(anchor="w")

        # Badge compteur
        self.pill_count = ctk.CTkFrame(self.frame_top, fg_color=BG,
                                       border_color=BORDER, border_width=1,
                                       corner_radius=20)
        self.pill_count.grid(row=0, column=1, padx=8, pady=10, sticky="w")
        self.lbl_count = ctk.CTkLabel(self.pill_count, text=t("players.count_one").replace("1 ", "0 "),
                                      font=ctk.CTkFont(size=11, weight="bold"),
                                      text_color=MUTED)
        self.lbl_count.pack(padx=14, pady=5)

        self.btn_refresh = ctk.CTkButton(
            self.frame_top, text=f"↻  {t('players.refresh')}", width=110,
            fg_color=SURFACE, hover_color=BG,
            border_color=BORDER, border_width=1,
            text_color=SUB,
            command=self._on_refresh_clicked)
        self.btn_refresh.grid(row=0, column=2, padx=12, pady=10, sticky="e")

        # === Zone de défilement ===
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG, scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=MUTED)
        self.scroll_frame.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._show_empty_state()
        self.after(200, lambda: self._bind_mousewheel(self.scroll_frame))

    # ── État vide ─────────────────────────────────────────────────────────────

    def _show_empty_state(self):
        frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame.grid(row=0, column=0, pady=60, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=t("players.empty_title"),
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT
                     ).grid(row=0, column=0)
        ctk.CTkLabel(frame, text=t("players.empty_sub"),
                     font=ctk.CTkFont(size=12), text_color=MUTED
                     ).grid(row=1, column=0, pady=(4, 0))

    # ── Scroll molette ────────────────────────────────────────────────────────

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>",   self._on_mousewheel)
        widget.bind("<Button-5>",   self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.scroll_frame._parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.scroll_frame._parent_canvas.yview_scroll(1, "units")
        else:
            self.scroll_frame._parent_canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units")

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_refresh_clicked(self):
        self.send_command_callback("list")

    # ── Rendu ─────────────────────────────────────────────────────────────────

    def update_player_list(self, players):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        count = len(players)
        if count == 0:
            self.lbl_count.configure(text=t("players.count_one").replace("1 ", "0 "),
                                     text_color=MUTED)
            self.pill_count.configure(fg_color=BG)
            self._show_empty_state()
            return

        if count == 1:
            count_txt = t("players.count_one")
        else:
            count_txt = t("players.count_many").format(n=count)
        self.lbl_count.configure(text=count_txt, text_color=GREEN)
        self.pill_count.configure(fg_color=GREEN_TINT)

        for idx, player in enumerate(sorted(players)):
            color   = _avatar_color(player)
            initial = player[0].upper()

            card = ctk.CTkFrame(self.scroll_frame, fg_color=SURFACE,
                                border_color=BORDER, border_width=1,
                                corner_radius=10)
            card.grid(row=idx, column=0, padx=4, pady=4, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # Avatar coloré + initiale
            avatar = ctk.CTkFrame(card, fg_color=color, width=38,
                                  height=38, corner_radius=10)
            avatar.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10)
            avatar.grid_propagate(False)
            ctk.CTkLabel(avatar, text=initial,
                         font=ctk.CTkFont(size=15, weight="bold"),
                         text_color="white"
                         ).place(relx=0.5, rely=0.5, anchor="center")

            # Nom + point vert
            name_row = ctk.CTkFrame(card, fg_color="transparent")
            name_row.grid(row=0, column=1, padx=(0, 8), pady=(10, 0), sticky="w")
            ctk.CTkLabel(name_row, text="●",
                         font=ctk.CTkFont(size=10), text_color=GREEN
                         ).pack(side="left", padx=(0, 4))
            ctk.CTkLabel(name_row, text=player,
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT
                         ).pack(side="left")

            ctk.CTkLabel(card, text=t("players.online"),
                         font=ctk.CTkFont(size=10), text_color=SUB
                         ).grid(row=1, column=1, padx=(0, 8), pady=(0, 10), sticky="w")

            # Boutons modération
            frame_btns = ctk.CTkFrame(card, fg_color="transparent")
            frame_btns.grid(row=0, column=2, rowspan=2, padx=8, pady=8)

            ctk.CTkButton(
                frame_btns, text="Op", width=56,
                fg_color=SURFACE, hover_color=BG,
                border_color=BORDER, border_width=1, text_color=TEXT,
                command=lambda p=player: self.send_command_callback(f"op {p}")
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                frame_btns, text="Kick", width=60,
                fg_color=ORANGE_TINT, hover_color="#3d2510",
                border_color=ORANGE_BDR, border_width=1, text_color=ORANGE,
                command=lambda p=player: self.send_command_callback(f"kick {p}")
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                frame_btns, text="Ban", width=56,
                fg_color=RED_TINT, hover_color="#5a2020",
                border_color=RED_BORDER, border_width=1, text_color=RED,
                command=lambda p=player: self.send_command_callback(f"ban {p}")
            ).pack(side="left", padx=3)

        self._bind_mousewheel(self.scroll_frame)
