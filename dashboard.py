"""Streamlit orqali churn bashoratini interaktiv ko'rish uchun dashboard."""

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Telecom Churn Predictor", page_icon="📉")
st.title("Telecom Churn Predictor")
st.caption(
    "Bu faqat lokal demo (Streamlit). Production frontend Next.js + Vercel'da bo'ladi — "
    "bu sahifa API'ni qo'lda tekshirish uchun."
)

col1, col2 = st.columns(2)

with col1:
    gender = st.selectbox("gender", ["Female", "Male"])
    senior_label = st.selectbox("SeniorCitizen", ["No", "Yes"])
    SeniorCitizen = 1 if senior_label == "Yes" else 0
    Partner = st.selectbox("Partner", ["No", "Yes"])
    Dependents = st.selectbox("Dependents", ["No", "Yes"])
    tenure = st.number_input("tenure (oy)", min_value=0, max_value=100, value=12, step=1)
    PhoneService = st.selectbox("PhoneService", ["Yes", "No"])

    if PhoneService == "No":
        st.selectbox("MultipleLines", ["No phone service"], disabled=True)
        MultipleLines = "No phone service"
    else:
        MultipleLines = st.selectbox("MultipleLines", ["No", "Yes"])

    InternetService = st.selectbox("InternetService", ["DSL", "Fiber optic", "No"])
    no_internet = InternetService == "No"

    def _internet_dependent_field(label):
        """InternetService='No' bo'lsa, bog'liq maydonni "No internet service"ga qulflaydi."""
        if no_internet:
            st.selectbox(label, ["No internet service"], disabled=True)
            return "No internet service"
        return st.selectbox(label, ["No", "Yes"])

    OnlineSecurity = _internet_dependent_field("OnlineSecurity")
    OnlineBackup = _internet_dependent_field("OnlineBackup")

with col2:
    DeviceProtection = _internet_dependent_field("DeviceProtection")
    TechSupport = _internet_dependent_field("TechSupport")
    StreamingTV = _internet_dependent_field("StreamingTV")
    StreamingMovies = _internet_dependent_field("StreamingMovies")

    Contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
    PaperlessBilling = st.selectbox("PaperlessBilling", ["Yes", "No"])
    PaymentMethod = st.selectbox(
        "PaymentMethod",
        [
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ],
    )
    MonthlyCharges = st.number_input("MonthlyCharges", min_value=0.0, value=70.0, step=0.5)
    TotalCharges = st.number_input("TotalCharges", min_value=0.0, value=840.0, step=1.0)

if st.button("Predict"):
    payload = {
        "gender": gender,
        "SeniorCitizen": SeniorCitizen,
        "Partner": Partner,
        "Dependents": Dependents,
        "tenure": tenure,
        "PhoneService": PhoneService,
        "MultipleLines": MultipleLines,
        "InternetService": InternetService,
        "OnlineSecurity": OnlineSecurity,
        "OnlineBackup": OnlineBackup,
        "DeviceProtection": DeviceProtection,
        "TechSupport": TechSupport,
        "StreamingTV": StreamingTV,
        "StreamingMovies": StreamingMovies,
        "Contract": Contract,
        "PaperlessBilling": PaperlessBilling,
        "PaymentMethod": PaymentMethod,
        "MonthlyCharges": MonthlyCharges,
        "TotalCharges": TotalCharges,
    }

    try:
        response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

        probability = result["churn_probability"]
        risk = result["risk"]

        st.metric("Churn ehtimoli", f"{probability * 100:.1f}%")
        st.progress(min(max(round(probability * 100), 0), 100))

        if risk == "high":
            st.error(f"Yuqori risk ({risk})")
        else:
            st.success(f"Past risk ({risk})")

    except requests.exceptions.ConnectionError:
        st.error(
            "API ishlamayapti. Avval `uvicorn main:app --app-dir api` ni boshqa "
            "terminalda ishga tushiring."
        )
    except requests.exceptions.RequestException as exc:
        st.error(f"So'rov xato bilan tugadi: {exc}")
