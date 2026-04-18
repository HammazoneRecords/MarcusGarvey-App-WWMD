# Marcus Garvey App — Python/Gunicorn API
# No venv inside Docker — install deps directly
FROM python:3.12-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source (data/ is volume-mounted — not baked in)
COPY backend/ ./backend/

EXPOSE 5050
# data/ is mounted at runtime via docker-compose volume
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5050", "backend.api.server:app"]
