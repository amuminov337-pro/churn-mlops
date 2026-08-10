# Backend uchun Docker image (Render, Docker runtime).
# DIQQAT: bu image lokalda build/run qilinmaydi (Docker Desktop yo'q) — Render o'zi build qiladi.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY src/ ./src/
COPY models/ ./models/

ENV MODEL_PATH=models/model.pkl

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --app-dir api --host 0.0.0.0 --port ${PORT:-8000}"]
