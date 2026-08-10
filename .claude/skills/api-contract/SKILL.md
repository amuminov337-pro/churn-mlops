---
name: api-contract
description: preprocess ustunlari, api/schema.py va frontend forma maydonlarini doim sinxron ushlab turish qoidasi — bittasi o'zgarsa, uchalasi ham yangilanadi.
---

# API Contract

## Uch tomonlama sinxronlik

Quyidagi uchta joy **har doim** bir-biriga aynan mos bo'lishi kerak (nom, tartib, tip,
required/optional holati):

1. `src/preprocess.py` — train paytida ishlatiladigan ustunlar/feature nomlari.
2. `api/schema.py` — FastAPI uchun Pydantic request sxemasi (`/predict` qabul qiladigan
   maydonlar).
3. `frontend/` — Next.js formasidagi input maydonlari (nomi, tipi, majburiyligi).

Bu CLAUDE.md qoida "d" ning kengaytmasi: `api/schema.py` train ustunlariga aynan mos bo'lishi
shart.

## Qoida: bittasi o'zgarsa, uchtasi ham o'zgaradi

Har qanday quyidagi o'zgarish — yangi ustun qo'shish, ustun o'chirish, tipni o'zgartirish,
nomni o'zgartirish — uchta joyda **bir vaqtda** amalga oshiriladi:

- `src/preprocess.py` dagi feature ro'yxati/transformatsiya yangilanadi.
- `api/schema.py` dagi Pydantic model shu o'zgarishga mos yangilanadi.
- `frontend` formasidagi tegishli maydon (agar frontend allaqachon mavjud bo'lsa) yangilanadi.

Faqat bittasini yangilab, qolganlarini eskicha qoldirish — production'da preprocessing va API
sxemasi mos kelmasligiga, ya'ni `/predict` xato yoki noto'g'ri natija berishiga olib keladi.

## O'zgarishdan keyin majburiy qadam

Uchta joy ham yangilangandan so'ng:

```powershell
pytest
```

`tests/test_pipeline.py` preprocess, schema va (agar mavjud bo'lsa) train ustunlari o'rtasidagi
kelishuvni tekshiradi. Test qizil bo'lsa, sinxronlik hali to'liq emas — deploy qilinmaydi (bog'liq:
[[deploy-check]]).
