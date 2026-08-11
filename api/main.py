"""FastAPI ilovasi: /health, /predict va /explain endpointlari uchun kirish nuqtasi.

Inference vaqtida src/preprocess.py dagi bir xil pipeline ishlatiladi
(u train paytida model.pkl ichiga Pipeline sifatida saqlangan).
"""

import json
import logging
import os
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
import sklearn
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schema import Customer, PredictResponse

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # Production'da (Render) muhit o'zgaruvchilari platforma orqali beriladi.

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = os.getenv("MODEL_PATH", str(ROOT / "models" / "model.pkl"))
METRICS_PATH = ROOT / "models" / "metrics.json"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
THRESHOLD = float(os.getenv("CHURN_THRESHOLD", "0.5"))

if not Path(MODEL_PATH).exists():
    raise RuntimeError(
        f"Model fayli topilmadi: {MODEL_PATH}. Avval `py -3.11 src/train.py` ni ishga tushiring."
    )

model = joblib.load(MODEL_PATH)

app = FastAPI(title="Churn Scoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _risk_label(probability: float) -> str:
    """Churn ehtimolini THRESHOLD asosida high/low toifalariga ajratadi (will_churn bilan bir xil chegara)."""
    return "high" if probability >= THRESHOLD else "low"


def _score(customers: list[Customer]) -> list[PredictResponse]:
    """Customer ro'yxatini model kutgan DataFrame'ga aylantirib, baholaydi."""
    df = pd.DataFrame([c.model_dump() for c in customers])
    probabilities = model.predict_proba(df)[:, 1]
    return [
        PredictResponse(
            churn_probability=float(probability),
            will_churn=bool(probability >= THRESHOLD),
            risk=_risk_label(float(probability)),
            threshold=THRESHOLD,
            model_version=Path(MODEL_PATH).name,
        )
        for probability in probabilities
    ]


try:
    from explain import router as explain_router

    app.include_router(explain_router)
except Exception:
    # openai/langfuse ixtiyoriy AI bog'liqliklar -- ular o'rnatilmagan yoki
    # noto'g'ri sozlangan bo'lsa ham /health va /predict ishlashda davom etishi kerak.
    logger.exception("/explain endpointi yuklanmadi (ixtiyoriy AI bog'liqlik)")


@app.get("/")
def root():
    """Render health-check uchun oddiy javob."""
    return {"service": "Churn Scoring API", "docs": "/docs"}


@app.get("/health")
def health():
    """Model va oxirgi train metrikalari haqida qisqa holat ma'lumoti."""
    trained_at = None
    if METRICS_PATH.exists():
        trained_at = json.loads(METRICS_PATH.read_text()).get("trained_at")
    return {
        "status": "ok",
        "model": Path(MODEL_PATH).name,
        "sklearn_version": sklearn.__version__,
        "trained_at": trained_at,
    }


@app.post("/predict", response_model=PredictResponse)
def predict(customer: Customer):
    """Bitta mijoz uchun churn ehtimolini baholaydi."""
    return _score([customer])[0]


@app.post("/predict/batch", response_model=list[PredictResponse])
def predict_batch(customers: Annotated[list[Customer], Body(..., max_length=500)]):
    """Bir nechta mijoz uchun (max 500) churn ehtimolini baholaydi."""
    return _score(customers)
