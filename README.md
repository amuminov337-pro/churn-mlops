# Telecom Churn MLOps

Telecom mijozlarining churn (ketib qolish) ehtimolini bashorat qiluvchi end-to-end MLOps loyihasi:
scikit-learn model + MLflow tracking + FastAPI serving + Docker + GitHub Actions (CI) + Render (backend)
+ Next.js (frontend, Vercel).

## Papka tuzilishi

```
churn-mlops/
├─ data/            # train uchun CSV (repo'da saqlanadi, .gitignore qilinmagan)
├─ models/          # o'qitilgan model.pkl (repo'da saqlanadi, .gitignore qilinmagan)
├─ src/
│  ├─ preprocess.py # train va serve uchun bir xil preprocessing pipeline
│  └─ train.py      # model o'qitish + MLflow tracking + 0.83 ROC-AUC gate
├─ api/
│  ├─ schema.py      # Pydantic request/response sxemalari
│  └─ main.py        # FastAPI ilovasi (/health, /predict)
├─ tests/
│  └─ test_pipeline.py
├─ frontend/         # Next.js ilovasi (hozircha bo'sh, keyinroq to'ldiriladi)
├─ dashboard.py       # Streamlit dashboard
├─ Dockerfile         # backend uchun (Render build qiladi, lokal build qilinmaydi)
├─ requirements.txt       # serving dependencies
├─ requirements-dev.txt   # + mlflow, pytest, streamlit, ruff
└─ .env.example
```

## Muhim eslatmalar

- **OS / terminal**: Windows, PowerShell. `&&` operatori PowerShell 5.1 da ishlamaydi —
  buyruqlarni bittadan yoki `;` bilan bering.
- **Python**: bir nechta versiya o'rnatilgan, shuning uchun har doim `py -3.11` ishlatiladi
  (`python` emas).
- **Docker**: lokalda Docker Desktop o'rnatilmagan. Dockerfile yoziladi va commit qilinadi,
  lekin lokal `docker build`/`docker run` qilinmaydi — Render deploy vaqtida o'zi build qiladi.

Batafsil qoidalar uchun [CLAUDE.md](CLAUDE.md) ga qarang.

## Tezkor boshlash (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Train:
```powershell
py -3.11 src\train.py
```

Testlar:
```powershell
pytest
```

API (lokal, reload bilan):
```powershell
uvicorn main:app --app-dir api --reload
```

Dashboard:
```powershell
streamlit run dashboard.py
```
