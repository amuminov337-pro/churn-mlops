# Backend uchun Docker image (Render, Docker runtime).
# DIQQAT: bu image lokalda build/run qilinmaydi (Docker Desktop yo'q) — Render o'zi build qiladi.

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY api ./api
COPY models ./models

RUN useradd --create-home appuser
USER appuser

ENV MODEL_PATH=/app/models/model.pkl
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /app/api

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
