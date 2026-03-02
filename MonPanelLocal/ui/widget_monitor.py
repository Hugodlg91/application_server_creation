import customtkinter as ctk

class WidgetMonitor(ctk.CTkFrame):
    """
    Cadre affichant l'utilisation du CPU et de la RAM en bas de la fenêtre.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure((0, 2), weight=1)
        
        # Section CPU
        self.lbl_cpu = ctk.CTkLabel(self, text="CPU: 0%")
        self.lbl_cpu.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.pb_cpu = ctk.CTkProgressBar(self, width=200)
        self.pb_cpu.set(0)
        self.pb_cpu.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Section RAM
        self.lbl_ram = ctk.CTkLabel(self, text="RAM: 0%")
        self.lbl_ram.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="e")
        
        self.pb_ram = ctk.CTkProgressBar(self, width=200)
        self.pb_ram.set(0)
        self.pb_ram.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="e")

    def update_metrics(self, cpu_percent, ram_percent):
        """Met à jour les labels et barres de progression."""
        self.lbl_cpu.configure(text=f"CPU: {cpu_percent}%")
        self.pb_cpu.set(cpu_percent / 100.0)
        
        self.lbl_ram.configure(text=f"RAM: {ram_percent}%")
        self.pb_ram.set(ram_percent / 100.0)
