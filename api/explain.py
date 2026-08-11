"""AI yordamida churn tushuntirish endpointi (Faza 11.1).

/explain — /predict bilan bir xil Customer payload'ini qabul qiladi, churn
ehtimolini hisoblaydi, modeldan asosiy omillarni ajratadi va LLM orqali
o'zbek tilida tabiiy tilli tushuntirish generatsiya qiladi. LLM kaliti
sozlanmagan yoki chaqiruv muvaffaqiyatsiz bo'lsa, shablon asosidagi fallback
ishlatiladi -- bu endpoint hech qachon LLM sababli 500 qaytarmasligi kerak.
"""

import logging
import os

import numpy as np
import openai
import pandas as pd
from fastapi import APIRouter
from main import _score, model
from schema import Customer, DriverImpact, ExplainResponse
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)
router = APIRouter()

TOP_N = 5
LLM_TIMEOUT = 20


def top_drivers(pipeline, row_df: pd.DataFrame, top_n: int = TOP_N) -> list[dict]:
    """Pipeline'ning oxirgi bosqichidagi klassifikatordan top_n ta asosiy
    churn omilini ajratadi.

    LogisticRegression: coef_ * transformlangan qiymat bo'yicha eng katta
    ijobiy (churn'ni oshiruvchi) hissa qo'shgan xususiyatlar (ishorali).
    RandomForestClassifier: feature_importances_ bo'yicha eng muhim
    xususiyatlar (faqat kattalik -- ishora yo'q; bu ikki model turi
    orasidagi assimetriya qasddan, chunki RF ansambli yo'nalish bermaydi).
    """
    preprocessor = pipeline.named_steps["preprocessor"]
    estimator = pipeline.named_steps["model"]
    feature_names = preprocessor.get_feature_names_out()

    transformed = preprocessor.transform(row_df)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    transformed = np.asarray(transformed).ravel()

    if isinstance(estimator, LogisticRegression):
        contributions = estimator.coef_.ravel() * transformed
        order = np.argsort(contributions)[::-1][:top_n]
        return [
            {"feature": str(feature_names[i]), "impact": float(contributions[i])} for i in order
        ]

    if isinstance(estimator, RandomForestClassifier):
        importances = estimator.feature_importances_
        order = np.argsort(importances)[::-1][:top_n]
        return [{"feature": str(feature_names[i]), "impact": float(importances[i])} for i in order]

    logger.warning("top_drivers: noma'lum estimator turi %s, bo'sh ro'yxat qaytarilmoqda", type(estimator))
    return []


def _try_provider(client_kwargs: dict, model_name: str, prompt: str) -> str | None:
    """Bitta LLM provayderni chaqiradi, 1 marta retry qiladi, muvaffaqiyatsiz
    bo'lsa (xato ko'tarmasdan) None qaytaradi."""
    for attempt in range(2):
        try:
            client = openai.OpenAI(timeout=LLM_TIMEOUT, **client_kwargs)
            resp = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content
        except Exception:
            logger.exception("LLM chaqiruvi muvaffaqiyatsiz (urinish %d/2)", attempt + 1)
    return None


def _call_llm(prompt: str) -> str | None:
    """GEMINI_PROXY_* -> GOOGLE_API_KEY tartibida urinadi. Kalit yo'q yoki
    ikkalasi ham ishlamasa None qaytaradi (hech qachon xato ko'tarmaydi)."""
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    proxy_key = os.getenv("GEMINI_PROXY_API_KEY")
    proxy_base = os.getenv("GEMINI_PROXY_BASE_URL")
    if proxy_key and proxy_base:
        result = _try_provider({"api_key": proxy_key, "base_url": proxy_base}, model_name, prompt)
        if result:
            return result

    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        # Google'ning OpenAI-mos keluvchi endpointi (openai SDK bilan ishlaydi,
        # alohida google-genai SDK talab qilinmaydi).
        result = _try_provider(
            {
                "api_key": google_key,
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
            },
            model_name,
            prompt,
        )
        if result:
            return result

    return None


