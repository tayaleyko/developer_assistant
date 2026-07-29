import tkinter as tk
import customtkinter as ctk
from ui import fix_scroll
from widgets.question_card import QuestionCard


class QuizScreen(ctk.CTkFrame):
    def __init__(self, master, block_id):
        super().__init__(master, fg_color="#F0F2FB")
        self.app = master
        blocks = self.app.app_state.blocks
        self.block = next(b for b in blocks if b.id == block_id)
        self.answers = dict(self.app.app_state.answers.get(block_id, {}))

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(16, 0))

        arrow_cv = tk.Canvas(
            top, width=110, height=30,
            bg="#F0F2FB", highlightthickness=0, cursor="hand2",
        )
        arrow_cv.pack(side="left")
        arrow_cv.create_line(6, 15, 30, 15, fill="#5B62E5", width=2)
        arrow_cv.create_line(6, 15, 15, 7,  fill="#5B62E5", width=2)
        arrow_cv.create_line(6, 15, 15, 23, fill="#5B62E5", width=2)
        arrow_cv.create_text(35, 15, text="Назад", fill="#5B62E5",
                             font=("Segoe UI", 16, "bold"), anchor="w")
        arrow_cv.bind("<Button-1>", lambda e: self._go_back())

        completed = sum(
            1 for b in blocks
            if self.app.app_state.is_block_complete(b.id)
        )
        total = len(blocks)

        progress = ctk.CTkProgressBar(
            top, width=200, height=8, corner_radius=4,
            fg_color="#DDE0FB", progress_color="#5B62E5",
        )
        progress.set(completed / total if total else 0)
        progress.pack(side="right", pady=4)

        ctk.CTkLabel(
            top, text=f"{completed}/{total}",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#5A5F7E",
        ).pack(side="right", padx=(0, 10))

        ctk.CTkLabel(
            self, text=self.block.title,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#15173A",
        ).pack(padx=24, pady=(20, 16), anchor="w")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        fix_scroll(scroll)

        for q in self.block.questions:
            card = QuestionCard(
                scroll, q,
                on_answer=self._on_answer,
                current_answer=self.answers.get(q.id),
            )
            card.pack(fill="x", padx=8, pady=6)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(8, 20))

        self.save_btn = ctk.CTkButton(
            btn_frame, text="Сохранить блок",
            width=220, height=46, corner_radius=16,
            fg_color="#5B62E5", hover_color="#7077EC",
            text_color="#ffffff",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._save_block,
        )
        self.save_btn.pack()
        self._update_save_btn()

    def _on_answer(self, question_id, value):
        if value is None:
            self.answers.pop(question_id, None)
        else:
            self.answers[question_id] = value
        self._update_save_btn()

    def _update_save_btn(self):
        all_answered = len(self.answers) == len(self.block.questions)
        if all_answered:
            self.save_btn.configure(
                state="normal", fg_color="#5B62E5", text_color="#ffffff"
            )
        else:
            self.save_btn.configure(
                state="disabled", fg_color="#E8EBF6", text_color="#8E94B0"
            )

    def _save_block(self):
        self.app.app_state.answers[self.block.id] = dict(self.answers)
        self.app.show_block_select()

    def _go_back(self):
        self.app.show_block_select()
