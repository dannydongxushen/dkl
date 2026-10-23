FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Create a non-root user and set permissions
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8088

CMD ["sh", "-c", "python seeding/seed_sqlite.py && python seeding/seed_chroma.py && uvicorn backend.main:app --host 0.0.0.0 --port 8088"]