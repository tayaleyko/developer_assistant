import customtkinter as ctk
from widgets.block_card import BlockCard
from storage import save_progress


class BlockSelectScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F0F2FB")
        self.app = master
        blocks = self.app.app_state.blocks

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(24, 16))

        ctk.CTkLabel(
            header, text="Выберите блок",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#15173A",
        ).pack(side="left")

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=22, pady=(0, 8))
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for i, block in enumerate(blocks):
            row, col = i // 2, i % 2

            if self.app.app_state.is_block_complete(block.id):
                status = "Завершён"
            elif block.id in self.app.app_state.answers:
                answered = len(self.app.app_state.answers[block.id])
                total = len(block.questions)
                status = f"{answered}/{total} вопросов"
            else:
                status = "Не начат"

            card = BlockCard(
                grid, block, status,
                color_index=i,
                on_click=lambda b=block: self._open_block(b.id),
            )
            card.grid(row=row, column=col, padx=8, pady=6, sticky="nsew")

        for r in range((len(blocks) + 1) // 2):
            grid.rowconfigure(r, weight=1)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=30, pady=(8, 20))

        self.save_btn = ctk.CTkButton(
            bottom, text="Сохранить",
            width=160, height=44, corner_radius=14,
            fg_color="#DDE0FB", hover_color="#C7CCF6",
            border_width=1, border_color="#5B62E5",
            text_color="#5B62E5",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save,
        )
        self.save_btn.pack(side="left")

        has_complete = self.app.app_state.has_any_complete_block()
        ctk.CTkButton(
            bottom, text="Далее",
            width=160, height=44, corner_radius=14,
            fg_color="#5B62E5" if has_complete else "#E8EBF6",
            hover_color="#7077EC",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff" if has_complete else "#8E94B0",
            command=self._next,
            state="normal" if has_complete else "disabled",
        ).pack(side="right")

    def _open_block(self, block_id):
        self.app.show_quiz(block_id)

    def _save(self):
        save_progress(self.app.app_state.to_dict())
        self.save_btn.configure(text="Сохранено!")
        self.after(1500, lambda: self.save_btn.configure(text="Сохранить"))

    def _next(self):
        self.app.show_result()
