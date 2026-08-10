---
name: deploy-check
description: Deploy oldidan majburiy checklist — pytest, /health, ALLOWED_ORIGINS, model.pkl commit holati, Dockerfile yo'llari (lokal docker build qilinmaydi, Render build log'iga ishoniladi).
---

# Deploy Check

Backend Render'da Docker runtime orqali deploy qilinadi. Lokalda Docker Desktop yo'q, shuning
uchun lokal `docker build`/`docker run` qilinmaydi — Render'ning o'z build jarayoni va build
log'iga ishoniladi. Shu sabab quyidagi tekshiruvlar **lokal** darajada, docker'siz bajariladi.

## Deploy oldidan majburiy checklist

1. **Testlar yashil**:
   ```powershell
   pytest
   ```
   Har qanday qizil test bilan deploy qilinmaydi.

2. **`/health` lokalda javob beradi**:
   ```powershell
   uvicorn api.main:app --reload
   ```
   so'ng `/health` endpoint'iga so'rov yuborib, 200 javob qaytarishini tasdiqlash.

3. **`ALLOWED_ORIGINS` to'g'ri sozlangan**: production frontend domeni (Vercel URL)
   `ALLOWED_ORIGINS` ga qo'shilgan, `.env`/Render environment variables orqali — `.env.example`
   emas, haqiqiy qiymat Render dashboard'ida.

4. **`models/model.pkl` commit qilingan**: `git status` bilan tekshirib, oxirgi o'qitilgan va
   [[train-and-eval]] gate'idan (ROC-AUC >= 0.83) o'tgan model repo'da borligiga ishonch hosil
   qilish. `models/` `.gitignore` qilinmagan — shu sabab bu fayl doim repo bilan birga yuradi.

5. **Dockerfile yo'llari to'g'ri**: `Dockerfile` dagi `COPY`/`WORKDIR`/`CMD` yo'llari haqiqiy
   loyiha strukturasiga mos ekanini ko'zdan kechirish (masalan `api/`, `src/`, `models/`
   nusxalanishi, `uvicorn api.main:app` to'g'ri module path'ga ishora qilishi). **Lokal build
   qilinmaydi** — bu tekshiruv faqat fayl mazmunini ko'zdan kechirish orqali, Render build
   log'iga tayangan holda amalga oshiriladi.

## Qachon deploy qilish mumkin emas

- Yuqoridagi 5 bandning bittasi ham bajarilmagan bo'lsa.
- [[api-contract]] bo'yicha preprocess/schema/frontend sinxronligi buzilgan bo'lsa.
- Yangi model [[train-and-eval]] dagi 0.83 ROC-AUC gate'idan o'tmagan bo'lsa.
