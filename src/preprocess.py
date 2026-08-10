"""Xom churn ma'lumotlarini train va serve uchun bir xil shaklga keltiruvchi preprocessing pipeline.

Bu yerda qurilgan transformatsiya train.py da fit qilinadi va api/main.py da
inference vaqtida aynan bir xil holda qayta ishlatiladi (bitta manba, ikki joyda ishlatish).
"""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET = "Churn"
DROP = ["customerID"]


def load_data(csv_path):
    """CSV faylni o'qiydi, TotalCharges ustunini raqamga o'giradi (yangi mijozlarda
    bo'sh bo'lgani uchun 0.0 bilan to'ldiradi), customerID ustunini tashlaydi va
    (X, y) juftligini qaytaradi. y — Churn=="Yes" bo'yicha 0/1 target.
    """
    df = pd.read_csv(csv_path)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0.0)
    df = df.drop(columns=DROP)
    y = (df[TARGET] == "Yes").astype(int)
    X = df.drop(columns=[TARGET])
    return X, y


def build_preprocessor(X):
    """X'dagi raqamli va kategorik ustunlarni avtomatik aniqlab, raqamlarga
    StandardScaler, kategoriyalarga OneHotEncoder(handle_unknown="ignore")
    qo'llaydigan ColumnTransformer quradi va qaytaradi.
    """
    num = X.select_dtypes(include="number").columns.tolist()
    cat = X.select_dtypes(include=["object", "string"]).columns.tolist()
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ]
    )
