import customtkinter as ctk

BLOCK_COLORS = ["#BFC4FF", "#FFBCA8", "#A8E8BC", "#A8D2F8", "#FFCF8A", "#C8A4F0", "#A0F0C8", "#FFA8C8"]


class BlockCard(ctk.CTkFrame):
    def __init__(self, master, block, status_text, color_index, on_click):
        color = BLOCK_COLORS[color_index % len(BLOCK_COLORS)]
        super().__init__(master, fg_color=color, corner_radius=16)

        ctk.CTkLabel(
            self, text=block.title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#15173A",
        ).pack(padx=20, pady=(16, 2), anchor="w")

        q_count = len(block.questions)
        ctk.CTkLabel(
            self, text=f"{q_count} вопросов",
            font=ctk.CTkFont(size=12),
            text_color="#2A2F55",
        ).pack(padx=20, pady=(0, 6), anchor="w")

        ctk.CTkLabel(
            self, text=status_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1B2046",
        ).pack(padx=20, pady=(0, 14), anchor="w")

        self._bind_recursive(self, on_click)

    def _bind_recursive(self, widget, callback):
        widget.bind("<Button-1>", lambda e: callback())
        for child in widget.winfo_children():
            self._bind_recursive(child, callback)
