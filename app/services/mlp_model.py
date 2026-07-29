import sys
import json
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, log_loss,
)

from services.encoder import SurveyEncoder

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"


def _print_ranked(items, out):
    for i, (lbl, prob) in enumerate(items, 1):
        bar = "█" * int(prob * 30)
        print(f"    {i}. {lbl:<30s} {prob:.4f} ({prob:.1%})  {bar}", file=out)


def _print_others(items, out):
    if not items:
        return
    print("\n  Остальные (>1%):", file=out)
    for lbl, prob in items:
        print(f"    {lbl:<30s} {prob:.4f} ({prob:.1%})", file=out)


def train_model(platform):
    """Обучить MLP для платформы (website / desktop) и сохранить его на диск."""
    df = pd.read_csv(DATA_DIR / f"{platform}.csv")

    encoder = SurveyEncoder()
    encoder.fit(df)

    X = encoder.transform(df)
    y = encoder.transform_target(df)

    # 15% на тест; валидацию early_stopping выделяет сам из обучающей части
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42, stratify=y,
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.15, random_state=42,
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

    out = sys.__stdout__

    train_acc = mlp.score(X_train, y_train)
    test_acc = mlp.score(X_test, y_test)

    y_pred_test = mlp.predict(X_test)
    y_proba_test = mlp.predict_proba(X_test)
    y_proba_train = mlp.predict_proba(X_train)

    f1_mac = f1_score(y_test, y_pred_test, average="macro", zero_division=0)
    prec_mac = precision_score(y_test, y_pred_test, average="macro", zero_division=0)
    rec_mac = recall_score(y_test, y_pred_test, average="macro", zero_division=0)

    all_labels = sorted(set(y_train) | set(y_test))
    logloss_train = log_loss(y_train, y_proba_train, labels=all_labels)
    logloss_test = log_loss(y_test, y_proba_test, labels=all_labels)

    overfit_gap = train_acc - test_acc

    n_classes = encoder.n_classes
    n_features = X_train.shape[1]
    n_params = (n_features * 128 + 128) + (128 * 64 + 64) + (64 * n_classes + n_classes)

    print(f"\n{'='*60}", file=out)
    print(f"  MLP — {platform}", file=out)
    print(f"{'='*60}", file=out)

    print("\n  ── Архитектура ──", file=out)
    print(f"  Слои:             {n_features} → 128 → 64 → {n_classes}", file=out)
    print("  Активация:        ReLU", file=out)
    print(f"  Параметров:       ~{n_params:,}", file=out)
    print(f"  Оптимизатор:      Adam (lr={mlp.learning_rate_init})", file=out)
    print(f"  L2-регуляризация: α={mlp.alpha}", file=out)
    print(f"  Batch size:       {mlp.batch_size}", file=out)

    print("\n  ── Датасет ──", file=out)
    print(f"  Всего примеров:   {len(X_train) + len(X_test)}", file=out)
    print(f"  Train:            {len(X_train)}  |  Test: {len(X_test)}", file=out)
    print(f"  Признаков (one-hot): {n_features}", file=out)
    print(f"  Классов:          {n_classes}", file=out)

    print("\n  ── Обучение ──", file=out)
    print(f"  Эпох:             {mlp.n_iter_} / {mlp.max_iter}", file=out)
    if getattr(mlp, "best_loss_", None) is not None:
        print(f"  Лучший val loss:  {mlp.best_loss_:.6f}", file=out)
    print(f"  Финальный loss:   {mlp.loss_:.6f}", file=out)

    print("\n  ── Accuracy ──", file=out)
    print(f"  Train accuracy:   {train_acc:.4f}  ({train_acc:.1%})", file=out)
    print(f"  Test  accuracy:   {test_acc:.4f}  ({test_acc:.1%})", file=out)
    if overfit_gap > 0.10:
        print(f"  ⚠  Разрыв train−test: {overfit_gap:.4f} — возможен переобуч.", file=out)
    elif overfit_gap > 0.05:
        print(f"  ⚡ Разрыв train−test: {overfit_gap:.4f} — умеренный", file=out)
    else:
        print(f"  ✓  Разрыв train−test: {overfit_gap:.4f} — в норме", file=out)

    print("\n  ── Cross-Entropy (Log Loss) ──", file=out)
    print(f"  Train log-loss:   {logloss_train:.4f}", file=out)
    print(f"  Test  log-loss:   {logloss_test:.4f}", file=out)

    print("\n  ── Macro-метрики (test) ──", file=out)
    print(f"  Precision:        {prec_mac:.4f}", file=out)
    print(f"  Recall:           {rec_mac:.4f}", file=out)
    print(f"  F1-score:         {f1_mac:.4f}", file=out)

    target_names = [encoder.decode_label(i) for i in sorted(set(y_test) | set(y_pred_test))]
    print("\n  ── Classification Report (test) ──", file=out)
    print(classification_report(y_test, y_pred_test, target_names=target_names, zero_division=0), file=out)

    cm = confusion_matrix(y_test, y_pred_test)
    print("  ── Confusion Matrix ──", file=out)
    print(f"  {cm}", file=out)
    print(f"{'='*60}\n", file=out)

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(mlp, MODEL_DIR / f"{platform}_mlp.pkl")
    encoder.save(MODEL_DIR / f"{platform}_encoder.pkl")

    metrics = {
        "architecture": f"{n_features} → 128 → 64 → {n_classes}",
        "parameters": n_params,
        "lr": mlp.learning_rate_init,
        "alpha": mlp.alpha,
        "batch_size": mlp.batch_size,
        "total_samples": len(X_train) + len(X_test),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features": n_features,
        "classes": n_classes,
        "epochs": f"{mlp.n_iter_} / {mlp.max_iter}",
        "final_loss": round(float(mlp.loss_), 6),
        "train_accuracy": round(float(train_acc), 4),
        "test_accuracy": round(float(test_acc), 4),
        "overfit_gap": round(float(overfit_gap), 4),
        "train_logloss": round(float(logloss_train), 4),
        "test_logloss": round(float(logloss_test), 4),
        "precision_macro": round(float(prec_mac), 4),
        "recall_macro": round(float(rec_mac), 4),
        "f1_macro": round(float(f1_mac), 4),
    }
    if getattr(mlp, "best_loss_", None) is not None:
        metrics["best_val_loss"] = round(float(mlp.best_loss_), 6)
    with open(MODEL_DIR / f"{platform}_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    return mlp, encoder


def _print_cached_metrics(platform):
    metrics_path = MODEL_DIR / f"{platform}_metrics.json"
    if not metrics_path.exists():
        return
    with open(metrics_path, encoding="utf-8") as f:
        m = json.load(f)

    out = sys.__stdout__
    print(f"\n{'='*60}", file=out)
    print(f"  MLP — {platform} (загружено из кэша)", file=out)
    print(f"{'='*60}", file=out)
    print("\n  ── Архитектура ──", file=out)
    print(f"  Слои:             {m.get('architecture', '?')}", file=out)
    print(f"  Параметров:       ~{m.get('parameters', 0):,}", file=out)
    print(f"  Оптимизатор:      Adam (lr={m.get('lr', 0.001)})", file=out)
    print(f"  L2-регуляризация: α={m.get('alpha', 0.001)}", file=out)
    print(f"  Batch size:       {m.get('batch_size', 32)}", file=out)
    print("\n  ── Датасет ──", file=out)
    print(f"  Всего примеров:   {m.get('total_samples', '?')}", file=out)
    print(f"  Train:            {m.get('train_samples', '?')}  |  Test: {m.get('test_samples', '?')}", file=out)
    print(f"  Признаков:        {m.get('features', '?')}", file=out)
    print(f"  Классов:          {m.get('classes', '?')}", file=out)
    print("\n  ── Обучение ──", file=out)
    print(f"  Эпох:             {m.get('epochs', '?')}", file=out)
    if "best_val_loss" in m:
        print(f"  Лучший val loss:  {m['best_val_loss']}", file=out)
    print(f"  Финальный loss:   {m.get('final_loss', '?')}", file=out)
    print("\n  ── Accuracy ──", file=out)
    ta = m.get("train_accuracy", 0)
    tea = m.get("test_accuracy", 0)
    print(f"  Train accuracy:   {ta}  ({ta:.1%})", file=out)
    print(f"  Test accuracy:    {tea}  ({tea:.1%})", file=out)
    gap = m.get("overfit_gap", 0)
    if gap > 0.10:
        print(f"  ⚠  Разрыв train−test: {gap} — возможен переобуч.", file=out)
    elif gap > 0.05:
        print(f"  ⚡ Разрыв train−test: {gap} — умеренный", file=out)
    else:
        print(f"  ✓  Разрыв train−test: {gap} — в норме", file=out)
    print("\n  ── Cross-Entropy (Log Loss) ──", file=out)
    print(f"  Train log-loss:   {m.get('train_logloss', '?')}", file=out)
    print(f"  Test log-loss:    {m.get('test_logloss', '?')}", file=out)
    print("\n  ── Macro-метрики (test) ──", file=out)
    print(f"  Precision:        {m.get('precision_macro', '?')}", file=out)
    print(f"  Recall:           {m.get('recall_macro', '?')}", file=out)
    print(f"  F1-score:         {m.get('f1_macro', '?')}", file=out)
    print(f"{'='*60}\n", file=out)


def _ensure_model(platform):
    model_path = MODEL_DIR / f"{platform}_mlp.pkl"
    encoder_path = MODEL_DIR / f"{platform}_encoder.pkl"
    metrics_path = MODEL_DIR / f"{platform}_metrics.json"

    if model_path.exists() and encoder_path.exists() and metrics_path.exists():
        _print_cached_metrics(platform)
        return

    print(f"Модель для «{platform}» не найдена — запускаю обучение...",
          file=sys.__stdout__)
    train_model(platform)


def predict_stack(answers_flat, platform):
    """Вернуть (label, top3), где top3 — список пар (метка, вероятность)."""
    _ensure_model(platform)

    mlp = joblib.load(MODEL_DIR / f"{platform}_mlp.pkl")
    encoder = SurveyEncoder.load(MODEL_DIR / f"{platform}_encoder.pkl")

    X = encoder.encode_answers(answers_flat)

    label_idx = mlp.predict(X)[0]
    label = encoder.decode_label(label_idx)

    probas = mlp.predict_proba(X)[0]
    top3_idx = np.argsort(probas)[::-1][:3]
    top3 = [(encoder.decode_label(int(i)), float(probas[i])) for i in top3_idx]

    probas_clipped = np.clip(probas, 1e-12, 1.0)
    entropy = -np.sum(probas_clipped * np.log2(probas_clipped))
    max_entropy = np.log2(len(probas))
    confidence = 1.0 - entropy / max_entropy

    out = sys.__stdout__
    print(f"\n{'='*60}", file=out)
    print(f"  MLP Prediction — {platform}", file=out)
    print(f"{'='*60}", file=out)
    print(f"  Предсказание:     {label}", file=out)
    print(f"  Уверенность (p):  {probas[label_idx]:.4f}  ({probas[label_idx]:.1%})", file=out)
    print(f"  Энтропия:         {entropy:.4f} / {max_entropy:.4f} бит", file=out)
    print(f"  Confidence:       {confidence:.4f}  ({confidence:.1%})", file=out)
    print("\n  Топ-3 стека:", file=out)
    _print_ranked(top3, out)

    all_sorted = np.argsort(probas)[::-1]
    others = [(encoder.decode_label(int(i)), float(probas[i]))
              for i in all_sorted[3:] if probas[i] > 0.01]
    _print_others(others, out)

    print(f"{'='*60}\n", file=out)

    return label, top3


def predict_stack_ensemble(answers_flat, platform):
    """Усреднить вероятности tech- и design-моделей. Возвращает (label, top3)."""
    design_name = f"design_{platform}"

    _ensure_model(platform)

    if not (DATA_DIR / f"{design_name}.csv").exists():
        return predict_stack(answers_flat, platform)
    _ensure_model(design_name)

    mlp_tech = joblib.load(MODEL_DIR / f"{platform}_mlp.pkl")
    enc_tech = SurveyEncoder.load(MODEL_DIR / f"{platform}_encoder.pkl")

    mlp_design = joblib.load(MODEL_DIR / f"{design_name}_mlp.pkl")
    enc_design = SurveyEncoder.load(MODEL_DIR / f"{design_name}_encoder.pkl")

    probas_tech = mlp_tech.predict_proba(enc_tech.encode_answers(answers_flat))[0]
    labels_tech = {
        enc_tech.decode_label(i): float(probas_tech[i])
        for i in range(len(probas_tech))
    }

    probas_design = mlp_design.predict_proba(enc_design.encode_answers(answers_flat))[0]
    labels_design = {
        enc_design.decode_label(i): float(probas_design[i])
        for i in range(len(probas_design))
    }

    combined = {
        lbl: (labels_tech.get(lbl, 0.0) + labels_design.get(lbl, 0.0)) / 2.0
        for lbl in set(labels_tech) | set(labels_design)
    }
    total = sum(combined.values())
    if total > 0:
        combined = {lbl: p / total for lbl, p in combined.items()}

    label = max(combined, key=combined.get)
    prob_best = combined[label]

    sorted_preds = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    top3 = sorted_preds[:3]

    probs = np.array(list(combined.values()))
    probs_clipped = np.clip(probs, 1e-12, 1.0)
    entropy = -np.sum(probs_clipped * np.log2(probs_clipped))
    max_entropy = np.log2(len(probs))
    confidence = 1.0 - entropy / max_entropy if max_entropy > 0 else 1.0

    out = sys.__stdout__
    print(f"\n{'='*60}", file=out)
    print(f"  MLP Ensemble — {platform} (tech + design)", file=out)
    print(f"{'='*60}", file=out)
    print(f"  Предсказание:     {label}", file=out)
    print(f"  Уверенность (p):  {prob_best:.4f}  ({prob_best:.1%})", file=out)
    print(f"  Энтропия:         {entropy:.4f} / {max_entropy:.4f} бит", file=out)
    print(f"  Confidence:       {confidence:.4f}  ({confidence:.1%})", file=out)

    print("\n  ── Tech MLP (top-3) ──", file=out)
    _print_ranked(sorted(labels_tech.items(), key=lambda x: x[1], reverse=True)[:3], out)

    print("\n  ── Design MLP (top-3) ──", file=out)
    _print_ranked(sorted(labels_design.items(), key=lambda x: x[1], reverse=True)[:3], out)

    print("\n  ── Ансамбль (top-3) ──", file=out)
    _print_ranked(top3, out)

    _print_others([(lbl, prob) for lbl, prob in sorted_preds[3:] if prob > 0.01], out)

    print(f"{'='*60}\n", file=out)

    return label, top3
