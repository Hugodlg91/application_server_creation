import customtkinter as ctk


class ScrollableDropdown(ctk.CTkButton):
    """
    Dropdown scrollable custom.
    Apparence : CTkButton affichant la valeur courante + ▼
    Au clic : popup CTkToplevel positionné sous le widget,
              contenant un CTkScrollableFrame. Max 8 entrées visibles,
              scroll molette au-delà.
    """

    def __init__(self, master, values, command=None, width=120,
                 dropdown_fg_color=None, dropdown_hover_color=None,
                 # ignorés, acceptés pour rétro-compat
                 button_color=None, button_hover_color=None,
                 **kwargs):
        self._values      = list(values)
        self._on_select   = command
        self._current     = self._values[0] if self._values else ""
        self._popup       = None
        self._disabled    = False
        self._dd_bg       = dropdown_fg_color    or ("gray85", "gray20")
        self._dd_hv       = dropdown_hover_color or ("gray70", "gray30")

        # Stocker les couleurs pour synchro du label ▼
        self._col_normal = kwargs.get("fg_color",    "#0f172a")
        self._col_hover  = kwargs.get("hover_color", "#1e293b")

        super().__init__(
            master,
            text=self._current,
            command=self._open_popup,
            width=width,
            anchor="w",
            **kwargs
        )

        # Overlay ▼ à droite du bouton via place()
        self._arrow_lbl = ctk.CTkLabel(
            self,
            text="▼",
            font=ctk.CTkFont(size=9),
            text_color=kwargs.get("text_color", "#e2e8f0"),
            fg_color=self._col_normal,  # même fond que le bouton
            width=14,
        )
        self.after(10, self._place_arrow)

        # Synchro hover : quand la souris entre/sort, mettre à jour les deux
        self.bind("<Enter>", lambda e: self._on_hover(True),  add="+")
        self.bind("<Leave>", lambda e: self._on_hover(False), add="+")
        self._arrow_lbl.bind("<Enter>", lambda e: self._on_hover(True))
        self._arrow_lbl.bind("<Leave>", lambda e: self._on_hover(False))

    def _place_arrow(self):
        self._arrow_lbl.place(relx=1.0, rely=0.5, anchor="e", x=-6)

    def _on_hover(self, entering: bool):
        color = self._col_hover if entering else self._col_normal
        self._arrow_lbl.configure(fg_color=color)

    # ── Popup ──────────────────────────────────────────────────────────────

    def _open_popup(self):
        if self._disabled:
            return
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

        scroll = ctk.CTkScrollableFrame(self._popup, fg_color=self._dd_bg)
        scroll.pack(fill="both", expand=True)
        scroll.grid_columnconfigure(0, weight=1)

        for i, val in enumerate(self._values):
            btn = ctk.CTkButton(
                scroll,
                text=val,
                anchor="w",
                fg_color="transparent",
                hover_color=self._dd_hv,
                text_color=("gray10", "gray90"),
                height=28,
                command=lambda v=val: self._select(v)
            )
            btn.grid(row=i, column=0, sticky="ew", padx=2, pady=1)

        scroll.bind("<Button-4>", lambda e: scroll._parent_canvas.yview_scroll(-1, "units"))
        scroll.bind("<Button-5>", lambda e: scroll._parent_canvas.yview_scroll(1, "units"))

        self._popup.bind("<FocusOut>", lambda e: self._close_popup())
        self._popup.bind("<Escape>",   lambda e: self._close_popup())
        self._popup.focus_force()

    def _close_popup(self):
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        self._popup = None

    def _select(self, value):
        self._current = value
        super().configure(text=value)
        self._close_popup()
        if self._on_select:
            self._on_select(value)

    # ── API publique ───────────────────────────────────────────────────────

    def get(self) -> str:
        return self._current

    def set(self, value: str):
        self._current = value
        super().configure(text=value)

    def configure(self, **kwargs):
        if "values" in kwargs:
            self._values = list(kwargs.pop("values"))
            if self._popup and self._popup.winfo_exists():
                self._close_popup()
        if "state" in kwargs:
            state = kwargs["state"]
            self._disabled = (state == "disabled")
            if state == "readonly":
                kwargs["state"] = "normal"
        if "command" in kwargs:
            self._on_select = kwargs.pop("command")
        if kwargs:
            super().configure(**kwargs)
