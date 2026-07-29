import tkinter.filedialog as filedialog
from pathlib import Path
import customtkinter as ctk


class QuestionCard(ctk.CTkFrame):
    def __init__(self, master, question, on_answer, current_answer=None):
        super().__init__(
            master, fg_color="#FFFFFF", corner_radius=16,
            border_width=1, border_color="#D6DAEC",
        )
        self.question = question
        self.on_answer = on_answer

        ctk.CTkLabel(
            self, text=question.text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#15173A",
            wraplength=620, anchor="w", justify="left",
        ).pack(padx=20, pady=(16, 2), anchor="w")

        if question.hint:
            ctk.CTkLabel(
                self, text=question.hint,
                font=ctk.CTkFont(size=12),
                text_color="#5B62E5",
                wraplength=620, anchor="w", justify="left",
            ).pack(padx=20, pady=(0, 6), anchor="w")

        opts_frame = ctk.CTkFrame(self, fg_color="transparent")
        opts_frame.pack(padx=20, pady=(4, 16), anchor="w", fill="x")

        self._text_entries = {}
        self._file_paths = {}
        self._upload_frames = {}

        if question.type == "single":
            # ответ приходит либо строкой "yes", либо {"value": "yes", "text": "..."}
            if isinstance(current_answer, dict):
                initial_val = current_answer.get("value", "")
            elif isinstance(current_answer, str):
                initial_val = current_answer
            else:
                initial_val = ""
            self._radio_var = ctk.StringVar(value=initial_val)
            for opt in question.options:
                label_text = opt.label
                if opt.hint:
                    label_text += f"  ({opt.hint})"

                rb = ctk.CTkRadioButton(
                    opts_frame, text=label_text,
                    variable=self._radio_var, value=opt.value,
                    font=ctk.CTkFont(size=13),
                    text_color="#15173A",
                    fg_color="#5B62E5", hover_color="#7077EC",
                    border_color="#9AA0CE",
                    command=self._on_radio,
                )
                rb.pack(anchor="w", pady=3)

                if opt.text_placeholder:
                    entry = ctk.CTkEntry(
                        opts_frame,
                        placeholder_text=opt.text_placeholder,
                        font=ctk.CTkFont(size=12),
                        fg_color="#F4F6FE", text_color="#15173A",
                        placeholder_text_color="#8E94B0",
                        border_color="#5B62E5", corner_radius=10,
                        width=400, height=32,
                    )
                    self._bind_hotkeys(entry)
                    entry.bind("<KeyRelease>", lambda e, v=opt.value: self._on_text_change(v))
                    entry.bind("<FocusOut>", lambda e, v=opt.value: self._on_text_change(v))
                    self._text_entries[opt.value] = entry
                    if isinstance(current_answer, dict) and current_answer.get("value") == opt.value:
                        saved_text = current_answer.get("text", "")
                        if saved_text:
                            entry.insert(0, saved_text)

                if opt.upload:
                    file_frame = ctk.CTkFrame(
                        opts_frame,
                        fg_color="#DDE0FB", corner_radius=10,
                        border_width=2, border_color="#5B62E5",
                    )
                    file_lbl = ctk.CTkLabel(
                        file_frame, text="Выбрать файл",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#5B62E5", cursor="hand2",
                    )
                    file_lbl.pack(padx=16, pady=8)
                    file_lbl.bind(
                        "<Button-1>",
                        lambda e, v=opt.value, lbl=file_lbl: self._pick_file(v, lbl),
                    )
                    self._upload_frames[opt.value] = file_frame
                    self._file_paths[opt.value] = None

            self._toggle_conditional_fields()
        else:
            self._check_vars = {}
            for opt in question.options:
                selected = current_answer is not None and opt.value in current_answer
                var = ctk.BooleanVar(value=selected)
                self._check_vars[opt.value] = var
                label_text = opt.label
                if opt.hint:
                    label_text += f"  ({opt.hint})"
                cb = ctk.CTkCheckBox(
                    opts_frame, text=label_text,
                    variable=var,
                    font=ctk.CTkFont(size=13),
                    text_color="#15173A",
                    fg_color="#5B62E5", hover_color="#7077EC",
                    border_color="#9AA0CE",
                    command=self._on_check,
                )
                cb.pack(anchor="w", pady=3)

    def _on_text_change(self, opt_value):
        if self._radio_var.get() == opt_value:
            text = self._text_entries[opt_value].get().strip()
            self.on_answer(self.question.id, {"value": opt_value, "text": text} if text else opt_value)

    def _toggle_conditional_fields(self):
        """Поля ввода и загрузки видны только у выбранного варианта."""
        val = self._radio_var.get()
        for opt_val, entry in self._text_entries.items():
            if opt_val == val:
                entry.pack(anchor="w", padx=(24, 0), pady=(2, 4))
                entry.focus_set()
            else:
                entry.pack_forget()
        for opt_val, frame in self._upload_frames.items():
            if opt_val == val:
                frame.pack(anchor="w", padx=(24, 0), pady=(4, 6))
            else:
                frame.pack_forget()

    def _on_radio(self):
        val = self._radio_var.get()
        self._toggle_conditional_fields()
        if val and val in self._text_entries:
            text = self._text_entries[val].get().strip()
            self.on_answer(self.question.id, {"value": val, "text": text} if text else val)
        elif val and val in self._file_paths:
            file = self._file_paths.get(val)
            self.on_answer(self.question.id, {"value": val, "file": file} if file else val)
        else:
            self.on_answer(self.question.id, val)

    @staticmethod
    def _bind_hotkeys(entry):
        """CTkEntry не пробрасывает Ctrl+A/C/V/X — вешаем их на внутренний Entry."""
        widget = entry._entry if hasattr(entry, "_entry") else entry

        def _select_all(e):
            widget.select_range(0, "end")
            widget.icursor("end")
            return "break"

        def _paste(e):
            try:
                text = widget.clipboard_get()
            except Exception:
                return
            if widget.select_present():
                widget.delete("sel.first", "sel.last")
            widget.insert("insert", text)
            widget.event_generate("<KeyRelease>")  # чтобы сработал _on_text_change
            return "break"

        def _copy(e):
            if widget.select_present():
                widget.clipboard_clear()
                widget.clipboard_append(widget.selection_get())
            return "break"

        def _cut(e):
            if widget.select_present():
                widget.clipboard_clear()
                widget.clipboard_append(widget.selection_get())
                widget.delete("sel.first", "sel.last")
            return "break"

        widget.bind("<Control-a>", _select_all)
        widget.bind("<Control-A>", _select_all)
        widget.bind("<Control-v>", _paste)
        widget.bind("<Control-V>", _paste)
        widget.bind("<Control-c>", _copy)
        widget.bind("<Control-C>", _copy)
        widget.bind("<Control-x>", _cut)
        widget.bind("<Control-X>", _cut)

    def _pick_file(self, opt_value, label):
        path = filedialog.askopenfilename(
            title="Выберите файл логотипа",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.svg *.ico"), ("Все файлы", "*.*")],
        )
        if path:
            self._file_paths[opt_value] = path
            label.configure(text=Path(path).name)
            if self._radio_var.get() == opt_value:
                self.on_answer(self.question.id, {"value": opt_value, "file": path})

    def _on_check(self):
        active = [v for v, var in self._check_vars.items() if var.get()]
        self.on_answer(self.question.id, active or None)
