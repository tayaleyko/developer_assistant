from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent / "output"
OUT_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT / "app"))

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Установите matplotlib: pip install matplotlib")
    sys.exit(1)


def load_metrics(platform: str) -> dict:
    path = MODEL_DIR / f"{platform}_metrics.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def plot_accuracy_comparison():
    """Рис. 3.X — Accuracy на обучении и тесте (website / desktop)."""
    platforms = ["website", "desktop"]
    labels_ru = ["Веб-сайт", "Десктоп"]
    train_acc, test_acc = [], []

    for p in platforms:
        m = load_metrics(p)
        train_acc.append(m["train_accuracy"])
        test_acc.append(m["test_accuracy"])

    x = np.arange(len(platforms))
    w = 0.35
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(x - w / 2, train_acc, w, label="Train accuracy", color="#64B5F6")
    ax.bar(x + w / 2, test_acc, w, label="Test accuracy", color="#1976D2")
    ax.set_ylabel("Accuracy")
    ax.set_xticks(x)
    ax.set_xticklabels(labels_ru)
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.set_title("Сравнение точности MLP на обучающей и тестовой выборках")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = OUT_DIR / "fig_3_3_accuracy_train_test.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Сохранено: {out}")


def plot_metrics_bars():
    """Рис. 3.X — F1 macro и log-loss (test) для website и desktop."""
    platforms = ["website", "desktop"]
    labels_ru = ["Веб-сайт", "Десктоп"]
    f1, ll = [], []
    for p in platforms:
        m = load_metrics(p)
        f1.append(m["f1_macro"])
        ll.append(m["test_logloss"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
    x = np.arange(2)
    ax1.bar(x, f1, color="#81C784")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels_ru)
    ax1.set_ylabel("F1-score (macro)")
    ax1.set_ylim(0, 1.05)
    ax1.set_title("F1 на тесте")
    ax1.grid(axis="y", alpha=0.3)

    ax2.bar(x, ll, color="#FFB74D")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels_ru)
    ax2.set_ylabel("Log-loss (test)")
    ax2.set_title("Кросс-энтропия на тесте")
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle("Метрики качества классификации MLP", fontsize=12)
    fig.tight_layout()
    out = OUT_DIR / "fig_3_3_f1_logloss.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Сохранено: {out}")


def plot_loss_curve_note():
    from sklearn.model_selection import train_test_split
    from sklearn.neural_network import MLPClassifier
    import pandas as pd
    import joblib

    from services.encoder import SurveyEncoder

    platform = "website"
    csv_path = DATA_DIR / f"{platform}.csv"
    if not csv_path.exists():
        print("Пропуск loss_curve: нет CSV")
        return

    df = pd.read_csv(csv_path)
    encoder = SurveyEncoder()
    encoder.fit(df)
    X = encoder.transform(df)
    y = encoder.transform_target(df)
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42, stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42
        )

    mlp = MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        learning_rate_init=0.001,
        batch_size=32,
        max_iter=300,
        early_stopping=True,
        validation_fraction=0.176,
        n_iter_no_change=20,
        alpha=0.001,
        random_state=42,
        verbose=False,
    )
    mlp.fit(X_train, y_train)

    if not hasattr(mlp, "loss_curve_") or len(mlp.loss_curve_) == 0:
        print("Пропуск loss_curve: пустая кривая")
        return

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(range(1, len(mlp.loss_curve_) + 1), mlp.loss_curve_, color="#5C6BC0")
    ax.set_xlabel("Итерация (батч / эпоха)")
    ax.set_ylabel("Loss")
    ax.set_title(f"Динамика функции потерь при обучении MLP ({platform})")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = OUT_DIR / "fig_3_3_loss_curve_website.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Сохранено: {out} (переобучение ~{mlp.n_iter_} итераций)")


def plot_confusion_matrix(platform: str = "website"):
    """Рис. 3.X — Матрица ошибок на тестовой выборке."""
    import joblib
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    from services.encoder import SurveyEncoder

    model_path = MODEL_DIR / f"{platform}_mlp.pkl"
    enc_path = MODEL_DIR / f"{platform}_encoder.pkl"
    csv_path = DATA_DIR / f"{platform}.csv"
    if not all(p.exists() for p in (model_path, enc_path, csv_path)):
        print(f"Пропуск confusion matrix для {platform}: нет файлов")
        return

    df = pd.read_csv(csv_path)
    encoder = SurveyEncoder.load(enc_path)
    X = encoder.transform(df)
    y = encoder.transform_target(df)
    try:
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42, stratify=y
        )
    except ValueError:
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42
        )

    mlp = joblib.load(model_path)
    y_pred = mlp.predict(X_test)
    labels = [encoder.decode_label(i) for i in sorted(set(y_test) | set(y_pred))]

    cm = confusion_matrix(y_test, y_pred, labels=sorted(set(y_test) | set(y_pred)))
    fig, ax = plt.subplots(figsize=(10, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, xticks_rotation=45, cmap="Blues", colorbar=False)
    ax.set_title(f"Матрица ошибок MLP ({platform}, тест 15 %)")
    fig.tight_layout()
    out = OUT_DIR / f"fig_3_3_confusion_matrix_{platform}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Сохранено: {out}")


def main():
    plot_accuracy_comparison()
    plot_metrics_bars()
    plot_confusion_matrix("website")
    plot_confusion_matrix("desktop")
    # Опционально: кривая loss (занимает ~30–60 с)
    plot_loss_curve_note()
    print("\nГотово. Вставьте PNG из docs/chapter3/output/ в диплом.")


if __name__ == "__main__":
    main()
