# CLAUDE.md — Telecom Churn MLOps

## Loyiha maqsadi

Telecom mijozlarining churn (xizmatdan voz kechish) ehtimolini bashorat qiluvchi model va uni
production'da xizmat ko'rsatadigan to'liq stack:

- **ML**: scikit-learn model, MLflow bilan experiment tracking.
- **Serving**: FastAPI backend (`api/main.py`), Docker image sifatida Render'da (Docker runtime)
  deploy qilinadi.
- **CI**: GitHub Actions — testlar va sifat gate'lari.
- **Frontend**: Next.js, Vercel'da deploy qilinadi, backend API bilan gaplashadi.

## Papka tuzilishi

- `data/` — train uchun CSV. `.gitignore` qilinmagan, repo'da saqlanadi.
- `models/` — o'qitilgan `model.pkl`. `.gitignore` qilinmagan, repo'da saqlanadi (Docker image
  va CI shunga tayanadi).
- `src/preprocess.py` — xom ma'lumotni model kutgan formatga keltiruvchi yagona pipeline.
- `src/train.py` — modelni o'qitadi, MLflow'ga log qiladi, sifat gate'ini tekshiradi.
- `api/schema.py` — FastAPI uchun Pydantic request/response sxemalari.
- `api/main.py` — FastAPI ilovasi (`/health`, `/predict`).
- `tests/test_pipeline.py` — preprocess/train/api kelishuvini tekshiruvchi testlar.
- `frontend/` — Next.js ilovasi (hozircha bo'sh).
- `dashboard.py` — Streamlit orqali interaktiv ko'rish.
- `Dockerfile` — backend uchun, faqat `requirements.txt` (serving) o'rnatadi.

## Buyruqlar (PowerShell)

> Har bir buyruq alohida qatorda yoki `;` bilan beriladi. `&&` **ishlatilmaydi** —
> pastdagi "Qat'iy qoidalar" bo'limiga qarang.

Virtual muhit yaratish va faollashtirish:
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

Dependencies o'rnatish (dev, mlflow/pytest/streamlit/ruff bilan):
```powershell
pip install -r requirements-dev.txt
```

Modelni o'qitish:
```powershell
py -3.11 src\train.py
```

Testlarni ishga tushirish:
```powershell
pytest
```

API'ni lokal ishga tushirish:
```powershell
uvicorn main:app --app-dir api --reload
```

Docker haqida: `Dockerfile` mavjud va commit qilinadi, lekin **lokalda `docker build`/`docker run`
qilinmaydi** (Docker Desktop o'rnatilmagan). Render deploy paytida image'ni o'zi build qiladi —
Dockerfile to'g'riligiga Render build log orqali ishonch hosil qilinadi.

## Qat'iy qoidalar

a. **Preprocess bir xil bo'lishi shart**: `src/preprocess.py` dagi transformatsiya train
   (`src/train.py`) va serve (`api/main.py`) uchun so'zma-so'z bir xil ishlatiladi. Ikkita
   alohida/mos kelmaydigan pipeline yozilmaydi.

b. **Sifat gate**: ROC-AUC **0.83 dan pastga tushmaydi**. Bu chegaradan past model
   `models/model.pkl` sifatida saqlanmaydi va deploy qilinmaydi.

c. **Sirlar hech qachon commit qilinmaydi**: haqiqiy API kalitlar, tokenlar, parollar faqat
   `.env` faylida (u `.gitignore`'da). `.env.example` faqat kalit nomlarini ko'rsatadi, qiymat
   emas.

d. **API sxema ↔ train ustunlari mos**: `api/schema.py` dagi Pydantic maydonlari
   `src/preprocess.py` train paytida ishlatadigan ustunlarga aynan mos bo'lishi shart (nom,
   tartib, tip). Bittasi o'zgarsa, ikkinchisi ham darhol yangilanadi.

e. **Python versiyasi**: har doim `py -3.11` ishlatiladi, oddiy `python` emas — kompyuterda
   bir nechta Python versiyasi o'rnatilgan va noto'g'ri versiyani chaqirish xatolarga olib
   keladi.

f. **PowerShell'da `&&` ishlatilmaydi**: PowerShell 5.1 `&&` operatorini qo'llab-quvvatlamaydi.
   Ketma-ket buyruqlar alohida chaqiriladi yoki `;` bilan ajratiladi (`;` — shartsiz ketma-ket
   bajarish, `&&` kabi muvaffaqiyatga bog'liq emas, shuni yodda tuting).
