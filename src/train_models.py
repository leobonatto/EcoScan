from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.features import extract_features


RANDOM_STATE = 42


def load_or_extract_features(project_dir: Path, manifest: pd.DataFrame):
    cache_path = project_dir / "data" / "processed" / "features.joblib"
    if cache_path.exists():
        cached = joblib.load(cache_path)
        if cached.get("paths") == manifest["path"].tolist():
            return cached["X"], np.asarray(cached["y"]), np.asarray(cached["source"])

    vectors = []
    total = len(manifest)
    for index, path in enumerate(manifest["path"], start=1):
        vectors.append(extract_features(path))
        if index % 500 == 0 or index == total:
            print(f"Características extraídas: {index}/{total}")
    X = np.vstack(vectors).astype(np.float32)
    y = manifest["label"].to_numpy()
    source = manifest["source"].to_numpy()
    joblib.dump(
        {"X": X, "y": y, "source": source, "paths": manifest["path"].tolist()},
        cache_path,
        compress=3,
    )
    return X, y, source


def build_models() -> dict:
    return {
        "Regressão Logística": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1500,
                        C=1.0,
                        class_weight="balanced",
                        solver="lbfgs",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_features="sqrt",
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "SVM RBF": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "model",
                    SVC(
                        C=5.0,
                        kernel="rbf",
                        gamma="scale",
                        probability=False,
                        class_weight="balanced",
                        cache_size=2048,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
    }


def metrics_row(name: str, y_true, y_pred, seconds: float) -> dict:
    return {
        "modelo": name,
        "acuracia": accuracy_score(y_true, y_pred),
        "precisao_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "f1_ponderado": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "tempo_treinamento_s": seconds,
    }


def save_confusion(y_true, y_pred, labels, title, path: Path) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(7.5, 6.2))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.xlabel("Classe prevista")
    plt.ylabel("Classe real")
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", dpi=180)
    plt.close()


def run_training(project_dir: Path) -> pd.DataFrame:
    manifest = pd.read_csv(project_dir / "data" / "processed" / "manifest.csv")
    X, y, source = load_or_extract_features(project_dir, manifest)
    labels = sorted(np.unique(y).tolist())
    figures_dir = project_dir / "reports" / "figures"
    tables_dir = project_dir / "reports" / "tables"
    models_dir = project_dir / "models"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    indices = np.arange(len(y))
    train_idx, test_idx = train_test_split(
        indices, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )
    results = []
    fitted = {}
    reports = {}
    for name, model in build_models().items():
        print(f"Treinando: {name}")
        start = time.perf_counter()
        model.fit(X[train_idx], y[train_idx])
        elapsed = time.perf_counter() - start
        predictions = model.predict(X[test_idx])
        results.append(metrics_row(name, y[test_idx], predictions, elapsed))
        reports[name] = classification_report(
            y[test_idx], predictions, labels=labels, output_dict=True, zero_division=0
        )
        fitted[name] = model
        safe_name = name.lower().replace(" ", "_").replace("ã", "a").replace("ó", "o")
        save_confusion(
            y[test_idx], predictions, labels, f"Matriz de confusão - {name}",
            figures_dir / f"matriz_confusao_{safe_name}.png",
        )

    results_df = pd.DataFrame(results).sort_values("f1_macro", ascending=False)
    results_df.to_csv(tables_dir / "comparacao_modelos.csv", index=False, encoding="utf-8-sig")
    with open(tables_dir / "relatorios_classificacao.json", "w", encoding="utf-8") as file:
        json.dump(reports, file, ensure_ascii=False, indent=2)

    melted = results_df.melt(
        id_vars="modelo",
        value_vars=["acuracia", "precisao_macro", "recall_macro", "f1_macro"],
        var_name="metrica",
        value_name="valor",
    )
    plt.figure(figsize=(10, 5.6))
    sns.barplot(data=melted, x="modelo", y="valor", hue="metrica")
    plt.ylim(0, 1)
    plt.title("Comparação dos modelos no conjunto de teste")
    plt.xlabel("Modelo")
    plt.ylabel("Resultado")
    plt.legend(title="Métrica", loc="lower right")
    plt.tight_layout()
    plt.savefig(figures_dir / "05_comparacao_modelos.png", bbox_inches="tight", dpi=180)
    plt.close()

    best_name = results_df.iloc[0]["modelo"]
    best_model = fitted[best_name]
    bundle = {
        "model": best_model,
        "model_name": best_name,
        "labels": labels,
        "feature_method": "HOG + histogramas HSV",
        "image_size": [64, 64],
    }
    joblib.dump(bundle, models_dir / "best_model.joblib", compress=3)

    # Experimento de mudança de domínio: aprende na TrashNet e testa na RealWaste.
    trash_idx = np.where(source == "TrashNet")[0]
    real_idx = np.where(source == "RealWaste")[0]
    trash_train, trash_test = train_test_split(
        trash_idx, test_size=0.20, stratify=y[trash_idx], random_state=RANDOM_STATE
    )
    domain_model = clone(build_models()[best_name])
    domain_model.fit(X[trash_train], y[trash_train])
    domain_rows = []
    for scenario, evaluation_idx in [
        ("TrashNet - teste interno", trash_test),
        ("RealWaste - teste externo", real_idx),
    ]:
        prediction = domain_model.predict(X[evaluation_idx])
        domain_rows.append(metrics_row(scenario, y[evaluation_idx], prediction, 0.0))
    domain_df = pd.DataFrame(domain_rows)
    domain_df.to_csv(tables_dir / "avaliacao_mudanca_dominio.csv", index=False, encoding="utf-8-sig")

    plt.figure(figsize=(8, 5))
    domain_melted = domain_df.melt(
        id_vars="modelo",
        value_vars=["acuracia", "precisao_macro", "recall_macro", "f1_macro"],
        var_name="metrica", value_name="valor",
    )
    sns.barplot(data=domain_melted, x="modelo", y="valor", hue="metrica")
    plt.ylim(0, 1)
    plt.title("Generalização de imagens controladas para imagens reais")
    plt.xlabel("Cenário de avaliação")
    plt.ylabel("Resultado")
    plt.tight_layout()
    plt.savefig(figures_dir / "06_mudanca_dominio.png", bbox_inches="tight", dpi=180)
    plt.close()

    metadata = {
        "total_images": int(len(y)),
        "train_images": int(len(train_idx)),
        "test_images": int(len(test_idx)),
        "classes": labels,
        "best_model": best_name,
        "best_f1_macro": float(results_df.iloc[0]["f1_macro"]),
        "random_state": RANDOM_STATE,
    }
    with open(tables_dir / "metadados_experimento.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, ensure_ascii=False, indent=2)
    return results_df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    results = run_training(args.project_dir.resolve())
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()

