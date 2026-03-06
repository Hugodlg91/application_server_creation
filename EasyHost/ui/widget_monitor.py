import customtkinter as ctk

BG       = "#0f172a"
SURFACE  = "#1e293b"
BORDER   = "#334155"
TEXT     = "#e2e8f0"
SUB      = "#94a3b8"
ACCENT   = "#6366f1"
ACCENT2  = "#8b5cf6"


class WidgetMonitor(ctk.CTkFrame):
    """
    Barre de métriques système (CPU / RAM) en bas de la fenêtre.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=SURFACE, border_color=BORDER,
                         border_width=1, corner_radius=0, **kwargs)

        # CPU
        frame_cpu = ctk.CTkFrame(self, fg_color="transparent")
        frame_cpu.pack(side="left", padx=20, pady=8)

        row_cpu = ctk.CTkFrame(frame_cpu, fg_color="transparent")
        row_cpu.pack()
        ctk.CTkLabel(row_cpu, text="CPU", font=("Arial", 10), text_color=SUB
                     ).pack(side="left")
        self.lbl_cpu = ctk.CTkLabel(row_cpu, text="0%",
                                    font=("Arial", 10, "bold"), text_color=TEXT)
        self.lbl_cpu.pack(side="right", padx=(10, 0))

        self.pb_cpu = ctk.CTkProgressBar(frame_cpu, width=200, height=5,
                                         corner_radius=2,
                                         progress_color=ACCENT, fg_color=BORDER)
        self.pb_cpu.set(0)
        self.pb_cpu.pack(pady=(3, 0))

        # RAM
        frame_ram = ctk.CTkFrame(self, fg_color="transparent")
        frame_ram.pack(side="left", padx=20, pady=8)

        row_ram = ctk.CTkFrame(frame_ram, fg_color="transparent")
        row_ram.pack()
        ctk.CTkLabel(row_ram, text="RAM", font=("Arial", 10), text_color=SUB
                     ).pack(side="left")
        self.lbl_ram = ctk.CTkLabel(row_ram, text="0%",
                                    font=("Arial", 10, "bold"), text_color=TEXT)
        self.lbl_ram.pack(side="right", padx=(10, 0))

        self.pb_ram = ctk.CTkProgressBar(frame_ram, width=200, height=5,
                                         corner_radius=2,
                                         progress_color=ACCENT2, fg_color=BORDER)
        self.pb_ram.set(0)
        self.pb_ram.pack(pady=(3, 0))

    def update_metrics(self, cpu_percent, ram_percent):
        self.lbl_cpu.configure(text=f"{cpu_percent}%")
        self.pb_cpu.set(cpu_percent / 100.0)
        self.lbl_ram.configure(text=f"{ram_percent}%")
        self.pb_ram.set(ram_percent / 100.0)
