import customtkinter as ctk

class TabPlayers(ctk.CTkFrame):
    """
    Onglet affichant la liste des joueurs connectés en temps réel avec des actions de modération.
    """
    def __init__(self, master, send_command_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.send_command_callback = send_command_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Titre et bouton rafraîchir
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.grid(row=0, column=0, pady=10, sticky="ew")
        self.frame_top.grid_columnconfigure(0, weight=1)
        
        self.lbl_title = ctk.CTkLabel(self.frame_top, text="Joueurs Connectés", font=("Arial", 16, "bold"))
        self.lbl_title.grid(row=0, column=0)
        
        self.btn_refresh = ctk.CTkButton(self.frame_top, text="Actualiser", width=100, command=self._on_refresh_clicked)
        self.btn_refresh.grid(row=0, column=1, padx=10, sticky="e")
        
        # Liste
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _on_refresh_clicked(self):
        """Demande au serveur de lister les joueurs, ce qui mettra à jour l'UI via le log parser."""
        self.send_command_callback("list")

    def update_player_list(self, players):
        """Met à jour l'affichage avec la nouvelle liste de joueurs."""
        # Effacer l'ancien contenu
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        if not players:
            lbl_empty = ctk.CTkLabel(self.scroll_frame, text="Aucun joueur en ligne.", text_color="gray")
            lbl_empty.grid(row=0, column=0, pady=20)
            return
            
        for idx, player in enumerate(sorted(players)):
            frame_player = ctk.CTkFrame(self.scroll_frame)
            frame_player.grid(row=idx, column=0, padx=5, pady=2, sticky="ew")
            frame_player.grid_columnconfigure(0, weight=1)
            
            lbl_name = ctk.CTkLabel(frame_player, text=player, font=("Arial", 14))
            lbl_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            btn_op = ctk.CTkButton(
                frame_player, text="Op", width=60, fg_color="green", hover_color="darkgreen",
                command=lambda p=player: self.send_command_callback(f"op {p}")
            )
            btn_op.grid(row=0, column=1, padx=5, pady=5)
            
            btn_kick = ctk.CTkButton(
                frame_player, text="Kick", width=60, fg_color="#d48806", hover_color="#ad6f05",
                command=lambda p=player: self.send_command_callback(f"kick {p}")
            )
            btn_kick.grid(row=0, column=2, padx=5, pady=5)
            
            btn_ban = ctk.CTkButton(
                frame_player, text="Ban", width=60, fg_color="red", hover_color="darkred",
                command=lambda p=player: self.send_command_callback(f"ban {p}")
            )
            btn_ban.grid(row=0, column=3, padx=5, pady=5)
