"""Генерация fig_3_3_mlp_architecture.puml с полной топологией MLP (website)."""
from pathlib import Path

# Фактические размерности tech-модели website (models/website_metrics.json)
LAYER_SIZES = [75, 128, 64, 12]
LAYER_LABELS = [
    "**входной слой**",
    "**скрытый слой 1**\\n128 · ReLU",
    "**скрытый слой 2**\\n64 · ReLU",
    "**выходной слой**\\n12 · Softmax",
]
PACKAGE_IDS = ["P1", "P2", "P3", "P4"]
LAYER_PREFIXES = ["in", "h1", "h2", "out"]


def node_id(layer_idx: int, i: int) -> str:
    return f"{LAYER_PREFIXES[layer_idx]}{i}"


def main() -> None:
    out_path = Path(__file__).with_name("fig_3_3_mlp_architecture_full.puml")
    print("Внимание: полная схема (~19k строк) не рендерится в PlantUML IDE.")
    print("Для диплома используйте fig_3_3_mlp_architecture.puml (схематичная).")
    lines: list[str] = [
        "@startuml fig_3_3_mlp_architecture",
        "' Рисунок 3.X — Архитектура MLP (website: 75 → 128 → 64 → 12)",
        "' Сгенерировано generate_fig_3_3_mlp_architecture.py",
        "",
        "left to right direction",
        "",
        "skinparam shadowing false",
        'skinparam defaultFontName "Segoe UI"',
        "skinparam packageBorderStyle dashed",
        "skinparam packageBorderColor #8B0000",
        "skinparam packageFontColor #8B0000",
        "skinparam packageBackgroundColor white",
        "skinparam usecaseBackgroundColor white",
        "skinparam usecaseBorderColor black",
        "skinparam ArrowColor black",
        "skinparam ArrowThickness 1",
        "skinparam nodesep 1",
        "skinparam ranksep 8",
        "skinparam NoteBorderColor #8B0000",
        "skinparam NoteFontColor #8B0000",
        "",
        "title Рисунок 3.X — Архитектура MLP\\n(website: 75 → 128 → 64 → 12)",
        "",
    ]

    # Слои в пунктирных рамках
    for layer_idx, (size, pkg, label) in enumerate(
        zip(LAYER_SIZES, PACKAGE_IDS, LAYER_LABELS)
    ):
        lines.append(f'package " " as {pkg} {{')
        for i in range(size):
            lines.append(f'  () " " as {node_id(layer_idx, i)}')
        lines.append("}")
        lines.append(f"note bottom of {pkg} : {label}")
        lines.append("")

    # Вертикальное выравнивание нейронов внутри слоя
    for layer_idx, size in enumerate(LAYER_SIZES):
        for i in range(size - 1):
            a = node_id(layer_idx, i)
            b = node_id(layer_idx, i + 1)
            lines.append(f"{a} -[hidden]down- {b}")

    lines.append("")

    # Внешние подписи (как в учебной схеме; нейронов в слоях — 75 и 12)
    lines.extend([
        '() " " as gin0 #white;line:white',
        '() " " as gin1 #white;line:white',
        '() " " as gout0 #white;line:white',
        "",
        "gin0 -right-> in0 : **вход**<sub>0</sub>",
        "gin1 -right-> in1 : **вход**<sub>1</sub>",
        "out0 -right-> gout0 : **выход**<sub>0</sub>",
        "",
        'note top of P1 : … **вход**<sub>2</sub> … **вход**<sub>74</sub>',
        'note top of P4 : … **выход**<sub>1</sub> … **выход**<sub>11</sub>',
        "",
    ])

    # Полносвязные связи между соседними слоями
    for layer_idx in range(len(LAYER_SIZES) - 1):
        n_in = LAYER_SIZES[layer_idx]
        n_out = LAYER_SIZES[layer_idx + 1]
        for i in range(n_in):
            for j in range(n_out):
                lines.append(f"{node_id(layer_idx, i)} --> {node_id(layer_idx + 1, j)}")

    lines.extend(["", "@enduml", ""])

    out_path.write_text("\n".join(lines), encoding="utf-8")
    edge_count = sum(
        LAYER_SIZES[i] * LAYER_SIZES[i + 1] for i in range(len(LAYER_SIZES) - 1)
    )
    print(f"Written: {out_path}")
    print(f"Nodes: {sum(LAYER_SIZES)}, edges: {edge_count}, lines: {len(lines)}")


if __name__ == "__main__":
    main()
