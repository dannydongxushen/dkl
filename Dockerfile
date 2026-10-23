# Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8088

CMD ["sh", "-c", "python seeding/seed_sqlite.py && python seeding/seed_chroma.py && uvicorn backend.main:app --host 0.0.0.0 --port 8088"]