FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install deps first for better layer caching
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy code (backend + ml_engine for on-start training)
COPY backend /app/backend
COPY ml_engine /app/ml_engine
COPY demo_statement.pdf /app/demo_statement.pdf

ENV PYTHONPATH=/app
ENV PORT=8000

WORKDIR /app/backend

CMD sh -c "python init_db.py && gunicorn -w 2 -b 0.0.0.0:${PORT} wsgi:app"

