import tkinter as tk
import customtkinter as ctk


class TemplatePreview(ctk.CTkFrame):
    """Масштабируемое превью spec["layout"] на обычном tkinter Canvas."""

    def __init__(self, master, spec=None, target_width=700):
        super().__init__(master, fg_color="transparent")
        self._target_w = target_width
        self._canvas = None
        if spec:
            self.set_spec(spec)

    def set_spec(self, spec):
        if self._canvas is not None:
            self._canvas.destroy()

        src_w = spec["canvas"]["width"]
        src_h = spec["canvas"]["height"]
        scale = self._target_w / src_w
        h = int(src_h * scale)

        self._canvas = tk.Canvas(
            self, width=self._target_w, height=h,
            bg=spec["palette"]["bg"], highlightthickness=1,
            highlightbackground=spec["palette"]["border"],
        )
        self._canvas.pack()
        for node in spec["layout"]:
            self._draw_node(node, scale)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        c = self._canvas
        r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
        if r <= 1:
            return c.create_rectangle(x1, y1, x2, y2, **kw)
        pts = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return c.create_polygon(pts, smooth=True, **kw)

    def _draw_node(self, n, s):
        t = n["type"]
        x, y = n["x"] * s, n["y"] * s
        w, h = n["w"] * s, n["h"] * s
        c = self._canvas

        if t in ("frame", "image", "bar", "button", "chip"):
            fill = n.get("fill", "#FFFFFF")
            stroke = n.get("stroke", "")
            width = n.get("stroke_width", 1)
            self._rounded_rect(
                x, y, x + w, y + h, n.get("radius", 0) * s,
                fill=fill, outline=stroke or fill, width=width,
            )
            if t == "image":
                c.create_line(x, y, x + w, y + h, fill="#FFFFFF", stipple="gray50")
                c.create_line(x + w, y, x, y + h, fill="#FFFFFF", stipple="gray50")
            if t in ("button", "chip") and n.get("label"):
                fs = max(7, int((13 if t == "button" else 11) * s))
                c.create_text(
                    x + w / 2, y + h / 2, text=n["label"],
                    fill=n.get("text_color", "#FFFFFF"),
                    font=("Segoe UI", fs, "bold"),
                )
        elif t == "text":
            fs = max(7, int(n.get("size", 14) * s * 0.92))
            weight = "bold" if n.get("bold") else "normal"
            family = "Georgia" if n.get("serif") else "Segoe UI"
            anchor = {"w": "w", "center": "center", "e": "e"}.get(n.get("anchor", "w"), "w")
            kw = {}
            wrap = n.get("wrap")
            if wrap:
                kw["width"] = wrap * s
            c.create_text(
                x, y - fs * 0.35, text=n.get("label", ""),
                fill=n.get("color", "#000000"),
                font=(family, fs, weight), anchor=anchor,
                justify="center" if anchor == "center" else "left", **kw
            )

        for child in n.get("children", []):
            self._draw_node(child, s)
