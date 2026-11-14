from __future__ import annotations

from pathlib import Path

from src.build_manifest import build_manifest
from src.eda import run_eda
from src.train_models import run_training


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    print("[1/3] Validando e catalogando as imagens...")
    manifest = build_manifest(project_dir)
    print(f"Imagens válidas: {len(manifest)}")
    print("[2/3] Gerando análise exploratória...")
    run_eda(project_dir)
    print("[3/3] Extraindo características e comparando modelos...")
    results = run_training(project_dir)
    print("\nPipeline concluído.\n")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()