def _build_prompt(customer: Customer, probability: float, risk: str, drivers: list[dict]) -> str:
    drivers_txt = "\n".join(f"- {d['feature']}: {d['impact']:.4f}" for d in drivers) or "- (aniqlanmadi)"
    return (
        "Sen churn (mijoz ketishi) tahlilchisisan.\n"
        f"Churn ehtimoli: {probability:.2%} ({risk} xavf darajasi).\n\n"
        f"Mijoz ma'lumotlari: {customer.model_dump()}\n\n"
        f"Model bo'yicha asosiy omillar:\n{drivers_txt}\n\n"
        "O'zbek tilida 3 ta gapdan iborat tushuntirish yoz, so'ngra mijozni "
        "ushlab qolish uchun 2 ta aniq tavsiya ber. Faqat oddiy matn qaytar, JSON emas."
    )


def _template_fallback(probability: float, risk: str, drivers: list[dict]) -> str:
    """LLM ishlamasa ishlatiladigan statik, lekin haqiqiy drivers'ga
    moslashadigan o'zbek tilidagi shablon."""
    pct = round(probability * 100, 1)
    driver_txt = ", ".join(d["feature"] for d in drivers[:3]) if drivers else "aniq omillar topilmadi"
    if risk == "high":
        return (
            f"Ushbu mijozning ketish ehtimoli {pct}% bo'lib, yuqori xavf darajasiga to'g'ri keladi. "
            f"Asosiy omillar: {driver_txt}. "
            "Tavsiyalar: (1) mijozga shaxsiy chegirma yoki uzoq muddatli shartnoma taklif qiling; "
            "(2) qo'llab-quvvatlash xizmati orqali bog'lanib, muammosini aniqlang."
        )
    return (
        f"Ushbu mijozning ketish ehtimoli {pct}% bo'lib, past xavf darajasiga to'g'ri keladi. "
        f"Asosiy omillar: {driver_txt}. "
        "Tavsiyalar: (1) mavjud xizmat sifatini saqlab qoling; "
        "(2) davriy aloqa orqali mijoz mamnuniyatini kuzatib boring."
    )


def _trace_langfuse(customer: Customer, prompt: str, explanation: str, source: str) -> None:
    """LANGFUSE_* kalitlari mavjud bo'lsagina trace yozadi; paket
    o'rnatilmagan yoki har qanday xato bo'lsa jimgina o'tkazib yuboriladi."""
    if not (os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_PUBLIC_KEY")):
        return
    try:
        from langfuse import Langfuse

        Langfuse().trace(
            name="explain",
            input={"customer": customer.model_dump(), "prompt": prompt},
            output={"explanation": explanation, "source": source},
        )
    except Exception:
        logger.exception("Langfuse trace yozib bo'lmadi")


@router.post("/explain", response_model=ExplainResponse)
def explain(customer: Customer):
    """Bitta mijoz uchun churn ehtimoli + AI (yoki fallback) tushuntirishi."""
    prediction = _score([customer])[0]
    row_df = pd.DataFrame([customer.model_dump()])
    drivers = top_drivers(model, row_df)

    prompt = _build_prompt(customer, prediction.churn_probability, prediction.risk, drivers)

    try:
        explanation_text = _call_llm(prompt)
    except Exception:
        logger.exception("_call_llm kutilmagan xato berdi, fallback ishlatiladi")
        explanation_text = None

    source = "llm"
    if not explanation_text:
        explanation_text = _template_fallback(prediction.churn_probability, prediction.risk, drivers)
        source = "template"

    _trace_langfuse(customer, prompt, explanation_text, source)

    return ExplainResponse(
        explanation=explanation_text,
        source=source,
        top_drivers=[DriverImpact(**d) for d in drivers],
        churn_probability=prediction.churn_probability,
        risk=prediction.risk,
    )
