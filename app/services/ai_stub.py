import sys

from services.mlp_model import predict_stack, predict_stack_ensemble
from services.stack_info import (
    get_stack, get_design, SIMILAR_SITES, SIMILAR_DESKTOP,
)
from services.site_analyzer import analyze_site, extract_palette, is_online_available


def _flatten_answers(answers):
    flat = {}
    for block_answers in answers.values():
        if isinstance(block_answers, dict):
            flat.update(block_answers)
    return flat


def _extract_url_from_answer(ans, key):
    val = ans.get(key)
    if isinstance(val, dict):
        text = val.get("text", "")
        if text and "." in text:
            return text.strip()
    if isinstance(val, str) and val.startswith("http"):
        return val
    return None


def _sphere_of(flat, project_type):
    sphere = flat.get("w_d0" if project_type == "website" else "d_d0", "other")
    if isinstance(sphere, dict):
        return sphere.get("value", "other")
    return sphere


def get_offline_result(answers, project_type):
    flat = _flatten_answers(answers)
    label, top3 = predict_stack_ensemble(flat, project_type)

    return {
        "label": label,
        "stack": get_stack(label, project_type),
        "design": get_design(_sphere_of(flat, project_type), project_type, flat),
        "top3": top3,
    }


def get_online_result(answers, project_type):
    flat = _flatten_answers(answers)
    result = {
        "label": None,
        "stack": {},
        "design": {},
        "similar_sites": [],
        "site_analysis": None,
        "palette": [],
        "error": None,
    }

    label, _ = predict_stack(flat, project_type)
    result["label"] = label
    result["stack"] = get_stack(label, project_type)
    result["design"] = get_design(_sphere_of(flat, project_type), project_type, flat)

    if project_type == "website":
        site_type = flat.get("w2", "other")
        if isinstance(site_type, dict):
            site_type = site_type.get("value", "other")
        result["similar_sites"] = list(
            SIMILAR_SITES.get(site_type, SIMILAR_SITES.get("corporate", []))
        )
    else:
        app_type = flat.get("d2", "other")
        if isinstance(app_type, dict):
            app_type = app_type.get("value", "other")
        result["similar_sites"] = SIMILAR_DESKTOP.get(app_type, SIMILAR_DESKTOP.get("other", []))

    if project_type == "website":
        user_url = _extract_url_from_answer(flat, "w4")
        palette_url = _extract_url_from_answer(flat, "w_d4")
    else:
        user_url = _extract_url_from_answer(flat, "d5")
        palette_url = None

    out = sys.__stdout__
    print(f"[online] w_d4={flat.get('w_d4')}, w4={flat.get('w4')}, d5={flat.get('d5')}", file=out)
    print(f"[online] palette_url={palette_url}, user_url={user_url}", file=out)

    if user_url and is_online_available():
        analysis = analyze_site(user_url)
        if "error" not in analysis:
            result["site_analysis"] = analysis
        else:
            result["error"] = f"Не удалось проанализировать {user_url}: {analysis['error']}"
    elif user_url and not is_online_available():
        result["error"] = "Нет подключения к интернету для анализа сайта"

    target_palette_url = palette_url or user_url
    print(f"[online] target_palette_url={target_palette_url}", file=out)
    if target_palette_url and is_online_available():
        print(f"[online] extracting palette from {target_palette_url}", file=out)
        palette = extract_palette(target_palette_url)
        print(f"[online] palette result: {palette}", file=out)
        if palette:
            result["palette"] = palette
    else:
        print(f"[online] palette skipped: url={target_palette_url}, "
              f"online={is_online_available() if target_palette_url else 'N/A'}", file=out)

    return result


def analyze(answers):
    """Оставлено для обратной совместимости — экран результатов её не вызывает."""
    return "Используйте обновлённый экран результатов"
