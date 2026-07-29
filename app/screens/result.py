import threading
from tkinter import filedialog
import customtkinter as ctk
from ui import fix_scroll
from services.ai_stub import get_offline_result, get_online_result
from services.template_generator import (
    generate_template, spec_to_html, spec_to_json,
)
from widgets.template_preview import TemplatePreview


class ResultScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F0F2FB")
        self.app = master
        self._mode = "offline"          # текущий режим
        self._offline_data = None
        self._online_data = None
        self._online_loading = False
        self._tpl_seed = 0              # вариант интерфейсного шаблона
        self._tpl_spec = None
        self._tpl_preview = None
        self._tpl_palette_override = None
        self._current_card = None

        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=24, pady=(24, 12))

        self._btn_offline = ctk.CTkButton(
            mode_frame, text="Автономный режим",
            width=220, height=38, corner_radius=14,
            fg_color="#5B62E5", hover_color="#7077EC",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._switch_mode("offline"),
        )
        self._btn_offline.pack(side="left", padx=(0, 8))

        self._btn_online = ctk.CTkButton(
            mode_frame, text="Режим с AI",
            width=220, height=38, corner_radius=14,
            fg_color="#DDE0FB", hover_color="#C7CCF6",
            border_width=1, border_color="#5B62E5",
            text_color="#5B62E5",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self._switch_mode("online"),
        )
        self._btn_online.pack(side="left")

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))
        fix_scroll(self._scroll)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=24, pady=(8, 20))
        ctk.CTkButton(
            bottom, text="Пройти заново",
            width=200, height=44, corner_radius=14,
            fg_color="#DDE0FB", hover_color="#C7CCF6",
            border_width=1, border_color="#5B62E5",
            text_color="#5B62E5",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._restart,
        ).pack()

        self._run_offline()

    def _switch_mode(self, mode):
        self._mode = mode
        if mode == "offline":
            self._btn_offline.configure(
                fg_color="#5B62E5", text_color="#ffffff", border_width=0,
            )
            self._btn_online.configure(
                fg_color="#DDE0FB", text_color="#5B62E5",
                border_width=1, border_color="#5B62E5",
            )
            self._render_offline()
        else:
            self._btn_online.configure(
                fg_color="#5B62E5", text_color="#ffffff", border_width=0,
            )
            self._btn_offline.configure(
                fg_color="#DDE0FB", text_color="#5B62E5",
                border_width=1, border_color="#5B62E5",
            )
            if self._online_data is None and not self._online_loading:
                self._run_online()
            else:
                self._render_online()

    def _run_offline(self):
        answers = self.app.app_state.answers
        pt = self.app.app_state.project_type
        try:
            self._offline_data = get_offline_result(answers, pt)
        except Exception as e:
            self._offline_data = {"error": str(e)}
        self._render_offline()

    def _render_offline(self):
        self._clear_scroll()
        data = self._offline_data
        if not data:
            self._add_label("Нет данных", bold=True)
            self._render_user_answers()
            return

        if "error" in data:
            self._add_label(f"Ошибка: {data['error']}", color="#E25A5A")
            self._render_user_answers()
            return

        self._add_section("Технологии")
        for key, val in data.get("stack", {}).items():
            self._add_kv(key, val)

        self._add_section("Дизайн")
        for key, val in data.get("design", {}).items():
            self._add_kv(key, val)

        self._render_template_section()
        self._render_user_answers()

    def _run_online(self):
        self._online_loading = True
        self._clear_scroll()
        self._add_label("Анализ сайтов… Пожалуйста, подождите.", bold=True)

        def worker():
            answers = self.app.app_state.answers
            pt = self.app.app_state.project_type
            try:
                self._online_data = get_online_result(answers, pt)
            except Exception as e:
                self._online_data = {"error": str(e)}
            self._online_loading = False
            self.after(0, self._render_online)

        threading.Thread(target=worker, daemon=True).start()

    def _render_online(self):
        self._clear_scroll()
        data = self._online_data

        if not data:
            self._add_label("Нет данных", bold=True)
            self._render_user_answers()
            return

        err = data.get("error")
        if err:
            self._add_label(f"Ошибка: {err}", color="#E25A5A")

        stack = data.get("stack", {})
        if stack:
            self._add_section("Технологии")
            for key, val in stack.items():
                self._add_kv(key, val)

        design = data.get("design", {})
        if design:
            self._add_section("Дизайн")
            for key, val in design.items():
                self._add_kv(key, val)

        sites = data.get("similar_sites", [])
        if sites:
            self._add_section("Похожие проекты")
            for s in sites:
                self._add_card_label(f"  •  {s}", size=13)

        site_analysis = data.get("site_analysis")
        if site_analysis:
            self._add_section("Анализ указанного сайта")
            for key, val in site_analysis.get("technologies", {}).items():
                self._add_kv(key, val)
            for key, val in site_analysis.get("design", {}).items():
                self._add_kv(key, val)

        palette = data.get("palette", [])
        if palette:
            self._add_section("Палитра цветов (KMeans-кластеризация)")
            self._add_card_label("  ".join(palette), size=13)
            self._render_color_swatches(palette)

        self._render_template_section(palette_override=palette or None)
        self._render_user_answers()

    def _render_template_section(self, palette_override=None):
        self._add_section("Интерфейсный шаблон")
        self._tpl_palette_override = palette_override
        card = self._current_card

        try:
            self._tpl_spec = generate_template(
                self.app.app_state.answers,
                self.app.app_state.project_type,
                palette_override=palette_override,
                seed=self._tpl_seed,
            )
        except Exception as e:
            self._add_card_label(f"Не удалось сгенерировать шаблон: {e}",
                                 color="#E25A5A", size=13)
            return

        meta = self._tpl_spec["meta"]
        subtitle = "Автоматически собран по ответам блока «Дизайн»"
        if meta.get("dark_mode") in ("yes", "optional"):
            subtitle += " · есть тёмная тема (в HTML)"
        self._add_card_label(subtitle, size=12, color="#8A90AC")

        self._tpl_preview = TemplatePreview(card, self._tpl_spec, target_width=700)
        self._tpl_preview.pack(padx=18, pady=(8, 4))

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(padx=18, pady=(6, 16), anchor="w")

        def mk(text, cmd, primary=False):
            return ctk.CTkButton(
                btns, text=text, command=cmd,
                width=150, height=32, corner_radius=10,
                fg_color="#5B62E5" if primary else "#DDE0FB",
                hover_color="#7077EC" if primary else "#C7CCF6",
                text_color="#ffffff" if primary else "#5B62E5",
                border_width=0 if primary else 1,
                border_color="#5B62E5",
                font=ctk.CTkFont(size=12, weight="bold"),
            )

        mk("Ещё вариант", self._tpl_reroll, primary=True).pack(side="left", padx=(0, 8))
        mk("Сохранить HTML…", self._tpl_save_html).pack(side="left", padx=(0, 8))
        mk("Сохранить JSON…", self._tpl_save_json).pack(side="left")

    def _tpl_reroll(self):
        self._tpl_seed += 1
        try:
            self._tpl_spec = generate_template(
                self.app.app_state.answers,
                self.app.app_state.project_type,
                palette_override=self._tpl_palette_override,
                seed=self._tpl_seed,
            )
            self._tpl_preview.set_spec(self._tpl_spec)
        except Exception:
            pass

    def _tpl_save_html(self):
        if not self._tpl_spec:
            return
        path = filedialog.asksaveasfilename(
            title="Сохранить шаблон как HTML",
            defaultextension=".html",
            initialfile="interface_template.html",
            filetypes=[("HTML", "*.html")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(spec_to_html(self._tpl_spec))

    def _tpl_save_json(self):
        if not self._tpl_spec:
            return
        path = filedialog.asksaveasfilename(
            title="Сохранить структуру шаблона (JSON)",
            defaultextension=".json",
            initialfile="interface_template.json",
            filetypes=[("JSON", "*.json")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(spec_to_json(self._tpl_spec))

    def _render_user_answers(self):
        self._add_section("Ваши данные", highlight=False)

        pt = self.app.app_state.project_type
        if pt:
            pt_label = next(
                (o.label for o in self.app.initial_question.options if o.value == pt),
                pt,
            )
            self._add_card_label(f"Тип проекта:  {pt_label}", bold=True, size=16, color="#5A5F7E")

        any_data = False
        for block in self.app.app_state.blocks:
            block_answers = self.app.app_state.answers.get(block.id, {})
            if not block_answers:
                continue
            any_data = True
            self._add_card_label(block.title, bold=True, size=15, color="#5B62E5")
            q_map = {q.id: q for q in block.questions}
            for qid, val in block_answers.items():
                q = q_map.get(qid)
                if not q:
                    continue
                display = self._format_answer(q, val)
                self._add_card_label(f"{q.text}:  {display}", size=13)

        if not any_data:
            self._add_label("Нет данных для отображения", color="#5B62E5")

        self._finish_card()

    def _clear_scroll(self):
        for w in self._scroll.winfo_children():
            w.destroy()

    def _card_parent(self):
        return self._current_card or self._scroll

    def _add_section(self, text, highlight=True):
        self._finish_card()
        card = ctk.CTkFrame(
            self._scroll, fg_color="#FFFFFF", corner_radius=16,
            border_width=2 if highlight else 1,
            border_color="#5B62E5" if highlight else "#D6DAEC",
        )
        card.pack(fill="x", padx=8, pady=(10, 6))
        ctk.CTkLabel(
            card, text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#5B62E5",
        ).pack(padx=18, pady=(14, 6), anchor="w")
        self._current_card = card

    def _finish_card(self):
        self._current_card = None

    def _add_kv(self, key, value):
        ctk.CTkLabel(
            self._card_parent(),
            text=f"{key}:  {value}",
            font=ctk.CTkFont(size=13),
            text_color="#5A5F7E",
            wraplength=680, anchor="w", justify="left",
        ).pack(padx=18, pady=2, anchor="w", fill="x")

    def _add_label(self, text, bold=False, size=14, color="#5A5F7E"):
        weight = "bold" if bold else "normal"
        ctk.CTkLabel(
            self._scroll, text=text,
            font=ctk.CTkFont(size=size, weight=weight),
            text_color=color,
            wraplength=680, anchor="w", justify="left",
        ).pack(padx=8, pady=2, anchor="w")

    def _add_card_label(self, text, bold=False, size=14, color="#5A5F7E"):
        weight = "bold" if bold else "normal"
        ctk.CTkLabel(
            self._card_parent(), text=text,
            font=ctk.CTkFont(size=size, weight=weight),
            text_color=color,
            wraplength=680, anchor="w", justify="left",
        ).pack(padx=18, pady=2, anchor="w")

    def _render_color_swatches(self, palette):
        row = ctk.CTkFrame(self._card_parent(), fg_color="transparent")
        row.pack(padx=18, pady=(6, 8), anchor="w")
        for hex_color in palette:
            swatch = ctk.CTkFrame(
                row, width=40, height=40,
                fg_color=hex_color, corner_radius=8,
                border_width=1, border_color="#D6DAEC",
            )
            swatch.pack(side="left", padx=4)
            swatch.pack_propagate(False)

    def _format_answer(self, question, val):
        if isinstance(val, dict):
            inner = val.get("value", "")
            text = val.get("text", "")
            label = next((o.label for o in question.options if o.value == inner), inner)
            if text:
                return f"{label} — {text}"
            return label
        if isinstance(val, list):
            return ", ".join(
                next((o.label for o in question.options if o.value == v), v)
                for v in val
            )
        return next((o.label for o in question.options if o.value == val), val)

    def _restart(self):
        self.app.app_state.clear()
        self.app.show_home()
