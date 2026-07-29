import customtkinter as ctk


class ProjectTypeScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F0F2FB")
        self.app = master
        self._selected = self.app.app_state.project_type

        iq = self.app.initial_question

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.42, anchor="center")

        ctk.CTkLabel(
            container, text=iq.text,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#15173A",
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            container,
            text="Выберите тип проекта",
            font=ctk.CTkFont(size=16),
            text_color="#5A5F7E",
        ).pack(pady=(0, 36))

        pastel_colors = ["#BFC4FF", "#FFBCA8", "#A8E8BC"]
        icons = ["( )", "( )", "( )"]
        self.cards = []

        cards_row = ctk.CTkFrame(container, fg_color="transparent")
        cards_row.pack()

        for i, opt in enumerate(iq.options):
            color = pastel_colors[i % len(pastel_colors)]
            icon = icons[i % len(icons)]
            selected = self._selected == opt.value

            card = ctk.CTkFrame(
                cards_row,
                fg_color=color if selected else "#FFFFFF",
                corner_radius=18,
                width=240, height=140,
                border_width=2,
                border_color=color if selected else "#D6DAEC",
            )
            card.pack(side="left", padx=10)
            card.pack_propagate(False)

            icon_lbl = ctk.CTkLabel(
                card, text=icon,
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#15173A" if selected else "#5B62E5",
            )
            icon_lbl.pack(pady=(24, 8))

            name_lbl = ctk.CTkLabel(
                card, text=opt.label,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#15173A",
            )
            name_lbl.pack()

            self.cards.append((opt.value, color, card, icon_lbl, name_lbl))

            for w in (card, icon_lbl, name_lbl):
                w.bind("<Button-1>", lambda e, v=opt.value: self._select(v))

        self.next_btn = ctk.CTkButton(
            container, text="Продолжить",
            width=240, height=50, corner_radius=16,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._next,
        )
        self.next_btn.pack(pady=(36, 0))
        self._update_next_btn()

    def _select(self, value):
        self._selected = value
        for v, color, card, icon_lbl, name_lbl in self.cards:
            if v == value:
                card.configure(fg_color=color, border_color=color)
                icon_lbl.configure(text_color="#15173A")
                name_lbl.configure(text_color="#15173A")
            else:
                card.configure(fg_color="#FFFFFF", border_color="#D6DAEC")
                icon_lbl.configure(text_color="#5B62E5")
                name_lbl.configure(text_color="#15173A")
        self._update_next_btn()

    def _update_next_btn(self):
        if self._selected:
            self.next_btn.configure(
                fg_color="#5B62E5", hover_color="#7077EC",
                text_color="#ffffff", state="normal",
            )
        else:
            self.next_btn.configure(
                fg_color="#E8EBF6", hover_color="#E8EBF6",
                text_color="#8E94B0", state="disabled",
            )

    def _next(self):
        self.app.set_platform(self._selected)
        self.app.show_block_select()
