from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import pandas as pd
from PIL import Image


TRASHNET_MAP = {
    "cardboard": "papelao",
    "glass": "vidro",
    "metal": "metal",
    "paper": "papel",
    "plastic": "plastico",
    "trash": "rejeito",
}

REALWASTE_MAP = {
    "Cardboard": "papelao",
    "Glass": "vidro",
    "Metal": "metal",
    "Miscellaneous Trash": "rejeito",
    "Paper": "papel",
    "Plastic": "plastico",
}

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def extract_archives(raw_dir: Path, extracted_dir: Path) -> None:
    extracted_dir.mkdir(parents=True, exist_ok=True)
    archives = {
        "trashnet_dataset_resized.zip": extracted_dir / "trashnet",
        "realwaste.zip": extracted_dir / "realwaste",
    }
    for filename, destination in archives.items():
        archive = raw_dir / filename
        marker = destination / ".extracted"
        if marker.exists():
            continue
        if not archive.exists():
            raise FileNotFoundError(f"Base ausente: {archive}")
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zip_file:
            zip_file.extractall(destination)
        marker.touch()


def find_class_dirs(root: Path, mapping: dict[str, str]):
    for directory in root.rglob("*"):
        if directory.is_dir() and directory.name in mapping:
            yield directory, mapping[directory.name]


def inspect_image(path: Path) -> dict:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            mode = image.mode
        return {
            "status": "valida",
            "width": width,
            "height": height,
            "mode": mode,
            "error": "",
        }
    except Exception as exc:
        return {
            "status": "invalida",
            "width": None,
            "height": None,
            "mode": "",
            "error": str(exc),
        }


def collect_rows(source: str, root: Path, mapping: dict[str, str]) -> list[dict]:
    rows = []
    seen = set()
    for class_dir, label in find_class_dirs(root, mapping):
        for path in class_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in VALID_EXTENSIONS:
                continue
            resolved = str(path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            info = inspect_image(path)
            rows.append(
                {
                    "path": resolved,
                    "source": source,
                    "original_class": class_dir.name,
                    "label": label,
                    "file_name": path.name,
                    "file_size_bytes": path.stat().st_size,
                    **info,
                }
            )
    return rows


def build_manifest(project_dir: Path) -> pd.DataFrame:
    raw_dir = project_dir / "data" / "raw"
    extracted_dir = project_dir / "data" / "extracted"
    processed_dir = project_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    extract_archives(raw_dir, extracted_dir)
    rows = []
    rows.extend(collect_rows("TrashNet", extracted_dir / "trashnet", TRASHNET_MAP))
    rows.extend(collect_rows("RealWaste", extracted_dir / "realwaste", REALWASTE_MAP))
    manifest = pd.DataFrame(rows).sort_values(["source", "label", "file_name"])
    manifest.to_csv(processed_dir / "manifest_all.csv", index=False, encoding="utf-8-sig")
    valid = manifest.loc[manifest["status"] == "valida"].copy()
    valid.to_csv(processed_dir / "manifest.csv", index=False, encoding="utf-8-sig")
    return valid


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    manifest = build_manifest(args.project_dir.resolve())
    print(manifest.groupby(["source", "label"]).size().unstack(fill_value=0))
    print(f"Total de imagens válidas: {len(manifest)}")


if __name__ == "__main__":
    main()

