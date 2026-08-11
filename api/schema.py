"""FastAPI so'rov/javob uchun Pydantic sxemalari.

Bu yerdagi maydonlar src/preprocess.py dagi ustunlarga va frontend forma
maydonlariga aynan mos bo'lishi shart (bittasi o'zgarsa, uchtasi ham yangilanadi).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class Customer(BaseModel):
    """/predict so'rov tanasi. Maydonlar nomi va tartibi src/preprocess.py dagi
    X ustunlariga aynan mos (customerID va Churn allaqachon tashlangan holat).
    """

    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "No",
                "Dependents": "No",
                "tenure": 5,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 89.9,
                "TotalCharges": 450.5,
            }
        }
    )


class PredictResponse(BaseModel):
    """/predict va /predict/batch javob tanasi."""

    churn_probability: float
    will_churn: bool
    risk: str
    threshold: float
    model_version: str


class DriverImpact(BaseModel):
    """Modelning bitta bashorat uchun ajratgan xususiyati va uning hissasi."""

    feature: str
    impact: float


class ExplainResponse(BaseModel):
    """/explain javob tanasi."""

    explanation: str
    source: Literal["llm", "template"]
    top_drivers: list[DriverImpact]
    churn_probability: float
    risk: str
