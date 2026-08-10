---
name: train-and-eval
description: Churn modelini o'qitish, ROC-AUC/PR-AUC/F1 metrikalarini tekshirish, 0.83 sifat gate'ini qo'llash va MLflow'da runlarni solishtirish.
---

# Train & Eval

## Ishga tushirish

```powershell
py -3.11 src\train.py
```

`python` emas — `py -3.11` ishlatiladi (CLAUDE.md, qoida "e").

## Metrikalarni tekshirish

Train tugagach quyidagilar tekshiriladi:

- **ROC-AUC** — asosiy sifat mezoni.
- **PR-AUC** — klass nomutanosibligi (churn odatda minority class) uchun qo'shimcha signal.
- **F1** — precision/recall balansi, threshold tanlashda foydali.

## 0.83 gate

CLAUDE.md qoida "b": **ROC-AUC 0.83 dan pastga tushmaydi**.

- Agar yangi run'ning ROC-AUC'i >= 0.83 bo'lsa — model `models/model.pkl` sifatida saqlanadi
  va commit qilinishi mumkin.
- Agar ROC-AUC < 0.83 bo'lsa — model **saqlanmaydi/almashtirilmaydi**. Sabablarni tekshirish
  kerak: feature engineering, hyperparametrlar, data sifati, yoki `src/preprocess.py` dagi
  o'zgarish preprocessingni buzganmi.

## MLflow'da runlarni solishtirish

```powershell
mlflow ui
```

So'ng brauzerda ochilgan UI orqali:

1. Oxirgi run bilan oldingi eng yaxshi run'ni yonma-yon solishtirish (ROC-AUC, PR-AUC, F1,
   parametrlar).
2. Agar yangi run yaxshiroq bo'lsa va gate'dan o'tsa — `models/model.pkl` shu run'ning
   artifact'iga almashtiriladi.
3. Regressiya (metrika yomonlashishi) bo'lsa, run commit qilinmaydi — sabab tahlil qilinadi.

Ishlatilgan preprocessing versiyasi har doim run parametrlari/tags orqali kuzatib boriladi,
shunda [[api-contract]] bilan qaysi ustunlar ishlatilgani aniq bo'ladi.
