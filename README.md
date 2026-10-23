# ClinicPilot AI

ClinicPilot AI is an intelligent medical clinic assistant MVP. It streamlines clinic operations through a conversational AI that handles clinical inquiries, treatment recommendations (via RAG), and automated appointment booking (via Agent Tool-Calling).

> **Note**: For in-depth architectural rationale, intent routing logic, and database design, please refer to `TECH_DOC.md`.

## 🛠️ Tech Stack

- **AI Engine**: DeepSeek API (Function Calling)
- **RAG**: ChromaDB, `Qwen3-Embedding-0.6B`, `Qwen3-Reranker-0.6B`
- **Backend**: FastAPI (Python 3.10+)
- **Database**: SQLite (Structured data), ChromaDB (Vector store)
- **Frontend**: Vanilla HTML/JS/CSS (Served statically by FastAPI)

## 🚀 Quick Start

### 1. Environment Setup
```bash
conda create -n dkl python=3.10 -y
conda activate dkl
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```
*(Optional: To enable Litefuse local tracing, run `~/.litefuse/bin/start.sh` in another terminal. If not running, the system falls back to local JSONL logging.)*

### 3. Initialize Database & Vector Store
```bash
# Load CSV data into SQLite
python seeding/seed_sqlite.py

# Chunk, embed, and load data into ChromaDB (Downloads models on first run)
python seeding/seed_chroma.py
```

### 4. Start the Application
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8088 --reload
```

### 5. Access the App
- **Frontend UI**: [http://127.0.0.1:8088](http://127.0.0.1:8088)
- **Swagger API Docs**: [http://127.0.0.1:8088/docs](http://127.0.0.1:8088/docs)

## 🔌 Core API Endpoints

- `POST /api/chat`: Handles multi-turn conversation. Receives user messages, routes intent to RAG or Database tools, and returns the LLM response.
- `GET /api/bookings`: Retrieves real-time appointment records for the UI table.

## 📂 Directory Structure
```text
├── ai-service/       # Agent loop, RAG engine, LLM wrappers
├── backend/          # FastAPI routes, Pydantic schemas, SQLite logic
├── frontend/         # HTML/JS/CSS UI
├── seeding/          # Offline scripts to populate SQLite & ChromaDB
├── mock-data/        # Raw CSV datasets
├── observability/    # Tracing (Litefuse/JSONL)
└── config.yaml       # Paths, models, and API configurations
