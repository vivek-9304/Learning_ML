from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
MODEL_PATH = Path(__file__).parent / "model.pkl"
ENCODER_PATH = Path(__file__).parent / "encoder.pkl"   # optional, agar use kiya ho

app = FastAPI(title="RainCast Prediction API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------------
model = None
encoder = None

def load_model():
    global model, encoder
    if MODEL_PATH.exists():
        import joblib
        model = joblib.load(MODEL_PATH)
        print(f"[RainCast] Model loaded from {MODEL_PATH}")
    else:
        print(f"[RainCast] WARNING: {MODEL_PATH} nahi mili — placeholder heuristic use ho rahi hai.")

    if ENCODER_PATH.exists():
        import joblib
        encoder = joblib.load(ENCODER_PATH)
        print(f"[RainCast] Encoder loaded from {ENCODER_PATH}")

load_model()

# ------------------------------------------------------------------
# REQUEST SCHEMA
# ------------------------------------------------------------------
class LinkTelemetry(BaseModel):
    timestamp: Optional[str] = None
    received_snr_db: Optional[float] = None
    carrier_frequency_ghz: Optional[float] = None
    elevation_angle_deg: Optional[float] = None
    slant_range_km: Optional[float] = None
    fspl_db: Optional[float] = None
    gaseous_attenuation_db: Optional[float] = None
    excess_attenuation_db: Optional[float] = None
    effective_path_length_km: Optional[float] = None
    specific_attenuation_db_per_km: Optional[float] = None
    rain_height_km: Optional[float] = None
    frequency_ghz: Optional[float] = None
    itu_k: Optional[float] = None
    itu_alpha: Optional[float] = None
    station: Optional[str] = None
    climate: Optional[str] = None
    simulation_id: Optional[str] = None
    rain_rate_mm_per_hr: Optional[float] = None
    rain_event: Optional[int] = Field(default=None, description="0 or 1, ground-truth flag if known")
    season_sin: Optional[float] = None
    season_cos: Optional[float] = None
    gs_latitude: Optional[float] = None
    gs_humidity: Optional[float] = None
    gs_wv: Optional[float] = None
    itu_R001: Optional[float] = None
    itu_P_rain: Optional[float] = None
    snr_roll_mean_5min: Optional[float] = None
    snr_roll_std_5min: Optional[float] = None
    snr_roll_max_5min: Optional[float] = None
    snr_roll_min_5min: Optional[float] = None
    snr_roll_mean_30min: Optional[float] = None
    snr_roll_std_30min: Optional[float] = None
    attenuation_roll_mean: Optional[float] = None
    attenuation_roll_std: Optional[float] = None
    attenuation_delta: Optional[float] = None
    snr_delta: Optional[float] = None

FEATURE_ORDER = [
    "received_snr_db", "carrier_frequency_ghz", "elevation_angle_deg",
    "slant_range_km", "fspl_db", "gaseous_attenuation_db",
    "excess_attenuation_db", "effective_path_length_km",
    "specific_attenuation_db_per_km", "rain_height_km", "frequency_ghz",
    "itu_k", "itu_alpha", "rain_rate_mm_per_hr", "season_sin", "season_cos",
    "gs_latitude", "gs_humidity", "gs_wv", "itu_R001", "itu_P_rain",
    "snr_roll_mean_5min", "snr_roll_std_5min", "snr_roll_max_5min",
    "snr_roll_min_5min", "snr_roll_mean_30min", "snr_roll_std_30min",
    "attenuation_roll_mean", "attenuation_roll_std", "attenuation_delta",
    "snr_delta",
]


# ------------------------------------------------------------------
# RESPONSE SCHEMA
# ------------------------------------------------------------------
class PredictionResponse(BaseModel):
    prediction: str            # "yes" ya "no"
    probability: float         # 0.0 - 1.0 (rain hone ki probability)
    reasons: list = []         # optional: [["label", "value"], ...]


# ------------------------------------------------------------------
# INFERENCE
# ------------------------------------------------------------------
def build_feature_row(data: LinkTelemetry) -> pd.DataFrame:
    """Pydantic input ko ek row DataFrame mein convert karta hai,
    model ke expected column order ke saath. Missing values ko 0 se
    fill kiya hai — apni training pipeline ke hisaab se isko adjust karo
    (mean imputation, etc.)."""
    row = {}
    for col in FEATURE_ORDER:
        val = getattr(data, col, None)
        row[col] = val if val is not None else 0.0

    return pd.DataFrame([row])


def predict_with_model(data: LinkTelemetry) -> PredictionResponse:
    features = build_feature_row(data)

    if model is not None:
        proba = float(model.predict_proba(features)[0][1])
        label = "yes" if proba >= 0.5 else "no"
        return PredictionResponse(prediction=label, probability=round(proba, 4))

    rain_rate = data.rain_rate_mm_per_hr or 0.0
    excess_att = data.excess_attenuation_db or 0.0
    snr_delta = data.snr_delta or 0.0
    p_rain = data.itu_P_rain or 0.0

    score = (rain_rate / 10) + (excess_att / 5) - (snr_delta / 5) + p_rain
    proba = 1 / (1 + np.exp(-(score - 1.5)))
    label = "yes" if proba >= 0.5 else "no"

    reasons = [
        ["Rain rate", f"{rain_rate:.1f} mm/hr"],
        ["Excess attenuation", f"{excess_att:.2f} dB"],
        ["SNR delta", f"{snr_delta:.2f} dB"],
    ]

    return PredictionResponse(prediction=label, probability=round(float(proba), 4), reasons=reasons)


# ------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------
@app.get("/")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "message": "RainCast API is running. POST telemetry to /predict.",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(data: LinkTelemetry):
    try:
        return predict_with_model(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)