from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from PIL import Image


PALETTE = ["#2E7D32", "#66BB6A", "#A5D6A7", "#1565C0", "#42A5F5", "#90CAF9"]


def configure_plotting() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update({"figure.dpi": 130, "savefig.dpi": 180, "font.size": 10})


def save_class_distribution(df: pd.DataFrame, figures_dir: Path, tables_dir: Path) -> None:
    counts = df.groupby(["source", "label"]).size().reset_index(name="quantidade")
    counts.to_csv(tables_dir / "distribuicao_classes.csv", index=False, encoding="utf-8-sig")
    plt.figure(figsize=(10, 5.5))
    sns.barplot(data=counts, x="label", y="quantidade", hue="source", palette=["#2E7D32", "#1565C0"])
    plt.title("Distribuição das classes por base")
    plt.xlabel("Classe padronizada")
    plt.ylabel("Quantidade de imagens")
    plt.legend(title="Base")
    plt.tight_layout()
    plt.savefig(figures_dir / "01_distribuicao_classes.png", bbox_inches="tight")
    plt.close()


def save_imbalance(df: pd.DataFrame, figures_dir: Path, tables_dir: Path) -> None:
    counts = df["label"].value_counts().sort_values(ascending=False)
    summary = pd.DataFrame({"classe": counts.index, "quantidade": counts.values})
    summary["percentual"] = summary["quantidade"] / summary["quantidade"].sum() * 100
    summary.to_csv(tables_dir / "resumo_balanceamento.csv", index=False, encoding="utf-8-sig")
    plt.figure(figsize=(8.5, 5))
    ax = sns.barplot(data=summary, x="classe", y="percentual", palette=PALETTE, hue="classe", legend=False)
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3)
    plt.title("Participação de cada classe no conjunto combinado")
    plt.xlabel("Classe")
    plt.ylabel("Percentual das imagens")
    plt.ylim(0, summary["percentual"].max() * 1.2)
    plt.tight_layout()
    plt.savefig(figures_dir / "02_balanceamento_percentual.png", bbox_inches="tight")
    plt.close()


def save_dimensions(df: pd.DataFrame, figures_dir: Path) -> None:
    sample = df.sample(min(len(df), 2500), random_state=42)
    plt.figure(figsize=(8, 5.5))
    sns.scatterplot(data=sample, x="width", y="height", hue="source", alpha=0.55, s=30)
    plt.title("Dimensões originais das imagens")
    plt.xlabel("Largura (pixels)")
    plt.ylabel("Altura (pixels)")
    plt.tight_layout()
    plt.savefig(figures_dir / "03_dimensoes_imagens.png", bbox_inches="tight")
    plt.close()


def save_samples(df: pd.DataFrame, figures_dir: Path) -> None:
    labels = sorted(df["label"].unique())
    fig, axes = plt.subplots(2, len(labels), figsize=(15, 6.2))
    for row_idx, source in enumerate(["TrashNet", "RealWaste"]):
        for col_idx, label in enumerate(labels):
            ax = axes[row_idx, col_idx]
            subset = df[(df["source"] == source) & (df["label"] == label)]
            if not subset.empty:
                path = subset.sample(1, random_state=100 + col_idx).iloc[0]["path"]
                with Image.open(path) as image:
                    ax.imshow(image.convert("RGB"))
            ax.set_title(f"{source}\n{label}", fontsize=9)
            ax.axis("off")
    fig.suptitle("Exemplos das classes nas duas bases", fontsize=14, y=1.01)
    plt.tight_layout()
    plt.savefig(figures_dir / "04_amostras_bases.png", bbox_inches="tight")
    plt.close()


def run_eda(project_dir: Path) -> None:
    manifest_path = project_dir / "data" / "processed" / "manifest.csv"
    df = pd.read_csv(manifest_path)
    figures_dir = project_dir / "reports" / "figures"
    tables_dir = project_dir / "reports" / "tables"
    figures_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    configure_plotting()
    save_class_distribution(df, figures_dir, tables_dir)
    save_imbalance(df, figures_dir, tables_dir)
    save_dimensions(df, figures_dir)
    save_samples(df, figures_dir)
    # Caminhos completos identificam o computador local e não agregam valor à
    # análise estatística. Eles são removidos antes de exportar a tabela.
    df.drop(columns=["path"], errors="ignore").describe(include="all").transpose().to_csv(
        tables_dir / "estatisticas_manifesto.csv", encoding="utf-8-sig"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    run_eda(args.project_dir.resolve())
    print("Análise exploratória concluída.")


if __name__ == "__main__":
    main()

