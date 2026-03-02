import customtkinter as ctk

class TabPlugins(ctk.CTkFrame):
    def __init__(self, master, on_search_callback, on_install_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_search_callback = on_search_callback
        self.on_install_callback = on_install_callback
        
        # Configuration de la grille principale
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Barre supérieure (Recherche) ---
        self.frame_search = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_search.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.frame_search.grid_columnconfigure(0, weight=1)
        
        self.entry_search = ctk.CTkEntry(self.frame_search, placeholder_text="Rechercher un plugin...", height=35)
        self.entry_search.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_search.bind("<Return>", lambda e: self._on_search_click())
        
        self.btn_search = ctk.CTkButton(self.frame_search, text="Rechercher", width=120, height=35, command=self._on_search_click)
        self.btn_search.grid(row=0, column=1)
        
        # --- Zone des résultats ---
        self.scroll_results = ctk.CTkScrollableFrame(self)
        self.scroll_results.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scroll_results.grid_columnconfigure(0, weight=1)
        
        # --- Barre de progression (Cachée par défaut) ---
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        
    def _on_search_click(self):
        query = self.entry_search.get().strip()
        if query:
            self.btn_search.configure(state="disabled")
            self.on_search_callback(query)
            
    def reset_search_state(self):
        self.btn_search.configure(state="normal")
        
    def display_results(self, results):
        self.reset_search_state()
        
        # Nettoyer les anciens résultats
        for widget in self.scroll_results.winfo_children():
            widget.destroy()
            
        if not results:
            lbl_empty = ctk.CTkLabel(self.scroll_results, text="Aucun résultat trouvé.")
            lbl_empty.grid(row=0, column=0, pady=20)
            return
            
        for i, res in enumerate(results):
            title = res.get("title", "Unknown")
            desc = res.get("description", "")
            project_id = res.get("project_id", "")
            
            # Tronquer la description si elle est trop longue
            if len(desc) > 100:
                desc = desc[:97] + "..."
                
            card = ctk.CTkFrame(self.scroll_results, fg_color=("gray80", "gray20"))
            card.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            card.grid_columnconfigure(0, weight=1)
            
            lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(weight="bold", size=14))
            lbl_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
            
            lbl_desc = ctk.CTkLabel(card, text=desc, text_color="gray", justify="left", anchor="w")
            lbl_desc.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")
            
            btn_install = ctk.CTkButton(
                card, 
                text="Installer", 
                width=100,
                command=lambda pid=project_id: self._on_install_click(pid)
            )
            btn_install.grid(row=0, column=1, rowspan=2, padx=10, pady=10)
            
    def _on_install_click(self, project_id):
        self.on_install_callback(project_id)
        
    def show_progress(self, show: bool):
        if show:
            self.progress_bar.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
            self.progress_bar.set(0)
        else:
            self.progress_bar.grid_forget()
            
    def update_progress(self, pct: float):
        self.progress_bar.set(pct)
