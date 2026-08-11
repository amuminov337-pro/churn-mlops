"""preprocess, train va api/schema o'rtasidagi kelishuvni tekshiruvchi testlar."""

import sys
from pathlib import Path

import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "api"))

from schema import Customer

from preprocess import build_preprocessor, load_data

DATA_PATH = ROOT / "data" / "telco_churn.csv"
MODEL_PATH = ROOT / "models" / "model.pkl"


def test_data_loads():
    X, y = load_data(DATA_PATH)
    assert len(X) == len(y) == 7043
    assert set(y.unique()) <= {0, 1}
    assert "customerID" not in X.columns
    assert X["TotalCharges"].isna().sum() == 0


def test_pipeline_trains_and_beats_baseline():
    X, y = load_data(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0, stratify=y
    )
    preprocessor = build_preprocessor(X)
    pipe = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LogisticRegression(class_weight="balanced", max_iter=1000)),
        ]
    )
    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:, 1]
    assert roc_auc_score(y_test, proba) > 0.78


def test_no_train_serve_skew():
    X, _ = load_data(DATA_PATH)
    preprocess_cols = set(X.columns.tolist())
    schema_fields = set(Customer.model_fields.keys())
    assert preprocess_cols == schema_fields


def test_api_health_and_predict():
    if not MODEL_PATH.exists():
        pytest.skip("model.pkl topilmadi, avval train.py ishga tushiring")

    # main.py joblib.load'ni import vaqtida bajaradi -- shuning uchun import
    # test funksiyasi ICHIDA, model.pkl mavjudligi tekshirilgandan keyin.
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    payload = Customer.model_config["json_schema_extra"]["example"]
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "churn_probability" in body
    assert "risk" in body
    assert 0.0 <= body["churn_probability"] <= 1.0


def test_api_explain_fallback():
    if not MODEL_PATH.exists():
        pytest.skip("model.pkl topilmadi, avval train.py ishga tushiring")

    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    payload = Customer.model_config["json_schema_extra"]["example"]
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    body = response.json()
    # CI/lokal muhitda LLM kalitlari sozlanmagan -- shablon fallback ishlatilishi kerak.
    assert body["source"] == "template"
    assert body["explanation"]
    assert 0.0 <= body["churn_probability"] <= 1.0
    assert body["risk"] in {"high", "low"}
    assert isinstance(body["top_drivers"], list)
