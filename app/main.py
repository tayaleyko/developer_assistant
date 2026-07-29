import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr, sys.__stdout__, sys.__stderr__):
    try:
        if _stream is not None:
            _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import customtkinter as ctk

from loader import load_json, load_initial_question, load_blocks
from state import AppState
from screens.home import HomeScreen
from screens.project_type import ProjectTypeScreen
from screens.block_select import BlockSelectScreen
from screens.quiz import QuizScreen
from screens.result import ResultScreen


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ассистент разработчика")
        self.geometry("960x720")
        self.minsize(800, 600)
        self.configure(fg_color="#F0F2FB")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        json_path = Path(__file__).resolve().parent.parent / "questions.json"
        self.raw_data = load_json(json_path)
        self.initial_question = load_initial_question(self.raw_data)
        self.app_state = AppState()

        self._current = None
        self._bind_global_hotkeys()
        self.show_home()

    def _bind_global_hotkeys(self):
        """Ctrl+A / C / V / X для всех Entry-виджетов в приложении."""
        def _select_all(e):
            w = e.widget
            if hasattr(w, "select_range"):
                w.select_range(0, "end")
                w.icursor("end")
                return "break"

        def _paste(e):
            w = e.widget
            if not hasattr(w, "insert"):
                return
            try:
                text = w.clipboard_get()
            except Exception:
                return
            if hasattr(w, "select_present") and w.select_present():
                w.delete("sel.first", "sel.last")
            w.insert("insert", text)
            return "break"

        def _copy(e):
            w = e.widget
            if hasattr(w, "select_present") and w.select_present():
                w.clipboard_clear()
                w.clipboard_append(w.selection_get())
            return "break"

        def _cut(e):
            w = e.widget
            if hasattr(w, "select_present") and w.select_present():
                w.clipboard_clear()
                w.clipboard_append(w.selection_get())
                w.delete("sel.first", "sel.last")
            return "break"

        for seq, handler in [
            ("<Control-a>", _select_all), ("<Control-A>", _select_all),
            ("<Control-v>", _paste), ("<Control-V>", _paste),
            ("<Control-c>", _copy), ("<Control-C>", _copy),
            ("<Control-x>", _cut), ("<Control-X>", _cut),
        ]:
            self.bind_all(seq, handler)

    def set_platform(self, platform_value):
        self.app_state.project_type = platform_value
        blocks = load_blocks(self.raw_data, platform_value)
        self.app_state.set_blocks(blocks)

    def _switch(self, screen_cls, **kwargs):
        if self._current:
            self._current.pack_forget()
            self._current.destroy()
        self._current = screen_cls(self, **kwargs)
        self._current.pack(fill="both", expand=True)

    def show_home(self):
        self._switch(HomeScreen)

    def show_project_type(self):
        self._switch(ProjectTypeScreen)

    def show_block_select(self):
        self._switch(BlockSelectScreen)

    def show_quiz(self, block_id):
        self._switch(QuizScreen, block_id=block_id)

    def show_result(self):
        self._switch(ResultScreen)


if __name__ == "__main__":
    App().mainloop()
