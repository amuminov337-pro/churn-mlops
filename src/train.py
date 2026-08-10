"""Churn modelini o'qitish, MLflow orqali kuzatish va models/model.pkl ga saqlash.

ROC-AUC >= 0.83 gate talabini qanoatlantirmagan model saqlanmasligi kerak.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from preprocess import build_preprocessor, load_data

DATA_PATH = os.getenv("DATA_PATH", "data/telco_churn.csv")
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
METRICS_PATH = Path(MODEL_PATH).parent / "metrics.json"
ROC_AUC_GATE = 0.83
RANDOM_STATE = 42

MODELS = {
    "logreg": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "random_forest": RandomForestClassifier(
        n_estimators=300, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
    ),
}


def main():
    """logreg va random_forest'ni bir xil train/test split'da o'qitadi, MLflow'ga
    har biri uchun alohida run log qiladi, ROC-AUC bo'yicha eng yaxshisini tanlaydi
    va gate'dan o'tsa modelni hamda metrics.json'ni saqlaydi. Gate'dan o'tmasa
    hech narsa saqlanmaydi va skript xato kod bilan tugaydi.
    """
    X, y = load_data(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    mlflow.set_experiment("churn")

    results = {}
    for name, model in MODELS.items():
        # Har model uchun preprocessor qayta quriladi -- bitta obyektni ikkala
        # pipeline'ga qayta ishlatish fit state'ini aralashtirib yuboradi.
        preprocessor = build_preprocessor(X)
        pipe = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])

        with mlflow.start_run(run_name=name):
            pipe.fit(X_train, y_train)

            y_proba = pipe.predict_proba(X_test)[:, 1]
            y_pred = pipe.predict(X_test)

            roc_auc = roc_auc_score(y_test, y_proba)
            pr_auc = average_precision_score(y_test, y_proba)
            f1 = f1_score(y_test, y_pred)

            mlflow.log_param("model", name)
            mlflow.log_param("n_rows", len(X))
            mlflow.log_metrics({"roc_auc": roc_auc, "pr_auc": pr_auc, "f1": f1})
            mlflow.sklearn.log_model(pipe, artifact_path="model")

            print(f"{name}: ROC-AUC={roc_auc:.4f} PR-AUC={pr_auc:.4f} F1={f1:.4f}")

            results[name] = {"pipeline": pipe, "roc_auc": roc_auc, "pr_auc": pr_auc, "f1": f1}

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    best = results[best_name]
    print(f"\nBest model: {best_name} (ROC-AUC={best['roc_auc']:.4f})")

    if best["roc_auc"] < ROC_AUC_GATE:
        print(
            f"GATE FAILED: eng yaxshi model ({best_name}) ROC-AUC "
            f"{best['roc_auc']:.4f} < {ROC_AUC_GATE} -- model va metrics.json saqlanmadi."
        )
        sys.exit(1)

    model_path = Path(MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best["pipeline"], model_path)

    metrics = {
        "best_model": best_name,
        "roc_auc": best["roc_auc"],
        "pr_auc": best["pr_auc"],
        "f1": best["f1"],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": sklearn.__version__,
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"GATE PASSED: model saqlandi -> {model_path}")
    print(f"Metrics saqlandi -> {METRICS_PATH}")


if __name__ == "__main__":
    main()
