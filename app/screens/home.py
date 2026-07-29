import customtkinter as ctk
from storage import load_progress


class HomeScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F0F2FB")
        self.app = master
        self._has_progress = load_progress() is not None

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.43, anchor="center")

        accent = ctk.CTkFrame(container, fg_color="#5B62E5", corner_radius=18, width=68, height=68)
        accent.pack(pady=(0, 22))
        accent.pack_propagate(False)
        ctk.CTkLabel(accent, text="AI", font=ctk.CTkFont(size=24, weight="bold"),
                      text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            container, text="Ассистент разработчика",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color="#15173A",
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            container,
            text="Ответьте на вопросы о вашем проекте\nи получите рекомендации по технологиям",
            font=ctk.CTkFont(size=15),
            text_color="#5A5F7E",
            justify="center",
        ).pack(pady=(0, 44))

        ctk.CTkButton(
            container, text="Начать",
            width=260, height=52, corner_radius=16,
            fg_color="#5B62E5", hover_color="#7077EC",
            text_color="#ffffff",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._on_start,
        ).pack()

    def _on_start(self):
        self.app.app_state.clear()
        self.app.show_project_type()
