# ClinicPilot AI

An intelligent medical clinic assistant MVP. The system streamlines clinic operations through a conversational AI that handles multi-turn dialogue, intent classification, clinical knowledge retrieval (RAG), and automated appointment management (booking & cancellation) via Agent Tool-Calling.

> **Note**: For in-depth architectural rationale, embedding/reranker choices, and workflow design, please refer to [TECH_DOC.md](./TECH_DOC.md).

## 🏗️ System Architecture

```text
[ Frontend UI (HTML/JS) ]
        │ (HTTP)
        ▼
[ FastAPI Backend ] ──(CRUD)──────────► [ SQLite Database ]
        │
        ▼ (Agent Loop)
[ Agent Core (DeepSeek/OpenRouter) ]
        │
        ├─► [ RAG Engine ] ──(Vector Search)──► [ ChromaDB ]
        │                         │
        │                         ▼
        │                   [ Qwen3-Reranker ]
        │
        └─► [ Tool Calling ] ──(Read/Write/Update)───► [ SQLite Database ]
```

## ✨ Key Features

- **Two-Stage RAG Pipeline**: Local `Qwen3-Embedding-0.6B` (Recall) + `Qwen3-Reranker-0.6B` (Precision).
- **Agentic Booking Flow**: Automatically extracts missing parameters (date, time) through natural conversation.
- **Agentic Cancellation**: Supports multi-turn confirmation and updates appointment status to "Cancelled" directly in the database.
- **Multi-Provider Support**: Works seamlessly with DeepSeek (default) or OpenRouter APIs.
- **Full Observability**: Built-in local tracing (JSONL fallback) and Litefuse (OpenTelemetry) support.
- **Auto-refreshing UI**: The frontend real-time UI automatically updates the booking table when the AI modifies any appointment.
- **Auto-Initialization**: Databases and vector stores are initialized automatically on the first run.

---

## 🚀 How to Run

### 1. Prerequisites
- Docker & Docker Compose (Recommended)
- **OR** Python 3.10+ and Conda (Local Development)
- An API Key from [DeepSeek](https://platform.deepseek.com/) or [OpenRouter](https://openrouter.ai/)

### 2. Set Environment Variables
Export the API key for your chosen provider. (If you switch to OpenRouter, change `active_provider` in `config.yaml` first).
```bash
# For DeepSeek (Default)
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# For OpenRouter (Optional)
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

### 3. Start the Application (Choose One)

#### Option A: Run with Docker (Recommended)
```bash
docker-compose up --build
```
*(Note: Do NOT use the `-d` flag. Running it in the foreground allows you to monitor the database initialization logs.)*
*(To stop the application, simply press `Ctrl + C` in your terminal.)*

**⚠️ IMPORTANT: First Run & Model Download**
The first time you run this, it will download ~1.5GB of AI models (`Qwen3`) into the container. 
*Note: Docker may not display the live download progress bar due to terminal TTY buffering. Please be patient if it appears stuck at "Warning: You are sending unauthenticated requests to the HF Hub". It usually takes 5-15 minutes depending on your network.*

**You MUST wait until you see these lines in the logs before opening your browser:**
```text
Loading weights: 100%|██████████| 310/310 [00:00<00:00, ...it/s]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)
```

Once ready, access:
- **Access UI**: [http://127.0.0.1:8088](http://127.0.0.1:8088)
- **Access Swagger Docs**: [http://127.0.0.1:8088/docs](http://127.0.0.1:8088/docs)

#### Option B: Run Locally
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Make the start script executable and run it
chmod +x start.sh
./start.sh
```
*(To stop the application, simply press `Ctrl + C` in your terminal.)*

**⚠️ IMPORTANT for Local Run:**
Similar to Docker, the local Uvicorn server needs time to load the `Qwen3` models into memory. It will automatically initialize the database on the first run.
**You MUST wait until your terminal prints the following lines before opening the browser:**
```text
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)
```

---

## 🎮 Demo Scenarios (How to test)

Here are a few recommended prompts to test the system's end-to-end capabilities:

**1. Test RAG & Clinical Knowledge (With Patient Context)**
> *"I have a peanut allergy. Is it safe for me to get a flu shot?"*
*Expected: The AI retrieves the Flu Shot treatment info and cross-references the hardcoded patient profile (P001) to reassure the user about their allergy.*

**2. Test Database Query (Read Operation)**
> *"What are my upcoming appointments?"*
*Expected: The AI triggers the `get_patient_bookings` tool to query the SQLite database and lists John Doe's existing bookings.*

**3. Test Agentic Booking Flow (Write Operation)**
> *"I want to book an appointment for my knee pain next Monday."*
*Expected: The AI recognizes the intent, gathers missing parameters (like exact time and specific doctor), and triggers the `create_booking` tool. The UI's right panel will instantly reflect the new booking.*

**4. Test Agentic Cancellation (Update Operation)**
> *"I want to cancel my appointment next Monday."*
*Expected: The AI queries existing bookings, finds the specific Booking ID, asks for confirmation, and triggers the `cancel_booking` tool. The UI's right panel will instantly update the status to "Cancelled".*

---

## ⏳ Startup Notes & Troubleshooting

### 1. Model Loading Time (First Run)
When the application starts, it needs to load two local AI models (`Qwen3-Embedding` and `Qwen3-Reranker`) into memory. It also automatically initializes the databases if they don't exist.
- **First run**: If not cached, it will download ~1.5GB of data. This can take 5-15 minutes depending on your network.
- **Subsequent runs**: If cached, startup takes about **30 - 60 seconds**.
- **How to check status**: The server is ready ONLY when you see the `Application startup complete.` log.

### 2. Corporate Firewalls & Offline Mode
If you are running this in a restricted network, the container might fail to download models from Hugging Face, resulting in `Temporary failure in name resolution` errors.
- **DNS Issues**: The `docker-compose.yml` includes public DNS (`8.8.8.8`, `114.114.114.114`) to bypass local network limitations.

### 3. Data Isolation Between Docker and Local Environments
To prevent file permission conflicts, the SQLite and ChromaDB data are **NOT** mounted to the host machine in the Docker setup. 
- **Docker Environment**: Stores data entirely inside the container. If you run `docker-compose down`, the database will be reset.
- **Local Environment**: Stores data in the `./database/` directory on your host machine.
- **Note**: The databases in these two environments are **completely isolated**. For the best Live Demo experience, please stick to one environment (preferably Docker) to ensure data consistency.

---

## 📂 Project Structure

```text
├── ai-service/       # Agent loop, RAG engine, LLM wrappers, Tool schemas
├── backend/          # FastAPI routes, Pydantic schemas, SQLite logic
├── frontend/         # Vanilla JS/CSS UI
├── seeding/          # Offline scripts to populate SQLite & ChromaDB
├── mock-data/        # Raw CSV datasets
├── observability/    # Logging & Tracing (JSONL / Litefuse)
├── start.sh          # One-click startup script for local run
├── config.yaml       # Paths, LLM providers, and API configurations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── TECH_DOC.md       # Detailed architectural rationale
```
