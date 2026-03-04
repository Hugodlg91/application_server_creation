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
ORANGE   = "#fb923c"
RED      = "#ef4444"
BLUE     = "#60a5fa"

# Tints solides (approximations Tkinter-compatibles sans canal alpha)
ACCENT_TINT  = "#1e2256"   # ACCENT ~15 % sur SURFACE
GREEN_TINT   = "#0d2a1a"   # GREEN ~15 % sur BG

TYPE_COLORS = {
    "PaperMC": GREEN,    # vert
    "Vanilla": ORANGE,   # orange
    "Fabric":  BLUE,     # bleu
}


class HeaderBar(ctk.CTkFrame):
    """
    Barre d'en-tête fixe affichant logo, info serveur, statut et métriques système.
    """

    def __init__(self, master, server_type="PaperMC", version="—",
                 is_running=False, player_count=0, **kwargs):
        super().__init__(master, fg_color=SURFACE, border_color=BORDER,
                         border_width=1, corner_radius=0, **kwargs)

        # ── Gauche ──────────────────────────────────────────────────────────
        frame_left = ctk.CTkFrame(self, fg_color="transparent")
        frame_left.pack(side="left", padx=12, pady=8, fill="y")

        # Logo ⛏
        logo = ctk.CTkFrame(frame_left, fg_color=ACCENT, width=34, height=34,
                            corner_radius=8)
        logo.pack(side="left", padx=(0, 10))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="⛏", font=("Arial", 15), text_color="white"
                     ).place(relx=0.5, rely=0.5, anchor="center")

        # Titre
        frame_title = ctk.CTkFrame(frame_left, fg_color="transparent")
        frame_title.pack(side="left", padx=(0, 14))
        ctk.CTkLabel(frame_title, text="MonPanel",
                     font=("Arial", 14, "bold"), text_color=TEXT
                     ).pack(side="left")
        ctk.CTkLabel(frame_title, text=" LOCAL",
                     font=("Arial", 11, "bold"), text_color=ACCENT
                     ).pack(side="left")

        # Pill serveur (● type · version)
        pill = ctk.CTkFrame(frame_left, fg_color=BG, border_color=BORDER,
                            border_width=1, corner_radius=8)
        pill.pack(side="left")
        self.lbl_type_dot = ctk.CTkLabel(
            pill, text="●", font=("Arial", 10),
            text_color=TYPE_COLORS.get(server_type, SUB))
        self.lbl_type_dot.pack(side="left", padx=(10, 0), pady=6)
        self.lbl_server_type = ctk.CTkLabel(
            pill, text=server_type, font=("Arial", 11), text_color=SUB)
        self.lbl_server_type.pack(side="left", padx=(4, 4), pady=6)
        ctk.CTkLabel(pill, text="·", font=("Arial", 11), text_color=BORDER
                     ).pack(side="left", padx=2)
        self.lbl_version = ctk.CTkLabel(
            pill, text=version, font=("Arial", 11, "bold"), text_color=TEXT)
        self.lbl_version.pack(side="left", padx=(4, 10), pady=6)

        # ── Droite ──────────────────────────────────────────────────────────
        frame_right = ctk.CTkFrame(self, fg_color="transparent")
        frame_right.pack(side="right", padx=12, pady=6, fill="y")

        # Pill statut
        self.pill_status = ctk.CTkFrame(frame_right, fg_color=MUTED,
                                        corner_radius=12)
        self.pill_status.pack(side="right", padx=(10, 0))
        self.lbl_status = ctk.CTkLabel(
            self.pill_status, text="● Éteint",
            font=("Arial", 11, "bold"), text_color=TEXT)
        self.lbl_status.pack(padx=14, pady=6)

        # RAM
        frame_ram = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_ram.pack(side="right", padx=(8, 0))
        row_ram = ctk.CTkFrame(frame_ram, fg_color="transparent")
        row_ram.pack()
        ctk.CTkLabel(row_ram, text="RAM", font=("Arial", 10), text_color=SUB
                     ).pack(side="left")
        self.lbl_ram = ctk.CTkLabel(row_ram, text="0%",
                                    font=("Arial", 10, "bold"), text_color=TEXT)
        self.lbl_ram.pack(side="right", padx=(8, 0))
        self.pb_ram = ctk.CTkProgressBar(frame_ram, width=80, height=5,
                                         corner_radius=2,
                                         progress_color=ACCENT2,
                                         fg_color=BORDER)
        self.pb_ram.set(0)
        self.pb_ram.pack(pady=(2, 0))

        # CPU
        frame_cpu = ctk.CTkFrame(frame_right, fg_color="transparent")
        frame_cpu.pack(side="right", padx=8)
        row_cpu = ctk.CTkFrame(frame_cpu, fg_color="transparent")
        row_cpu.pack()
        ctk.CTkLabel(row_cpu, text="CPU", font=("Arial", 10), text_color=SUB
                     ).pack(side="left")
        self.lbl_cpu = ctk.CTkLabel(row_cpu, text="0%",
                                    font=("Arial", 10, "bold"), text_color=TEXT)
        self.lbl_cpu.pack(side="right", padx=(8, 0))
        self.pb_cpu = ctk.CTkProgressBar(frame_cpu, width=80, height=5,
                                         corner_radius=2,
                                         progress_color=ACCENT,
                                         fg_color=BORDER)
        self.pb_cpu.set(0)
        self.pb_cpu.pack(pady=(2, 0))

        self.update_status(is_running, player_count)

    # ── API publique ─────────────────────────────────────────────────────────

    def update_status(self, is_running, player_count=0):
        if is_running:
            self.pill_status.configure(fg_color=GREEN_TINT)
            s = "s" if player_count > 1 else ""
            self.lbl_status.configure(
                text=f"● En ligne · {player_count} joueur{s}", text_color=GREEN)
        else:
            self.pill_status.configure(fg_color=MUTED)
            self.lbl_status.configure(text="● Éteint", text_color=TEXT)

    def update_metrics(self, cpu_percent, ram_percent):
        self.pb_cpu.set(cpu_percent / 100.0)
        self.lbl_cpu.configure(text=f"{cpu_percent}%")
        self.pb_ram.set(ram_percent / 100.0)
        self.lbl_ram.configure(text=f"{ram_percent}%")

    def set_server_info(self, server_type, version):
        self.lbl_server_type.configure(text=server_type)
        self.lbl_version.configure(text=version)
        self.lbl_type_dot.configure(text_color=TYPE_COLORS.get(server_type, SUB))
