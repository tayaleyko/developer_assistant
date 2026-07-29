from dataclasses import dataclass, field


@dataclass
class Option:
    value: str
    label: str
    hint: str = ""
    text_placeholder: str = ""
    upload: bool = False


@dataclass
class Question:
    id: str
    text: str
    type: str
    options: list[Option] = field(default_factory=list)
    hint: str = ""
    has_text_input: bool = False


@dataclass
class Block:
    id: str
    title: str
    order: int = 0
    questions: list[Question] = field(default_factory=list)
