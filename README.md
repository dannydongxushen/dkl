# ClinicPilot AI

An intelligent medical clinic assistant MVP. The system streamlines clinic operations through a conversational AI that handles multi-turn dialogue, intent classification, clinical knowledge retrieval (RAG), and automated appointment booking via Agent Tool-Calling.

> **Note**: For in-depth architectural rationale, embedding/reranker choices, and workflow design, please refer to `TECH_DOC.md`.

## 🏗️ System Architecture

```text
[ Frontend UI (HTML/JS) ]
        │ (HTTP)
        ▼
[ FastAPI Backend ] ──(CRUD)──────────► [ SQLite Database ]
        │
        ▼ (Agent Loop)
[ Agent Core (DeepSeek) ]
        │
        ├─► [ RAG Engine ] ──(Vector Search)──► [ ChromaDB ]
        │                         │
        │                         ▼
        │                   [ Qwen3-Reranker ]
        │
        └─► [ Tool Calling ] ──(Read/Write)───► [ SQLite Database ]
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **AI Engine**: DeepSeek API (Function Calling / Tool Use)
- **RAG**: ChromaDB, `Qwen3-Embedding-0.6B` (Recall), `Qwen3-Reranker-0.6B` (Precision)
- **Database**: SQLite (Structured data), ChromaDB (Vector store)
- **Frontend**: Vanilla HTML/JS/CSS (Served statically by FastAPI)
- **Deployment**: Docker, Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (Recommended)
- **OR** Python 3.10+ and Conda (Local Development)
- A valid DeepSeek API Key

### Option 1: Run with Docker (Recommended)

1. Export your DeepSeek API Key to the environment:
   ```bash
   export DEEPSEEK_API_KEY="your-deepseek-api-key"
   ```
2. Build and start the container:
   ```bash
   docker-compose up --build -d
   ```
   *(Note: The first build may take a few minutes. The container will automatically seed the SQLite and ChromaDB databases on startup.)*

### Option 2: Run Locally

1. Create and activate the Conda environment:
   ```bash
   conda create -n dkl python=3.10 -y
   conda activate dkl
   pip install -r requirements.txt
   ```
2. Set the environment variable:
   ```bash
   export DEEPSEEK_API_KEY="your-deepseek-api-key"
   ```
3. Initialize the databases (downloads HuggingFace models on first run):
   ```bash
   python seeding/seed_sqlite.py
   python seeding/seed_chroma.py
   ```
4. Start the application:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8088 --reload
   ```

### Access the App
- **Frontend UI**: [http://127.0.0.1:8088](http://127.0.0.1:8088)
- **Swagger API Docs**: [http://127.0.0.1:8088/docs](http://127.0.0.1:8088/docs)

## 🔌 Core API Endpoints

- `POST /api/chat`: The main entry for user conversations. Routes intent to RAG or Database tools based on the LLM's Function Calling and returns the final response.
- `GET /api/bookings`: Retrieves the real-time list of appointments for the frontend UI to render.

## 📂 Directory Structure

```text
├── ai-service/       # Agent loop, RAG engine, LLM wrappers, Tool schemas
├── backend/          # FastAPI routes, Pydantic schemas, SQLite logic
├── frontend/         # Vanilla JS/CSS UI
├── seeding/          # Offline scripts to populate SQLite & ChromaDB
├── mock-data/        # Raw CSV datasets
├── observability/    # Logging & Tracing (Local JSONL / Litefuse)
├── config.yaml       # Paths, models, and API configurations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── TECH_DOC.md       # Detailed architectural rationale
```
