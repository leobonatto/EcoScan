from __future__ import annotations

from io import BytesIO
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile

from src.features import extract_features


PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_DIR / "models" / "best_model.joblib"

app = FastAPI(
    title="EcoScan API",
    description="Classificação experimental de resíduos por imagem.",
    version="1.0.0",
)


def load_bundle():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


@app.get("/health")
def health():
    bundle = load_bundle()
    return {
        "status": "ok" if bundle else "modelo_nao_treinado",
        "modelo": bundle["model_name"] if bundle else None,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Envie um arquivo de imagem.")
    bundle = load_bundle()
    if bundle is None:
        raise HTTPException(status_code=503, detail="O modelo ainda não foi treinado.")
    content = await file.read()
    try:
        vector = extract_features(BytesIO(content)).reshape(1, -1)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Imagem inválida: {exc}") from exc

    model = bundle["model"]
    prediction = str(model.predict(vector)[0])
    response = {"classe": prediction, "modelo": bundle["model_name"]}
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(vector)[0]
        classes = [str(value) for value in model.classes_]
        response["confianca"] = float(np.max(probabilities))
        response["probabilidades"] = {
            label: float(value) for label, value in zip(classes, probabilities)
        }
    elif hasattr(model, "decision_function"):
        scores = np.asarray(model.decision_function(vector)[0], dtype=np.float64)
        scores = scores - np.max(scores)
        probabilities = np.exp(scores) / np.exp(scores).sum()
        classes = [str(value) for value in model.classes_]
        response["confianca_aproximada"] = float(np.max(probabilities))
        response["pontuacoes_normalizadas"] = {
            label: float(value) for label, value in zip(classes, probabilities)
        }
    return response

