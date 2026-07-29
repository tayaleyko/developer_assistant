import customtkinter as ctk


class OptionChip(ctk.CTkButton):
    def __init__(self, master, label, selected=False, on_toggle=None):
        self._selected = selected
        self._on_toggle = on_toggle
        super().__init__(
            master,
            text=label,
            corner_radius=20,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._toggle,
            border_width=1,
            **self._style()
        )

    def _style(self):
        if self._selected:
            return dict(
                fg_color="#5B62E5",
                hover_color="#7077EC",
                border_color="#5B62E5",
                text_color="#ffffff",
            )
        return dict(
            fg_color="#DDE0FB",
            hover_color="#C7CCF6",
            border_color="#5B62E5",
            text_color="#5B62E5",
        )

    def _toggle(self):
        self._selected = not self._selected
        self._apply_style()
        if self._on_toggle:
            self._on_toggle(self._selected)

    def set_selected(self, val):
        self._selected = val
        self._apply_style()

    @property
    def selected(self):
        return self._selected

    def _apply_style(self):
        self.configure(**self._style())
