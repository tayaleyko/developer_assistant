import sys


def fix_scroll(scrollable_frame):
    """Прокрутка колесом внутри CTkScrollableFrame.

    На macOS delta приходит уже в «шагах», на Windows и Linux она кратна 120.
    """
    canvas = scrollable_frame._parent_canvas
    step = 1 if sys.platform == "darwin" else 120
    canvas.unbind_all("<MouseWheel>")
    canvas.bind_all("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-e.delta // step, "units"))
