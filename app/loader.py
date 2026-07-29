import json
from pathlib import Path
from models import Option, Question, Block

SKIP_VALUE = "skip"


def _parse_options(raw_options):
    return [
        Option(
            o["value"],
            o["label"],
            hint=o.get("hint", ""),
            text_placeholder=o.get("textPlaceholder", ""),
            upload=o.get("upload", False),
        )
        for o in raw_options
    ]


def _parse_questions(raw_questions):
    return [
        Question(
            id=q["id"],
            text=q["text"],
            type=q["type"],
            options=_parse_options(q.get("options", [])),
            hint=q.get("hint", ""),
            has_text_input=q.get("hasTextInput", False),
        )
        for q in raw_questions
    ]


def _parse_blocks(raw_blocks):
    blocks = [
        Block(
            id=b["id"],
            title=b["title"],
            order=b.get("order", 0),
            questions=_parse_questions(b.get("questions", [])),
        )
        for b in raw_blocks
    ]
    blocks.sort(key=lambda b: b.order)
    return blocks


def load_json(path: Path) -> dict:
    # BOM встречается в файлах, сохранённых из «Блокнота»
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def load_initial_question(data: dict) -> Question:
    iq = data["initialQuestion"]
    return Question(
        id=iq["id"],
        text=iq["text"],
        type=iq["type"],
        options=_parse_options(iq.get("options", [])),
    )


def load_blocks(data: dict, platform: str) -> list[Block]:
    return _parse_blocks(data.get(platform, {}).get("blocks", []))
