import customtkinter as ctk


class ScrollableDropdown(ctk.CTkButton):
    """
    Dropdown scrollable custom.
    Apparence : CTkButton affichant la valeur courante + ▼
    Au clic : popup CTkToplevel positionné sous le widget,
              contenant un CTkScrollableFrame. Max 8 entrées visibles,
              scroll molette au-delà.
    """

    def __init__(self, master, values, command=None, width=120, **kwargs):
        self._values = list(values)
        self._command = command
        self._current_value = self._values[0] if self._values else ""
        self._popup = None
        self._disabled = False

        # NE PAS passer command au super — on câble _open_popup à la place
        super().__init__(
            master,
            text=f"{self._current_value} ▼",
            command=self._open_popup,
            width=width,
            anchor="w",
            **kwargs
        )

    # ──────────────────────────────────────────────
    # Popup
    # ──────────────────────────────────────────────

    def _open_popup(self):
        if self._disabled:
            return

        # Toggle : fermer si déjà ouvert
        if self._popup and self._popup.winfo_exists():
            self._close_popup()
            return

        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        w = self.winfo_width()
        n = min(len(self._values), 8)
        h = n * 30

        self._popup = ctk.CTkToplevel(self)
        self._popup.overrideredirect(True)
        self._popup.geometry(f"{w}x{h}+{x}+{y}")
        self._popup.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(self._popup, fg_color=("gray85", "gray20"))
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)

        for i, val in enumerate(self._values):
            btn = ctk.CTkButton(
                scroll,
                text=val,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                text_color=("gray10", "gray90"),
                height=28,
                command=lambda v=val: self._select(v)
            )
            btn.grid(row=i, column=0, sticky="ew", padx=2, pady=1)

        # Scroll molette Linux
        scroll.bind("<Button-4>", lambda e: scroll._parent_canvas.yview_scroll(-1, "units"))
        scroll.bind("<Button-5>", lambda e: scroll._parent_canvas.yview_scroll(1, "units"))

        # Fermeture automatique sur perte de focus
        self._popup.bind("<FocusOut>", lambda e: self._close_popup())
        self._popup.bind("<Escape>", lambda e: self._close_popup())
        self._popup.focus_force()

    def _close_popup(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        self._popup = None

    def _select(self, value):
        self._current_value = value
        super().configure(text=f"{value} ▼")
        self._close_popup()
        if self._command:
            self._command(value)

    # ──────────────────────────────────────────────
    # API publique (compatible CTkComboBox / CTkOptionMenu)
    # ──────────────────────────────────────────────

    def get(self):
        return self._current_value

    def set(self, value):
        self._current_value = value
        super().configure(text=f"{value} ▼")

    def configure(self, **kwargs):
        # Intercepter "values" : mise à jour de la liste interne
        if "values" in kwargs:
            self._values = list(kwargs.pop("values"))
            if self._popup and self._popup.winfo_exists():
                self._close_popup()

        # Intercepter "state" : mapper "readonly" → "normal" pour CTkButton
        if "state" in kwargs:
            state = kwargs["state"]
            self._disabled = (state == "disabled")
            if state == "readonly":
                kwargs["state"] = "normal"

        # Intercepter "command" : stocker comme callback de sélection
        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if kwargs:
            super().configure(**kwargs)
