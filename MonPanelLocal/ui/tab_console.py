import customtkinter as ctk
from .widgets.scrollable_dropdown import ScrollableDropdown

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
BLUE     = "#60a5fa"

RED_TINT    = "#3d1a1a"
RED_BORDER  = "#6b2d2d"
BLUE_TINT   = "#111e3a"
BLUE_BORDER = "#1e3560"
GREEN_TINT  = "#0d2a1a"


class TabConsole(ctk.CTkFrame):
    def __init__(self, master, on_start, on_stop, on_send_command, on_download,
                 on_version_change, on_type_change, on_bore_toggle=None, **kwargs):
        super().__init__(master, fg_color=BG, **kwargs)

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
        self.grid_rowconfigure(3, weight=1)   # row 3 = console_box

        # ── row 0 : Barre de contrôles ────────────────────────────────────────
        self.frame_controls = ctk.CTkFrame(self, fg_color=SURFACE,
                                           border_color=BORDER, border_width=1,
                                           corner_radius=10)
        self.frame_controls.grid(row=0, column=0, padx=8, pady=(8, 4), sticky="ew")

        # Groupe gauche : sélection du serveur
        grp_server = ctk.CTkFrame(self.frame_controls, fg_color=BG,
                                  border_color=BORDER, border_width=1,
                                  corner_radius=8)
        grp_server.pack(side="left", padx=(10, 0), pady=8)

        ctk.CTkLabel(grp_server, text="Type", text_color=SUB,
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=(10, 4))
        self.option_type = ctk.CTkOptionMenu(
            grp_server,
            values=["PaperMC", "Vanilla", "Fabric"],
            width=106, height=30,
            fg_color=BG, button_color=ACCENT,
            button_hover_color=ACCENT2, text_color=TEXT,
            dropdown_fg_color=SURFACE, dropdown_text_color=TEXT,
            dropdown_hover_color=BORDER)
        self.option_type.pack(side="left", padx=(0, 6), pady=4)

        # Séparateur vertical
        ctk.CTkFrame(grp_server, fg_color=BORDER, width=1).pack(
            side="left", fill="y", pady=6)

        ctk.CTkLabel(grp_server, text="Version", text_color=SUB,
                     font=ctk.CTkFont(size=11)).pack(side="left", padx=(8, 4))
        self.option_version = ScrollableDropdown(
            grp_server,
            values=["Chargement..."],
            width=116, height=30,
            fg_color=BG, text_color=TEXT,
            hover_color=SURFACE,
            command=self._on_version_selected)
        self.option_version.pack(side="left", padx=(0, 10), pady=4)

        # Boutons action (milieu)
        self.btn_install = ctk.CTkButton(
            self.frame_controls, text="⬇  Installer", width=110,
            fg_color=SURFACE, hover_color=BG,
            border_color=BORDER, border_width=1,
            text_color=SUB, height=32,
            command=self._on_download_clicked)
        self.btn_install.pack(side="left", padx=(8, 4), pady=8)

        self.btn_start = ctk.CTkButton(
            self.frame_controls, text="▶  Démarrer", width=120,
            fg_color=ACCENT, hover_color=ACCENT2,
            text_color=TEXT, height=32,
            command=self._on_start_clicked)
        self.btn_start.pack(side="left", padx=4, pady=8)
        self.btn_start.pack_forget()

        self.btn_stop = ctk.CTkButton(
            self.frame_controls, text="■  Arrêter", width=110,
            fg_color=RED_TINT, hover_color="#5a2020",
            text_color=RED, border_color=RED_BORDER,
            border_width=1, height=32, state="disabled",
            command=self._on_stop_clicked)
        self.btn_stop.pack(side="left", padx=4, pady=8)

        # Groupe droite : bore + statut
        self.btn_bore = ctk.CTkButton(
            self.frame_controls, text="🌐  Public", width=100,
            fg_color=BLUE_TINT, hover_color=SURFACE,
            text_color=BLUE, border_color=BLUE_BORDER,
            border_width=1, height=32,
            command=self._on_bore_clicked)
        self.btn_bore.pack(side="right", padx=(4, 10), pady=8)

        self.entry_bore_ip = ctk.CTkEntry(
            self.frame_controls, width=160, state="readonly",
            justify="center", fg_color=BG, border_color=BORDER,
            text_color=BLUE, font=("Consolas", 11))

        # Pill statut (côté droit)
        self.pill_state = ctk.CTkFrame(self.frame_controls,
                                       fg_color=RED_TINT, corner_radius=12)
        self.pill_state.pack(side="right", padx=(4, 8), pady=8)
        self.lbl_state = ctk.CTkLabel(
            self.pill_state, text="● Éteint",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=RED)
        self.lbl_state.pack(padx=12, pady=5)

        # ── row 1 : Header console ────────────────────────────────────────────
        hdr_console = ctk.CTkFrame(self, fg_color="transparent")
        hdr_console.grid(row=1, column=0, padx=12, pady=(2, 0), sticky="ew")
        ctk.CTkLabel(hdr_console, text="◉", font=ctk.CTkFont(size=11),
                     text_color=GREEN).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(hdr_console, text="CONSOLE EN DIRECT",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=MUTED).pack(side="left")

        # ── row 2 : Barre de progression (cachée par défaut) ──────────────────
        self.progress_bar = ctk.CTkProgressBar(
            self, height=4, corner_radius=0, border_width=0,
            progress_color=ACCENT, fg_color=BORDER)
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()

        # ── row 3 : Console textbox ───────────────────────────────────────────
        self.console_box = ctk.CTkTextbox(
            self, state="disabled",
            font=("Consolas", 12),
            fg_color=BG, text_color=TEXT,
            border_color=BORDER, border_width=1,
            corner_radius=8)
        self.console_box.grid(row=3, column=0, padx=8, pady=(4, 4), sticky="nsew")

        # ── row 4 : Zone de commande ──────────────────────────────────────────
        self.frame_input = ctk.CTkFrame(self, fg_color=SURFACE,
                                        border_color=BORDER, border_width=1,
                                        corner_radius=10)
        self.frame_input.grid(row=4, column=0, padx=8, pady=(0, 8), sticky="ew")
        self.frame_input.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.frame_input, text="›", font=ctk.CTkFont(size=18),
                     text_color=ACCENT, width=24).grid(row=0, column=0, padx=(10, 0))

        self.entry_cmd = ctk.CTkEntry(
            self.frame_input,
            placeholder_text="Entrez une commande…",
            fg_color=BG, border_color=BORDER,
            text_color=TEXT, placeholder_text_color=MUTED,
            border_width=1)
        self.entry_cmd.grid(row=0, column=1, padx=(4, 4), pady=8, sticky="ew")
        self.entry_cmd.bind("<Return>", self._on_send_clicked)
        self.entry_cmd.bind("<Up>",     self._on_history_up)
        self.entry_cmd.bind("<Down>",   self._on_history_down)

        self.btn_send = ctk.CTkButton(
            self.frame_input, text="Envoyer", width=90,
            fg_color=ACCENT, hover_color=ACCENT2,
            command=self._on_send_clicked, state="disabled")
        self.btn_send.grid(row=0, column=2, padx=(0, 8), pady=8)

        # Câblage différé (évite le callback prématuré sur Linux)
        self.option_type.configure(command=self._on_type_selected)
        self.after(100, self._configure_log_tags)

    # ── Tags console ──────────────────────────────────────────────────────────

    def _configure_log_tags(self):
        self.console_box._textbox.tag_configure("error",   foreground="#f87171")
        self.console_box._textbox.tag_configure("warn",    foreground="#fbbf24")
        self.console_box._textbox.tag_configure("system",  foreground="#93c5fd")
        self.console_box._textbox.tag_configure("default", foreground="#cbd5e1")
        self._tags_ready = True

    # ── API publique ──────────────────────────────────────────────────────────

    def set_versions(self, versions):
        if versions:
            self.option_version.configure(values=versions)
            self.option_version.set(versions[0])
            self.on_version_change(versions[0])
        else:
            self.option_version.configure(values=["Erreur API"])
            self.option_version.set("Erreur API")
            self.btn_install.configure(state="disabled")

    def set_loading_state(self, loading: bool):
        state = "disabled" if loading else "normal"
        self.option_type.configure(state=state)
        self.option_version.configure(state=state)
        if loading:
            self.option_version.configure(values=["Chargement..."])
            self.option_version.set("Chargement...")

    def update_install_state(self, is_installed):
        if is_installed:
            self.btn_install.pack_forget()
            self.btn_start.pack(side="left", padx=4, pady=8,
                                after=self.btn_install)
        else:
            self.btn_start.pack_forget()
            self.btn_install.pack(side="left", padx=(8, 4), pady=8,
                                  after=self.option_version)

    def show_progress(self, show=True):
        if show:
            self.progress_bar.grid(row=2, column=0, padx=0, pady=0, sticky="ew")
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
        if is_running:
            self.option_version.configure(state="disabled")
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
            self.btn_send.configure(state="normal")
            self.pill_state.configure(fg_color=GREEN_TINT)
            self.lbl_state.configure(text="● En ligne", text_color=GREEN)
        else:
            self.option_version.configure(state="normal")
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.btn_send.configure(state="disabled")
            self.pill_state.configure(fg_color=RED_TINT)
            self.lbl_state.configure(text="● Éteint", text_color=RED)

    def set_bore_state(self, is_running, ip=""):
        if is_running:
            self.btn_bore.configure(
                text="✕  Tunnel actif",
                fg_color=RED_TINT, hover_color="#5a2020",
                text_color=RED, border_color=RED_BORDER)
            if ip:
                self.entry_bore_ip.pack(side="right", padx=4, pady=8,
                                        before=self.btn_bore)
                self.entry_bore_ip.configure(state="normal")
                self.entry_bore_ip.delete(0, "end")
                self.entry_bore_ip.insert(0, ip)
                self.entry_bore_ip.configure(state="readonly")
        else:
            self.btn_bore.configure(
                text="🌐  Public", fg_color=BLUE_TINT,
                hover_color=SURFACE, text_color=BLUE,
                border_color=BLUE_BORDER)
            self.entry_bore_ip.pack_forget()

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_version_selected(self, value):
        self.on_version_change(value)

    def _on_type_selected(self, value):
        self.on_type_change(value)

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
